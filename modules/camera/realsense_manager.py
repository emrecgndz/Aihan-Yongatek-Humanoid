# =======================
# modules/camera/realsense_manager.py - Intel RealSense D435i Yöneticisi (DÜZELTME)
# =======================

import pyrealsense2 as rs
import numpy as np
import cv2
from typing import Tuple, Optional, Dict, Any
from threading import Thread, Lock
import time

from config.settings import CameraSettings
from modules.system.logger import SystemLogger


class RealSenseManager:
    """Intel RealSense D435i kamera yöneticisi - macOS uyumlu"""
    
    def __init__(self, settings: CameraSettings, logger: SystemLogger):
        self.settings = settings
        self.logger = logger
        
        # RealSense nesneleri
        self.pipeline = None
        self.config = None
        self.align = None
        
        # Frame verileri
        self.rgb_frame = None
        self.depth_frame = None
        self.colorized_depth = None
        self.intrinsics = None
        
        # Thread kontrolü
        self.is_running = False
        self.capture_thread = None
        self.frame_lock = Lock()
        
        # İstatistikler
        self.frame_count = 0
        self.fps_counter = 0
        self.last_fps_time = time.time()
        
        # D435i spesifik ayarlar
        self.device_info = None
        self.depth_scale = 0.001  # meter
        
        # macOS optimizasyonları
        self.use_threading = True
        self.skip_frames = 0  # Frame atlama sayısı
        
    def list_available_devices(self) -> Dict[str, Any]:
        """Kullanılabilir RealSense cihazları listele"""
        try:
            ctx = rs.context()
            devices = ctx.query_devices()
            
            device_list = {}
            for i, device in enumerate(devices):
                device_info = {
                    'name': device.get_info(rs.camera_info.name),
                    'serial': device.get_info(rs.camera_info.serial_number),
                    'firmware': device.get_info(rs.camera_info.firmware_version),
                    'product_id': device.get_info(rs.camera_info.product_id)
                }
                device_list[f"device_{i}"] = device_info
                self.logger.info(f"RealSense cihazı bulundu: {device_info['name']} (SN: {device_info['serial']})")
            
            return device_list
            
        except Exception as e:
            self.logger.error(f"RealSense cihazları listelenirken hata: {e}")
            return {}
    
    def initialize(self) -> bool:
        """Kamerayı başlat - D435i optimizasyonu"""
        try:
            # Mevcut cihazları kontrol et
            available_devices = self.list_available_devices()
            if not available_devices:
                self.logger.error("RealSense cihazı bulunamadı")
                return False
            
            # Pipeline ve config oluştur
            self.pipeline = rs.pipeline()
            self.config = rs.config()
            
            # D435i için desteklenen çözünürlükleri kontrol et
            supported_resolutions = [
                (1280, 720),
                (848, 480),
                (640, 480),
                (424, 240)
            ]
            
            # Kullanıcının istediği çözünürlüğü desteklenen listede ara
            target_width, target_height = self.settings.width, self.settings.height
            best_resolution = self._find_best_resolution(target_width, target_height, supported_resolutions)
            
            self.logger.info(f"Hedef çözünürlük: {target_width}x{target_height}")
            self.logger.info(f"Kullanılacak çözünürlük: {best_resolution[0]}x{best_resolution[1]}")
            
            # RGB stream'i etkinleştir
            if self.settings.enable_rgb:
                try:
                    self.config.enable_stream(
                        rs.stream.color,
                        best_resolution[0],
                        best_resolution[1],
                        rs.format.bgr8,
                        self.settings.fps
                    )
                    self.logger.info(f"RGB stream etkinleştirildi: {best_resolution[0]}x{best_resolution[1]}@{self.settings.fps}fps")
                except Exception as e:
                    self.logger.warning(f"RGB stream hatası, varsayılan ayarlara geçiliyor: {e}")
                    self.config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
            
            # Depth stream'i etkinleştir
            if self.settings.enable_depth:
                try:
                    self.config.enable_stream(
                        rs.stream.depth,
                        best_resolution[0],
                        best_resolution[1],
                        rs.format.z16,
                        self.settings.fps
                    )
                    self.logger.info(f"Depth stream etkinleştirildi: {best_resolution[0]}x{best_resolution[1]}@{self.settings.fps}fps")
                except Exception as e:
                    self.logger.warning(f"Depth stream hatası, varsayılan ayarlara geçiliyor: {e}")
                    self.config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
            
            # Pipeline'ı başlat
            self.logger.info("Pipeline başlatılıyor...")
            profile = self.pipeline.start(self.config)
            
            # Device bilgilerini al
            device = profile.get_device()
            self.device_info = {
                'name': device.get_info(rs.camera_info.name),
                'serial': device.get_info(rs.camera_info.serial_number)
            }
            
            # Depth scale'i al
            depth_sensor = device.first_depth_sensor()
            self.depth_scale = depth_sensor.get_depth_scale()
            self.logger.info(f"Depth scale: {self.depth_scale}")
            
            # Align nesnesi oluştur (depth'i RGB'ye hizala)
            if self.settings.enable_rgb and self.settings.enable_depth:
                align_to = rs.stream.color
                self.align = rs.align(align_to)
                self.logger.info("Frame alignment etkinleştirildi")
            
            # Kamera içsel parametrelerini al
            if self.settings.enable_rgb:
                color_stream = profile.get_stream(rs.stream.color)
                self.intrinsics = color_stream.as_video_stream_profile().get_intrinsics()
                self.logger.info(f"Kamera intrinsics: fx={self.intrinsics.fx:.2f}, fy={self.intrinsics.fy:.2f}")
            
            # İlk birkaç frame'i atla (stabilizasyon için)
            self.logger.info("Kamera stabilizasyonu...")
            for i in range(10):
                try:
                    frames = self.pipeline.wait_for_frames(timeout_ms=1000)
                except:
                    pass
            
            self.logger.info("RealSense D435i başarıyla başlatıldı")
            return True
            
        except Exception as e:
            self.logger.error(f"RealSense başlatılamadı: {e}")
            self.logger.error("Olası çözümler:")
            self.logger.error("1. RealSense SDK yüklü mü kontrol edin")
            self.logger.error("2. Kamera USB 3.0 porta bağlı mı kontrol edin") 
            self.logger.error("3. Başka uygulama kamerayı kullanıyor mu kontrol edin")
            self.logger.error("4. macOS'ta kamera izinlerini kontrol edin")
            return False
    
    def _find_best_resolution(self, target_width: int, target_height: int, supported_resolutions: list) -> Tuple[int, int]:
        """En yakın desteklenen çözünürlüğü bul"""
        target_ratio = target_width / target_height
        best_match = supported_resolutions[0]
        best_score = float('inf')
        
        for width, height in supported_resolutions:
            ratio = width / height
            ratio_diff = abs(ratio - target_ratio)
            size_diff = abs(width - target_width) + abs(height - target_height)
            score = ratio_diff + size_diff / 1000  # Normalize etme
            
            if score < best_score:
                best_score = score
                best_match = (width, height)
        
        return best_match
    
    def start_capture(self):
        """Frame yakalama thread'ini başlat"""
        if self.pipeline is None:
            self.logger.error("Kamera başlatılmamış")
            return False
        
        self.is_running = True
        if self.use_threading:
            self.capture_thread = Thread(target=self._capture_loop, daemon=True)
            self.capture_thread.start()
            self.logger.info("Threaded kamera yakalama başlatıldı")
        else:
            self.logger.info("Sync kamera yakalama başlatıldı")
        return True
    
    def stop_capture(self):
        """Frame yakalama thread'ini durdur"""
        self.is_running = False
        if self.capture_thread:
            self.capture_thread.join(timeout=2.0)
        self.logger.info("Kamera yakalama durduruldu")
    
    def _capture_loop(self):
        """Ana frame yakalama döngüsü - macOS optimizasyonlu"""
        colorizer = rs.colorizer()
        frame_skip_counter = 0
        
        while self.is_running:
            try:
                # Frame'leri al - timeout süresi artırıldı
                frames = self.pipeline.wait_for_frames(timeout_ms=5000)
                
                # Frame atlama (performans için)
                if self.skip_frames > 0:
                    frame_skip_counter += 1
                    if frame_skip_counter % (self.skip_frames + 1) != 0:
                        continue
                
                # Frame'leri hizala
                if self.align:
                    try:
                        aligned_frames = self.align.process(frames)
                        color_frame = aligned_frames.get_color_frame()
                        depth_frame = aligned_frames.get_depth_frame()
                    except:
                        # Alignment başarısız olursa normal frame'leri kullan
                        color_frame = frames.get_color_frame()
                        depth_frame = frames.get_depth_frame()
                else:
                    color_frame = frames.get_color_frame()
                    depth_frame = frames.get_depth_frame()
                
                # RGB frame'i işle
                if color_frame and self.settings.enable_rgb:
                    try:
                        rgb_data = np.asanyarray(color_frame.get_data())
                        with self.frame_lock:
                            self.rgb_frame = rgb_data.copy()
                    except Exception as e:
                        self.logger.warning(f"RGB frame işleme hatası: {e}")
                
                # Depth frame'i işle
                if depth_frame and self.settings.enable_depth:
                    try:
                        depth_data = np.asanyarray(depth_frame.get_data())
                        
                        # Depth'i renklendir
                        colorized = np.asanyarray(colorizer.colorize(depth_frame).get_data())
                        
                        with self.frame_lock:
                            self.depth_frame = depth_data.copy()
                            self.colorized_depth = colorized.copy()
                    except Exception as e:
                        self.logger.warning(f"Depth frame işleme hatası: {e}")
                
                # FPS hesapla
                self._update_fps()
                
            except RuntimeError as e:
                if "timeout" in str(e).lower():
                    self.logger.warning("Frame timeout, devam ediliyor...")
                    continue
                else:
                    self.logger.error(f"Runtime error: {e}")
                    break
            except Exception as e:
                self.logger.error(f"Frame yakalama hatası: {e}")
                time.sleep(0.1)  # Hata durumunda kısa bekle
    
    def get_single_frame(self) -> Tuple[Optional[np.ndarray], Optional[np.ndarray]]:
        """Tek frame al (threading kullanmıyorsak)"""
        if not self.use_threading and self.pipeline:
            try:
                frames = self.pipeline.wait_for_frames(timeout_ms=1000)
                
                if self.align:
                    aligned_frames = self.align.process(frames)
                    color_frame = aligned_frames.get_color_frame()
                    depth_frame = aligned_frames.get_depth_frame()
                else:
                    color_frame = frames.get_color_frame()
                    depth_frame = frames.get_depth_frame()
                
                rgb_data = np.asanyarray(color_frame.get_data()) if color_frame else None
                depth_data = np.asanyarray(depth_frame.get_data()) if depth_frame else None
                
                return rgb_data, depth_data
                
            except Exception as e:
                self.logger.warning(f"Single frame alma hatası: {e}")
                return None, None
        
        return self.get_rgb_frame(), self.get_depth_frame()
    
    def _update_fps(self):
        """FPS hesapla ve güncelle"""
        self.frame_count += 1
        current_time = time.time()
        
        if current_time - self.last_fps_time >= 1.0:
            self.fps_counter = self.frame_count
            self.frame_count = 0
            self.last_fps_time = current_time
    
    def get_frames(self) -> Tuple[Optional[np.ndarray], Optional[np.ndarray], Optional[np.ndarray]]:
        """Mevcut frame'leri döndür (RGB, Depth, Colorized Depth)"""
        with self.frame_lock:
            return (
                self.rgb_frame.copy() if self.rgb_frame is not None else None,
                self.depth_frame.copy() if self.depth_frame is not None else None,
                self.colorized_depth.copy() if self.colorized_depth is not None else None
            )
    
    def get_rgb_frame(self) -> Optional[np.ndarray]:
        """Sadece RGB frame'i döndür"""
        with self.frame_lock:
            return self.rgb_frame.copy() if self.rgb_frame is not None else None
    
    def get_depth_frame(self) -> Optional[np.ndarray]:
        """Sadece depth frame'i döndür"""
        with self.frame_lock:
            return self.depth_frame.copy() if self.depth_frame is not None else None
    
    def get_distance_at_pixel(self, x: int, y: int) -> Optional[float]:
        """Belirli bir piksel koordinatındaki mesafeyi döndür (metre)"""
        if self.depth_frame is None:
            return None
        
        try:
            with self.frame_lock:
                if (0 <= y < self.depth_frame.shape[0] and 
                    0 <= x < self.depth_frame.shape[1]):
                    depth_value = self.depth_frame[y, x]
                    return depth_value * self.depth_scale if depth_value > 0 else None
        except (IndexError, TypeError):
            pass
        return None
    
    def pixel_to_3d(self, x: int, y: int, depth: float) -> Optional[Tuple[float, float, float]]:
        """2D piksel koordinatını 3D dünya koordinatına dönüştür"""
        if self.intrinsics is None:
            return None
        
        try:
            point_3d = rs.rs2_deproject_pixel_to_point(
                self.intrinsics, [x, y], depth
            )
            return tuple(point_3d)
        except Exception:
            return None
    
    def get_fps(self) -> int:
        """Mevcut FPS'i döndür"""
        return self.fps_counter
    
    def get_camera_info(self) -> Dict[str, Any]:
        """Kamera bilgilerini döndür"""
        info = {
            "fps": self.fps_counter,
            "device_connected": self.pipeline is not None,
            "depth_scale": self.depth_scale
        }
        
        if self.device_info:
            info.update(self.device_info)
            
        if self.intrinsics:
            info.update({
                "width": self.intrinsics.width,
                "height": self.intrinsics.height,
                "fx": self.intrinsics.fx,
                "fy": self.intrinsics.fy,
                "ppx": self.intrinsics.ppx,
                "ppy": self.intrinsics.ppy,
                "model": str(self.intrinsics.model)
            })
        
        return info
    
    def set_threading_mode(self, use_threading: bool):
        """Threading modunu değiştir"""
        if not self.is_running:
            self.use_threading = use_threading
            self.logger.info(f"Threading modu: {use_threading}")
    
    def set_frame_skip(self, skip_count: int):
        """Frame atlama sayısını ayarla (performans için)"""
        self.skip_frames = max(0, skip_count)
        self.logger.info(f"Frame skip ayarlandı: {self.skip_frames}")
    
    def cleanup(self):
        """Kaynakları temizle"""
        self.stop_capture()
        
        if self.pipeline:
            try:
                self.pipeline.stop()
                self.logger.info("Pipeline durduruldu")
            except Exception as e:
                self.logger.error(f"Pipeline durdurulurken hata: {e}")
        
        self.logger.info("RealSense kaynakları temizlendi")
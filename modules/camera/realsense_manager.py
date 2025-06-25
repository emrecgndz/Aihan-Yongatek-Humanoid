import pyrealsense2 as rs
import numpy as np
import cv2
from typing import Tuple, Optional, Dict, Any
from threading import Thread, Lock
import time

from config.settings import CameraSettings
from modules.system.logger import SystemLogger


class RealSenseManager:
    """Intel RealSense D455 kamera yöneticisi"""
    
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
        
    def initialize(self) -> bool:
        """Kamerayı başlat"""
        try:
            # Pipeline ve config oluştur
            self.pipeline = rs.pipeline()
            self.config = rs.config()
            
            # RGB stream'i etkinleştir
            if self.settings.enable_rgb:
                self.config.enable_stream(
                    rs.stream.color,
                    self.settings.width,
                    self.settings.height,
                    rs.format.bgr8,
                    self.settings.fps
                )
            
            # Depth stream'i etkinleştir
            if self.settings.enable_depth:
                self.config.enable_stream(
                    rs.stream.depth,
                    self.settings.width,
                    self.settings.height,
                    rs.format.z16,
                    self.settings.fps
                )
            
            # Pipeline'ı başlat
            profile = self.pipeline.start(self.config)
            
            # Align nesnesi oluştur (depth'i RGB'ye hizala)
            if self.settings.enable_rgb and self.settings.enable_depth:
                align_to = rs.stream.color
                self.align = rs.align(align_to)
            
            # Kamera içsel parametrelerini al
            color_stream = profile.get_stream(rs.stream.color)
            self.intrinsics = color_stream.as_video_stream_profile().get_intrinsics()
            
            self.logger.info("RealSense D455 başarıyla başlatıldı")
            return True
            
        except Exception as e:
            self.logger.error(f"RealSense başlatılamadı: {e}")
            return False
    
    def start_capture(self):
        """Frame yakalama thread'ini başlat"""
        if self.pipeline is None:
            self.logger.error("Kamera başlatılmamış")
            return False
        
        self.is_running = True
        self.capture_thread = Thread(target=self._capture_loop, daemon=True)
        self.capture_thread.start()
        self.logger.info("Kamera yakalama başlatıldı")
        return True
    
    def stop_capture(self):
        """Frame yakalama thread'ini durdur"""
        self.is_running = False
        if self.capture_thread:
            self.capture_thread.join(timeout=2.0)
        self.logger.info("Kamera yakalama durduruldu")
    
    def _capture_loop(self):
        """Ana frame yakalama döngüsü"""
        colorizer = rs.colorizer()
        
        while self.is_running:
            try:
                # Frame'leri al
                frames = self.pipeline.wait_for_frames(timeout_ms=1000)
                
                # Frame'leri hizala
                if self.align:
                    aligned_frames = self.align.process(frames)
                    color_frame = aligned_frames.get_color_frame()
                    depth_frame = aligned_frames.get_depth_frame()
                else:
                    color_frame = frames.get_color_frame()
                    depth_frame = frames.get_depth_frame()
                
                # RGB frame'i işle
                if color_frame and self.settings.enable_rgb:
                    rgb_data = np.asanyarray(color_frame.get_data())
                    with self.frame_lock:
                        self.rgb_frame = rgb_data.copy()
                
                # Depth frame'i işle
                if depth_frame and self.settings.enable_depth:
                    depth_data = np.asanyarray(depth_frame.get_data())
                    colorized = np.asanyarray(colorizer.colorize(depth_frame).get_data())
                    
                    with self.frame_lock:
                        self.depth_frame = depth_data.copy()
                        self.colorized_depth = colorized.copy()
                
                # FPS hesapla
                self._update_fps()
                
            except Exception as e:
                self.logger.error(f"Frame yakalama hatası: {e}")
                time.sleep(0.01)
    
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
                depth_value = self.depth_frame[y, x]
                return depth_value * self.settings.depth_scale
        except (IndexError, TypeError):
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
        if self.intrinsics is None:
            return {}
        
        return {
            "width": self.intrinsics.width,
            "height": self.intrinsics.height,
            "fx": self.intrinsics.fx,
            "fy": self.intrinsics.fy,
            "ppx": self.intrinsics.ppx,
            "ppy": self.intrinsics.ppy,
            "fps": self.fps_counter,
            "model": self.intrinsics.model
        }
    
    def cleanup(self):
        """Kaynakları temizle"""
        self.stop_capture()
        
        if self.pipeline:
            try:
                self.pipeline.stop()
            except Exception as e:
                self.logger.error(f"Pipeline durdurulurken hata: {e}")
        
        self.logger.info("RealSense kaynakları temizlendi")

# =======================
# modules/camera/camera_interface.py - Düzeltilmiş Kamera Arayüzü
# =======================

from abc import ABC, abstractmethod
import numpy as np
import cv2
import time
from typing import Optional, Tuple, Dict, Any


class CameraInterface(ABC):
    """Kamera modülleri için temel arayüz"""
    
    @abstractmethod
    def initialize(self) -> bool:
        """Kamerayı başlat"""
        pass
    
    @abstractmethod
    def start_capture(self) -> bool:
        """Frame yakalama başlat"""
        pass
    
    @abstractmethod
    def stop_capture(self):
        """Frame yakalama durdur"""
        pass
    
    @abstractmethod
    def get_rgb_frame(self) -> Optional[np.ndarray]:
        """RGB frame al"""
        pass
    
    @abstractmethod
    def get_depth_frame(self) -> Optional[np.ndarray]:
        """Depth frame al"""
        pass
    
    @abstractmethod
    def get_fps(self) -> int:
        """FPS al"""
        pass
    
    @abstractmethod
    def cleanup(self):
        """Kaynakları temizle"""
        pass


class MockCamera(CameraInterface):
    """Test için sahte kamera sınıfı - Düzeltilmiş"""
    
    def __init__(self, width: int = 640, height: int = 480):
        self.width = width
        self.height = height
        self.is_running = False
        self.frame_count = 0
        self.start_time = time.time()
        
        # Mock için gerçekçi parametreler
        self.mock_people_positions = [
            (width // 3, height // 2, 80, 200),      # x, y, width, height
            (2 * width // 3, height // 2, 90, 180),
        ]
        self.person_colors = [(0, 255, 0), (0, 0, 255)]  # Yeşil, Mavi
    
    def initialize(self) -> bool:
        """Mock kamerayı başlat"""
        print(f"Mock Camera başlatıldı: {self.width}x{self.height}")
        return True
    
    def start_capture(self) -> bool:
        """Mock yakalama başlat"""
        self.is_running = True
        self.start_time = time.time()
        print("Mock Camera yakalama başlatıldı")
        return True
    
    def stop_capture(self):
        """Mock yakalama durdur"""
        self.is_running = False
        print("Mock Camera yakalama durduruldu")
    
    def get_rgb_frame(self) -> Optional[np.ndarray]:
        """Mock RGB frame oluştur"""
        if not self.is_running:
            return None
        
        # Rastgele arka plan
        frame = np.random.randint(20, 50, (self.height, self.width, 3), dtype=np.uint8)
        
        # Gradient arka plan ekle (daha gerçekçi)
        for y in range(self.height):
            intensity = int(30 + (y / self.height) * 30)
            frame[y, :, :] = np.clip(frame[y, :, :] + intensity, 0, 255)
        
        # Mock insanları çiz
        for i, (px, py, pw, ph) in enumerate(self.mock_people_positions):
            # Hafif hareket simulasyonu
            movement_x = int(10 * np.sin(time.time() * 0.5 + i))
            movement_y = int(5 * np.sin(time.time() * 0.3 + i))
            
            x = max(0, min(self.width - pw, px + movement_x))
            y = max(0, min(self.height - ph, py + movement_y))
            
            # İnsan şekli çiz (dikdörtgen + daire kafa)
            color = self.person_colors[i % len(self.person_colors)]
            
            # Vücut
            cv2.rectangle(frame, (x, y + ph//4), (x + pw, y + ph), color, -1)
            
            # Kafa
            head_radius = pw // 4
            cv2.circle(frame, (x + pw//2, y + head_radius), head_radius, color, -1)
            
            # Etiket
            label = f"Person {i+1}"
            cv2.putText(frame, label, (x, y - 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        # Frame bilgisi
        info_text = f"Mock Camera - Frame {self.frame_count} | FPS: {self.get_fps()}"
        cv2.putText(frame, info_text, (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # Zaman damgası
        timestamp = f"Time: {time.time() - self.start_time:.1f}s"
        cv2.putText(frame, timestamp, (10, self.height - 20), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        self.frame_count += 1
        return frame
    
    def get_depth_frame(self) -> Optional[np.ndarray]:
        """Mock depth frame oluştur"""
        if not self.is_running:
            return None
        
        # Merkez yakın, kenarlar uzak depth pattern
        y, x = np.ogrid[:self.height, :self.width]
        center_x, center_y = self.width // 2, self.height // 2
        
        # Radial distance
        distance = np.sqrt((x - center_x)**2 + (y - center_y)**2)
        
        # Depth değerleri (mm cinsinden)
        max_distance = max(self.width, self.height) // 2
        depth_frame = 1000 + (distance / max_distance) * 3000  # 1-4 metre arası
        
        # Mock insanlar için daha yakın depth değerleri
        for px, py, pw, ph in self.mock_people_positions:
            # Hafif hareket simulasyonu
            movement_x = int(10 * np.sin(time.time() * 0.5))
            movement_y = int(5 * np.sin(time.time() * 0.3))
            
            x = max(0, min(self.width - pw, px + movement_x))
            y = max(0, min(self.height - ph, py + movement_y))
            
            # İnsan bölgesini daha yakın yap
            depth_frame[y:y+ph, x:x+pw] = 1500  # 1.5 metre
        
        return depth_frame.astype(np.uint16)
    
    def get_fps(self) -> int:
        """Mock FPS döndür"""
        if not self.is_running:
            return 0
        
        # Gerçekçi FPS simulasyonu
        elapsed = time.time() - self.start_time
        if elapsed > 0 and self.frame_count > 0:
            return min(30, int(self.frame_count / elapsed))
        return 30
    
    def get_distance_at_pixel(self, x: int, y: int) -> Optional[float]:
        """Mock mesafe al"""
        depth_frame = self.get_depth_frame()
        if depth_frame is not None and 0 <= y < self.height and 0 <= x < self.width:
            return depth_frame[y, x] * 0.001  # mm to meter
        return None
    
    def get_camera_info(self) -> Dict[str, Any]:
        """Mock kamera bilgileri"""
        return {
            "width": self.width,
            "height": self.height,
            "fps": self.get_fps(),
            "device_type": "MockCamera",
            "is_running": self.is_running,
            "frame_count": self.frame_count
        }
    
    def cleanup(self):
        """Mock temizlik"""
        self.stop_capture()
        print("Mock Camera temizlendi")


class WebcamCamera(CameraInterface):
    """Sistem webcam'i kullanan kamera sınıfı (fallback)"""
    
    def __init__(self, camera_id: int = 0, width: int = 640, height: int = 480):
        self.camera_id = camera_id
        self.width = width
        self.height = height
        self.cap = None
        self.is_running = False
        self.frame_count = 0
        self.start_time = time.time()
    
    def initialize(self) -> bool:
        """Webcam'i başlat"""
        try:
            self.cap = cv2.VideoCapture(self.camera_id)
            if not self.cap.isOpened():
                return False
            
            # Çözünürlük ayarla
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
            self.cap.set(cv2.CAP_PROP_FPS, 30)
            
            return True
        except Exception as e:
            print(f"Webcam başlatılamadı: {e}")
            return False
    
    def start_capture(self) -> bool:
        """Yakalama başlat"""
        self.is_running = True
        self.start_time = time.time()
        return True
    
    def stop_capture(self):
        """Yakalama durdur"""
        self.is_running = False
    
    def get_rgb_frame(self) -> Optional[np.ndarray]:
        """Webcam frame'i al"""
        if not self.is_running or not self.cap:
            return None
        
        ret, frame = self.cap.read()
        if ret:
            self.frame_count += 1
            # Boyutu ayarla
            if frame.shape[:2] != (self.height, self.width):
                frame = cv2.resize(frame, (self.width, self.height))
            return frame
        return None
    
    def get_depth_frame(self) -> Optional[np.ndarray]:
        """Webcam'de depth yok"""
        return None
    
    def get_fps(self) -> int:
        """FPS hesapla"""
        if not self.is_running:
            return 0
        
        elapsed = time.time() - self.start_time
        if elapsed > 0 and self.frame_count > 0:
            return int(self.frame_count / elapsed)
        return 0
    
    def cleanup(self):
        """Webcam'i kapat"""
        self.stop_capture()
        if self.cap:
            self.cap.release()
            self.cap = None
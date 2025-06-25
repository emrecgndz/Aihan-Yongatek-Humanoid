from abc import ABC, abstractmethod
import numpy as np
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
    """Test için sahte kamera sınıfı"""
    
    def __init__(self, width: int = 640, height: int = 480):
        self.width = width
        self.height = height
        self.is_running = False
        self.frame_count = 0
    
    def initialize(self) -> bool:
        return True
    
    def start_capture(self) -> bool:
        self.is_running = True
        return True
    
    def stop_capture(self):
        self.is_running = False
    
    def get_rgb_frame(self) -> Optional[np.ndarray]:
        if not self.is_running:
            return None
        
        # Rastgele renkli frame oluştur
        frame = np.random.randint(0, 255, (self.height, self.width, 3), dtype=np.uint8)
        
        # Ortaya bir test deseni çiz
        center_x, center_y = self.width // 2, self.height // 2
        cv2.circle(frame, (center_x, center_y), 50, (0, 255, 0), 2)
        cv2.putText(frame, f"Mock Camera - Frame {self.frame_count}", 
                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        self.frame_count += 1
        return frame
    
    def get_depth_frame(self) -> Optional[np.ndarray]:
        if not self.is_running:
            return None
        
        # Sahte depth frame (merkez yakın, kenarlar uzak)
        y, x = np.ogrid[:self.height, :self.width]
        center_x, center_y = self.width // 2, self.height // 2
        distance = np.sqrt((x - center_x)**2 + (y - center_y)**2)
        depth_frame = (distance * 10).astype(np.uint16)
        
        return depth_frame
    
    def get_fps(self) -> int:
        return 30 if self.is_running else 0
    
    def cleanup(self):
        self.stop_capture()
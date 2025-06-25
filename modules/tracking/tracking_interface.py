from abc import ABC, abstractmethod
from typing import List, Optional, Tuple
import numpy as np

from modules.utils.data_structures import Detection


class TrackingInterface(ABC):
    """Takip modülleri için temel arayüz"""
    
    @abstractmethod
    def update_targets(self, detections: List[Detection], depth_frame: np.ndarray) -> Optional:
        """Hedefleri güncelle"""
        pass
    
    @abstractmethod
    def get_primary_target(self) -> Optional:
        """Birincil hedefi döndür"""
        pass
    
    @abstractmethod
    def clear_targets(self):
        """Tüm hedefleri temizle"""
        pass


class DistanceInterface(ABC):
    """Mesafe hesaplama arayüzü"""
    
    @abstractmethod
    def calculate_distance_from_depth(self, detection: Detection, depth_frame: np.ndarray) -> Optional[float]:
        """Depth verisi ile mesafe hesapla"""
        pass
    
    @abstractmethod
    def calculate_3d_position(self, detection: Detection, depth_frame: np.ndarray) -> Optional[Tuple[float, float, float]]:
        """3D pozisyon hesapla"""
        pass
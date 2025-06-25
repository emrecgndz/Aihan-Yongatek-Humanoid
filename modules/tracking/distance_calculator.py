# =======================
# modules/tracking/distance_calculator.py - Mesafe Hesaplama
# =======================

import numpy as np
import math
from typing import Tuple, Optional, List
import cv2

from modules.utils.data_structures import Detection, BoundingBox


class DistanceCalculator:
    """3D mesafe hesaplama yardımcısı"""
    
    def __init__(self, camera_intrinsics=None):
        self.camera_intrinsics = camera_intrinsics
        self.depth_scale = 0.001  # mm to m
    
    def calculate_distance_from_depth(self, detection: Detection, depth_frame: np.ndarray) -> Optional[float]:
        """Depth frame kullanarak mesafe hesapla"""
        if depth_frame is None:
            return None
        
        try:
            # Tespitin merkez bölgesinden depth değerlerini al
            bbox = detection.bbox
            center_x, center_y = detection.center_x, detection.center_y
            
            # Merkez etrafında bir alan örnekle
            sample_radius = min(bbox.width, bbox.height) // 6
            
            distances = []
            for dy in range(-sample_radius, sample_radius + 1, 3):
                for dx in range(-sample_radius, sample_radius + 1, 3):
                    px = center_x + dx
                    py = center_y + dy
                    
                    # Sınırları kontrol et
                    if (0 <= px < depth_frame.shape[1] and 
                        0 <= py < depth_frame.shape[0]):
                        
                        depth_value = depth_frame[py, px]
                        if depth_value > 0:  # Geçerli depth
                            distance = depth_value * self.depth_scale
                            if 0.3 <= distance <= 8.0:  # Makul mesafe aralığı
                                distances.append(distance)
            
            if distances:
                # Median kullan (outlier'ları filtrele)
                distances.sort()
                return distances[len(distances) // 2]
            
            return None
            
        except Exception:
            return None
    
    def calculate_distance_from_size(self, detection: Detection, known_height: float = 1.7) -> Optional[float]:
        """Nesne boyutu kullanarak mesafe tahmin et"""
        if self.camera_intrinsics is None:
            return None
        
        try:
            # İnsan boyutunu piksel cinsinden al
            height_pixels = detection.bbox.height
            
            # Kamera focal length
            focal_length = self.camera_intrinsics.fy
            
            # Mesafe hesapla: distance = (real_height * focal_length) / pixel_height
            distance = (known_height * focal_length) / height_pixels
            
            return distance if 0.5 <= distance <= 10.0 else None
            
        except Exception:
            return None
    
    def calculate_3d_position(self, detection: Detection, depth_frame: np.ndarray) -> Optional[Tuple[float, float, float]]:
        """2D tespit + depth ile 3D pozisyon hesapla"""
        if self.camera_intrinsics is None or depth_frame is None:
            return None
        
        try:
            center_x, center_y = detection.center_x, detection.center_y
            
            # Depth değerini al
            depth_value = depth_frame[center_y, center_x]
            if depth_value <= 0:
                return None
            
            depth_meters = depth_value * self.depth_scale
            
            # 2D pikseli 3D koordinata dönüştür
            x = (center_x - self.camera_intrinsics.ppx) * depth_meters / self.camera_intrinsics.fx
            y = (center_y - self.camera_intrinsics.ppy) * depth_meters / self.camera_intrinsics.fy
            z = depth_meters
            
            return (x, y, z)
            
        except Exception:
            return None
    
    def calculate_relative_angle(self, detection: Detection, frame_width: int) -> float:
        """Kamera merkezine göre açı hesapla (derece)"""
        center_x = detection.center_x
        frame_center = frame_width / 2
        
        # Horizontal field of view (FOV) yaklaşık 69° for RealSense D455
        horizontal_fov = 69.0  # derece
        
        # Açı hesapla
        pixel_offset = center_x - frame_center
        max_offset = frame_width / 2
        
        angle = (pixel_offset / max_offset) * (horizontal_fov / 2)
        
        return angle
    
    def filter_distances(self, distances: List[float], method: str = "median") -> Optional[float]:
        """Mesafe değerlerini filtrele"""
        if not distances:
            return None
        
        # Outlier'ları temizle
        valid_distances = [d for d in distances if 0.3 <= d <= 8.0]
        
        if not valid_distances:
            return None
        
        if method == "median":
            valid_distances.sort()
            return valid_distances[len(valid_distances) // 2]
        elif method == "mean":
            return sum(valid_distances) / len(valid_distances)
        elif method == "min":
            return min(valid_distances)
        else:
            return valid_distances[0]
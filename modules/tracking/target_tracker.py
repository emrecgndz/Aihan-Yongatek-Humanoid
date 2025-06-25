# =======================
# modules/tracking/target_tracker.py - Hedef Takibi
# =======================

import math
import time
from typing import List, Optional, Tuple
from dataclasses import dataclass

from modules.utils.data_structures import Detection
from config.settings import TrackingSettings
from modules.system.logger import SystemLogger


@dataclass
class TrackedTarget:
    """Takip edilen hedef"""
    detection: Detection
    distance: float
    last_seen: float
    track_duration: float
    is_primary: bool = False


class TargetTracker:
    """Çoklu hedef takip sistemi"""
    
    def __init__(self, settings: TrackingSettings, logger: SystemLogger):
        self.settings = settings
        self.logger = logger
        
        # Mevcut hedefler
        self.tracked_targets: List[TrackedTarget] = []
        self.primary_target: Optional[TrackedTarget] = None
        
        # Takip parametreleri
        self.last_update_time = time.time()
        self.target_lost_threshold = 2.0  # saniye
        
    def update_targets(self, detections: List[Detection], depth_frame) -> Optional[TrackedTarget]:
        """Hedefleri güncelle ve birincil hedefi döndür"""
        current_time = time.time()
        
        # Mesafe bilgilerini hesapla
        targets_with_distance = []
        
        for detection in detections:
            distance = self._calculate_distance(detection, depth_frame)
            
            if distance and self.settings.min_distance <= distance <= self.settings.max_distance:
                target = TrackedTarget(
                    detection=detection,
                    distance=distance,
                    last_seen=current_time,
                    track_duration=0.0
                )
                targets_with_distance.append(target)
        
        # Mevcut hedefleri güncelle
        self._update_tracked_targets(targets_with_distance, current_time)
        
        # Birincil hedefi belirle
        self._select_primary_target()
        
        return self.primary_target
    
    def _calculate_distance(self, detection: Detection, depth_frame) -> Optional[float]:
        """Tespit edilen kişinin mesafesini hesapla"""
        if depth_frame is None:
            return None
        
        try:
            # Tespitin merkez bölgesinden örnek al
            center_x, center_y = detection.center_x, detection.center_y
            sample_size = 10
            
            distances = []
            for dx in range(-sample_size, sample_size + 1, 5):
                for dy in range(-sample_size, sample_size + 1, 5):
                    px, py = center_x + dx, center_y + dy
                    
                    if 0 <= px < depth_frame.shape[1] and 0 <= py < depth_frame.shape[0]:
                        depth_value = depth_frame[py, px]
                        if depth_value > 0:
                            distance = depth_value * 0.001  # mm to m
                            distances.append(distance)
            
            if distances:
                # Median mesafeyi kullan (outlier'ları filtrelemek için)
                distances.sort()
                return distances[len(distances) // 2]
            
        except Exception as e:
            self.logger.error(f"Mesafe hesaplama hatası: {e}")
        
        return None
    
    def _update_tracked_targets(self, new_targets: List[TrackedTarget], current_time: float):
        """Mevcut hedefleri yeni tespitlerle güncelle"""
        # Eski hedefleri temizle (uzun süre görülmeyen)
        self.tracked_targets = [
            target for target in self.tracked_targets
            if current_time - target.last_seen < self.target_lost_threshold
        ]
        
        # Yeni hedefleri mevcut hedeflerle eşleştir
        updated_targets = []
        
        for new_target in new_targets:
            matched = False
            
            for existing_target in self.tracked_targets:
                # Pozisyon ve boyut benzerliği kontrol et
                if self._targets_match(new_target, existing_target):
                    # Mevcut hedefi güncelle
                    existing_target.detection = new_target.detection
                    existing_target.distance = new_target.distance
                    existing_target.last_seen = current_time
                    existing_target.track_duration = current_time - (existing_target.last_seen - existing_target.track_duration)
                    
                    updated_targets.append(existing_target)
                    matched = True
                    break
            
            if not matched:
                # Yeni hedef ekle
                new_target.track_duration = 0.0
                updated_targets.append(new_target)
        
        self.tracked_targets = updated_targets
    
    def _targets_match(self, target1: TrackedTarget, target2: TrackedTarget) -> bool:
        """İki hedefin aynı kişi olup olmadığını kontrol et"""
        det1, det2 = target1.detection, target2.detection
        
        # Merkez noktaları arası mesafe
        center_distance = math.sqrt(
            (det1.center_x - det2.center_x) ** 2 +
            (det1.center_y - det2.center_y) ** 2
        )
        
        # Boyut benzerliği
        size_diff = abs(det1.bbox.width - det2.bbox.width) + abs(det1.bbox.height - det2.bbox.height)
        
        # Eşleştirme kriterleri
        max_center_distance = 50  # piksel
        max_size_difference = 100  # piksel
        
        return center_distance < max_center_distance and size_diff < max_size_difference
    
    def _select_primary_target(self):
        """Birincil hedefi seç"""
        if not self.tracked_targets:
            self.primary_target = None
            return
        
        # Mevcut birincil hedef hala var mı?
        current_primary_exists = any(
            target == self.primary_target for target in self.tracked_targets
        ) if self.primary_target else False
        
        # Otomatik hedef değiştirme kapalıysa mevcut hedefle devam et
        if not self.settings.auto_switch_target and current_primary_exists:
            return
        
        # Yeni birincil hedef seç
        if self.settings.face_priority:
            # Önce kameraya bakan kişileri tercih et
            facing_targets = [
                target for target in self.tracked_targets
                if self._is_facing_camera(target.detection)
            ]
            
            if facing_targets:
                candidates = facing_targets
            else:
                candidates = self.tracked_targets
        else:
            candidates = self.tracked_targets
        
        # En yakın hedefi seç
        primary_candidate = min(candidates, key=lambda t: t.distance)
        
        # Birincil hedef değişti mi?
        if self.primary_target != primary_candidate:
            if self.primary_target:
                self.primary_target.is_primary = False
            
            self.primary_target = primary_candidate
            self.primary_target.is_primary = True
            
            self.logger.info(f"Yeni birincil hedef: mesafe {primary_candidate.distance:.2f}m")
    
    def _is_facing_camera(self, detection: Detection) -> bool:
        """Kişinin kameraya bakıp bakmadığını tahmin et (basit heuristic)"""
        # Bu gerçek bir yüz yönelimi tespiti değil, sadece placeholder
        # Gerçek uygulamada pose estimation veya face landmarks kullanılabilir
        bbox = detection.bbox
        
        # Yükseklik/genişlik oranı (frontal bakış daha kare olur)
        aspect_ratio = bbox.height / bbox.width
        
        # 1.2-1.8 arası oran frontal bakış olarak kabul edilir
        return 1.2 <= aspect_ratio <= 1.8
    
    def force_target_selection(self, detection_id: int) -> bool:
        """Belirli bir tespit ID'sini birincil hedef olarak zorla"""
        for target in self.tracked_targets:
            if target.detection.id == detection_id:
                if self.primary_target:
                    self.primary_target.is_primary = False
                
                self.primary_target = target
                target.is_primary = True
                self.logger.info(f"Hedef manuel olarak değiştirildi: ID {detection_id}")
                return True
        
        return False
    
    def get_all_targets(self) -> List[TrackedTarget]:
        """Tüm takip edilen hedefleri döndür"""
        return self.tracked_targets.copy()
    
    def get_primary_target(self) -> Optional[TrackedTarget]:
        """Birincil hedefi döndür"""
        return self.primary_target
    
    def clear_targets(self):
        """Tüm hedefleri temizle"""
        self.tracked_targets.clear()
        self.primary_target = None
        self.logger.info("Tüm hedefler temizlendi")


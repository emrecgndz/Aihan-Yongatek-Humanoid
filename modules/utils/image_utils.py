# =======================
# modules/utils/image_utils.py - Görüntü İşleme Yardımcıları
# =======================

import cv2
import numpy as np
from typing import Tuple, Optional, List
from modules.utils.data_structures import BoundingBox


def resize_frame(frame: np.ndarray, target_width: int, target_height: int) -> np.ndarray:
    """Frame'i yeniden boyutlandır"""
    return cv2.resize(frame, (target_width, target_height))


def crop_bbox(frame: np.ndarray, bbox: BoundingBox) -> Optional[np.ndarray]:
    """Bounding box alanını kırp"""
    try:
        height, width = frame.shape[:2]
        
        # Sınırları kontrol et
        x1 = max(0, bbox.x1)
        y1 = max(0, bbox.y1)
        x2 = min(width, bbox.x2)
        y2 = min(height, bbox.y2)
        
        if x2 <= x1 or y2 <= y1:
            return None
        
        return frame[y1:y2, x1:x2]
        
    except Exception:
        return None


def enhance_contrast(frame: np.ndarray, alpha: float = 1.5, beta: int = 0) -> np.ndarray:
    """Kontrast ve parlaklık ayarla"""
    return cv2.convertScaleAbs(frame, alpha=alpha, beta=beta)


def apply_gaussian_blur(frame: np.ndarray, kernel_size: int = 5) -> np.ndarray:
    """Gaussian blur uygula"""
    if kernel_size % 2 == 0:
        kernel_size += 1  # Tek sayı olmalı
    return cv2.GaussianBlur(frame, (kernel_size, kernel_size), 0)


def draw_tracking_info(frame: np.ndarray, detections: List, primary_target=None) -> np.ndarray:
    """Takip bilgilerini frame üzerine çiz"""
    annotated_frame = frame.copy()
    
    for i, detection in enumerate(detections):
        bbox = detection.bbox
        
        # Renk seç
        if primary_target and detection == primary_target.detection:
            color = (0, 255, 0)  # Yeşil - birincil hedef
            thickness = 3
        else:
            color = (255, 165, 0)  # Turuncu - diğer hedefler
            thickness = 2
        
        # Bounding box çiz
        cv2.rectangle(annotated_frame, (bbox.x1, bbox.y1), (bbox.x2, bbox.y2), color, thickness)
        
        # ID ve mesafe bilgisi
        label = f"ID: {detection.id}"
        if hasattr(detection, 'distance') and detection.distance:
            label += f" | {detection.distance:.2f}m"
        
        # Label arka planı
        label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)[0]
        cv2.rectangle(
            annotated_frame,
            (bbox.x1, bbox.y1 - label_size[1] - 10),
            (bbox.x1 + label_size[0] + 10, bbox.y1),
            color, -1
        )
        
        # Label yazısı
        cv2.putText(
            annotated_frame, label,
            (bbox.x1 + 5, bbox.y1 - 5),
            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2
        )
        
        # Merkez noktası
        cv2.circle(annotated_frame, (detection.center_x, detection.center_y), 4, color, -1)
    
    return annotated_frame


def add_system_overlay(frame: np.ndarray, fps: int, detection_count: int, 
                      target_distance: Optional[float] = None) -> np.ndarray:
    """Sistem bilgilerini overlay olarak ekle"""
    annotated_frame = frame.copy()
    
    # Bilgi metinleri
    info_texts = [
        f"FPS: {fps}",
        f"Detections: {detection_count}",
    ]
    
    if target_distance is not None:
        info_texts.append(f"Target: {target_distance:.2f}m")
    
    # Arka plan dikdörtgeni
    overlay_height = len(info_texts) * 25 + 10
    cv2.rectangle(annotated_frame, (10, 10), (200, overlay_height), (0, 0, 0), -1)
    cv2.rectangle(annotated_frame, (10, 10), (200, overlay_height), (255, 255, 255), 1)
    
    # Metinleri yaz
    for i, text in enumerate(info_texts):
        y_pos = 30 + i * 25
        cv2.putText(annotated_frame, text, (15, y_pos), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
    
    return annotated_frame


def create_depth_colormap(depth_frame: np.ndarray, max_distance: float = 5.0) -> np.ndarray:
    """Depth frame'i renkli haritaya dönüştür"""
    if depth_frame is None:
        return None
    
    # Normalize depth values
    depth_normalized = depth_frame.astype(np.float32) * 0.001  # mm to m
    depth_normalized = np.clip(depth_normalized / max_distance, 0, 1)
    
    # Apply colormap
    depth_colored = cv2.applyColorMap((depth_normalized * 255).astype(np.uint8), cv2.COLORMAP_JET)
    
    return depth_colored


def stack_frames_horizontally(frame1: np.ndarray, frame2: np.ndarray) -> np.ndarray:
    """İki frame'i yatay olarak birleştir"""
    if frame1 is None:
        return frame2
    if frame2 is None:
        return frame1
    
    # Boyutları eşitle
    h1, w1 = frame1.shape[:2]
    h2, w2 = frame2.shape[:2]
    
    target_height = min(h1, h2)
    
    frame1_resized = cv2.resize(frame1, (int(w1 * target_height / h1), target_height))
    frame2_resized = cv2.resize(frame2, (int(w2 * target_height / h2), target_height))
    
    return np.hstack([frame1_resized, frame2_resized])

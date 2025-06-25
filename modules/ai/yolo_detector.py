# =======================
# modules/ai/yolo_detector.py - YOLOv8 İnsan Tespiti
# =======================

import cv2
import numpy as np
from ultralytics import YOLO
import torch
from typing import List, Dict, Tuple, Optional
import time
from threading import Lock

from config.settings import YOLOSettings
from modules.system.logger import SystemLogger
from modules.utils.data_structures import Detection, BoundingBox


class YOLODetector:
    """YOLOv8-People derin öğrenme modeli ile insan tespiti"""
    
    def __init__(self, settings: YOLOSettings, logger: SystemLogger):
        self.settings = settings
        self.logger = logger
        
        # Model
        self.model = None
        self.device = None
        
        # Tespit verileri
        self.last_detections = []
        self.detection_lock = Lock()
        
        # İstatistikler
        self.inference_time = 0.0
        self.total_detections = 0
        
    def initialize(self) -> bool:
        """YOLO modelini yükle"""
        try:
            # CUDA kullanılabilirliğini kontrol et
            if self.settings.device == "cuda" and torch.cuda.is_available():
                self.device = "cuda"
                self.logger.info(f"CUDA kullanılıyor: {torch.cuda.get_device_name()}")
            else:
                self.device = "cpu"
                self.logger.info("CPU kullanılıyor")
            
            # Model yükle
            self.model = YOLO(self.settings.model_path)
            self.model.to(self.device)
            
            # Modeli test et
            test_image = np.zeros((640, 640, 3), dtype=np.uint8)
            _ = self.model(test_image, verbose=False)
            
            self.logger.info(f"YOLOv8 modeli başarıyla yüklendi: {self.settings.model_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"YOLO modeli yüklenemedi: {e}")
            return False
    
    def detect_people(self, frame: np.ndarray) -> List[Detection]:
        """Frame'de insan tespiti yap"""
        if self.model is None:
            return []
        
        start_time = time.time()
        
        try:
            # YOLO inference
            results = self.model(
                frame,
                conf=self.settings.confidence_threshold,
                classes=[0],  # Sadece person class (0)
                verbose=False,
                device=self.device
            )
            
            detections = []
            
            if results and len(results) > 0:
                result = results[0]
                
                if result.boxes is not None and len(result.boxes) > 0:
                    boxes = result.boxes.xyxy.cpu().numpy()
                    confidences = result.boxes.conf.cpu().numpy()
                    
                    for i, (box, conf) in enumerate(zip(boxes, confidences)):
                        if i >= self.settings.max_detections:
                            break
                        
                        x1, y1, x2, y2 = box.astype(int)
                        
                        # BoundingBox oluştur
                        bbox = BoundingBox(
                            x1=x1, y1=y1, x2=x2, y2=y2,
                            width=x2-x1, height=y2-y1
                        )
                        
                        # Detection oluştur
                        detection = Detection(
                            id=i,
                            bbox=bbox,
                            confidence=float(conf),
                            class_name="person",
                            center_x=int((x1 + x2) / 2),
                            center_y=int((y1 + y2) / 2)
                        )
                        
                        detections.append(detection)
            
            # İstatistikleri güncelle
            self.inference_time = time.time() - start_time
            self.total_detections += len(detections)
            
            # Thread-safe güncelleme
            with self.detection_lock:
                self.last_detections = detections
            
            return detections
            
        except Exception as e:
            self.logger.error(f"YOLO tespit hatası: {e}")
            return []
    
    def get_last_detections(self) -> List[Detection]:
        """Son tespitleri döndür"""
        with self.detection_lock:
            return self.last_detections.copy()
    
    def draw_detections(self, frame: np.ndarray, detections: List[Detection]) -> np.ndarray:
        """Tespitleri frame üzerine çiz"""
        annotated_frame = frame.copy()
        
        for detection in detections:
            bbox = detection.bbox
            
            # Kutu çiz
            cv2.rectangle(
                annotated_frame,
                (bbox.x1, bbox.y1),
                (bbox.x2, bbox.y2),
                (0, 255, 0), 2
            )
            
            # Güven skoru yazısı
            label = f"Person {detection.confidence:.2f}"
            label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)[0]
            
            # Arka plan dikdörtgeni
            cv2.rectangle(
                annotated_frame,
                (bbox.x1, bbox.y1 - label_size[1] - 10),
                (bbox.x1 + label_size[0], bbox.y1),
                (0, 255, 0), -1
            )
            
            # Yazı
            cv2.putText(
                annotated_frame,
                label,
                (bbox.x1, bbox.y1 - 5),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5, (0, 0, 0), 2
            )
            
            # Merkez noktası
            cv2.circle(
                annotated_frame,
                (detection.center_x, detection.center_y),
                5, (255, 0, 0), -1
            )
        
        return annotated_frame
    
    def get_inference_time(self) -> float:
        """Son inference süresini döndür (ms)"""
        return self.inference_time * 1000
    
    def get_stats(self) -> Dict[str, any]:
        """Tespit istatistiklerini döndür"""
        return {
            "total_detections": self.total_detections,
            "last_inference_time_ms": self.get_inference_time(),
            "device": self.device,
            "model_loaded": self.model is not None,
            "current_detections": len(self.last_detections)
        }

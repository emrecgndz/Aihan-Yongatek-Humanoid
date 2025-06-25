# =======================
# modules/ai/yolo_detector.py - Düzeltilmiş YOLOv8 İnsan Tespiti
# =======================

import cv2
import numpy as np
import time
import os
from threading import Lock
from typing import List, Dict, Tuple, Optional

try:
    from ultralytics import YOLO
    import torch
    YOLO_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  YOLO import hatası: {e}")
    YOLO_AVAILABLE = False

from config.settings import YOLOSettings
from modules.system.logger import SystemLogger
from modules.utils.data_structures import Detection, BoundingBox


class YOLODetector:
    """YOLOv8-People derin öğrenme modeli ile insan tespiti - Düzeltilmiş"""
    
    def __init__(self, settings: YOLOSettings, logger: SystemLogger):
        self.settings = settings
        self.logger = logger
        
        # Model
        self.model = None
        self.device = None
        self.model_loaded = False
        
        # Tespit verileri
        self.last_detections = []
        self.detection_lock = Lock()
        
        # İstatistikler
        self.inference_time = 0.0
        self.total_detections = 0
        self.frame_count = 0
        
        # Mock mode (YOLO yoksa)
        self.mock_mode = not YOLO_AVAILABLE
        
    def initialize(self) -> bool:
        """YOLO modelini yükle"""
        if not YOLO_AVAILABLE:
            self.logger.warning("YOLO kütüphanesi bulunamadı, mock mode aktif")
            self.mock_mode = True
            return True
        
        try:
            # CUDA kullanılabilirliğini kontrol et
            if self.settings.device == "cuda" and torch.cuda.is_available():
                self.device = "cuda"
                self.logger.info(f"CUDA kullanılıyor: {torch.cuda.get_device_name()}")
            else:
                self.device = "cpu"
                self.logger.info("CPU kullanılıyor")
            
            # Model dosyası kontrolü
            model_path = self.settings.model_path
            if not os.path.exists(model_path):
                self.logger.warning(f"Model dosyası bulunamadı: {model_path}")
                self.logger.info("Varsayılan YOLOv8n modeli indiriliyor...")
                
                # Varsayılan model indir
                try:
                    self.model = YOLO('yolov8n.pt')
                    
                    # Model dosyasını kaydet
                    os.makedirs(os.path.dirname(model_path), exist_ok=True)
                    # YOLOv8 otomatik olarak ~/.ultralytics/weights/ dizinine indirir
                    import shutil
                    weights_dir = os.path.expanduser("~/.ultralytics/weights/yolov8n.pt")
                    if os.path.exists(weights_dir):
                        shutil.copy(weights_dir, model_path)
                        self.logger.info(f"Model kaydedildi: {model_path}")
                    
                except Exception as e:
                    self.logger.error(f"Model indirme hatası: {e}")
                    self.mock_mode = True
                    return True
            else:
                # Mevcut model dosyasını yükle
                self.model = YOLO(model_path)
            
            # Model cihazı ayarla
            if self.model:
                # Test inference
                test_image = np.zeros((640, 640, 3), dtype=np.uint8)
                _ = self.model(test_image, verbose=False, device=self.device)
                
                self.model_loaded = True
                self.logger.info(f"YOLOv8 modeli başarıyla yüklendi: {model_path}")
                return True
            
        except Exception as e:
            self.logger.error(f"YOLO modeli yüklenemedi: {e}")
            self.logger.info("Mock mode'a geçiliyor...")
            self.mock_mode = True
            return True
    
    def detect_people(self, frame: np.ndarray) -> List[Detection]:
        """Frame'de insan tespiti yap"""
        if frame is None:
            return []
        
        start_time = time.time()
        self.frame_count += 1
        
        try:
            if self.mock_mode or not self.model_loaded:
                # Mock detection
                detections = self._generate_mock_detections(frame)
            else:
                # Gerçek YOLO detection
                detections = self._run_yolo_detection(frame)
            
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
    
    def _run_yolo_detection(self, frame: np.ndarray) -> List[Detection]:
        """Gerçek YOLO detection"""
        try:
            # YOLO inference
            results = self.model(
                frame,
                conf=self.settings.confidence_threshold,
                classes=[0],  # Sadece person class (0)
                verbose=False,
                device=self.device,
                max_det=self.settings.max_detections
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
                        
                        # Sınırları kontrol et
                        height, width = frame.shape[:2]
                        x1 = max(0, min(width-1, x1))
                        y1 = max(0, min(height-1, y1))
                        x2 = max(x1+1, min(width, x2))
                        y2 = max(y1+1, min(height, y2))
                        
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
            
            return detections
            
        except Exception as e:
            self.logger.error(f"YOLO inference hatası: {e}")
            return []
    
    def _generate_mock_detections(self, frame: np.ndarray) -> List[Detection]:
        """Mock detection üret (test için)"""
        detections = []
        height, width = frame.shape[:2]
        
        # Frame sayısına göre dinamik mock detections
        num_people = min(3, (self.frame_count // 30) % 4)  # 0-3 kişi, 30 frame'de bir değişir
        
        for i in range(num_people):
            # Rastgele pozisyon
            person_width = 80 + (i * 20)
            person_height = 180 + (i * 30)
            
            # Hareket simulasyonu
            time_factor = time.time() * 0.5
            x_offset = int(50 * np.sin(time_factor + i))
            y_offset = int(20 * np.cos(time_factor + i * 0.7))
            
            center_x = (width // (num_people + 1)) * (i + 1) + x_offset
            center_y = height // 2 + y_offset
            
            # Sınırları kontrol et
            x1 = max(0, center_x - person_width // 2)
            y1 = max(0, center_y - person_height // 2)
            x2 = min(width, center_x + person_width // 2)
            y2 = min(height, center_y + person_height // 2)
            
            if x2 <= x1 or y2 <= y1:
                continue
            
            # BoundingBox oluştur
            bbox = BoundingBox(
                x1=x1, y1=y1, x2=x2, y2=y2,
                width=x2-x1, height=y2-y1
            )
            
            # Detection oluştur
            detection = Detection(
                id=i,
                bbox=bbox,
                confidence=0.7 + (i * 0.1),  # Farklı confidence değerleri
                class_name="person",
                center_x=center_x,
                center_y=center_y
            )
            
            detections.append(detection)
        
        return detections
    
    def get_last_detections(self) -> List[Detection]:
        """Son tespitleri döndür"""
        with self.detection_lock:
            return self.last_detections.copy()
    
    def draw_detections(self, frame: np.ndarray, detections: List[Detection]) -> np.ndarray:
        """Tespitleri frame üzerine çiz"""
        if frame is None or not detections:
            return frame
        
        annotated_frame = frame.copy()
        
        for detection in detections:
            bbox = detection.bbox
            
            # Renk seç (mock için farklı renkler)
            if self.mock_mode:
                colors = [(0, 255, 0), (255, 0, 0), (0, 0, 255), (255, 255, 0)]
                color = colors[detection.id % len(colors)]
            else:
                color = (0, 255, 0)  # Yeşil
            
            # Kutu çiz
            cv2.rectangle(
                annotated_frame,
                (bbox.x1, bbox.y1),
                (bbox.x2, bbox.y2),
                color, 2
            )
            
            # Güven skoru yazısı
            label = f"Person {detection.confidence:.2f}"
            if self.mock_mode:
                label += " (Mock)"
            
            label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)[0]
            
            # Arka plan dikdörtgeni
            cv2.rectangle(
                annotated_frame,
                (bbox.x1, bbox.y1 - label_size[1] - 10),
                (bbox.x1 + label_size[0], bbox.y1),
                color, -1
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
                5, color, -1
            )
        
        # Bilgi yazısı
        info_text = f"Detections: {len(detections)} | "
        info_text += f"Inference: {self.inference_time*1000:.1f}ms | "
        info_text += f"Mode: {'Mock' if self.mock_mode else 'YOLO'}"
        
        cv2.putText(
            annotated_frame, info_text,
            (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2
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
            "device": self.device or "mock",
            "model_loaded": self.model_loaded,
            "current_detections": len(self.last_detections),
            "mock_mode": self.mock_mode,
            "frame_count": self.frame_count,
            "yolo_available": YOLO_AVAILABLE
        }
    
    def set_mock_mode(self, enable_mock: bool):
        """Mock mode'u manuel olarak aç/kapat"""
        if enable_mock or not YOLO_AVAILABLE:
            self.mock_mode = True
            self.logger.info("Mock detection mode aktif")
        else:
            if self.model_loaded:
                self.mock_mode = False
                self.logger.info("YOLO detection mode aktif")
            else:
                self.logger.warning("YOLO modeli yüklü değil, mock mode devam ediyor")
    
    def cleanup(self):
        """Kaynakları temizle"""
        if self.model:
            try:
                # Model'i temizle
                del self.model
                self.model = None
                self.model_loaded = False
                
                # CUDA cache'i temizle
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
                    
                self.logger.info("YOLO model temizlendi")
            except Exception as e:
                self.logger.error(f"YOLO temizleme hatası: {e}")
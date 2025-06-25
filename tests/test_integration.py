# =======================
# tests/test_integration.py - Entegrasyon Testleri
# =======================

import unittest
import numpy as np
from unittest.mock import Mock, patch, MagicMock

from config.settings import Settings
from modules.system.logger import SystemLogger
from modules.camera.camera_interface import MockCamera
from modules.ai.yolo_detector import YOLODetector
from modules.tracking.target_tracker import TargetTracker
from modules.utils.data_structures import Detection, BoundingBox


class TestSystemIntegration(unittest.TestCase):
    """Sistem entegrasyon testleri"""
    
    def setUp(self):
        self.settings = Settings()
        self.logger = SystemLogger()
    
    def test_camera_yolo_integration(self):
        """Kamera-YOLO entegrasyonu testi"""
        # Mock kamera
        camera = MockCamera(640, 480)
        camera.initialize()
        camera.start_capture()
        
        # Test frame al
        frame = camera.get_rgb_frame()
        self.assertIsNotNone(frame)
        
        # YOLO detector (mock)
        with patch('ultralytics.YOLO'):
            detector = YOLODetector(self.settings.yolo, self.logger)
            
            # Model olmadan detection testi
            with patch.object(detector, 'model', None):
                detections = detector.detect_people(frame)
                self.assertIsInstance(detections, list)
    
    def test_detection_tracking_integration(self):
        """Tespit-takip entegrasyonu testi"""
        tracker = TargetTracker(self.settings.tracking, self.logger)
        
        # Sahte detection'lar oluştur
        detections = [
            Detection(
                id=1,
                bbox=BoundingBox(100, 100, 200, 300, 100, 200),
                confidence=0.8,
                class_name="person",
                center_x=150,
                center_y=200
            ),
            Detection(
                id=2,
                bbox=BoundingBox(300, 150, 400, 350, 100, 200),
                confidence=0.9,
                class_name="person",
                center_x=350,
                center_y=250
            )
        ]
        
        # Sahte depth frame
        depth_frame = np.random.randint(1000, 3000, (480, 640), dtype=np.uint16)
        
        # Tracking güncellemesi
        primary_target = tracker.update_targets(detections, depth_frame)
        
        # Sonuçları kontrol et
        all_targets = tracker.get_all_targets()
        self.assertEqual(len(all_targets), 2)
        self.assertIsNotNone(primary_target)
    
    def test_settings_loading_saving(self):
        """Ayar yükleme-kaydetme testi"""
        settings = Settings()
        
        # Bir ayarı değiştir
        original_fps = settings.camera.fps
        settings.camera.fps = 60
        
        # Kaydet
        settings.save_settings()
        
        # Yeni nesne oluştur ve yükle
        new_settings = Settings()
        
        # FPS değişikliği yüklenmiş olmalı
        self.assertEqual(new_settings.camera.fps, 60)
        
        # Orijinal değeri geri yükle
        settings.camera.fps = original_fps
        settings.save_settings()
    
    def test_system_performance_monitoring(self):
        """Sistem performans izleme testi"""
        from modules.system.monitor import SystemMonitor
        
        monitor = SystemMonitor()
        status = monitor.get_system_status()
        
        # Temel sistem bilgilerinin okunabildiğini kontrol et
        self.assertIsInstance(status.cpu_usage, float)
        self.assertIsInstance(status.memory_usage, float)
        self.assertGreaterEqual(status.cpu_usage, 0)
        self.assertLessEqual(status.cpu_usage, 100)


class TestDataFlow(unittest.TestCase):
    """Veri akışı testleri"""
    
    def test_detection_to_servo_pipeline(self):
        """Tespit'ten servo'ya veri akışı testi"""
        # Tespit verisi oluştur
        detection = Detection(
            id=1,
            bbox=BoundingBox(200, 150, 400, 450, 200, 300),
            confidence=0.85,
            class_name="person",
            center_x=300,  # Frame ortasında
            center_y=300
        )
        
        # Servo açıları hesaplama fonksiyonunu test et
        from modules.utils.math_utils import calculate_servo_angles_for_point
        
        pan_angle, tilt_angle = calculate_servo_angles_for_point(
            detection.center_x, detection.center_y, 640, 480
        )
        
        # Açıların makul aralıkta olduğunu kontrol et
        self.assertGreaterEqual(pan_angle, 30)
        self.assertLessEqual(pan_angle, 150)
        self.assertGreaterEqual(tilt_angle, 60)
        self.assertLessEqual(tilt_angle, 120)
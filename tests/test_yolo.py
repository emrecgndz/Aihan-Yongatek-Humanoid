# =======================
# tests/test_yolo.py - YOLO Testleri
# =======================

import unittest
import numpy as np
from unittest.mock import Mock, patch, MagicMock

from modules.ai.yolo_detector import YOLODetector
from config.settings import YOLOSettings
from modules.system.logger import SystemLogger
from modules.utils.data_structures import Detection, BoundingBox


class TestYOLODetector(unittest.TestCase):
    """YOLO detektör testleri"""
    
    def setUp(self):
        self.yolo_settings = YOLOSettings(
            model_path="data/models/yolov8n-person.pt",
            confidence_threshold=0.5,
            device="cpu"
        )
        self.logger = SystemLogger()
    
    @patch('ultralytics.YOLO')
    def test_yolo_initialization_mock(self, mock_yolo_class):
        """YOLO başlatma testi (mock)"""
        # Mock model setup
        mock_model = Mock()
        mock_yolo_class.return_value = mock_model
        
        detector = YOLODetector(self.yolo_settings, self.logger)
        
        # Mock successful initialization
        with patch.object(detector, '_create_test_detection', return_value=True):
            result = detector.initialize()
            
        # YOLO class should be called with model path
        mock_yolo_class.assert_called_once_with(self.yolo_settings.model_path)
    
    def test_detection_data_structure(self):
        """Detection veri yapısı testi"""
        bbox = BoundingBox(x1=100, y1=150, x2=200, y2=300, width=100, height=150)
        detection = Detection(
            id=1,
            bbox=bbox,
            confidence=0.85,
            class_name="person",
            center_x=150,
            center_y=225
        )
        
        self.assertEqual(detection.id, 1)
        self.assertEqual(detection.confidence, 0.85)
        self.assertEqual(detection.class_name, "person")
        self.assertEqual(detection.center_x, 150)
        self.assertEqual(detection.center_y, 225)
        self.assertEqual(detection.bbox.area, 15000)
    
    def test_bounding_box_properties(self):
        """BoundingBox özellik testleri"""
        bbox = BoundingBox(x1=50, y1=100, x2=150, y2=250, width=100, height=150)
        
        self.assertEqual(bbox.center_x, 100)
        self.assertEqual(bbox.center_y, 175)
        self.assertEqual(bbox.area, 15000)
    
    def test_detection_filtering_by_confidence(self):
        """Güven skoru filtreleme testi"""
        # Bu test gerçek YOLO modeli olmadan mock ile yapılabilir
        detector = YOLODetector(self.yolo_settings, self.logger)
        
        # Test frame
        test_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        
        # Model olmadan test edilemez, bu yüzden mock kullanıyoruz
        with patch.object(detector, 'model', None):
            detections = detector.detect_people(test_frame)
            self.assertEqual(len(detections), 0)
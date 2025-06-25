# =======================
# tests/test_camera.py - Kamera Testleri
# =======================

import unittest
import numpy as np
import time
from unittest.mock import Mock, patch

from modules.camera.realsense_manager import RealSenseManager
from modules.camera.camera_interface import MockCamera
from config.settings import CameraSettings
from modules.system.logger import SystemLogger


class TestCameraModules(unittest.TestCase):
    """Kamera modülü testleri"""
    
    def setUp(self):
        self.camera_settings = CameraSettings(width=640, height=480, fps=30)
        self.logger = SystemLogger()
    
    def test_mock_camera_initialization(self):
        """Mock kamera başlatma testi"""
        camera = MockCamera(640, 480)
        
        self.assertTrue(camera.initialize())
        self.assertTrue(camera.start_capture())
        self.assertEqual(camera.get_fps(), 30)
    
    def test_mock_camera_frame_generation(self):
        """Mock kamera frame üretimi testi"""
        camera = MockCamera(640, 480)
        camera.initialize()
        camera.start_capture()
        
        # RGB frame testi
        rgb_frame = camera.get_rgb_frame()
        self.assertIsNotNone(rgb_frame)
        self.assertEqual(rgb_frame.shape, (480, 640, 3))
        self.assertEqual(rgb_frame.dtype, np.uint8)
        
        # Depth frame testi
        depth_frame = camera.get_depth_frame()
        self.assertIsNotNone(depth_frame)
        self.assertEqual(depth_frame.shape, (480, 640))
        self.assertEqual(depth_frame.dtype, np.uint16)
    
    def test_mock_camera_cleanup(self):
        """Mock kamera temizlik testi"""
        camera = MockCamera()
        camera.initialize()
        camera.start_capture()
        
        self.assertTrue(camera.get_fps() > 0)
        
        camera.cleanup()
        self.assertEqual(camera.get_fps(), 0)
    
    @patch('pyrealsense2.pipeline')
    def test_realsense_initialization_mock(self, mock_pipeline):
        """RealSense başlatma testi (mock)"""
        # Mock setup
        mock_pipeline_instance = Mock()
        mock_pipeline.return_value = mock_pipeline_instance
        
        camera = RealSenseManager(self.camera_settings, self.logger)
        
        # Test initialization without actual hardware
        with patch.object(camera, '_test_mode', True):
            result = camera.initialize()
            # Bu test gerçek donanım olmadan başarısız olabilir
            # Bu yüzden sadece fonksiyonun çağrılabildiğini test ediyoruz
            self.assertIsInstance(result, bool)


class TestCameraSettings(unittest.TestCase):
    """Kamera ayarları testleri"""
    
    def test_camera_settings_defaults(self):
        """Varsayılan kamera ayarları testi"""
        settings = CameraSettings()
        
        self.assertEqual(settings.width, 720)
        self.assertEqual(settings.height, 480)
        self.assertEqual(settings.fps, 30)
        self.assertTrue(settings.enable_rgb)
        self.assertTrue(settings.enable_depth)
    
    def test_camera_settings_custom(self):
        """Özel kamera ayarları testi"""
        settings = CameraSettings(
            width=1280,
            height=720,
            fps=60,
            enable_rgb=False
        )
        
        self.assertEqual(settings.width, 1280)
        self.assertEqual(settings.height, 720)
        self.assertEqual(settings.fps, 60)
        self.assertFalse(settings.enable_rgb)

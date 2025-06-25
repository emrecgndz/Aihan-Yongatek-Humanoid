# =======================
# tests/test_servo.py - Servo Testleri
# =======================

import unittest
from unittest.mock import Mock, patch

from modules.servo.servo_controller import ServoController, ArmPosition
from modules.servo.arduino_comm import ArduinoComm
from config.settings import ServoSettings
from config.constants import ServoIDs
from modules.system.logger import SystemLogger


class TestServoController(unittest.TestCase):
    """Servo kontrolcü testleri"""
    
    def setUp(self):
        self.servo_settings = ServoSettings(
            port="/dev/ttyUSB0",
            baudrate=115200,
            movement_speed=5
        )
        self.logger = SystemLogger()
    
    @patch('serial.Serial')
    def test_arduino_comm_mock(self, mock_serial):
        """Arduino iletişim testi (mock)"""
        # Mock serial port
        mock_serial_instance = Mock()
        mock_serial.return_value = mock_serial_instance
        mock_serial_instance.is_open = True
        
        arduino = ArduinoComm(self.servo_settings, self.logger)
        
        # Test connection (mock)
        with patch.object(arduino, '_ping_arduino', return_value=True):
            result = arduino.connect()
            # Gerçek donanım olmadan test etmek zor
            mock_serial.assert_called_once()
    
    def test_servo_angle_limits(self):
        """Servo açı limitleri testi"""
        arduino_mock = Mock()
        arduino_mock.is_connected = True
        arduino_mock.set_servo_angle.return_value = True
        
        controller = ServoController(self.servo_settings, self.logger)
        controller.arduino = arduino_mock
        
        # Geçerli açı
        result = controller.set_servo_angle(ServoIDs.HEAD_PAN.value, 90)
        self.assertTrue(result)
        
        # Geçersiz açı (negatif)
        result = controller.set_servo_angle(ServoIDs.HEAD_PAN.value, -10, check_limits=True)
        self.assertFalse(result)
        
        # Geçersiz açı (çok yüksek)
        result = controller.set_servo_angle(ServoIDs.HEAD_PAN.value, 200, check_limits=True)
        self.assertFalse(result)
    
    def test_arm_position_setting(self):
        """Kol pozisyonu ayarlama testi"""
        arduino_mock = Mock()
        arduino_mock.is_connected = True
        arduino_mock.set_servo_angle.return_value = True
        
        controller = ServoController(self.servo_settings, self.logger)
        controller.arduino = arduino_mock
        
        # Test arm position
        arm_position = ArmPosition(
            shoulder=45,
            elbow=90,
            wrist=135,
            hand=90
        )
        
        with patch.object(controller, 'set_servo_angle', return_value=True) as mock_set_servo:
            result = controller.set_arm_position('right', arm_position)
            
            # set_servo_angle should be called multiple times for each joint
            self.assertTrue(mock_set_servo.call_count >= 6)  # 6 servos per arm
    
    def test_head_position_calculation(self):
        """Kafa pozisyonu hesaplama testi"""
        arduino_mock = Mock()
        arduino_mock.is_connected = True
        
        controller = ServoController(self.servo_settings, self.logger)
        controller.arduino = arduino_mock
        
        with patch.object(controller, 'set_servo_angle', return_value=True) as mock_set_servo:
            # Test pointing to center of frame
            controller.point_to_position(320, 240, 640, 480)
            
            # Should call set_servo_angle for head servos
            mock_set_servo.assert_called()


class TestArmPosition(unittest.TestCase):
    """ArmPosition veri yapısı testleri"""
    
    def test_arm_position_creation(self):
        """ArmPosition oluşturma testi"""
        position = ArmPosition(
            shoulder=45,
            elbow=90,
            wrist=135
        )
        
        self.assertEqual(position.shoulder, 45)
        self.assertEqual(position.elbow, 90)
        self.assertEqual(position.wrist, 135)
        self.assertEqual(position.hand, 90)  # Default value
        self.assertEqual(position.thumb, 90)  # Default value
# =======================
# modules/servo/servo_controller.py - Servo Motor Kontrolü
# =======================

import math
import time
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

from config.settings import ServoSettings
from config.constants import ServoIDs
from modules.servo.arduino_comm import ArduinoComm
from modules.system.logger import SystemLogger


@dataclass
class ServoPosition:
    """Servo pozisyon bilgisi"""
    servo_id: int
    angle: int
    timestamp: float
    
@dataclass
class ArmPosition:
    """Kol pozisyon bilgisi"""
    shoulder: int
    elbow: int
    wrist: int
    hand: int = 90
    thumb: int = 90
    index: int = 90


class ServoController:
    """14 DOF servo motor kontrolcüsü"""
    
    def __init__(self, settings: ServoSettings, logger: SystemLogger):
        self.settings = settings
        self.logger = logger
        
        # Arduino iletişimi
        self.arduino = ArduinoComm(settings, logger)
        
        # Mevcut pozisyonlar
        self.current_positions = {}
        self.target_positions = {}
        
        # Hareket kontrolü
        self.is_moving = False
        self.movement_speed = settings.movement_speed
        
        # Güvenlik limitleri
        self.servo_limits = self._load_servo_limits()
        
    def initialize(self) -> bool:
        """Servo kontrolcüsünü başlat"""
        if not self.arduino.connect():
            return False
        
        # Servolar merkez pozisyona al
        self.calibrate_all_servos()
        self.logger.info("Servo kontrolcüsü başlatıldı")
        return True
    
    def _load_servo_limits(self) -> Dict[int, Tuple[int, int]]:
        """Servo açı limitlerini yükle"""
        limits = {}
        
        # Kol limitleri
        for servo_name, (min_angle, max_angle) in self.settings.arm_limits.items():
            if "left" in servo_name:
                servo_id = getattr(ServoIDs, servo_name.upper().replace("LEFT_", "LEFT_"))
            else:
                servo_id = getattr(ServoIDs, servo_name.upper().replace("RIGHT_", "RIGHT_"))
            limits[servo_id.value] = (min_angle, max_angle)
        
        # Kafa limitleri
        for servo_name, (min_angle, max_angle) in self.settings.head_limits.items():
            servo_id = getattr(ServoIDs, servo_name.upper())
            limits[servo_id.value] = (min_angle, max_angle)
        
        return limits
    
    def calibrate_all_servos(self):
        """Tüm servoları merkez pozisyona getir"""
        self.arduino.calibrate_servos()
        
        # Mevcut pozisyonları güncelle
        for servo_id in ServoIDs:
            self.current_positions[servo_id.value] = 90
            self.target_positions[servo_id.value] = 90
        
        time.sleep(2)  # Hareket tamamlanana kadar bekle
        self.logger.info("Tüm servolar kalibre edildi")
    
    def set_servo_angle(self, servo_id: int, angle: int, check_limits: bool = True) -> bool:
        """Tekil servo açısını ayarla"""
        if check_limits and servo_id in self.servo_limits:
            min_angle, max_angle = self.servo_limits[servo_id]
            if not (min_angle <= angle <= max_angle):
                self.logger.warning(f"Servo {servo_id} için açı limit dışı: {angle}")
                return False
        
        success = self.arduino.set_servo_angle(servo_id, angle)
        if success:
            self.current_positions[servo_id] = angle
        
        return success
    
    def set_arm_position(self, arm: str, position: ArmPosition) -> bool:
        """Kol pozisyonunu ayarla (left/right)"""
        if arm not in ['left', 'right']:
            return False
        
        # Servo ID'lerini belirle
        if arm == 'left':
            shoulder_id = ServoIDs.LEFT_SHOULDER.value
            elbow_id = ServoIDs.LEFT_ELBOW.value
            wrist_id = ServoIDs.LEFT_WRIST.value
            hand_id = ServoIDs.LEFT_HAND.value
            thumb_id = ServoIDs.LEFT_THUMB.value
            index_id = ServoIDs.LEFT_INDEX.value
        else:
            shoulder_id = ServoIDs.RIGHT_SHOULDER.value
            elbow_id = ServoIDs.RIGHT_ELBOW.value
            wrist_id = ServoIDs.RIGHT_WRIST.value
            hand_id = ServoIDs.RIGHT_HAND.value
            thumb_id = ServoIDs.RIGHT_THUMB.value
            index_id = ServoIDs.RIGHT_INDEX.value
        
        # Tüm servolar için açıları ayarla
        success = True
        success &= self.set_servo_angle(shoulder_id, position.shoulder)
        success &= self.set_servo_angle(elbow_id, position.elbow)
        success &= self.set_servo_angle(wrist_id, position.wrist)
        success &= self.set_servo_angle(hand_id, position.hand)
        success &= self.set_servo_angle(thumb_id, position.thumb)
        success &= self.set_servo_angle(index_id, position.index)
        
        return success
    
    def set_head_position(self, pan: int, tilt: int) -> bool:
        """Kafa pozisyonunu ayarla"""
        success = True
        success &= self.set_servo_angle(ServoIDs.HEAD_PAN.value, pan)
        success &= self.set_servo_angle(ServoIDs.HEAD_TILT.value, tilt)
        return success
    
    def point_to_position(self, x: int, y: int, frame_width: int, frame_height: int):
        """Ekrandaki bir noktaya doğru kafa ve kolları yönlendir"""
        # Kafa için pan/tilt hesapla
        pan_angle = int(90 + (x - frame_width/2) / frame_width * 60)  # ±30 derece
        tilt_angle = int(90 - (y - frame_height/2) / frame_height * 40)  # ±20 derece
        
        # Limitleri kontrol et
        pan_angle = max(60, min(120, pan_angle))
        tilt_angle = max(70, min(110, tilt_angle))
        
        # Kafa pozisyonunu ayarla
        self.set_head_position(pan_angle, tilt_angle)
        
        # Sol kol ile işaret et
        if x < frame_width / 2:  # Sol taraf
            shoulder_angle = 45  # Kolun yukselmesi
            elbow_angle = 135     # Dirsek kıvrımı
            wrist_angle = 90      # Bilek düz
        else:  # Sağ taraf
            shoulder_angle = 135  # Kolun yukselmesi
            elbow_angle = 45      # Dirsek kıvrımı
            wrist_angle = 90      # Bilek düz
        
        # İşaret etme pozisyonu
        pointing_position = ArmPosition(
            shoulder=shoulder_angle,
            elbow=elbow_angle,
            wrist=wrist_angle,
            hand=90,
            thumb=90,
            index=180  # İşaret parmağı uzatılmış
        )
        
        # Hangi kol kullanılacak
        arm = 'left' if x < frame_width / 2 else 'right'
        self.set_arm_position(arm, pointing_position)
    
    def wave_gesture(self, arm: str = 'right'):
        """El sallama jesti"""
        if arm not in ['left', 'right']:
            return
        
        # Başlangıç pozisyonu - kol yukarı
        wave_up = ArmPosition(
            shoulder=45,
            elbow=90,
            wrist=90,
            hand=90
        )
        
        # El sallama pozisyonu
        wave_side = ArmPosition(
            shoulder=45,
            elbow=90,
            wrist=135,  # El yana
            hand=90
        )
        
        # El sallama animasyonu
        for _ in range(3):
            self.set_arm_position(arm, wave_up)
            time.sleep(0.5)
            self.set_arm_position(arm, wave_side)
            time.sleep(0.5)
        
        # Kol aşağı
        rest_position = ArmPosition(
            shoulder=90,
            elbow=90,
            wrist=90,
            hand=90
        )
        self.set_arm_position(arm, rest_position)
    
    def set_movement_speed(self, speed: int):
        """Hareket hızını ayarla (1-10)"""
        if 1 <= speed <= 10:
            self.movement_speed = speed
            self.arduino.set_servo_speed(speed)
    
    def get_current_positions(self) -> Dict[int, int]:
        """Mevcut servo pozisyonlarını döndür"""
        return self.current_positions.copy()
    
    def is_arduino_connected(self) -> bool:
        """Arduino bağlantı durumunu döndür"""
        return self.arduino.is_connected
    
    def cleanup(self):
        """Kaynakları temizle"""
        self.arduino.disconnect()
        self.logger.info("Servo kontrolcüsü temizlendi")

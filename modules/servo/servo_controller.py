# =======================
# modules/servo/servo_controller.py - Animation Engine Entegrasyonlu
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
    """14 DOF servo motor kontrolcüsü - Animation Engine Entegrasyonlu"""
    
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
        self.last_command = None
        
        # Güvenlik limitleri
        self.servo_limits = self._load_servo_limits()
        
        # Animation engine (lazy loading)
        self._animation_engine = None
        
        # Mock mode (Arduino yoksa)
        self.mock_mode = False
        
    @property
    def animation_engine(self):
        """Animation engine'i lazy loading ile al"""
        if self._animation_engine is None:
            try:
                from modules.servo.animation_engine import AnimationEngine
                self._animation_engine = AnimationEngine(self, self.logger)
                self.logger.info("Animation engine yüklendi")
            except ImportError as e:
                self.logger.warning(f"Animation engine yüklenemedi: {e}")
                # Mock animation engine
                self._animation_engine = MockAnimationEngine(self.logger)
        return self._animation_engine
        
    def initialize(self) -> bool:
        """Servo kontrolcüsünü başlat"""
        try:
            if not self.arduino.connect():
                self.logger.warning("Arduino bağlanamadı, mock mode aktif")
                self.mock_mode = True
                self._initialize_mock_positions()
                return True
            
            # Servolar merkez pozisyona al
            self.calibrate_all_servos()
            self.logger.info("Servo kontrolcüsü başlatıldı")
            return True
            
        except Exception as e:
            self.logger.error(f"Servo başlatma hatası: {e}")
            self.mock_mode = True
            self._initialize_mock_positions()
            return True
    
    def _initialize_mock_positions(self):
        """Mock pozisyonları başlat"""
        for servo_id in ServoIDs:
            self.current_positions[servo_id.value] = 90
            self.target_positions[servo_id.value] = 90
    
    def _load_servo_limits(self) -> Dict[int, Tuple[int, int]]:
        """Servo açı limitlerini yükle"""
        limits = {}
        
        # Kol limitleri
        arm_servo_mapping = {
            "shoulder_left": ServoIDs.LEFT_SHOULDER,
            "elbow_left": ServoIDs.LEFT_ELBOW,
            "wrist_left": ServoIDs.LEFT_WRIST,
            "shoulder_right": ServoIDs.RIGHT_SHOULDER,
            "elbow_right": ServoIDs.RIGHT_ELBOW,
            "wrist_right": ServoIDs.RIGHT_WRIST
        }
        
        for servo_name, (min_angle, max_angle) in self.settings.arm_limits.items():
            if servo_name in arm_servo_mapping:
                servo_id = arm_servo_mapping[servo_name]
                limits[servo_id.value] = (min_angle, max_angle)
        
        # Kafa limitleri
        head_servo_mapping = {
            "head_pan": ServoIDs.HEAD_PAN,
            "head_tilt": ServoIDs.HEAD_TILT
        }
        
        for servo_name, (min_angle, max_angle) in self.settings.head_limits.items():
            if servo_name in head_servo_mapping:
                servo_id = head_servo_mapping[servo_name]
                limits[servo_id.value] = (min_angle, max_angle)
        
        return limits
    
    def calibrate_all_servos(self):
        """Tüm servoları merkez pozisyona getir"""
        if self.mock_mode:
            self.logger.info("Mock servo kalibrasyonu")
            self._initialize_mock_positions()
            return
            
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
        
        if self.mock_mode:
            # Mock mode
            self.current_positions[servo_id] = angle
            self.last_command = f"Mock: Servo {servo_id} -> {angle}°"
            self.logger.debug(f"Mock servo {servo_id}: {angle}°")
            return True
        
        success = self.arduino.set_servo_angle(servo_id, angle)
        if success:
            self.current_positions[servo_id] = angle
            self.last_command = f"Servo {servo_id} -> {angle}°"
        
        return success
    
    def set_arm_position(self, arm: str, position: ArmPosition) -> bool:
        """Kol pozisyonunu ayarla (left/right)"""
        if arm not in ['left', 'right']:
            return False
        
        # Servo ID'lerini belirle
        if arm == 'left':
            servo_ids = [
                ServoIDs.LEFT_SHOULDER.value,
                ServoIDs.LEFT_ELBOW.value,
                ServoIDs.LEFT_WRIST.value,
                ServoIDs.LEFT_HAND.value,
                ServoIDs.LEFT_THUMB.value,
                ServoIDs.LEFT_INDEX.value
            ]
        else:
            servo_ids = [
                ServoIDs.RIGHT_SHOULDER.value,
                ServoIDs.RIGHT_ELBOW.value,
                ServoIDs.RIGHT_WRIST.value,
                ServoIDs.RIGHT_HAND.value,
                ServoIDs.RIGHT_THUMB.value,
                ServoIDs.RIGHT_INDEX.value
            ]
        
        angles = [
            position.shoulder,
            position.elbow,
            position.wrist,
            position.hand,
            position.thumb,
            position.index
        ]
        
        # Tüm servolar için açıları ayarla
        success = True
        for servo_id, angle in zip(servo_ids, angles):
            success &= self.set_servo_angle(servo_id, angle)
        
        if success:
            self.last_command = f"{arm.title()} kol pozisyonu ayarlandı"
        
        return success
    
    def set_head_position(self, pan: int, tilt: int) -> bool:
        """Kafa pozisyonunu ayarla"""
        success = True
        success &= self.set_servo_angle(ServoIDs.HEAD_PAN.value, pan)
        success &= self.set_servo_angle(ServoIDs.HEAD_TILT.value, tilt)
        
        if success:
            self.last_command = f"Kafa pozisyonu: Pan={pan}°, Tilt={tilt}°"
        
        return success
    
    def point_to_position(self, x: int, y: int, frame_width: int, frame_height: int):
        """Ekrandaki bir noktaya doğru kafa ve kolları yönlendir"""
        try:
            # Kafa için pan/tilt hesapla
            pan_angle = int(90 + (x - frame_width/2) / frame_width * 60)  # ±30 derece
            tilt_angle = int(90 - (y - frame_height/2) / frame_height * 40)  # ±20 derece
            
            # Limitleri kontrol et
            pan_angle = max(30, min(150, pan_angle))
            tilt_angle = max(60, min(120, tilt_angle))
            
            # Kafa pozisyonunu ayarla
            self.set_head_position(pan_angle, tilt_angle)
            
            # İşaret etme hareketi (isteğe bağlı)
            if x < frame_width / 2:  # Sol taraf
                self._point_with_arm('left', x, y, frame_width, frame_height)
            else:  # Sağ taraf
                self._point_with_arm('right', x, y, frame_width, frame_height)
                
        except Exception as e:
            self.logger.error(f"Point to position hatası: {e}")
    
    def _point_with_arm(self, arm: str, x: int, y: int, frame_width: int, frame_height: int):
        """Belirli bir kolla işaret etme"""
        try:
            # Basit işaret etme pozisyonu
            if arm == 'left':
                shoulder_angle = 45 if x < frame_width / 3 else 60
                elbow_angle = 135
                wrist_angle = 90
            else:  # right
                shoulder_angle = 135 if x > 2 * frame_width / 3 else 120
                elbow_angle = 45
                wrist_angle = 90
            
            pointing_position = ArmPosition(
                shoulder=shoulder_angle,
                elbow=elbow_angle,
                wrist=wrist_angle,
                hand=90,
                thumb=90,
                index=180  # İşaret parmağı uzatılmış
            )
            
            self.set_arm_position(arm, pointing_position)
            
        except Exception as e:
            self.logger.error(f"Arm pointing hatası: {e}")
    
    def wave_gesture(self, arm: str = 'right'):
        """El sallama jesti"""
        if arm not in ['left', 'right']:
            return
        
        try:
            # Animasyon engine kullan
            if hasattr(self.animation_engine, 'play_animation'):
                self.animation_engine.play_animation('wave')
            else:
                # Manuel el sallama
                self._manual_wave_gesture(arm)
                
        except Exception as e:
            self.logger.error(f"Wave gesture hatası: {e}")
    
    def _manual_wave_gesture(self, arm: str):
        """Manuel el sallama animasyonu"""
        # Başlangıç pozisyonu - kol yukarı
        wave_up = ArmPosition(
            shoulder=45 if arm == 'right' else 135,
            elbow=90,
            wrist=90,
            hand=90
        )
        
        # El sallama pozisyonu
        wave_side = ArmPosition(
            shoulder=45 if arm == 'right' else 135,
            elbow=90,
            wrist=135 if arm == 'right' else 45,
            hand=90
        )
        
        # El sallama animasyonu
        for _ in range(3):
            self.set_arm_position(arm, wave_up)
            time.sleep(0.5)
            self.set_arm_position(arm, wave_side)
            time.sleep(0.5)
        
        # Kol aşağı (rest position)
        rest_position = ArmPosition(
            shoulder=90,
            elbow=90,
            wrist=90,
            hand=90
        )
        self.set_arm_position(arm, rest_position)
    
    def play_animation(self, animation_name: str) -> bool:
        """Animasyon oynat"""
        try:
            if self.animation_engine:
                return self.animation_engine.play_animation(animation_name)
            else:
                self.logger.warning("Animation engine mevcut değil")
                return False
        except Exception as e:
            self.logger.error(f"Animasyon oynatma hatası: {e}")
            return False
    
    def stop_animation(self):
        """Mevcut animasyonu durdur"""
        try:
            if self.animation_engine:
                self.animation_engine.stop_animation()
        except Exception as e:
            self.logger.error(f"Animasyon durdurma hatası: {e}")
    
    def get_available_animations(self) -> List[str]:
        """Kullanılabilir animasyonları listele"""
        try:
            if self.animation_engine:
                return self.animation_engine.get_available_animations()
            else:
                return ["wave", "greeting", "goodbye"]  # Varsayılan liste
        except Exception as e:
            self.logger.error(f"Animasyon listesi hatası: {e}")
            return []
    
    def set_movement_speed(self, speed: int):
        """Hareket hızını ayarla (1-10)"""
        if 1 <= speed <= 10:
            self.movement_speed = speed
            if not self.mock_mode:
                self.arduino.set_servo_speed(speed)
            self.last_command = f"Hız ayarlandı: {speed}"
    
    def get_current_positions(self) -> Dict[int, int]:
        """Mevcut servo pozisyonlarını döndür"""
        return self.current_positions.copy()
    
    def is_arduino_connected(self) -> bool:
        """Arduino bağlantı durumunu döndür"""
        if self.mock_mode:
            return False
        return self.arduino.is_connected
    
    def get_status(self) -> Dict[str, any]:
        """Servo kontrolcü durumunu döndür"""
        return {
            "arduino_connected": self.is_arduino_connected(),
            "mock_mode": self.mock_mode,
            "is_moving": self.is_moving,
            "movement_speed": self.movement_speed,
            "last_command": self.last_command,
            "servo_count": len(self.current_positions),
            "animation_engine_loaded": self._animation_engine is not None
        }
    
    def cleanup(self):
        """Kaynakları temizle"""
        try:
            # Animasyonu durdur
            self.stop_animation()
            
            # Arduino bağlantısını kapat
            if not self.mock_mode:
                self.arduino.disconnect()
            
            self.logger.info("Servo kontrolcüsü temizlendi")
            
        except Exception as e:
            self.logger.error(f"Servo cleanup hatası: {e}")


class MockAnimationEngine:
    """Animation engine yoksa kullanılacak mock"""
    
    def __init__(self, logger):
        self.logger = logger
        
    def play_animation(self, animation_name: str) -> bool:
        self.logger.info(f"Mock animasyon oynatılıyor: {animation_name}")
        return True
        
    def stop_animation(self):
        self.logger.info("Mock animasyon durduruldu")
        
    def get_available_animations(self) -> List[str]:
        return ["greeting", "goodbye", "wave", "thinking"]
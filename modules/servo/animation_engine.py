# =======================
# modules/servo/animation_engine.py - Animasyon Motoru
# =======================

import json
import time
import math
from threading import Thread, Event
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
from pathlib import Path

from config.constants import ServoIDs
from modules.servo.servo_controller import ServoController, ArmPosition
from modules.system.logger import SystemLogger


@dataclass
class KeyFrame:
    """Animasyon anahtar karesi"""
    timestamp: float  # saniye
    servo_positions: Dict[int, int]  # servo_id: angle
    duration: float = 0.5  # bu frame'e geçiş süresi
    easing: str = "linear"  # linear, ease_in, ease_out, ease_in_out


@dataclass
class Animation:
    """Animasyon tanımı"""
    name: str
    description: str
    keyframes: List[KeyFrame]
    loop: bool = False
    total_duration: float = 0.0
    
    def __post_init__(self):
        if self.keyframes:
            self.total_duration = max(kf.timestamp for kf in self.keyframes)


class AnimationEngine:
    """Servo animasyon motoru"""
    
    def __init__(self, servo_controller: ServoController, logger: SystemLogger):
        self.servo_controller = servo_controller
        self.logger = logger
        
        # Animasyon verileri
        self.animations: Dict[str, Animation] = {}
        self.animation_path = Path("data/animations")
        
        # Oynatma kontrolü
        self.current_animation: Optional[Animation] = None
        self.is_playing = False
        self.animation_thread: Optional[Thread] = None
        self.stop_event = Event()
        
        # Callback'ler
        self.on_animation_complete: Optional[Callable] = None
        self.on_animation_start: Optional[Callable] = None
        
        # Yüklü animasyonları başlat
        self.load_default_animations()
    
    def load_default_animations(self):
        """Varsayılan animasyonları yükle"""
        try:
            self.animation_path.mkdir(parents=True, exist_ok=True)
            
            # Varsayılan animasyonları oluştur
            self._create_default_animations()
            
            # Dosyalardan animasyonları yükle
            for animation_file in self.animation_path.glob("*.json"):
                self.load_animation_from_file(animation_file)
                
        except Exception as e:
            self.logger.error(f"Varsayılan animasyonlar yüklenirken hata: {e}")
    
    def _create_default_animations(self):
        """Varsayılan animasyon dosyalarını oluştur"""
        # Selamlama animasyonu
        greeting_animation = {
            "name": "greeting",
            "description": "Selamlama hareketi",
            "loop": False,
            "keyframes": [
                {
                    "timestamp": 0.0,
                    "servo_positions": {servo.value: 90 for servo in ServoIDs},
                    "duration": 0.5,
                    "easing": "ease_out"
                },
                {
                    "timestamp": 1.0,
                    "servo_positions": {
                        ServoIDs.RIGHT_SHOULDER.value: 45,
                        ServoIDs.RIGHT_ELBOW.value: 90,
                        ServoIDs.RIGHT_WRIST.value: 135,
                        ServoIDs.HEAD_PAN.value: 90,
                        ServoIDs.HEAD_TILT.value: 85
                    },
                    "duration": 1.0,
                    "easing": "ease_in_out"
                },
                {
                    "timestamp": 2.0,
                    "servo_positions": {
                        ServoIDs.RIGHT_SHOULDER.value: 45,
                        ServoIDs.RIGHT_ELBOW.value: 90,
                        ServoIDs.RIGHT_WRIST.value: 90,
                        ServoIDs.HEAD_PAN.value: 90,
                        ServoIDs.HEAD_TILT.value: 85
                    },
                    "duration": 0.5,
                    "easing": "ease_in_out"
                },
                {
                    "timestamp": 3.0,
                    "servo_positions": {servo.value: 90 for servo in ServoIDs},
                    "duration": 1.0,
                    "easing": "ease_in"
                }
            ]
        }
        
        # Vedalaşma animasyonu
        goodbye_animation = {
            "name": "goodbye",
            "description": "Vedalaşma hareketi",
            "loop": False,
            "keyframes": [
                {
                    "timestamp": 0.0,
                    "servo_positions": {servo.value: 90 for servo in ServoIDs},
                    "duration": 0.5
                },
                {
                    "timestamp": 1.0,
                    "servo_positions": {
                        ServoIDs.LEFT_SHOULDER.value: 45,
                        ServoIDs.LEFT_ELBOW.value: 45,
                        ServoIDs.LEFT_WRIST.value: 90,
                        ServoIDs.RIGHT_SHOULDER.value: 135,
                        ServoIDs.RIGHT_ELBOW.value: 135,
                        ServoIDs.RIGHT_WRIST.value: 90,
                        ServoIDs.HEAD_TILT.value: 80
                    },
                    "duration": 1.5
                },
                {
                    "timestamp": 3.0,
                    "servo_positions": {servo.value: 90 for servo in ServoIDs},
                    "duration": 1.0
                }
            ]
        }
        
        # Düşünme animasyonu
        thinking_animation = {
            "name": "thinking",
            "description": "Düşünme hareketi",
            "loop": True,
            "keyframes": [
                {
                    "timestamp": 0.0,
                    "servo_positions": {
                        ServoIDs.RIGHT_SHOULDER.value: 60,
                        ServoIDs.RIGHT_ELBOW.value: 45,
                        ServoIDs.RIGHT_WRIST.value: 90,
                        ServoIDs.HEAD_TILT.value: 95,
                        ServoIDs.HEAD_PAN.value: 85
                    },
                    "duration": 1.0
                },
                {
                    "timestamp": 2.0,
                    "servo_positions": {
                        ServoIDs.HEAD_PAN.value: 95
                    },
                    "duration": 1.0
                },
                {
                    "timestamp": 4.0,
                    "servo_positions": {
                        ServoIDs.HEAD_PAN.value: 85
                    },
                    "duration": 1.0
                }
            ]
        }
        
        # Dosyalara kaydet
        animations = [greeting_animation, goodbye_animation, thinking_animation]
        
        for anim_data in animations:
            file_path = self.animation_path / f"{anim_data['name']}.json"
            if not file_path.exists():
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(anim_data, f, indent=2, ensure_ascii=False)
    
    def load_animation_from_file(self, file_path: Path) -> bool:
        """Dosyadan animasyon yükle"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # KeyFrame nesneleri oluştur
            keyframes = []
            for kf_data in data.get('keyframes', []):
                keyframe = KeyFrame(
                    timestamp=kf_data['timestamp'],
                    servo_positions=kf_data['servo_positions'],
                    duration=kf_data.get('duration', 0.5),
                    easing=kf_data.get('easing', 'linear')
                )
                keyframes.append(keyframe)
            
            # Animation nesnesi oluştur
            animation = Animation(
                name=data['name'],
                description=data.get('description', ''),
                keyframes=keyframes,
                loop=data.get('loop', False)
            )
            
            self.animations[animation.name] = animation
            self.logger.info(f"Animasyon yüklendi: {animation.name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Animasyon yükleme hatası {file_path}: {e}")
            return False
    
    def play_animation(self, animation_name: str, blocking: bool = False) -> bool:
        """Animasyon oynat"""
        if animation_name not in self.animations:
            self.logger.error(f"Animasyon bulunamadı: {animation_name}")
            return False
        
        if self.is_playing:
            self.stop_animation()
        
        self.current_animation = self.animations[animation_name]
        self.is_playing = True
        self.stop_event.clear()
        
        if self.on_animation_start:
            self.on_animation_start(animation_name)
        
        if blocking:
            self._play_animation_sync()
        else:
            self.animation_thread = Thread(target=self._play_animation_sync, daemon=True)
            self.animation_thread.start()
        
        return True
    
    def _play_animation_sync(self):
        """Animasyonu senkron olarak oynat"""
        if not self.current_animation:
            return
        
        animation = self.current_animation
        start_time = time.time()
        
        try:
            while self.is_playing and not self.stop_event.is_set():
                current_time = time.time() - start_time
                
                # Loop kontrolü
                if animation.loop:
                    current_time = current_time % animation.total_duration
                elif current_time >= animation.total_duration:
                    break
                
                # Mevcut keyframe'leri bul
                current_keyframe = None
                next_keyframe = None
                
                for i, keyframe in enumerate(animation.keyframes):
                    if keyframe.timestamp <= current_time:
                        current_keyframe = keyframe
                        if i + 1 < len(animation.keyframes):
                            next_keyframe = animation.keyframes[i + 1]
                    else:
                        break
                
                if current_keyframe:
                    if next_keyframe and current_time < next_keyframe.timestamp:
                        # İki keyframe arası interpolasyon
                        self._interpolate_and_apply(current_keyframe, next_keyframe, current_time)
                    else:
                        # Direkt keyframe uygula
                        self._apply_keyframe(current_keyframe)
                
                time.sleep(0.02)  # 50Hz güncelleme
            
            # Animasyon tamamlandı
            self.is_playing = False
            if self.on_animation_complete:
                self.on_animation_complete(animation.name)
                
        except Exception as e:
            self.logger.error(f"Animasyon oynatma hatası: {e}")
            self.is_playing = False
    
    def _interpolate_and_apply(self, current_kf: KeyFrame, next_kf: KeyFrame, current_time: float):
        """İki keyframe arası interpolasyon yaparak pozisyon hesapla"""
        # Interpolasyon faktörü hesapla
        time_diff = next_kf.timestamp - current_kf.timestamp
        if time_diff <= 0:
            self._apply_keyframe(current_kf)
            return
        
        progress = (current_time - current_kf.timestamp) / time_diff
        progress = max(0.0, min(1.0, progress))
        
        # Easing fonksiyonu uygula
        eased_progress = self._apply_easing(progress, next_kf.easing)
        
        # Servo pozisyonlarını interpolate et
        interpolated_positions = {}
        
        for servo_id in current_kf.servo_positions:
            current_angle = current_kf.servo_positions[servo_id]
            next_angle = next_kf.servo_positions.get(servo_id, current_angle)
            
            interpolated_angle = int(current_angle + (next_angle - current_angle) * eased_progress)
            interpolated_positions[servo_id] = interpolated_angle
        
        # Pozisyonları uygula
        for servo_id, angle in interpolated_positions.items():
            self.servo_controller.set_servo_angle(servo_id, angle, check_limits=True)
    
    def _apply_keyframe(self, keyframe: KeyFrame):
        """Keyframe'i direkt uygula"""
        for servo_id, angle in keyframe.servo_positions.items():
            self.servo_controller.set_servo_angle(servo_id, angle, check_limits=True)
    
    def _apply_easing(self, progress: float, easing: str) -> float:
        """Easing fonksiyonu uygula"""
        if easing == "ease_in":
            return progress * progress
        elif easing == "ease_out":
            return 1 - (1 - progress) * (1 - progress)
        elif easing == "ease_in_out":
            if progress < 0.5:
                return 2 * progress * progress
            else:
                return 1 - 2 * (1 - progress) * (1 - progress)
        else:  # linear
            return progress
    
    def stop_animation(self):
        """Mevcut animasyonu durdur"""
        self.is_playing = False
        self.stop_event.set()
        
        if self.animation_thread and self.animation_thread.is_alive():
            self.animation_thread.join(timeout=1.0)
        
        self.logger.info("Animasyon durduruldu")
    
    def get_available_animations(self) -> List[str]:
        """Kullanılabilir animasyonları listele"""
        return list(self.animations.keys())
    
    def get_animation_info(self, animation_name: str) -> Optional[Dict]:
        """Animasyon bilgilerini döndür"""
        if animation_name in self.animations:
            anim = self.animations[animation_name]
            return {
                "name": anim.name,
                "description": anim.description,
                "duration": anim.total_duration,
                "loop": anim.loop,
                "keyframe_count": len(anim.keyframes)
            }
        return None

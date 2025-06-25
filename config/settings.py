# =======================
# config/settings.py - Sistem Konfigürasyonları
# =======================

import json
import os
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Dict, Any, Optional

@dataclass
class CameraSettings:
    """Kamera ayarları"""
    width: int = 720
    height: int = 480
    fps: int = 30
    enable_rgb: bool = True
    enable_depth: bool = True
    depth_scale: float = 0.001

@dataclass
class YOLOSettings:
    """YOLO model ayarları"""
    model_path: str = "data/models/yolov8n-person.pt"
    confidence_threshold: float = 0.5
    device: str = "cuda"
    enable_tracking: bool = True
    max_detections: int = 10

@dataclass
class ServoSettings:
    """Servo motor ayarları"""
    port: str = "/dev/ttyUSB0"  # macOS için "/dev/cu.usbserial-..."
    baudrate: int = 115200
    timeout: float = 1.0
    movement_speed: int = 5
    enable_pid: bool = True
    
    # Servo açı limitleri
    arm_limits: Dict[str, tuple] = None
    head_limits: Dict[str, tuple] = None
    
    def __post_init__(self):
        if self.arm_limits is None:
            self.arm_limits = {
                "shoulder_left": (0, 180),
                "elbow_left": (0, 180),
                "wrist_left": (0, 180),
                "shoulder_right": (0, 180),
                "elbow_right": (0, 180),
                "wrist_right": (0, 180)
            }
        if self.head_limits is None:
            self.head_limits = {
                "head_pan": (0, 180),
                "head_tilt": (30, 150)
            }

@dataclass
class AISettings:
    """AI ve konuşma ayarları"""
    openai_api_key: str = ""
    model: str = "gpt-4o"
    language: str = "tr"
    max_tokens: int = 150
    temperature: float = 0.7
    enable_tts: bool = True
    enable_stt: bool = True

@dataclass
class TrackingSettings:
    """Takip ayarları"""
    min_distance: float = 0.5  # metre
    max_distance: float = 5.0  # metre
    tracking_smoothing: float = 0.3
    face_priority: bool = True
    auto_switch_target: bool = False

@dataclass
class SystemSettings:
    """Sistem ayarları"""
    log_level: str = "INFO"
    performance_monitoring: bool = True
    auto_save_config: bool = True
    gui_theme: str = "dark"
    fullscreen: bool = False


class Settings:
    """Ana ayarlar sınıfı"""
    
    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file or "data/configs/settings.json"
        self.project_root = Path(__file__).parent.parent
        
        # Varsayılan ayarları yükle
        self.camera = CameraSettings()
        self.yolo = YOLOSettings()
        self.servo = ServoSettings()
        self.ai = AISettings()
        self.tracking = TrackingSettings()
        self.system = SystemSettings()
        
        # Dosyadan ayarları yükle
        self.load_settings()
    
    def load_settings(self):
        """Ayarları dosyadan yükle"""
        config_path = self.project_root / self.config_file
        
        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # Her kategoriyi güncelle
                if 'camera' in data:
                    self.camera = CameraSettings(**data['camera'])
                if 'yolo' in data:
                    self.yolo = YOLOSettings(**data['yolo'])
                if 'servo' in data:
                    self.servo = ServoSettings(**data['servo'])
                if 'ai' in data:
                    self.ai = AISettings(**data['ai'])
                if 'tracking' in data:
                    self.tracking = TrackingSettings(**data['tracking'])
                if 'system' in data:
                    self.system = SystemSettings(**data['system'])
                    
            except Exception as e:
                print(f"Ayarlar yüklenirken hata: {e}")
    
    def save_settings(self):
        """Ayarları dosyaya kaydet"""
        config_path = self.project_root / self.config_file
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            'camera': asdict(self.camera),
            'yolo': asdict(self.yolo),
            'servo': asdict(self.servo),
            'ai': asdict(self.ai),
            'tracking': asdict(self.tracking),
            'system': asdict(self.system)
        }
        
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Ayarlar kaydedilirken hata: {e}")
    
    def get_model_path(self) -> str:
        """YOLO model dosyasının tam yolunu döndür"""
        return str(self.project_root / self.yolo.model_path)
    
    def update_setting(self, category: str, key: str, value: Any):
        """Belirli bir ayarı güncelle"""
        if hasattr(self, category):
            setting_obj = getattr(self, category)
            if hasattr(setting_obj, key):
                setattr(setting_obj, key, value)
                if self.system.auto_save_config:
                    self.save_settings()

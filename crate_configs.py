#!/usr/bin/env python3
# =======================
# create_configs.py - Konfigürasyon Dosyalarını Oluştur
# =======================

"""
Expo-Humanoid için gerekli konfigürasyon dosyalarını oluşturur.
Kurulum sonrası veya ayarları sıfırlama için kullanın.

Kullanım:
    python create_configs.py
    python create_configs.py --force  # Mevcut dosyaları üzerine yaz
"""

import os
import json
import sys
from pathlib import Path

def create_directory_structure():
    """Gerekli dizinleri oluştur"""
    directories = [
        "data",
        "data/configs",
        "data/models", 
        "data/animations",
        "logs",
        "modules",
        "modules/gui",
        "modules/gui/widgets",
        "modules/gui/styles"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Dizin oluşturuldu: {directory}")

def create_main_settings():
    """Ana ayarlar dosyası"""
    settings = {
        "camera": {
            "width": 720,
            "height": 480,
            "fps": 30,
            "enable_rgb": True,
            "enable_depth": True,
            "depth_scale": 0.001
        },
        "yolo": {
            "model_path": "data/models/yolov8n.pt",
            "confidence_threshold": 0.5,
            "device": "cpu",
            "enable_tracking": True,
            "max_detections": 10
        },
        "servo": {
            "port": "/dev/cu.usbserial-1410",
            "baudrate": 115200,
            "timeout": 1.0,
            "movement_speed": 5,
            "enable_pid": True,
            "arm_limits": {
                "shoulder_left": [0, 180],
                "elbow_left": [0, 180],
                "wrist_left": [0, 180],
                "shoulder_right": [0, 180],
                "elbow_right": [0, 180],
                "wrist_right": [0, 180]
            },
            "head_limits": {
                "head_pan": [30, 150],
                "head_tilt": [60, 120]
            }
        },
        "ai": {
            "openai_api_key": "",
            "model": "gpt-4o",
            "language": "tr",
            "max_tokens": 150,
            "temperature": 0.7,
            "enable_tts": True,
            "enable_stt": True
        },
        "tracking": {
            "min_distance": 0.5,
            "max_distance": 5.0,
            "tracking_smoothing": 0.3,
            "face_priority": True,
            "auto_switch_target": False
        },
        "system": {
            "log_level": "INFO",
            "performance_monitoring": True,
            "auto_save_config": True,
            "gui_theme": "dark",
            "fullscreen": False
        }
    }
    
    return settings

def create_servo_limits():
    """Servo limitleri dosyası"""
    servo_limits = {
        "description": "Servo motor açı limitleri ve güvenlik ayarları",
        "servo_limits": {
            "0": {"name": "LEFT_SHOULDER", "min": 0, "max": 180, "center": 90},
            "1": {"name": "LEFT_ELBOW", "min": 0, "max": 180, "center": 90},
            "2": {"name": "LEFT_WRIST", "min": 0, "max": 180, "center": 90},
            "3": {"name": "LEFT_HAND", "min": 0, "max": 180, "center": 90},
            "4": {"name": "LEFT_THUMB", "min": 0, "max": 180, "center": 90},
            "5": {"name": "LEFT_INDEX", "min": 0, "max": 180, "center": 90},
            "6": {"name": "RIGHT_SHOULDER", "min": 0, "max": 180, "center": 90},
            "7": {"name": "RIGHT_ELBOW", "min": 0, "max": 180, "center": 90},
            "8": {"name": "RIGHT_WRIST", "min": 0, "max": 180, "center": 90},
            "9": {"name": "RIGHT_HAND", "min": 0, "max": 180, "center": 90},
            "10": {"name": "RIGHT_THUMB", "min": 0, "max": 180, "center": 90},
            "11": {"name": "RIGHT_INDEX", "min": 0, "max": 180, "center": 90},
            "12": {"name": "HEAD_PAN", "min": 30, "max": 150, "center": 90},
            "13": {"name": "HEAD_TILT", "min": 60, "max": 120, "center": 90}
        },
        "safety_settings": {
            "max_speed": 10,
            "min_speed": 1,
            "emergency_stop_enabled": True,
            "watchdog_timeout": 30,
            "movement_timeout": 5
        }
    }
    
    return servo_limits

def create_camera_params():
    """Kamera parametreleri dosyası"""
    camera_params = {
        "description": "Kamera kalibrasyon parametreleri",
        "realsense_d435i": {
            "supported_resolutions": [
                {"width": 1920, "height": 1080, "fps": [6, 15, 30]},
                {"width": 1280, "height": 720, "fps": [6, 15, 30]},
                {"width": 848, "height": 480, "fps": [6, 15, 30, 60]},
                {"width": 640, "height": 480, "fps": [6, 15, 30, 60]},
                {"width": 424, "height": 240, "fps": [6, 15, 30, 60]}
            ],
            "default_intrinsics": {
                "fx": 615.0,
                "fy": 615.0,
                "ppx": 324.0,
                "ppy": 240.0
            },
            "depth_settings": {
                "depth_scale": 0.001,
                "min_distance": 0.3,
                "max_distance": 10.0,
                "accuracy": "high"
            }
        },
        "webcam": {
            "supported_resolutions": [
                {"width": 1920, "height": 1080, "fps": [30]},
                {"width": 1280, "height": 720, "fps": [30]},
                {"width": 640, "height": 480, "fps": [30]}
            ],
            "default_settings": {
                "brightness": 0,
                "contrast": 0,
                "saturation": 0,
                "auto_exposure": True
            }
        }
    }
    
    return camera_params

def create_animations():
    """Animasyon dosyalarını oluştur"""
    animations = {
        "greeting": {
            "name": "greeting",
            "description": "Selamlama hareketi",
            "loop": False,
            "total_duration": 4.0,
            "keyframes": [
                {
                    "timestamp": 0.0,
                    "servo_positions": {
                        str(i): 90 for i in range(14)
                    },
                    "duration": 0.5,
                    "easing": "ease_out"
                },
                {
                    "timestamp": 1.0,
                    "servo_positions": {
                        "6": 45,   # RIGHT_SHOULDER
                        "7": 90,   # RIGHT_ELBOW
                        "8": 135,  # RIGHT_WRIST
                        "12": 90,  # HEAD_PAN
                        "13": 85   # HEAD_TILT
                    },
                    "duration": 1.0,
                    "easing": "ease_in_out"
                },
                {
                    "timestamp": 2.5,
                    "servo_positions": {
                        "6": 45,
                        "7": 90,
                        "8": 90,
                        "12": 90,
                        "13": 85
                    },
                    "duration": 0.5,
                    "easing": "ease_in_out"
                },
                {
                    "timestamp": 4.0,
                    "servo_positions": {
                        str(i): 90 for i in range(14)
                    },
                    "duration": 1.0,
                    "easing": "ease_in"
                }
            ]
        },
        
        "goodbye": {
            "name": "goodbye",
            "description": "Vedalaşma hareketi",
            "loop": False,
            "total_duration": 3.0,
            "keyframes": [
                {
                    "timestamp": 0.0,
                    "servo_positions": {str(i): 90 for i in range(14)},
                    "duration": 0.5,
                    "easing": "ease_out"
                },
                {
                    "timestamp": 1.0,
                    "servo_positions": {
                        "0": 45,   # LEFT_SHOULDER
                        "1": 45,   # LEFT_ELBOW
                        "2": 90,   # LEFT_WRIST
                        "6": 135,  # RIGHT_SHOULDER
                        "7": 135,  # RIGHT_ELBOW
                        "8": 90,   # RIGHT_WRIST
                        "13": 80   # HEAD_TILT
                    },
                    "duration": 1.5,
                    "easing": "ease_in_out"
                },
                {
                    "timestamp": 3.0,
                    "servo_positions": {str(i): 90 for i in range(14)},
                    "duration": 1.0,
                    "easing": "ease_in"
                }
            ]
        },
        
        "thinking": {
            "name": "thinking",
            "description": "Düşünme hareketi",
            "loop": True,
            "total_duration": 4.0,
            "keyframes": [
                {
                    "timestamp": 0.0,
                    "servo_positions": {
                        "6": 60,   # RIGHT_SHOULDER
                        "7": 45,   # RIGHT_ELBOW
                        "8": 90,   # RIGHT_WRIST
                        "13": 95,  # HEAD_TILT
                        "12": 85   # HEAD_PAN
                    },
                    "duration": 1.0,
                    "easing": "ease_in_out"
                },
                {
                    "timestamp": 2.0,
                    "servo_positions": {
                        "12": 95   # HEAD_PAN
                    },
                    "duration": 1.0,
                    "easing": "ease_in_out"
                },
                {
                    "timestamp": 4.0,
                    "servo_positions": {
                        "12": 85   # HEAD_PAN
                    },
                    "duration": 1.0,
                    "easing": "ease_in_out"
                }
            ]
        }
    }
    
    return animations

def save_json_file(filepath, data, force=False):
    """JSON dosyasını kaydet"""
    if os.path.exists(filepath) and not force:
        print(f"⚠️  Dosya zaten var: {filepath} (--force ile üzerine yazın)")
        return False
    
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"✅ Dosya oluşturuldu: {filepath}")
        return True
    except Exception as e:
        print(f"❌ Dosya oluşturulamadı {filepath}: {e}")
        return False

def create_run_script():
    """Başlatma script'i oluştur"""
    script_content = '''#!/bin/bash

# =======================
# modules/__init__.py - Ana modül init
# =======================

"""
Expo-Humanoid Ana Modülleri

Bu paket Expo-Humanoid robotik sisteminin tüm ana bileşenlerini içerir:
- camera: Kamera yönetimi (RealSense, Mock, Webcam)
- ai: Yapay zeka modülleri (YOLO, OpenAI)
- servo: Servo motor kontrolü ve animasyonlar
- tracking: Hedef takibi
- gui: Kullanıcı arayüzü
- system: Sistem izleme ve logging
- utils: Yardımcı fonksiyonlar
"""

__version__ = "1.0.0"
__author__ = "Expo-Humanoid Team"

# Ana modül import'ları
from .camera import RealSenseManager, CameraInterface, MockCamera
from .ai import YOLODetector, OpenAIChat
from .servo import ServoController, AnimationEngine
from .tracking import TargetTracker, DistanceCalculator
from .system import SystemLogger, SystemMonitor
from .utils import Detection, BoundingBox, SystemStatus

__all__ = [
    # Camera
    'RealSenseManager', 'CameraInterface', 'MockCamera',
    
    # AI
    'YOLODetector', 'OpenAIChat', 
    
    # Servo
    'ServoController', 'AnimationEngine',
    
    # Tracking
    'TargetTracker', 'DistanceCalculator',
    
    # System
    'SystemLogger', 'SystemMonitor',
    
    # Utils
    'Detection', 'BoundingBox', 'SystemStatus'
]

def get_version():
    """Versiyon bilgisini döndür"""
    return __version__

def get_system_info():
    """Sistem bilgilerini döndür"""
    import platform
    import sys
    
    return {
        "version": __version__,
        "python": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        "platform": platform.system(),
        "architecture": platform.machine()
    }
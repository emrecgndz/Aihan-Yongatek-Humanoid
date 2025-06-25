from enum import Enum
from typing import Dict, List

class ServoIDs(Enum):
    """Servo motor ID'leri"""
    # Sol kol
    LEFT_SHOULDER = 0
    LEFT_ELBOW = 1
    LEFT_WRIST = 2
    LEFT_HAND = 3
    LEFT_THUMB = 4
    LEFT_INDEX = 5
    
    # Sağ kol
    RIGHT_SHOULDER = 6
    RIGHT_ELBOW = 7
    RIGHT_WRIST = 8
    RIGHT_HAND = 9
    RIGHT_THUMB = 10
    RIGHT_INDEX = 11
    
    # Kafa ve boyun
    HEAD_PAN = 12
    HEAD_TILT = 13

class SystemStates(Enum):
    """Sistem durumları"""
    IDLE = "idle"
    TRACKING = "tracking"
    INTERACTING = "interacting"
    ANIMATING = "animating"
    ERROR = "error"
    CALIBRATING = "calibrating"

class LogLevels(Enum):
    """Log seviyeleri"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

# Renk kodları (BGR formatı - OpenCV için)
COLORS = {
    'red': (0, 0, 255),
    'green': (0, 255, 0),
    'blue': (255, 0, 0),
    'yellow': (0, 255, 255),
    'cyan': (255, 255, 0),
    'magenta': (255, 0, 255),
    'white': (255, 255, 255),
    'black': (0, 0, 0),
    'orange': (0, 165, 255),
    'purple': (128, 0, 128)
}

# Ses komutları
AUDIO_COMMANDS = {
    'greeting': ['merhaba', 'selam', 'günaydın', 'hello', 'hi'],
    'goodbye': ['hoşçakal', 'güle güle', 'bye', 'goodbye'],
    'question': ['nasılsın', 'ne yapıyorsun', 'how are you'],
    'thanks': ['teşekkür', 'sağol', 'thank you', 'thanks']
}

# Animasyon türleri
ANIMATION_TYPES = {
    'greeting': 'Selamlama',
    'goodbye': 'Vedalaşma',
    'wave': 'El sallama',
    'point': 'İşaret etme',
    'thinking': 'Düşünme',
    'idle': 'Bekleme',
    'dance': 'Dans',
    'presentation': 'Sunum'
}

# Sistem limitleri
SYSTEM_LIMITS = {
    'max_cpu_usage': 80,  # %
    'max_gpu_usage': 90,  # %
    'max_temperature': 75,  # °C
    'min_fps': 15,
    'max_response_time': 3.0,  # saniye
    'max_tracking_distance': 5.0,  # metre
    'min_tracking_distance': 0.3   # metre
}

# GUI sabitleri
GUI_CONSTANTS = {
    'window_width': 1400,
    'window_height': 900,
    'camera_widget_width': 640,
    'camera_widget_height': 480,
    'refresh_rate': 30,  # Hz
    'status_update_interval': 1000,  # ms
    'log_max_lines': 1000
}

# Arduino komut protokolü
ARDUINO_COMMANDS = {
    'SET_SERVO': 'S',
    'GET_STATUS': 'G',
    'SET_SPEED': 'V',
    'CALIBRATE': 'C',
    'RESET': 'R',
    'PING': 'P'
}

# Mesaj tipleri
MESSAGE_TYPES = {
    'info': 'INFO',
    'warning': 'WARNING',
    'error': 'ERROR',
    'success': 'SUCCESS'
}
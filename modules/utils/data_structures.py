# =======================
# modules/utils/data_structures.py - Veri Yapıları
# =======================

from dataclasses import dataclass
from typing import Optional, List, Dict, Any
import time


@dataclass
class BoundingBox:
    """Nesne sınırlayıcı kutu"""
    x1: int
    y1: int
    x2: int
    y2: int
    width: int
    height: int
    
    @property
    def center_x(self) -> int:
        return (self.x1 + self.x2) // 2
    
    @property
    def center_y(self) -> int:
        return (self.y1 + self.y2) // 2
    
    @property
    def area(self) -> int:
        return self.width * self.height


@dataclass
class Detection:
    """Nesne tespit sonucu"""
    id: int
    bbox: BoundingBox
    confidence: float
    class_name: str
    center_x: int
    center_y: int
    timestamp: float = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = time.time()


@dataclass
class SystemStatus:
    """Sistem durumu"""
    cpu_usage: float
    gpu_usage: float
    memory_usage: float
    temperature: float
    fps: int
    active_modules: List[str]
    errors: List[str]
    warnings: List[str]


@dataclass
class RobotState:
    """Robot durumu"""
    is_tracking: bool
    current_target: Optional[Detection]
    servo_positions: Dict[int, int]
    animation_playing: Optional[str]
    last_interaction: Optional[str]
    system_status: SystemStatus
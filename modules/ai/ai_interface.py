# =======================
# modules/ai/ai_interface.py - AI Arayüzü
# =======================

from abc import ABC, abstractmethod
from typing import List, Dict, Any
import numpy as np

from modules.utils.data_structures import Detection


class AIInterface(ABC):
    """AI modülleri için temel arayüz"""
    
    @abstractmethod
    def initialize(self) -> bool:
        """AI modülünü başlat"""
        pass
    
    @abstractmethod
    def get_stats(self) -> Dict[str, Any]:
        """İstatistikleri döndür"""
        pass


class DetectionInterface(AIInterface):
    """Nesne tespit modülleri için arayüz"""
    
    @abstractmethod
    def detect_people(self, frame: np.ndarray) -> List[Detection]:
        """İnsan tespiti yap"""
        pass
    
    @abstractmethod
    def draw_detections(self, frame: np.ndarray, detections: List[Detection]) -> np.ndarray:
        """Tespitleri çiz"""
        pass


class ChatInterface(AIInterface):
    """Sohbet modülleri için arayüz"""
    
    @abstractmethod
    def get_response(self, user_input: str) -> str:
        """Kullanıcı girdisine yanıt ver"""
        pass
    
    @abstractmethod
    def clear_conversation(self):
        """Konuşma geçmişini temizle"""
        pass

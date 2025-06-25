# =======================
# modules/system/logger.py - Günlük Kayıt Sistemi
# =======================

import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Optional


class SystemLogger:
    """Expo-Humanoid sistem logger'ı"""
    
    def __init__(self, log_level: str = "INFO", log_file: Optional[str] = None):
        self.logger = logging.getLogger("ExpoHumanoid")
        self.logger.setLevel(getattr(logging, log_level.upper()))
        
        # Eğer logger zaten handler'a sahipse, ekleme yapma
        if not self.logger.handlers:
            # Formatter oluştur
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            
            # Console handler
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            self.logger.addHandler(console_handler)
            
            # File handler
            if log_file is None:
                log_dir = Path("logs")
                log_dir.mkdir(exist_ok=True)
                log_file = log_dir / f"expo_humanoid_{datetime.now().strftime('%Y%m%d')}.log"
            
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
    
    def debug(self, message: str):
        self.logger.debug(message)
    
    def info(self, message: str):
        self.logger.info(message)
    
    def warning(self, message: str):
        self.logger.warning(message)
    
    def error(self, message: str):
        self.logger.error(message)
    
    def critical(self, message: str):
        self.logger.critical(message)

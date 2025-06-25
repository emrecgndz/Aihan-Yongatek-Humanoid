# =======================
# main.py - Ana Uygulama
# =======================

import sys
import os
import asyncio
from pathlib import Path

# Proje root dizinini path'e ekle
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QThread
from modules.gui.main_window import MainWindow
from modules.system.logger import SystemLogger
from config.settings import Settings


class ExpoHumanoidApp:
    """Expo-Humanoid Ana Uygulama Sınıfı"""
    
    def __init__(self):
        self.app = None
        self.main_window = None
        self.settings = Settings()
        self.logger = SystemLogger()
        
    def initialize(self):
        """Uygulamayı başlat"""
        try:
            # PyQt5 uygulamasını oluştur
            self.app = QApplication(sys.argv)
            self.app.setApplicationName("Expo-Humanoid")
            self.app.setApplicationVersion("1.0")
            
            # Ana pencereyi oluştur
            self.main_window = MainWindow(self.settings, self.logger)
            
            self.logger.info("Expo-Humanoid başlatıldı")
            return True
            
        except Exception as e:
            self.logger.error(f"Uygulama başlatılamadı: {e}")
            return False
    
    def run(self):
        """Uygulamayı çalıştır"""
        if not self.initialize():
            return -1
            
        # Ana pencereyi göster
        self.main_window.show()
        
        # Olay döngüsünü başlat
        return self.app.exec_()
    
    def shutdown(self):
        """Uygulamayı güvenli şekilde kapat"""
        self.logger.info("Expo-Humanoid kapatılıyor...")
        
        if self.main_window:
            self.main_window.cleanup()
            
        if self.app:
            self.app.quit()


def main():
    """Ana giriş noktası"""
    app = ExpoHumanoidApp()
    
    try:
        exit_code = app.run()
        app.shutdown()
        return exit_code
        
    except KeyboardInterrupt:
        print("\nKullanıcı tarafından durduruldu")
        app.shutdown()
        return 0
        
    except Exception as e:
        print(f"Kritik hata: {e}")
        app.shutdown()
        return -1


if __name__ == "__main__":
    sys.exit(main())
# =======================
# main.py - Düzeltilmiş Ana Uygulama
# =======================

import sys
import os
import argparse
from pathlib import Path

# Proje root dizinini path'e ekle
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

try:
    from PyQt5.QtWidgets import QApplication, QMessageBox
    from PyQt5.QtCore import QThread, Qt
    from PyQt5.QtGui import QIcon
except ImportError as e:
    print(f"❌ PyQt5 import hatası: {e}")
    print("Çözüm: pip install PyQt5==5.15.9")
    sys.exit(1)

try:
    from modules.gui.main_window import MainWindow
    from modules.gui.styles import apply_theme
    from modules.system.logger import SystemLogger
    from config.settings import Settings
except ImportError as e:
    print(f"❌ Modül import hatası: {e}")
    print("Proje dosyaları eksik olabilir.")
    sys.exit(1)


class ExpoHumanoidApp:
    """Expo-Humanoid Ana Uygulama Sınıfı - Düzeltilmiş"""
    
    def __init__(self, args=None):
        self.app = None
        self.main_window = None
        self.settings = None
        self.logger = None
        self.args = args or {}
        
    def initialize(self):
        """Uygulamayı başlat"""
        try:
            # PyQt5 uygulamasını oluştur
            self.app = QApplication(sys.argv)
            self.app.setApplicationName("Expo-Humanoid")
            self.app.setApplicationVersion("1.0")
            self.app.setApplicationDisplayName("Expo-Humanoid Control Center")
            
            # macOS için özel ayarlar
            if sys.platform == "darwin":
                self.app.setAttribute(Qt.AA_DontShowIconsInMenus, False)
                self.app.setQuitOnLastWindowClosed(True)
            
            # Logger'ı başlat
            self.logger = SystemLogger()
            self.logger.info("Expo-Humanoid başlatılıyor...")
            
            # Ayarları yükle
            self.settings = Settings()
            
            # Tema uygula
            theme = self.settings.system.gui_theme
            apply_theme(self.app, theme)
            
            # Ana pencereyi oluştur
            self.main_window = MainWindow(self.settings, self.logger)
            
            # Preset modunu uygula (varsa)
            if hasattr(self.args, 'preset') and self.args.preset:
                self.apply_startup_preset(self.args.preset)
            
            self.logger.info("Expo-Humanoid başarıyla başlatıldı")
            return True
            
        except Exception as e:
            error_msg = f"Uygulama başlatılamadı: {e}"
            print(f"❌ {error_msg}")
            
            if self.logger:
                self.logger.error(error_msg)
            
            # Hata dialog'u göster
            if self.app:
                QMessageBox.critical(None, "Başlatma Hatası", error_msg)
            
            return False
    
    def apply_startup_preset(self, preset_name):
        """Başlangıç preset'ini uygula"""
        try:
            if preset_name == "demo":
                self.logger.info("Demo modu uygulanıyor...")
                # Demo modu ayarları main_window'da uygulanacak
                
            elif preset_name == "manual":
                self.logger.info("Manuel modu uygulanıyor...")
                # Manuel modu ayarları
                
            elif preset_name == "calibration":
                self.logger.info("Kalibrasyon modu uygulanıyor...")
                # Kalibrasyon modu ayarları
                
            elif preset_name == "test":
                self.logger.info("Test modu uygulanıyor...")
                # Test modu - sadece mock kamera
                
            else:
                self.logger.warning(f"Bilinmeyen preset: {preset_name}")
                
        except Exception as e:
            self.logger.error(f"Preset uygulama hatası: {e}")
    
    def run(self):
        """Uygulamayı çalıştır"""
        if not self.initialize():
            return -1
        
        try:
            # Ana pencereyi göster
            if self.settings.system.fullscreen:
                self.main_window.showFullScreen()
            else:
                self.main_window.show()
            
            # Pencereyi öne getir (macOS için)
            self.main_window.raise_()
            self.main_window.activateWindow()
            
            # Olay döngüsünü başlat
            self.logger.info("GUI olay döngüsü başlatılıyor...")
            return self.app.exec_()
            
        except KeyboardInterrupt:
            self.logger.info("Kullanıcı tarafından durduruldu (Ctrl+C)")
            return 0
        except Exception as e:
            self.logger.error(f"Çalışma hatası: {e}")
            return -1
    
    def shutdown(self):
        """Uygulamayı güvenli şekilde kapat"""
        try:
            if self.logger:
                self.logger.info("Expo-Humanoid kapatılıyor...")
            
            if self.main_window:
                self.main_window.cleanup()
                
            if self.app:
                self.app.quit()
                
            if self.logger:
                self.logger.info("Expo-Humanoid başarıyla kapatıldı")
                
        except Exception as e:
            print(f"❌ Kapatma hatası: {e}")


def parse_arguments():
    """Komut satırı argümanlarını parse et"""
    parser = argparse.ArgumentParser(
        description="Expo-Humanoid İnteraktif Robotik Sunum Sistemi",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Kullanım örnekleri:
  python main.py                     # Normal başlangıç
  python main.py --preset demo       # Demo modu
  python main.py --preset manual     # Manuel kontrol modu
  python main.py --preset calibration # Kalibrasyon modu
  python main.py --theme dark        # Dark tema ile başlat
  python main.py --fullscreen        # Tam ekran modu
  python main.py --log-level DEBUG   # Debug logları aktif

Daha fazla bilgi için: docs/Usage.md
        """
    )
    
    # Preset modları
    parser.add_argument(
        '--preset', 
        choices=['demo', 'manual', 'calibration', 'test'],
        help='Başlangıç preset modu'
    )
    
    # Tema seçimi
    parser.add_argument(
        '--theme',
        choices=['dark', 'light', 'macos', 'system'],
        default='dark',
        help='GUI teması (varsayılan: dark)'
    )
    
    # Tam ekran modu
    parser.add_argument(
        '--fullscreen',
        action='store_true',
        help='Tam ekran modunda başlat'
    )
    
    # Log seviyesi
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        default='INFO',
        help='Log seviyesi (varsayılan: INFO)'
    )
    
    # Kamera tipi zorla
    parser.add_argument(
        '--camera',
        choices=['auto', 'realsense', 'mock', 'webcam'],
        default='auto',
        help='Kamera tipi (varsayılan: auto)'
    )
    
    # Konfigürasyon dosyası
    parser.add_argument(
        '--config',
        type=str,
        help='Özel konfigürasyon dosyası yolu'
    )
    
    # Hata ayıklama modu
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Hata ayıklama modunu aktifleştir'
    )
    
    # Sadece test yap ve çık
    parser.add_argument(
        '--test-only',
        action='store_true',
        help='Sadece sistem testlerini çalıştır ve çık'
    )
    
    return parser.parse_args()


def run_system_tests():
    """Sistem testlerini çalıştır"""
    print("🧪 Sistem testleri çalıştırılıyor...")
    
    tests_passed = 0
    total_tests = 0
    
    # Import testleri
    total_tests += 1
    try:
        from modules.camera.realsense_manager import RealSenseManager
        from modules.ai.yolo_detector import YOLODetector
        from modules.servo.servo_controller import ServoController
        print("✅ Import testleri başarılı")
        tests_passed += 1
    except ImportError as e:
        print(f"❌ Import testleri başarısız: {e}")
    
    # Konfigürasyon testi
    total_tests += 1
    try:
        settings = Settings()
        print("✅ Konfigürasyon testi başarılı")
        tests_passed += 1
    except Exception as e:
        print(f"❌ Konfigürasyon testi başarısız: {e}")
    
    # Model dosyası testi
    total_tests += 1
    model_path = PROJECT_ROOT / "data" / "models" / "yolov8n.pt"
    if model_path.exists():
        print("✅ YOLO model dosyası mevcut")
        tests_passed += 1
    else:
        print("❌ YOLO model dosyası bulunamadı")
        print(f"   Beklenen konum: {model_path}")
    
    # Sonuç
    print(f"\n📊 Test Sonuçları: {tests_passed}/{total_tests} başarılı")
    
    if tests_passed == total_tests:
        print("🎉 Tüm testler başarılı! Sistem kullanıma hazır.")
        return True
    else:
        print("⚠️  Bazı testler başarısız. Kurulumu kontrol edin.")
        return False


def main():
    """Ana giriş noktası"""
    # Argümanları parse et
    args = parse_arguments()
    
    # Sadece test modunda çalış
    if args.test_only:
        success = run_system_tests()
        return 0 if success else 1
    
    # Ana uygulamayı başlat
    app = ExpoHumanoidApp(args)
    
    try:
        exit_code = app.run()
        app.shutdown()
        return exit_code
        
    except KeyboardInterrupt:
        print("\n⏹️  Kullanıcı tarafından durduruldu")
        app.shutdown()
        return 0
        
    except Exception as e:
        print(f"\n❌ Kritik hata: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        app.shutdown()
        return -1


if __name__ == "__main__":
    # Özel durum yakalama
    try:
        sys.exit(main())
    except SystemExit:
        pass
    except Exception as e:
        print(f"\n💥 Beklenmeyen hata: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(-1)
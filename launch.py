#!/usr/bin/env python3
# =======================
# launch.py - Expo-Humanoid Modern Başlatma Script'i
# =======================

"""
Expo-Humanoid'i farklı modlarda başlatmak için modern launcher.
Otomatik sistem kontrolü, konfigürasyon doğrulama ve hata yönetimi sağlar.

Kullanım:
    python launch.py                    # Normal başlatma
    python launch.py --mode demo        # Demo modu
    python launch.py --mode safe        # Güvenli mod (mock)
    python launch.py --check-system     # Sadece sistem kontrolü
    python launch.py --setup            # Kurulum modu
"""

import sys
import os
import subprocess
import time
import json
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, List, Optional

# Renkli çıktı için
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

@dataclass
class SystemStatus:
    """Sistem durum bilgisi"""
    python_ok: bool = False
    venv_active: bool = False
    dependencies_ok: bool = False
    config_ok: bool = False
    camera_available: bool = False
    models_ok: bool = False
    arduino_available: bool = False
    overall_status: str = "unknown"

class ExpoHumanoidLauncher:
    """Expo-Humanoid Launcher"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        os.chdir(self.project_root)
        
        self.system_status = SystemStatus()
        self.launch_modes = {
            'normal': 'Normal mod - Tüm özellikler aktif',
            'demo': 'Demo modu - Fuar için optimize edilmiş',
            'safe': 'Güvenli mod - Sadece mock bileşenler',
            'calibration': 'Kalibrasyon modu - Servo ayarları',
            'test': 'Test modu - Tanılama ve debugging'
        }
        
    def print_header(self):
        """Başlık yazdır"""
        print(f"{Colors.CYAN}{Colors.BOLD}")
        print("╔" + "═" * 58 + "╗")
        print("║" + " " * 58 + "║")
        print("║" + " " * 15 + "🤖 EXPO-HUMANOID v1.0" + " " * 15 + "║")
        print("║" + " " * 10 + "İnteraktif Robotik Sunum Sistemi" + " " * 10 + "║")
        print("║" + " " * 58 + "║")
        print("╚" + "═" * 58 + "╝")
        print(f"{Colors.END}")
    
    def check_python_version(self) -> bool:
        """Python versiyonu kontrol"""
        version = sys.version_info
        required = (3, 8)
        
        if version >= required:
            print(f"{Colors.GREEN}✅ Python {version.major}.{version.minor}.{version.micro}{Colors.END}")
            self.system_status.python_ok = True
            return True
        else:
            print(f"{Colors.RED}❌ Python {version.major}.{version.minor} - Gerekli: {required[0]}.{required[1]}+{Colors.END}")
            return False
    
    def check_virtual_environment(self) -> bool:
        """Sanal ortam kontrol"""
        venv_active = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
        
        if venv_active:
            print(f"{Colors.GREEN}✅ Sanal ortam aktif{Colors.END}")
            self.system_status.venv_active = True
            return True
        else:
            print(f"{Colors.YELLOW}⚠️  Sanal ortam aktif değil{Colors.END}")
            return True  # Uyarı ama engel değil
    
    def check_dependencies(self) -> bool:
        """Temel bağımlılıkları kontrol"""
        critical_packages = [
            ('PyQt5', 'PyQt5.QtWidgets'),
            ('OpenCV', 'cv2'),
            ('NumPy', 'numpy')
        ]
        
        optional_packages = [
            ('RealSense', 'pyrealsense2'),
            ('PyTorch', 'torch'),
            ('Ultralytics', 'ultralytics'),
            ('OpenAI', 'openai'),
            ('PySerial', 'serial')
        ]
        
        critical_ok = True
        optional_count = 0
        
        # Kritik paketler
        for name, module in critical_packages:
            try:
                __import__(module)
                print(f"{Colors.GREEN}✅ {name}{Colors.END}")
            except ImportError:
                print(f"{Colors.RED}❌ {name} - KRİTİK{Colors.END}")
                critical_ok = False
        
        # Opsiyonel paketler
        for name, module in optional_packages:
            try:
                __import__(module)
                print(f"{Colors.GREEN}✅ {name}{Colors.END}")
                optional_count += 1
            except ImportError:
                print(f"{Colors.YELLOW}⚠️  {name} - Opsiyonel{Colors.END}")
        
        self.system_status.dependencies_ok = critical_ok
        
        if critical_ok:
            print(f"{Colors.GREEN}✅ Kritik bağımlılıklar OK ({optional_count}/{len(optional_packages)} opsiyonel){Colors.END}")
        
        return critical_ok
    
    def check_configuration(self) -> bool:
        """Konfigürasyon dosyalarını kontrol"""
        config_files = [
            'data/configs/settings.json',
            'config/settings.py',
            'config/constants.py'
        ]
        
        missing_files = []
        
        for config_file in config_files:
            if not Path(config_file).exists():
                missing_files.append(config_file)
        
        if missing_files:
            print(f"{Colors.RED}❌ Eksik konfigürasyon dosyaları:{Colors.END}")
            for file in missing_files:
                print(f"   • {file}")
            return False
        else:
            print(f"{Colors.GREEN}✅ Konfigürasyon dosyaları mevcut{Colors.END}")
            self.system_status.config_ok = True
            return True
    
    def check_camera_availability(self) -> bool:
        """Kamera kullanılabilirliğini kontrol"""
        camera_types = []
        
        # RealSense kontrol
        try:
            import pyrealsense2 as rs
            ctx = rs.context()
            devices = ctx.query_devices()
            if len(devices) > 0:
                camera_types.append("RealSense")
        except:
            pass
        
        # Webcam kontrol
        try:
            import cv2
            cap = cv2.VideoCapture(0)
            if cap.isOpened():
                camera_types.append("Webcam")
                cap.release()
        except:
            pass
        
        # Mock her zaman mevcut
        camera_types.append("Mock")
        
        if "RealSense" in camera_types:
            print(f"{Colors.GREEN}✅ Kameralar: {', '.join(camera_types)}{Colors.END}")
            self.system_status.camera_available = True
        else:
            print(f"{Colors.YELLOW}⚠️  Kameralar: {', '.join(camera_types)} (RealSense önerilir){Colors.END}")
            self.system_status.camera_available = False
        
        return len(camera_types) > 0
    
    def check_models(self) -> bool:
        """Model dosyalarını kontrol"""
        model_files = [
            'data/models/yolov8n.pt'
        ]
        
        missing_models = []
        
        for model_file in model_files:
            if not Path(model_file).exists():
                missing_models.append(model_file)
        
        if missing_models:
            print(f"{Colors.YELLOW}⚠️  Eksik model dosyaları:{Colors.END}")
            for model in missing_models:
                print(f"   • {model}")
            print(f"{Colors.BLUE}   💡 Otomatik indirilecek{Colors.END}")
            return False
        else:
            print(f"{Colors.GREEN}✅ Model dosyaları mevcut{Colors.END}")
            self.system_status.models_ok = True
            return True
    
    def check_arduino(self) -> bool:
        """Arduino bağlantısını kontrol"""
        try:
            import serial.tools.list_ports
            ports = list(serial.tools.list_ports.comports())
            
            arduino_ports = []
            for port in ports:
                if any(keyword in port.description.lower() for keyword in ['arduino', 'usb', 'serial']):
                    arduino_ports.append(port.device)
            
            if arduino_ports:
                print(f"{Colors.GREEN}✅ Arduino portları: {', '.join(arduino_ports)}{Colors.END}")
                self.system_status.arduino_available = True
                return True
            else:
                print(f"{Colors.YELLOW}⚠️  Arduino bulunamadı (mock modda çalışır){Colors.END}")
                return False
                
        except Exception:
            print(f"{Colors.YELLOW}⚠️  Arduino kontrol edilemedi{Colors.END}")
            return False
    
    def run_system_check(self) -> bool:
        """Tam sistem kontrolü"""
        print(f"{Colors.BLUE}{Colors.BOLD}🔍 Sistem Kontrolü{Colors.END}")
        print("─" * 40)
        
        checks = [
            ("Python Versiyonu", self.check_python_version),
            ("Sanal Ortam", self.check_virtual_environment),
            ("Bağımlılıklar", self.check_dependencies),
            ("Konfigürasyon", self.check_configuration),
            ("Kameralar", self.check_camera_availability),
            ("Model Dosyaları", self.check_models),
            ("Arduino/Servo", self.check_arduino)
        ]
        
        passed = 0
        total = len(checks)
        
        for name, check_func in checks:
            print(f"\n📋 {name}:")
            if check_func():
                passed += 1
        
        # Genel durum
        success_rate = (passed / total) * 100
        
        print(f"\n{Colors.BOLD}📊 Sistem Durumu:{Colors.END}")
        print(f"   Başarılı: {passed}/{total} ({success_rate:.1f}%)")
        
        if success_rate >= 85:
            self.system_status.overall_status = "excellent"
            print(f"{Colors.GREEN}🎉 Sistem mükemmel durumda!{Colors.END}")
            return True
        elif success_rate >= 70:
            self.system_status.overall_status = "good"
            print(f"{Colors.GREEN}✅ Sistem iyi durumda{Colors.END}")
            return True
        elif success_rate >= 50:
            self.system_status.overall_status = "fair"
            print(f"{Colors.YELLOW}⚠️  Sistem kısmen hazır{Colors.END}")
            return True
        else:
            self.system_status.overall_status = "poor"
            print(f"{Colors.RED}❌ Sistem kurulumu eksik{Colors.END}")
            return False
    
    def download_missing_models(self):
        """Eksik modelleri indir"""
        print(f"{Colors.BLUE}📥 Model dosyaları indiriliyor...{Colors.END}")
        
        try:
            # YOLO modeli indir
            python_cmd = [sys.executable, "-c", 
                         "from ultralytics import YOLO; import os; os.makedirs('data/models', exist_ok=True); YOLO('yolov8n.pt')"]
            
            result = subprocess.run(python_cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                # Model dosyasını doğru yere taşı
                import shutil
                home_dir = Path.home()
                source_model = home_dir / ".ultralytics" / "weights" / "yolov8n.pt"
                target_model = Path("data/models/yolov8n.pt")
                
                if source_model.exists():
                    target_model.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy(source_model, target_model)
                    print(f"{Colors.GREEN}✅ YOLO modeli indirildi{Colors.END}")
                    return True
            
            print(f"{Colors.RED}❌ Model indirme başarısız{Colors.END}")
            return False
            
        except Exception as e:
            print(f"{Colors.RED}❌ Model indirme hatası: {e}{Colors.END}")
            return False
    
    def create_missing_configs(self):
        """Eksik konfigürasyon dosyalarını oluştur"""
        print(f"{Colors.BLUE}⚙️  Konfigürasyon dosyaları oluşturuluyor...{Colors.END}")
        
        try:
            # create_configs.py çalıştır
            result = subprocess.run([sys.executable, "create_configs.py"], capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"{Colors.GREEN}✅ Konfigürasyon dosyaları oluşturuldu{Colors.END}")
                return True
            else:
                print(f"{Colors.RED}❌ Konfigürasyon oluşturma başarısız{Colors.END}")
                return False
                
        except Exception as e:
            print(f"{Colors.RED}❌ Konfigürasyon hatası: {e}{Colors.END}")
            return False
    
    def launch_application(self, mode: str = "normal", extra_args: List[str] = None):
        """Uygulamayı başlat"""
        print(f"{Colors.GREEN}{Colors.BOLD}🚀 Expo-Humanoid Başlatılıyor...{Colors.END}")
        print(f"{Colors.BLUE}Mod: {self.launch_modes.get(mode, mode)}{Colors.END}")
        
        # Komut oluştur
        cmd = [sys.executable, "main.py"]
        
        # Mod parametreleri
        if mode == "demo":
            cmd.extend(["--preset", "demo"])
        elif mode == "safe":
            cmd.extend(["--camera", "mock", "--preset", "manual"])
        elif mode == "calibration":
            cmd.extend(["--preset", "calibration"])
        elif mode == "test":
            cmd.extend(["--debug", "--log-level", "DEBUG", "--camera", "mock"])
        
        # Ek parametreler
        if extra_args:
            cmd.extend(extra_args)
        
        print(f"{Colors.CYAN}Komut: {' '.join(cmd)}{Colors.END}")
        print("─" * 50)
        
        try:
            # Uygulamayı başlat
            process = subprocess.Popen(cmd)
            
            # Çıkış kodunu bekle
            exit_code = process.wait()
            
            if exit_code == 0:
                print(f"\n{Colors.GREEN}✅ Uygulama normal şekilde kapandı{Colors.END}")
            else:
                print(f"\n{Colors.YELLOW}⚠️  Uygulama hata kodu ile kapandı: {exit_code}{Colors.END}")
            
            return exit_code
            
        except KeyboardInterrupt:
            print(f"\n{Colors.YELLOW}⏹️  Kullanıcı tarafından durduruldu{Colors.END}")
            process.terminate()
            return 1
        except Exception as e:
            print(f"\n{Colors.RED}❌ Başlatma hatası: {e}{Colors.END}")
            return 1
    
    def show_launch_options(self):
        """Başlatma seçeneklerini göster"""
        print(f"{Colors.BLUE}{Colors.BOLD}🎮 Başlatma Modları:{Colors.END}")
        print("─" * 40)
        
        for mode, description in self.launch_modes.items():
            print(f"{Colors.CYAN}• {mode:12}{Colors.END} - {description}")
        
        print(f"\n{Colors.YELLOW}Kullanım:{Colors.END}")
        print("  python launch.py --mode <mod_adı>")
        print("  python launch.py --check-system")
        print("  python launch.py --setup")
    
    def setup_mode(self):
        """Kurulum modu"""
        print(f"{Colors.BLUE}{Colors.BOLD}🛠️  Kurulum Modu{Colors.END}")
        print("─" * 40)
        
        # Sistem kontrolü
        if not self.run_system_check():
            print(f"\n{Colors.YELLOW}⚙️  Sistem iyileştirmeleri yapılıyor...{Colors.END}")
            
            # Eksik modelleri indir
            if not self.system_status.models_ok:
                self.download_missing_models()
            
            # Eksik konfigürasyonları oluştur
            if not self.system_status.config_ok:
                self.create_missing_configs()
            
            # Tekrar kontrol
            print(f"\n{Colors.BLUE}🔄 Sistem tekrar kontrol ediliyor...{Colors.END}")
            self.run_system_check()
        
        print(f"\n{Colors.GREEN}✅ Kurulum tamamlandı!{Colors.END}")

def main():
    """Ana fonksiyon"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Expo-Humanoid Modern Launcher",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Örnek kullanımlar:
  python launch.py                     # Normal başlatma
  python launch.py --mode demo         # Demo modu
  python launch.py --mode safe         # Güvenli mod
  python launch.py --check-system      # Sistem kontrolü
  python launch.py --setup             # Kurulum/onarım modu
  python launch.py --list-modes        # Mevcut modları listele
        """
    )
    
    parser.add_argument('--mode', '-m', 
                       choices=['normal', 'demo', 'safe', 'calibration', 'test'],
                       default='normal',
                       help='Başlatma modu')
    
    parser.add_argument('--check-system', '-c', 
                       action='store_true',
                       help='Sadece sistem kontrolü yap')
    
    parser.add_argument('--setup', '-s',
                       action='store_true', 
                       help='Kurulum/onarım modu')
    
    parser.add_argument('--list-modes', '-l',
                       action='store_true',
                       help='Mevcut modları listele')
    
    parser.add_argument('--force-check',
                       action='store_true',
                       help='Sistem kontrolünü zorla yap')
    
    # Ana uygulama argümanları
    parser.add_argument('--theme',
                       choices=['dark', 'light', 'macos'],
                       help='GUI teması')
    
    parser.add_argument('--fullscreen',
                       action='store_true',
                       help='Tam ekran modunda başlat')
    
    args = parser.parse_args()
    
    # Launcher oluştur
    launcher = ExpoHumanoidLauncher()
    launcher.print_header()
    
    try:
        # Mod seçeneklerini listele
        if args.list_modes:
            launcher.show_launch_options()
            return 0
        
        # Kurulum modu
        if args.setup:
            launcher.setup_mode()
            return 0
        
        # Sadece sistem kontrolü
        if args.check_system:
            system_ok = launcher.run_system_check()
            return 0 if system_ok else 1
        
        # Normal başlatma için sistem kontrolü
        if not args.force_check:
            print(f"{Colors.BLUE}📋 Hızlı sistem kontrolü...{Colors.END}")
            # Sadece kritik kontroller
            if not (launcher.check_python_version() and 
                   launcher.check_dependencies() and 
                   launcher.check_configuration()):
                print(f"\n{Colors.RED}❌ Kritik sistem sorunları tespit edildi!{Colors.END}")
                print(f"{Colors.YELLOW}💡 Çözüm: python launch.py --setup{Colors.END}")
                return 1
        else:
            # Tam sistem kontrolü
            if not launcher.run_system_check():
                return 1
        
        # Ek argümanları hazırla
        extra_args = []
        if args.theme:
            extra_args.extend(['--theme', args.theme])
        if args.fullscreen:
            extra_args.append('--fullscreen')
        
        # Uygulamayı başlat
        exit_code = launcher.launch_application(args.mode, extra_args)
        return exit_code
        
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}⏹️  İşlem kullanıcı tarafından iptal edildi{Colors.END}")
        return 1
    except Exception as e:
        print(f"\n{Colors.RED}💥 Beklenmeyen hata: {e}{Colors.END}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
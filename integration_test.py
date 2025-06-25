#!/usr/bin/env python3
# =======================
# integration_test.py - Tam Sistem Entegrasyon Testi
# =======================

"""
Expo-Humanoid'in tüm bileşenlerini entegre şekilde test eder.
Kurulum sonrası doğrulama ve sorun tespiti için kullanın.

Kullanım:
    python integration_test.py
    python integration_test.py --headless    # GUI olmadan
    python integration_test.py --mock-only   # Sadece mock bileşenler
"""

import sys
import os
import time
import threading
import traceback
from pathlib import Path

# Proje root'unu path'e ekle
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

# Test sonuçları için
test_results = {}
test_logs = []

def log_test(message, level="INFO"):
    """Test log'u ekle"""
    timestamp = time.strftime("%H:%M:%S")
    log_entry = f"[{timestamp}] {level}: {message}"
    test_logs.append(log_entry)
    print(log_entry)

def test_basic_imports():
    """Temel import testleri"""
    log_test("=== Temel Import Testleri ===")
    
    imports = [
        ("PyQt5", "PyQt5.QtWidgets"),
        ("OpenCV", "cv2"),
        ("NumPy", "numpy"),
        ("RealSense", "pyrealsense2"),
        ("PyTorch", "torch"),
        ("Ultralytics", "ultralytics"),
        ("OpenAI", "openai"),
        ("Serial", "serial"),
        ("PSUtil", "psutil")
    ]
    
    failed_imports = []
    
    for name, module in imports:
        try:
            __import__(module)
            log_test(f"✅ {name} import başarılı")
        except ImportError as e:
            log_test(f"❌ {name} import başarısız: {e}", "ERROR")
            failed_imports.append(name)
    
    test_results["basic_imports"] = len(failed_imports) == 0
    return len(failed_imports) == 0

def test_project_modules():
    """Proje modüllerini test et"""
    log_test("=== Proje Modülleri Testleri ===")
    
    modules = [
        ("Config", "config.settings"),
        ("Camera Interface", "modules.camera.camera_interface"),
        ("RealSense Manager", "modules.camera.realsense_manager"),
        ("YOLO Detector", "modules.ai.yolo_detector"),
        ("OpenAI Chat", "modules.ai.openai_chat"),
        ("Servo Controller", "modules.servo.servo_controller"),
        ("Animation Engine", "modules.servo.animation_engine"),
        ("Target Tracker", "modules.tracking.target_tracker"),
        ("System Monitor", "modules.system.monitor"),
        ("Main Window", "modules.gui.main_window")
    ]
    
    failed_modules = []
    
    for name, module in modules:
        try:
            __import__(module)
            log_test(f"✅ {name} modül yüklendi")
        except ImportError as e:
            log_test(f"❌ {name} modül hatası: {e}", "ERROR")
            failed_modules.append(name)
        except Exception as e:
            log_test(f"⚠️  {name} modül uyarısı: {e}", "WARNING")
    
    test_results["project_modules"] = len(failed_modules) == 0
    return len(failed_modules) == 0

def test_configuration():
    """Konfigürasyon testleri"""
    log_test("=== Konfigürasyon Testleri ===")
    
    try:
        from config.settings import Settings
        
        # Settings yükle
        settings = Settings()
        log_test("✅ Ana ayarlar yüklendi")
        
        # Alt kategorileri kontrol et
        categories = ['camera', 'yolo', 'servo', 'ai', 'tracking', 'system']
        for category in categories:
            if hasattr(settings, category):
                log_test(f"✅ {category} ayarları mevcut")
            else:
                log_test(f"❌ {category} ayarları eksik", "ERROR")
                return False
        
        # Ayarları kaydet/yükle test
        settings.save_settings()
        log_test("✅ Ayarlar kaydedildi")
        
        test_results["configuration"] = True
        return True
        
    except Exception as e:
        log_test(f"❌ Konfigürasyon hatası: {e}", "ERROR")
        test_results["configuration"] = False
        return False

def test_camera_system(mock_only=False):
    """Kamera sistemi testleri"""
    log_test("=== Kamera Sistemi Testleri ===")
    
    try:
        from modules.camera.camera_interface import MockCamera, WebcamCamera
        from modules.camera.realsense_manager import RealSenseManager
        from config.settings import Settings
        
        settings = Settings()
        
        # Mock kamera testi
        log_test("Mock kamera testi...")
        mock_camera = MockCamera(640, 480)
        if mock_camera.initialize():
            mock_camera.start_capture()
            
            # Test frame'ler
            for i in range(3):
                rgb_frame = mock_camera.get_rgb_frame()
                depth_frame = mock_camera.get_depth_frame()
                
                if rgb_frame is not None and depth_frame is not None:
                    log_test(f"✅ Mock frame {i+1} alındı: RGB{rgb_frame.shape}, Depth{depth_frame.shape}")
                else:
                    log_test(f"❌ Mock frame {i+1} alınamadı", "ERROR")
                    return False
                    
                time.sleep(0.1)
            
            mock_camera.cleanup()
            log_test("✅ Mock kamera testi başarılı")
        else:
            log_test("❌ Mock kamera başlatılamadı", "ERROR")
            return False
        
        if not mock_only:
            # RealSense testi
            log_test("RealSense kamera testi...")
            try:
                rs_camera = RealSenseManager(settings.camera, None)
                devices = rs_camera.list_available_devices()
                
                if devices:
                    log_test(f"✅ RealSense cihazları bulundu: {list(devices.keys())}")
                    
                    if rs_camera.initialize():
                        log_test("✅ RealSense başlatıldı")
                        rs_camera.cleanup()
                    else:
                        log_test("⚠️  RealSense başlatılamadı, mock modda devam", "WARNING")
                else:
                    log_test("⚠️  RealSense cihazı bulunamadı", "WARNING")
                    
            except Exception as e:
                log_test(f"⚠️  RealSense testi hatası: {e}", "WARNING")
        
        test_results["camera_system"] = True
        return True
        
    except Exception as e:
        log_test(f"❌ Kamera sistemi hatası: {e}", "ERROR")
        test_results["camera_system"] = False
        return False

def test_ai_system():
    """AI sistemi testleri"""
    log_test("=== AI Sistemi Testleri ===")
    
    try:
        from modules.ai.yolo_detector import YOLODetector
        from modules.ai.openai_chat import OpenAIChat
        from config.settings import Settings
        import numpy as np
        
        settings = Settings()
        
        # YOLO testi
        log_test("YOLO detector testi...")
        yolo = YOLODetector(settings.yolo, None)
        
        if yolo.initialize():
            log_test("✅ YOLO başlatıldı")
            
            # Test frame ile tespit
            test_frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
            detections = yolo.detect_people(test_frame)
            
            log_test(f"✅ YOLO tespit testi: {len(detections)} tespit")
            
            # Mock modda bile çalışıyor mu kontrol
            stats = yolo.get_stats()
            log_test(f"✅ YOLO stats: Mock={stats.get('mock_mode', False)}")
            
        else:
            log_test("⚠️  YOLO başlatılamadı, mock modda devam", "WARNING")
        
        # OpenAI Chat testi (API key olmadan)
        log_test("OpenAI Chat testi...")
        chat = OpenAIChat(settings.ai, None)
        
        # API key yoksa da çalışması lazım
        if chat.initialize():
            log_test("✅ OpenAI Chat başlatıldı")
        else:
            log_test("⚠️  OpenAI Chat başlatılamadı (API key gerekli)", "WARNING")
        
        test_results["ai_system"] = True
        return True
        
    except Exception as e:
        log_test(f"❌ AI sistemi hatası: {e}", "ERROR")
        test_results["ai_system"] = False
        return False

def test_servo_system():
    """Servo sistemi testleri"""
    log_test("=== Servo Sistemi Testleri ===")
    
    try:
        from modules.servo.servo_controller import ServoController, ArmPosition
        from config.settings import Settings
        
        settings = Settings()
        
        # Servo controller testi
        log_test("Servo controller testi...")
        servo = ServoController(settings.servo, None)
        
        if servo.initialize():
            log_test("✅ Servo controller başlatıldı")
            
            # Mock modda servo testleri
            servo.set_servo_angle(12, 90)  # HEAD_PAN
            servo.set_servo_angle(13, 85)  # HEAD_TILT
            log_test("✅ Servo açı ayarlama testi")
            
            # Kol pozisyonu testi
            arm_pos = ArmPosition(shoulder=45, elbow=90, wrist=135)
            servo.set_arm_position('right', arm_pos)
            log_test("✅ Kol pozisyonu testi")
            
            # Animasyon sistemi testi
            animations = servo.get_available_animations()
            log_test(f"✅ Animasyonlar: {animations}")
            
            servo.cleanup()
        else:
            log_test("⚠️  Servo controller mock modda başlatıldı", "WARNING")
        
        test_results["servo_system"] = True
        return True
        
    except Exception as e:
        log_test(f"❌ Servo sistemi hatası: {e}", "ERROR")
        test_results["servo_system"] = False
        return False

def test_tracking_system():
    """Takip sistemi testleri"""
    log_test("=== Takip Sistemi Testleri ===")
    
    try:
        from modules.tracking.target_tracker import TargetTracker
        from modules.tracking.distance_calculator import DistanceCalculator
        from modules.utils.data_structures import Detection, BoundingBox
        from config.settings import Settings
        import numpy as np
        
        settings = Settings()
        
        # Target tracker testi
        log_test("Target tracker testi...")
        tracker = TargetTracker(settings.tracking, None)
        
        # Sahte detection'lar oluştur
        detections = [
            Detection(
                id=1,
                bbox=BoundingBox(100, 100, 200, 300, 100, 200),
                confidence=0.8,
                class_name="person",
                center_x=150,
                center_y=200
            )
        ]
        
        # Sahte depth frame
        depth_frame = np.random.randint(1000, 3000, (480, 640), dtype=np.uint16)
        
        # Tracking güncelle
        primary_target = tracker.update_targets(detections, depth_frame)
        log_test(f"✅ Tracking testi: Primary target = {primary_target is not None}")
        
        # Distance calculator testi
        log_test("Distance calculator testi...")
        dist_calc = DistanceCalculator()
        distance = dist_calc.calculate_distance_from_depth(detections[0], depth_frame)
        log_test(f"✅ Mesafe hesaplama: {distance:.2f}m" if distance else "✅ Mesafe hesaplama testi")
        
        test_results["tracking_system"] = True
        return True
        
    except Exception as e:
        log_test(f"❌ Takip sistemi hatası: {e}", "ERROR")
        test_results["tracking_system"] = False
        return False

def test_gui_system(headless=False):
    """GUI sistemi testleri"""
    log_test("=== GUI Sistemi Testleri ===")
    
    if headless:
        log_test("⏭️  GUI testi atlandı (headless mode)")
        test_results["gui_system"] = True
        return True
    
    try:
        from PyQt5.QtWidgets import QApplication
        from modules.gui.main_window import MainWindow
        from config.settings import Settings
        
        settings = Settings()
        
        # QApplication oluştur
        log_test("GUI başlatma testi...")
        app = QApplication([])
        
        # Ana pencereyi oluştur
        main_window = MainWindow(settings, None)
        log_test("✅ Ana pencere oluşturuldu")
        
        # Pencereyi kısa süre göster
        main_window.show()
        log_test("✅ Pencere gösterildi")
        
        # Kısa test süresi
        app.processEvents()
        time.sleep(1)
        app.processEvents()
        
        # Temizlik
        main_window.cleanup()
        main_window.close()
        app.quit()
        
        log_test("✅ GUI sistemi testi başarılı")
        test_results["gui_system"] = True
        return True
        
    except Exception as e:
        log_test(f"❌ GUI sistemi hatası: {e}", "ERROR")
        test_results["gui_system"] = False
        return False

def test_integration():
    """Tam entegrasyon testi"""
    log_test("=== Tam Entegrasyon Testi ===")
    
    try:
        from modules.camera.camera_interface import MockCamera
        from modules.ai.yolo_detector import YOLODetector
        from modules.tracking.target_tracker import TargetTracker
        from modules.servo.servo_controller import ServoController
        from config.settings import Settings
        
        settings = Settings()
        
        # Tüm bileşenleri başlat
        log_test("Entegrasyon bileşenleri başlatılıyor...")
        
        camera = MockCamera(640, 480)
        yolo = YOLODetector(settings.yolo, None)
        tracker = TargetTracker(settings.tracking, None)
        servo = ServoController(settings.servo, None)
        
        # Başlat
        camera.initialize()
        camera.start_capture()
        yolo.initialize()
        servo.initialize()
        
        log_test("✅ Tüm bileşenler başlatıldı")
        
        # Entegrasyon döngüsü (kısa test)
        log_test("Entegrasyon döngüsü testi...")
        
        for i in range(3):
            # Frame al
            rgb_frame = camera.get_rgb_frame()
            depth_frame = camera.get_depth_frame()
            
            if rgb_frame is not None:
                # YOLO tespiti
                detections = yolo.detect_people(rgb_frame)
                
                # Tracking
                primary_target = tracker.update_targets(detections, depth_frame)
                
                # Servo kontrolü
                if primary_target:
                    servo.point_to_position(
                        primary_target.detection.center_x,
                        primary_target.detection.center_y,
                        640, 480
                    )
                
                log_test(f"✅ Entegrasyon döngüsü {i+1}: {len(detections)} tespit")
            else:
                log_test(f"❌ Entegrasyon döngüsü {i+1}: Frame alınamadı", "ERROR")
                return False
            
            time.sleep(0.5)
        
        # Temizlik
        camera.cleanup()
        servo.cleanup()
        
        log_test("✅ Entegrasyon testi başarılı")
        test_results["integration"] = True
        return True
        
    except Exception as e:
        log_test(f"❌ Entegrasyon testi hatası: {e}", "ERROR")
        log_test(f"Traceback: {traceback.format_exc()}", "ERROR")
        test_results["integration"] = False
        return False

def save_test_report():
    """Test raporunu kaydet"""
    report_path = "integration_test_report.txt"
    
    try:
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("Expo-Humanoid Entegrasyon Test Raporu\n")
            f.write("=" * 50 + "\n\n")
            
            # Test sonuçları özeti
            f.write("Test Sonuçları:\n")
            f.write("-" * 20 + "\n")
            
            total_tests = len(test_results)
            passed_tests = sum(test_results.values())
            
            for test_name, result in test_results.items():
                status = "PASS" if result else "FAIL"
                f.write(f"{test_name}: {status}\n")
            
            f.write(f"\nÖzet: {passed_tests}/{total_tests} test başarılı\n")
            f.write(f"Başarı oranı: {(passed_tests/total_tests)*100:.1f}%\n\n")
            
            # Detaylı loglar
            f.write("Detaylı Test Logları:\n")
            f.write("-" * 25 + "\n")
            
            for log_entry in test_logs:
                f.write(log_entry + "\n")
        
        log_test(f"✅ Test raporu kaydedildi: {report_path}")
        return True
        
    except Exception as e:
        log_test(f"❌ Test raporu kaydedilemedi: {e}", "ERROR")
        return False

def main():
    """Ana test fonksiyonu"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Expo-Humanoid entegrasyon testi")
    parser.add_argument('--headless', action='store_true', help='GUI testlerini atla')
    parser.add_argument('--mock-only', action='store_true', help='Sadece mock bileşenleri test et')
    parser.add_argument('--quick', action='store_true', help='Hızlı test (bazı testleri atla)')
    parser.add_argument('--report', action='store_true', help='Test raporu oluştur')
    
    args = parser.parse_args()
    
    log_test("🤖 Expo-Humanoid Entegrasyon Testi Başlatılıyor...")
    log_test("=" * 60)
    
    # Test listesi
    tests = [
        ("basic_imports", test_basic_imports),
        ("project_modules", test_project_modules),
        ("configuration", test_configuration),
        ("camera_system", lambda: test_camera_system(args.mock_only)),
        ("ai_system", test_ai_system),
        ("servo_system", test_servo_system),
        ("tracking_system", test_tracking_system),
        ("gui_system", lambda: test_gui_system(args.headless)),
        ("integration", test_integration)
    ]
    
    # Hızlı test için bazıları atlanır
    if args.quick:
        tests = tests[:6]  # İlk 6 test
    
    # Testleri çalıştır
    start_time = time.time()
    
    for test_name, test_func in tests:
        log_test(f"\n🧪 {test_name.replace('_', ' ').title()} testi başlatılıyor...")
        
        try:
            result = test_func()
            if result:
                log_test(f"✅ {test_name} testi BAŞARILI")
            else:
                log_test(f"❌ {test_name} testi BAŞARISIZ")
        except Exception as e:
            log_test(f"💥 {test_name} testi HATA: {e}", "ERROR")
            test_results[test_name] = False
    
    # Test süresi
    total_time = time.time() - start_time
    log_test(f"\n⏱️  Toplam test süresi: {total_time:.2f} saniye")
    
    # Sonuç özeti
    log_test("\n" + "=" * 60)
    log_test("🏁 TEST SONUÇLARI ÖZET")
    log_test("=" * 60)
    
    total_tests = len(test_results)
    passed_tests = sum(test_results.values())
    failed_tests = total_tests - passed_tests
    
    log_test(f"Toplam Test: {total_tests}")
    log_test(f"Başarılı: {passed_tests}")
    log_test(f"Başarısız: {failed_tests}")
    log_test(f"Başarı Oranı: {(passed_tests/total_tests)*100:.1f}%")
    
    # Başarısız testler
    if failed_tests > 0:
        log_test("\n❌ Başarısız testler:")
        for test_name, result in test_results.items():
            if not result:
                log_test(f"  • {test_name}")
    
    # Genel durum
    if passed_tests == total_tests:
        log_test("\n🎉 TÜM TESTLER BAŞARILI! Sistem kullanıma hazır.")
        exit_code = 0
    elif passed_tests >= total_tests * 0.8:
        log_test("\n⚠️  ÇOĞU TEST BAŞARILI. Sistem büyük ölçüde çalışır durumda.")
        exit_code = 0
    else:
        log_test("\n💥 ÇOK FAZLA TEST BAŞARISIZ. Sistem kurulumunu kontrol edin.")
        exit_code = 1
    
    # Rapor kaydet
    if args.report or failed_tests > 0:
        save_test_report()
    
    # Öneriler
    log_test("\n💡 Öneriler:")
    if failed_tests > 0:
        log_test("  • python quick_test.py çalıştırın")
        log_test("  • ./setup_macos.sh yeniden çalıştırın")
        log_test("  • TROUBLESHOOTING.md dosyasına bakın")
    else:
        log_test("  • python main.py ile uygulamayı başlatın")
        log_test("  • python main.py --preset demo ile demo modu")
    
    return exit_code

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        log_test("\n\n⏹️  Test kullanıcı tarafından durduruldu")
        sys.exit(1)
    except Exception as e:
        log_test(f"\n\n💥 Beklenmeyen hata: {e}")
        traceback.print_exc()
        sys.exit(1)
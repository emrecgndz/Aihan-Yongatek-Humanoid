#!/usr/bin/env python3
# =======================
# test_camera_d435i.py - RealSense D435i Test Script'i
# =======================

"""
RealSense D435i kamerasını test etmek için basit script.
Bu script'i çalıştırarak kameranızın çalışıp çalışmadığını kontrol edebilirsiniz.

Kullanım:
    python test_camera_d435i.py
"""

import sys
import os
import time
import traceback

# Proje root'unu path'e ekle
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Gerekli kütüphaneleri test et"""
    print("=== Kütüphane İmport Testi ===")
    
    # OpenCV
    try:
        import cv2
        print(f"✓ OpenCV: {cv2.__version__}")
    except ImportError as e:
        print(f"✗ OpenCV: {e}")
        return False
    
    # PyRealSense2
    try:
        import pyrealsense2 as rs
        print(f"✓ PyRealSense2: Yüklü")
    except ImportError as e:
        print(f"✗ PyRealSense2: {e}")
        print("  Çözüm: pip install pyrealsense2")
        return False
    
    # NumPy
    try:
        import numpy as np
        print(f"✓ NumPy: {np.__version__}")
    except ImportError as e:
        print(f"✗ NumPy: {e}")
        return False
    
    return True

def test_realsense_devices():
    """RealSense cihazlarını test et"""
    print("\n=== RealSense Cihaz Testi ===")
    
    try:
        import pyrealsense2 as rs
        
        # Context oluştur
        ctx = rs.context()
        devices = ctx.query_devices()
        
        if len(devices) == 0:
            print("✗ RealSense cihazı bulunamadı")
            print("  Kontrol listesi:")
            print("  1. Kamera USB 3.0 porta bağlı mı?")
            print("  2. RealSense SDK doğru yüklü mü?")
            print("  3. macOS'ta kamera izinleri verildi mi?")
            print("  4. Başka uygulama kamerayı kullanıyor mu?")
            return False
        
        print(f"✓ {len(devices)} RealSense cihazı bulundu:")
        
        for i, device in enumerate(devices):
            try:
                name = device.get_info(rs.camera_info.name)
                serial = device.get_info(rs.camera_info.serial_number)
                firmware = device.get_info(rs.camera_info.firmware_version)
                product_id = device.get_info(rs.camera_info.product_id)
                
                print(f"  Cihaz {i+1}:")
                print(f"    Adı: {name}")
                print(f"    Seri No: {serial}")
                print(f"    Firmware: {firmware}")
                print(f"    Ürün ID: {product_id}")
                
                # D435i kontrolü
                if "D435I" in name.upper() or "D435I" in product_id:
                    print(f"    ✓ D435i cihazı tespit edildi!")
                elif "D435" in name.upper():
                    print(f"    ! D435 (IMU'suz) tespit edildi")
                else:
                    print(f"    ? Bilinmeyen RealSense modeli")
                    
            except Exception as e:
                print(f"    ✗ Cihaz bilgisi alınamadı: {e}")
        
        return True
        
    except Exception as e:
        print(f"✗ RealSense test hatası: {e}")
        traceback.print_exc()
        return False

def test_camera_streams():
    """Kamera stream'lerini test et"""
    print("\n=== Kamera Stream Testi ===")
    
    try:
        import pyrealsense2 as rs
        import numpy as np
        
        # Pipeline oluştur
        pipeline = rs.pipeline()
        config = rs.config()
        
        # Stream'leri yapılandır
        print("Stream'ler yapılandırılıyor...")
        
        # RGB stream
        try:
            config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
            print("✓ RGB stream: 640x480@30fps")
        except Exception as e:
            print(f"✗ RGB stream hatası: {e}")
            
        # Depth stream
        try:
            config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
            print("✓ Depth stream: 640x480@30fps")
        except Exception as e:
            print(f"✗ Depth stream hatası: {e}")
        
        # Pipeline'ı başlat
        print("\nPipeline başlatılıyor...")
        profile = pipeline.start(config)
        
        # Device bilgisi
        device = profile.get_device()
        device_name = device.get_info(rs.camera_info.name)
        print(f"✓ Pipeline başlatıldı: {device_name}")
        
        # Depth scale
        depth_sensor = device.first_depth_sensor()
        depth_scale = depth_sensor.get_depth_scale()
        print(f"✓ Depth scale: {depth_scale} metre/birim")
        
        # Frame'leri test et
        print("\nFrame'ler test ediliyor...")
        frame_count = 0
        test_duration = 5  # saniye
        start_time = time.time()
        
        while time.time() - start_time < test_duration:
            try:
                frames = pipeline.wait_for_frames(timeout_ms=1000)
                
                # RGB frame
                color_frame = frames.get_color_frame()
                if color_frame:
                    rgb_data = np.asanyarray(color_frame.get_data())
                    if frame_count == 0:
                        print(f"✓ RGB frame: {rgb_data.shape}, dtype: {rgb_data.dtype}")
                
                # Depth frame
                depth_frame = frames.get_depth_frame()
                if depth_frame:
                    depth_data = np.asanyarray(depth_frame.get_data())
                    if frame_count == 0:
                        print(f"✓ Depth frame: {depth_data.shape}, dtype: {depth_data.dtype}")
                
                frame_count += 1
                
            except Exception as e:
                print(f"✗ Frame alma hatası: {e}")
                break
        
        # İstatistikler
        elapsed = time.time() - start_time
        fps = frame_count / elapsed
        print(f"\n✓ Test tamamlandı:")
        print(f"  Frame sayısı: {frame_count}")
        print(f"  Süre: {elapsed:.1f} saniye")
        print(f"  Ortalama FPS: {fps:.1f}")
        
        # Pipeline'ı durdur
        pipeline.stop()
        print("✓ Pipeline durduruldu")
        
        return True
        
    except Exception as e:
        print(f"✗ Stream test hatası: {e}")
        traceback.print_exc()
        return False

def test_camera_with_display():
    """Kamerayı görüntü ile test et"""
    print("\n=== Görüntülü Kamera Testi ===")
    print("Not: Bu test bir pencere açacak. ESC'ye basarak kapatabilirsiniz.")
    
    input("Devam etmek için Enter'a basın (Ctrl+C ile iptal)...")
    
    try:
        import pyrealsense2 as rs
        import numpy as np
        import cv2
        
        # Pipeline oluştur
        pipeline = rs.pipeline()
        config = rs.config()
        
        # Stream'leri etkinleştir
        config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
        config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
        
        # Pipeline'ı başlat
        pipeline.start(config)
        print("✓ Kamera başlatıldı")
        
        # Colorizer (depth'i renklendir)
        colorizer = rs.colorizer()
        
        # Ana döngü
        print("Kamera görüntüsü açılıyor... ESC'ye basarak kapatın.")
        
        try:
            while True:
                # Frame'leri al
                frames = pipeline.wait_for_frames()
                
                # RGB frame
                color_frame = frames.get_color_frame()
                depth_frame = frames.get_depth_frame()
                
                if not color_frame or not depth_frame:
                    continue
                
                # Numpy array'e çevir
                rgb_image = np.asanyarray(color_frame.get_data())
                depth_image = np.asanyarray(colorizer.colorize(depth_frame).get_data())
                
                # İki görüntüyü yan yana birleştir
                combined = np.hstack((rgb_image, depth_image))
                
                # Bilgi yazısı ekle
                cv2.putText(combined, "RGB (Sol) | Depth (Sag) - ESC'ye basarak cik", 
                           (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                
                # Göster
                cv2.imshow('RealSense D435i Test', combined)
                
                # ESC'ye basıldı mı kontrol et
                if cv2.waitKey(1) & 0xFF == 27:  # ESC key
                    break
                    
        except KeyboardInterrupt:
            print("\nKullanıcı tarafından durduruldu")
        
        # Temizlik
        cv2.destroyAllWindows()
        pipeline.stop()
        print("✓ Test tamamlandı")
        
        return True
        
    except Exception as e:
        print(f"✗ Görüntülü test hatası: {e}")
        traceback.print_exc()
        return False

def main():
    """Ana test fonksiyonu"""
    print("RealSense D435i Kamera Test Programı")
    print("=====================================\n")
    
    # Test 1: Kütüphane import'ları
    if not test_imports():
        print("\n❌ Kütüphane testleri başarısız!")
        return False
    
    # Test 2: RealSense cihaz tespiti
    if not test_realsense_devices():
        print("\n❌ Cihaz testleri başarısız!")
        return False
    
    # Test 3: Stream testleri
    if not test_camera_streams():
        print("\n❌ Stream testleri başarısız!")
        return False
    
    # Test 4: Görüntülü test (opsiyonel)
    print("\n" + "="*50)
    response = input("Görüntülü test yapmak istiyor musunuz? (y/N): ").lower()
    if response in ['y', 'yes', 'evet']:
        test_camera_with_display()
    
    print("\n" + "="*50)
    print("🎉 Tüm testler tamamlandı!")
    print("\nKameranız çalışıyor durumdadır.")
    print("Ana uygulamayı şu komutla çalıştırabilirsiniz:")
    print("    python main.py")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTest kullanıcı tarafından durduruldu.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Beklenmeyen hata: {e}")
        traceback.print_exc()
        sys.exit(1)
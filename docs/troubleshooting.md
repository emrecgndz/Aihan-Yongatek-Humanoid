# Expo-Humanoid Sorun Giderme Rehberi

## 🚨 Acil Durum Kontrol Listesi

### Sistem Çalışmıyor?
```bash
# 1. Hızlı test
python quick_test.py

# 2. Kamera test
python test_camera_d435i.py

# 3. Mock mode ile test
python main.py --camera mock --log-level DEBUG
```

## 📋 Sık Karşılaşılan Sorunlar

### 1. **Kamera Siyah Kalıyor / Çalışmıyor**

#### RealSense D435i Sorunları
```bash
# Cihaz listesi kontrol
rs-enumerate-devices

# Eğer boş çıkıyorsa:
brew uninstall librealsense
brew tap intelrealsense/librealsense
brew install librealsense

# Kamera iznini kontrol et (macOS)
# System Preferences > Security & Privacy > Camera
```

#### USB Bağlantı Sorunları
- ✅ **USB 3.0 port kullanın** (mavi renkli)
- ✅ **Hub kullanmayın**, direkt bilgisayara bağlayın
- ✅ **Farklı USB port** deneyin
- ✅ **Kablo değiştirin** (kaliteli USB 3.0 kablo)

#### macOS İzin Sorunları
```bash
# Terminal'e kamera izni ver
# System Preferences > Security & Privacy > Privacy > Camera
# Terminal uygulamasını işaretleyin

# Eğer Python app görünüyorsa onu da işaretleyin
```

### 2. **PyQt5 / GUI Sorunları**

#### Import Hataları
```bash
# PyQt5'i yeniden yükle
pip uninstall PyQt5 PyQt5-Qt5 PyQt5-sip
pip install PyQt5==5.15.9

# macOS için özel
brew install pyqt@5
```

#### Display Sorunları
```bash
# macOS için
export QT_MAC_WANTS_LAYER=1

# Retina display sorunları için
export QT_AUTO_SCREEN_SCALE_FACTOR=1
```

### 3. **YOLO Model Sorunları**

#### Model Dosyası Bulunamadı
```bash
# Model dizini oluştur
mkdir -p data/models

# Model indir
python -c "
from ultralytics import YOLO
import shutil
model = YOLO('yolov8n.pt')
shutil.move('yolov8n.pt', 'data/models/yolov8n.pt')
print('Model indirildi')
"
```

#### CUDA/PyTorch Sorunları
```bash
# CPU moduna zorla
# settings.json içinde:
# "yolo": {"device": "cpu"}

# PyTorch yeniden yükle
pip uninstall torch torchvision
pip install torch==2.0.1 torchvision==0.15.2
```

### 4. **Arduino/Servo Sorunları**

#### Seri Port Bulunamadı
```bash
# macOS için portları listele
ls /dev/cu.*

# Linux için
ls /dev/ttyUSB* /dev/ttyACM*

# Port izinleri (Linux)
sudo usermod -a -G dialout $USER
```

#### Arduino Sketch Yükleme
1. Arduino IDE'yi açın
2. `arduino_servo_controller.ino` dosyasını açın
3. Board: Arduino Uno/Mega seçin
4. Port'u seçin
5. Upload edin

#### Seri Port İzinleri (macOS)
```bash
# Dialout grubuna ekle
sudo dscl . -append /Groups/dialout GroupMembership $USER

# Terminal'i yeniden başlat
```

### 5. **Performance Sorunları**

#### Düşük FPS
```python
# settings.json içinde:
{
  "camera": {
    "width": 640,
    "height": 480,
    "fps": 30
  },
  "yolo": {
    "device": "cpu"  # GPU yoksa
  }
}
```

#### Yüksek CPU Kullanımı
- Frame skip kullanın
- YOLO confidence threshold'u artırın (0.7)
- Düşük çözünürlük kullanın (640x480)

### 6. **Network/API Sorunları**

#### OpenAI API
```bash
# API key test
export OPENAI_API_KEY="your-key-here"
python -c "
import openai
openai.api_key = 'your-key'
try:
    response = openai.ChatCompletion.create(
        model='gpt-3.5-turbo',
        messages=[{'role': 'user', 'content': 'test'}],
        max_tokens=5
    )
    print('API çalışıyor')
except Exception as e:
    print(f'API hatası: {e}')
"
```

## 🔧 Gelişmiş Sorun Giderme

### Debug Mode
```bash
# Maksimum debug bilgisi
python main.py --debug --log-level DEBUG --camera mock

# Log dosyalarını kontrol et
tail -f logs/expo_humanoid_*.log
```

### Memory Leaks
```bash
# Memory monitoring
python -c "
import psutil
import time
process = psutil.Process()
for i in range(10):
    print(f'Memory: {process.memory_info().rss / 1024 / 1024:.1f}MB')
    time.sleep(1)
"
```

### GPU Memory (NVIDIA)
```python
import torch
if torch.cuda.is_available():
    print(f"GPU: {torch.cuda.get_device_name()}")
    print(f"Memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f}GB")
    torch.cuda.empty_cache()  # Memory temizle
```

## 📱 Platform Özel Sorunlar

### macOS Monterey/Ventura
```bash
# Rosetta 2 (M1 Mac için)
softwareupdate --install-rosetta

# Homebrew path
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile

# Python path
export PATH="/opt/homebrew/bin/python3:$PATH"
```

### Linux (Ubuntu)
```bash
# Additional dependencies
sudo apt install python3-pyqt5 python3-opencv

# RealSense
echo 'deb https://librealsense.intel.com/Debian/apt-repo $(lsb_release -cs) main' | sudo tee /etc/apt/sources.list.d/librealsense.list
sudo apt-key adv --keyserver keys.gnupg.net --recv-key F6E65AC044F831AC80A06380C8B3A55A6F3EFCDE
sudo apt update
sudo apt install librealsense2-devel
```

### Windows
```cmd
# Intel RealSense SDK
# GitHub'dan Windows installer indir

# Visual Studio Build Tools
# C++ build tools yükle

# PyQt5 için
pip install PyQt5 --no-cache-dir
```

## 🔍 Diagnostic Tools

### System Info Script
```bash
# Sistem bilgileri topla
python -c "
import platform
import sys
import subprocess

print('=== System Info ===')
print(f'OS: {platform.system()} {platform.release()}')
print(f'Python: {sys.version}')
print(f'Architecture: {platform.machine()}')

try:
    result = subprocess.run(['brew', '--version'], capture_output=True, text=True)
    print(f'Homebrew: {result.stdout.split()[1] if result.returncode == 0 else \"Not installed\"}')
except:
    print('Homebrew: Not found')
"
```

### Camera Debug
```python
# Detaylı kamera testi
import pyrealsense2 as rs
import cv2
import numpy as np

def debug_camera():
    pipeline = rs.pipeline()
    config = rs.config()
    
    try:
        # Profilleri listele
        prof = pipeline.start(config)
        device = prof.get_device()
        
        print(f"Device: {device.get_info(rs.camera_info.name)}")
        print(f"Serial: {device.get_info(rs.camera_info.serial_number)}")
        print(f"Firmware: {device.get_info(rs.camera_info.firmware_version)}")
        
        # Test frame'ler
        for i in range(10):
            frames = pipeline.wait_for_frames()
            color_frame = frames.get_color_frame()
            if color_frame:
                print(f"Frame {i}: OK")
            else:
                print(f"Frame {i}: FAIL")
        
        pipeline.stop()
        print("Camera test completed")
        
    except Exception as e:
        print(f"Camera test failed: {e}")

debug_camera()
```

## 💡 Performans Optimizasyonu

### Önerilen Ayarlar (Düşük Performans)
```json
{
  "camera": {
    "width": 640,
    "height": 480,
    "fps": 15
  },
  "yolo": {
    "confidence_threshold": 0.7,
    "device": "cpu",
    "max_detections": 5
  },
  "tracking": {
    "tracking_smoothing": 0.5
  }
}
```

### Önerilen Ayarlar (Yüksek Performans)
```json
{
  "camera": {
    "width": 1280,
    "height": 720,
    "fps": 30
  },
  "yolo": {
    "confidence_threshold": 0.5,
    "device": "cuda",
    "max_detections": 10
  },
  "tracking": {
    "tracking_smoothing": 0.3
  }
}
```

## 🆘 Son Çare

### Temiz Kurulum
```bash
# Eski kurulumu temizle
rm -rf venv
rm -rf data/models
rm -rf logs

# Homebrew paketlerini yeniden yükle
brew uninstall librealsense opencv python@3.10
brew install python@3.10 opencv librealsense

# Sanal ortamı yeniden oluştur
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Setup script'ini çalıştır
./setup_macos.sh
```

### Factory Reset
```bash
# Git repoyu temizle
git clean -fdx
git reset --hard HEAD

# Kurulum script'ini yeniden çalıştır
./setup_macos.sh
```

## 📞 Yardım Alma

### Log Dosyalarını Paylaş
```bash
# Log dosyalarını zip'le
zip -r logs.zip logs/

# Diagnostic report oluştur
python quick_test.py --report
```

### GitHub Issues Template
```markdown
**Sorun Açıklaması:**
Kısa açıklama

**Sisteminiz:**
- OS: macOS 13.0
- Python: 3.10.8
- Kamera: RealSense D435i

**Denenen Çözümler:**
- [ ] quick_test.py çalıştırıldı
- [ ] setup_macos.sh yeniden çalıştırıldı
- [ ] ...

**Log Dosyaları:**
(log dosyalarını ekleyin)

**Hata Mesajı:**
```
Error message here
```
```

---

💡 **İpucu**: Çoğu sorun `python quick_test.py` çalıştırılarak teşhis edilebilir!
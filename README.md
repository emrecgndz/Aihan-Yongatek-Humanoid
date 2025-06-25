# =======================
# docs/README.md - Ana Dokümantasyon
# =======================

"""
# Expo-Humanoid İnteraktif Robotik Sunum Sistemi

## Genel Bakış

Expo-Humanoid, Intel RealSense D455 derinlik kamerası ve YOLOv8-People modeli ile gerçek zamanlı insan algılama, tanımlama ve takip sistemlerini gelişmiş bir insansı robot platformuna entegre eden profesyonel bir interaktif robotik sunum sistemidir.

## Özellikler

### 🎯 Görüntü İşleme ve Derinlik Algısı
- Intel RealSense D455 ile RGB-D görüntü yakalama
- YOLOv8-People modeli ile CUDA hızlandırmalı insan tespiti
- Gerçek zamanlı mesafe ve 3D koordinat hesaplama
- Çoklu kişi takibi ve akıllı hedef seçimi

### 🤖 Servo Motor Yönetimi
- 14 DOF (Degrees of Freedom) servo motor kontrolü
- 12 DOF kol hareketleri (her kol 6 servo)
- 2 DOF kafa ve boyun hareketleri
- PID kontrollü yumuşak hareket profilleri

### 🧠 Yapay Zeka Destekli Sohbet
- OpenAI GPT-4o API entegrasyonu
- Türkçe ve İngilizce doğal dil işleme
- Bağlamsal sohbet ve durum farkındalığı

### 💻 Modern GUI Kontrolü
- PyQt5 tabanlı tek pencere kontrol merkezi
- Gerçek zamanlı sistem izleme
- Kapsamlı manuel kontrol seçenekleri
- Hızlı preset modları

## Sistem Gereksinimleri

### Donanım
- Intel RealSense D455 kamera
- 14x servo motor (örn: SG90, MG996R)
- Arduino Uno/Mega veya uyumlu mikrodenetleyici
- NVIDIA GPU (CUDA desteği için önerilen)
- macOS (test edildi) / Linux / Windows

### Yazılım
- Python 3.8+
- PyQt5
- OpenCV
- PyRealSense2
- Ultralytics YOLOv8
- PyTorch
- OpenAI Python kütüphanesi

## Kurulum

### 1. Depo Klonlama
```bash
git clone https://github.com/your-repo/expo-humanoid.git
cd expo-humanoid
```

### 2. Sanal Ortam Oluşturma
```bash
python -m venv expo_humanoid_env
source expo_humanoid_env/bin/activate  # macOS/Linux
# veya
expo_humanoid_env\Scripts\activate  # Windows
```

### 3. Bağımlılıkları Yükleme
```bash
pip install -r requirements.txt
```

### 4. YOLO Modelini İndirme
```bash
# YOLOv8n-person modelini indirin
mkdir -p data/models
wget https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.pt -O data/models/yolov8n-person.pt
```

### 5. Konfigürasyon
```bash
cp config/settings_template.json config/settings.json
# Ayarları ihtiyaçlarınıza göre düzenleyin
```

## Kullanım

### Temel Başlatma
```bash
python main.py
```

### Gelişmiş Başlatma
```bash
# Demo modu ile başlat
python main.py --preset demo

# Manuel modda başlat
python main.py --preset manual

# Kalibrasyon modunda başlat
python main.py --preset calibration
```

## Konfigürasyon

### Kamera Ayarları
```json
{
  "camera": {
    "width": 720,
    "height": 480,
    "fps": 30,
    "enable_rgb": true,
    "enable_depth": true
  }
}
```

### YOLO Ayarları
```json
{
  "yolo": {
    "model_path": "data/models/yolov8n-person.pt",
    "confidence_threshold": 0.5,
    "device": "cuda",
    "enable_tracking": true
  }
}
```

### Servo Ayarları
```json
{
  "servo": {
    "port": "/dev/cu.usbserial-...",
    "baudrate": 115200,
    "movement_speed": 5,
    "enable_pid": true
  }
}
```

## API Referansı

### Kamera Modülü
```python
from modules.camera.realsense_manager import RealSenseManager

camera = RealSenseManager(settings.camera, logger)
camera.initialize()
camera.start_capture()

rgb_frame = camera.get_rgb_frame()
depth_frame = camera.get_depth_frame()
```

### YOLO Detektör
```python
from modules.ai.yolo_detector import YOLODetector

detector = YOLODetector(settings.yolo, logger)
detector.initialize()

detections = detector.detect_people(frame)
annotated_frame = detector.draw_detections(frame, detections)
```

### Servo Kontrolcü
```python
from modules.servo.servo_controller import ServoController

servo_controller = ServoController(settings.servo, logger)
servo_controller.initialize()

# Kafa pozisyonu ayarla
servo_controller.set_head_position(pan=90, tilt=85)

# Kol pozisyonu ayarla
arm_position = ArmPosition(shoulder=45, elbow=90, wrist=135)
servo_controller.set_arm_position('right', arm_position)
```

## Animasyon Sistemi

### Animasyon Oluşturma
```json
{
  "name": "greeting",
  "description": "Selamlama hareketi",
  "loop": false,
  "keyframes": [
    {
      "timestamp": 0.0,
      "servo_positions": {"12": 90, "13": 85},
      "duration": 1.0,
      "easing": "ease_in_out"
    }
  ]
}
```

### Animasyon Oynatma
```python
from modules.servo.animation_engine import AnimationEngine

animation_engine = AnimationEngine(servo_controller, logger)
animation_engine.play_animation("greeting")
```

## Troubleshooting

### Kamera Bağlantı Sorunları
1. RealSense SDK'nın doğru yüklendiğinden emin olun
2. Kamera USB 3.0 portuna bağlı olduğunu kontrol edin
3. Diğer uygulamaların kamerayı kullanmadığından emin olun

### YOLO Model Sorunları
1. Model dosyasının doğru konumda olduğunu kontrol edin
2. CUDA kurulumunu kontrol edin
3. PyTorch ve Ultralytics versiyonlarını kontrol edin

### Servo Bağlantı Sorunları
1. Arduino'nun doğru porta bağlı olduğunu kontrol edin
2. Seri port izinlerini kontrol edin (Linux/macOS)
3. Arduino sketch'inin yüklendiğinden emin olun

## Geliştirme

### Test Çalıştırma
```bash
# Tüm testleri çalıştır
python tests/run_tests.py

# Belirli modül testini çalıştır
python tests/run_tests.py camera
python tests/run_tests.py yolo
python tests/run_tests.py servo
```

### Kod Kalitesi
```bash
# Linting
flake8 modules/
pylint modules/

# Type checking
mypy modules/
```

## Katkıda Bulunma

1. Fork oluşturun
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Değişikliklerinizi commit edin (`git commit -m 'Add amazing feature'`)
4. Branch'i push edin (`git push origin feature/amazing-feature`)
5. Pull Request oluşturun

## Lisans

Bu proje MIT Lisansı altında lisanslanmıştır. Detaylar için `LICENSE` dosyasına bakın.

## İletişim

- Proje Sahibi: [Your Name]
- Email: your.email@example.com
- Proje Linki: https://github.com/your-repo/expo-humanoid

## Acknowledgments

- Intel RealSense ekibi
- Ultralytics YOLOv8 ekibi
- OpenAI ekibi
- PyQt5 geliştiricileri
"""
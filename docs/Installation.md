# =======================
# docs/Installation.md - Kurulum Rehberi
# =======================

"""
# Expo-Humanoid Kurulum Rehberi

## Sistem Gereksinimleri

### Minimum Donanım
- Intel RealSense D455 kamera
- Arduino Uno/Mega
- 14x Servo motor
- 4GB RAM
- USB 3.0 port

### Önerilen Donanım
- NVIDIA GPU (GTX 1660 veya üzeri)
- 8GB+ RAM
- SSD depolama
- USB 3.0 hub (çoklu cihaz için)

## macOS Kurulumu

### 1. Homebrew Kurulumu
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### 2. Python ve Bağımlılıklar
```bash
brew install python@3.10
brew install cmake
brew install pkg-config
```

### 3. Intel RealSense SDK
```bash
brew install librealsense
```

### 4. Proje Kurulumu
```bash
git clone https://github.com/your-repo/expo-humanoid.git
cd expo-humanoid
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Linux (Ubuntu) Kurulumu

### 1. Sistem Güncellemesi
```bash
sudo apt update && sudo apt upgrade -y
```

### 2. Bağımlılıklar
```bash
sudo apt install python3 python3-pip python3-venv
sudo apt install cmake build-essential
sudo apt install libusb-1.0-0-dev pkg-config
sudo apt install libglfw3-dev libgl1-mesa-dev libglu1-mesa-dev
```

### 3. Intel RealSense SDK
```bash
sudo apt-key adv --keyserver keys.gnupg.net --recv-key F6E65AC044F831AC80A06380C8B3A55A6F3EFCDE
sudo add-apt-repository "deb https://librealsense.intel.com/Debian/apt-repo $(lsb_release -cs) main" -u
sudo apt install librealsense2-devel librealsense2-utils
```

### 4. CUDA (Opsiyonel)
```bash
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2004/x86_64/cuda-ubuntu2004.pin
sudo mv cuda-ubuntu2004.pin /etc/apt/preferences.d/cuda-repository-pin-600
sudo apt-key adv --fetch-keys https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2004/x86_64/7fa2af80.pub
sudo add-apt-repository "deb https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2004/x86_64/ /"
sudo apt update
sudo apt install cuda
```

## Windows Kurulumu

### 1. Python Kurulumu"
- Python 3.10'u python.org'dan indirin
- "Add to PATH" seçeneğini işaretleyin

### 2. Visual Studio Build Tools
- Visual Studio Build Tools'u indirin
- C++ build tools'ları yükleyin

### 3. Intel RealSense SDK
- GitHub'dan Windows installer'ı indirin
- SDK'yı kurun ve PATH'e ekleyin

### 4. Git ve Proje
```cmd
git clone https://github.com/your-repo/expo-humanoid.git
cd expo-humanoid
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## Arduino Kurulumu

### 1. Arduino IDE
Arduino IDE'yi arduino.cc'den indirin ve kurun.

### 2. Servo Control Sketch
```cpp
// arduino_servo_controller.ino
#include <Servo.h>

Servo servos[14];
int servoPins[14] = {2,3,4,5,6,7,8,9,10,11,12,13,A0,A1};

void setup() {
  Serial.begin(115200);
  for(int i = 0; i < 14; i++) {
    servos[i].attach(servoPins[i]);
    servos[i].write(90); // Center position
  }
  Serial.println("Arduino Servo Controller Ready");
}

void loop() {
  if(Serial.available()) {
    String command = Serial.readStringUntil('\n');
    processCommand(command);
  }
}

void processCommand(String cmd) {
  if(cmd.startsWith("S")) {
    // Set servo: S<id>,<angle>
    int commaIndex = cmd.indexOf(',');
    int servoId = cmd.substring(1, commaIndex).toInt();
    int angle = cmd.substring(commaIndex + 1).toInt();
    
    if(servoId >= 0 && servoId < 14 && angle >= 0 && angle <= 180) {
      servos[servoId].write(angle);
      Serial.println("OK");
    } else {
      Serial.println("ERROR");
    }
  }
  else if(cmd == "P") {
    // Ping
    Serial.println("PONG");
  }
}
```

### 3. Sketch Yükleme
1. Arduino'yu USB ile bağlayın
2. Sketch'i Arduino IDE'de açın
3. Board ve port seçin
4. Upload edin

## Konfigürasyon

### 1. Ayar Dosyası
```bash
cp data/configs/settings_template.json data/configs/settings.json
```

### 2. OpenAI API Key
```json
{
  "ai": {
    "openai_api_key": "your-api-key-here"
  }
}
```

### 3. Arduino Port
macOS'ta:
```json
{
  "servo": {
    "port": "/dev/cu.usbserial-1410"
  }
}
```

Linux'ta:
```json
{
  "servo": {
    "port": "/dev/ttyUSB0"
  }
}
```

## Test ve Doğrulama

### 1. Bileşen Testleri
```bash
# Kamera testi
python -c "from modules.camera.realsense_manager import RealSenseManager; print('Camera OK')"

# YOLO testi
python -c "from modules.ai.yolo_detector import YOLODetector; print('YOLO OK')"

# Arduino testi
python -c "from modules.servo.arduino_comm import ArduinoComm; print('Arduino OK')"
```

### 2. Sistem Testi
```bash
python tests/run_tests.py
```

### 3. Manuel Test
```bash
python main.py --preset calibration
```

## Sorun Giderme

### Kamera Sorunları
```bash
# RealSense bağlantısını test et
rs-enumerate-devices

# Kamera izinlerini kontrol et (Linux)
sudo usermod -a -G video $USER
sudo udevadm control --reload-rules && sudo udevadm trigger
```

### Arduino Sorunları
```bash
# Port izinlerini kontrol et (Linux/macOS)
sudo usermod -a -G dialout $USER  # Linux
sudo dscl . -append /Groups/dialout GroupMembership $USER  # macOS

# Portu test et
ls /dev/tty* | grep -E "(USB|ACM|cu\.)"
```

### Python Sorunları
```bash
# Sanal ortamı yeniden oluştur
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

Bu kurulum tamamlandıktan sonra sistem kullanıma hazır olacaktır.
"""
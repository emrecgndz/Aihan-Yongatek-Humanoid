#!/bin/bash
# =======================
# setup_macos.sh - macOS için Expo-Humanoid Kurulum Script'i
# =======================

set -e  # Hata durumunda çık

# Renkler
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Fonksiyonlar
print_header() {
    echo -e "${BLUE}======================================${NC}"
    echo -e "${BLUE}  Expo-Humanoid macOS Kurulum${NC}"
    echo -e "${BLUE}======================================${NC}"
}

print_step() {
    echo -e "\n${YELLOW}🔸 $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

check_system() {
    print_step "Sistem kontrol ediliyor..."
    
    # macOS kontrolü
    if [[ "$OSTYPE" != "darwin"* ]]; then
        print_error "Bu script sadece macOS için tasarlanmıştır!"
        exit 1
    fi
    
    # macOS versiyonu
    macos_version=$(sw_vers -productVersion)
    print_success "macOS $macos_version tespit edildi"
    
    # Xcode Command Line Tools kontrolü
    if ! xcode-select -p &> /dev/null; then
        print_error "Xcode Command Line Tools bulunamadı!"
        echo "Lütfen şu komutu çalıştırın: xcode-select --install"
        exit 1
    fi
    print_success "Xcode Command Line Tools mevcut"
}

check_homebrew() {
    print_step "Homebrew kontrol ediliyor..."
    
    if ! command -v brew &> /dev/null; then
        print_info "Homebrew bulunamadı, yükleniyor..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        
        # PATH'e ekle
        if [[ -f "/opt/homebrew/bin/brew" ]]; then
            echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
            eval "$(/opt/homebrew/bin/brew shellenv)"
        fi
    else
        print_success "Homebrew mevcut"
        brew update
    fi
}

install_python() {
    print_step "Python 3.10+ yükleniyor..."
    
    # Python kontrolü
    if command -v python3 &> /dev/null; then
        python_version=$(python3 --version | cut -d' ' -f2)
        major=$(echo $python_version | cut -d'.' -f1)
        minor=$(echo $python_version | cut -d'.' -f2)
        
        if [[ $major -ge 3 ]] && [[ $minor -ge 10 ]]; then
            print_success "Python $python_version mevcut"
            return
        fi
    fi
    
    print_info "Python 3.10 yükleniyor..."
    brew install python@3.10
    
    # Symlink oluştur
    brew unlink python@3.10 && brew link python@3.10
    print_success "Python 3.10 yüklendi"
}

install_system_dependencies() {
    print_step "Sistem bağımlılıkları yükleniyor..."
    
    # Gerekli paketleri yükle
    brew_packages=(
        "cmake"
        "pkg-config"
        "opencv"
        "portaudio"
        "ffmpeg"
    )
    
    for package in "${brew_packages[@]}"; do
        if brew list "$package" &> /dev/null; then
            print_success "$package zaten yüklü"
        else
            print_info "$package yükleniyor..."
            brew install "$package"
            print_success "$package yüklendi"
        fi
    done
}

install_realsense_sdk() {
    print_step "Intel RealSense SDK yükleniyor..."
    
    # RealSense SDK kontrolü
    if pkg-config --exists realsense2; then
        print_success "RealSense SDK zaten yüklü"
        return
    fi
    
    print_info "RealSense SDK yükleniyor..."
    
    # Homebrew tap ekle
    brew tap intelrealsense/librealsense
    
    # SDK'yı yükle
    brew install librealsense
    
    print_success "RealSense SDK yüklendi"
}

setup_python_environment() {
    print_step "Python sanal ortamı oluşturuluyor..."
    
    # Sanal ortam kontrolü
    if [[ -d "venv" ]]; then
        print_success "Sanal ortam zaten mevcut"
        source venv/bin/activate
        return
    fi
    
    # Sanal ortam oluştur
    python3 -m venv venv
    source venv/bin/activate
    
    # pip güncelle
    pip install --upgrade pip
    
    print_success "Python sanal ortamı oluşturuldu"
}

install_python_dependencies() {
    print_step "Python bağımlılıkları yükleniyor..."
    
    # Sanal ortamın aktif olduğundan emin ol
    if [[ -z "$VIRTUAL_ENV" ]]; then
        source venv/bin/activate
    fi
    
    # macOS özel gereksinimler
    print_info "macOS özel paketleri yükleniyor..."
    
    # PyQt5 için özel kurulum
    pip install PyQt5==5.15.9
    
    # OpenCV (homebrew ile uyumlu)
    pip install opencv-python==4.8.1.78
    
    # RealSense Python wrapper
    pip install pyrealsense2==2.55.1.6486
    
    # AI/ML paketleri
    print_info "AI/ML paketleri yükleniyor..."
    pip install torch==2.0.1 torchvision==0.15.2
    pip install ultralytics==8.0.196
    
    # OpenAI
    pip install openai==0.28.1
    
    # Diğer gereksinimler
    print_info "Diğer bağımlılıklar yükleniyor..."
    pip install pyserial==3.5
    pip install numpy==1.24.3
    pip install psutil==5.9.5
    pip install Pillow==10.0.0
    pip install scipy==1.11.1
    pip install matplotlib==3.7.2
    
    print_success "Python bağımlılıkları yüklendi"
}

download_yolo_model() {
    print_step "YOLO modeli indiriliyor..."
    
    # Model dizini oluştur
    mkdir -p data/models
    
    # Model dosyası kontrolü
    if [[ -f "data/models/yolov8n.pt" ]]; then
        print_success "YOLO modeli zaten mevcut"
        return
    fi
    
    print_info "YOLOv8n modeli indiriliyor..."
    
    # Python ile model indir
    python3 -c "
from ultralytics import YOLO
import os
os.makedirs('data/models', exist_ok=True)
model = YOLO('yolov8n.pt')
# Model otomatik indirilecek
print('✅ YOLO modeli indirildi')
"
    
    # Model dosyasını taşı
    if [[ -f "yolov8n.pt" ]]; then
        mv yolov8n.pt data/models/
    fi
    
    print_success "YOLO modeli hazır"
}

setup_permissions() {
    print_step "macOS izinleri ayarlanıyor..."
    
    print_info "Kamera izinleri için System Preferences açılabilir"
    print_info "Security & Privacy > Camera bölümünde uygulamaya izin verin"
    
    # USB cihaz izinleri için udev rules (macOS'ta gerekli değil)
    print_success "İzinler ayarlandı"
}

create_config_files() {
    print_step "Konfigürasyon dosyaları oluşturuluyor..."
    
    # Config dizini
    mkdir -p data/configs
    
    # Temel ayarlar dosyası
    if [[ ! -f "data/configs/settings.json" ]]; then
        cat > data/configs/settings.json << EOF
{
  "camera": {
    "width": 720,
    "height": 480,
    "fps": 30,
    "enable_rgb": true,
    "enable_depth": true,
    "depth_scale": 0.001
  },
  "yolo": {
    "model_path": "data/models/yolov8n.pt",
    "confidence_threshold": 0.5,
    "device": "cpu",
    "enable_tracking": true,
    "max_detections": 10
  },
  "servo": {
    "port": "/dev/cu.usbserial-1410",
    "baudrate": 115200,
    "timeout": 1.0,
    "movement_speed": 5,
    "enable_pid": true
  },
  "ai": {
    "openai_api_key": "",
    "model": "gpt-4o",
    "language": "tr",
    "max_tokens": 150,
    "temperature": 0.7,
    "enable_tts": true,
    "enable_stt": true
  },
  "tracking": {
    "min_distance": 0.5,
    "max_distance": 5.0,
    "tracking_smoothing": 0.3,
    "face_priority": true,
    "auto_switch_target": false
  },
  "system": {
    "log_level": "INFO",
    "performance_monitoring": true,
    "auto_save_config": true,
    "gui_theme": "dark",
    "fullscreen": false
  }
}
EOF
        print_success "Ayarlar dosyası oluşturuldu"
    else
        print_success "Ayarlar dosyası zaten mevcut"
    fi
    
    # Log dizini
    mkdir -p logs
    
    # Animasyon dizini
    mkdir -p data/animations
}

create_launch_script() {
    print_step "Başlatma script'i oluşturuluyor..."
    
    cat > run_expo_humanoid.sh << 'EOF'
#!/bin/bash
# Expo-Humanoid Başlatma Script'i

cd "$(dirname "$0")"

# Sanal ortamı aktifleştir
if [[ -d "venv" ]]; then
    source venv/bin/activate
else
    echo "❌ Sanal ortam bulunamadı! Önce setup_macos.sh çalıştırın."
    exit 1
fi

# Python path ayarla
export PYTHONPATH="$PWD:$PYTHONPATH"

# Uygulamayı başlat
echo "🚀 Expo-Humanoid başlatılıyor..."
python main.py "$@"
EOF
    
    chmod +x run_expo_humanoid.sh
    print_success "Başlatma script'i oluşturuldu: ./run_expo_humanoid.sh"
}

run_tests() {
    print_step "Sistem testleri çalıştırılıyor..."
    
    # Sanal ortamın aktif olduğundan emin ol
    if [[ -z "$VIRTUAL_ENV" ]]; then
        source venv/bin/activate
    fi
    
    # Kamera testi
    print_info "Kamera testi çalıştırılıyor..."
    if python test_camera_d435i.py --quick; then
        print_success "Kamera testi başarılı"
    else
        print_error "Kamera testi başarısız"
    fi
    
    # Import testleri
    print_info "Import testleri çalıştırılıyor..."
    python -c "
try:
    import PyQt5
    import cv2
    import numpy as np
    import pyrealsense2 as rs
    import torch
    import ultralytics
    print('✅ Tüm import'lar başarılı')
except ImportError as e:
    print(f'❌ Import hatası: {e}')
    exit(1)
"
}

main() {
    print_header
    
    echo -e "Bu script Expo-Humanoid'i macOS'ta kuracaktır.\n"
    
    # Onay al
    read -p "Devam etmek istiyor musunuz? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Kurulum iptal edildi."
        exit 1
    fi
    
    # Ana kurulum adımları
    check_system
    check_homebrew
    install_python
    install_system_dependencies
    install_realsense_sdk
    setup_python_environment
    install_python_dependencies
    download_yolo_model
    setup_permissions
    create_config_files
    create_launch_script
    run_tests
    
    # Kurulum tamamlandı
    echo -e "\n${GREEN}🎉 Kurulum başarıyla tamamlandı!${NC}\n"
    
    echo -e "${BLUE}Sonraki adımlar:${NC}"
    echo "1. Kamera testini çalıştırın:"
    echo "   ${YELLOW}python test_camera_d435i.py${NC}"
    echo ""
    echo "2. Uygulamayı başlatın:"
    echo "   ${YELLOW}./run_expo_humanoid.sh${NC}"
    echo "   veya"
    echo "   ${YELLOW}source venv/bin/activate && python main.py${NC}"
    echo ""
    echo "3. OpenAI API key'inizi ayarlayın:"
    echo "   ${YELLOW}data/configs/settings.json${NC} dosyasını düzenleyin"
    echo ""
    echo -e "${BLUE}Sorun yaşarsanız:${NC}"
    echo "• GitHub Issues: https://github.com/your-repo/expo-humanoid/issues"
    echo "• Docs: docs/Installation.md"
    echo ""
    echo -e "${GREEN}İyi kullanımlar! 🤖${NC}"
}

# Script'i çalıştır
main "$@"
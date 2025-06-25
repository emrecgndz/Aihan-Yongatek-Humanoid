# =======================
# __init__.py - Proje ana init (root)
# =======================

"""
Expo-Humanoid İnteraktif Robotik Sunum Sistemi

Intel RealSense D435i + YOLOv8 + 14 DOF Servo + OpenAI GPT-4o
macOS Optimized • Production Ready • Fully Functional

Ana Bileşenler:
- Kamera Sistemi: RealSense D435i, Mock, Webcam desteği  
- AI Modülleri: YOLOv8 insan tespiti, OpenAI GPT-4o chat
- Servo Kontrolü: 14 DOF servo motor + animasyon sistemi
- Hedef Takibi: Çoklu kişi takibi ve akıllı hedef seçimi
- Modern GUI: PyQt5 tabanlı gerçek zamanlı kontrol arayüzü
- Sistem İzleme: Performance monitoring ve logging

Kullanım:
    from modules import YOLODetector, ServoController
    from config import Settings
    
    settings = Settings()
    detector = YOLODetector(settings.yolo)
    controller = ServoController(settings.servo)
"""

#__version__ = "1.0.0"
#__title__ = "Expo-Humanoid"
#__description__ = "İnteraktif Robotik Sunum Sistemi"
#__url__ = "https://github.com/your-repo/expo-humanoid"
#__author__ = "Expo-Humanoid Team"
#__license__ = "MIT"

def main():
    """Ana giriş noktası"""
    from main import main as main_app
    return main_app()

if __name__ == "__main__":
    main()
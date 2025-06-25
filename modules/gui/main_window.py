# =======================
# modules/gui/main_window.py - Düzeltilmiş Ana GUI Penceresi
# =======================

import sys
import traceback
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import cv2
import numpy as np

from config.settings import Settings
from modules.system.logger import SystemLogger
from modules.system.monitor import SystemMonitor
from modules.camera.realsense_manager import RealSenseManager
from modules.camera.camera_interface import MockCamera, WebcamCamera
from modules.ai.yolo_detector import YOLODetector
from modules.ai.openai_chat import OpenAIChat
from modules.servo.servo_controller import ServoController
from modules.tracking.target_tracker import TargetTracker

# Widget import'ları
from modules.gui.widgets.camera_widget import CameraWidget, DualCameraWidget
from modules.gui.widgets.status_widget import SystemStatusWidget, DetectionStatusWidget, ServoStatusWidget
from modules.gui.widgets.control_widget import SystemControlWidget, ServoControlWidget, TargetControlWidget


class MainWindow(QMainWindow):
    """Expo-Humanoid ana penceresi - Düzeltilmiş"""
    
    def __init__(self, settings: Settings, logger: SystemLogger):
        super().__init__()
        
        self.settings = settings
        self.logger = logger
        
        # Sistem bileşenleri
        self.system_monitor = SystemMonitor()
        self.camera = None
        self.yolo_detector = None
        self.chat_system = None
        self.servo_controller = None
        self.target_tracker = None
        
        # GUI bileşenleri
        self.central_widget = None
        self.camera_widget = None
        self.system_status_widget = None
        self.detection_status_widget = None
        self.servo_status_widget = None
        self.system_control_widget = None
        self.servo_control_widget = None
        self.target_control_widget = None
        self.log_text = None
        
        # Timer'lar
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_display)
        
        # Durum
        self.is_system_running = False
        self.current_frame = None
        self.detections = []
        self.primary_target = None
        self.camera_type = "none"  # "realsense", "mock", "webcam", "none"
        
        # Hata sayacı
        self.consecutive_errors = 0
        self.max_consecutive_errors = 5
        
        self.setup_ui()
        self.connect_signals()
        self.initialize_system()
    
    def setup_ui(self):
        """Kullanıcı arayüzünü oluştur"""
        self.setWindowTitle("Expo-Humanoid Control Center v1.0")
        self.setGeometry(100, 100, 1600, 1000)
        
        # Ana widget ve layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        main_layout = QHBoxLayout(self.central_widget)
        
        # Sol panel - Kamera ve kontroller
        left_panel = self.create_left_panel()
        main_layout.addWidget(left_panel, 3)
        
        # Sağ panel - Durum ve loglar
        right_panel = self.create_right_panel()
        main_layout.addWidget(right_panel, 2)
        
        # Menü ve durum çubuğu
        self.create_menu_bar()
        self.statusBar().showMessage("Sistem başlatılıyor...")
        
        # Stil uygula
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2b2b2b;
                color: white;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #555;
                border-radius: 5px;
                margin: 5px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QPushButton {
                background-color: #404040;
                border: 1px solid #555;
                padding: 5px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #505050;
            }
            QPushButton:pressed {
                background-color: #606060;
            }
        """)
    
    def create_left_panel(self) -> QWidget:
        """Sol paneli oluştur"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Kamera widget'ı
        camera_group = QGroupBox("Kamera Görüntüsü")
        camera_layout = QVBoxLayout(camera_group)
        
        # Kamera tipi seçimi
        camera_type_layout = QHBoxLayout()
        camera_type_layout.addWidget(QLabel("Kamera Tipi:"))
        
        self.camera_type_combo = QComboBox()
        self.camera_type_combo.addItems(["Auto Detect", "RealSense D435i", "Mock Camera", "Webcam"])
        self.camera_type_combo.currentTextChanged.connect(self.change_camera_type)
        camera_type_layout.addWidget(self.camera_type_combo)
        
        self.camera_reconnect_btn = QPushButton("Yeniden Bağlan")
        self.camera_reconnect_btn.clicked.connect(self.reconnect_camera)
        camera_type_layout.addWidget(self.camera_reconnect_btn)
        
        camera_layout.addLayout(camera_type_layout)
        
        # Kamera widget'ı (tek veya çift)
        self.camera_widget = DualCameraWidget()
        camera_layout.addWidget(self.camera_widget)
        
        layout.addWidget(camera_group)
        
        # Kontrol panelleri
        control_tabs = QTabWidget()
        
        # Sistem kontrolleri
        self.system_control_widget = SystemControlWidget()
        control_tabs.addTab(self.system_control_widget, "Sistem")
        
        # Servo kontrolleri
        self.servo_control_widget = ServoControlWidget()
        control_tabs.addTab(self.servo_control_widget, "Servo")
        
        # Hedef kontrolleri
        self.target_control_widget = TargetControlWidget()
        control_tabs.addTab(self.target_control_widget, "Hedef")
        
        layout.addWidget(control_tabs)
        
        return panel
    
    def create_right_panel(self) -> QWidget:
        """Sağ paneli oluştur"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Durum panelleri
        status_tabs = QTabWidget()
        
        # Sistem durumu
        self.system_status_widget = SystemStatusWidget()
        status_tabs.addTab(self.system_status_widget, "Sistem")
        
        # Tespit durumu
        self.detection_status_widget = DetectionStatusWidget()
        status_tabs.addTab(self.detection_status_widget, "Tespit")
        
        # Servo durumu
        self.servo_status_widget = ServoStatusWidget()
        status_tabs.addTab(self.servo_status_widget, "Servo")
        
        layout.addWidget(status_tabs)
        
        # Log paneli
        log_group = QGroupBox("Sistem Logları")
        log_layout = QVBoxLayout(log_group)
        
        self.log_text = QTextEdit()
        self.log_text.setMaximumHeight(250)
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #ffffff;
                font-family: 'Courier New', monospace;
                font-size: 9pt;
            }
        """
        )
        log_layout.addWidget(self.log_text)
        
        # Log kontrolleri
        log_controls = QHBoxLayout()
        
        clear_log_btn = QPushButton("Temizle")
        clear_log_btn.clicked.connect(self.log_text.clear)
        log_controls.addWidget(clear_log_btn)
        
        save_log_btn = QPushButton("Kaydet")
        save_log_btn.clicked.connect(self.save_logs)
        log_controls.addWidget(save_log_btn)
        
        log_controls.addStretch()
        log_layout.addLayout(log_controls)
        
        layout.addWidget(log_group)
        
        return panel
    
    def create_menu_bar(self):
        """Menü çubuğunu oluştur"""
        menubar = self.menuBar()
        
        # Dosya menüsü
        file_menu = menubar.addMenu('Dosya')
        
        settings_action = QAction('Ayarlar', self)
        settings_action.triggered.connect(self.open_settings)
        file_menu.addAction(settings_action)
        
        file_menu.addSeparator()
        
        export_config_action = QAction('Konfigürasyon Dışa Aktar', self)
        export_config_action.triggered.connect(self.export_config)
        file_menu.addAction(export_config_action)
        
        import_config_action = QAction('Konfigürasyon İçe Aktar', self)
        import_config_action.triggered.connect(self.import_config)
        file_menu.addAction(import_config_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction('Çıkış', self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Araçlar menüsü
        tools_menu = menubar.addMenu('Araçlar')
        
        camera_test_action = QAction('Kamera Testi', self)
        camera_test_action.triggered.connect(self.test_camera)
        tools_menu.addAction(camera_test_action)
        
        servo_calibration_action = QAction('Servo Kalibrasyonu', self)
        servo_calibration_action.triggered.connect(self.calibrate_servos)
        tools_menu.addAction(servo_calibration_action)
        
        # Yardım menüsü
        help_menu = menubar.addMenu('Yardım')
        
        about_action = QAction('Hakkında', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
        help_action = QAction('Yardım', self)
        help_action.triggered.connect(self.show_help)
        help_menu.addAction(help_action)
    
    def connect_signals(self):
        """Widget sinyallerini bağla"""
        # Sistem kontrol sinyalleri
        self.system_control_widget.camera_toggled.connect(self.toggle_camera)
        self.system_control_widget.yolo_toggled.connect(self.toggle_yolo)
        self.system_control_widget.servo_toggled.connect(self.toggle_servo)
        self.system_control_widget.chat_toggled.connect(self.toggle_chat)
        self.system_control_widget.tracking_toggled.connect(self.toggle_tracking)
        self.system_control_widget.preset_applied.connect(self.apply_preset)
        
        # Servo kontrol sinyalleri
        self.servo_control_widget.servo_angle_changed.connect(self.set_servo_angle)
        self.servo_control_widget.speed_changed.connect(self.set_servo_speed)
        self.servo_control_widget.animation_requested.connect(self.play_animation)
        
        # Hedef kontrol sinyalleri
        self.target_control_widget.target_changed.connect(self.change_target)
        self.target_control_widget.interaction_paused.connect(self.pause_interaction)
        self.target_control_widget.targets_cleared.connect(self.clear_targets)
        
        # Kamera widget sinyalleri
        self.camera_widget.rgb_widget.frame_clicked.connect(self.on_frame_clicked)
    
    def initialize_system(self):
        """Sistem bileşenlerini başlat"""
        self.add_log("Sistem başlatılıyor...")
        
        try:
            # Kamerayı başlat
            self.initialize_camera()
            
            # YOLO'yu başlat
            self.initialize_yolo()
            
            # Servo kontrolcüyü başlat
            self.initialize_servo()
            
            # Chat sistemini başlat
            self.initialize_chat()
            
            # Takip sistemini başlat
            self.initialize_tracking()
            
            # Güncelleme timer'ını başlat
            self.update_timer.start(33)  # ~30 FPS
            self.is_system_running = True
            
            self.statusBar().showMessage("Sistem aktif")
            self.add_log("Sistem başarıyla başlatıldı")
            
        except Exception as e:
            self.add_log(f"Sistem başlatma hatası: {e}")
            self.add_log(f"Hata detayı: {traceback.format_exc()}")
            self.statusBar().showMessage("Sistem başlatma hatası")
    
    def initialize_camera(self):
        """Kamerayı başlat"""
        try:
            # Önce RealSense dene
            self.camera = RealSenseManager(self.settings.camera, self.logger)
            if self.camera.initialize():
                self.camera.start_capture()
                self.camera_type = "realsense"
                self.add_log("RealSense D435i başarıyla başlatıldı")
                self.camera_type_combo.setCurrentText("RealSense D435i")
                return
        except Exception as e:
            self.add_log(f"RealSense başlatılamadı: {e}")
        
        # RealSense başarısız olursa Webcam dene
        try:
            self.camera = WebcamCamera(0, self.settings.camera.width, self.settings.camera.height)
            if self.camera.initialize():
                self.camera.start_capture()
                self.camera_type = "webcam"
                self.add_log("Sistem kamerası başlatıldı")
                self.camera_type_combo.setCurrentText("Webcam")
                return
        except Exception as e:
            self.add_log(f"Webcam başlatılamadı: {e}")
        
        # Her şey başarısız olursa Mock kullan
        self.camera = MockCamera(self.settings.camera.width, self.settings.camera.height)
        self.camera.initialize()
        self.camera.start_capture()
        self.camera_type = "mock"
        self.add_log("Mock kamera başlatıldı (test modu)")
        self.camera_type_combo.setCurrentText("Mock Camera")
    
    def initialize_yolo(self):
        """YOLO detektörünü başlat"""
        try:
            self.yolo_detector = YOLODetector(self.settings.yolo, self.logger)
            if self.yolo_detector.initialize():
                self.add_log("YOLO detektörü başlatıldı")
            else:
                self.add_log("YOLO detektörü başlatılamadı - Mock mode")
                self.yolo_detector = None
        except Exception as e:
            self.add_log(f"YOLO başlatma hatası: {e}")
            self.yolo_detector = None
    
    def initialize_servo(self):
        """Servo kontrolcüyü başlat"""
        try:
            self.servo_controller = ServoController(self.settings.servo, self.logger)
            if self.servo_controller.initialize():
                self.add_log("Servo kontrolcüsü başlatıldı")
            else:
                self.add_log("Servo kontrolcüsü başlatılamadı - Mock mode")
                # Mock servo controller oluşturabilirsiniz
        except Exception as e:
            self.add_log(f"Servo başlatma hatası: {e}")
            self.servo_controller = None
    
    def initialize_chat(self):
        """Chat sistemini başlat"""
        try:
            self.chat_system = OpenAIChat(self.settings.ai, self.logger)
            if self.chat_system.initialize():
                self.add_log("AI Chat sistemi başlatıldı")
            else:
                self.add_log("AI Chat sistemi başlatılamadı")
                self.chat_system = None
        except Exception as e:
            self.add_log(f"Chat başlatma hatası: {e}")
            self.chat_system = None
    
    def initialize_tracking(self):
        """Takip sistemini başlat"""
        try:
            self.target_tracker = TargetTracker(self.settings.tracking, self.logger)
            self.add_log("Hedef takip sistemi başlatıldı")
        except Exception as e:
            self.add_log(f"Takip başlatma hatası: {e}")
            self.target_tracker = None
    
    def change_camera_type(self, camera_type_text: str):
        """Kamera tipini değiştir"""
        if not self.is_system_running:
            return
            
        self.add_log(f"Kamera tipi değiştiriliyor: {camera_type_text}")
        
        # Mevcut kamerayı kapat
        if self.camera:
            self.camera.cleanup()
            self.camera = None
        
        # Yeni kamerayı başlat
        try:
            if camera_type_text == "RealSense D435i":
                self.camera = RealSenseManager(self.settings.camera, self.logger)
                self.camera_type = "realsense"
            elif camera_type_text == "Mock Camera":
                self.camera = MockCamera(self.settings.camera.width, self.settings.camera.height)
                self.camera_type = "mock"
            elif camera_type_text == "Webcam":
                self.camera = WebcamCamera(0, self.settings.camera.width, self.settings.camera.height)
                self.camera_type = "webcam"
            else:  # Auto Detect
                self.initialize_camera()
                return
            
            if self.camera.initialize():
                self.camera.start_capture()
                self.add_log(f"{camera_type_text} başarıyla başlatıldı")
            else:
                self.add_log(f"{camera_type_text} başlatılamadı")
                
        except Exception as e:
            self.add_log(f"Kamera değiştirme hatası: {e}")
    
    def reconnect_camera(self):
        """Kamerayı yeniden bağla"""
        current_type = self.camera_type_combo.currentText()
        self.change_camera_type(current_type)
    
    def update_display(self):
        """Ekranı güncelle"""
        if not self.is_system_running:
            return
        
        try:
            # Kamera frame'lerini al
            rgb_frame = None
            depth_frame = None
            
            if self.camera and self.system_control_widget.camera_cb.isChecked():
                if self.camera_type == "realsense":
                    rgb_frame, depth_frame, _ = self.camera.get_frames()
                else:
                    rgb_frame = self.camera.get_rgb_frame()
                    depth_frame = self.camera.get_depth_frame()
                
                if rgb_frame is not None:
                    self.current_frame = rgb_frame.copy()
                    
                    # YOLO tespiti
                    if (self.yolo_detector and 
                        self.system_control_widget.yolo_cb.isChecked()):
                        try:
                            self.detections = self.yolo_detector.detect_people(rgb_frame)
                            
                            # Takip güncelle
                            if (self.target_tracker and 
                                self.system_control_widget.tracking_cb.isChecked()):
                                self.primary_target = self.target_tracker.update_targets(
                                    self.detections, depth_frame
                                )
                                
                                # Servo kontrolü
                                if (self.servo_controller and 
                                    self.system_control_widget.servo_cb.isChecked() and 
                                    self.primary_target):
                                    self.servo_controller.point_to_position(
                                        self.primary_target.detection.center_x,
                                        self.primary_target.detection.center_y,
                                        rgb_frame.shape[1],
                                        rgb_frame.shape[0]
                                    )
                        except Exception as e:
                            self.add_log(f"YOLO/Tracking hatası: {e}")
                            self.detections = []
                    
                    # Frame'leri widget'ta göster
                    self.camera_widget.display_frames(rgb_frame, depth_frame, self.detections)
                else:
                    self.camera_widget.rgb_widget.set_no_camera_message("Frame alınamıyor")
            else:
                self.camera_widget.rgb_widget.set_no_camera_message("Kamera kapalı")
            
            # Durum widget'larını güncelle
            self.update_status_widgets()
            
            # Hata sayacını sıfırla
            self.consecutive_errors = 0
            
        except Exception as e:
            self.consecutive_errors += 1
            if self.consecutive_errors <= 3:  # İlk birkaç hatayı logla
                self.add_log(f"Display güncelleme hatası: {e}")
            
            if self.consecutive_errors >= self.max_consecutive_errors:
                self.add_log("Çok fazla hata! Timer durduruluyor.")
                self.update_timer.stop()
    
    def update_status_widgets(self):
        """Durum widget'larını güncelle"""
        try:
            # Sistem durumu
            system_status = self.system_monitor.get_system_status()
            status_dict = {
                'cpu_usage': system_status.cpu_usage,
                'gpu_usage': system_status.gpu_usage,
                'memory_usage': system_status.memory_usage,
                'temperature': system_status.temperature,
                'fps': self.camera.get_fps() if self.camera else 0
            }
            self.system_status_widget.update_status(status_dict)
            
            # Tespit durumu
            inference_time = 0
            if self.yolo_detector:
                inference_time = self.yolo_detector.get_inference_time()
            
            self.detection_status_widget.update_detections(
                self.detections, 
                self.primary_target, 
                inference_time
            )
            
            # Servo durumu
            if self.servo_controller:
                self.servo_status_widget.update_servo_status(
                    self.servo_controller.is_arduino_connected(),
                    self.servo_controller.get_current_positions(),
                    False  # is_moving - bunu servo controller'dan alabilirsiniz
                )
            
        except Exception as e:
            self.add_log(f"Status widget güncelleme hatası: {e}")
    
    def add_log(self, message: str):
        """Log mesajı ekle"""
        timestamp = QTime.currentTime().toString("hh:mm:ss")
        log_message = f"[{timestamp}] {message}"
        
        # GUI log'a ekle
        self.log_text.append(log_message)
        
        # System logger'a da gönder
        self.logger.info(message)
        
        # Scroll to bottom
        scrollbar = self.log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
        
        # Çok fazla log satırı varsa eski olanları sil
        if self.log_text.document().lineCount() > 1000:
            cursor = self.log_text.textCursor()
            cursor.movePosition(cursor.Start)
            cursor.select(cursor.LineUnderCursor)
            cursor.removeSelectedText()
    
    # Kontrol metotları
    def toggle_camera(self, enabled):
        self.add_log(f"Kamera {'aktif' if enabled else 'pasif'}")
    
    def toggle_yolo(self, enabled):
        self.add_log(f"YOLO tespiti {'aktif' if enabled else 'pasif'}")
        if not enabled:
            self.detections = []
    
    def toggle_servo(self, enabled):
        self.add_log(f"Servo kontrol {'aktif' if enabled else 'pasif'}")
    
    def toggle_chat(self, enabled):
        self.add_log(f"AI Chat {'aktif' if enabled else 'pasif'}")
    
    def toggle_tracking(self, enabled):
        if not enabled and self.target_tracker:
            self.target_tracker.clear_targets()
            self.primary_target = None
        self.add_log(f"Otomatik takip {'aktif' if enabled else 'pasif'}")
    
    def apply_preset(self, preset_name):
        """Preset ayarlarını uygula"""
        self.system_control_widget.apply_preset(preset_name)
        self.add_log(f"{preset_name.title()} modu uygulandı")
    
    def set_servo_angle(self, servo_id, angle):
        """Servo açısını ayarla"""
        if self.servo_controller:
            success = self.servo_controller.set_servo_angle(servo_id, angle)
            if success:
                self.add_log(f"Servo {servo_id}: {angle}°")
    
    def set_servo_speed(self, speed):
        """Servo hızını ayarla"""
        if self.servo_controller:
            self.servo_controller.set_movement_speed(speed)
            self.add_log(f"Servo hızı: {speed}")
    
    def play_animation(self, animation_name):
        """Animasyon oynat"""
        # TODO: Animation engine entegrasyonu
        self.add_log(f"Animasyon oynatılıyor: {animation_name}")
    
    def change_target(self):
        """Hedefi değiştir"""
        self.add_log("Hedef değiştirildi")
    
    def pause_interaction(self):
        """Etkileşimi duraklat"""
        self.add_log("Etkileşim duraklatıldı")
    
    def clear_targets(self):
        """Hedefleri temizle"""
        if self.target_tracker:
            self.target_tracker.clear_targets()
        self.primary_target = None
        self.add_log("Hedefler temizlendi")
    
    def on_frame_clicked(self, x, y):
        """Frame tıklama olayı"""
        if self.current_frame is not None:
            self.add_log(f"Frame tıklandı: ({x}, {y})")
            # TODO: Tıklanan noktaya servo yönlendirmesi
    
    # Menü fonksiyonları
    def open_settings(self):
        """Ayarlar penceresini aç"""
        self.add_log("Ayarlar penceresi açılacak (TODO)")
    
    def export_config(self):
        """Konfigürasyonu dışa aktar"""
        filename, _ = QFileDialog.getSaveFileName(
            self, "Konfigürasyon Kaydet", "", "JSON Files (*.json)"
        )
        if filename:
            self.settings.save_settings()
            self.add_log(f"Konfigürasyon kaydedildi: {filename}")
    
    def import_config(self):
        """Konfigürasyonu içe aktar"""
        filename, _ = QFileDialog.getOpenFileName(
            self, "Konfigürasyon Yükle", "", "JSON Files (*.json)"
        )
        if filename:
            # TODO: Konfigürasyon yükleme
            self.add_log(f"Konfigürasyon yüklendi: {filename}")
    
    def test_camera(self):
        """Kamera testi"""
        if self.camera:
            info = self.camera.get_camera_info()
            self.add_log(f"Kamera testi: {info}")
        else:
            self.add_log("Kamera bağlı değil")
    
    def calibrate_servos(self):
        """Servo kalibrasyonu"""
        if self.servo_controller:
            self.servo_controller.calibrate_all_servos()
            self.add_log("Servo kalibrasyonu tamamlandı")
        else:
            self.add_log("Servo kontrolcü bağlı değil")
    
    def save_logs(self):
        """Logları dosyaya kaydet"""
        filename, _ = QFileDialog.getSaveFileName(
            self, "Log Kaydet", "", "Text Files (*.txt)"
        )
        if filename:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(self.log_text.toPlainText())
            self.add_log(f"Loglar kaydedildi: {filename}")
    
    def show_about(self):
        """Hakkında penceresi"""
        QMessageBox.about(self, "Hakkında", 
                         """Expo-Humanoid v1.0
                         
İnteraktif Robotik Sunum Sistemi

• Intel RealSense D435i Derinlik Kamerası
• YOLOv8-People İnsan Tespiti  
• 14 DOF Servo Motor Kontrolü
• OpenAI GPT-4o Chat Entegrasyonu
• PyQt5 Modern GUI

macOS Optimized""")
    
    def show_help(self):
        """Yardım penceresi"""
        help_text = """Expo-Humanoid Kullanım Kılavuzu

BAŞLATMA:
1. Kamera tipini seçin (Auto Detect önerilir)
2. Sistem kontrolleri ile modülleri etkinleştirin
3. Demo modu için "Demo Modu" butonuna tıklayın

KAMERA:
• RealSense D435i: En iyi performans
• Mock Camera: Test modu  
• Webcam: Fallback seçeneği

KONTROLLER:
• Sistem sekmesi: Ana kontroller
• Servo sekmesi: Manuel servo kontrolü
• Hedef sekmesi: Takip ayarları

SORUN GİDERME:
• Kamera açılmıyorsa USB bağlantısını kontrol edin
• YOLO çalışmıyorsa model dosyasını kontrol edin
• Servo çalışmıyorsa Arduino bağlantısını kontrol edin"""
        
        msg_box = QMessageBox()
        msg_box.setWindowTitle("Yardım")
        msg_box.setText(help_text)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec_()
    
    def cleanup(self):
        """Kaynakları temizle"""
        self.add_log("Sistem kapatılıyor...")
        self.is_system_running = False
        self.update_timer.stop()
        
        if self.camera:
            self.camera.cleanup()
        
        if self.servo_controller:
            self.servo_controller.cleanup()
        
        self.add_log("Sistem kapatıldı")
    
    def closeEvent(self, event):
        """Pencere kapatılırken temizlik yap"""
        reply = QMessageBox.question(
            self, 'Çıkış', 'Uygulamayı kapatmak istediğinize emin misiniz?',
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.cleanup()
            event.accept()
        else:
            event.ignore()
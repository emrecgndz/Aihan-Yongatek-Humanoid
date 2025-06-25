# =======================
# modules/gui/main_window.py - Ana GUI Penceresi
# =======================

import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import cv2
import numpy as np

from config.settings import Settings
from modules.system.logger import SystemLogger
from modules.system.monitor import SystemMonitor
from modules.camera.realsense_manager import RealSenseManager
from modules.ai.yolo_detector import YOLODetector
from modules.ai.openai_chat import OpenAIChat
from modules.servo.servo_controller import ServoController
from modules.tracking.target_tracker import TargetTracker


class MainWindow(QMainWindow):
    """Expo-Humanoid ana penceresi"""
    
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
        self.camera_label = None
        self.control_panel = None
        self.status_panel = None
        self.log_panel = None
        
        # Timer'lar
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_display)
        
        # Durum
        self.is_system_running = False
        self.current_frame = None
        self.detections = []
        
        self.setup_ui()
        self.initialize_system()
    
    def setup_ui(self):
        """Kullanıcı arayüzünü oluştur"""
        self.setWindowTitle("Expo-Humanoid Control Center")
        self.setGeometry(100, 100, 1400, 900)
        
        # Merkezi widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Ana layout
        main_layout = QHBoxLayout(self.central_widget)
        
        # Sol panel - Kamera ve kontroller
        left_panel = self.create_left_panel()
        main_layout.addWidget(left_panel, 2)
        
        # Sağ panel - Durum ve loglar
        right_panel = self.create_right_panel()
        main_layout.addWidget(right_panel, 1)
        
        # Menü çubuğu
        self.create_menu_bar()
        
        # Durum çubuğu
        self.statusBar().showMessage("Sistem başlatılıyor...")
    
    def create_left_panel(self) -> QWidget:
        """Sol paneli oluştur"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Kamera görüntüsü
        camera_group = QGroupBox("Kamera Görüntüsü")
        camera_layout = QVBoxLayout(camera_group)
        
        self.camera_label = QLabel("Kamera bağlanıyor...")
        self.camera_label.setMinimumSize(640, 480)
        self.camera_label.setStyleSheet("border: 1px solid gray; background-color: black;")
        self.camera_label.setAlignment(Qt.AlignCenter)
        camera_layout.addWidget(self.camera_label)
        
        layout.addWidget(camera_group)
        
        # Kontrol paneli
        self.control_panel = self.create_control_panel()
        layout.addWidget(self.control_panel)
        
        return panel
    
    def create_control_panel(self) -> QWidget:
        """Kontrol panelini oluştur"""
        panel = QGroupBox("Sistem Kontrolleri")
        layout = QGridLayout(panel)
        
        # Ana sistem kontrolleri
        row = 0
        
        # Kamera kontrolü
        self.camera_enable_cb = QCheckBox("Kamera Aktif")
        self.camera_enable_cb.setChecked(True)
        self.camera_enable_cb.toggled.connect(self.toggle_camera)
        layout.addWidget(self.camera_enable_cb, row, 0)
        
        # YOLO kontrolü
        self.yolo_enable_cb = QCheckBox("YOLO Tespiti")
        self.yolo_enable_cb.setChecked(True)
        self.yolo_enable_cb.toggled.connect(self.toggle_yolo)
        layout.addWidget(self.yolo_enable_cb, row, 1)
        
        row += 1
        
        # Servo kontrolü
        self.servo_enable_cb = QCheckBox("Servo Aktif")
        self.servo_enable_cb.setChecked(True)
        self.servo_enable_cb.toggled.connect(self.toggle_servo)
        layout.addWidget(self.servo_enable_cb, row, 0)
        
        # Chat kontrolü
        self.chat_enable_cb = QCheckBox("AI Chat")
        self.chat_enable_cb.setChecked(True)
        self.chat_enable_cb.toggled.connect(self.toggle_chat)
        layout.addWidget(self.chat_enable_cb, row, 1)
        
        row += 1
        
        # Takip kontrolü
        self.tracking_enable_cb = QCheckBox("Otomatik Takip")
        self.tracking_enable_cb.setChecked(False)
        self.tracking_enable_cb.toggled.connect(self.toggle_tracking)
        layout.addWidget(self.tracking_enable_cb, row, 0, 1, 2)
        
        row += 1
        
        # Hedef değiştirme
        self.change_target_btn = QPushButton("Hedef Değiştir")
        self.change_target_btn.clicked.connect(self.change_target)
        layout.addWidget(self.change_target_btn, row, 0)
        
        # Etkileşim duraklat
        self.pause_interaction_btn = QPushButton("Etkileşim Duraklat")
        self.pause_interaction_btn.clicked.connect(self.pause_interaction)
        layout.addWidget(self.pause_interaction_btn, row, 1)
        
        row += 1
        
        # Hız kontrolü
        layout.addWidget(QLabel("Servo Hızı:"), row, 0)
        self.speed_slider = QSlider(Qt.Horizontal)
        self.speed_slider.setRange(1, 10)
        self.speed_slider.setValue(5)
        self.speed_slider.valueChanged.connect(self.change_servo_speed)
        layout.addWidget(self.speed_slider, row, 1)
        
        row += 1
        
        # Quick Presets
        presets_group = QGroupBox("Hızlı Ayarlar")
        presets_layout = QHBoxLayout(presets_group)
        
        demo_btn = QPushButton("Demo Modu")
        demo_btn.clicked.connect(lambda: self.apply_preset("demo"))
        presets_layout.addWidget(demo_btn)
        
        manual_btn = QPushButton("Manuel Modu")
        manual_btn.clicked.connect(lambda: self.apply_preset("manual"))
        presets_layout.addWidget(manual_btn)
        
        calibration_btn = QPushButton("Kalibrasyon")
        calibration_btn.clicked.connect(lambda: self.apply_preset("calibration"))
        presets_layout.addWidget(calibration_btn)
        
        layout.addWidget(presets_group, row, 0, 1, 2)
        
        return panel
    
    def create_right_panel(self) -> QWidget:
        """Sağ paneli oluştur"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Durum paneli
        self.status_panel = self.create_status_panel()
        layout.addWidget(self.status_panel)
        
        # Log paneli
        self.log_panel = self.create_log_panel()
        layout.addWidget(self.log_panel)
        
        return panel
    
    def create_status_panel(self) -> QWidget:
        """Durum panelini oluştur"""
        panel = QGroupBox("Sistem Durumu")
        layout = QGridLayout(panel)
        
        # Sistem bilgileri
        self.cpu_label = QLabel("CPU: 0%")
        self.gpu_label = QLabel("GPU: 0%")
        self.memory_label = QLabel("RAM: 0%")
        self.temp_label = QLabel("Sıcaklık: 0°C")
        self.fps_label = QLabel("FPS: 0")
        
        layout.addWidget(self.cpu_label, 0, 0)
        layout.addWidget(self.gpu_label, 0, 1)
        layout.addWidget(self.memory_label, 1, 0)
        layout.addWidget(self.temp_label, 1, 1)
        layout.addWidget(self.fps_label, 2, 0)
        
        # Tespit bilgileri
        self.detection_count_label = QLabel("Tespit: 0 kişi")
        self.target_distance_label = QLabel("Hedef Mesafe: -")
        
        layout.addWidget(self.detection_count_label, 3, 0)
        layout.addWidget(self.target_distance_label, 3, 1)
        
        return panel
    
    def create_log_panel(self) -> QWidget:
        """Log panelini oluştur"""
        panel = QGroupBox("Sistem Logları")
        layout = QVBoxLayout(panel)
        
        self.log_text = QTextEdit()
        self.log_text.setMaximumHeight(300)
        self.log_text.setReadOnly(True)
        layout.addWidget(self.log_text)
        
        # Log temizleme
        clear_btn = QPushButton("Logları Temizle")
        clear_btn.clicked.connect(self.log_text.clear)
        layout.addWidget(clear_btn)
        
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
        
        exit_action = QAction('Çıkış', self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Yardım menüsü
        help_menu = menubar.addMenu('Yardım')
        
        about_action = QAction('Hakkında', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def initialize_system(self):
        """Sistem bileşenlerini başlat"""
        try:
            # Kamerayı başlat
            self.camera = RealSenseManager(self.settings.camera, self.logger)
            if self.camera.initialize():
                self.camera.start_capture()
                self.add_log("Kamera başarıyla başlatıldı")
            else:
                self.add_log("Kamera başlatılamadı")
            
            # YOLO'yu başlat
            self.yolo_detector = YOLODetector(self.settings.yolo, self.logger)
            if self.yolo_detector.initialize():
                self.add_log("YOLO detektörü başlatıldı")
            else:
                self.add_log("YOLO detektörü başlatılamadı")
            
            # Servo kontrolcüyü başlat
            self.servo_controller = ServoController(self.settings.servo, self.logger)
            if self.servo_controller.initialize():
                self.add_log("Servo kontrolcüsü başlatıldı")
            else:
                self.add_log("Servo kontrolcüsü başlatılamadı")
            
            # Chat sistemini başlat
            self.chat_system = OpenAIChat(self.settings.ai, self.logger)
            if self.chat_system.initialize():
                self.add_log("AI Chat sistemi başlatıldı")
            else:
                self.add_log("AI Chat sistemi başlatılamadı")
            
            # Takip sistemini başlat
            self.target_tracker = TargetTracker(self.settings.tracking, self.logger)
            self.add_log("Hedef takip sistemi başlatıldı")
            
            # Güncelleme timer'ını başlat
            self.update_timer.start(33)  # ~30 FPS
            self.is_system_running = True
            
            self.statusBar().showMessage("Sistem aktif")
            
        except Exception as e:
            self.add_log(f"Sistem başlatma hatası: {e}")
            self.statusBar().showMessage("Sistem başlatma hatası")
    
    def update_display(self):
        """Ekranı güncelle"""
        if not self.is_system_running:
            return
        
        try:
            # Kamera frame'ini al
            if self.camera and self.camera_enable_cb.isChecked():
                rgb_frame = self.camera.get_rgb_frame()
                if rgb_frame is not None:
                    self.current_frame = rgb_frame.copy()
                    
                    # YOLO tespiti
                    if self.yolo_detector and self.yolo_enable_cb.isChecked():
                        self.detections = self.yolo_detector.detect_people(rgb_frame)
                        
                        # Takip güncelle
                        if self.target_tracker and self.tracking_enable_cb.isChecked():
                            depth_frame = self.camera.get_depth_frame()
                            primary_target = self.target_tracker.update_targets(self.detections, depth_frame)
                            
                            # Servo kontrolü
                            if self.servo_controller and self.servo_enable_cb.isChecked() and primary_target:
                                self.servo_controller.point_to_position(
                                    primary_target.detection.center_x,
                                    primary_target.detection.center_y,
                                    rgb_frame.shape[1],
                                    rgb_frame.shape[0]
                                )
                        
                        # Tespitleri çiz
                        rgb_frame = self.yolo_detector.draw_detections(rgb_frame, self.detections)
                    
                    # Frame'i GUI'de göster
                    self.display_frame(rgb_frame)
            
            # Sistem durumunu güncelle
            self.update_system_status()
            
        except Exception as e:
            self.add_log(f"Güncelleme hatası: {e}")
    
    def display_frame(self, frame):
        """Frame'i label'da göster"""
        try:
            height, width, channel = frame.shape
            bytes_per_line = 3 * width
            
            # OpenCV BGR'den RGB'ye çevir
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # QImage oluştur
            qt_image = QImage(rgb_frame.data, width, height, bytes_per_line, QImage.Format_RGB888)
            
            # QPixmap'e çevir ve göster
            pixmap = QPixmap.fromImage(qt_image)
            scaled_pixmap = pixmap.scaled(self.camera_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.camera_label.setPixmap(scaled_pixmap)
            
        except Exception as e:
            self.add_log(f"Frame gösterme hatası: {e}")
    
    def update_system_status(self):
        """Sistem durum bilgilerini güncelle"""
        status = self.system_monitor.get_system_status()
        
        self.cpu_label.setText(f"CPU: {status.cpu_usage:.1f}%")
        self.gpu_label.setText(f"GPU: {status.gpu_usage:.1f}%")
        self.memory_label.setText(f"RAM: {status.memory_usage:.1f}%")
        self.temp_label.setText(f"Sıcaklık: {status.temperature:.1f}°C")
        
        if self.camera:
            self.fps_label.setText(f"FPS: {self.camera.get_fps()}")
        
        self.detection_count_label.setText(f"Tespit: {len(self.detections)} kişi")
        
        if self.target_tracker and self.target_tracker.get_primary_target():
            distance = self.target_tracker.get_primary_target().distance
            self.target_distance_label.setText(f"Hedef Mesafe: {distance:.2f}m")
        else:
            self.target_distance_label.setText("Hedef Mesafe: -")
    
    def add_log(self, message: str):
        """Log mesajı ekle"""
        timestamp = QTime.currentTime().toString()
        log_message = f"[{timestamp}] {message}"
        self.log_text.append(log_message)
        
        # Scroll to bottom
        scrollbar = self.log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    # Kontrol metotları
    def toggle_camera(self, enabled):
        if enabled and self.camera:
            self.camera.start_capture()
        elif self.camera:
            self.camera.stop_capture()
        self.add_log(f"Kamera {'aktif' if enabled else 'pasif'}")
    
    def toggle_yolo(self, enabled):
        self.add_log(f"YOLO tespiti {'aktif' if enabled else 'pasif'}")
    
    def toggle_servo(self, enabled):
        self.add_log(f"Servo kontrol {'aktif' if enabled else 'pasif'}")
    
    def toggle_chat(self, enabled):
        self.add_log(f"AI Chat {'aktif' if enabled else 'pasif'}")
    
    def toggle_tracking(self, enabled):
        if not enabled and self.target_tracker:
            self.target_tracker.clear_targets()
        self.add_log(f"Otomatik takip {'aktif' if enabled else 'pasif'}")
    
    def change_target(self):
        # Sonraki hedefi seç
        self.add_log("Hedef değiştirildi")
    
    def pause_interaction(self):
        self.add_log("Etkileşim duraklatıldı")
    
    def change_servo_speed(self, value):
        if self.servo_controller:
            self.servo_controller.set_movement_speed(value)
        self.add_log(f"Servo hızı: {value}")
    
    def apply_preset(self, preset_name):
        """Hızlı ayar profili uygula"""
        if preset_name == "demo":
            self.camera_enable_cb.setChecked(True)
            self.yolo_enable_cb.setChecked(True)
            self.servo_enable_cb.setChecked(True)
            self.chat_enable_cb.setChecked(True)
            self.tracking_enable_cb.setChecked(True)
        elif preset_name == "manual":
            self.tracking_enable_cb.setChecked(False)
            self.servo_enable_cb.setChecked(False)
        elif preset_name == "calibration":
            self.camera_enable_cb.setChecked(True)
            self.yolo_enable_cb.setChecked(False)
            self.servo_enable_cb.setChecked(True)
            self.chat_enable_cb.setChecked(False)
            self.tracking_enable_cb.setChecked(False)
        
        self.add_log(f"{preset_name.title()} modu uygulandı")
    
    def open_settings(self):
        self.add_log("Ayarlar penceresi açılacak") # Placeholder
    
    def show_about(self):
        QMessageBox.about(self, "Hakkında", 
                         "Expo-Humanoid v1.0\nInteraktif Robotik Sunum Sistemi")
    
    def cleanup(self):
        """Kaynakları temizle"""
        self.is_system_running = False
        self.update_timer.stop()
        
        if self.camera:
            self.camera.cleanup()
        
        if self.servo_controller:
            self.servo_controller.cleanup()
    
    def closeEvent(self, event):
        """Pencere kapatılırken temizlik yap"""
        self.cleanup()
        event.accept()


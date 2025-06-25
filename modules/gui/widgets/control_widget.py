# =======================
# modules/gui/widgets/control_widget.py - Kontrol Widget'ları
# =======================

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from typing import Dict, Any


class SystemControlWidget(QGroupBox):
    """Sistem kontrol widget'ı"""
    
    # Sinyal tanımları
    camera_toggled = pyqtSignal(bool)
    yolo_toggled = pyqtSignal(bool)
    servo_toggled = pyqtSignal(bool)
    chat_toggled = pyqtSignal(bool)
    tracking_toggled = pyqtSignal(bool)
    preset_applied = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__("Sistem Kontrolleri", parent)
        
        self.setup_ui()
        
    def setup_ui(self):
        layout = QGridLayout(self)
        
        # Ana kontroller
        self.camera_cb = QCheckBox("Kamera Aktif")
        self.camera_cb.setChecked(True)
        self.camera_cb.toggled.connect(self.camera_toggled.emit)
        layout.addWidget(self.camera_cb, 0, 0)
        
        self.yolo_cb = QCheckBox("YOLO Tespiti")
        self.yolo_cb.setChecked(True)
        self.yolo_cb.toggled.connect(self.yolo_toggled.emit)
        layout.addWidget(self.yolo_cb, 0, 1)
        
        self.servo_cb = QCheckBox("Servo Aktif")
        self.servo_cb.setChecked(True)
        self.servo_cb.toggled.connect(self.servo_toggled.emit)
        layout.addWidget(self.servo_cb, 1, 0)
        
        self.chat_cb = QCheckBox("AI Chat")
        self.chat_cb.setChecked(True)
        self.chat_cb.toggled.connect(self.chat_toggled.emit)
        layout.addWidget(self.chat_cb, 1, 1)
        
        self.tracking_cb = QCheckBox("Otomatik Takip")
        self.tracking_cb.setChecked(False)
        self.tracking_cb.toggled.connect(self.tracking_toggled.emit)
        layout.addWidget(self.tracking_cb, 2, 0, 1, 2)
        
        # Preset butonları
        preset_group = QGroupBox("Hızlı Ayarlar")
        preset_layout = QHBoxLayout(preset_group)
        
        demo_btn = QPushButton("Demo Modu")
        demo_btn.clicked.connect(lambda: self.preset_applied.emit("demo"))
        preset_layout.addWidget(demo_btn)
        
        manual_btn = QPushButton("Manuel Modu")
        manual_btn.clicked.connect(lambda: self.preset_applied.emit("manual"))
        preset_layout.addWidget(manual_btn)
        
        calibration_btn = QPushButton("Kalibrasyon")
        calibration_btn.clicked.connect(lambda: self.preset_applied.emit("calibration"))
        preset_layout.addWidget(calibration_btn)
        
        layout.addWidget(preset_group, 3, 0, 1, 2)
        
    def apply_preset(self, preset_name: str):
        """Preset ayarlarını uygula"""
        if preset_name == "demo":
            self.camera_cb.setChecked(True)
            self.yolo_cb.setChecked(True)
            self.servo_cb.setChecked(True)
            self.chat_cb.setChecked(True)
            self.tracking_cb.setChecked(True)
        elif preset_name == "manual":
            self.tracking_cb.setChecked(False)
            self.servo_cb.setChecked(False)
        elif preset_name == "calibration":
            self.camera_cb.setChecked(True)
            self.yolo_cb.setChecked(False)
            self.servo_cb.setChecked(True)
            self.chat_cb.setChecked(False)
            self.tracking_cb.setChecked(False)


class ServoControlWidget(QGroupBox):
    """Servo kontrol widget'ı"""
    
    # Sinyal tanımları
    servo_angle_changed = pyqtSignal(int, int)  # servo_id, angle
    speed_changed = pyqtSignal(int)
    animation_requested = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__("Servo Kontrolü", parent)
        
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Hız kontrolü
        speed_group = QGroupBox("Hareket Hızı")
        speed_layout = QHBoxLayout(speed_group)
        
        speed_layout.addWidget(QLabel("Yavaş"))
        self.speed_slider = QSlider(Qt.Horizontal)
        self.speed_slider.setRange(1, 10)
        self.speed_slider.setValue(5)
        self.speed_slider.valueChanged.connect(self.speed_changed.emit)
        speed_layout.addWidget(self.speed_slider)
        speed_layout.addWidget(QLabel("Hızlı"))
        
        self.speed_value_label = QLabel("5")
        self.speed_slider.valueChanged.connect(lambda v: self.speed_value_label.setText(str(v)))
        speed_layout.addWidget(self.speed_value_label)
        
        layout.addWidget(speed_group)
        
        # Kafa kontrolü
        head_group = QGroupBox("Kafa Kontrolü")
        head_layout = QGridLayout(head_group)
        
        # Pan kontrolü
        head_layout.addWidget(QLabel("Pan (Yatay):"), 0, 0)
        self.head_pan_slider = QSlider(Qt.Horizontal)
        self.head_pan_slider.setRange(30, 150)
        self.head_pan_slider.setValue(90)
        self.head_pan_slider.valueChanged.connect(lambda v: self.servo_angle_changed.emit(12, v))
        head_layout.addWidget(self.head_pan_slider, 0, 1)
        
        self.head_pan_label = QLabel("90°")
        self.head_pan_slider.valueChanged.connect(lambda v: self.head_pan_label.setText(f"{v}°"))
        head_layout.addWidget(self.head_pan_label, 0, 2)
        
        # Tilt kontrolü
        head_layout.addWidget(QLabel("Tilt (Dikey):"), 1, 0)
        self.head_tilt_slider = QSlider(Qt.Horizontal)
        self.head_tilt_slider.setRange(60, 120)
        self.head_tilt_slider.setValue(90)
        self.head_tilt_slider.valueChanged.connect(lambda v: self.servo_angle_changed.emit(13, v))
        head_layout.addWidget(self.head_tilt_slider, 1, 1)
        
        self.head_tilt_label = QLabel("90°")
        self.head_tilt_slider.valueChanged.connect(lambda v: self.head_tilt_label.setText(f"{v}°"))
        head_layout.addWidget(self.head_tilt_label, 1, 2)
        
        layout.addWidget(head_group)
        
        # Animasyon kontrolü
        animation_group = QGroupBox("Animasyonlar")
        animation_layout = QVBoxLayout(animation_group)
        
        animation_buttons_layout = QHBoxLayout()
        
        greeting_btn = QPushButton("Selamlama")
        greeting_btn.clicked.connect(lambda: self.animation_requested.emit("greeting"))
        animation_buttons_layout.addWidget(greeting_btn)
        
        goodbye_btn = QPushButton("Vedalaşma")
        goodbye_btn.clicked.connect(lambda: self.animation_requested.emit("goodbye"))
        animation_buttons_layout.addWidget(goodbye_btn)
        
        thinking_btn = QPushButton("Düşünme")
        thinking_btn.clicked.connect(lambda: self.animation_requested.emit("thinking"))
        animation_buttons_layout.addWidget(thinking_btn)
        
        animation_layout.addLayout(animation_buttons_layout)
        
        # Reset butonu
        reset_btn = QPushButton("Pozisyon Sıfırla")
        reset_btn.clicked.connect(self.reset_position)
        animation_layout.addWidget(reset_btn)
        
        layout.addWidget(animation_group)
        
    def reset_position(self):
        """Tüm servoları merkez pozisyonuna getir"""
        self.head_pan_slider.setValue(90)
        self.head_tilt_slider.setValue(90)
        # Diğer servolar için de sinyal gönder
        for servo_id in [0, 1, 2, 6, 7, 8]:  # Ana servo'lar
            self.servo_angle_changed.emit(servo_id, 90)


class TargetControlWidget(QGroupBox):
    """Hedef kontrol widget'ı"""
    
    # Sinyal tanımları
    target_changed = pyqtSignal()
    interaction_paused = pyqtSignal()
    targets_cleared = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__("Hedef Kontrolü", parent)
        
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Hedef değiştirme
        change_target_btn = QPushButton("Sonraki Hedef")
        change_target_btn.clicked.connect(self.target_changed.emit)
        layout.addWidget(change_target_btn)
        
        # Etkileşim duraklat
        pause_btn = QPushButton("Etkileşim Duraklat")
        pause_btn.clicked.connect(self.interaction_paused.emit)
        layout.addWidget(pause_btn)
        
        # Hedefleri temizle
        clear_btn = QPushButton("Hedefleri Temizle")
        clear_btn.clicked.connect(self.targets_cleared.emit)
        layout.addWidget(clear_btn)
        
        # Hedef ayarları
        settings_group = QGroupBox("Takip Ayarları")
        settings_layout = QFormLayout(settings_group)
        
        # Minimum mesafe
        self.min_distance_spin = QDoubleSpinBox()
        self.min_distance_spin.setRange(0.1, 2.0)
        self.min_distance_spin.setValue(0.5)
        self.min_distance_spin.setSuffix(" m")
        settings_layout.addRow("Min Mesafe:", self.min_distance_spin)
        
        # Maksimum mesafe
        self.max_distance_spin = QDoubleSpinBox()
        self.max_distance_spin.setRange(2.0, 10.0)
        self.max_distance_spin.setValue(5.0)
        self.max_distance_spin.setSuffix(" m")
        settings_layout.addRow("Max Mesafe:", self.max_distance_spin)
        
        layout.addWidget(settings_group)
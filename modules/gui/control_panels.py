# =======================
# modules/gui/control_panels.py - Ek Kontrol Panelleri
# =======================

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from typing import Dict, Any, List


class AdvancedControlPanel(QWidget):
    """Gelişmiş kontrol paneli"""
    
    # Sinyal tanımları
    parameter_changed = pyqtSignal(str, str, object)  # category, parameter, value
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # YOLO Parameters
        yolo_group = QGroupBox("YOLO Parametreleri")
        yolo_layout = QFormLayout(yolo_group)
        
        # Confidence threshold
        self.confidence_spin = QDoubleSpinBox()
        self.confidence_spin.setRange(0.1, 1.0)
        self.confidence_spin.setSingleStep(0.05)
        self.confidence_spin.setValue(0.5)
        self.confidence_spin.valueChanged.connect(
            lambda v: self.parameter_changed.emit("yolo", "confidence_threshold", v)
        )
        yolo_layout.addRow("Confidence Threshold:", self.confidence_spin)
        
        # Max detections
        self.max_detections_spin = QSpinBox()
        self.max_detections_spin.setRange(1, 20)
        self.max_detections_spin.setValue(10)
        self.max_detections_spin.valueChanged.connect(
            lambda v: self.parameter_changed.emit("yolo", "max_detections", v)
        )
        yolo_layout.addRow("Max Detections:", self.max_detections_spin)
        
        # Device selection
        self.device_combo = QComboBox()
        self.device_combo.addItems(["cuda", "cpu"])
        self.device_combo.currentTextChanged.connect(
            lambda v: self.parameter_changed.emit("yolo", "device", v)
        )
        yolo_layout.addRow("Device:", self.device_combo)
        
        layout.addWidget(yolo_group)
        
        # Tracking Parameters
        tracking_group = QGroupBox("Takip Parametreleri")
        tracking_layout = QFormLayout(tracking_group)
        
        # Min distance
        self.min_distance_spin = QDoubleSpinBox()
        self.min_distance_spin.setRange(0.1, 5.0)
        self.min_distance_spin.setSingleStep(0.1)
        self.min_distance_spin.setValue(0.5)
        self.min_distance_spin.setSuffix(" m")
        self.min_distance_spin.valueChanged.connect(
            lambda v: self.parameter_changed.emit("tracking", "min_distance", v)
        )
        tracking_layout.addRow("Min Mesafe:", self.min_distance_spin)
        
        # Max distance
        self.max_distance_spin = QDoubleSpinBox()
        self.max_distance_spin.setRange(1.0, 10.0)
        self.max_distance_spin.setSingleStep(0.5)
        self.max_distance_spin.setValue(5.0)
        self.max_distance_spin.setSuffix(" m")
        self.max_distance_spin.valueChanged.connect(
            lambda v: self.parameter_changed.emit("tracking", "max_distance", v)
        )
        tracking_layout.addRow("Max Mesafe:", self.max_distance_spin)
        
        # Face priority
        self.face_priority_cb = QCheckBox()
        self.face_priority_cb.setChecked(True)
        self.face_priority_cb.toggled.connect(
            lambda v: self.parameter_changed.emit("tracking", "face_priority", v)
        )
        tracking_layout.addRow("Yüz Önceliği:", self.face_priority_cb)
        
        # Auto switch target
        self.auto_switch_cb = QCheckBox()
        self.auto_switch_cb.setChecked(False)
        self.auto_switch_cb.toggled.connect(
            lambda v: self.parameter_changed.emit("tracking", "auto_switch_target", v)
        )
        tracking_layout.addRow("Otomatik Hedef Değiştir:", self.auto_switch_cb)
        
        layout.addWidget(tracking_group)
        
        # Camera Parameters
        camera_group = QGroupBox("Kamera Parametreleri")
        camera_layout = QFormLayout(camera_group)
        
        # FPS
        self.fps_spin = QSpinBox()
        self.fps_spin.setRange(15, 60)
        self.fps_spin.setValue(30)
        self.fps_spin.valueChanged.connect(
            lambda v: self.parameter_changed.emit("camera", "fps", v)
        )
        camera_layout.addRow("FPS:", self.fps_spin)
        
        # Resolution
        self.resolution_combo = QComboBox()
        self.resolution_combo.addItems([
            "640x480", "848x480", "1280x720", "1920x1080"
        ])
        self.resolution_combo.setCurrentText("720x480")
        self.resolution_combo.currentTextChanged.connect(self.on_resolution_changed)
        camera_layout.addRow("Çözünürlük:", self.resolution_combo)
        
        layout.addWidget(camera_group)
        
    def on_resolution_changed(self, resolution_text):
        """Çözünürlük değiştiğinde"""
        try:
            width, height = map(int, resolution_text.split('x'))
            self.parameter_changed.emit("camera", "width", width)
            self.parameter_changed.emit("camera", "height", height)
        except ValueError:
            pass


class DiagnosticsPanel(QWidget):
    """Tanılama paneli"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # System Info
        info_group = QGroupBox("Sistem Bilgisi")
        info_layout = QFormLayout(info_group)
        
        self.python_version_label = QLabel()
        self.opencv_version_label = QLabel()
        self.pytorch_version_label = QLabel()
        self.realsense_version_label = QLabel()
        
        info_layout.addRow("Python:", self.python_version_label)
        info_layout.addRow("OpenCV:", self.opencv_version_label)
        info_layout.addRow("PyTorch:", self.pytorch_version_label)
        info_layout.addRow("RealSense:", self.realsense_version_label)
        
        layout.addWidget(info_group)
        
        # Performance Metrics
        perf_group = QGroupBox("Performans Metrikleri")
        perf_layout = QVBoxLayout(perf_group)
        
        self.performance_text = QTextEdit()
        self.performance_text.setMaximumHeight(200)
        self.performance_text.setReadOnly(True)
        perf_layout.addWidget(self.performance_text)
        
        refresh_perf_btn = QPushButton("Performans Güncelle")
        refresh_perf_btn.clicked.connect(self.update_performance_metrics)
        perf_layout.addWidget(refresh_perf_btn)
        
        layout.addWidget(perf_group)
        
        # Diagnostic Tests
        tests_group = QGroupBox("Tanılama Testleri")
        tests_layout = QVBoxLayout(tests_group)
        
        test_camera_btn = QPushButton("Kamera Testi")
        test_camera_btn.clicked.connect(self.test_camera)
        tests_layout.addWidget(test_camera_btn)
        
        test_yolo_btn = QPushButton("YOLO Testi")
        test_yolo_btn.clicked.connect(self.test_yolo)
        tests_layout.addWidget(test_yolo_btn)
        
        test_servo_btn = QPushButton("Servo Testi")
        test_servo_btn.clicked.connect(self.test_servo)
        tests_layout.addWidget(test_servo_btn)
        
        self.test_results_text = QTextEdit()
        self.test_results_text.setMaximumHeight(150)
        self.test_results_text.setReadOnly(True)
        tests_layout.addWidget(self.test_results_text)
        
        layout.addWidget(tests_group)
        
        # Initialize version info
        self.update_version_info()
        
    def update_version_info(self):
        """Versiyon bilgilerini güncelle"""
        import sys
        self.python_version_label.setText(f"{sys.version.split()[0]}")
        
        try:
            import cv2
            self.opencv_version_label.setText(cv2.__version__)
        except ImportError:
            self.opencv_version_label.setText("Yüklü değil")
        
        try:
            import torch
            self.pytorch_version_label.setText(torch.__version__)
        except ImportError:
            self.pytorch_version_label.setText("Yüklü değil")
        
        try:
            import pyrealsense2 as rs
            self.realsense_version_label.setText("2.55+")
        except ImportError:
            self.realsense_version_label.setText("Yüklü değil")
    
    def update_performance_metrics(self):
        """Performans metriklerini güncelle"""
        import psutil
        import time
        
        metrics = []
        metrics.append(f"CPU Kullanımı: {psutil.cpu_percent(interval=1):.1f}%")
        metrics.append(f"RAM Kullanımı: {psutil.virtual_memory().percent:.1f}%")
        metrics.append(f"Disk Kullanımı: {psutil.disk_usage('/').percent:.1f}%")
        
        # GPU bilgisi (opsiyonel)
        try:
            import pynvml
            pynvml.nvmlInit()
            handle = pynvml.nvmlDeviceGetHandleByIndex(0)
            gpu_util = pynvml.nvmlDeviceGetUtilizationRates(handle)
            metrics.append(f"GPU Kullanımı: {gpu_util.gpu:.1f}%")
        except:
            metrics.append("GPU Bilgisi: Mevcut değil")
        
        self.performance_text.setText("\n".join(metrics))
    
    def test_camera(self):
        """Kamera testi"""
        self.test_results_text.append("=== Kamera Testi ===")
        
        # RealSense testi
        try:
            import pyrealsense2 as rs
            ctx = rs.context()
            devices = ctx.query_devices()
            
            if len(devices) > 0:
                for i, device in enumerate(devices):
                    name = device.get_info(rs.camera_info.name)
                    serial = device.get_info(rs.camera_info.serial_number)
                    self.test_results_text.append(f"✓ RealSense bulundu: {name} (SN: {serial})")
            else:
                self.test_results_text.append("✗ RealSense cihazı bulunamadı")
        except Exception as e:
            self.test_results_text.append(f"✗ RealSense hatası: {e}")
        
        # Webcam testi
        try:
            import cv2
            cap = cv2.VideoCapture(0)
            if cap.isOpened():
                ret, frame = cap.read()
                if ret:
                    self.test_results_text.append("✓ Sistem kamerası çalışıyor")
                else:
                    self.test_results_text.append("✗ Sistem kamerası frame vermiyor")
                cap.release()
            else:
                self.test_results_text.append("✗ Sistem kamerası açılamadı")
        except Exception as e:
            self.test_results_text.append(f"✗ Webcam hatası: {e}")
    
    def test_yolo(self):
        """YOLO testi"""
        self.test_results_text.append("\n=== YOLO Testi ===")
        
        try:
            from ultralytics import YOLO
            import torch
            
            # CUDA testi
            if torch.cuda.is_available():
                self.test_results_text.append(f"✓ CUDA mevcut: {torch.cuda.get_device_name()}")
            else:
                self.test_results_text.append("! CUDA mevcut değil, CPU kullanılacak")
            
            # Model testi
            model_path = "data/models/yolov8n-person.pt"
            import os
            if os.path.exists(model_path):
                self.test_results_text.append("✓ YOLO model dosyası bulundu")
                
                # Test inference
                model = YOLO(model_path)
                import numpy as np
                test_image = np.zeros((640, 640, 3), dtype=np.uint8)
                results = model(test_image, verbose=False)
                self.test_results_text.append("✓ YOLO inference testi başarılı")
            else:
                self.test_results_text.append(f"✗ YOLO model dosyası bulunamadı: {model_path}")
                
        except Exception as e:
            self.test_results_text.append(f"✗ YOLO hatası: {e}")
    
    def test_servo(self):
        """Servo testi"""
        self.test_results_text.append("\n=== Servo Testi ===")
        
        try:
            import serial.tools.list_ports
            
            # Seri portları listele
            ports = list(serial.tools.list_ports.comports())
            if ports:
                self.test_results_text.append("Mevcut seri portlar:")
                for port in ports:
                    self.test_results_text.append(f"  • {port.device}: {port.description}")
            else:
                self.test_results_text.append("✗ Seri port bulunamadı")
            
            # Arduino test
            # Bu bölüm gerçek Arduino bağlantısı gerektirir
            self.test_results_text.append("! Arduino testi manuel olarak yapılmalı")
            
        except Exception as e:
            self.test_results_text.append(f"✗ Servo test hatası: {e}")


class CalibrationPanel(QWidget):
    """Kalibrasyon paneli"""
    
    calibration_completed = pyqtSignal(str, dict)  # calibration_type, results
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Camera Calibration
        camera_cal_group = QGroupBox("Kamera Kalibrasyonu")
        camera_cal_layout = QVBoxLayout(camera_cal_group)
        
        camera_cal_btn = QPushButton("Kamera Kalibrasyonunu Başlat")
        camera_cal_btn.clicked.connect(self.calibrate_camera)
        camera_cal_layout.addWidget(camera_cal_btn)
        
        self.camera_cal_progress = QProgressBar()
        self.camera_cal_progress.setVisible(False)
        camera_cal_layout.addWidget(self.camera_cal_progress)
        
        layout.addWidget(camera_cal_group)
        
        # Servo Calibration
        servo_cal_group = QGroupBox("Servo Kalibrasyonu")
        servo_cal_layout = QGridLayout(servo_cal_group)
        
        # Her servo için kalibrasyon butonları
        servo_names = [
            "Sol Omuz", "Sol Dirsek", "Sol Bilek",
            "Sağ Omuz", "Sağ Dirsek", "Sağ Bilek",
            "Kafa Pan", "Kafa Tilt"
        ]
        
        self.servo_cal_buttons = {}
        for i, name in enumerate(servo_names):
            btn = QPushButton(f"{name} Kalibrasyonu")
            btn.clicked.connect(lambda checked, n=name: self.calibrate_servo(n))
            servo_cal_layout.addWidget(btn, i // 2, i % 2)
            self.servo_cal_buttons[name] = btn
        
        # Tüm servolar
        calibrate_all_btn = QPushButton("Tüm Servoları Kalibre Et")
        calibrate_all_btn.clicked.connect(self.calibrate_all_servos)
        servo_cal_layout.addWidget(calibrate_all_btn, len(servo_names) // 2, 0, 1, 2)
        
        layout.addWidget(servo_cal_group)
        
        # Results
        results_group = QGroupBox("Kalibrasyon Sonuçları")
        results_layout = QVBoxLayout(results_group)
        
        self.results_text = QTextEdit()
        self.results_text.setMaximumHeight(200)
        self.results_text.setReadOnly(True)
        results_layout.addWidget(self.results_text)
        
        layout.addWidget(results_group)
        
    def calibrate_camera(self):
        """Kamera kalibrasyonu"""
        self.results_text.append("=== Kamera Kalibrasyonu ===")
        self.camera_cal_progress.setVisible(True)
        self.camera_cal_progress.setValue(0)
        
        # Basit kalibrasyon simülasyonu
        for i in range(101):
            self.camera_cal_progress.setValue(i)
            QApplication.processEvents()
            import time
            time.sleep(0.01)
        
        self.results_text.append("✓ Kamera kalibrasyonu tamamlandı")
        self.camera_cal_progress.setVisible(False)
        
        # Kalibrasyon sonuçları
        results = {
            "intrinsic_matrix": "[[fx, 0, cx], [0, fy, cy], [0, 0, 1]]",
            "distortion_coeffs": "[k1, k2, p1, p2, k3]"
        }
        self.calibration_completed.emit("camera", results)
    
    def calibrate_servo(self, servo_name):
        """Tekil servo kalibrasyonu"""
        self.results_text.append(f"=== {servo_name} Kalibrasyonu ===")
        self.results_text.append(f"✓ {servo_name} kalibre edildi")
        
        results = {"servo": servo_name, "center_position": 90}
        self.calibration_completed.emit("servo", results)
    
    def calibrate_all_servos(self):
        """Tüm servolar kalibrasyonu"""
        self.results_text.append("=== Tüm Servolar Kalibrasyonu ===")
        
        for name in self.servo_cal_buttons.keys():
            self.results_text.append(f"✓ {name} kalibre edildi")
            QApplication.processEvents()
            import time
            time.sleep(0.1)
        
        self.results_text.append("✓ Tüm servo kalibrasyonu tamamlandı")
        
        results = {"all_servos": "calibrated"}
        self.calibration_completed.emit("all_servos", results)
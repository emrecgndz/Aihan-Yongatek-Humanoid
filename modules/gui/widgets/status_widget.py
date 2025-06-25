# =======================
# modules/gui/widgets/status_widget.py - Durum Widget'ları
# =======================

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from typing import Dict, Any


class SystemStatusWidget(QGroupBox):
    """Sistem durumu widget'ı"""
    
    def __init__(self, parent=None):
        super().__init__("Sistem Durumu", parent)
        
        self.setup_ui()
        
    def setup_ui(self):
        layout = QGridLayout(self)
        
        # CPU kullanımı
        self.cpu_label = QLabel("CPU: 0%")
        self.cpu_progress = QProgressBar()
        self.cpu_progress.setMaximum(100)
        layout.addWidget(QLabel("CPU:"), 0, 0)
        layout.addWidget(self.cpu_progress, 0, 1)
        layout.addWidget(self.cpu_label, 0, 2)
        
        # GPU kullanımı
        self.gpu_label = QLabel("GPU: 0%")
        self.gpu_progress = QProgressBar()
        self.gpu_progress.setMaximum(100)
        layout.addWidget(QLabel("GPU:"), 1, 0)
        layout.addWidget(self.gpu_progress, 1, 1)
        layout.addWidget(self.gpu_label, 1, 2)
        
        # RAM kullanımı
        self.memory_label = QLabel("RAM: 0%")
        self.memory_progress = QProgressBar()
        self.memory_progress.setMaximum(100)
        layout.addWidget(QLabel("RAM:"), 2, 0)
        layout.addWidget(self.memory_progress, 2, 1)
        layout.addWidget(self.memory_label, 2, 2)
        
        # Sıcaklık
        self.temp_label = QLabel("Sıcaklık: 0°C")
        layout.addWidget(QLabel("Sıcaklık:"), 3, 0)
        layout.addWidget(self.temp_label, 3, 1, 1, 2)
        
        # FPS
        self.fps_label = QLabel("FPS: 0")
        layout.addWidget(QLabel("FPS:"), 4, 0)
        layout.addWidget(self.fps_label, 4, 1, 1, 2)
        
    def update_status(self, status_dict: Dict[str, Any]):
        """Durum bilgilerini güncelle"""
        if 'cpu_usage' in status_dict:
            cpu = status_dict['cpu_usage']
            self.cpu_label.setText(f"CPU: {cpu:.1f}%")
            self.cpu_progress.setValue(int(cpu))
            
            # Renk kodlaması
            if cpu > 80:
                self.cpu_progress.setStyleSheet("QProgressBar::chunk { background-color: red; }")
            elif cpu > 60:
                self.cpu_progress.setStyleSheet("QProgressBar::chunk { background-color: orange; }")
            else:
                self.cpu_progress.setStyleSheet("QProgressBar::chunk { background-color: green; }")
        
        if 'gpu_usage' in status_dict:
            gpu = status_dict['gpu_usage']
            self.gpu_label.setText(f"GPU: {gpu:.1f}%")
            self.gpu_progress.setValue(int(gpu))
        
        if 'memory_usage' in status_dict:
            memory = status_dict['memory_usage']
            self.memory_label.setText(f"RAM: {memory:.1f}%")
            self.memory_progress.setValue(int(memory))
        
        if 'temperature' in status_dict:
            temp = status_dict['temperature']
            self.temp_label.setText(f"Sıcaklık: {temp:.1f}°C")
        
        if 'fps' in status_dict:
            fps = status_dict['fps']
            self.fps_label.setText(f"FPS: {fps}")


class DetectionStatusWidget(QGroupBox):
    """Tespit durumu widget'ı"""
    
    def __init__(self, parent=None):
        super().__init__("Tespit Durumu", parent)
        
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Tespit sayısı
        self.detection_count_label = QLabel("Tespit: 0 kişi")
        self.detection_count_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout.addWidget(self.detection_count_label)
        
        # Birincil hedef
        self.primary_target_label = QLabel("Birincil Hedef: Yok")
        layout.addWidget(self.primary_target_label)
        
        # Hedef mesafesi
        self.target_distance_label = QLabel("Mesafe: -")
        layout.addWidget(self.target_distance_label)
        
        # YOLO inference süresi
        self.inference_time_label = QLabel("YOLO Süresi: 0ms")
        layout.addWidget(self.inference_time_label)
        
        # Tespit listesi
        self.detection_list = QListWidget()
        self.detection_list.setMaximumHeight(120)
        layout.addWidget(self.detection_list)
        
    def update_detections(self, detections: list, primary_target=None, inference_time: float = 0):
        """Tespit bilgilerini güncelle"""
        # Tespit sayısı
        count = len(detections)
        self.detection_count_label.setText(f"Tespit: {count} kişi")
        
        # Birincil hedef
        if primary_target:
            self.primary_target_label.setText(f"Birincil Hedef: ID {primary_target.detection.id}")
            self.target_distance_label.setText(f"Mesafe: {primary_target.distance:.2f}m")
        else:
            self.primary_target_label.setText("Birincil Hedef: Yok")
            self.target_distance_label.setText("Mesafe: -")
        
        # Inference süresi
        self.inference_time_label.setText(f"YOLO Süresi: {inference_time:.1f}ms")
        
        # Tespit listesi
        self.detection_list.clear()
        for i, detection in enumerate(detections):
            item_text = f"ID {detection.id}: {detection.confidence:.2f}"
            if hasattr(detection, 'distance') and detection.distance:
                item_text += f" | {detection.distance:.2f}m"
            
            item = QListWidgetItem(item_text)
            if primary_target and detection.id == primary_target.detection.id:
                item.setBackground(QColor(144, 238, 144))  # Light green
                
            self.detection_list.addItem(item)


class ServoStatusWidget(QGroupBox):
    """Servo durumu widget'ı"""
    
    def __init__(self, parent=None):
        super().__init__("Servo Durumu", parent)
        
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Arduino bağlantı durumu
        self.arduino_status_label = QLabel("Arduino: Bağlı değil")
        self.arduino_status_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(self.arduino_status_label)
        
        # Hareket durumu
        self.movement_status_label = QLabel("Hareket: Pasif")
        layout.addWidget(self.movement_status_label)
        
        # Son komut
        self.last_command_label = QLabel("Son Komut: -")
        layout.addWidget(self.last_command_label)
        
        # Servo pozisyonları (sadece ana servolar)
        positions_group = QGroupBox("Ana Pozisyonlar")
        positions_layout = QGridLayout(positions_group)
        
        self.head_pan_label = QLabel("Kafa Pan: 90°")
        self.head_tilt_label = QLabel("Kafa Tilt: 90°")
        self.right_shoulder_label = QLabel("Sağ Omuz: 90°")
        self.left_shoulder_label = QLabel("Sol Omuz: 90°")
        
        positions_layout.addWidget(self.head_pan_label, 0, 0)
        positions_layout.addWidget(self.head_tilt_label, 0, 1)
        positions_layout.addWidget(self.right_shoulder_label, 1, 0)
        positions_layout.addWidget(self.left_shoulder_label, 1, 1)
        
        layout.addWidget(positions_group)
        
    def update_servo_status(self, arduino_connected: bool, servo_positions: Dict[int, int], 
                           is_moving: bool = False, last_command: str = None):
        """Servo durumunu güncelle"""
        # Arduino bağlantı durumu
        if arduino_connected:
            self.arduino_status_label.setText("Arduino: Bağlı")
            self.arduino_status_label.setStyleSheet("font-weight: bold; color: green;")
        else:
            self.arduino_status_label.setText("Arduino: Bağlı değil")
            self.arduino_status_label.setStyleSheet("font-weight: bold; color: red;")
        
        # Hareket durumu
        if is_moving:
            self.movement_status_label.setText("Hareket: Aktif")
            self.movement_status_label.setStyleSheet("color: blue;")
        else:
            self.movement_status_label.setText("Hareket: Pasif")
            self.movement_status_label.setStyleSheet("color: black;")
        
        # Son komut
        if last_command:
            self.last_command_label.setText(f"Son Komut: {last_command}")
        
        # Pozisyonları güncelle
        if 12 in servo_positions:  # HEAD_PAN
            self.head_pan_label.setText(f"Kafa Pan: {servo_positions[12]}°")
        if 13 in servo_positions:  # HEAD_TILT
            self.head_tilt_label.setText(f"Kafa Tilt: {servo_positions[13]}°")
        if 6 in servo_positions:   # RIGHT_SHOULDER
            self.right_shoulder_label.setText(f"Sağ Omuz: {servo_positions[6]}°")
        if 0 in servo_positions:   # LEFT_SHOULDER
            self.left_shoulder_label.setText(f"Sol Omuz: {servo_positions[0]}°")
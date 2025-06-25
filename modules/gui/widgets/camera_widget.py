# =======================
# modules/gui/widgets/camera_widget.py - Kamera Görüntü Widget'ı
# =======================

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import cv2
import numpy as np
from typing import Optional


class CameraWidget(QLabel):
    """Kamera görüntüsü için özelleştirilmiş widget"""
    
    frame_clicked = pyqtSignal(int, int)  # x, y koordinatları
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setMinimumSize(640, 480)
        self.setStyleSheet("""
            QLabel {
                border: 2px solid #333;
                background-color: #000;
                color: #fff;
            }
        """)
        self.setAlignment(Qt.AlignCenter)
        self.setText("Kamera bağlanıyor...")
        
        # Görüntü bilgileri
        self.current_frame = None
        self.scale_factor = 1.0
        self.frame_size = (640, 480)
        
    def display_frame(self, frame: np.ndarray, detections: list = None):
        """Frame'i widget'ta göster"""
        if frame is None:
            self.setText("Kamera verisi yok")
            return
            
        try:
            # Tespitleri çiz (varsa)
            display_frame = frame.copy()
            if detections:
                display_frame = self._draw_detections(display_frame, detections)
            
            # OpenCV BGR'den RGB'ye çevir
            if len(display_frame.shape) == 3:
                rgb_frame = cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB)
            else:
                rgb_frame = display_frame
                
            height, width = rgb_frame.shape[:2]
            bytes_per_line = 3 * width if len(rgb_frame.shape) == 3 else width
            
            # QImage formatını belirle
            if len(rgb_frame.shape) == 3:
                format = QImage.Format_RGB888
            else:
                format = QImage.Format_Grayscale8
            
            # QImage oluştur
            qt_image = QImage(rgb_frame.data, width, height, bytes_per_line, format)
            
            # QPixmap'e çevir ve boyutlandır
            pixmap = QPixmap.fromImage(qt_image)
            scaled_pixmap = pixmap.scaled(
                self.size(), 
                Qt.KeepAspectRatio, 
                Qt.SmoothTransformation
            )
            
            # Scale factor'ü hesapla (mouse click mapping için)
            self.scale_factor = min(
                self.width() / width,
                self.height() / height
            )
            self.frame_size = (width, height)
            
            self.setPixmap(scaled_pixmap)
            self.current_frame = frame
            
        except Exception as e:
            self.setText(f"Görüntü hatası: {str(e)}")
    
    def _draw_detections(self, frame: np.ndarray, detections: list) -> np.ndarray:
        """Tespitleri frame üzerine çiz"""
        for detection in detections:
            bbox = detection.bbox
            
            # Kutu çiz
            cv2.rectangle(frame, (bbox.x1, bbox.y1), (bbox.x2, bbox.y2), (0, 255, 0), 2)
            
            # Label
            label = f"Person {detection.confidence:.2f}"
            if hasattr(detection, 'distance') and detection.distance:
                label += f" | {detection.distance:.2f}m"
                
            # Label arka planı
            label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)[0]
            cv2.rectangle(
                frame,
                (bbox.x1, bbox.y1 - label_size[1] - 10),
                (bbox.x1 + label_size[0], bbox.y1),
                (0, 255, 0), -1
            )
            
            # Label yazısı
            cv2.putText(
                frame, label,
                (bbox.x1, bbox.y1 - 5),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2
            )
            
            # Merkez noktası
            cv2.circle(frame, (detection.center_x, detection.center_y), 5, (255, 0, 0), -1)
        
        return frame
    
    def mousePressEvent(self, event):
        """Mouse tıklama olayı"""
        if event.button() == Qt.LeftButton and self.current_frame is not None:
            # Widget koordinatlarını frame koordinatlarına dönüştür
            widget_x = event.x()
            widget_y = event.y()
            
            # Scale ve offset hesapla
            frame_x = int(widget_x / self.scale_factor)
            frame_y = int(widget_y / self.scale_factor)
            
            # Sınırları kontrol et
            if (0 <= frame_x < self.frame_size[0] and 
                0 <= frame_y < self.frame_size[1]):
                self.frame_clicked.emit(frame_x, frame_y)
        
        super().mousePressEvent(event)
    
    def set_no_camera_message(self, message: str = "Kamera bağlı değil"):
        """Kamera olmadığında gösterilecek mesaj"""
        self.setText(message)
        self.current_frame = None


class DualCameraWidget(QWidget):
    """RGB ve Depth görüntüleri için ikili widget"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        layout = QHBoxLayout(self)
        
        # RGB widget
        self.rgb_widget = CameraWidget()
        self.rgb_widget.setMaximumWidth(400)
        layout.addWidget(self.rgb_widget)
        
        # Depth widget
        self.depth_widget = CameraWidget()
        self.depth_widget.setMaximumWidth(400)
        layout.addWidget(self.depth_widget)
        
        # Label'lar
        rgb_label = QLabel("RGB")
        rgb_label.setAlignment(Qt.AlignCenter)
        rgb_label.setStyleSheet("font-weight: bold;")
        
        depth_label = QLabel("Depth")
        depth_label.setAlignment(Qt.AlignCenter) 
        depth_label.setStyleSheet("font-weight: bold;")
        
        # Layout'u organize et
        main_layout = QVBoxLayout()
        
        # Üst label'lar
        label_layout = QHBoxLayout()
        label_layout.addWidget(rgb_label)
        label_layout.addWidget(depth_label)
        main_layout.addLayout(label_layout)
        
        # Kamera widget'ları
        main_layout.addLayout(layout)
        
        self.setLayout(main_layout)
    
    def display_frames(self, rgb_frame: np.ndarray, depth_frame: np.ndarray, detections: list = None):
        """Her iki frame'i de göster"""
        self.rgb_widget.display_frame(rgb_frame, detections)
        
        if depth_frame is not None:
            # Depth'i görselleştir
            depth_colorized = cv2.applyColorMap(
                cv2.convertScaleAbs(depth_frame, alpha=0.03), 
                cv2.COLORMAP_JET
            )
            self.depth_widget.display_frame(depth_colorized)
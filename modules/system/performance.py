# =======================
# modules/system/performance.py - Performans Ölçümü
# =======================

import time
import psutil
from collections import deque
from typing import Dict, List, Optional
from dataclasses import dataclass, field


@dataclass
class PerformanceMetrics:
    """Performans metrikleri"""
    fps: float = 0.0
    frame_time_ms: float = 0.0
    detection_time_ms: float = 0.0
    tracking_time_ms: float = 0.0
    servo_response_time_ms: float = 0.0
    total_cpu_usage: float = 0.0
    total_memory_usage: float = 0.0
    gpu_usage: float = 0.0
    timestamp: float = field(default_factory=time.time)


class PerformanceMonitor:
    """Performans izleme sistemi"""
    
    def __init__(self, history_size: int = 100):
        self.history_size = history_size
        
        # Metrik geçmişi
        self.metrics_history: deque = deque(maxlen=history_size)
        
        # Timing contexts
        self.timing_contexts: Dict[str, float] = {}
        
        # FPS hesaplama
        self.frame_times: deque = deque(maxlen=30)
        self.last_frame_time = time.time()
        
    def start_timing(self, context: str):
        """Timing context başlat"""
        self.timing_contexts[context] = time.time()
    
    def end_timing(self, context: str) -> float:
        """Timing context bitir ve süreyi döndür (ms)"""
        if context in self.timing_contexts:
            duration = (time.time() - self.timing_contexts[context]) * 1000
            del self.timing_contexts[context]
            return duration
        return 0.0
    
    def update_fps(self):
        """FPS'i güncelle"""
        current_time = time.time()
        frame_time = current_time - self.last_frame_time
        self.frame_times.append(frame_time)
        self.last_frame_time = current_time
    
    def get_current_fps(self) -> float:
        """Mevcut FPS'i hesapla"""
        if len(self.frame_times) < 5:
            return 0.0
        
        avg_frame_time = sum(self.frame_times) / len(self.frame_times)
        return 1.0 / avg_frame_time if avg_frame_time > 0 else 0.0
    
    def record_metrics(self, **kwargs) -> PerformanceMetrics:
        """Metrikleri kaydet"""
        metrics = PerformanceMetrics(
            fps=self.get_current_fps(),
            total_cpu_usage=psutil.cpu_percent(),
            total_memory_usage=psutil.virtual_memory().percent,
            **kwargs
        )
        
        self.metrics_history.append(metrics)
        return metrics
    
    def get_average_metrics(self, last_n: int = 10) -> Optional[PerformanceMetrics]:
        """Son N metriğin ortalamasını al"""
        if not self.metrics_history:
            return None
        
        recent_metrics = list(self.metrics_history)[-last_n:]
        
        if not recent_metrics:
            return None
        
        # Ortalamaları hesapla
        avg_metrics = PerformanceMetrics(
            fps=sum(m.fps for m in recent_metrics) / len(recent_metrics),
            frame_time_ms=sum(m.frame_time_ms for m in recent_metrics) / len(recent_metrics),
            detection_time_ms=sum(m.detection_time_ms for m in recent_metrics) / len(recent_metrics),
            tracking_time_ms=sum(m.tracking_time_ms for m in recent_metrics) / len(recent_metrics),
            servo_response_time_ms=sum(m.servo_response_time_ms for m in recent_metrics) / len(recent_metrics),
            total_cpu_usage=sum(m.total_cpu_usage for m in recent_metrics) / len(recent_metrics),
            total_memory_usage=sum(m.total_memory_usage for m in recent_metrics) / len(recent_metrics),
            gpu_usage=sum(m.gpu_usage for m in recent_metrics) / len(recent_metrics)
        )
        
        return avg_metrics
    
    def get_performance_report(self) -> Dict:
        """Performans raporu oluştur"""
        if not self.metrics_history:
            return {"error": "No metrics available"}
        
        recent_avg = self.get_average_metrics(10)
        overall_avg = self.get_average_metrics(len(self.metrics_history))
        latest = self.metrics_history[-1]
        
        return {
            "latest": {
                "fps": latest.fps,
                "cpu_usage": latest.total_cpu_usage,
                "memory_usage": latest.total_memory_usage,
                "detection_time": latest.detection_time_ms
            },
            "recent_average": {
                "fps": recent_avg.fps,
                "cpu_usage": recent_avg.total_cpu_usage,
                "memory_usage": recent_avg.total_memory_usage,
                "detection_time": recent_avg.detection_time_ms
            } if recent_avg else None,
            "overall_average": {
                "fps": overall_avg.fps,
                "cpu_usage": overall_avg.total_cpu_usage,
                "memory_usage": overall_avg.total_memory_usage,
                "detection_time": overall_avg.detection_time_ms
            } if overall_avg else None,
            "total_samples": len(self.metrics_history)
        }
    
    def is_performance_degraded(self, fps_threshold: float = 15.0, 
                               cpu_threshold: float = 85.0) -> bool:
        """Performans düşüşü var mı kontrol et"""
        if not self.metrics_history:
            return False
        
        recent_avg = self.get_average_metrics(5)
        if not recent_avg:
            return False
        
        return (recent_avg.fps < fps_threshold or 
                recent_avg.total_cpu_usage > cpu_threshold)
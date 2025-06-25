# =======================
# modules/system/monitor.py - Sistem İzleme
# =======================

import psutil
import time
from typing import Dict, Any, Optional
import platform

try:
    import pynvml
    NVIDIA_GPU_AVAILABLE = True
except ImportError:
    NVIDIA_GPU_AVAILABLE = False

from modules.utils.data_structures import SystemStatus


class SystemMonitor:
    """Sistem performans izleyicisi"""
    
    def __init__(self):
        self.start_time = time.time()
        self.gpu_initialized = False
        
        # GPU başlat
        if NVIDIA_GPU_AVAILABLE:
            try:
                pynvml.nvmlInit()
                self.gpu_initialized = True
            except:
                pass
    
    def get_system_status(self) -> SystemStatus:
        """Mevcut sistem durumunu döndür"""
        return SystemStatus(
            cpu_usage=self.get_cpu_usage(),
            gpu_usage=self.get_gpu_usage(),
            memory_usage=self.get_memory_usage(),
            temperature=self.get_temperature(),
            fps=0,  # Bu GUI'den güncellenecek
            active_modules=[],  # Bu ana uygulamadan güncellenecek
            errors=[],
            warnings=[]
        )
    
    def get_cpu_usage(self) -> float:
        """CPU kullanım yüzdesi"""
        return psutil.cpu_percent(interval=0.1)
    
    def get_memory_usage(self) -> float:
        """RAM kullanım yüzdesi"""
        memory = psutil.virtual_memory()
        return memory.percent
    
    def get_gpu_usage(self) -> float:
        """GPU kullanım yüzdesi (NVIDIA)"""
        if not self.gpu_initialized:
            return 0.0
        
        try:
            handle = pynvml.nvmlDeviceGetHandleByIndex(0)
            utilization = pynvml.nvmlDeviceGetUtilizationRates(handle)
            return float(utilization.gpu)
        except:
            return 0.0
    
    def get_temperature(self) -> float:
        """Sistem sıcaklığı"""
        try:
            if platform.system() == "Darwin":  # macOS
                # macOS için özel sıcaklık okuma
                return self._get_macos_temperature()
            else:
                # Linux için
                temps = psutil.sensors_temperatures()
                if temps:
                    for name, entries in temps.items():
                        if entries:
                            return entries[0].current
        except:
            pass
        
        return 0.0
    
    def _get_macos_temperature(self) -> float:
        """macOS için CPU sıcaklığı (yaklaşık)"""
        try:
            # macOS'ta psutil ile sıcaklık okuma
            import subprocess
            result = subprocess.run(['sysctl', '-n', 'machdep.xcpm.cpu_thermal_state'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                # Thermal state'i sıcaklığa çevir (yaklaşık)
                thermal_state = int(result.stdout.strip())
                return 30.0 + (thermal_state * 10.0)  # Yaklaşık dönüşüm
        except:
            pass
        
        return 45.0  # Varsayılan normal sıcaklık
    
    def get_disk_usage(self) -> float:
        """Disk kullanım yüzdesi"""
        disk = psutil.disk_usage('/')
        return (disk.used / disk.total) * 100
    
    def get_uptime(self) -> float:
        """Uygulama çalışma süresi (saniye)"""
        return time.time() - self.start_time

# =======================
# modules/servo/arduino_comm.py - Arduino İletişimi
# =======================

import serial
import time
import json
from threading import Thread, Lock
from typing import Dict, List, Optional, Tuple
import queue

from config.settings import ServoSettings
from config.constants import ServoIDs, ARDUINO_COMMANDS
from modules.system.logger import SystemLogger


class ArduinoComm:
    """Arduino ile seri port iletişimi"""
    
    def __init__(self, settings: ServoSettings, logger: SystemLogger):
        self.settings = settings
        self.logger = logger
        
        # Seri port
        self.serial_port = None
        self.is_connected = False
        
        # Komut kuyruğu
        self.command_queue = queue.Queue()
        self.response_queue = queue.Queue()
        
        # Thread kontrolü
        self.comm_thread = None
        self.is_running = False
        self.lock = Lock()
        
        # Durum takibi
        self.last_servo_positions = {}
        self.arduino_status = {
            'connected': False,
            'last_ping': 0,
            'error_count': 0
        }
    
    def connect(self) -> bool:
        """Arduino'ya bağlan"""
        try:
            self.serial_port = serial.Serial(
                port=self.settings.port,
                baudrate=self.settings.baudrate,
                timeout=self.settings.timeout,
                write_timeout=self.settings.timeout
            )
            
            # Bağlantıyı test et
            time.sleep(2)  # Arduino reset bekleme
            
            if self._ping_arduino():
                self.is_connected = True
                self.arduino_status['connected'] = True
                self.start_communication()
                self.logger.info(f"Arduino bağlandı: {self.settings.port}")
                return True
            else:
                self.serial_port.close()
                return False
                
        except Exception as e:
            self.logger.error(f"Arduino bağlantı hatası: {e}")
            return False
    
    def disconnect(self):
        """Arduino bağlantısını kes"""
        self.is_running = False
        self.is_connected = False
        
        if self.comm_thread:
            self.comm_thread.join(timeout=2.0)
        
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()
        
        self.logger.info("Arduino bağlantısı kesildi")
    
    def start_communication(self):
        """İletişim thread'ini başlat"""
        self.is_running = True
        self.comm_thread = Thread(target=self._communication_loop, daemon=True)
        self.comm_thread.start()
    
    def _communication_loop(self):
        """Ana iletişim döngüsü"""
        while self.is_running and self.is_connected:
            try:
                # Komut kuyruğunu kontrol et
                if not self.command_queue.empty():
                    command = self.command_queue.get_nowait()
                    self._send_command(command)
                
                # Arduino'dan gelen yanıtları oku
                if self.serial_port.in_waiting > 0:
                    response = self._read_response()
                    if response:
                        self.response_queue.put(response)
                
                # Periyodik ping
                current_time = time.time()
                if current_time - self.arduino_status['last_ping'] > 5.0:
                    self._ping_arduino()
                
                time.sleep(0.01)  # CPU kullanımını azalt
                
            except Exception as e:
                self.logger.error(f"Arduino iletişim hatası: {e}")
                self.arduino_status['error_count'] += 1
                time.sleep(0.1)
    
    def _send_command(self, command: str):
        """Arduino'ya komut gönder"""
        try:
            with self.lock:
                if self.serial_port and self.serial_port.is_open:
                    self.serial_port.write((command + '\n').encode())
                    self.serial_port.flush()
        except Exception as e:
            self.logger.error(f"Komut gönderme hatası: {e}")
    
    def _read_response(self) -> Optional[str]:
        """Arduino'dan yanıt oku"""
        try:
            if self.serial_port and self.serial_port.is_open:
                line = self.serial_port.readline().decode().strip()
                return line if line else None
        except Exception as e:
            self.logger.error(f"Yanıt okuma hatası: {e}")
            return None
    
    def _ping_arduino(self) -> bool:
        """Arduino bağlantısını test et"""
        try:
            self._send_command(ARDUINO_COMMANDS['PING'])
            
            # Yanıt bekle
            start_time = time.time()
            while time.time() - start_time < 1.0:
                if not self.response_queue.empty():
                    response = self.response_queue.get_nowait()
                    if "PONG" in response:
                        self.arduino_status['last_ping'] = time.time()
                        return True
                time.sleep(0.01)
            
            return False
            
        except Exception:
            return False
    
    def set_servo_angle(self, servo_id: int, angle: int):
        """Servo açısını ayarla"""
        if not self.is_connected:
            return False
        
        # Açı sınırlarını kontrol et
        if not (0 <= angle <= 180):
            self.logger.warning(f"Geçersiz servo açısı: {angle}")
            return False
        
        # Komut oluştur
        command = f"{ARDUINO_COMMANDS['SET_SERVO']}{servo_id},{angle}"
        self.command_queue.put(command)
        
        # Pozisyonu kaydet
        self.last_servo_positions[servo_id] = angle
        
        return True
    
    def set_servo_speed(self, speed: int):
        """Servo hızını ayarla (1-10)"""
        if not self.is_connected:
            return False
        
        if not (1 <= speed <= 10):
            return False
        
        command = f"{ARDUINO_COMMANDS['SET_SPEED']}{speed}"
        self.command_queue.put(command)
        return True
    
    def calibrate_servos(self):
        """Servoları kalibre et (90 derece ortala)"""
        if not self.is_connected:
            return False
        
        command = ARDUINO_COMMANDS['CALIBRATE']
        self.command_queue.put(command)
        return True
    
    def get_status(self) -> Dict:
        """Arduino durumunu döndür"""
        return self.arduino_status.copy()
    
    def get_servo_positions(self) -> Dict[int, int]:
        """Mevcut servo pozisyonlarını döndür"""
        return self.last_servo_positions.copy()

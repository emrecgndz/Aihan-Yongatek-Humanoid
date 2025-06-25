/*
 * ===============================================
 * arduino_servo_controller.ino
 * Expo-Humanoid 14 DOF Servo Controller
 * ===============================================
 * 
 * Bu sketch 14 adet servo motoru kontrol eder:
 * - Sol kol: 6 servo (0-5)
 * - Sağ kol: 6 servo (6-11) 
 * - Kafa: 2 servo (12-13)
 * 
 * Komutlar:
 * - S<id>,<angle>  : Servo açısını ayarla (örn: S0,90)
 * - V<speed>       : Hareket hızını ayarla (1-10)
 * - C              : Tüm servoları kalibre et (90°)
 * - R              : Reset
 * - P              : Ping (bağlantı testi)
 * - G              : Durum bilgisi al
 */

#include <Servo.h>

// Konfigürasyon
const int SERVO_COUNT = 14;
const int BAUD_RATE = 115200;
const int DEFAULT_POSITION = 90;
const int MIN_ANGLE = 0;
const int MAX_ANGLE = 180;
const int DEFAULT_SPEED = 5;

// Servo nesneleri
Servo servos[SERVO_COUNT];

// Servo pin tanımları (Arduino Uno/Mega uyumlu)
int servoPins[SERVO_COUNT] = {
  2,  3,  4,  5,  6,  7,    // Sol kol (0-5)
  8,  9,  10, 11, 12, 13,   // Sağ kol (6-11)
  A0, A1                    // Kafa (12-13)
};

// Servo durumları
int currentPositions[SERVO_COUNT];
int targetPositions[SERVO_COUNT];
bool servoAttached[SERVO_COUNT];

// Hareket kontrolü
int movementSpeed = DEFAULT_SPEED;
unsigned long lastMoveTime = 0;
const unsigned long MOVE_INTERVAL = 20; // 20ms (50Hz)

// İstatistikler
unsigned long commandCount = 0;
unsigned long errorCount = 0;
unsigned long startTime = 0;

void setup() {
  // Seri port başlat
  Serial.begin(BAUD_RATE);
  
  // Başlangıç zamanı
  startTime = millis();
  
  // Servoları başlat
  initializeServos();
  
  // Başlangıç mesajı
  Serial.println("Expo-Humanoid Servo Controller v1.0");
  Serial.println("14 DOF Ready");
  Serial.print("Servo pins: ");
  for(int i = 0; i < SERVO_COUNT; i++) {
    Serial.print(servoPins[i]);
    if(i < SERVO_COUNT - 1) Serial.print(",");
  }
  Serial.println();
  Serial.println("Commands: S<id>,<angle> | V<speed> | C | R | P | G");
  Serial.println("READY");
}

void loop() {
  // Seri port komutlarını işle
  if(Serial.available()) {
    String command = Serial.readStringUntil('\n');
    command.trim();
    processCommand(command);
  }
  
  // Yumuşak hareket güncelleme
  updateSmoothMovement();
  
  // Watchdog (optional)
  // checkWatchdog();
}

void initializeServos() {
  for(int i = 0; i < SERVO_COUNT; i++) {
    // Servo attach
    servos[i].attach(servoPins[i]);
    servoAttached[i] = true;
    
    // Başlangıç pozisyonuna getir
    currentPositions[i] = DEFAULT_POSITION;
    targetPositions[i] = DEFAULT_POSITION;
    servos[i].write(DEFAULT_POSITION);
    
    // Kısa gecikme (servo stabilizasyon)
    delay(50);
  }
  
  Serial.println("Servos initialized to center position (90°)");
}

void processCommand(String cmd) {
  commandCount++;
  
  if(cmd.length() == 0) {
    sendError("Empty command");
    return;
  }
  
  char cmdType = cmd.charAt(0);
  
  switch(cmdType) {
    case 'S':
    case 's':
      handleServoCommand(cmd);
      break;
      
    case 'V':
    case 'v':
      handleSpeedCommand(cmd);
      break;
      
    case 'C':
    case 'c':
      handleCalibrateCommand();
      break;
      
    case 'R':
    case 'r':
      handleResetCommand();
      break;
      
    case 'P':
    case 'p':
      handlePingCommand();
      break;
      
    case 'G':
    case 'g':
      handleStatusCommand();
      break;
      
    default:
      sendError("Unknown command: " + String(cmdType));
      break;
  }
}

void handleServoCommand(String cmd) {
  // Format: S<id>,<angle>
  // Örnek: S0,90
  
  int commaIndex = cmd.indexOf(',');
  if(commaIndex == -1) {
    sendError("Invalid servo command format. Use: S<id>,<angle>");
    return;
  }
  
  int servoId = cmd.substring(1, commaIndex).toInt();
  int angle = cmd.substring(commaIndex + 1).toInt();
  
  // Validasyon
  if(servoId < 0 || servoId >= SERVO_COUNT) {
    sendError("Invalid servo ID: " + String(servoId) + " (0-" + String(SERVO_COUNT-1) + ")");
    return;
  }
  
  if(angle < MIN_ANGLE || angle > MAX_ANGLE) {
    sendError("Invalid angle: " + String(angle) + " (" + String(MIN_ANGLE) + "-" + String(MAX_ANGLE) + ")");
    return;
  }
  
  if(!servoAttached[servoId]) {
    sendError("Servo " + String(servoId) + " not attached");
    return;
  }
  
  // Hedef pozisyonu ayarla
  targetPositions[servoId] = angle;
  
  Serial.println("OK:" + String(servoId) + ":" + String(angle));
}

void handleSpeedCommand(String cmd) {
  // Format: V<speed>
  // Örnek: V5
  
  int speed = cmd.substring(1).toInt();
  
  if(speed < 1 || speed > 10) {
    sendError("Invalid speed: " + String(speed) + " (1-10)");
    return;
  }
  
  movementSpeed = speed;
  Serial.println("OK:SPEED:" + String(speed));
}

void handleCalibrateCommand() {
  // Tüm servoları merkez pozisyona getir
  for(int i = 0; i < SERVO_COUNT; i++) {
    if(servoAttached[i]) {
      targetPositions[i] = DEFAULT_POSITION;
    }
  }
  
  Serial.println("OK:CALIBRATE:ALL");
}

void handleResetCommand() {
  // Sistem reset
  Serial.println("OK:RESET");
  delay(100);
  
  // Servolar detach
  for(int i = 0; i < SERVO_COUNT; i++) {
    if(servoAttached[i]) {
      servos[i].detach();
      servoAttached[i] = false;
    }
  }
  
  delay(500);
  
  // Yeniden başlat
  initializeServos();
  
  // İstatistikleri sıfırla
  commandCount = 0;
  errorCount = 0;
  startTime = millis();
  
  Serial.println("RESET_COMPLETE");
}

void handlePingCommand() {
  // Bağlantı testi
  Serial.println("PONG");
}

void handleStatusCommand() {
  // Sistem durumu
  unsigned long uptime = millis() - startTime;
  
  Serial.println("STATUS:");
  Serial.println("  Uptime: " + String(uptime) + "ms");
  Serial.println("  Commands: " + String(commandCount));
  Serial.println("  Errors: " + String(errorCount));
  Serial.println("  Speed: " + String(movementSpeed));
  Serial.println("  Free RAM: " + String(getFreeRam()) + " bytes");
  
  Serial.print("  Positions: ");
  for(int i = 0; i < SERVO_COUNT; i++) {
    Serial.print(String(i) + ":" + String(currentPositions[i]));
    if(i < SERVO_COUNT - 1) Serial.print(",");
  }
  Serial.println();
  
  Serial.print("  Targets: ");
  for(int i = 0; i < SERVO_COUNT; i++) {
    Serial.print(String(i) + ":" + String(targetPositions[i]));
    if(i < SERVO_COUNT - 1) Serial.print(",");
  }
  Serial.println();
  
  Serial.println("STATUS_END");
}

void updateSmoothMovement() {
  // Hareket hızı kontrolü
  unsigned long currentTime = millis();
  if(currentTime - lastMoveTime < MOVE_INTERVAL) {
    return;
  }
  lastMoveTime = currentTime;
  
  // Her servo için yumuşak hareket
  for(int i = 0; i < SERVO_COUNT; i++) {
    if(!servoAttached[i]) continue;
    
    int current = currentPositions[i];
    int target = targetPositions[i];
    
    if(current != target) {
      // Hareket miktarını hesapla (hıza bağlı)
      int maxStep = movementSpeed; // 1-10 arası
      int diff = target - current;
      int step = 0;
      
      if(abs(diff) <= maxStep) {
        step = diff;
      } else {
        step = (diff > 0) ? maxStep : -maxStep;
      }
      
      // Yeni pozisyon
      int newPosition = current + step;
      currentPositions[i] = newPosition;
      
      // Servo'yu hareket ettir
      servos[i].write(newPosition);
    }
  }
}

void sendError(String message) {
  errorCount++;
  Serial.println("ERROR:" + message);
}

int getFreeRam() {
  // Arduino Uno/Nano için RAM hesaplama
  extern int __heap_start, *__brkval; 
  int v; 
  return (int) &v - (__brkval == 0 ? (int) &__heap_start : (int) __brkval); 
}

// Watchdog fonksiyonu (opsiyonel)
void checkWatchdog() {
  // Uzun süre komut gelmezse güvenlik önlemi
  static unsigned long lastCommandTime = 0;
  const unsigned long WATCHDOG_TIMEOUT = 30000; // 30 saniye
  
  if(commandCount > 0) {
    lastCommandTime = millis();
  }
  
  if(millis() - lastCommandTime > WATCHDOG_TIMEOUT) {
    // Timeout durumunda merkez pozisyona getir
    for(int i = 0; i < SERVO_COUNT; i++) {
      targetPositions[i] = DEFAULT_POSITION;
    }
    
    Serial.println("WATCHDOG:TIMEOUT:CENTERING");
    lastCommandTime = millis();
  }
}

/*
 * Test komutları:
 * 
 * P              // Ping test
 * S0,45          // Sol omuz 45°
 * S12,120        // Kafa pan 120°
 * V8             // Hız 8
 * C              // Kalibre et
 * G              // Status
 * 
 * Servo mapping:
 * 0-5:   Sol kol (omuz, dirsek, bilek, el, başparmak, işaret)
 * 6-11:  Sağ kol (omuz, dirsek, bilek, el, başparmak, işaret)
 * 12:    Kafa pan (yatay)
 * 13:    Kafa tilt (dikey)
 */
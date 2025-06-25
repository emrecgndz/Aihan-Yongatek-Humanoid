# =======================
# modules/utils/math_utils.py - Matematik Yardımcıları
# =======================

import math
import numpy as np
from typing import Tuple, List, Optional


def angle_difference(angle1: float, angle2: float) -> float:
    """İki açı arasındaki en kısa farkı hesapla (derece)"""
    diff = angle2 - angle1
    while diff > 180:
        diff -= 360
    while diff < -180:
        diff += 360
    return diff


def lerp(start: float, end: float, t: float) -> float:
    """Linear interpolation"""
    return start + (end - start) * t


def clamp(value: float, min_val: float, max_val: float) -> float:
    """Değeri belirli aralıkta sınırla"""
    return max(min_val, min(max_val, value))


def smooth_angle_transition(current: float, target: float, speed: float) -> float:
    """Yumuşak açı geçişi"""
    diff = angle_difference(current, target)
    
    if abs(diff) < speed:
        return target
    
    if diff > 0:
        return current + speed
    else:
        return current - speed


def calculate_servo_angles_for_point(target_x: int, target_y: int, 
                                   frame_width: int, frame_height: int) -> Tuple[int, int]:
    """Ekrandaki bir noktaya bakmak için servo açılarını hesapla"""
    # Normalize coordinates (-1 to 1)
    norm_x = (target_x - frame_width / 2) / (frame_width / 2)
    norm_y = (target_y - frame_height / 2) / (frame_height / 2)
    
    # Convert to servo angles (0-180)
    pan_angle = int(90 + norm_x * 45)  # ±45 degrees
    tilt_angle = int(90 - norm_y * 30)  # ±30 degrees
    
    # Clamp to servo limits
    pan_angle = clamp(pan_angle, 30, 150)
    tilt_angle = clamp(tilt_angle, 60, 120)
    
    return pan_angle, tilt_angle


def calculate_arm_reach_position(target_x: float, target_y: float, target_z: float,
                               arm_length_1: float = 0.3, arm_length_2: float = 0.25) -> Optional[Tuple[int, int, int]]:
    """3D hedef için kol servo açılarını hesapla (basit 2-link IK)"""
    try:
        # Target distance from shoulder
        distance = math.sqrt(target_x**2 + target_y**2 + target_z**2)
        
        # Check if target is reachable
        max_reach = arm_length_1 + arm_length_2
        if distance > max_reach:
            return None
        
        # Base angle (shoulder rotation)
        base_angle = math.atan2(target_y, target_x)
        
        # Project to 2D for IK calculation
        distance_2d = math.sqrt(target_x**2 + target_z**2)
        
        # Law of cosines for elbow angle
        cos_elbow = (arm_length_1**2 + arm_length_2**2 - distance_2d**2) / (2 * arm_length_1 * arm_length_2)
        cos_elbow = clamp(cos_elbow, -1, 1)
        elbow_angle = math.acos(cos_elbow)
        
        # Shoulder angle
        angle_to_target = math.atan2(target_z, math.sqrt(target_x**2 + target_y**2))
        cos_shoulder = (arm_length_1**2 + distance_2d**2 - arm_length_2**2) / (2 * arm_length_1 * distance_2d)
        cos_shoulder = clamp(cos_shoulder, -1, 1)
        shoulder_offset = math.acos(cos_shoulder)
        shoulder_angle = angle_to_target + shoulder_offset
        
        # Convert to servo angles (radians to degrees, then to servo range)
        shoulder_servo = int(90 + math.degrees(shoulder_angle))
        elbow_servo = int(180 - math.degrees(elbow_angle))
        base_servo = int(90 + math.degrees(base_angle))
        
        # Clamp to realistic ranges
        shoulder_servo = clamp(shoulder_servo, 0, 180)
        elbow_servo = clamp(elbow_servo, 0, 180)
        base_servo = clamp(base_servo, 0, 180)
        
        return shoulder_servo, elbow_servo, base_servo
        
    except Exception:
        return None


def moving_average(values: List[float], window_size: int = 5) -> float:
    """Hareketli ortalama hesapla"""
    if not values:
        return 0.0
    
    relevant_values = values[-window_size:]
    return sum(relevant_values) / len(relevant_values)


def euclidean_distance(point1: Tuple[float, float], point2: Tuple[float, float]) -> float:
    """2D Öklid mesafesi"""
    return math.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)


def normalize_angle(angle: float) -> float:
    """Açıyı 0-360 aralığına normalize et"""
    while angle < 0:
        angle += 360
    while angle >= 360:
        angle -= 360
    return angle

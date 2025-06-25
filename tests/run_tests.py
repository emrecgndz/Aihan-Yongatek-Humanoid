# =======================
# tests/run_tests.py - Test Çalıştırıcı
# =======================

import unittest
import sys
import os
from pathlib import Path

# Proje root'unu path'e ekle
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def run_all_tests():
    """Tüm testleri çalıştır"""
    # Test modüllerini import et
    from tests.test_camera import TestCameraModules, TestCameraSettings
    from tests.test_yolo import TestYOLODetector
    from tests.test_servo import TestServoController, TestArmPosition
    from tests.test_integration import TestSystemIntegration, TestDataFlow
    
    # Test suite oluştur
    test_suite = unittest.TestSuite()
    
    # Test sınıflarını ekle
    test_classes = [
        TestCameraModules,
        TestCameraSettings,
        TestYOLODetector,
        TestServoController,
        TestArmPosition,
        TestSystemIntegration,
        TestDataFlow
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Test runner
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    return result.wasSuccessful()


def run_specific_test(test_name):
    """Belirli bir test modülünü çalıştır"""
    test_modules = {
        'camera': 'tests.test_camera',
        'yolo': 'tests.test_yolo',
        'servo': 'tests.test_servo',
        'integration': 'tests.test_integration'
    }
    
    if test_name not in test_modules:
        print(f"Geçersiz test adı. Kullanılabilir testler: {list(test_modules.keys())}")
        return False
    
    module_name = test_modules[test_name]
    suite = unittest.TestLoader().loadTestsFromName(module_name)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Belirli test çalıştır
        test_name = sys.argv[1]
        success = run_specific_test(test_name)
    else:
        # Tüm testleri çalıştır
        success = run_all_tests()
    
    sys.exit(0 if success else 1)

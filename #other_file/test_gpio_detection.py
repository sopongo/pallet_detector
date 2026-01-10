"""
Test GPIO Detection and Mock GPIO functionality
Tests the improved OS detection and Mock GPIO implementation
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

def test_gpio_detection():
    """Test that GPIO detection works correctly"""
    print("\n" + "="*60)
    print("TEST 1: GPIO Detection Logic")
    print("="*60)
    
    from utils.gpio_control import is_raspberry_pi, IS_RASPBERRY_PI, GPIO_AVAILABLE, DEVICE_MODEL
    
    # Test is_raspberry_pi function
    is_rpi, device = is_raspberry_pi()
    print(f"is_raspberry_pi() returned: ({is_rpi}, {device})")
    print(f"IS_RASPBERRY_PI constant: {IS_RASPBERRY_PI}")
    print(f"GPIO_AVAILABLE: {GPIO_AVAILABLE}")
    print(f"DEVICE_MODEL: {DEVICE_MODEL}")
    
    # Should return tuple of (bool, str)
    assert isinstance(is_rpi, bool), "is_raspberry_pi()[0] should return bool"
    assert isinstance(device, str), "is_raspberry_pi()[1] should return str"
    assert IS_RASPBERRY_PI == is_rpi, "IS_RASPBERRY_PI should match is_raspberry_pi()[0]"
    assert DEVICE_MODEL == device, "DEVICE_MODEL should match is_raspberry_pi()[1]"
    
    print("✅ TEST PASSED: GPIO detection working correctly")
    return True


def test_mock_led():
    """Test MockLED functionality"""
    print("\n" + "="*60)
    print("TEST 2: Mock LED Functionality")
    print("="*60)
    
    from utils.gpio_control import MockLED
    
    # Create Mock LED
    led = MockLED(17, name="Test")
    assert led.pin == 17
    assert led.name == "Test"
    assert led.is_on == False
    
    # Test on()
    led.on()
    assert led.is_on == True
    
    # Test off()
    led.off()
    assert led.is_on == False
    
    print("✅ TEST PASSED: MockLED works correctly")
    return True


def test_light_controller_creation():
    """Test that LightController can be created without errors"""
    print("\n" + "="*60)
    print("TEST 3: LightController Creation")
    print("="*60)
    
    from utils.gpio_control import LightController
    
    # Should work on any platform (uses Mock on non-RPi)
    controller = LightController(red_pin=17, green_pin=27)
    
    assert controller.red_pin == 17
    assert controller.green_pin == 27
    assert controller.red_light is not None
    assert controller.green_light is not None
    
    print("✅ TEST PASSED: LightController created successfully")
    return True


def test_light_controller_methods():
    """Test all LightController methods"""
    print("\n" + "="*60)
    print("TEST 4: LightController Methods")
    print("="*60)
    
    from utils.gpio_control import LightController
    
    controller = LightController()
    
    # Test test_red()
    result = controller.test_red()
    assert result['success'] == True
    assert result['state'] == 'on'
    assert 'mode' in result
    print(f"test_red(): {result}")
    
    # Test test_green()
    result = controller.test_green()
    assert result['success'] == True
    assert result['state'] == 'on'
    assert 'mode' in result
    print(f"test_green(): {result}")
    
    # Test turn_off_red()
    result = controller.turn_off_red()
    assert result['success'] == True
    assert result['state'] == 'off'
    print(f"turn_off_red(): {result}")
    
    # Test turn_off_green()
    result = controller.turn_off_green()
    assert result['success'] == True
    assert result['state'] == 'off'
    print(f"turn_off_green(): {result}")
    
    # Test all_off()
    result = controller.all_off()
    assert result['success'] == True
    print(f"all_off(): {result}")
    
    print("✅ TEST PASSED: All LightController methods work correctly")
    return True


def test_gpio_function():
    """Test test_gpio() function"""
    print("\n" + "="*60)
    print("TEST 5: test_gpio() Function")
    print("="*60)
    
    from utils.gpio_control import test_gpio
    import json
    
    result = test_gpio()
    
    assert 'success' in result
    assert 'message' in result
    assert 'details' in result
    
    details = result['details']
    assert 'is_raspberry_pi' in details
    assert 'device' in details
    assert 'gpio_mode' in details
    assert 'gpio_library' in details
    
    print(f"test_gpio() result:")
    print(json.dumps(result, indent=2))
    
    print("✅ TEST PASSED: test_gpio() returns correct structure")
    return True


def test_no_exceptions_on_non_rpi():
    """Test that no exceptions are raised on non-Raspberry Pi systems"""
    print("\n" + "="*60)
    print("TEST 6: No Exceptions on Non-RPi Systems")
    print("="*60)
    
    try:
        from utils.gpio_control import LightController, test_gpio
        
        # Should not raise exception
        controller = LightController()
        controller.test_red()
        controller.test_green()
        controller.turn_off_red()
        controller.turn_off_green()
        controller.all_off()
        
        test_gpio()
        
        print("✅ TEST PASSED: No exceptions raised on non-RPi system")
        return True
    except Exception as e:
        print(f"❌ TEST FAILED: Exception raised: {e}")
        raise


def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("GPIO DETECTION & MOCK GPIO - TEST SUITE")
    print("="*70)
    
    tests = [
        ("GPIO Detection Logic", test_gpio_detection),
        ("Mock LED Functionality", test_mock_led),
        ("LightController Creation", test_light_controller_creation),
        ("LightController Methods", test_light_controller_methods),
        ("test_gpio() Function", test_gpio_function),
        ("No Exceptions on Non-RPi", test_no_exceptions_on_non_rpi),
    ]
    
    passed = 0
    failed = 0
    
    for name, test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            failed += 1
            print(f"\n❌ TEST FAILED: {name}")
            print(f"   Error: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "="*70)
    print(f"TEST RESULTS: {passed} passed, {failed} failed")
    print("="*70)
    
    if failed > 0:
        print(f"❌ {failed} TEST(S) FAILED")
        sys.exit(1)
    else:
        print("✅ ALL TESTS PASSED!")
        sys.exit(0)


if __name__ == '__main__':
    main()

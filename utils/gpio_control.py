"""
utils/gpio_control.py - GPIO Controller
ควบคุมไฟ LED ผ่าน GPIO (Raspberry Pi)
"""

import platform

# ตรวจสอบว่าเป็น Raspberry Pi หรือไม่
IS_RASPBERRY_PI = platform. machine().startswith('arm') or platform.machine().startswith('aarch')

if IS_RASPBERRY_PI: 
    try:
        from gpiozero import LED
        GPIO_AVAILABLE = True
    except ImportError: 
        GPIO_AVAILABLE = False
        print("⚠️ gpiozero not installed.  Run: pip install gpiozero")
else:
    GPIO_AVAILABLE = False
    print("⚠️ Not running on Raspberry Pi - GPIO disabled")


# ========================================
# Class: LightController
# ========================================
class LightController:
    """ควบคุมไฟ Red/Green LED"""
    
    def __init__(self, red_pin=17, green_pin=27):
        self.red_pin = red_pin
        self.green_pin = green_pin
        
        if GPIO_AVAILABLE:
            self. red_light = LED(red_pin)
            self.green_light = LED(green_pin)
        else:
            self.red_light = None
            self.green_light = None
    
    def test_red(self):
        """ทดสอบไฟแดง"""
        if not GPIO_AVAILABLE:
            return {"success": False, "message": "⚠️ GPIO not available"}
        
        try: 
            self.red_light.on()
            return {"success": True, "message":  "🔴 Red light ON", "state": "on"}
        except Exception as e: 
            return {"success": False, "message": str(e)}
    
    def test_green(self):
        """ทดสอบไฟเขียว"""
        if not GPIO_AVAILABLE:
            return {"success": False, "message":  "⚠️ GPIO not available"}
        
        try: 
            self.green_light. on()
            return {"success":  True, "message": "🟢 Green light ON", "state": "on"}
        except Exception as e:
            return {"success": False, "message": str(e)}
    
    def turn_off_red(self):
        """ปิดไฟแดง"""
        if GPIO_AVAILABLE:
            self. red_light.off()
            return {"success": True, "state": "off"}
        return {"success": False}
    
    def turn_off_green(self):
        """ปิดไฟเขียว"""
        if GPIO_AVAILABLE:
            self.green_light.off()
            return {"success": True, "state": "off"}
        return {"success": False}
    
    def all_off(self):
        """ปิดทุกไฟ"""
        if GPIO_AVAILABLE:
            self.red_light.off()
            self.green_light. off()
            return {"success":  True, "message": "All lights OFF"}
        return {"success": False}


# ========================================
# ฟังก์ชัน Standalone (ใช้นอก class)
# ========================================
def test_gpio():
    """ทดสอบ GPIO ว่าพร้อมใช้งานหรือไม่"""
    if not GPIO_AVAILABLE:
        return {
            "success": False,
            "message": "⚠️ GPIO not available (not Raspberry Pi or gpiozero not installed)"
        }
    
    return {
        "success": True,
        "message": "✅ GPIO ready",
        "details": {
            "platform": platform.machine(),
            "gpio_library": "gpiozero"
        }
    }
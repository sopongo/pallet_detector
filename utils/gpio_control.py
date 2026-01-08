"""
utils/gpio_control.py - GPIO Controller
ควบคุมไฟ LED ผ่าน GPIO (Raspberry Pi)

รองรับ:
- Raspberry Pi: ใช้ GPIO จริงผ่าน gpiozero
- Windows/Mac/Linux อื่นๆ: ใช้ Mock GPIO (log output)
"""

import platform
import os


# ========================================
# Mock GPIO Classes
# ========================================
class MockLED:
    """
    Mock LED class สำหรับระบบที่ไม่มี GPIO (Windows/Mac/Linux อื่นๆ)
    มี API เหมือน gpiozero.LED แต่ใช้ logging แทนการควบคุม GPIO จริง
    """
    
    def __init__(self, pin, name="LED"):
        """
        สร้าง Mock LED
        
        Args:
            pin (int): Pin number (สำหรับแสดงใน log)
            name (str): ชื่อ LED (เช่น "Red", "Green")
        """
        self.pin = pin
        self.name = name
        self.is_on = False
        print(f"🔧 Mock LED initialized on pin {pin} ({name})")
    
    def on(self):
        """เปิด LED (mock - แสดง log)"""
        self.is_on = True
        print(f"💡 Mock LED {self.name} (pin {self.pin}) → ON")
    
    def off(self):
        """ปิด LED (mock - แสดง log)"""
        self.is_on = False
        print(f"⚫ Mock LED {self.name} (pin {self.pin}) → OFF")


# ========================================
# Raspberry Pi Detection
# ========================================
def is_raspberry_pi():
    """
    ตรวจสอบว่าระบบปัจจุบันเป็น Raspberry Pi หรือไม่
    
    วิธีการตรวจสอบ:
    1. ตรวจสอบว่าเป็น Linux ก่อน (Windows/Mac จะ return False ทันที)
    2. ตรวจสอบไฟล์ /proc/device-tree/model เพื่อยืนยันว่าเป็น Raspberry Pi
    
    Returns:
        tuple: (bool, str) - (is_rpi, device_model)
            - is_rpi: True ถ้าเป็น Raspberry Pi, False ถ้าไม่ใช่
            - device_model: ชื่อ model ของอุปกรณ์
    """
    # ✅ ตรวจสอบว่าเป็น Linux ก่อน (Windows/Mac จะไม่ผ่าน)
    if platform.system() != "Linux":
        return False, f"{platform.system()} ({platform.machine()})"
    
    # ✅ ตรวจสอบไฟล์ /proc/device-tree/model (มีเฉพาะ Raspberry Pi)
    device_model_path = "/proc/device-tree/model"
    if os.path.exists(device_model_path):
        try:
            with open(device_model_path, 'r') as f:
                model = f.read().strip('\x00').strip()
                # ตรวจสอบว่ามีคำว่า "raspberry pi" ในชื่อ model
                # รองรับ Pi Zero, Pi 1, 2, 3, 4, 5
                if "raspberry pi" in model.lower():
                    return True, model
        except Exception:
            pass
    
    # ถ้าไม่มีไฟล์หรืออ่านไม่ได้ → ไม่ใช่ Raspberry Pi
    return False, f"Linux ({platform.machine()})"


# ========================================
# GPIO Initialization
# ========================================
def detect_gpio():
    """
    ตรวจสอบและตั้งค่า GPIO
    
    Returns:
        tuple: (IS_RASPBERRY_PI, GPIO_AVAILABLE, LED_class, device_model)
            - IS_RASPBERRY_PI: bool - เป็น Raspberry Pi หรือไม่
            - GPIO_AVAILABLE: bool - GPIO พร้อมใช้งานหรือไม่
            - LED_class: class - Real LED หรือ Mock LED class
            - device_model: str - ชื่อ model ของอุปกรณ์
    """
    IS_RPI, device_model = is_raspberry_pi()
    
    if IS_RPI:
        # ✅ เป็น Raspberry Pi → พยายามโหลด gpiozero
        try:
            # พยายาม import gpiozero
            from gpiozero import LED as RealLED
            print(f"✅ Running on Raspberry Pi (Model: {device_model})")
            print("✅ GPIO enabled (gpiozero)")
            return True, True, RealLED, device_model
            
        except ImportError:
            # Raspberry Pi แต่ไม่มี gpiozero → ใช้ Mock
            print(f"⚠️ Running on Raspberry Pi but gpiozero not installed")
            print("⚠️ Using Mock GPIO - Run: pip install gpiozero")
            return True, False, MockLED, device_model
    else:
        # ✅ ไม่ใช่ Raspberry Pi (Windows/Mac/Linux อื่นๆ) → ใช้ Mock
        system = platform.system()
        print(f"⚠️ Not running on Raspberry Pi ({system})")
        print("⚠️ GPIO disabled - using Mock Mode")
        return False, False, MockLED, device_model


# เรียก detect_gpio() ครั้งเดียวตอน import module
IS_RASPBERRY_PI, GPIO_AVAILABLE, LED, DEVICE_MODEL = detect_gpio()


# ========================================
# Class: LightController
# ========================================
class LightController:
    """
    ควบคุมไฟ Red/Green LED
    
    รองรับทั้ง:
    - Real GPIO (Raspberry Pi with gpiozero)
    - Mock GPIO (Windows/Mac/Linux อื่นๆ - แสดง log แทน)
    
    API เหมือนเดิมทุกอย่าง - ไม่มี breaking changes
    """
    
    def __init__(self, red_pin=17, green_pin=27):
        """
        สร้าง LightController
        
        Args:
            red_pin (int): GPIO pin สำหรับไฟแดง (default: 17)
            green_pin (int): GPIO pin สำหรับไฟเขียว (default: 27)
        """
        self.red_pin = red_pin
        self.green_pin = green_pin
        
        # ✅ สร้าง LED objects (Real หรือ Mock ขึ้นกับระบบ)
        # Real LED (gpiozero) ไม่รับ name parameter
        # Mock LED รับ name parameter เพื่อแสดงใน log
        if GPIO_AVAILABLE:
            self.red_light = LED(red_pin)
            self.green_light = LED(green_pin)
        else:
            self.red_light = LED(red_pin, name="Red")
            self.green_light = LED(green_pin, name="Green")
        
        # Log การตั้งค่า
        if GPIO_AVAILABLE:
            print(f"✅ GPIO initialized: Red={red_pin}, Green={green_pin}")
        else:
            print(f"⚠️ Mock GPIO initialized: Red={red_pin}, Green={green_pin}")
    
    def test_red(self):
        """
        ทดสอบไฟแดง (เปิด)
        
        Returns:
            dict: {"success": bool, "message": str, "state": str}
        """
        try: 
            self.red_light.on()
            return {
                "success": True, 
                "message": "🔴 Red light ON", 
                "state": "on",
                "mode": "real" if GPIO_AVAILABLE else "mock"
            }
        except Exception as e: 
            return {"success": False, "message": str(e)}
    
    def test_green(self):
        """
        ทดสอบไฟเขียว (เปิด)
        
        Returns:
            dict: {"success": bool, "message": str, "state": str}
        """
        try: 
            self.green_light.on()
            return {
                "success": True, 
                "message": "🟢 Green light ON", 
                "state": "on",
                "mode": "real" if GPIO_AVAILABLE else "mock"
            }
        except Exception as e:
            return {"success": False, "message": str(e)}
    
    def turn_off_red(self):
        """
        ปิดไฟแดง
        
        Returns:
            dict: {"success": bool, "state": str}
        """
        try:
            self.red_light.off()
            return {"success": True, "state": "off"}
        except Exception as e:
            return {"success": False, "message": str(e)}
    
    def turn_off_green(self):
        """
        ปิดไฟเขียว
        
        Returns:
            dict: {"success": bool, "state": str}
        """
        try:
            self.green_light.off()
            return {"success": True, "state": "off"}
        except Exception as e:
            return {"success": False, "message": str(e)}
    
    def all_off(self):
        """
        ปิดทุกไฟ
        
        Returns:
            dict: {"success": bool, "message": str}
        """
        try:
            self.red_light.off()
            self.green_light.off()
            return {"success": True, "message": "All lights OFF"}
        except Exception as e:
            return {"success": False, "message": str(e)}


# ========================================
# ฟังก์ชัน Standalone (ใช้นอก class)
# ========================================
def test_gpio():
    """
    ทดสอบ GPIO ว่าพร้อมใช้งานหรือไม่
    
    Returns:
        dict: ข้อมูลสถานะ GPIO
            - success: bool - GPIO พร้อมใช้งานหรือไม่
            - message: str - ข้อความสถานะ
            - details: dict - รายละเอียดเพิ่มเติม
    """
    if not IS_RASPBERRY_PI:
        return {
            "success": False,
            "message": f"⚠️ Not running on Raspberry Pi - GPIO disabled (using Mock Mode)",
            "details": {
                "is_raspberry_pi": False,
                "device": DEVICE_MODEL,
                "gpio_mode": "mock",
                "gpio_library": None
            }
        }
    
    if not GPIO_AVAILABLE:
        return {
            "success": False,
            "message": "⚠️ Running on Raspberry Pi but gpiozero not installed",
            "details": {
                "is_raspberry_pi": True,
                "device": DEVICE_MODEL,
                "gpio_mode": "mock",
                "gpio_library": None,
                "install_command": "pip install gpiozero"
            }
        }
    
    return {
        "success": True,
        "message": "✅ GPIO ready",
        "details": {
            "is_raspberry_pi": True,
            "device": DEVICE_MODEL,
            "gpio_mode": "real",
            "gpio_library": "gpiozero"
        }
    }
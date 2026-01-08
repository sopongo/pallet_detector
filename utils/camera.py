"""
utils/camera.py - Camera Tester
ทดสอบการเชื่อมต่อกล้อง USB/Pi Camera
รองรับ: USB Webcam, Raspberry Pi Camera v1/v2/v3
"""

import cv2
import os
import time
import logging
from typing import Optional, Tuple

# ตั้งค่า logger
logger = logging.getLogger(__name__)


def test_camera(camera_index):
    """
    ทดสอบกล้อง (รองรับทั้ง USB และ Pi Camera)
    
    Args: 
        camera_index (int/str): index ของกล้องหรือ 'picamera'
        
    Returns:
        dict: result
    """
    try:
        logger.info(f"🔍 Testing camera: {camera_index}")
        
        # ใช้ CameraWrapper (รองรับทั้ง USB และ Pi Camera)
        camera = CameraWrapper(camera_index, width=640, height=480)
        
        if not camera.is_opened():
            return {
                "success": False,
                "message": f"❌ Cannot open camera {camera_index}"
            }
        
        # อ่านภาพทดสอบ
        ret, frame = camera.read()
        
        # ปิดกล้อง
        camera.release()
        
        if not ret or frame is None:
            return {
                "success": False,
                "message": "❌ Cannot capture image from camera"
            }
        
        # ดึงขนาดรูป
        height, width = frame.shape[:2]
        
        return {
            "success": True,
            "message": f"✅ Camera {camera_index} is working! ({camera.camera_type})",
            "details": {
                "resolution": f"{width}x{height}",
                "camera_index": camera_index,
                "camera_type": camera.camera_type
            }
        }
        
    except Exception as e:
        logger.error(f"Camera test error: {e}")
        return {
            "success": False,
            "message": f"❌ Camera test failed: {str(e)}"
        }


def detect_cameras():
    """
    หากล้องที่เชื่อมต่ออยู่ทั้งหมด (USB 0-5 + Pi Camera)
    Returns:
        list: [0, 1, 2, ... ] กล้องที่ใช้ได้ + ['picamera'] ถ้ามี Pi Camera
    """
    available = []
    
    # 1. ตรวจสอบ USB cameras (0-5)
    for i in range(6):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            available.append(i)
            cap.release()
    
    # 2. ตรวจสอบ Pi Camera (picamera2)
    try:
        from picamera2 import Picamera2
        # ลองสร้าง object ทดสอบ
        cam = Picamera2()
        cam.close()
        available.append('picamera')
        logger.info("✅ Picamera2 detected")
    except ImportError:
        pass
    except Exception as e:
        logger.debug(f"Picamera2 detection error: {e}")
    
    return available


def capture_test_image(camera_index, save_path="/tmp/test_capture.jpg"):
    """
    ถ่ายรูปทดสอบ
    Returns:
        dict: result with image path
    """
    try: 
        cap = cv2.VideoCapture(int(camera_index))
        ret, frame = cap.read()
        cap.release()
        
        if ret:
            cv2.imwrite(save_path, frame)
            return {
                "success": True,
                "message": "✅ Image captured",
                "image_path": save_path
            }
        else:
            return {"success": False, "message": "❌ Capture failed"}
    
    except Exception as e:
        return {"success": False, "message": str(e)}


# ========================================
# New Camera Enhancement Features
# ========================================

def detect_camera_type(camera_index):
    """
    ตรวจจับประเภทกล้อง
    
    Args:
        camera_index (int/str): Camera index หรือ path
        
    Returns:
        str: 'usb', 'picamera2', 'unknown'
    """
    logger.info(f"🔍 Detecting camera type for index {camera_index}...")
    
    # 1. ถ้าเป็น string "picamera" หรือ "pi" -> ลอง picamera2
    if isinstance(camera_index, str) and camera_index.lower() in ['picamera', 'pi', 'picamera2']:
        try:
            from picamera2 import Picamera2
            # ลองสร้าง object ทดสอบ
            cam = Picamera2()
            cam.close()
            logger.info("✅ Picamera2 library detected and working")
            return 'picamera2'
        except ImportError:
            logger.warning("⚠️ Picamera2 library not installed")
            return 'unknown'
        except Exception as e:
            logger.warning(f"⚠️ Picamera2 error: {e}")
            return 'unknown'
    
    # 2. เช็คว่ามี picamera2 library และมี camera module หรือไม่
    try:
        from picamera2 import Picamera2
        # เช็คว่ามี Pi Camera module ติดตั้งอยู่หรือไม่
        if os.path.exists('/sys/class/video4linux/'):
            # ลองหา camera ที่เป็น Pi Camera (มักจะเป็น video0 บน Raspberry Pi)
            video_devices = os.listdir('/sys/class/video4linux/')
            for device in video_devices:
                device_path = f'/sys/class/video4linux/{device}/name'
                if os.path.exists(device_path):
                    with open(device_path, 'r') as f:
                        device_name = f.read().strip().lower()
                        # เช็คว่าเป็น Pi Camera หรือไม่
                        if 'unicam' in device_name or 'picamera' in device_name or 'rp1-cfe' in device_name:
                            logger.info(f"✅ Raspberry Pi Camera detected: {device_name}")
                            return 'picamera2'
    except ImportError:
        pass
    except Exception as e:
        logger.debug(f"Pi Camera detection error: {e}")
    
    # 3. ตรวจสอบว่าเป็น USB camera หรือไม่
    try:
        if isinstance(camera_index, int) or (isinstance(camera_index, str) and camera_index.isdigit()):
            index = int(camera_index)
            # ลองเปิด USB camera
            cap = cv2.VideoCapture(index)
            if cap.isOpened():
                cap.release()
                logger.info(f"✅ USB Camera detected at index {index}")
                return 'usb'
    except Exception as e:
        logger.debug(f"USB camera detection error: {e}")
    
    logger.warning(f"⚠️ Unknown camera type for index {camera_index}")
    return 'unknown'


class CameraWrapper:
    """
    Camera wrapper รองรับทั้ง OpenCV และ picamera2
    
    Attributes:
        camera_index: Camera index หรือ path
        camera_type: 'usb' หรือ 'picamera2'
        camera: OpenCV VideoCapture หรือ Picamera2 object
    """
    
    def __init__(self, camera_index, width=640, height=480):
        """
        Initialize camera wrapper
        
        Args:
            camera_index: Camera index (int) หรือ 'picamera'
            width: ความกว้างภาพ
            height: ความสูงภาพ
        """
        self.camera_index = camera_index
        self.width = width
        self.height = height
        self.camera = None
        self.camera_type = None
        self._is_opened = False
        
        # Auto-detect camera type
        self.camera_type = detect_camera_type(camera_index)
        
        # Initialize appropriate camera object
        if self.camera_type == 'picamera2':
            self._init_picamera2()
        elif self.camera_type == 'usb':
            self._init_opencv()
        else:
            # Fallback to OpenCV
            logger.warning("⚠️ Unknown camera type, trying OpenCV...")
            self._init_opencv()
    
    def _init_picamera2(self):
        """Initialize Picamera2"""
        try:
            from picamera2 import Picamera2
            logger.info("📸 Initializing Picamera2...")
            
            self.camera = Picamera2()
            
            # Configure camera
            config = self.camera.create_preview_configuration(
                main={"size": (self.width, self.height), "format": "RGB888"}
            )
            self.camera.configure(config)
            self.camera.start()
            
            self._is_opened = True
            self.camera_type = 'picamera2'
            logger.info(f"✅ Picamera2 initialized ({self.width}x{self.height})")
            
        except Exception as e:
            logger.error(f"❌ Picamera2 init failed: {e}")
            logger.info("🔄 Falling back to OpenCV...")
            self._init_opencv()
    
    def _init_opencv(self):
        """Initialize OpenCV VideoCapture"""
        try:
            if isinstance(self.camera_index, str) and not self.camera_index.isdigit():
                # ถ้าเป็น string ที่ไม่ใช่ตัวเลข -> ไม่สามารถใช้ OpenCV ได้
                logger.error(f"❌ Invalid camera index for OpenCV: {self.camera_index}")
                self._is_opened = False
                return
            
            camera_index = int(self.camera_index)
            logger.info(f"📸 Initializing OpenCV camera {camera_index}...")
            
            # บน Windows ใช้ CAP_DSHOW
            if os.name == 'nt':
                self.camera = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)
            else:
                self.camera = cv2.VideoCapture(camera_index)
            
            if self.camera.isOpened():
                # ตั้งค่าความละเอียด
                self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
                self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)
                
                self._is_opened = True
                self.camera_type = 'usb'
                logger.info(f"✅ OpenCV camera initialized ({self.width}x{self.height})")
            else:
                logger.error(f"❌ Cannot open camera {camera_index}")
                self._is_opened = False
                
        except Exception as e:
            logger.error(f"❌ OpenCV init failed: {e}")
            self._is_opened = False
    
    def is_opened(self):
        """ตรวจสอบว่ากล้องเปิดอยู่หรือไม่"""
        return self._is_opened
    
    def read(self):
        """
        อ่านภาพ (API เดียวกันทั้ง OpenCV และ picamera2)
        
        Returns:
            tuple: (ret, frame) เหมือน OpenCV
        """
        if not self._is_opened:
            return False, None
        
        try:
            if self.camera_type == 'picamera2':
                # Picamera2 API
                frame = self.camera.capture_array()
                # แปลง RGB -> BGR สำหรับความเข้ากันได้กับ OpenCV
                import numpy as np
                frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                return True, frame_bgr
            else:
                # OpenCV API
                return self.camera.read()
                
        except Exception as e:
            logger.error(f"❌ Camera read error: {e}")
            return False, None
    
    def release(self):
        """ปิดกล้อง"""
        try:
            if self.camera is not None:
                if self.camera_type == 'picamera2':
                    self.camera.stop()
                    self.camera.close()
                else:
                    self.camera.release()
                
                logger.info(f"✅ Camera released ({self.camera_type})")
                self._is_opened = False
                
        except Exception as e:
            logger.error(f"❌ Camera release error: {e}")


class RobustCamera:
    """
    Camera with auto-reconnect capability
    
    Features:
        - Auto-retry on connection failure (3 attempts)
        - Timeout handling (5 seconds)
        - Auto-reconnect on read failure
    """
    
    def __init__(self, camera_index, max_retries=3, timeout=5, width=640, height=480):
        """
        Initialize robust camera
        
        Args:
            camera_index: Camera index หรือ 'picamera'
            max_retries: จำนวนครั้งที่จะลองใหม่
            timeout: Timeout สำหรับแต่ละครั้ง (วินาที)
            width: ความกว้างภาพ
            height: ความสูงภาพ
        """
        self.camera_index = camera_index
        self.max_retries = max_retries
        self.timeout = timeout
        self.width = width
        self.height = height
        self.camera = None
        self.camera_type = None
        self._failed_reads = 0
        self._max_failed_reads = 5  # จำนวนครั้งที่อ่านไม่สำเร็จก่อน reconnect
        
        # เชื่อมต่อกล้อง
        self.connect()
    
    def connect(self):
        """เชื่อมต่อกล้อง (พร้อม retry)"""
        for attempt in range(1, self.max_retries + 1):
            try:
                logger.info(f"🔌 Connecting to camera (attempt {attempt}/{self.max_retries})...")
                
                self.camera = CameraWrapper(
                    self.camera_index,
                    width=self.width,
                    height=self.height
                )
                
                if self.camera.is_opened():
                    self.camera_type = self.camera.camera_type
                    logger.info(f"✅ Camera connected successfully (type: {self.camera_type})")
                    self._failed_reads = 0
                    return True
                else:
                    logger.warning(f"⚠️ Connection attempt {attempt} failed")
                    
            except Exception as e:
                logger.error(f"❌ Connection error (attempt {attempt}): {e}")
            
            # รอก่อนลองใหม่
            if attempt < self.max_retries:
                wait_time = min(attempt * 2, self.timeout)
                logger.info(f"⏳ Waiting {wait_time} seconds before retry...")
                time.sleep(wait_time)
        
        logger.error(f"❌ Failed to connect after {self.max_retries} attempts")
        return False
    
    def is_opened(self):
        """ตรวจสอบว่ากล้องเปิดอยู่หรือไม่"""
        return self.camera is not None and self.camera.is_opened()
    
    def read(self):
        """
        อ่านภาพ (auto-reconnect ถ้า fail)
        
        Returns:
            tuple: (ret, frame)
        """
        if not self.is_opened():
            logger.warning("⚠️ Camera not opened, attempting to connect...")
            if not self.connect():
                return False, None
        
        try:
            ret, frame = self.camera.read()
            
            if ret:
                # อ่านสำเร็จ -> reset failed counter
                self._failed_reads = 0
                return True, frame
            else:
                # อ่านไม่สำเร็จ
                self._failed_reads += 1
                logger.warning(f"⚠️ Camera read failed (count: {self._failed_reads}/{self._max_failed_reads})")
                
                # ถ้าอ่านไม่สำเร็จหลายครั้ง -> reconnect
                if self._failed_reads >= self._max_failed_reads:
                    logger.warning("⚠️ Too many failed reads, reconnecting...")
                    self.reconnect()
                
                return False, None
                
        except Exception as e:
            logger.error(f"❌ Camera read exception: {e}")
            self._failed_reads += 1
            
            if self._failed_reads >= self._max_failed_reads:
                self.reconnect()
            
            return False, None
    
    def reconnect(self):
        """Reconnect กล้อง"""
        logger.info("🔄 Reconnecting camera...")
        
        # ปิดกล้องเก่า
        if self.camera is not None:
            try:
                self.camera.release()
            except Exception as e:
                logger.error(f"Error releasing camera: {e}")
            self.camera = None
        
        # เชื่อมต่อใหม่
        time.sleep(1)  # รอก่อนเชื่อมต่อใหม่
        success = self.connect()
        
        if success:
            logger.info("✅ Camera reconnected successfully")
        else:
            logger.error("❌ Camera reconnection failed")
        
        return success
    
    def release(self):
        """ปิดกล้อง"""
        if self.camera is not None:
            self.camera.release()
            self.camera = None
            logger.info("✅ Robust camera released")
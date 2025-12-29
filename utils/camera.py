"""
utils/camera.py - Camera Tester
ทดสอบการเชื่อมต่อกล้อง USB/Pi Camera
"""

import cv2
import os


def test_camera(camera_index=0):
    """
    ทดสอบกล้อง
    Args:
        camera_index (int/str): 0, 1, 2 หรือ 'rtsp://...'
    Returns:
        dict: result with success status
    """
    try: 
        # แปลง index เป็น int ถ้าเป็นตัวเลข
        if str(camera_index).isdigit():
            camera_index = int(camera_index)
        
        # เปิดกล้อง
        cap = cv2.VideoCapture(camera_index)
        
        if not cap.isOpened():
            return {
                "success": False,
                "message": f"❌ Cannot open camera {camera_index}"
            }
        
        # อ่าน 1 frame ทดสอบ
        ret, frame = cap.read()
        cap.release()
        
        if not ret:
            return {
                "success": False,
                "message": "❌ Camera opened but cannot read frame"
            }
        
        return {
            "success": True,
            "message": "✅ Camera working! ",
            "details": {
                "resolution": f"{frame.shape[1]}x{frame.shape[0]}",
                "camera_index": camera_index
            }
        }
    
    except Exception as e: 
        return {
            "success":  False,
            "message": f"❌ Camera error: {str(e)}"
        }


def detect_cameras():
    """
    หากล้องที่เชื่อมต่ออยู่ทั้งหมด (USB 0-5)
    Returns:
        list: [0, 1, 2, ... ] กล้องที่ใช้ได้
    """
    available = []
    for i in range(6):  # ตรวจสอบ 0-5
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            available.append(i)
            cap.release()
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
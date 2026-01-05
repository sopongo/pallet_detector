"""
utils/detector.py - YOLOv8 Pallet Detector
ตรวจจับพาเลทด้วย YOLOv8
"""

import cv2
import os
from ultralytics import YOLO
from datetime import datetime
import config
from utils.logger import setup_logger

logger = setup_logger()

class PalletDetector:  
    """Class สำหรับ detect พาเลทด้วย YOLO"""
    
    def __init__(self):
        """Initialize detector"""
        self.cfg = config.load_config()
        self.model_path = self. cfg['detection']['modelPath']
        self.confidence = self.cfg['detection']['confidenceThreshold']
        self.iou = self.cfg['detection']['iouThreshold']
        self.img_size = self.cfg['detection']['imageSize']
        self.device = self.cfg['detection']['deviceMode']
        
        # โหลด YOLO model
        try:
            self.model = YOLO(self.model_path)
            logger.info(f"✅ YOLOv8 model loaded:   {self.model_path}")
            
            # ✅ แสดง class names
            logger.info(f"📋 Model classes: {self. model.names}")
            
        except Exception as e:
            logger.error(f"❌ Cannot load YOLO model: {e}")
            raise
    
    def detect_pallets(self, image_path):
        """
        ตรวจจับพาเลทในรูป
        
        Args: 
            image_path (str): path ของรูปที่จะ detect
            
        Returns:  
            dict:  {
                'count': int,
                'pallets': [
                    {
                        'bbox': [x1, y1, x2, y2],
                        'center': [cx, cy],
                        'confidence': float,
                        'class_name': str
                    }
                ],
                'image_path':  str,
                'annotated_image': numpy.ndarray
            }
        """
        try:
            # อ่านรูป
            image = cv2.imread(image_path)
            if image is None:
                logger. error(f"Cannot read image:  {image_path}")
                return None
            
            # ✅ กำหนด class ที่ต้องการ (ถ้ารู้ class ID)
            # ถ้าไม่รู้ ให้รันดู log ก่อน
            PALLET_CLASSES = None  # หรือ [0] ถ้ารู้ว่า pallet เป็น class 0
            
            # Run detection
            results = self.model.predict(
                source=image,
                conf=self.confidence,
                iou=self. iou,
                imgsz=self.img_size,
                device=self.device,
                classes=PALLET_CLASSES,  # ✅ กรอง class
                verbose=False
            )
            
            # ✅ ดึง class names
            class_names = self.model.names
            
            # Parse results
            pallets = []
            for result in results:
                boxes = result.boxes
                for box in boxes:
                    # ดึง class ID
                    class_id = int(box.cls[0])
                    class_name = class_names[class_id]
                    
                    # ✅ กรองเฉพาะ pallet
                    if 'pallet' not in class_name. lower():
                        logger.warning(f"Filtered out: {class_name}")
                        continue
                    
                    # Bounding box coordinates
                    x1, y1, x2, y2 = box.xyxy[0]. cpu().numpy()
                    
                    # Center point
                    cx = (x1 + x2) / 2
                    cy = (y1 + y2) / 2
                    
                    # Confidence
                    conf = float(box.conf[0])
                    
                    pallets.append({
                        'bbox': [int(x1), int(y1), int(x2), int(y2)],
                        'center': [float(cx), float(cy)],
                        'confidence': conf,
                        'class_name':  class_name
                    })
            
            # Annotated image (วาดกรอบ)
            annotated_image = results[0].plot()
            
            logger.info(f"Detected {len(pallets)} pallet(s) in {os.path.basename(image_path)}")
            
            return {
                'count':   len(pallets),
                'pallets': pallets,
                'image_path': image_path,
                'annotated_image': annotated_image
            }
            
        except Exception as e:
            logger.error(f"Detection error: {e}")
            return None
    
    def save_annotated_image(self, annotated_image, original_path):
        """
        บันทึกรูปที่วาดกรอบแล้ว
        
        Args:
            annotated_image:   รูปที่วาดกรอบแล้ว
            original_path:  path รูปต้นฉบับ
            
        Returns:
            str:   path ของรูปที่บันทึก
        """
        try:  
            # สร้าง path ใหม่ (เพิ่ม _detected)
            dir_name = os.path.dirname(original_path)
            file_name = os.path.basename(original_path)
            name, ext = os.path.splitext(file_name)
            new_path = os.path.join(dir_name, f"{name}_detected{ext}")
            
            # บันทึกรูป
            cv2.imwrite(new_path, annotated_image)
            logger.info(f"Saved annotated image:   {new_path}")
            
            return new_path
            
        except Exception as e: 
            logger.error(f"Cannot save annotated image: {e}")
            return None
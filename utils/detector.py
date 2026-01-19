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
from shapely.geometry import Polygon, box as shapely_box

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
        ตรวจจับพาเลทและคนในรูป (Multi-class detection)
        
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
                        'class_name': str,
                        'class_type': str  # 'pallet' or 'person'
                    }
                ],
                'image_path':  str,
                'original_image': numpy.ndarray
            }
        """
        try:
            # อ่านรูป
            image = cv2.imread(image_path)
            if image is None:
                logger.error(f"Cannot read image: {image_path}")
                return None
            
            # Run detection (ไม่กรอง class ให้ detect ทุกอย่าง)
            results = self.model.predict(
                source=image,
                conf=self.confidence,
                iou=self.iou,
                imgsz=self.img_size,
                device=self.device,
                classes=None,  # ✅ ตรวจจับทุก class
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
                    
                    # ✅ กรองเฉพาะ pallet และ person (case-insensitive)
                    class_name_lower = class_name.lower()
                    if 'pallet' in class_name_lower:
                        class_type = 'pallet'
                    elif 'person' in class_name_lower:
                        class_type = 'person'
                    else:
                        logger.debug(f"Filtered out: {class_name}")
                        continue
                    
                    # Bounding box coordinates
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    
                    # Center point
                    cx = (x1 + x2) / 2
                    cy = (y1 + y2) / 2
                    
                    # Confidence
                    conf = float(box.conf[0])
                    
                    pallets.append({
                        'bbox': [int(x1), int(y1), int(x2), int(y2)],
                        'center': [float(cx), float(cy)],
                        'confidence': conf,
                        'class_name': class_name,
                        'class_type': class_type  # ✅ เพิ่ม class_type
                    })
            
            logger.info(f"Detected {len(pallets)} object(s) in {os.path.basename(image_path)}")
            
            return {
                'count':   len(pallets),
                'pallets': pallets,
                'image_path': image_path,
                'original_image': image  # ✅ คืนรูปต้นฉบับแทน annotated
            }
            
        except Exception as e:
            logger.error(f"Detection error: {e}")
            return None
    
    def save_annotated_image(self, original_image, pallets, original_path, db_manager):
        """
        วาดกรอบและ label แบบกำหนดเอง พร้อมเรียงลำดับ
        
        Args:
            original_image: รูปต้นฉบับ
            pallets: list ของ detection results (จะถูก modified in-place)
            original_path:  path รูปต้นฉบับ
            db_manager: DatabaseManager instance สำหรับ query pallet_no
            
        Returns:
            str: path ของรูปที่บันทึก
        """
        try:
            # คัดลอกรูปเพื่อวาดกรอบ
            annotated = original_image.copy()
            
            # ✅ เรียงลำดับ: top-to-bottom (y), left-to-right (x)
            sorted_pallets = sorted(pallets, key=lambda p: (p['center'][1], p['center'][0]))
            
            # ✅ Query เลข pallet_no ล่าสุด
            latest_no = db_manager.get_latest_pallet_no()
            next_no = latest_no + 1
            
            # ✅ Prefix สำหรับแต่ละ class
            PALLET_PREFIX = "PL-"
            PERSON_PREFIX = "PE-"
            
            # ✅ กำหนดสี (BGR format)
            COLOR_PALLET = (0, 255, 0)   # เขียว
            COLOR_PERSON = (255, 0, 0)   # น้ำเงิน
            
            # วาดกรอบและ label
            for pallet in sorted_pallets:
                class_type = pallet['class_type']
                bbox = pallet['bbox']
                confidence = pallet['confidence']
                
                # กำหนด prefix และสี
                if class_type == 'pallet':
                    prefix = PALLET_PREFIX
                    color = COLOR_PALLET
                elif class_type == 'person':
                    prefix = PERSON_PREFIX
                    color = COLOR_PERSON
                else:
                    continue
                
                # ✅ ใช้เลขเก่าถ้าเป็นพาเลทเดิม, สร้างใหม่ถ้าเป็นพาเลทใหม่
                if pallet.get('is_existing', False):
                    # ใช้เลขเก่า
                    pallet_no = pallet.get('pallet_no', next_no)
                    pallet_name = pallet.get('pallet_name', f"{prefix}{next_no:04d}")
                else:
                    # สร้างเลขใหม่
                    pallet_name = f"{prefix}{next_no:04d}"
                    pallet['pallet_no'] = next_no
                    pallet['pallet_name'] = pallet_name
                    next_no += 1
                    
                    # ✅ อัปเดตข้อมูลกลับไปที่ pallets ต้นฉบับ (เพื่อให้บันทึกลง database ได้)
                    for orig_pallet in pallets:
                        # หาตัวเดียวกันโดยเทียบ center และ bbox
                        if (orig_pallet.get('center') == pallet['center'] and 
                            orig_pallet.get('bbox') == pallet['bbox']):
                            orig_pallet['pallet_no'] = pallet['pallet_no']
                            orig_pallet['pallet_name'] = pallet['pallet_name']
                            logger.debug(f"✅ Updated original pallet: {pallet['pallet_name']}")
                            break
                
                # วาดกรอบ
                x1, y1, x2, y2 = bbox
                cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 2)
                
                # สร้าง label text
                label = f"{pallet_name} ({confidence*100:.1f}%)"
                
                # คำนวณขนาด text
                font = cv2.FONT_HERSHEY_SIMPLEX
                font_scale = 0.6
                thickness = 2
                (text_width, text_height), baseline = cv2.getTextSize(
                    label, font, font_scale, thickness
                )
                
                # วาดพื้นหลัง label
                cv2.rectangle(
                    annotated,
                    (x1, y1 - text_height - baseline - 10),
                    (x1 + text_width + 10, y1),
                    color,
                    -1
                )
                
                # วาด text
                cv2.putText(
                    annotated,
                    label,
                    (x1 + 5, y1 - baseline - 5),
                    font,
                    font_scale,
                    (255, 255, 255),  # สีขาว
                    thickness
                )
            
            # สร้าง path ใหม่ (เพิ่ม _detected)
            dir_name = os.path.dirname(original_path)
            file_name = os.path.basename(original_path)
            name, ext = os.path.splitext(file_name)
            new_path = os.path.join(dir_name, f"{name}_detected{ext}")
            
            # บันทึกรูป
            cv2.imwrite(new_path, annotated)
            logger.info(f"Saved annotated image:   {new_path}")
            
            return new_path
            
        except Exception as e: 
            logger.error(f"Cannot save annotated image: {e}")
            return None
    
    def calculate_bbox_overlap(self, bbox, zone_points, image_width, image_height):
        """
        คำนวณ % ของ bbox ที่อยู่ใน zone
        
        Args:
            bbox: [x1, y1, x2, y2] pixel coordinates
            zone_points: [[x1, y1], [x2, y2], ...] normalized (0.0-1.0)
            image_width, image_height: ขนาดรูป
            
        Returns:
            float: % overlap (0.0-1.0)
        """
        try:
            # แปลง bbox เป็น Polygon
            bbox_poly = shapely_box(bbox[0], bbox[1], bbox[2], bbox[3])
            
            # แปลง zone points (normalized 0.0-1.0) → pixel
            pixel_points = [
                (p[0] * image_width, p[1] * image_height)
                for p in zone_points
            ]
            zone_poly = Polygon(pixel_points)
            
            # คำนวณ intersection area
            if not bbox_poly.intersects(zone_poly):
                return 0.0
            
            intersection = bbox_poly.intersection(zone_poly)
            overlap_ratio = intersection.area / bbox_poly.area
            
            return overlap_ratio
            
        except Exception as e:
            logger.error(f"Error calculating overlap: {e}")
            return 0.0
    
    def filter_by_zones(self, detections, zones, image_width, image_height, threshold=0.5):
        """
        กรอง detections โดยเช็คว่า bbox อยู่ใน zone > threshold %
        
        Args:
            detections: list of detection dicts
            zones: list of zone dicts with 'points' (normalized 0.0-1.0)
            image_width, image_height: ขนาดรูป
            threshold: % ขั้นต่ำที่ต้องอยู่ใน zone (default 0.5 = 50%)
            
        Returns:
            list: filtered detections with 'zone_id', 'zone_name', 'zone_threshold'
        """
        if not zones:
            logger.debug("No zones configured, returning all detections")
            return detections
        
        filtered = []
        
        for detection in detections:
            bbox = detection['bbox']
            best_zone = None
            best_overlap = 0.0
            
            # หา zone ที่ overlap มากที่สุด
            for zone in zones:
                if not zone.get('enabled', True):
                    continue
                
                overlap = self.calculate_bbox_overlap(
                    bbox, 
                    zone['points'], 
                    image_width, 
                    image_height
                )
                
                if overlap > best_overlap:
                    best_overlap = overlap
                    best_zone = zone
            
            # ถ้า overlap >= threshold → เพิ่มเข้า filtered
            if best_zone and best_overlap >= threshold:
                detection['zone_id'] = best_zone['id']
                detection['zone_name'] = best_zone['name']
                detection['zone_threshold'] = best_zone.get('alertThreshold', 30)
                detection['overlap_ratio'] = round(best_overlap * 100, 1)
                filtered.append(detection)
                
                logger.debug(
                    f"Detection bbox={bbox} → Zone '{best_zone['name']}' "
                    f"(overlap: {best_overlap*100:.1f}%)"
                )
            else:
                logger.debug(
                    f"Detection bbox={bbox} → Outside zones "
                    f"(best overlap: {best_overlap*100:.1f}%)"
                )
        
        logger.info(f"🗺️ Filtered: {len(filtered)}/{len(detections)} detections in zones")
        
        return filtered
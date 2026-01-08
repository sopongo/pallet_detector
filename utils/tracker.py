"""
utils/tracker.py - Pallet Tracker
ติดตามพาเลทด้วย position-based tracking
"""

import pymysql
from datetime import datetime, timedelta
import math
import config
from utils.logger import setup_logger

logger = setup_logger()

class PalletTracker:
    """Class สำหรับติดตามพาเลท"""
    
    def __init__(self):
        """Initialize tracker"""
        self.cfg = config.load_config()
        self.db_config = {
            'host': self.cfg['network']['database']['host'],
            'user': self.cfg['network']['database']['user'],
            'password': self.cfg['network']['database']['password'],
            'database': self.cfg['network']['database']['database'],
            'port': self.cfg['network']['database']['port']
        }
        self.alert_threshold = self.cfg['detection']['alertThreshold']  # นาที
        # ✅ ลบ fixed distance_threshold - จะคำนวณแบบ dynamic แทน
    
    def get_db_connection(self):
        """สร้าง database connection"""
        return pymysql.connect(**self.db_config, cursorclass=pymysql.cursors.DictCursor)
    
    def calculate_distance(self, pos1, pos2):
        """
        คำนวณระยะห่างระหว่าง 2 จุด
        
        Args:
            pos1: [x1, y1]
            pos2: [x2, y2]
            
        Returns:
            float: ระยะห่าง (pixels)
        """
        return math.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)
    
    def get_active_pallets(self):
        """
        ดึงพาเลทที่ active อยู่ (is_active=1)
        
        Returns: 
            list: [{'id_pallet': .. ., 'pos_x': .. ., 'pos_y': .. ., ... }]
        """
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM tb_pallet
                WHERE is_active = 1
                ORDER BY first_detected_at DESC
            """)
            
            pallets = cursor.fetchall()
            cursor.close()
            conn.close()
            
            return pallets
            
        except Exception as e: 
            logger.error(f"Error getting active pallets: {e}")
            return []
    
    def find_matching_pallet(self, new_center, active_pallets, image_width, image_height):
        """
        หาพาเลทที่ตรงกับตำแหน่งใหม่ (Position-based matching ± อ้างอิงไฟล์ config ตัวแปร alignmentTolerance)
        
        Args:
            new_center:  [cx, cy] ของพาเลทใหม่
            active_pallets: list ของพาเลท active
            image_width: ความกว้างของภาพ (pixels)
            image_height: ความสูงของภาพ (pixels)
            
        Returns:
            dict or None: พาเลทที่ตรงกัน หรือ None
        """
        # ✅ คำนวณ threshold แบบ dynamic (±% ของขนาดภาพเพื่อรองรับการเคลื่อนไหวเล็กน้อย อ้างอิงไฟล์ config ตัวแปร alignmentTolerance)
        threshold_x = image_width * (self.cfg['detection']['alignmentTolerance'] / 100)
        threshold_y = image_height * (self.cfg['detection']['alignmentTolerance'] / 100)
        
        logger.debug(f"Position tolerance: ±{threshold_x:.1f}px (X), ±{threshold_y:.1f}px (Y)")
        
        best_match = None
        min_distance = float('inf')
        
        for pallet in active_pallets:
            old_center = [float(pallet['pos_x']), float(pallet['pos_y'])]
            
            # ✅ เช็คตำแหน่งว่าอยู่ใน tolerance หรือไม่
            dx = abs(new_center[0] - old_center[0])
            dy = abs(new_center[1] - old_center[1])
            
            if dx <= threshold_x and dy <= threshold_y:
                # คำนวณระยะห่างจริงเพื่อหา best match
                distance = self.calculate_distance(new_center, old_center)
                if distance < min_distance:
                    min_distance = distance
                    best_match = pallet
                    logger.debug(f"  → Match candidate: Pallet #{pallet['id_pallet']} (distance: {distance:.1f}px)")
        
        if best_match:
            logger.info(f"✅ Matched: New pos {new_center} → Pallet #{best_match['id_pallet']} (distance: {min_distance:.1f}px)")
        else:
            logger.info(f"❌ No match found for position {new_center} (threshold: ±{threshold_x:.1f}px, ±{threshold_y:.1f}px)")
        
        return best_match
    
    def update_pallet(self, pallet_id, detection_time):
        """
        อัพเดทพาเลทที่เจออีกครั้ง
        
        Args:
            pallet_id: ID ของพาเลท
            detection_time: เวลาที่เจอ
            
        Returns:
            dict: {
                'pallet_id': int,
                'duration': float (minutes),
                'status': int (0=normal, 1=overtime, 2=removed)
            }
        """
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            # ดึงข้อมูลปัจจุบัน
            cursor.execute("SELECT * FROM tb_pallet WHERE id_pallet = %s", (pallet_id,))
            pallet = cursor.fetchone()
            
            if not pallet:
                logger.error(f"❌ Pallet #{pallet_id} not found in database")
                return None
            
            # คำนวณระยะเวลาที่ค้าง (นาที)
            first_time = pallet['first_detected_at']
            duration = (detection_time - first_time).total_seconds() / 60
            
            # ✅ เพิ่ม: Log ค่า threshold และ duration
            logger.debug(f"⏱️ Pallet #{pallet_id}: duration={duration:.2f}m, threshold={self.alert_threshold:.2f}m")
            
            # ตรวจสอบว่าเกิน threshold หรือไม่
            new_status = 0  # Normal
            over_time = None
            in_over = 0
            
            if duration > self.alert_threshold:
                new_status = 1  # Overtime
                in_over = 1
                if pallet['over_time'] is None:
                    over_time = detection_time
                # ✅ เพิ่ม: Log overtime detection
                logger.warning(f"🔴 Pallet #{pallet_id} OVERTIME: {duration:.2f}m > {self.alert_threshold:.2f}m")
            else:
                # ✅ เพิ่ม: Log normal status
                logger.debug(f"🟢 Pallet #{pallet_id} OK: {duration:.2f}m <= {self.alert_threshold:.2f}m")
            
            # อัพเดท
            cursor.execute("""
                UPDATE tb_pallet
                SET last_detected_at = %s,
                    detector_count = detector_count + 1,
                    status = %s,
                    in_over = %s,
                    over_time = COALESCE(over_time, %s)
                WHERE id_pallet = %s
            """, (detection_time, new_status, in_over, over_time, pallet_id))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            # ✅ สำคัญ: Log return value พร้อม status
            logger.info(f"✅ Updated pallet #{pallet_id} (duration: {duration:.1f} min, status: {new_status})")
            
            # ✅ สร้าง result object และ log ก่อน return
            result = {
                'pallet_id': pallet_id,
                'duration': duration,
                'status': new_status
            }
            logger.debug(f"📤 Returning: {result}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Error updating pallet #{pallet_id}: {e}", exc_info=True)
            return None
    
    def create_new_pallet(self, ref_id_img, pallet_data, detection_time, pallet_no, pallet_name):
        """
        สร้างพาเลทใหม่
        
        Args:
            ref_id_img: ID ของรูป
            pallet_data: {'bbox': [... ], 'center': [...], 'confidence': ...}
            detection_time: เวลาที่เจอ
            pallet_no: เลขลำดับพาเลท (INT)
            pallet_name: ชื่อพาเลท (VARCHAR เช่น "PL-0001")
            
        Returns:
            int: ID ของพาเลทที่สร้าง
        """
        try: 
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            bbox = pallet_data['bbox']
            center = pallet_data['center']
            confidence = pallet_data['confidence']
            
            cursor.execute("""
                INSERT INTO tb_pallet (
                    pallet_no, pallet_name, ref_id_img, pos_x, pos_y,
                    bbox_x1, bbox_y1, bbox_x2, bbox_y2,
                    accuracy, pallet_date_in, first_detected_at, last_detected_at,
                    is_active, status, detector_count
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 1, 0, 1)
            """, (
                pallet_no, pallet_name, ref_id_img, center[0], center[1],
                bbox[0], bbox[1], bbox[2], bbox[3],
                confidence, detection_time, detection_time, detection_time
            ))
            
            pallet_id = cursor.lastrowid
            conn.commit()
            cursor.close()
            conn.close()
            
            logger.info(f"Created new pallet #{pallet_id} ({pallet_name})")
            
            return pallet_id
            
        except Exception as e: 
            logger.error(f"Error creating pallet: {e}")
            return None
    
    def deactivate_missing_pallets(self, current_pallet_ids, ref_id_img):
        """
        ปิดสถานะพาเลทที่ไม่เจอในรูปปัจจุบัน
        
        Args:
            current_pallet_ids: list ของ ID พาเลทที่เจอในรูปนี้
            ref_id_img: ID ของรูปปัจจุบัน
        """
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            if current_pallet_ids:
                placeholders = ','.join(['%s'] * len(current_pallet_ids))
                cursor.execute(f"""
                    UPDATE tb_pallet
                    SET is_active = 0, status = 2
                    WHERE is_active = 1
                    AND id_pallet NOT IN ({placeholders})
                """, current_pallet_ids)
            else:
                cursor.execute("""
                    UPDATE tb_pallet
                    SET is_active = 0, status = 2
                    WHERE is_active = 1
                """)
            
            affected = cursor.rowcount
            conn.commit()
            cursor.close()
            conn.close()
            
            if affected > 0:
                logger.info(f"Deactivated {affected} pallet(s) (moved)")
            
        except Exception as e:
            logger.error(f"Error deactivating pallets: {e}")
    
    def find_recently_deactivated_pallet(self, new_center, image_width, image_height, minutes=5):
        """
        หาพาเลทที่ถูก deactivate ไปไม่นาน ที่ตำแหน่งใกล้เคียง
        ใช้สำหรับตรวจสอบว่าพาเลทใหม่อาจเป็นพาเลทเดิมที่หายไปชั่วคราว
        
        Args:
            new_center: [cx, cy] ของตำแหน่งใหม่
            image_width: ความกว้างภาพ (pixels)
            image_height: ความสูงภาพ (pixels)
            minutes: ช่วงเวลาย้อนหลัง (นาที) - default 5 นาที
            
        Returns:
            dict or None: พาเลทที่เคย deactivate หรือ None
        """
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            # ✅ Query พาเลทที่ถูก deactivate ไม่เกิน X นาที และคำนวณระยะเวลารวม
            cursor.execute("""
                SELECT 
                    id_pallet,
                    pallet_no,
                    pallet_name,
                    pos_x,
                    pos_y,
                    TIMESTAMPDIFF(MINUTE, first_detected_at, last_detected_at) as total_duration,
                    last_detected_at,
                    in_over
                FROM tb_pallet
                WHERE is_active = 0
                  AND status = 2
                  AND last_detected_at >= DATE_SUB(NOW(), INTERVAL %s MINUTE)
                ORDER BY last_detected_at DESC
            """, (minutes,))
            
            recent_pallets = cursor.fetchall()
            cursor.close()
            conn.close()
            
            if not recent_pallets:
                return None
            
            # ✅ หาว่าตรงกับตำแหน่งใหม่หรือไม่ (ใช้ threshold เดียวกับ find_matching_pallet)
            threshold_x = image_width * (self.cfg['detection']['alignmentTolerance'] / 100)
            threshold_y = image_height * (self.cfg['detection']['alignmentTolerance'] / 100)
            
            for pallet in recent_pallets:
                old_center = [float(pallet['pos_x']), float(pallet['pos_y'])]
                dx = abs(new_center[0] - old_center[0])
                dy = abs(new_center[1] - old_center[1])
                
                if dx <= threshold_x and dy <= threshold_y:
                    logger.info(f"🔍 Found recently deactivated pallet: #{pallet['id_pallet']} ({pallet['pallet_name']}) - duration: {pallet['total_duration']:.1f} min")
                    return pallet
            
            return None
            
        except Exception as e:
            logger.error(f"Error finding recently deactivated pallet: {e}")
            return None
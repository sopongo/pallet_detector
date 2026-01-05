"""
detection_service.py - Main Detection Service
Background service สำหรับ detection loop
"""

import os
import time
import cv2
from datetime import datetime, timedelta
import signal
import sys
import config
from utils. logger import setup_logger
from utils.detector import PalletDetector
from utils. tracker import PalletTracker
from utils.database import DatabaseManager
from utils.line_messaging import LineMessagingAPI
from utils.gpio_control import LightController

logger = setup_logger()

class DetectionService:
    """Main detection service"""
    
    def __init__(self):
        """Initialize detection service"""
        self.running = False
        self.cfg = config.load_config()
        
        # Initialize components
        try:
            self.detector = PalletDetector()
            self.tracker = PalletTracker()
            self.db = DatabaseManager()
            self.line = LineMessagingAPI()
            self.lights = LightController(
                red_pin=self.cfg['gpio']['redLightPin'],
                green_pin=self.cfg['gpio']['greenLightPin']
            )
            
            logger.info("✅ Detection service initialized")
            
        except Exception as e:
            logger.error(f"❌ Initialization failed: {e}")
            raise
    
    def is_within_operating_hours(self):
        """ตรวจสอบว่าอยู่ในช่วงเวลาทำงานหรือไม่"""
        now = datetime.now()
        current_time = now.time()
        
        start_time = datetime.strptime(self.cfg['detection']['operatingHours']['start'], '%H:%M').time()
        end_time = datetime.strptime(self. cfg['detection']['operatingHours']['end'], '%H:%M').time()
        
        return start_time <= current_time <= end_time
    
    def capture_image(self):
        """ถ่ายรูปจากกล้อง"""
        camera = None
        try:
            camera_index = int(self.cfg['camera']['selectedCamera'])
            
            # เปิดกล้อง
            camera = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)
            
            if not camera.isOpened():
                logger.error(f"Cannot open camera {camera_index}")
                return None
            
            # ตั้งค่าความละเอียด
            camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            
            # รอให้กล้องพร้อม
            time.sleep(0.5)
            
            # อ่านภาพหลายครั้ง (ทิ้ง frame แรกๆ)
            for _ in range(3):
                camera.read()
            
            # อ่านภาพจริง
            ret, frame = camera. read()
            
            if not ret or frame is None:
                logger. error("Cannot capture image")
                return None
            
            # สร้าง path
            base_path = self.cfg['general']['imagePath']
            
            # แปลงเป็น absolute path
            if not os.path.isabs(base_path):
                base_path = os. path.abspath(base_path)
            
            # สร้างโฟลเดอร์ตามวันที่
            date_folder = datetime.now().strftime('%Y-%m-%d')
            full_path = os.path.join(base_path, date_folder)
            os.makedirs(full_path, exist_ok=True)
            
            # ชื่อไฟล์
            filename = datetime.now().strftime('IMG_%Y%m%d_%H%M%S.jpg')
            filepath = os. path. join(full_path, filename)
            
            # บันทึกรูป
            success = cv2.imwrite(filepath, frame)
            
            if not success:
                logger.error(f"Cannot save image:  {filepath}")
                return None
            
            logger.info(f"📸 Captured:  {filepath}")
            return filepath
            
        except Exception as e: 
            logger.error(f"Capture error: {e}")
            return None
        
        finally:
            # ปิดกล้องเสมอ
            if camera is not None:
                camera.release()
    
    def process_detection(self, image_path):
        """ประมวลผล detection และ tracking"""
        try:
            # 1. Detect pallets
            detection_result = self.detector.detect_pallets(image_path)
            
            if not detection_result:
                logger.warning("Detection failed")
                return None
            
            # 2. Save image record
            image_data = {
                'image_date': datetime.now(),
                'image_name': os.path.basename(image_path),
                'pallet_detected': detection_result['count'],
                'site':  int(self.cfg['general']['siteCompany']),
                'location': int(self.cfg['general']['siteLocation'])
            }
            
            ref_id_img = self.db.save_image_record(image_data)
            
            if not ref_id_img: 
                logger.error("Cannot save image record")
                return None
            
            # 3. Track pallets
            active_pallets = self.tracker. get_active_pallets()
            detected_pallets = detection_result['pallets']
            current_pallet_ids = []
            overtime_pallets = []
            
            for pallet_data in detected_pallets:
                center = pallet_data['center']
                
                # หาว่าตรงกับพาเลทเก่าหรือไม่
                matching_pallet = self.tracker.find_matching_pallet(center, active_pallets)
                
                if matching_pallet: 
                    # อัพเดทพาเลทเดิม
                    result = self.tracker.update_pallet(
                        matching_pallet['id_pallet'],
                        datetime.now()
                    )
                    
                    if result and result['status'] == 1:  # Overtime
                        overtime_pallets. append({
                            'pallet_id': result['pallet_id'],
                            'duration': result['duration'],
                            'site': image_data['site'],
                            'location': image_data['location']
                        })
                    
                    current_pallet_ids.append(matching_pallet['id_pallet'])
                else:
                    # สร้างพาเลทใหม่
                    new_id = self.tracker.create_new_pallet(
                        ref_id_img,
                        pallet_data,
                        datetime.now()
                    )
                    if new_id:
                        current_pallet_ids.append(new_id)
            
            # 4. Deactivate missing pallets
            self.tracker.deactivate_missing_pallets(current_pallet_ids, ref_id_img)
            
            # 5. บันทึกรูปที่วาดกรอบ
            annotated_path = self.detector.save_annotated_image(
                detection_result['annotated_image'],
                image_path
            )
            
            return {
                'ref_id_img': ref_id_img,
                'detected_count': detection_result['count'],
                'overtime_pallets': overtime_pallets,
                'annotated_path': annotated_path
            }
            
        except Exception as e:
            logger.error(f"Process detection error: {e}")
            return None
    
    def handle_alerts(self, overtime_pallets, annotated_path):
        """จัดการ alerts (LINE + GPIO)"""
        try:
            if overtime_pallets:
                # เปิดไฟแดง
                self.lights.test_red()
                
                # ส่ง LINE alert
                for pallet in overtime_pallets:
                    result = self.line.send_overtime_alert(pallet, None)
                    
                    # บันทึก log
                    self.db.save_notification_log({
                        'ref_id_pallet': pallet['pallet_id'],
                        'notify_type': 'LINE',
                        'message': f"Overtime alert: {pallet['duration']:. 1f} min",
                        'sent_at': datetime.now(),
                        'success': result['success']
                    })
                    
                    # อัพเดทจำนวนครั้งแจ้งเตือน
                    if result['success']:
                        self.db.increment_notify_count(pallet['pallet_id'])
                
                logger.warning(f"⚠️ Sent {len(overtime_pallets)} overtime alert(s)")
            else:
                # เปิดไฟเขียว
                self.lights. test_green()
                
        except Exception as e:
            logger.error(f"Alert handling error: {e}")
    
    def run_detection_cycle(self):
        """รันวงจร detection 1 รอบ"""
        try: 
            logger.info("🔄 Starting detection cycle...")
            
            # 1. ถ่ายรูป
            image_path = self.capture_image()
            if not image_path:
                return
            
            # 2. ประมวลผล
            result = self.process_detection(image_path)
            if not result:
                return
            
            # 3. จัดการ alerts
            self.handle_alerts(result['overtime_pallets'], result['annotated_path'])
            
            logger.info(f"✅ Cycle completed:  {result['detected_count']} pallet(s) detected")
            
        except Exception as e: 
            logger.error(f"Detection cycle error: {e}")
    
    def start(self):
        """เริ่มต้น detection service"""
        logger.info("🚀 Starting Pallet Detection Service...")
        self.running = True
        
        interval = self.cfg['detection']['captureInterval']
        
        while self.running:
            try:
                # ตรวจสอบว่าอยู่ในช่วงเวลาทำงานหรือไม่
                if self.is_within_operating_hours():
                    self.run_detection_cycle()
                else: 
                    logger.info("⏸️ Outside operating hours, waiting...")
                    self.lights.all_off()
                
                # รอตาม interval
                logger.info(f"💤 Sleeping for {interval} seconds...")
                time.sleep(interval)
                
            except KeyboardInterrupt:
                logger.info("⚠️ Keyboard interrupt received")
                break
            except Exception as e: 
                logger.error(f"Main loop error: {e}")
                time.sleep(10)
        
        self.stop()
    
    def stop(self):
        """หยุด detection service"""
        logger.info("🛑 Stopping detection service...")
        self.running = False
        self.lights.all_off()
        logger.info("✅ Detection service stopped")


# ========================================
# Signal Handler (นอก class)
# ========================================
def signal_handler(sig, frame):
    """Handle shutdown signals"""
    global service
    logger.info(f"Received signal {sig}")
    if service:
        service.stop()
    sys.exit(0)


# ========================================
# Main
# ========================================
if __name__ == '__main__':
    # สร้าง logs folder
    os.makedirs('logs', exist_ok=True)
    
    # สร้าง service (global variable)
    service = None
    
    try:
        service = DetectionService()
        
        # Register signal handlers
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # เริ่มต้น service
        service.start()
        
    except KeyboardInterrupt:
        logger. info("⚠️ Keyboard interrupt")
        if service:
            service.stop()
    except Exception as e: 
        logger.error(f"Fatal error: {e}")
        if service:
            service.stop()
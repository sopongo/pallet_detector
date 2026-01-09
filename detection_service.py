"""
detection_service.py - Main Detection Service
Background service สำหรับ detection loop
"""

import os
import time
import cv2
import json
from datetime import datetime, timedelta
import signal
import sys
import config
from utils.logger import setup_logger
from utils.detector import PalletDetector
from utils.tracker import PalletTracker
from utils.database import DatabaseManager
from utils.line_messaging import LineMessagingAPI
from utils.gpio_control import LightController
from utils.camera import RobustCamera
from utils.image_uploader import ImageUploader

logger = setup_logger()

class DetectionService:
    """Main detection service"""
    
    def __init__(self):
        """Initialize detection service"""
        self.running = False
        self.cfg = config.load_config()
        
        # ✅ โหลด sites.json ครั้งเดียวตอน init (แทนที่จะอ่านทุกครั้งที่เรียก method)
        self._sites_data = None
        try:
            sites_file = os.path.join(os.path.dirname(__file__), 'config', 'sites.json')
            if os.path.exists(sites_file):
                with open(sites_file, 'r', encoding='utf-8') as f:
                    self._sites_data = json.load(f)
                    logger.info(f"✅ Loaded sites data: {len(self._sites_data)} site(s)")
        except Exception as e:
            logger.error(f"Error loading sites.json: {e}")
            self._sites_data = {}
        
        # Initialize components
        try:
            self.detector = PalletDetector()
            self.tracker = PalletTracker()
            self.db = DatabaseManager()
            self.line = LineMessagingAPI()
            self.uploader = ImageUploader()
            
            # ✅ Initialize RobustCamera
            camera_index = self.cfg['camera']['selectedCamera']
            # แปลง camera_index เป็น int ถ้าเป็นตัวเลข
            if isinstance(camera_index, str) and camera_index.isdigit():
                camera_index = int(camera_index)
            
            logger.info(f"🎥 Initializing camera: {camera_index}")
            self.camera = None  # จะถูกสร้างตอนต้องใช้งาน (lazy initialization)
            self.camera_index = camera_index
            
            # ✅ ตรวจสอบ LINE config
            line_token = self.cfg['network']['lineNotify'].get('token', '')
            line_group = self.cfg['network']['lineNotify'].get('groupId', '')
            
            if not line_token or line_token == 'NULL':
                logger.warning("⚠️ LINE token not configured - alerts will NOT be sent!")
            else:
                logger.info(f"✅ LINE token configured: {line_token[:20]}...")
            
            if not line_group or line_group == 'NULL':
                logger.warning("⚠️ LINE group ID not configured - alerts will NOT be sent!")
            else:
                logger.info(f"✅ LINE group ID configured: {line_group[:10]}...")
            
            self.lights = LightController(
                red_pin=self.cfg['gpio']['redLightPin'],
                green_pin=self.cfg['gpio']['greenLightPin']
            )
            
            logger.info("✅ Detection service initialized")
            
        except Exception as e:
            logger.error(f"❌ Initialization failed: {e}")
            raise
    
    def get_site_name(self, site_id):
        """
        แปลง site ID เป็นชื่อ
        
        Args:
            site_id (int): Site ID (1, 2, 3...)
            
        Returns:
            str: Site name (e.g., "PCS", "PACT")
        """
        try:
            if self._sites_data:
                site_info = self._sites_data.get(str(site_id), {})
                return site_info.get('site_name', f'Site {site_id}')
        except Exception as e:
            logger.error(f"Error getting site name: {e}")
        
        # Fallback: ใช้ ID
        return f'Site {site_id}'
    
    def get_location_name(self, site_id, location_id):
        """
        แปลง location ID เป็นชื่อ
        
        Args:
            site_id (int): Site ID
            location_id (int): Location ID
            
        Returns:
            str: Location name (e.g., "Building 1")
        """
        try:
            if self._sites_data:
                site_info = self._sites_data.get(str(site_id), {})
                locations = site_info.get('location', {})
                return locations.get(str(location_id), f'Location {location_id}')
        except Exception as e:
            logger.error(f"Error getting location name: {e}")
        
        # Fallback: ใช้ ID
        return f'Location {location_id}'
    
    def generate_image_url(self, annotated_path):
        """
        สร้าง image URL จาก annotated_path
        
        Args:
            annotated_path (str): Path ของรูปภาพที่มี annotation
            
        Returns:
            str: Image URL หรือ empty string ถ้าสร้างไม่ได้
        """
        if not annotated_path:
            return ''
        
        try:
            base_path = self.cfg['general']['imagePath']
            if not os.path.isabs(base_path):
                base_path = os.path.abspath(base_path)
            
            image_rel_path = os.path.relpath(annotated_path, base_path)
            image_url = f"http://localhost/{os.path.basename(base_path)}/{image_rel_path.replace(os.sep, '/')}"
            return image_url
        except Exception as e:
            logger.warning(f"Cannot create image URL: {e}")
            return ''
    
    def is_within_operating_hours(self):
        """ตรวจสอบว่าอยู่ในช่วงเวลาทำงานหรือไม่"""
        now = datetime.now()
        current_time = now.time()
        
        start_time = datetime.strptime(self.cfg['detection']['operatingHours']['start'], '%H:%M').time()
        end_time = datetime.strptime(self.cfg['detection']['operatingHours']['end'], '%H:%M').time()
        
        return start_time <= current_time <= end_time
    
    def capture_image(self):
        """ถ่ายรูปจากกล้อง (ใช้ RobustCamera)"""
        try:
            # ✅ Lazy initialization - สร้าง camera ครั้งแรกที่ใช้งาน
            if self.camera is None:
                logger.info(f"📸 Creating RobustCamera for index: {self.camera_index}")
                self.camera = RobustCamera(
                    self.camera_index,
                    max_retries=3,
                    timeout=5,
                    width=640,
                    height=480
                )
                
                if self.camera.is_opened():
                    logger.info(f"✅ Camera initialized (type: {self.camera.camera_type})")
                else:
                    logger.error("❌ Camera initialization failed")
                    return None
            
            # ✅ ตรวจสอบว่ากล้องยังเปิดอยู่หรือไม่
            if not self.camera.is_opened():
                logger.warning("⚠️ Camera not opened, attempting reconnect...")
                if not self.camera.connect():
                    logger.error("❌ Cannot reconnect camera")
                    return None
            
            # รอให้กล้องพร้อม (สำหรับ USB camera)
            if self.camera.camera_type == 'usb':
                time.sleep(0.5)
                # อ่านภาพหลายครั้ง (ทิ้ง frame แรกๆ)
                for _ in range(3):
                    self.camera.read()
            
            # ✅ อ่านภาพจริง (with auto-reconnect)
            ret, frame = self.camera.read()
            
            if not ret or frame is None:
                logger.error("❌ Cannot capture image")
                return None
            
            # สร้าง path
            base_path = self.cfg['general']['imagePath']
            
            # แปลงเป็น absolute path
            if not os.path.isabs(base_path):
                base_path = os.path.abspath(base_path)
            
            # สร้างโฟลเดอร์ตามวันที่
            date_folder = datetime.now().strftime('%Y-%m-%d')
            full_path = os.path.join(base_path, date_folder)
            os.makedirs(full_path, exist_ok=True)
            
            # ชื่อไฟล์
            filename = datetime.now().strftime('IMG_%Y%m%d_%H%M%S.jpg')
            filepath = os.path.join(full_path, filename)
            
            # บันทึกรูป
            success = cv2.imwrite(filepath, frame)
            
            if not success:
                logger.error(f"❌ Cannot save image: {filepath}")
                return None
            
            logger.info(f"📸 Captured: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"❌ Capture error: {e}")
            return None
    
    def process_detection(self, image_path):
        """ประมวลผล detection และ tracking"""
        try:
            # 1. Detect pallets
            detection_result = self.detector.detect_pallets(image_path)
            
            if not detection_result:
                logger.warning("Detection failed")
                return None
            
            # ✅ ดึงขนาดภาพ
            original_image = detection_result['original_image']
            image_height, image_width = original_image.shape[:2]
            logger.info(f"Image dimensions: {image_width}x{image_height}")
            
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
            active_pallets = self.tracker.get_active_pallets()
            detected_pallets = detection_result['pallets']
            current_pallet_ids = []
            overtime_pallets = []
            
            # ✅ สำหรับพาเลทใหม่ที่จะสร้าง - รอเรียงลำดับก่อน
            new_pallets_to_create = []
            
            for pallet_data in detected_pallets:
                center = pallet_data['center']
                
                # ✅ หาว่าตรงกับพาเลทเก่าหรือไม่ (ส่ง image dimensions)
                matching_pallet = self.tracker.find_matching_pallet(
                    center, active_pallets, image_width, image_height
                )
                
                if matching_pallet: 
                    # อัพเดทพาเลทเดิม
                    result = self.tracker.update_pallet(
                        matching_pallet['id_pallet'],
                        datetime.now()
                    )
                    
                    # ตรวจสอบว่าพาเลท/person เกินเวลาหรือไม่
                    if result and result['status'] == 1:  # Status = 1 หมายถึง Overtime
                        overtime_pallets.append({
                            'pallet_id': result['pallet_id'],
                            'duration': result['duration'],
                            'site': image_data['site'],
                            'location': image_data['location'],
                            'image_url': ''  # ✅ จะถูกอัพเดทหลังจากมี annotated_path
                        })
                        logger.warning(f"⚠️ Overtime detected: Pallet #{result['pallet_id']} ({result['duration']:.1f} min)")
                    
                    current_pallet_ids.append(matching_pallet['id_pallet'])
                    # ✅ ใส่ข้อมูลเก่า
                    pallet_data['pallet_no'] = matching_pallet['pallet_no']
                    pallet_data['pallet_name'] = matching_pallet['pallet_name']
                    pallet_data['is_existing'] = True
                else:
                    # ✅ เก็บไว้สร้างทีหลัง
                    pallet_data['is_existing'] = False
                    new_pallets_to_create.append(pallet_data)
            
            # ✅ 4. วาดกรอบก่อน (เพื่อให้ได้ pallet_no/pallet_name)
            annotated_path = self.detector.save_annotated_image(
                original_image,
                detected_pallets,
                image_path,
                self.db
            )
            
            # ✅ 4.5. Upload รูปไป SSL server
            if annotated_path:
                logger.info("📤 Uploading image to SSL server...")
                upload_result = self.uploader.upload_image(annotated_path)
                
                if upload_result['success']:
                    logger.info(f"✅ Image uploaded: {upload_result['url']}")
                    image_url = upload_result['url']
                else:
                    logger.warning(f"⚠️ Upload failed, using default: {upload_result['message']}")
                    image_url = upload_result['url']  # default image
            else:
                logger.warning("⚠️ No annotated image, using default")
                image_url = self.uploader.default_image
            
            # ✅ อัพเดท image URL ให้กับ overtime_pallets ทั้งหมด
            if overtime_pallets:
                for pallet in overtime_pallets:
                    pallet['image_url'] = image_url
                logger.info(f"📷 Image URL added to {len(overtime_pallets)} overtime alert(s)")
            
            # ✅ 5. สร้างพาเลทใหม่ (หลังจากได้ pallet_no/name แล้ว)
            for pallet_data in new_pallets_to_create:
                # ✅ เช็คว่ามีพาเลทเก่าที่ตำแหน่งใกล้เคียงหรือไม่ (ภายใน 5 นาทีที่ผ่านมา)
                recently_deactivated = self.tracker.find_recently_deactivated_pallet(
                    pallet_data['center'],
                    image_width,
                    image_height,
                    minutes=5
                )
                
                if recently_deactivated:
                    logger.warning(f"⚠️ New pallet at same position as recently deactivated #{recently_deactivated['id_pallet']} ({recently_deactivated['pallet_name']})")
                    logger.warning(f"   Previous duration: {recently_deactivated['total_duration']:.1f} min")
                    
                    # ✅ ถ้าพาเลทเก่าเคย overtime (in_over=1) → แจ้งเตือนทันที
                    if recently_deactivated['in_over'] == 1 and recently_deactivated['total_duration'] > self.tracker.alert_threshold:
                        # ✅ ใช้ image URL ที่ upload แล้ว (ตัวแปร image_url ถูกสร้างข้างบนแล้ว)
                        
                        overtime_pallets.append({
                            'pallet_id': recently_deactivated['id_pallet'],
                            'duration': recently_deactivated['total_duration'],
                            'site': image_data['site'],
                            'location': image_data['location'],
                            'image_url': image_url  # ใช้ URL ที่ upload แล้ว
                        })
                        logger.warning(f"⚠️ Immediate alert: Position matches overtime pallet! (duration: {recently_deactivated['total_duration']:.1f} min)")
                
                # สร้างพาเลทใหม่
                new_id = self.tracker.create_new_pallet(
                    ref_id_img,
                    pallet_data,
                    datetime.now(),
                    pallet_data.get('pallet_no', 0),
                    pallet_data.get('pallet_name', '')
                )
                if new_id:
                    current_pallet_ids.append(new_id)
                    logger.info(f"✅ Created pallet: #{new_id} ({pallet_data.get('pallet_name', 'UNKNOWN')})")
            
            # 6. Deactivate missing pallets
            self.tracker.deactivate_missing_pallets(current_pallet_ids, ref_id_img)
            
            # ตรวจสอบ overtime เสร็จสิ้น
            logger.info(f"🔍 Overtime check complete: {len(overtime_pallets)} alert(s) pending")
            
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
            # ✅ Debug log แสดงข้อมูลที่ส่งเข้ามา
            logger.info(f"📢 Handling alerts: {len(overtime_pallets)} overtime pallet(s)")
            logger.debug(f"📋 Overtime pallets data: {overtime_pallets}")
            
            if overtime_pallets:
                # ✅ เพิ่ม: Try-except สำหรับ GPIO (อาจจะไม่มีในบางเครื่อง)
                try:
                    self.lights.test_red()
                    logger.debug("🔴 Red light turned on")
                except Exception as gpio_error:
                    logger.warning(f"⚠️ GPIO error (ignored): {gpio_error}")
                
                # ✅ Log ก่อนเข้า loop
                logger.info(f"🔄 Processing {len(overtime_pallets)} alert(s)...")
                
                # ส่ง LINE alert
                alert_count = 0
                for i, pallet in enumerate(overtime_pallets):
                    # ✅ Log แต่ละ pallet
                    logger.info(f"📤 Sending alert {i+1}/{len(overtime_pallets)}: Pallet #{pallet['pallet_id']} (duration: {pallet['duration']:.1f} min)")
                    
                    # ✅ แปลง site/location ID เป็น name
                    site_name = self.get_site_name(pallet.get('site', 0))
                    location_name = self.get_location_name(pallet.get('site', 0), pallet.get('location', 0))
                    
                    # ✅ สร้าง dict ใหม่พร้อม site/location names
                    alert_data = {
                        'pallet_id': pallet['pallet_id'],
                        'duration': pallet['duration'],
                        'site': site_name,           # ← ชื่อแทน ID
                        'location': location_name,   # ← ชื่อแทน ID
                        'image_url': pallet.get('image_url', ''),  # ← เพิ่ม (ถ้ามี)
                        'first_detected_at':  pallet.get('first_detected_at'),
                        'last_detected_at': datetime.now()  # หรือ pallet.get('last_detected_at')
                    }
                    
                    # ✅ Log ข้อมูลที่จะส่ง
                    logger.debug(f"   Alert data: {alert_data}")
                    
                    # ส่ง LINE alert
                    try:
                        result = self.line.send_overtime_alert(alert_data)
                        
                        # ✅ Log ผลลัพธ์
                        if result['success']:
                            logger.info(f"   ✅ LINE alert sent successfully")
                            alert_count += 1
                        else:
                            logger.error(f"   ❌ LINE alert failed: {result['message']}")
                        
                        # ✅ บันทึก log ลง database
                        self.db.save_notification_log({
                            'ref_id_pallet': pallet['pallet_id'],
                            'notify_type': 'LINE',
                            'message': f"Overtime alert: {pallet['duration']:.1f} min",
                            'sent_at': datetime.now(),
                            'success': result['success']
                        })
                        
                        # อัพเดทจำนวนครั้งแจ้งเตือน
                        if result['success']:
                            self.db.increment_notify_count(pallet['pallet_id'])
                            
                    except Exception as alert_error:
                        # ✅ Catch exception ของแต่ละ alert
                        logger.error(f"   ❌ Exception sending alert: {alert_error}", exc_info=True)
                
                logger.warning(f"⚠️ Sent {alert_count}/{len(overtime_pallets)} overtime alert(s)")
            else:
                # ✅ เพิ่ม: Try-except สำหรับ GPIO
                try:
                    self.lights.test_green()
                    logger.debug("🟢 Green light turned on")
                except Exception as gpio_error:
                    logger.warning(f"⚠️ GPIO error (ignored): {gpio_error}")
                
                logger.info("✅ No overtime pallets - all clear")
                
        except Exception as e:
            logger.error(f"❌ Alert handling error: {e}", exc_info=True)
    
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
        
        # ✅ ปิดกล้อง
        if hasattr(self, 'camera') and self.camera is not None:
            try:
                self.camera.release()
                logger.info("✅ Camera released")
            except Exception as e:
                logger.error(f"Error releasing camera: {e}")
        
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
        logger.info("⚠️ Keyboard interrupt")
        if service:
            service.stop()
    except Exception as e: 
        logger.error(f"Fatal error: {e}")
        if service:
            service.stop()
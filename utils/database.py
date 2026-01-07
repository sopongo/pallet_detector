"""
utils/database.py - Database Helper Functions
จัดการ database operations
"""

import pymysql
from pymysql import Error
from datetime import datetime
import config
from utils.logger import setup_logger

logger = setup_logger()

class DatabaseManager:
    """Class สำหรับจัดการ database"""
    
    def __init__(self):
        """Initialize database manager"""
        cfg = config.load_config()
        self.db_config = {
            'host': cfg['network']['database']['host'],
            'user': cfg['network']['database']['user'],
            'password': cfg['network']['database']['password'],
            'database': cfg['network']['database']['database'],
            'port': cfg['network']['database']['port']
        }
    
    def get_connection(self):
        """สร้าง database connection"""
        return pymysql.connect(**self. db_config, cursorclass=pymysql.cursors.DictCursor)
    
    def test_connection(self):
        """ทดสอบการเชื่อมต่อ database"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()
            cursor.close()
            conn.close()
            
            logger.info(f"✅ Database connected:  MySQL {version}")
            return {'success': True, 'version': version}
            
        except Error as e:
            logger. error(f"❌ Database connection failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def save_image_record(self, image_data):
        """
        บันทึกข้อมูลรูปลง tb_image
        
        Args: 
            image_data (dict): {
                'image_date': datetime,
                'image_name':  str,
                'pallet_detected': int,
                'site':  int,
                'location': int
            }
            
        Returns:
            int: id_img ที่สร้าง หรือ None
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO tb_image (image_date, image_name, pallet_detected, site, location)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                image_data['image_date'],
                image_data['image_name'],
                image_data['pallet_detected'],
                image_data['site'],
                image_data['location']
            ))
            
            id_img = cursor.lastrowid
            conn.commit()
            cursor.close()
            conn.close()
            
            logger.info(f"Saved image record #{id_img}:  {image_data['image_name']}")
            return id_img
            
        except Exception as e:
            logger.error(f"Error saving image record:  {e}")
            return None
    
    def get_pallets_need_alert(self, threshold_minutes):
        """
        ดึงพาเลทที่ต้องแจ้งเตือน (overtime + ยังไม่แจ้ง)
        
        Args: 
            threshold_minutes (int): เวลา threshold (นาที)
            
        Returns:
            list: รายการพาเลทที่ต้องแจ้งเตือน
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT p.*, i.site, i.location, i.image_name
                FROM tb_pallet p
                JOIN tb_image i ON p.ref_id_img = i.id_img
                WHERE p.is_active = 1
                AND p. status = 1
                AND TIMESTAMPDIFF(MINUTE, p.first_detected_at, p.last_detected_at) >= %s
                AND (p.notify_count = 0 OR TIMESTAMPDIFF(MINUTE, p.over_time, NOW()) >= 15)
                ORDER BY p.first_detected_at ASC
            """, (threshold_minutes,))
            
            pallets = cursor.fetchall()
            cursor.close()
            conn.close()
            
            return pallets
            
        except Exception as e:
            logger.error(f"Error getting pallets for alert: {e}")
            return []
    
    def increment_notify_count(self, pallet_id):
        """
        เพิ่มจำนวนครั้งที่แจ้งเตือน
        
        Args:
            pallet_id (int): ID พาเลท
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE tb_pallet
                SET notify_count = notify_count + 1
                WHERE id_pallet = %s
            """, (pallet_id,))
            
            conn.commit()
            cursor.close()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error incrementing notify count: {e}")
    
    def save_notification_log(self, notif_data):
        """
        บันทึก log การแจ้งเตือน
        
        Args: 
            notif_data (dict): {
                'ref_id_pallet': int,
                'notify_type': str,
                'message': str,
                'sent_at': datetime,
                'success': bool
            }
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO tb_notifications (ref_id_pallet, notify_type, message, sent_at, success)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                notif_data['ref_id_pallet'],
                notif_data['notify_type'],
                notif_data['message'],
                notif_data['sent_at'],
                notif_data['success']
            ))
            
            conn.commit()
            cursor.close()
            conn.close()
            
        except Exception as e: 
            logger.error(f"Error saving notification log: {e}")
    
    def get_latest_pallet_no(self, date=None):
        """
        ดึงเลข pallet_no ล่าสุดของวันนั้นๆ (สำหรับ auto-increment)
        
        Args:
            date (str): วันที่ในรูปแบบ 'YYYY-MM-DD' (ถ้าไม่ระบุใช้วันนี้)
            
        Returns:
            int: เลข pallet_no สูงสุด (เช่น 5 → ถัดไปจะเป็น 6) หรือ 0 ถ้ายังไม่มีข้อมูล
        """
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Query MAX(pallet_no) สำหรับวันที่กำหนด
            cursor.execute("""
                SELECT COALESCE(MAX(pallet_no), 0) as max_no
                FROM tb_pallet p
                JOIN tb_image i ON p.ref_id_img = i.id_img
                WHERE DATE(i.image_date) = %s
            """, (date,))
            
            result = cursor.fetchone()
            max_no = result['max_no'] if result else 0
            
            cursor.close()
            conn.close()
            
            return max_no
            
        except Exception as e:
            logger.error(f"Error getting latest pallet_no: {e}")
            return 0
    
    def get_daily_summary(self, date=None):
        """
        ดึงข้อมูลสรุปประจำวัน
        
        Args: 
            date (str): วันที่ในรูปแบบ 'YYYY-MM-DD' (ถ้าไม่ระบุใช้วันนี้)
            
        Returns:
            dict: ข้อมูลสรุป
        """
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # จำนวนรูปทั้งหมด
            cursor.execute("""
                SELECT COUNT(*) as total_photos
                FROM tb_image
                WHERE DATE(image_date) = %s
            """, (date,))
            total_photos = cursor. fetchone()['total_photos']
            
            # จำนวนพาเลททั้งหมด
            cursor.execute("""
                SELECT COUNT(*) as total_detected
                FROM tb_pallet p
                JOIN tb_image i ON p.ref_id_img = i.id_img
                WHERE DATE(i.image_date) = %s
            """, (date,))
            total_detected = cursor. fetchone()['total_detected']
            
            # จำนวนพาเลท in time
            cursor.execute("""
                SELECT COUNT(*) as in_time
                FROM tb_pallet p
                JOIN tb_image i ON p.ref_id_img = i.id_img
                WHERE DATE(i.image_date) = %s
                AND p.in_over = 0
            """, (date,))
            in_time = cursor. fetchone()['in_time']
            
            # จำนวนพาเลท over time
            cursor.execute("""
                SELECT COUNT(*) as over_time
                FROM tb_pallet p
                JOIN tb_image i ON p.ref_id_img = i.id_img
                WHERE DATE(i.image_date) = %s
                AND p.in_over = 1
            """, (date,))
            over_time = cursor.fetchone()['over_time']
            
            # จำนวน notifications
            cursor.execute("""
                SELECT COUNT(*) as notifications
                FROM tb_notifications
                WHERE DATE(sent_at) = %s
            """, (date,))
            notifications = cursor. fetchone()['notifications']
            
            cursor.close()
            conn.close()
            
            return {
                'date': date,
                'total_photos': total_photos,
                'total_detected': total_detected,
                'in_time':  in_time,
                'over_time': over_time,
                'notifications': notifications
            }
            
        except Exception as e:
            logger.error(f"Error getting daily summary: {e}")
            return {
                'date': date,
                'total_photos': 0,
                'total_detected':  0,
                'in_time': 0,
                'over_time': 0,
                'notifications': 0
            }


# ========================================
# Legacy Functions (backward compatible)
# ========================================

def test_database_connection(host, user, password, database, port=3306):
    """
    ทดสอบการเชื่อมต่อ MySQL (legacy function)
    """
    try:
        connection = pymysql.connect(
            host=host,
            user=user,
            password=password,
            database=database,
            port=int(port),
            connect_timeout=5
        )
        
        cursor = connection.cursor()
        cursor.execute("SELECT VERSION()")
        version = cursor.fetchone()[0]
        
        cursor.close()
        connection.close()
        
        return {
            "success": True,
            "message": "✅ Database connection successful! ",
            "details": {
                "host": host,
                "database": database,
                "version": version
            }
        }
    
    except Error as e:
        error_code = e.args[0] if e.args else 0
        
        if error_code == 1045:
            message = "❌ Access denied: Invalid username or password"
        elif error_code == 1049:
            message = f"❌ Database '{database}' does not exist"
        elif error_code == 2003:
            message = f"❌ Cannot connect to MySQL server at '{host}:{port}'"
        else: 
            message = f"❌ Database error: {str(e)}"
        
        return {
            "success": False,
            "message": message,
            "details": {
                "error_code": error_code,
                "error":  str(e)
            }
        }
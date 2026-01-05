"""
utils/logger.py - System Logger
บันทึก log ลง database และไฟล์
"""

import logging
from datetime import datetime
import pymysql
import config

class DatabaseLogHandler(logging.Handler):
    """Custom handler เพื่อบันทึก log ลง database"""
    
    def __init__(self, db_config):
        super().__init__()
        self.db_config = db_config
    
    def emit(self, record):
        """บันทึก log record ลง database"""
        try:
            conn = pymysql.connect(**self.db_config)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO tb_system_logs (log_level, message, created_at)
                VALUES (%s, %s, %s)
            """, (record.levelname, record.getMessage(), datetime.now()))
            
            conn.commit()
            cursor. close()
            conn.close()
        except Exception as e:
            print(f"Error logging to database:  {e}")

def setup_logger(name='pallet_detector'):
    """Setup logger ที่บันทึกทั้งไฟล์และ database"""
    
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # ถ้ามี handler อยู่แล้วไม่ต้องเพิ่ม
    if logger.handlers:
        return logger
    
    # Format
    formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # File Handler
    file_handler = logging.FileHandler('logs/detection.log', encoding='utf-8')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Console Handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Database Handler
    try:
        cfg = config.load_config()
        db_config = {
            'host': cfg['network']['database']['host'],
            'user': cfg['network']['database']['user'],
            'password': cfg['network']['database']['password'],
            'database': cfg['network']['database']['database'],
            'port': cfg['network']['database']['port']
        }
        db_handler = DatabaseLogHandler(db_config)
        db_handler.setFormatter(formatter)
        logger.addHandler(db_handler)
    except Exception as e:
        logger.warning(f"Cannot setup database logging: {e}")
    
    return logger
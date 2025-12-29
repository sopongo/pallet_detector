"""
utils/database.py - Database Connection Tester
ทดสอบการเชื่อมต่อ MySQL Database
"""

import pymysql
from pymysql import Error


# ========================================
# ฟังก์ชัน:  Test Database Connection
# ========================================
def test_database_connection(host, user, password, database, port=3306):
    """
    ทดสอบการเชื่อมต่อ MySQL
    Args:
        host (str): hostname หรือ IP
        user (str): username
        password (str): password
        database (str): database name
        port (int): port number (default: 3306)
    Returns:
        dict: {
            "success": bool,
            "message":  str,
            "details": dict (optional)
        }
    """
    try:
        # พยายามเชื่อมต่อ
        connection = pymysql.connect(
            host=host,
            user=user,
            password=password,
            database=database,
            port=int(port),
            connect_timeout=5  # timeout 5 วินาที
        )
        
        # ถ้าเชื่อมต่อได้ ลองดึง version
        cursor = connection.cursor()
        cursor.execute("SELECT VERSION()")
        version = cursor. fetchone()[0]
        
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
        # จัดการ error ต่างๆ
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
    
    except Exception as e:
        return {
            "success": False,
            "message": f"❌ Unexpected error: {str(e)}",
            "details": {}
        }


# ========================================
# ฟังก์ชัน: สร้าง Database Tables (ถ้ายังไม่มี)
# ========================================
def create_tables(host, user, password, database, port=3306):
    """
    สร้างตารางที่จำเป็นสำหรับระบบ
    Returns:
        dict: result
    """
    try:
        connection = pymysql.connect(
            host=host,
            user=user,
            password=password,
            database=database,
            port=int(port)
        )
        cursor = connection.cursor()
        
        # ตาราง pallet_detections
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pallet_detections (
                id INT AUTO_INCREMENT PRIMARY KEY,
                timestamp DATETIME NOT NULL,
                pallet_count INT NOT NULL,
                image_path VARCHAR(255),
                duration_minutes INT DEFAULT 0,
                alert_sent BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # ตาราง system_logs
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS system_logs (
                id INT AUTO_INCREMENT PRIMARY KEY,
                log_level VARCHAR(20),
                message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        connection.commit()
        cursor.close()
        connection.close()
        
        return {
            "success":  True,
            "message": "✅ Tables created successfully"
        }
    
    except Exception as e:
        return {
            "success": False,
            "message": f"❌ Error creating tables: {str(e)}"
        }
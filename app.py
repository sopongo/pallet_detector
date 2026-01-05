"""
05-01-2026 15:45:00 - app.py - Flask Backend (แก้ไข - เพิ่ม Camera Stream)
05-01-2026 15:45:00 - app.py - เพิ่ม API สำหรับ Monitoring Page
"""

from flask import Flask, request, jsonify, send_file, Response
from flask_cors import CORS
import json
import os
import cv2
import io
import config
from utils.database import DatabaseManager, test_database_connection
from utils.network import test_network_connection
from utils.camera import test_camera, detect_cameras
from utils.gpio_control import LightController, test_gpio
from utils.logger import setup_logger
import subprocess
import psutil
from datetime import datetime

# ========================================
# สร้างโฟลเดอร์ที่จำเป็น
# ========================================
os.makedirs('logs', exist_ok=True)
os.makedirs('config', exist_ok=True)

# ========================================
# Setup Logger
# ========================================
logger = setup_logger()

# ========================================
# Flask App Setup
# ========================================
app = Flask(__name__)
CORS(app)

# สร้าง Light Controller
light_controller = LightController(red_pin=17, green_pin=27)

# สร้าง Database Manager
db = DatabaseManager()

logger.info("🚀 Flask app initialized")


# ========================================
# Camera Stream Functions
# ========================================

def generate_frames(camera_index):
    """Generator สำหรับ MJPEG stream"""
    camera = None
    try:
        camera_index = int(camera_index)
        
        # เปิดกล้องด้วย CAP_DSHOW (Windows)
        camera = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)
        
        if not camera.isOpened():
            logger.error(f"Cannot open camera {camera_index}")
            return
        
        # ตั้งค่าความละเอียด
        camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        camera.set(cv2.CAP_PROP_FPS, 15)
        
        logger.info(f"Camera {camera_index} stream started")
        
        while True:
            success, frame = camera.read()
            if not success:
                logger.warning("Cannot read frame")
                break
            
            # Encode เป็น JPEG
            ret, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
            if not ret:
                continue
            
            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
    
    except Exception as e:
        logger.error(f"Stream error: {e}")
    
    finally:
        if camera is not None:
            camera.release()
            logger.info(f"Camera {camera_index} released")


# ========================================
# Routes - Config
# ========================================

@app.route('/api/config', methods=['GET'])
def get_config():
    """ดึง config ปัจจุบัน"""
    cfg = config.load_config()
    return jsonify(cfg), 200


@app.route('/api/config', methods=['POST'])
def save_config():
    """บันทึก config ใหม่"""
    try:
        data = request.get_json()
        if config.save_config(data):
            logger.info("Config saved successfully")
            return jsonify({"success": True, "message": "✅ Config saved"}), 200
        else:
            return jsonify({"success": False, "message": "❌ Save failed"}), 500
    except Exception as e: 
        logger. error(f"Save config error:  {e}")
        return jsonify({"success": False, "message": str(e)}), 400


@app.route('/api/config/reset', methods=['POST'])
def reset_config():
    """Reset config เป็นค่า default"""
    cfg = config.reset_config()
    logger.info("Config reset to default")
    return jsonify({"success": True, "config": cfg}), 200


@app.route('/api/config/export', methods=['GET'])
def export_config():
    """Export config เป็นไฟล์ JSON"""
    return send_file(config.CONFIG_FILE, as_attachment=True, download_name='pallet_config.json')


# ========================================
# Routes - Test
# ========================================

@app. route('/api/test/database', methods=['POST'])
def test_db():
    """ทดสอบ Database"""
    data = request.get_json()
    result = test_database_connection(
        host=data. get('host'),
        user=data.get('user'),
        password=data.get('password'),
        database=data.get('database'),
        port=data. get('port', 3306)
    )
    return jsonify(result), 200


@app.route('/api/test/network', methods=['POST'])
def test_net():
    """ทดสอบ Network/WiFi"""
    result = test_network_connection()
    return jsonify(result), 200


@app.route('/api/test/camera', methods=['POST'])
def test_cam():
    """ทดสอบกล้อง"""
    try: 
        data = request.get_json()
        camera_index = int(data.get('camera', 0))
        
        logger. info(f"Testing camera {camera_index}...")
        result = test_camera(camera_index)
        
        return jsonify(result), 200
        
    except Exception as e: 
        logger.error(f"Camera test error: {e}")
        return jsonify({
            "success": False,
            "message": f"Error:  {str(e)}"
        }), 500


@app.route('/api/test/gpio', methods=['POST'])
def test_gpio_route():
    """ทดสอบ GPIO"""
    result = test_gpio()
    return jsonify(result), 200


# ========================================
# Routes - Camera
# ========================================

@app.route('/api/camera/detect', methods=['GET'])
def detect_cam():
    """หากล้องที่เชื่อมต่ออยู่"""
    cameras = detect_cameras()
    return jsonify({"cameras": cameras}), 200


@app.route('/api/camera/stream/<int:camera_id>')
def video_stream(camera_id):
    """
    Stream camera feed (MJPEG)
    Example: http://localhost:5000/api/camera/stream/0
    """
    try: 
        response = Response(
            generate_frames(camera_id),
            mimetype='multipart/x-mixed-replace; boundary=frame'
        )
        
        # ✅ เพิ่ม headers ป้องกัน cache
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        response.headers['X-Content-Type-Options'] = 'nosniff'
        
        return response
        
    except Exception as e:
        logger.error(f"Video stream error: {e}")
        return jsonify({"success": False, "message": str(e)}), 500


# ========================================
# Routes - GPIO
# ========================================

@app.route('/api/gpio/red/on', methods=['POST'])
def red_on():
    """เปิดไฟแดง"""
    result = light_controller. test_red()
    return jsonify(result), 200


@app.route('/api/gpio/red/off', methods=['POST'])
def red_off():
    """ปิดไฟแดง"""
    result = light_controller. turn_off_red()
    return jsonify(result), 200


@app.route('/api/gpio/green/on', methods=['POST'])
def green_on():
    """เปิดไฟเขียว"""
    result = light_controller.test_green()
    return jsonify(result), 200


@app.route('/api/gpio/green/off', methods=['POST'])
def green_off():
    """ปิดไฟเขียว"""
    result = light_controller.turn_off_green()
    return jsonify(result), 200


# ========================================
# Routes - System
# ========================================

@app.route('/api/system/storage', methods=['GET'])
def get_storage_info():
    """ดึงข้อมูล storage"""
    import shutil
    try:
        cfg = config.load_config()
        path = cfg['general']['imagePath']
        
        if not os.path.exists(path):
            os.makedirs(path, exist_ok=True)
            return jsonify({
                "success": True,
                "data": {
                    "usedMB": 0,
                    "totalFiles": 0,
                    "totalDiskGB": round(shutil.disk_usage(os.path.dirname(path)).total / (1024**3), 2),
                    "freeDiskGB": round(shutil. disk_usage(os.path. dirname(path)).free / (1024**3), 2),
                    "path": path
                }
            })
        
        total_files = 0
        total_size = 0
        
        for dirpath, dirnames, filenames in os.walk(path):
            total_files += len(filenames)
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                try: 
                    total_size += os.path.getsize(filepath)
                except: 
                    continue
        
        used_mb = total_size / (1024 * 1024)
        
        try: 
            disk = shutil.disk_usage(path)
            total_disk_gb = disk.total / (1024**3)
            free_disk_gb = disk. free / (1024**3)
        except:
            disk = shutil.disk_usage(os.getcwd())
            total_disk_gb = disk.total / (1024**3)
            free_disk_gb = disk. free / (1024**3)
        
        return jsonify({
            "success": True,
            "data": {
                "usedMB": round(used_mb, 2),
                "totalFiles": total_files,
                "totalDiskGB":  round(total_disk_gb, 2),
                "freeDiskGB": round(free_disk_gb, 2),
                "path": path
            }
        })
        
    except Exception as e:
        return jsonify({"success": False, "message": f"Error: {str(e)}"})

# ========================================
# Global Variables - Process Control
# ========================================
detection_process = None

# ========================================
# Routes - Detection Control
# ========================================

@app.route('/api/detection/status', methods=['GET'])
def get_detection_status():
    """ตรวจสอบสถานะ detection service"""
    global detection_process
    
    is_running = False
    pid = None
    
    if detection_process and detection_process.poll() is None:
        is_running = True
        pid = detection_process. pid
    
    return jsonify({
        "success": True,
        "running": is_running,
        "pid": pid,
        "timestamp": datetime. now().strftime('%Y-%m-%d %H:%M:%S')
    })


@app.route('/api/detection/start', methods=['POST'])
def start_detection():
    """เริ่ม detection service"""
    global detection_process
    
    try:
        # ตรวจสอบว่ารันอยู่แล้วหรือไม่
        if detection_process and detection_process.poll() is None:
            return jsonify({
                "success":  False,
                "message": "⚠️ Detection service is already running"
            }), 400
        
        # เริ่ม detection_service. py
        detection_process = subprocess.Popen(
            ['python', 'detection_service. py'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        logger.info(f"✅ Detection service started (PID: {detection_process. pid})")
        
        return jsonify({
            "success": True,
            "message": "✅ Detection service started",
            "pid": detection_process.pid
        })
        
    except Exception as e:
        logger.error(f"❌ Cannot start detection service: {e}")
        return jsonify({
            "success": False,
            "message": f"❌ Error: {str(e)}"
        }), 500


@app.route('/api/detection/stop', methods=['POST'])
def stop_detection():
    """หยุด detection service"""
    global detection_process
    
    try: 
        if not detection_process or detection_process.poll() is not None:
            return jsonify({
                "success": False,
                "message": "⚠️ Detection service is not running"
            }), 400
        
        # หยุด process
        detection_process.terminate()
        detection_process.wait(timeout=5)
        
        logger.info("✅ Detection service stopped")
        
        detection_process = None
        
        return jsonify({
            "success": True,
            "message":  "✅ Detection service stopped"
        })
        
    except Exception as e:
        logger. error(f"❌ Cannot stop detection service: {e}")
        return jsonify({
            "success": False,
            "message": f"❌ Error:  {str(e)}"
        }), 500


@app.route('/api/detection/latest', methods=['GET'])
def get_latest_detection():
    """ดึงข้อมูล detection ล่าสุด (2 รูปล่าสุด)"""
    try:
        conn = db.get_connection()
        cursor = conn.cursor()
        
        # ดึง 2 รูปล่าสุด
        cursor.execute("""
            SELECT id_img, image_date, image_name, pallet_detected, site, location
            FROM tb_image
            ORDER BY image_date DESC
            LIMIT 2
        """)
        
        images = cursor.fetchall()
        
        result = {
            "success": True,
            "before":  None,
            "after": None
        }
        
        if len(images) >= 2:
            # ✅ Before image (ใช้รูปที่ตีกรอบ)
            before_name = images[1]['image_name']
            before_name_detected = before_name.replace('.jpg', '_detected.jpg')
            
            result["before"] = {
                "id": images[1]['id_img'],
                "date": images[1]['image_date']. strftime('%d/%m/%Y %H:%M:%S'),
                "filename": images[1]['image_name'],
                "count": images[1]['pallet_detected'],
                "image_url": f"http://localhost:5000/static/upload_image/{images[1]['image_date'].strftime('%Y-%m-%d')}/{before_name_detected}"
            }
            
            # ✅ After image (ใช้รูปที่ตีกรอบ)
            after_name = images[0]['image_name']
            after_name_detected = after_name.replace('.jpg', '_detected.jpg')
            
            result["after"] = {
                "id": images[0]['id_img'],
                "date": images[0]['image_date'].strftime('%d/%m/%Y %H:%M:%S'),
                "filename": images[0]['image_name'],
                "count": images[0]['pallet_detected'],
                "image_url": f"http://localhost:5000/static/upload_image/{images[0]['image_date'].strftime('%Y-%m-%d')}/{after_name_detected}"
            }
        
        cursor.close()
        conn.close()
        
        return jsonify(result)
        
    except Exception as e:
        logger. error(f"Error getting latest detection: {e}")
        return jsonify({"success": False, "message": str(e)}), 500


@app.route('/api/detection/summary/today', methods=['GET'])
def get_today_summary():
    """ดึงสรุปข้อมูลวันนี้"""
    try:
        summary = db.get_daily_summary()
        
        cfg = config.load_config()
        
        # ดึงข้อมูล site/location จาก config
        site_id = int(cfg['general']. get('siteCompany', 1))
        location_id = int(cfg['general'].get('siteLocation', 1))
        
        # แปลง site/location เป็นชื่อ
        site_map = {1: "PACJ", 2: "Site B", 3: "Site C"}
        location_map = {1: "Building 1", 2: "Building 2", 3: "Building 3"}
        
        result = {
            "success": True,
            "site": site_map. get(site_id, f"Site {site_id}"),
            "location": location_map.get(location_id, f"Location {location_id}"),
            "total_photos": summary. get('total_photos', 0),
            "total_detected": summary.get('total_detected', 0),
            "in_time": summary.get('in_time', 0),
            "over_time": summary.get('over_time', 0),
            "notifications": summary.get('notifications', 0),
            "date": summary.get('date', datetime.now().strftime('%Y-%m-%d'))
        }
        
        logger.info(f"Summary:  {result}")
        
        return jsonify(result)
        
    except Exception as e: 
        logger.error(f"Error getting summary: {e}")
        return jsonify({"success": False, "message": str(e)}), 500


@app.route('/api/detection/logs', methods=['GET'])
def get_detection_logs():
    """ดึง system logs"""
    try:
        limit = int(request.args.get('limit', 10))
        
        # อ่านจากไฟล์ log
        log_file = 'logs/detection.log'
        
        # ✅ Debug:  ตรวจสอบไฟล์
        if not os.path.exists(log_file):
            logger.error(f"Log file not found: {log_file}")
            return jsonify({"success": True, "logs": [], "error": "Log file not found"})
        
        # ✅ Debug: ดูขนาดไฟล์
        file_size = os.path.getsize(log_file)
        logger.info(f"Log file size: {file_size} bytes")
        
        # ✅ อ่านไฟล์ (เพิ่ม error handling)
        try:
            with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
        except Exception as e:
            logger.error(f"Cannot read log file: {e}")
            return jsonify({"success":  False, "message": f"Cannot read log file: {str(e)}"})
        
        # ✅ Debug: จำนวนบรรทัดทั้งหมด
        logger.info(f"Total lines in log file: {len(lines)}")
        
        # ดึง N บรรทัดล่าสุด
        recent_logs = lines[-limit: ] if len(lines) > limit else lines
        
        # ✅ Debug: ดูข้อมูลก่อน filter
        logger.info(f"Recent logs (before filter): {len(recent_logs)} lines")
        
        # แปลงเป็น list (ลบ newline + filter blank)
        logs = [line.strip() for line in recent_logs if line.strip()]
        
        # ✅ Debug: ดูข้อมูลหลัง filter
        logger.info(f"Logs (after filter): {len(logs)} lines")
        
        # ✅ Debug: แสดง log 3 บรรทัดแรก
        if logs: 
            logger.info(f"Sample logs: {logs[:3]}")
        
        return jsonify({
            "success":  True,
            "logs": logs,
            "debug": {
                "file_size": file_size,
                "total_lines": len(lines),
                "filtered_lines": len(logs)
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting logs: {e}")
        return jsonify({"success": False, "message": str(e)}), 500


@app.route('/api/system/info', methods=['GET'])
def get_system_info():
    """ดึงข้อมูล system (CPU, RAM, Temp)"""
    try:
        cfg = config.load_config()
        
        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # RAM usage
        ram = psutil.virtual_memory()
        ram_total_gb = ram.total / (1024**3)
        ram_percent = ram.percent
        
        # Temperature (ถ้าอยู่บน Pi)
        temp = "N/A"
        try:
            with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
                temp = f"{int(f.read()) / 1000:.2f}"
        except:
            pass
        
        return jsonify({
            "success": True,
            "working_hours": f"{cfg['detection']['operatingHours']['start']} - {cfg['detection']['operatingHours']['end']}",
            "confidence": cfg['detection']['confidenceThreshold'],
            "iou_threshold": cfg['detection']['iouThreshold'],
            "image_size": f"{cfg['detection']['imageSize']}px",
            "interval": f"{cfg['detection']['captureInterval']}s ({cfg['detection']['captureInterval']//60}m)",
            "alert_threshold": f"{cfg['detection']['alertThreshold']}m",
            "device_mode": cfg['detection']['deviceMode']. upper(),
            "cpu_usage":  f"{cpu_percent}%",
            "ram_total": f"{ram_total_gb:.0f} GB",
            "ram_usage": f"{ram_percent}%",
            "temperature": f"{temp} °C"
        })
        
    except Exception as e:
        logger. error(f"Error getting system info: {e}")
        return jsonify({"success": False, "message": str(e)}), 500


@app.route('/api/pallets/active', methods=['GET'])
def get_active_pallets():
    """ดึงพาเลทที่ active อยู่"""
    try: 
        conn = db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id_pallet, pos_x, pos_y, 
                   TIMESTAMPDIFF(MINUTE, first_detected_at, NOW()) as duration_minutes,
                   in_over, status
            FROM tb_pallet
            WHERE is_active = 1
            ORDER BY first_detected_at DESC
        """)
        
        pallets = cursor.fetchall()
        
        result = []
        for p in pallets:
            result. append({
                "id": p['id_pallet'],
                "position": [float(p['pos_x']), float(p['pos_y'])],
                "duration": p['duration_minutes'],
                "overtime": bool(p['in_over']),
                "status": p['status']
            })
        
        cursor.close()
        conn.close()
        
        return jsonify({
            "success": True,
            "count": len(result),
            "pallets": result
        })
        
    except Exception as e: 
        logger.error(f"Error getting active pallets: {e}")
        return jsonify({"success": False, "message": str(e)}), 500


# ========================================
# Static Files - Serve Images
# ========================================
from flask import send_from_directory

@app.route('/static/upload_image/<path:filename>')
def serve_uploaded_image(filename):
    """Serve uploaded images"""
    try:
        cfg = config.load_config()
        image_dir = cfg['general']['imagePath']
        
        # แปลงเป็น absolute path
        if not os.path.isabs(image_dir):
            image_dir = os.path.abspath(image_dir)
        
        return send_from_directory(image_dir, filename)
        
    except Exception as e:
        logger.error(f"Error serving image: {e}")
        return jsonify({"success": False, "message": str(e)}), 404

@app.route('/api/config/locations', methods=['GET'])
def get_locations():
    """ดึง locations ตาม site_id"""
    try: 
        site_id = request. args.get('site_id')
        
        if not site_id:
            return jsonify({"success": False, "message":  "site_id required"}), 400
        
        # อ่าน sites.json
        sites_file = os.path.join(os.path.dirname(__file__), 'config', 'sites.json')
        
        if not os.path.exists(sites_file):
            return jsonify({
                "success": False,
                "message": "Sites data not found"
            }), 404
        
        with open(sites_file, 'r', encoding='utf-8') as f:
            sites_data = json.load(f)
        
        # ดึง locations ของ site นี้
        site_id_int = int(site_id)
        
        if str(site_id_int) in sites_data:
            locations = sites_data[str(site_id_int)].get('location', {})
            return jsonify({
                "success": True,
                "locations": locations
            })
        else:
            return jsonify({
                "success": False,
                "message": f"Site {site_id} not found"
            }), 404
            
    except Exception as e:
        logger.error(f"Error getting locations: {e}")
        return jsonify({"success": False, "message": str(e)}), 500

# ========================================
# Main
# ========================================
if __name__ == '__main__':
    logger.info("🚀 Starting Pallet Detection Backend...")
    app.run(host='0.0.0.0', port=5000, debug=True)

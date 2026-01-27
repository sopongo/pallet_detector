"""
05-01-2026 15:45:00 - app.py - Flask Backend (แก้ไข - เพิ่ม Camera Stream)
05-01-2026 15:45:00 - app.py - เพิ่ม API สำหรับ Monitoring Page

แก้ไขเพิ่มเติม:
- เพิ่มการควบคุม process ของ detection_service.py (start / stop / status)
- ใช้ sys.executable เพื่อให้ subprocess ใช้ interpreter เดียวกับ Flask
- เขียน PID ลงไฟล์ detection_service.pid เพื่อให้ status ทำงานหลัง Flask รีสตาร์ท
- ส่ง stdout/stderr ของ subprocess ไปยัง logs/detection_service.log
- ใช้ psutil สำหรับตรวจสถานะ process และ terminate process tree อย่างปลอดภัย
"""
from flask import Flask, request, jsonify, send_file, Response, send_from_directory
from flask_cors import CORS
import json
import os
import sys
import subprocess
import time
import psutil
import cv2
import io
import config
from utils.database import DatabaseManager, test_database_connection
from utils.network import test_network_connection
from utils.camera import test_camera, detect_cameras, RobustCamera
from utils.gpio_control import LightController, test_gpio
from utils.logger import setup_logger
from utils.zone_config import get_zone_manager
from datetime import datetime

# ----------------------------------------
# สร้างโฟลเดอร์ที่จำเป็นถ้ายังไม่มี
# ----------------------------------------
os.makedirs('logs', exist_ok=True)
os.makedirs('config', exist_ok=True)

# ----------------------------------------
# ตั้งค่า Logger
# ----------------------------------------
logger = setup_logger()

# ----------------------------------------
# สร้าง Flask app และเปิด CORS
# ----------------------------------------
app = Flask(__name__)
CORS(app)

# ✅ NEW: Serve static images from upload_image directory
# Serve uploaded images (ใช้ imagePath จาก config)
@app.route('/upload_image/<path:filename>')
def serve_uploaded_image(filename):
    """
    Serve images from upload_image directory with CORS headers
    to prevent canvas tainting
    """
    upload_dir = os.path.join(os.path.dirname(__file__), 'upload_image')
    
    response = send_from_directory(upload_dir, filename)
    
    # ✅ Add CORS headers to allow canvas export
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    
    return response


# ----------------------------------------
# สร้าง LightController (ถ้ามีข้อผิดพลาดเช่นบน Windows ให้จับ exception)
# ----------------------------------------
try:
    light_controller = LightController(red_pin=17, green_pin=27)
except Exception as e:
    logger.warning(f"LightController init failed: {e}")
    light_controller = None

# ----------------------------------------
# สร้าง Database Manager
# ----------------------------------------
db = DatabaseManager()

logger.info("🚀 Flask app initialized")

# ----------------------------------------
# ฟังก์ชันสร้าง MJPEG stream จากกล้อง (ใช้ RobustCamera)
# ----------------------------------------
def generate_frames(camera_index):
    """Generator สำหรับ MJPEG streaming. ดูแลการเปิด-ปิดกล้องและการ encode (ใช้ RobustCamera)"""
    camera = None
    try:
        logger.info(f"📸 Starting video stream for camera {camera_index}")
        
        # ✅ ใช้ RobustCamera แทน OpenCV VideoCapture
        camera = RobustCamera(
            camera_index,
            max_retries=3,
            timeout=5,
            width=640,
            height=480
        )
        
        if not camera.is_opened():
            logger.error(f"❌ Cannot open camera {camera_index}")
            return
        
        logger.info(f"✅ Camera stream started (type: {camera.camera_type})")

        while True:
            # ✅ อ่าน frame (with auto-reconnect)
            ret, frame = camera.read()
            
            if not ret or frame is None:
                logger.warning("⚠️ Cannot read frame")
                # RobustCamera จะพยายาม reconnect อัตโนมัติ
                time.sleep(0.5)
                continue
            
            # Encode เป็น JPEG
            ret_encode, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
            if not ret_encode:
                continue
            
            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
                   
    except Exception as e:
        logger.error(f"❌ Stream error: {e}")
    finally:
        if camera is not None:
            camera.release()
            logger.info(f"✅ Camera {camera_index} stream stopped")


# ----------------------------------------
# Routes - Config (ดึง/บันทึก/รีเซ็ต/ดาวน์โหลด config)
# ----------------------------------------
@app.route('/api/config', methods=['GET'])
def get_config():
    cfg = config.load_config()
    return jsonify(cfg), 200

@app.route('/api/config', methods=['POST'])
def save_config():
    try:
        data = request.get_json()
        if config.save_config(data):
            logger.info("Config saved successfully")
            return jsonify({"success": True, "message": "✅ Config saved"}), 200
        else:
            return jsonify({"success": False, "message": "❌ Save failed"}), 500
    except Exception as e:
        logger.error(f"Save config error: {e}")
        return jsonify({"success": False, "message": str(e)}), 400

@app.route('/api/config/reset', methods=['POST'])
def reset_config():
    cfg = config.reset_config()
    logger.info("Config reset to default")
    return jsonify({"success": True, "config": cfg}), 200

@app.route('/api/config/export', methods=['GET'])
def export_config():
    return send_file(config.CONFIG_FILE, as_attachment=True, download_name='pallet_config.json')


# ----------------------------------------
# Routes - Test (Database / Network / Camera / GPIO / LINE)
# ----------------------------------------
@app.route('/api/test/database', methods=['POST'])
def test_db():
    data = request.get_json()
    result = test_database_connection(
        host=data.get('host'),
        user=data.get('user'),
        password=data.get('password'),
        database=data.get('database'),
        port=data.get('port', 3306)
    )
    return jsonify(result), 200

@app.route('/api/test/network', methods=['POST'])
def test_net():
    result = test_network_connection()
    return jsonify(result), 200

@app.route('/api/test/camera', methods=['POST'])
def test_cam():
    try:
        data = request.get_json()
        camera_index = int(data.get('camera', 0))
        logger.info(f"Testing camera {camera_index}...")
        result = test_camera(camera_index)
        return jsonify(result), 200
    except Exception as e:
        logger.error(f"Camera test error: {e}")
        return jsonify({"success": False, "message": f"Error: {str(e)}"}), 500

@app.route('/api/test/gpio', methods=['POST'])
def test_gpio_route():
    result = test_gpio()
    return jsonify(result), 200

from utils.line_messaging import test_line_connection
@app.route('/api/test/line', methods=['POST'])
def test_line():
    try:
        result = test_line_connection()
        return jsonify(result), 200
    except Exception as e:
        logger.error(f"LINE test error: {e}")
        return jsonify({"success": False, "message": f"Error: {str(e)}"}), 500

# ----------------------------------------
# Camera routes: detect list / stream
# ----------------------------------------
@app.route('/api/camera/detect', methods=['GET'])
def detect_cam():
    cameras = detect_cameras()
    return jsonify({"cameras": cameras}), 200

@app.route('/api/camera/stream/<int:camera_id>')
def video_stream(camera_id):
    try:
        response = Response(generate_frames(camera_id), mimetype='multipart/x-mixed-replace; boundary=frame')
        # ป้องกันการ cache
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        response.headers['X-Content-Type-Options'] = 'nosniff'
        return response
    except Exception as e:
        logger.error(f"Video stream error: {e}")
        return jsonify({"success": False, "message": str(e)}), 500




# ----------------------------------------
# GPIO control routes (เปิด/ปิดไฟ)
# ----------------------------------------
@app.route('/api/gpio/red/on', methods=['POST'])
def red_on():
    if light_controller:
        result = light_controller.test_red()
    else:
        result = {"success": False, "message": "GPIO not available"}
    return jsonify(result), 200

@app.route('/api/gpio/red/off', methods=['POST'])
def red_off():
    if light_controller:
        result = light_controller.turn_off_red()
    else:
        result = {"success": False, "message": "GPIO not available"}
    return jsonify(result), 200

@app.route('/api/gpio/green/on', methods=['POST'])
def green_on():
    if light_controller:
        result = light_controller.test_green()
    else:
        result = {"success": False, "message": "GPIO not available"}
    return jsonify(result), 200

@app.route('/api/gpio/green/off', methods=['POST'])
def green_off():
    if light_controller:
        result = light_controller.turn_off_green()
    else:
        result = {"success": False, "message": "GPIO not available"}
    return jsonify(result), 200


# ----------------------------------------
# System info (storage/cpu/ram/temp)
# ----------------------------------------
@app.route('/api/system/storage', methods=['GET'])
def get_storage_info():
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
                    "freeDiskGB": round(shutil.disk_usage(os.path.dirname(path)).free / (1024**3), 2),
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
            free_disk_gb = disk.free / (1024**3)
        except:
            disk = shutil.disk_usage(os.getcwd())
            total_disk_gb = disk.total / (1024**3)
            free_disk_gb = disk.free / (1024**3)
        return jsonify({
            "success": True,
            "data": {
                "usedMB": round(used_mb, 2),
                "totalFiles": total_files,
                "totalDiskGB": round(total_disk_gb, 2),
                "freeDiskGB": round(free_disk_gb, 2),
                "path": path
            }
        })
    except Exception as e:
        return jsonify({"success": False, "message": f"Error: {str(e)}"})


# ----------------------------------------
# Process control helpers สำหรับ detection_service
# ----------------------------------------
PID_FILE = os.path.join(os.path.dirname(__file__), 'detection_service.pid')
DETECTION_LOG = os.path.join(os.path.dirname(__file__), 'logs', 'detection_service.log')
detection_process = None  # object ของ subprocess จะอยู่แค่ขณะที่ Flask ทำงาน

def _write_pid(pid: int):
    """เขียน PID ลงไฟล์ เพื่อให้ตรวจสถานะหลัง Flask รีสตาร์ทได้"""
    try:
        with open(PID_FILE, 'w') as f:
            f.write(str(pid))
    except Exception as e:
        logger.error(f"Cannot write PID file: {e}")

def _read_pid():
    """อ่าน PID จาก pidfile"""
    try:
        if os.path.exists(PID_FILE):
            with open(PID_FILE, 'r') as f:
                return int(f.read().strip())
    except Exception as e:
        logger.error(f"Cannot read PID file: {e}")
    return None

def _remove_pidfile():
    """ลบ pidfile ถ้ามี"""
    try:
        if os.path.exists(PID_FILE):
            os.remove(PID_FILE)
    except Exception as e:
        logger.error(f"Cannot remove PID file: {e}")

def _is_pid_running(pid: int) -> bool:
    """ตรวจสอบว่า PID ยังรันอยู่หรือไม่ (ใช้ psutil)"""
    try:
        p = psutil.Process(pid)
        return p.is_running() and p.status() != psutil.STATUS_ZOMBIE
    except Exception:
        return False

def _ensure_logfile():
    """สร้างไฟล์ log ของ detection ถ้ายังไม่มี"""
    try:
        logdir = os.path.dirname(DETECTION_LOG)
        os.makedirs(logdir, exist_ok=True)
        open(DETECTION_LOG, 'a').close()
    except Exception as e:
        logger.error(f"Cannot ensure detection log file: {e}")


# ----------------------------------------
# Detection control routes: status / start / stop
# ----------------------------------------
@app.route('/api/detection/status', methods=['GET'])
def get_detection_status():
    """ส่งสถานะการรันของ detection_service"""
    global detection_process
    is_running = False
    pid = None

    # ถ้ามี subprocess object อยู่และยังรัน -> ใช้
    if detection_process and detection_process.poll() is None:
        is_running = True
        pid = detection_process.pid
    else:
        # fallback: อ่าน pidfile
        pid_file_pid = _read_pid()
        if pid_file_pid and _is_pid_running(pid_file_pid):
            is_running = True
            pid = pid_file_pid
        else:
            # ลบ pidfile ถ้าเป็น stale
            _remove_pidfile()

    return jsonify({
        "success": True,
        "running": is_running,
        "pid": pid,
        "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })


@app.route('/api/detection/start', methods=['POST'])
def start_detection():
    """เริ่ม detection_service.py เป็น subprocess"""
    global detection_process

    try:
        # ถ้ามี process อยู่แล้ว -> แจ้ง error
        if detection_process and detection_process.poll() is None:
            return jsonify({"success": False, "message": "⚠️ Detection service is already running"}), 400

        # ตรวจ pidfile เผื่อ process เริ่มจากก่อนหน้า
        existing_pid = _read_pid()
        if existing_pid and _is_pid_running(existing_pid):
            return jsonify({"success": False, "message": f"⚠️ Detection service already running (PID: {existing_pid})"}), 400

        # ตรวจหาไฟล์สคริปต์
        script_path = os.path.join(os.path.dirname(__file__), 'detection_service.py')
        if not os.path.exists(script_path):
            return jsonify({"success": False, "message": "❌ detection_service.py not found"}), 500

        # สร้าง logfile ถ้ายังไม่มี
        _ensure_logfile()

        # สั่งรันด้วย interpreter เดียวกับ Flask (ลดปัญหา path/venv)
        cmd = [sys.executable, script_path]

        # Windows: กำหนด creationflags เพื่อแยก process group (optional)
        creationflags = 0
        if os.name == 'nt':
            try:
                creationflags = subprocess.CREATE_NEW_PROCESS_GROUP
            except Exception:
                creationflags = 0

        # เปิดไฟล์ log และ redirect stdout/stderr ของ subprocess ไปที่ไฟล์
        logfile = open(DETECTION_LOG, 'a', buffering=1, encoding='utf-8', errors='replace')

        detection_process = subprocess.Popen(
            cmd,
            cwd=os.path.dirname(__file__),
            stdout=logfile,
            stderr=logfile,
            creationflags=creationflags
        )

        # เขียน PID ลงไฟล์
        _write_pid(detection_process.pid)
        logger.info(f"✅ Detection service started (PID: {detection_process.pid})")

        return jsonify({"success": True, "message": "✅ Detection service started", "pid": detection_process.pid})
    except Exception as e:
        logger.error(f"❌ Cannot start detection service: {e}")
        return jsonify({"success": False, "message": f"❌ Error: {str(e)}"}), 500


@app.route('/api/detection/stop', methods=['POST'])
def stop_detection():
    """หยุด detection_service.py: พยายาม terminate ก่อน ถ้าไม่ยอมก็ kill"""
    global detection_process

    try:
        logger.info(f"🔴 Stop request received. Current process object: {detection_process}")

        # หา pid: ถ้ามี object ใช้ pid นั้น, ถ้าไม่มีอ่านจาก pidfile
        pid = None
        if detection_process and detection_process.poll() is None:
            pid = detection_process.pid
        else:
            pid = _read_pid()

        if not pid or not _is_pid_running(pid):
            _remove_pidfile()
            return jsonify({"success": False, "message": "⚠️ Detection service is not running"}), 400

        # พยายาม terminate อย่างสุภาพก่อน
        try:
            if detection_process and detection_process.pid == pid:
                detection_process.terminate()
                detection_process.wait(timeout=10)
            else:
                # ใช้ psutil หยุด process tree
                parent = psutil.Process(pid)
                children = parent.children(recursive=True)
                for child in children:
                    try:
                        child.terminate()
                    except Exception:
                        pass
                parent.terminate()
                gone, alive = psutil.wait_procs([parent] + children, timeout=10)
                # ถ้ายังมีตัวที่ไม่ยอมตาย -> kill
                for p in alive:
                    try:
                        p.kill()
                    except Exception:
                        pass
        except psutil.TimeoutExpired:
            logger.warning("⚠️ Terminate timeout, forcing kill...")
            try:
                p = psutil.Process(pid)
                p.kill()
            except Exception as e:
                logger.error(f"Cannot kill process: {e}")

        # ล้าง pidfile และ object
        _remove_pidfile()
        detection_process = None
        logger.info("✅ Detection service stopped")

        return jsonify({"success": True, "message": "✅ Detection service stopped"})
    except Exception as e:
        logger.error(f"❌ Cannot stop detection service: {e}")
        return jsonify({"success": False, "message": f"❌ Error: {str(e)}"}), 500


# ----------------------------------------
# APIs ด้าน detection (latest / summary / logs / active pallets)
# โค้ดส่วนนี้คงเดิม แต่เพิ่ม logging และ error handling เพิ่มเติม
# ----------------------------------------
@app.route('/api/detection/latest', methods=['GET'])
def get_latest_detection():
    try:
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id_img, image_date, image_name, pallet_detected, site, location
            FROM tb_image
            ORDER BY image_date DESC
            LIMIT 2
        """)
        images = cursor.fetchall()
        result = {"success": True, "before": None, "after": None}
        if len(images) >= 2:
            before_name = images[1]['image_name']
            before_name_detected = before_name.replace('.jpg', '_detected.jpg')
            result["before"] = {
                "id": images[1]['id_img'],
                "date": images[1]['image_date'].strftime('%d/%m/%Y %H:%M:%S'),
                "filename": images[1]['image_name'],
                "count": images[1]['pallet_detected'],
                "image_url": f"http://localhost:5000/static/upload_image/{images[1]['image_date'].strftime('%Y-%m-%d')}/{before_name_detected}"
            }
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
        logger.error(f"Error getting latest detection: {e}")
        return jsonify({"success": False, "message": str(e)}), 500


@app.route('/api/detection/summary/today', methods=['GET'])
def get_today_summary():
    try:
        summary = db.get_daily_summary()
        cfg = config.load_config()
        site_id = int(cfg['general'].get('siteCompany', 1))
        location_id = int(cfg['general'].get('siteLocation', 1))
        sites_file = os.path.join(os.path.dirname(__file__), 'config', 'sites.json')
        site_name = f"Site {site_id}"
        location_name = f"Location {location_id}"
        try:
            if os.path.exists(sites_file):
                with open(sites_file, 'r', encoding='utf-8') as f:
                    sites_data = json.load(f)
                if str(site_id) in sites_data:
                    site_info = sites_data[str(site_id)]
                    site_name = site_info.get('site_name', site_name)
                    locations = site_info.get('location', {})
                    if str(location_id) in locations:
                        location_name = locations[str(location_id)]
            else:
                logger.warning(f"sites.json not found")
        except Exception as e:
            logger.error(f"Error reading sites.json: {e}")
        result = {
            "success": True,
            "site": site_name,
            "location": location_name,
            "total_photos": summary.get('total_photos', 0),
            "total_detected": summary.get('total_detected', 0),
            "in_time": summary.get('in_time', 0),
            "over_time": summary.get('over_time', 0),
            "notifications": summary.get('notifications', 0),
            "date": summary.get('date', datetime.now().strftime('%Y-%m-%d'))
        }
        logger.info(f"Summary: {result}")
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error getting summary: {e}")
        return jsonify({"success": False, "message": str(e)}), 500


@app.route('/api/detection/logs', methods=['GET'])
def get_detection_logs():
    try:
        limit = int(request.args.get('limit', 10))
        log_file = os.path.join('logs', 'detection.log')
        if not os.path.exists(log_file):
            logger.error(f"Log file not found: {log_file}")
            return jsonify({"success": True, "logs": [], "error": "Log file not found"})
        file_size = os.path.getsize(log_file)
        logger.info(f"Log file size: {file_size} bytes")
        try:
            with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
        except Exception as e:
            logger.error(f"Cannot read log file: {e}")
            return jsonify({"success": False, "message": f"Cannot read log file: {str(e)}"})
        logger.info(f"Total lines in log file: {len(lines)}")
        recent_logs = lines[-limit:] if len(lines) > limit else lines
        
        # ✅ เพิ่ม: แปลง log เป็น dict พร้อม color class
        formatted_logs = []
        for line in recent_logs:
            line_stripped = line.strip()
            if not line_stripped:
                continue
                
            log_dict = {
                'text': line_stripped,
                'class': ''  # Default: no special class
            }
            
            # ✅ เช็คว่า log มี keyword overtime หรือไม่
            line_lower = line_stripped.lower()
            if 'overtime' in line_lower or '⚠️' in line_stripped or 'pallet over time' in line_lower:
                log_dict['class'] = 'log-error'  # CSS class สีแดง
            elif 'error' in line_lower or '❌' in line_stripped:
                log_dict['class'] = 'log-error'
            elif 'warning' in line_lower or '🔴' in line_stripped:
                log_dict['class'] = 'log-warning'
            
            formatted_logs.append(log_dict)
        
        logger.info(f"Logs (after filter): {len(formatted_logs)} lines")
        if formatted_logs:
            logger.info(f"Sample logs: {[log['text'][:50] for log in formatted_logs[:3]]}")
        return jsonify({"success": True, "logs": formatted_logs, "debug": {"file_size": file_size, "total_lines": len(lines), "filtered_lines": len(formatted_logs)}})
    except Exception as e:
        logger.error(f"Error getting logs: {e}")
        return jsonify({"success": False, "message": str(e)}), 500



@app.route('/api/system/info', methods=['GET'])
def get_system_info():
    try:
        cfg = config.load_config()
        
        # Load zones and count inbound/outbound
        zones_file = os.path.join(os.path.dirname(__file__), 'config', 'zones.json')
        inbound_zones = 0
        outbound_zones = 0
        try:
            if os.path.exists(zones_file):
                with open(zones_file, 'r') as f:
                    zones_data = json.load(f)
                    zones = zones_data.get('zones', [])
                    inbound_zones = sum(1 for z in zones if z.get('pallet_type') == 1)
                    outbound_zones = sum(1 for z in zones if z.get('pallet_type') == 2)
        except Exception as e:
            logger.warning(f"Cannot load zones for system info: {e}")
        
        cpu_percent = psutil.cpu_percent(interval=1)
        ram = psutil.virtual_memory()
        ram_total_gb = ram.total / (1024**3)
        ram_percent = ram.percent
        temp = "N/A"
        try:
            with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
                temp = f"{int(f.read()) / 1000:.2f}"
        except:
            pass
        return jsonify({
            "success": True,
            "operating_hours": f"{cfg['detection']['operatingHours']['start']} - {cfg['detection']['operatingHours']['end']}",
            "inbound_zones": inbound_zones,
            "outbound_zones": outbound_zones,
            "cpu_usage": f"{cpu_percent}%",
            "ram_total": f"{ram_total_gb:.0f} GB",
            "ram_usage": f"{ram_percent}%",
            "temperature": f"{temp} °C"
        })
    except Exception as e:
        logger.error(f"Error getting system info: {e}")
        return jsonify({"success": False, "message": str(e)}), 500


@app.route('/api/pallets/active', methods=['GET'])
def get_active_pallets():
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
            result.append({
                "id": p['id_pallet'],
                "position": [float(p['pos_x']), float(p['pos_y'])],
                "duration": p['duration_minutes'],
                "overtime": bool(p['in_over']),
                "status": p['status']
            })
        cursor.close()
        conn.close()
        return jsonify({"success": True, "count": len(result), "pallets": result})
    except Exception as e:
        logger.error(f"Error getting active pallets: {e}")
        return jsonify({"success": False, "message": str(e)}), 500



@app.route('/api/config/locations', methods=['GET'])
def get_locations():
    try:
        site_id = request.args.get('site_id')
        if not site_id:
            return jsonify({"success": False, "message": "site_id required"}), 400
        sites_file = os.path.join(os.path.dirname(__file__), 'config', 'sites.json')
        if not os.path.exists(sites_file):
            return jsonify({"success": False, "message": "Sites data not found"}), 404
        with open(sites_file, 'r', encoding='utf-8') as f:
            sites_data = json.load(f)
        site_id_int = int(site_id)
        if str(site_id_int) in sites_data:
            locations = sites_data[str(site_id_int)].get('location', {})
            return jsonify({"success": True, "locations": locations})
        else:
            return jsonify({"success": False, "message": f"Site {site_id} not found"}), 404
    except Exception as e:
        logger.error(f"Error getting locations: {e}")
        return jsonify({"success": False, "message": str(e)}), 500


# ----------------------------------------
# Zone Management APIs
# ----------------------------------------
@app.route('/api/zones', methods=['GET'])
def get_zones():
    """Get all zones"""
    try:
        zone_manager = get_zone_manager()
        zones_data = zone_manager.load_zones()
        return jsonify({
            "success": True,
            "zones": zones_data['zones'],
            "enabled": zones_data['enabled']
        }), 200
    except Exception as e:
        logger.error(f"Error getting zones: {e}")
        return jsonify({"success": False, "message": str(e)}), 500


@app.route('/api/zones', methods=['POST'])
def create_zone():
    """Create a new zone"""
    try:
        zone_manager = get_zone_manager()
        data = request.get_json()
        
        # Validate request
        if 'zone' not in data:
            return jsonify({"success": False, "message": "Missing 'zone' in request"}), 400
        
        zone = data['zone']
        success, message = zone_manager.add_zone(zone)
        
        if success:
            logger.info(f"Zone created: {zone.get('name')}")
            return jsonify({"success": True, "message": message}), 200
        else:
            return jsonify({"success": False, "message": message}), 400
            
    except Exception as e:
        logger.error(f"Error creating zone: {e}")
        return jsonify({"success": False, "message": str(e)}), 500


@app.route('/api/zones/<int:zone_id>', methods=['PUT'])
def update_zone(zone_id):
    """Update an existing zone"""
    try:
        zone_manager = get_zone_manager()
        data = request.get_json()
        
        # Validate request
        if 'zone' not in data:
            return jsonify({"success": False, "message": "Missing 'zone' in request"}), 400
        
        zone = data['zone']
        success, message = zone_manager.update_zone(zone_id, zone)
        
        if success:
            logger.info(f"Zone {zone_id} updated")
            return jsonify({"success": True, "message": message}), 200
        else:
            return jsonify({"success": False, "message": message}), 400
            
    except Exception as e:
        logger.error(f"Error updating zone: {e}")
        return jsonify({"success": False, "message": str(e)}), 500


@app.route('/api/zones/<int:zone_id>', methods=['DELETE'])
def delete_zone(zone_id):
    """Delete a zone"""
    try:
        zone_manager = get_zone_manager()
        success, message = zone_manager.delete_zone(zone_id)
        
        if success:
            logger.info(f"Zone {zone_id} deleted")
            return jsonify({"success": True, "message": message}), 200
        else:
            return jsonify({"success": False, "message": message}), 404
            
    except Exception as e:
        logger.error(f"Error deleting zone: {e}")
        return jsonify({"success": False, "message": str(e)}), 500


@app.route('/api/zones/validate', methods=['POST'])
def validate_zones():
    """Validate zones for overlaps and other issues"""
    try:
        zone_manager = get_zone_manager()
        data = request.get_json()
        
        # Validate request
        if 'zones' not in data:
            return jsonify({"success": False, "message": "Missing 'zones' in request"}), 400
        
        zones = data['zones']
        is_valid, error_message = zone_manager.validate_zones_list(zones)
        
        if is_valid:
            return jsonify({"success": True, "message": "Zones are valid", "valid": True}), 200
        else:
            return jsonify({"success": True, "message": error_message, "valid": False}), 200
            
    except Exception as e:
        logger.error(f"Error validating zones: {e}")
        return jsonify({"success": False, "message": str(e)}), 500


@app.route('/api/zones/enabled', methods=['POST'])
def set_zones_enabled():
    """Enable or disable zone system"""
    try:
        zone_manager = get_zone_manager()
        data = request.get_json()
        
        if 'enabled' not in data:
            return jsonify({"success": False, "message": "Missing 'enabled' in request"}), 400
        
        enabled = bool(data['enabled'])
        success = zone_manager.set_enabled(enabled)
        
        if success:
            status = "enabled" if enabled else "disabled"
            logger.info(f"Zone system {status}")
            return jsonify({"success": True, "message": f"Zone system {status}"}), 200
        else:
            return jsonify({"success": False, "message": "Failed to update zone system status"}), 500
            
    except Exception as e:
        logger.error(f"Error setting zone enabled: {e}")
        return jsonify({"success": False, "message": str(e)}), 500


@app.route('/api/zones/image', methods=['POST'])
def upload_zone_image():
    """Upload reference image for zone configuration"""
    try:
        if 'image' not in request.files:
            return jsonify({"success": False, "message": "No image file provided"}), 400
        
        file = request.files['image']
        
        if file.filename == '':
            return jsonify({"success": False, "message": "No file selected"}), 400
        
        # Validate file type
        allowed_extensions = {'jpg', 'jpeg', 'png'}
        file_ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
        
        if file_ext not in allowed_extensions:
            return jsonify({"success": False, "message": "Invalid file type. Only JPEG/PNG allowed."}), 400
        
        # Generate filename
        from datetime import datetime
        now = datetime.now()
        filename = f"img_configzone_{now.strftime('%d-%m-%Y')}.jpg"
        
        # Save to upload_image directory
        upload_dir = os.path.join(os.path.dirname(__file__), 'upload_image')
        os.makedirs(upload_dir, exist_ok=True)
        
        filepath = os.path.join(upload_dir, filename)
        file.save(filepath)
        
        logger.info(f"✅ Zone reference image saved: {filepath}")
        
        return jsonify({
            "success": True,
            "message": "Reference image uploaded successfully",
            "filepath": f"upload_image/{filename}",
            "filename": filename
        }), 200
        
    except Exception as e:
        logger.error(f"Error uploading zone image: {e}")
        return jsonify({"success": False, "message": str(e)}), 500


@app.route('/api/zones/capture', methods=['POST'])
def capture_zone_image():
    """
    ✅ Capture image from configured camera
    """
    try:
        import cv2
        
        # ✅ อ่าน config โดยตรงจากไฟล์
        config_file = os.path.join(os.path.dirname(__file__), 'config', 'pallet_config.json')
        
        if not os.path.exists(config_file):
            raise Exception("Config file not found. Please configure camera first.")
        
        with open(config_file, 'r', encoding='utf-8') as f:
            cfg = json.load(f)
        
        # ดึงค่า camera config
        camera_id = cfg.get('camera', {}).get('selectedCamera', '0')
        resolution = cfg.get('camera', {}).get('resolution', {'width': 1280, 'height': 720})
        
        # แปลง camera_id เป็น int
        if isinstance(camera_id, str) and camera_id.isdigit():
            camera_id = int(camera_id)
        
        logger.info(f"📷 Capturing from camera {camera_id} at {resolution['width']}x{resolution['height']}")
        
        # Initialize camera
        cap = cv2.VideoCapture(camera_id, cv2.CAP_DSHOW)  # CAP_DSHOW for Windows
        
        if not cap.isOpened():
            raise Exception(f"Cannot open camera {camera_id}. Please check camera connection.")
        
        # Set resolution
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, resolution['width'])
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, resolution['height'])
        
        # Warm up (read 5 frames)
        for i in range(5):
            ret, frame = cap.read()
            if not ret:
                logger.warning(f"⚠️ Warm-up frame {i+1} failed")
        
        # Capture final frame
        ret, frame = cap.read()
        
        # Release camera immediately
        cap.release()
        
        if not ret or frame is None:
            raise Exception("Failed to capture frame from camera")
        
        # Save to temp directory
        temp_dir = os.path.join(os.path.dirname(__file__), 'upload_image', 'temp')
        os.makedirs(temp_dir, exist_ok=True)
        
        temp_filename = 'zone_capture.jpg'
        temp_path = os.path.join(temp_dir, temp_filename)
        
        # Save with high quality
        cv2.imwrite(temp_path, frame, [cv2.IMWRITE_JPEG_QUALITY, 95])
        
        # Return relative path
        relative_path = f"upload_image/temp/{temp_filename}"
        
        logger.info(f"✅ Image captured: {relative_path} ({frame.shape[1]}x{frame.shape[0]})")
        
        return jsonify({
            "success": True,
            "message": "Image captured successfully",
            "image_path": relative_path,
            "camera_id": camera_id,
            "width": frame.shape[1],
            "height": frame.shape[0]
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Capture error: {e}")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            "success": False,
            "message": f"Camera capture failed: {str(e)}\n\nPlease:\n1. Stop camera stream in Camera tab\n2. Check camera connection\n3. Verify camera configuration"
        }), 500


@app.route('/api/zones/save-image', methods=['POST'])
def save_zone_images():
    """
    Save master and polygon zone images
    บันทึกภาพต้นฉบับและภาพโซนที่วาด
    
    Expected format:
    {
        "master_image": "data:image/jpeg;base64,...",
        "polygon_image": "data:image/jpeg;base64,..."
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'master_image' not in data or 'polygon_image' not in data:
            return jsonify({
                "success": False,
                "message": "Missing master_image or polygon_image in request"
            }), 400
        
        # Create config_zone directory
        # สร้างโฟลเดอร์ config_zone
        upload_dir = os.path.join(
            os.path.dirname(__file__),
            'upload_image',
            'config_zone'
        )
        os.makedirs(upload_dir, exist_ok=True)
        
        # Generate filenames with current date
        # สร้างชื่อไฟล์พร้อมวันที่ปัจจุบัน
        from datetime import datetime
        now = datetime.now()
        date_str = now.strftime('%d-%m-%Y')
        
        master_filename = f"img_master_configzone.png" #master_filename = f"img_master_configzone_{date_str}.png"
        polygon_filename = f"img_polygon_configzone.png" #polygon_filename = f"img_polygon_configzone_{date_str}.png"
        
        # Save master image
        # บันทึกภาพต้นฉบับ
        import base64
        master_data = data['master_image']
        if master_data.startswith('data:image'):
            master_data = master_data.split(',')[1]
        
        master_bytes = base64.b64decode(master_data)
        master_path = os.path.join(upload_dir, master_filename)
        
        with open(master_path, 'wb') as f:
            f.write(master_bytes)
        
        # Save polygon image
        # บันทึกภาพโซนที่วาด
        polygon_data = data['polygon_image']
        if polygon_data.startswith('data:image'):
            polygon_data = polygon_data.split(',')[1]
        
        polygon_bytes = base64.b64decode(polygon_data)
        polygon_path = os.path.join(upload_dir, polygon_filename)
        
        with open(polygon_path, 'wb') as f:
            f.write(polygon_bytes)
        
        logger.info(f"✅ Zone images saved: {master_filename}, {polygon_filename}")
        
        return jsonify({
            "success": True,
            "message": "Zone images saved successfully",
            "master_path": f"upload_image/config_zone/{master_filename}",
            "polygon_path": f"upload_image/config_zone/{polygon_filename}"
        }), 200
        
    except Exception as e:
        logger.error(f"Error saving zone images: {e}")
        return jsonify({
            "success": False,
            "message": f"Save error: {str(e)}"
        }), 500


@app.route('/api/zones/save', methods=['POST'])
def save_zones_config():
    """
    Save zones configuration to zones.json
    บันทึกการตั้งค่าโซนลงใน zones.json
    
    Expected format:
    {
        "zones": [
            {
                "id": 1,
                "name": "Entry_Slot_1",
                "polygon": [[0.0781, 0.6944], [0.1562, 0.6944], ...],
                "threshold_percent": 45.0,
                "alert_threshold": 3000,
                "pallet_type": 1,
                "active": true
            }
        ]
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'zones' not in data:
            return jsonify({
                "success": False,
                "message": "Missing 'zones' in request"
            }), 400
        
        zones = data['zones']
        
        # Validate zones
        zone_manager = get_zone_manager()
        is_valid, error_message = zone_manager.validate_zones_list(zones)
        
        if not is_valid:
            return jsonify({
                "success": False,
                "message": f"Validation error: {error_message}"
            }), 400
        
        # Save zones
        existing_data = zone_manager.load_zones()
        zones_data = {
            "zones": zones,
            "enabled": existing_data.get('enabled', True)
        }
        
        if zone_manager.save_zones(zones_data):
            logger.info(f"✅ Zones configuration saved: {len(zones)} zones")
            
            # ✅ NEW: Return polygon image path
            polygon_image_path = "upload_image/config_zone/img_polygon_configzone.jpg"
            
            return jsonify({
                "success": True,
                "message": f"Zones saved successfully ({len(zones)} zones)",
                "polygon_image": polygon_image_path,  # ✅ เพิ่มบรรทัดนี้
                "zones": zones  # ✅ ส่ง zones กลับไปด้วย
            }), 200
        else:
            return jsonify({
                "success": False,
                "message": "Failed to save zones configuration"
            }), 500
        
    except Exception as e:
        logger.error(f"Error saving zones config: {e}")
        return jsonify({
            "success": False,
            "message": f"Save error: {str(e)}"
        }), 500

@app.route('/api/zones/latest-images', methods=['GET'])
def get_latest_zone_images():
    """Get paths to the latest zone configuration images"""
    try:
        config_zone_dir = os.path.join(
            os.path.dirname(__file__),
            'upload_image',
            'config_zone'
        )
        
        if not os.path.exists(config_zone_dir):
            return jsonify({
                "success": True,
                "master_image": None,
                "polygon_image": None,
                "message": "No zone images found"
            }), 200
        
        # ✅ รองรับทั้ง img_polygon_configzone.png และ img_polygon_configzone_DD-MM-YYYY.png   
        all_files = os.listdir(config_zone_dir)
        
        master_files = [f for f in all_files 
                       if f.startswith('img_master_configzone') and f.endswith('.png')]
        polygon_files = [f for f in all_files 
                        if f.startswith('img_polygon_configzone') and f.endswith('.png')]
        
        if master_files:
            master_files.sort(key=lambda f: os.path.getmtime(os.path.join(config_zone_dir, f)), reverse=True)
        if polygon_files:
            polygon_files.sort(key=lambda f: os.path.getmtime(os.path.join(config_zone_dir, f)), reverse=True)
        
        master_path = f"upload_image/config_zone/{master_files[0]}" if master_files else None
        polygon_path = f"upload_image/config_zone/{polygon_files[0]}" if polygon_files else None
        
        logger.info(f"📸 Latest images: master={master_path}, polygon={polygon_path}")
        
        return jsonify({
            "success": True,
            "master_image": master_path,
            "polygon_image": polygon_path,
            "message": "Latest images retrieved"
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting latest zone images: {e}")
        return jsonify({
            "success": False,
            "message": f"Error: {str(e)}"
        }), 500


# ----------------------------------------
# Main
# ----------------------------------------
if __name__ == '__main__':
    logger.info("🚀 Starting Pallet Detection Backend...")
    app.run(host='0.0.0.0', port=5000, debug=True)
"""
app.py - Flask Backend for Pallet Detection Config
Main API routes สำหรับ Web UI
"""

from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import config
from utils.database import test_database_connection, create_tables
from utils.network import test_network_connection
from utils.camera import test_camera, detect_cameras
from utils.gpio_control import LightController, test_gpio

# ========================================
# Flask App Setup
# ========================================
app = Flask(__name__)
CORS(app)  # อนุญาต Cross-Origin (ถ้า frontend อยู่คนละ port)

# สร้าง Light Controller
light_controller = LightController(red_pin=17, green_pin=27)


# ========================================
# Route: GET /api/config (ดึง config)
# ========================================
@app.route('/api/config', methods=['GET'])
def get_config():
    """ดึง config ปัจจุบัน"""
    cfg = config.load_config()
    return jsonify(cfg), 200


# ========================================
# Route: POST /api/config (บันทึก config)
# ========================================
@app.route('/api/config', methods=['POST'])
def save_config():
    """บันทึก config ใหม่"""
    try:
        data = request. get_json()
        if config.save_config(data):
            return jsonify({"success": True, "message": "✅ Config saved"}), 200
        else:
            return jsonify({"success":  False, "message": "❌ Save failed"}), 500
    except Exception as e: 
        return jsonify({"success":  False, "message": str(e)}), 400


# ========================================
# Route: POST /api/config/reset
# ========================================
@app. route('/api/config/reset', methods=['POST'])
def reset_config():
    """Reset config เป็นค่า default"""
    cfg = config.reset_config()
    return jsonify({"success": True, "config": cfg}), 200


# ========================================
# Route: POST /api/test/database
# ========================================
@app.route('/api/test/database', methods=['POST'])
def test_db():
    """ทดสอบ Database"""
    data = request.get_json()
    result = test_database_connection(
        host=data. get('host'),
        user=data.get('user'),
        password=data.get('password'),
        database=data.get('database'),
        port=data.get('port', 3306)
    )
    return jsonify(result), 200


# ========================================
# Route: GET /api/system/storage
# ========================================
import os
import shutil
@app.route('/api/system/storage', methods=['GET'])
def get_storage_info():
    """ดึงข้อมูล storage"""
    try:
        cfg = config. load_config()
        path = cfg['general']['imagePath']
        
        # ตรวจสอบว่า path มีอยู่จริงหรือไม่
        if not os.path.exists(path):
            # ถ้าไม่มี ให้สร้างโฟลเดอร์
            os.makedirs(path, exist_ok=True)
            return jsonify({
                "success": True,
                "data": {
                    "usedMB":  0,
                    "totalFiles": 0,
                    "totalDiskGB": round(shutil.disk_usage(os.path.dirname(path)).total / (1024**3), 2),
                    "freeDiskGB": round(shutil.disk_usage(os.path.dirname(path)).free / (1024**3), 2),
                    "path": path
                }
            })
        
        # นับไฟล์
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
        
        # Disk usage (ใช้ drive ของ path)
        try:
            disk = shutil. disk_usage(path)
            total_disk_gb = disk.total / (1024**3)
            free_disk_gb = disk.free / (1024**3)
        except:
            # ถ้า error ให้ใช้ current directory
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
        return jsonify({
            "success": False,
            "message": f"Error:  {str(e)}"
        })

# ========================================
# Route: POST /api/system/cleanup
# ========================================
@app.route('/api/system/cleanup', methods=['POST'])
def cleanup_old_images():
    """ลบรูปเก่า >7 วัน"""
    try:
        cfg = config.load_config()
        path = cfg['general']['imagePath']
        days = cfg['system']['autoCleanupDays']
        
        if not os.path.exists(path):
            return jsonify({"success": False, "message":  "Path not found"})
        
        import time
        now = time.time()
        deleted = 0
        
        for filename in os.listdir(path):
            filepath = os.path. join(path, filename)
            if os.path.isfile(filepath):
                if os.path.getmtime(filepath) < now - (days * 86400):
                    os.remove(filepath)
                    deleted += 1
        
        return jsonify({
            "success": True,
            "message": f"Deleted {deleted} old file(s)"
        })
        
    except Exception as e:
        return jsonify({"success": False, "message": str(e)})


# ========================================
# Route:  POST /api/test/network
# ========================================
@app.route('/api/test/network', methods=['POST'])
def test_net():
    """ทดสอบ Network/WiFi"""
    result = test_network_connection()
    return jsonify(result), 200


# ========================================
# Route: GET /api/camera/stream/<int:camera_id>
# ========================================
import cv2
def generate_frames(camera_index):
    """Generator สำหรับ MJPEG stream"""
    camera = cv2.VideoCapture(int(camera_index))
    while True:
        success, frame = camera.read()
        if not success:
            break
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    camera.release()

@app.route('/api/camera/stream/<int:camera_id>')
def video_stream(camera_id):
    """Stream camera feed"""
    from flask import Response
    return Response(generate_frames(camera_id),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


# ========================================
# Route: POST /api/test/camera
# ========================================
@app.route('/api/test/camera', methods=['POST'])
def test_cam():
    """ทดสอบกล้อง"""
    data = request.get_json()
    camera_index = data.get('camera', 0)
    result = test_camera(camera_index)
    return jsonify(result), 200


# ========================================
# Route: GET /api/camera/detect
# ========================================
@app.route('/api/camera/detect', methods=['GET'])
def detect_cam():
    """หากล้องที่เชื่อมต่ออยู่"""
    cameras = detect_cameras()
    return jsonify({"cameras": cameras}), 200


# ========================================
# Route: POST /api/test/gpio
# ========================================
@app.route('/api/test/gpio', methods=['POST'])
def test_gpio_route():
    """ทดสอบ GPIO"""
    result = test_gpio()
    return jsonify(result), 200


# ========================================
# Route:  POST /api/gpio/red/on
# ========================================
@app.route('/api/gpio/red/on', methods=['POST'])
def red_on():
    """เปิดไฟแดง"""
    result = light_controller.test_red()
    return jsonify(result), 200


# ========================================
# Route: POST /api/gpio/red/off
# ========================================
@app.route('/api/gpio/red/off', methods=['POST'])
def red_off():
    """ปิดไฟแดง"""
    result = light_controller.turn_off_red()
    return jsonify(result), 200


# ========================================
# Route: POST /api/gpio/green/on
# ========================================
@app.route('/api/gpio/green/on', methods=['POST'])
def green_on():
    """เปิดไฟเขียว"""
    result = light_controller.test_green()
    return jsonify(result), 200


# ========================================
# Route: POST /api/gpio/green/off
# ========================================
@app.route('/api/gpio/green/off', methods=['POST'])
def green_off():
    """ปิดไฟเขียว"""
    result = light_controller. turn_off_green()
    return jsonify(result), 200


# ========================================
# Route: GET /api/config/export
# ========================================
@app.route('/api/config/export', methods=['GET'])
def export_config():
    """Export config เป็นไฟล์ JSON"""
    return send_file(config.CONFIG_FILE, as_attachment=True, download_name='pallet_config.json')


# ========================================
# Main
# ========================================
if __name__ == '__main__':
    print("🚀 Starting Pallet Detection Backend...")
    app.run(host='0.0.0.0', port=5000, debug=True)
"""
config.py - Configuration File Handler
จัดการ Load/Save/Reset config จาก JSON file
"""

import json
import os
from datetime import datetime

# ========================================
# กำหนด Path ของ config file
# ========================================
CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'config', 'pallet_config.json')


# ========================================
# ฟังก์ชัน:  Load Config จากไฟล์
# ========================================
def load_config():
    """
    อ่าน config จากไฟล์ JSON
    Returns: 
        dict: configuration dictionary
    """
    try: 
        if not os.path.exists(CONFIG_FILE):
            # ถ้าไม่มีไฟล์ ให้สร้าง default
            print(f"⚠️  Config file not found.  Creating default at {CONFIG_FILE}")
            save_config(get_default_config())
        
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = json.load(f)
            print("✅ Config loaded successfully")
            return config
    except Exception as e:
        print(f"❌ Error loading config: {e}")
        return get_default_config()


# ========================================
# ฟังก์ชัน: Save Config ลงไฟล์
# ========================================
def save_config(config):
    """
    บันทึก config ลงไฟล์ JSON
    Args:
        config (dict): configuration dictionary
    Returns:
        bool: True if success, False otherwise
    """
    try:
        # สร้างโฟลเดอร์ถ้ายังไม่มี
        os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
        
        # อัพเดท lastUpdate
        config['general']['lastUpdate'] = datetime.now().strftime('%Y-%m-%d')
        
        # เขียนลงไฟล์
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
        
        print("✅ Config saved successfully")
        return True
    except Exception as e: 
        print(f"❌ Error saving config: {e}")
        return False


# ========================================
# ฟังก์ชัน: Reset Config เป็นค่า Default
# ========================================
def reset_config():
    """
    รีเซ็ต config เป็นค่า default
    Returns:
        dict: default configuration
    """
    default = get_default_config()
    save_config(default)
    print("✅ Config reset to default")
    return default


# ========================================
# ฟังก์ชัน: Get Default Config
# ========================================
def get_default_config():
    """
    คืนค่า default configuration
    Returns:
        dict:  default config
    """
    return {
        "general": {
            "imagePath": "/home/pi/pallet_detection/data_source",
            "version": "1.0",
            "lastUpdate": datetime.now().strftime('%Y-%m-%d'),
            "device": "Raspberry Pi 5",
            "siteCompany": "My Company",
            "siteLocation": "Building A"
        },
        "network":  {
            "database": {
                "host": "localhost",
                "user": "root",
                "password": "",
                "port": 3306,
                "database": "pallet_db"
            },
            "wifi": {
                "ssid":  "",
                "username": "",
                "password": ""
            },
            "lineNotify": {
                "token": "",
                "groupId": ""
            }
        },
        "detection":  {
            "modelPath": "runs/detect/pallet_v35/weights/best.pt",
            "confidenceThreshold":  0.75,
            "iouThreshold": 0.45,
            "imageSize":  1280,
            "deviceMode": "cpu",
            "captureInterval": 600,
            "alertThreshold": 30
        },
        "camera":  {
            "selectedCamera": "0",
            "resolution": {
                "width": 1280,
                "height": 720
            }
        },
        "gpio": {
            "redLightPin": 17,
            "greenLightPin": 27
        },
        "system": {
            "storageUsedMB": 0,
            "totalFiles": 0,
            "autoCleanupDays": 7
        }
    }


# ========================================
# ฟังก์ชัน: Update Config (เฉพาะบางส่วน)
# ========================================
def update_config(section, key, value):
    """
    อัพเดท config เฉพาะส่วน
    Args:
        section (str): หมวดหมู่ เช่น 'network', 'detection'
        key (str): key ที่ต้องการแก้
        value:  ค่าใหม่
    Returns: 
        bool: True if success
    """
    try:
        config = load_config()
        if section in config and key in config[section]:
            config[section][key] = value
            save_config(config)
            return True
        else:
            print(f"❌ Section '{section}' or key '{key}' not found")
            return False
    except Exception as e: 
        print(f"❌ Error updating config: {e}")
        return False
"""
utils/network.py - Network Connection Tester
ทดสอบการเชื่อมต่อ WiFi และ Internet
"""

import socket
import subprocess
import platform


# ========================================
# ฟังก์ชัน: Test Network Connection
# ========================================
def test_network_connection():
    """
    ทดสอบการเชื่อมต่อเครือข่าย
    Returns: 
        dict: {
            "success": bool,
            "message": str,
            "details":  dict
        }
    """
    try:
        # 1. เช็ค WiFi SSID (Linux/Raspberry Pi)
        ssid = get_wifi_ssid()
        
        # 2. เช็ค IP Address
        ip_address = get_local_ip()
        
        # 3. เช็ค Internet (ping google.com)
        internet = test_internet_connection()
        
        return {
            "success": True,
            "message":  "✅ Network connection active",
            "details": {
                "ssid": ssid,
                "ip_address": ip_address,
                "internet": internet
            }
        }
    
    except Exception as e: 
        return {
            "success":  False,
            "message": f"❌ Network error: {str(e)}",
            "details": {}
        }


# ========================================
# ฟังก์ชัน: Get WiFi SSID
# ========================================
def get_wifi_ssid():
    """
    ดึงชื่อ WiFi SSID ที่เชื่อมต่ออยู่
    Returns: 
        str: SSID name หรือ "Unknown"
    """
    try:
        system = platform.system()
        
        if system == "Linux": 
            # Raspberry Pi / Linux
            result = subprocess.check_output(
                ["iwgetid", "-r"],
                stderr=subprocess.DEVNULL,
                timeout=3
            ).decode('utf-8').strip()
            return result if result else "Not connected"
        
        elif system == "Windows":
            # Windows
            result = subprocess.check_output(
                ["netsh", "wlan", "show", "interfaces"],
                shell=True,
                timeout=3
            ).decode('utf-8')
            for line in result.split('\n'):
                if "SSID" in line and "BSSID" not in line:
                    return line.split(": ")[1].strip()
            return "Not connected"
        
        else:
            return "Unknown OS"
    
    except: 
        return "Unable to detect"


# ========================================
# ฟังก์ชัน: Get Local IP Address
# ========================================
def get_local_ip():
    """
    ดึง IP Address ของเครื่อง
    Returns:
        str: IP address
    """
    try: 
        # สร้าง socket ชั่วคราวเพื่อหา IP
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))  # Google DNS
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "No network"


# ========================================
# ฟังก์ชัน: Test Internet Connection
# ========================================
def test_internet_connection(host="8.8.8.8", port=53, timeout=3):
    """
    ทดสอบว่ามี internet หรือไม่ (ping Google DNS)
    Args:
        host (str): host to ping (default: 8.8.8.8 - Google DNS)
        port (int): port (default: 53 - DNS)
        timeout (int): timeout in seconds
    Returns:
        bool: True if connected
    """
    try: 
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except socket.error:
        return False
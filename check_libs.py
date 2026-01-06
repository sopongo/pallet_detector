#!/usr/bin/env python3
"""
check_libs.py - ตรวจสอบ Libraries ที่ติดตั้ง
"""

import sys

def check_library(name, import_name=None):
    """เช็คว่า library ติดตั้งแล้วหรือไม่"""
    if import_name is None:
        import_name = name
    
    try:
        module = __import__(import_name)
        version = getattr(module, '__version__', 'unknown')
        print(f"✅ {name: 20s} - Version: {version}")
        return True
    except ImportError:
        print(f"❌ {name:20s} - NOT INSTALLED")
        return False

print("=" * 60)
print("🔍 Checking Pallet Detector Libraries")
print("=" * 60)

libraries = [
    ('Flask', 'flask'),
    ('flask-cors', 'flask_cors'),
    ('OpenCV', 'cv2'),
    ('Ultralytics (YOLO)', 'ultralytics'),
    ('PyMySQL', 'pymysql'),
    ('Requests', 'requests'),
    ('psutil', 'psutil'),
    ('Pillow', 'PIL'),
    ('NumPy', 'numpy'),
    ('PyTorch', 'torch'),
]

# เช็ค optional libraries
optional_libs = [
    ('RPi.GPIO', 'RPi. GPIO'),
    ('picamera2', 'picamera2'),
]

print("\n📦 Core Libraries:")
print("-" * 60)
missing = []
for name, import_name in libraries: 
    if not check_library(name, import_name):
        missing.append(name)

print("\n🔧 Optional Libraries (Raspberry Pi):")
print("-" * 60)
for name, import_name in optional_libs:
    check_library(name, import_name)

print("\n" + "=" * 60)
if missing:
    print(f"⚠️  Missing {len(missing)} libraries: {', '.join(missing)}")
    print("\n💡 To install missing libraries, run:")
    print("   pip3 install -r requirements. txt")
else:
    print("✅ All core libraries are installed!")
print("=" * 60)
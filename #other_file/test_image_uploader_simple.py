"""
test_image_uploader_simple.py - Simple test for image uploader module
Tests without requiring full dependencies
"""

import os
import sys
import tempfile

# Test basic import
print("Testing image uploader module...")
print("=" * 60)

# Test 1: Test that config structure is correct
print("\n1. Testing config structure...")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config

cfg = config.get_default_config()
print(f"   Config loaded: {cfg is not None}")

# Check if network section exists
assert 'network' in cfg, "network section missing"
print(f"   ✅ 'network' section exists")

# Check if imageUpload section exists
assert 'imageUpload' in cfg['network'], "imageUpload section missing in network"
print(f"   ✅ 'imageUpload' section exists in network")

# Check required fields
required_fields = ['enabled', 'url', 'apiKey', 'defaultImage', 'timeout', 'maxRetries']
upload_cfg = cfg['network']['imageUpload']

for field in required_fields:
    assert field in upload_cfg, f"{field} missing in imageUpload config"
    print(f"   ✅ '{field}' field exists")

# Check field types and values
assert isinstance(upload_cfg['enabled'], bool), "enabled should be boolean"
assert isinstance(upload_cfg['url'], str), "url should be string"
assert isinstance(upload_cfg['apiKey'], str), "apiKey should be string"
assert isinstance(upload_cfg['defaultImage'], str), "defaultImage should be string"
assert isinstance(upload_cfg['timeout'], int), "timeout should be int"
assert isinstance(upload_cfg['maxRetries'], int), "maxRetries should be int"

print(f"\n   Config values:")
print(f"   - enabled: {upload_cfg['enabled']}")
print(f"   - url: {upload_cfg['url']}")
print(f"   - apiKey: {upload_cfg['apiKey']}")
print(f"   - defaultImage: {upload_cfg['defaultImage']}")
print(f"   - timeout: {upload_cfg['timeout']}")
print(f"   - maxRetries: {upload_cfg['maxRetries']}")

print("\n✅ Config structure test passed!")

# Test 2: Test image_uploader.py syntax
print("\n2. Testing image_uploader.py syntax...")
image_uploader_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    'utils',
    'image_uploader.py'
)

assert os.path.exists(image_uploader_path), "image_uploader.py not found"
print(f"   ✅ image_uploader.py exists at {image_uploader_path}")

# Compile the file
import py_compile
try:
    py_compile.compile(image_uploader_path, doraise=True)
    print(f"   ✅ image_uploader.py compiles successfully")
except py_compile.PyCompileError as e:
    print(f"   ❌ Syntax error: {e}")
    sys.exit(1)

print("\n✅ Syntax test passed!")

# Test 3: Check that required imports are present in image_uploader.py
print("\n3. Checking imports in image_uploader.py...")
with open(image_uploader_path, 'r') as f:
    content = f.read()
    
required_imports = ['import requests', 'import os', 'import time', 'import config', 'from utils.logger import setup_logger']
for imp in required_imports:
    assert imp in content, f"Missing import: {imp}"
    print(f"   ✅ Found: {imp}")

print("\n✅ Import check passed!")

# Test 4: Check that ImageUploader class exists
print("\n4. Checking ImageUploader class structure...")
assert 'class ImageUploader:' in content, "ImageUploader class not found"
print(f"   ✅ ImageUploader class exists")

assert 'def __init__(self):' in content, "__init__ method not found"
print(f"   ✅ __init__ method exists")

assert 'def upload_image(self, image_path):' in content, "upload_image method not found"
print(f"   ✅ upload_image method exists")

print("\n✅ Class structure check passed!")

# Test 5: Verify integration in detection_service.py
print("\n5. Checking detection_service.py integration...")
detection_service_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    'detection_service.py'
)

with open(detection_service_path, 'r') as f:
    content = f.read()

# Check import
assert 'from utils.image_uploader import ImageUploader' in content, "ImageUploader import not found"
print(f"   ✅ ImageUploader import found")

# Check initialization
assert 'self.uploader = ImageUploader()' in content, "uploader initialization not found"
print(f"   ✅ uploader initialization found")

# Check usage
assert 'upload_result = self.uploader.upload_image' in content, "upload_image call not found"
print(f"   ✅ upload_image call found")

print("\n✅ detection_service.py integration check passed!")

# Test 6: Verify line_messaging.py changes
print("\n6. Checking line_messaging.py changes...")
line_messaging_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    'utils',
    'line_messaging.py'
)

with open(line_messaging_path, 'r') as f:
    content = f.read()

# Check that it uses pallet_data['image_url']
assert "pallet_data.get('image_url'" in content, "image_url usage not found"
print(f"   ✅ Uses pallet_data['image_url']")

# Check that old hardcoded URL is removed
old_url = "https://ebooking.jwdcoldchain.com/sopon_test/IMG_20260108_003143_detected.jpg"
assert old_url not in content, "Old hardcoded URL still present"
print(f"   ✅ Old hardcoded URL removed")

print("\n✅ line_messaging.py changes check passed!")

print("\n" + "=" * 60)
print("ALL TESTS PASSED! ✅")
print("=" * 60)
print("\nSummary:")
print("  ✅ Config structure is correct")
print("  ✅ image_uploader.py syntax is valid")
print("  ✅ All required imports are present")
print("  ✅ ImageUploader class structure is correct")
print("  ✅ detection_service.py integration is correct")
print("  ✅ line_messaging.py uses uploaded image URL")

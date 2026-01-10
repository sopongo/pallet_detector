"""
test_image_uploader.py - Test image uploader module
"""

import os
import sys
import tempfile

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.image_uploader import ImageUploader
import config

def create_test_image():
    """Create a temporary test image (simple file)"""
    temp_dir = tempfile.gettempdir()
    temp_path = os.path.join(temp_dir, "test_image_uploader.jpg")
    
    # Create a dummy JPEG file
    with open(temp_path, 'wb') as f:
        # Write a minimal JPEG header
        f.write(b'\xFF\xD8\xFF\xE0\x00\x10JFIF')
        f.write(b'\x00' * 100)  # Some dummy data
        f.write(b'\xFF\xD9')  # JPEG end marker
    
    return temp_path

def test_uploader_disabled():
    """Test uploader when disabled"""
    print("=" * 60)
    print("Test 1: Upload disabled")
    print("=" * 60)
    
    # Temporarily modify config
    cfg = config.load_config()
    original_enabled = cfg.get('network', {}).get('imageUpload', {}).get('enabled', True)
    
    # Create uploader
    uploader = ImageUploader()
    uploader.enabled = False
    
    # Create test image
    test_image = create_test_image()
    
    # Try upload
    result = uploader.upload_image(test_image)
    
    print(f"Result: {result}")
    print(f"Success: {result.get('success')}")
    print(f"Skipped: {result.get('skipped')}")
    print(f"URL: {result.get('url')}")
    
    # Cleanup
    if os.path.exists(test_image):
        os.remove(test_image)
    
    assert result.get('success') == True
    assert result.get('skipped') == True
    assert result.get('url') == uploader.default_image
    
    print("✅ Test passed!\n")

def test_uploader_no_config():
    """Test uploader when config incomplete"""
    print("=" * 60)
    print("Test 2: Upload config incomplete")
    print("=" * 60)
    
    # Create uploader
    uploader = ImageUploader()
    uploader.enabled = True
    uploader.url = ""  # No URL configured
    uploader.api_key = ""  # No API key
    
    # Create test image
    test_image = create_test_image()
    
    # Try upload
    result = uploader.upload_image(test_image)
    
    print(f"Result: {result}")
    print(f"Success: {result.get('success')}")
    print(f"URL: {result.get('url')}")
    print(f"Message: {result.get('message')}")
    
    # Cleanup
    if os.path.exists(test_image):
        os.remove(test_image)
    
    assert result.get('success') == False
    assert result.get('url') == uploader.default_image
    assert result.get('message') == "Upload config not set"
    
    print("✅ Test passed!\n")

def test_uploader_file_not_found():
    """Test uploader when file doesn't exist"""
    print("=" * 60)
    print("Test 3: File not found")
    print("=" * 60)
    
    # Create uploader
    uploader = ImageUploader()
    uploader.enabled = True
    uploader.url = "https://example.com/upload"
    uploader.api_key = "test-key"
    
    # Try upload non-existent file
    result = uploader.upload_image("/path/to/nonexistent/file.jpg")
    
    print(f"Result: {result}")
    print(f"Success: {result.get('success')}")
    print(f"URL: {result.get('url')}")
    print(f"Message: {result.get('message')}")
    
    assert result.get('success') == False
    assert result.get('url') == uploader.default_image
    assert result.get('message') == "File not found"
    
    print("✅ Test passed!\n")

def test_uploader_initialization():
    """Test uploader initialization"""
    print("=" * 60)
    print("Test 4: Uploader initialization")
    print("=" * 60)
    
    uploader = ImageUploader()
    
    print(f"Enabled: {uploader.enabled}")
    print(f"URL: {uploader.url}")
    print(f"API Key: {uploader.api_key[:20] if uploader.api_key else 'Not set'}...")
    print(f"Default Image: {uploader.default_image}")
    print(f"Timeout: {uploader.timeout}")
    print(f"Max Retries: {uploader.max_retries}")
    
    assert hasattr(uploader, 'enabled')
    assert hasattr(uploader, 'url')
    assert hasattr(uploader, 'api_key')
    assert hasattr(uploader, 'default_image')
    assert hasattr(uploader, 'timeout')
    assert hasattr(uploader, 'max_retries')
    
    print("✅ Test passed!\n")

if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("IMAGE UPLOADER TESTS")
    print("=" * 60 + "\n")
    
    try:
        test_uploader_initialization()
        test_uploader_disabled()
        test_uploader_no_config()
        test_uploader_file_not_found()
        
        print("=" * 60)
        print("ALL TESTS PASSED! ✅")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

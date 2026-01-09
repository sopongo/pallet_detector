"""
utils/image_uploader.py - Image Upload to SSL Server
อัพโหลดรูปไปยัง SSL server เพื่อให้ได้ HTTPS URL
"""

import requests
import os
import time
import config
from utils.logger import setup_logger

logger = setup_logger()

class ImageUploader:
    """Class สำหรับอัพโหลดรูปไป SSL server"""
    
    def __init__(self):
        """Initialize uploader"""
        self.cfg = config.load_config()
        upload_cfg = self.cfg.get('network', {}).get('imageUpload', {})
        
        # Get configuration values
        self.enabled = upload_cfg.get('enabled', True)
        self.url = upload_cfg.get('url', '')
        self.api_key = upload_cfg.get('apiKey', '')
        self.default_image = upload_cfg.get('defaultImage', 'https://sb.kaleidousercontent.com/67418/960x550/3e324c0328/individuals-removed.png')
        self.timeout = upload_cfg.get('timeout', 30)
        self.max_retries = upload_cfg.get('maxRetries', 1)
        
        # Validate configuration
        if not self.enabled:
            logger.info("📤 Image upload is disabled")
        elif not self.url or not self.api_key or self.api_key == 'your-secret-api-key-here':
            logger.warning("⚠️ Image upload enabled but URL or API key not configured properly")
            logger.warning("   Upload will be skipped and default image will be used")
    
    def upload_image(self, image_path):
        """
        อัพโหลดรูปไปยัง SSL server
        
        Args:
            image_path (str): Path ของรูปที่จะอัพโหลด
            
        Returns:
            dict: {"success": True/False, "url": "https://...", "message": "..."}
        """
        # ตรวจสอบว่า enabled หรือไม่
        if not self.enabled:
            logger.info("⏭️ Upload skipped (disabled)")
            return {
                "success": True,
                "url": self.default_image,
                "message": "Upload disabled, using default image",
                "skipped": True
            }
        
        # ตรวจสอบ config
        if not self.url or not self.api_key or self.api_key == 'your-secret-api-key-here':
            logger.warning("⚠️ Upload config incomplete or placeholder key detected, using default image")
            return {
                "success": False,
                "url": self.default_image,
                "message": "Upload config not set properly"
            }
        
        # ตรวจสอบไฟล์
        if not os.path.exists(image_path):
            logger.error(f"❌ File not found: {image_path}")
            return {
                "success": False,
                "url": self.default_image,
                "message": "File not found"
            }
        
        # พยายาม upload (with retry)
        for attempt in range(self.max_retries + 1):
            try:
                if attempt > 0:
                    logger.info(f"🔄 Retry upload attempt {attempt}/{self.max_retries}")
                    time.sleep(2)  # รอ 2 วินาทีก่อน retry
                
                logger.info(f"📤 Uploading image: {os.path.basename(image_path)}")
                
                # เปิดไฟล์และ upload
                with open(image_path, 'rb') as f:
                    files = {'image': (os.path.basename(image_path), f, 'image/jpeg')}
                    headers = {'X-API-Key': self.api_key}
                    
                    response = requests.post(
                        self.url,
                        files=files,
                        headers=headers,
                        timeout=self.timeout
                    )
                
                # ตรวจสอบ response
                if response.status_code == 200:
                    data = response.json()
                    
                    if data.get('success'):
                        image_url = data.get('url')
                        logger.info(f"✅ Upload successful: {image_url}")
                        return {
                            "success": True,
                            "url": image_url,
                            "message": "Upload successful"
                        }
                    else:
                        error_msg = data.get('message', 'Unknown error')
                        logger.error(f"❌ Upload failed: {error_msg}")
                        
                        # ถ้ายังมี retry → ลองใหม่
                        if attempt < self.max_retries:
                            continue
                        
                        # ถ้าหมด retry → ใช้ default
                        return {
                            "success": False,
                            "url": self.default_image,
                            "message": error_msg
                        }
                else:
                    error_msg = f"HTTP {response.status_code}: {response.text[:100]}"
                    logger.error(f"❌ Upload error: {error_msg}")
                    
                    # ถ้ายังมี retry → ลองใหม่
                    if attempt < self.max_retries:
                        continue
                    
                    # ถ้าหมด retry → ใช้ default
                    return {
                        "success": False,
                        "url": self.default_image,
                        "message": error_msg
                    }
                    
            except requests.exceptions.Timeout:
                logger.error(f"❌ Upload timeout ({self.timeout}s)")
                
                if attempt < self.max_retries:
                    continue
                
                return {
                    "success": False,
                    "url": self.default_image,
                    "message": "Timeout"
                }
                
            except Exception as e:
                logger.error(f"❌ Upload exception: {e}")
                
                if attempt < self.max_retries:
                    continue
                
                return {
                    "success": False,
                    "url": self.default_image,
                    "message": str(e)
                }
        
        # ถ้า loop จบแล้วยังไม่ return (ไม่ควรเกิด)
        return {
            "success": False,
            "url": self.default_image,
            "message": "Max retries exceeded"
        }


# Helper function
def upload_image(image_path):
    """Shortcut function"""
    default_image = 'https://sb.kaleidousercontent.com/67418/960x550/3e324c0328/individuals-removed.png'
    try:
        uploader = ImageUploader()
        return uploader.upload_image(image_path)
    except Exception as e:
        logger.error(f"❌ Upload error: {e}")
        cfg = config.load_config()
        default_image = cfg.get('network', {}).get('imageUpload', {}).get('defaultImage', default_image)
        return {
            "success": False,
            "url": default_image,
            "message": str(e)
        }

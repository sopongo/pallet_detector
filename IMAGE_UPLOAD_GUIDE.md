# Image Upload to SSL Server - Implementation Guide

## 📋 Overview

This feature enables automatic upload of annotated pallet detection images to an SSL server, providing HTTPS URLs for use in LINE Flex Messages. When uploads fail, the system automatically falls back to a default image.

## 🔄 Upload Flow

```
1. Detect → Create IMG_YYYYMMDD_HHMMSS_detected.jpg
2. Upload → SSL server via HTTPS API
3. Get URL → https://jaiangelbot.jwdcoldchain.com/uploads-temp/line_push/2026-01-09/IMG_xxx.jpg
4. Send LINE → Use HTTPS URL in Flex Message
5. Fallback → If upload fails, use default image
```

## 🏗️ Architecture

### Python Components

#### 1. `utils/image_uploader.py`
- **ImageUploader class**: Handles image upload to SSL server
- **Features**:
  - API key authentication via `X-API-Key` header
  - Retry logic (default: 1 retry = 2 total attempts)
  - Automatic fallback to default image on failure
  - Timeout handling (default: 30 seconds)
  - Comprehensive logging

#### 2. `config.py`
Added `imageUpload` configuration section:
```python
'imageUpload': {
    'enabled': True,
    'url': 'https://jaiangelbot.jwdcoldchain.com/console/jai_receive_photo.php',
    'apiKey': 'your-secret-api-key-here',  # ⚠️ Must be changed!
    'defaultImage': 'https://sb.kaleidousercontent.com/67418/960x550/3e324c0328/individuals-removed.png',
    'timeout': 30,
    'maxRetries': 1
}
```

#### 3. `detection_service.py`
- Imports and initializes `ImageUploader`
- Uploads annotated image after detection
- Updates overtime pallets with uploaded image URL
- Handles upload failures gracefully

#### 4. `utils/line_messaging.py`
- Uses `pallet_data['image_url']` from uploaded/fallback source
- Removed hardcoded image URL
- Automatic fallback to default image if not provided

### Server Component

#### `jai_receive_photo.php`
Server-side PHP script that:
- Authenticates requests via `X-API-Key` header
- Validates file type (JPEG only) and size (max 5MB)
- Organizes uploads by date: `uploads-temp/line_push/{YYYY-MM-DD}/`
- Returns JSON response with HTTPS URL

## 📥 Installation

### Step 1: Pull Latest Code
```bash
git pull origin main
```

### Step 2: Configure API Key

**Python side** - Edit `config.py` or `config/pallet_config.json`:
```json
{
  "network": {
    "imageUpload": {
      "enabled": true,
      "apiKey": "YOUR-ACTUAL-SECRET-KEY"
    }
  }
}
```

**Server side** - Edit `jai_receive_photo.php`:
```php
$valid_api_key = "YOUR-ACTUAL-SECRET-KEY";  // Must match Python config!
```

⚠️ **Important**: API keys must match on both sides!

### Step 3: Upload PHP Script

Upload `jai_receive_photo.php` to your server:
```
https://jaiangelbot.jwdcoldchain.com/console/jai_receive_photo.php
```

### Step 4: Create Upload Directory

On the server, create directory with proper permissions:
```bash
mkdir -p uploads-temp/line_push
chmod 755 uploads-temp
```

### Step 5: Restart Service

```bash
python detection_service.py
```

## 🧪 Testing

### Test 1: Verify Configuration
```bash
python test_image_uploader_simple.py
```

Expected output:
```
============================================================
ALL TESTS PASSED! ✅
============================================================
```

### Test 2: Check Upload Success
Monitor the log file:
```bash
tail -f logs/detection_service.log | grep "Upload\|📤\|✅"
```

Successful upload:
```
📤 Uploading image: IMG_20260109_123456_detected.jpg
✅ Upload successful: https://jaiangelbot.jwdcoldchain.com/uploads-temp/line_push/2026-01-09/IMG_xxx.jpg
📷 Image URL added to 1 overtime alert(s)
```

### Test 3: Verify Upload Failure Handling
Temporarily set wrong API key in config and check logs:
```
📤 Uploading image...
❌ Upload error: HTTP 401
⚠️ Upload failed, using default: HTTP 401
📷 Image URL added to 1 overtime alert(s)
```

### Test 4: Check LINE Messages
Verify that LINE Flex Messages show:
- **Success case**: Actual pallet image (HTTPS URL)
- **Failure case**: Default fallback image

## 🔧 Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `enabled` | boolean | `true` | Enable/disable upload feature |
| `url` | string | (required) | SSL server endpoint URL |
| `apiKey` | string | (required) | Secret API key for authentication |
| `defaultImage` | string | (provided) | Fallback image URL |
| `timeout` | integer | `30` | Upload timeout in seconds |
| `maxRetries` | integer | `1` | Number of retry attempts |

## 📊 Behavior

### When Upload is Enabled
1. After pallet detection, annotated image is uploaded to SSL server
2. If successful: Use HTTPS URL from server response
3. If failed: Retry up to `maxRetries` times
4. If all retries fail: Use `defaultImage` URL
5. All overtime alerts get the same image URL

### When Upload is Disabled
- System immediately uses `defaultImage` URL
- No upload attempts are made
- Logged as "Upload skipped (disabled)"

### When Config is Incomplete
- Missing URL or API key → Use `defaultImage`
- Placeholder API key detected → Use `defaultImage`
- Warning logged: "Upload config not set properly"

## 🐛 Troubleshooting

### Issue: Upload Always Fails with 401
**Cause**: API key mismatch between Python and PHP
**Solution**: Verify both keys match exactly

### Issue: Upload Timeout
**Cause**: Network issue or server slow
**Solution**: 
- Increase `timeout` value in config
- Check network connectivity
- Verify server is responding

### Issue: File Not Found Error
**Cause**: Annotated image not created
**Solution**: Check detection process logs

### Issue: "Invalid file type" Error
**Cause**: Non-JPEG file attempted
**Solution**: Verify detector creates JPEG files

### Issue: LINE Shows Default Image
**Cause**: Upload failed or disabled
**Solution**: Check logs for upload errors

## 📝 Important Notes

1. **API Key Security**: Never commit actual API keys to version control
2. **Server Permissions**: Ensure `uploads-temp/` is writable (755)
3. **Disk Space**: Monitor server disk usage as images accumulate
4. **Image Cleanup**: Consider implementing automatic cleanup of old images
5. **Testing**: Always test upload functionality before production deployment
6. **Monitoring**: Regularly check logs for upload success rate

## 🔒 Security Considerations

- API key authentication required for all uploads
- File type validation (JPEG only)
- File size limit (5MB max)
- MIME type verification
- Proper error handling without exposing sensitive info

## 📈 Monitoring

### Key Metrics to Monitor
1. Upload success rate
2. Upload response time
3. Retry frequency
4. Fallback usage rate
5. Server disk usage

### Log Messages to Watch
- `✅ Upload successful` - Success
- `❌ Upload error` - Failed uploads
- `🔄 Retry upload attempt` - Retries happening
- `⚠️ Upload failed, using default` - Fallback in use

## 🆘 Support

If issues persist:
1. Check all configuration values
2. Verify server is accessible
3. Test PHP script directly with curl
4. Review server error logs
5. Verify network connectivity

---

**Last Updated**: 2026-01-09
**Version**: 1.0
**Status**: ✅ Production Ready

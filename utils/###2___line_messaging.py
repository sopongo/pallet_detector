"""
utils/line_messaging.py - LINE Official Account Messaging API
ส่ง message ผ่าน LINE OA เข้า Group
"""

import requests
import json
from datetime import datetime
import config
from utils.logger import setup_logger

logger = setup_logger()

class LineMessagingAPI: 
    """Class สำหรับส่งข้อความผ่าน LINE OA"""
    
    def __init__(self):
        """Initialize LINE Messaging API"""
        self.cfg = config.load_config()
        self.channel_access_token = self.cfg['network']['lineNotify']['token']
        self.group_id = self.cfg['network']['lineNotify']. get('groupId', '')
        self.api_url = 'https://api.line.me/v2/bot/message'
        
        if self.group_id and not self.group_id.startswith('C'):
            logger.warning(f"⚠️ Group ID should start with 'C', got: {self.group_id[: 5]}...")
    
    def get_headers(self):
        """สร้าง headers สำหรับ API request"""
        return {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.channel_access_token}'
        }
    
    def push_to_group(self, messages):
        """ส่งข้อความเข้า Group"""
        try:
            if not self.group_id:
                logger.error("❌ Group ID not configured")
                return {'success': False, 'message':  'Group ID not set'}
            
            url = f'{self.api_url}/push'
            payload = {'to': self.group_id, 'messages': messages}
            
            logger.info(f"📤 Sending to Group: {self.group_id[: 10]}...")
            
            response = requests.post(url, headers=self.get_headers(), data=json.dumps(payload), timeout=10)
            
            if response. status_code == 200:
                logger.info(f"✅ LINE message sent to group")
                return {'success':  True, 'message': 'Sent successfully'}
            else:
                error_msg = response.text
                logger.error(f"❌ LINE API error: {response.status_code} - {error_msg}")
                
                if response.status_code == 400:
                    return {'success': False, 'message': 'Invalid request'}
                elif response.status_code == 401:
                    return {'success': False, 'message': 'Invalid Token'}
                elif response.status_code == 403:
                    return {'success':  False, 'message': 'Bot not in group'}
                else:
                    return {'success':  False, 'message': f'HTTP {response.status_code}'}
                
        except requests.exceptions.Timeout:
            logger. error("❌ LINE API timeout")
            return {'success': False, 'message': 'Timeout'}
        except Exception as e:
            logger.error(f"❌ LINE error: {e}")
            return {'success': False, 'message':  str(e)}
    
    def send_text_message(self, text):
        """ส่งข้อความธรรมดา"""
        messages = [{'type': 'text', 'text': text}]
        return self.push_to_group(messages)
    
    def send_overtime_alert(self, pallet_info):
        """ส่ง alert พาเลทเกินเวลา (Text Message)"""
        try:
            # ดึงข้อมูล
            pallet_id = pallet_info.get('pallet_id', 'N/A')
            pallet_name = pallet_info.get('pallet_name', 'N/A')
            duration = pallet_info. get('duration', 0)
            site = pallet_info. get('site', 'N/A')
            location = pallet_info.get('location', 'N/A')
            
            # แปลง datetime
            first_detected = pallet_info.get('first_detected_at')
            last_detected = pallet_info.get('last_detected_at')
            
            if isinstance(first_detected, datetime):
                first_detected_str = first_detected.strftime('%H:%M')
            else:
                first_detected_str = 'N/A'
            
            if isinstance(last_detected, datetime):
                last_detected_str = last_detected. strftime('%H:%M')
            else:
                last_detected_str = 'N/A'
            
            # ✅ สร้างข้อความแบบ Text
            message_text = f"""⚠️ OVERDUE PALLET ALERT ⚠️
            🔴 Pallet: #{pallet_id} ({pallet_name})
            📍 Site: {site}
            🏢 Location: {location}

            ⏰ Detected at: {first_detected_str}
            ⏰ Last detected: {last_detected_str}
            🔴 Over time:  {duration:.1f} minute(s)

            ⚠️ Please check and put away immediately!"""
            
            logger.info(f"📤 Sending overtime alert for Pallet #{pallet_id}")
            
            flexible_message = {
                "type": "flex",
                "altText": "Overtime Pallet Alert",
                "contents": {
                }
            }
            # ส่ง text message
            result = self.send_text_message(message_text)
            
            if result['success']: 
                logger.info(f"✅ Overtime alert sent")
            else:
                logger. error(f"❌ Overtime alert failed: {result['message']}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Exception: {e}", exc_info=True)
            return {'success': False, 'message': str(e)}
    
    def test_connection(self):
        """ทดสอบการเชื่อมต่อ"""
        if not self.group_id:
            return {'success': False, 'message': '❌ Group ID not configured'}
        if not self.channel_access_token:
            return {'success': False, 'message': '❌ Token not configured'}
        
        message = f"🧪 Test\n\n✅ OK!\n\n📅 {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
        return self.send_text_message(message)


# Helper Functions
def send_pallet_alert(pallet_info):
    """Shortcut"""
    try:
        return LineMessagingAPI().send_overtime_alert(pallet_info)
    except Exception as e: 
        logger.error(f"❌ Error:  {e}")
        return {'success': False, 'message': str(e)}

def test_line_connection():
    """Shortcut"""
    try: 
        return LineMessagingAPI().test_connection()
    except Exception as e:
        logger.error(f"❌ Error:  {e}")
        return {'success': False, 'message': str(e)}
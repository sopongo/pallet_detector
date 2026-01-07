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
        
        # ✅ Validate Group ID
        if self.group_id and not self.group_id.startswith('C'):
            logger.warning(f"⚠️ Group ID should start with 'C', got: {self.group_id[: 5]}...")
    
    def get_headers(self):
        """สร้าง headers สำหรับ API request"""
        return {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.channel_access_token}'
        }
    
    def push_to_group(self, messages):
        """
        ส่งข้อความเข้า Group (Push Message)
        
        Args: 
            messages (list): รายการข้อความ
            
        Returns:
            dict: {'success': bool, 'message': str}
        """
        try:
            # ✅ เช็คว่ามี Group ID หรือไม่
            if not self.group_id:
                logger.error("❌ Group ID not configured")
                return {'success': False, 'message': 'Group ID not set'}
            
            # ✅ ส่งผ่าน Push API
            url = f'{self.api_url}/push'
            payload = {
                'to': self.group_id,
                'messages': messages
            }
            
            logger.info(f"📤 Sending to Group: {self.group_id[: 10]}...")
            
            response = requests.post(
                url,
                headers=self.get_headers(),
                data=json.dumps(payload),
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info(f"✅ LINE message sent to group")
                return {'success': True, 'message': 'Sent successfully'}
            else:
                error_msg = response.text
                logger.error(f"❌ LINE API error: {response.status_code} - {error_msg}")
                
                # ✅ แสดง error ที่เข้าใจง่าย
                if response.status_code == 400:
                    return {'success':  False, 'message': 'Invalid Group ID or Token'}
                elif response.status_code == 401:
                    return {'success': False, 'message': 'Invalid Channel Access Token'}
                elif response. status_code == 403:
                    return {'success':  False, 'message': 'Bot not in the group'}
                else:
                    return {'success':  False, 'message': f'HTTP {response.status_code}'}
                
        except requests.exceptions.Timeout:
            logger. error("❌ LINE API timeout")
            return {'success': False, 'message': 'Request timeout'}
        except Exception as e:
            logger.error(f"❌ LINE Messaging error: {e}")
            return {'success': False, 'message': str(e)}
    
    def send_text_message(self, text):
        """
        ส่งข้อความธรรมดาเข้า Group
        
        Args:
            text (str): ข้อความ
            
        Returns: 
            dict: result
        """
        messages = [{'type': 'text', 'text': text}]
        return self.push_to_group(messages)
    
    def send_overtime_alert(self, pallet_info):
        """
        ส่ง alert พาเลทเกินเวลา (Text Message ธรรมดา)
        
        Args:
            pallet_info (dict): ข้อมูลพาเลท
            
        Returns:
            dict: {'success': bool, 'message': str}
        """
        try:
            # ✅ ส่งข้อความสั้นๆ ธรรมดา
            message_text = "มีพาเลทเกินเวลา"
            
            logger.info(f"📤 Sending overtime alert: {message_text}")
            
            # ใช้ method ส่ง text ที่มีอยู่แล้ว
            result = self.send_text_message(message_text)
            
            if result['success']:
                logger.info(f"✅ Overtime alert sent successfully")
            else:
                logger.error(f"❌ Overtime alert failed: {result['message']}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Exception in send_overtime_alert: {e}", exc_info=True)
            return {
                'success': False,
                'message': str(e)
            }
    
    def test_connection(self):
        """
        ทดสอบการเชื่อมต่อ LINE OA
        
        Returns:
            dict: result
        """
        if not self.group_id:
            return {'success': False, 'message': '❌ Group ID not configured'}
        
        if not self.channel_access_token:
            return {'success': False, 'message': '❌ Channel Access Token not configured'}
        
        message = f"🧪 LINE OA Test Message\n\n✅ Connection successful!\n\n📅 {datetime.now().strftime('%d/%m/%Y')}\n🕐 {datetime.now().strftime('%H:%M:%S')}"
        
        return self.send_text_message(message)


# ========================================
# Helper Functions
# ========================================

def send_pallet_alert(pallet_info):
    """
    ส่ง alert พาเลทเกินเวลา (Shortcut function)
    
    Args:
        pallet_info (dict): ข้อมูลพาเลท
        
    Returns:
        dict: result
    """
    try:
        line_api = LineMessagingAPI()
        return line_api. send_overtime_alert(pallet_info)
    except Exception as e:
        logger.error(f"❌ Send alert error: {e}")
        return {'success': False, 'message': str(e)}


def test_line_connection():
    """
    ทดสอบการเชื่อมต่อ (Shortcut function)
    
    Returns:
        dict: result
    """
    try:
        line_api = LineMessagingAPI()
        return line_api.test_connection()
    except Exception as e: 
        logger.error(f"❌ Test connection error: {e}")
        return {'success': False, 'message': str(e)}
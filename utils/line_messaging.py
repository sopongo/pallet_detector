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
        ส่ง alert พาเลทค้างเกินเวลา (Flex Message) เข้า Group
        
        Args:
            pallet_info (dict): ข้อมูลพาเลท
            
        Returns:
            dict: result
        """
        pallet_id = pallet_info. get('pallet_id', 'N/A')
        duration = pallet_info.get('duration', 0)
        site = pallet_info.get('site', 'N/A')
        location = pallet_info.get('location', 'N/A')
        image_url = pallet_info. get('image_url', '')
        
        # ✅ สร้าง Flex Message
        flex_content = {
            "type": "bubble",
            "header": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "⚠️ PALLET OVERTIME ALERT",
                        "color": "#ffffff",
                        "weight": "bold",
                        "size": "lg",
                        "align": "center"
                    }
                ],
                "backgroundColor": "#FF4444",
                "paddingAll": "20px"
            },
            "body":  {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": f"Pallet #{pallet_id}",
                        "weight": "bold",
                        "size": "xxl",
                        "margin": "md",
                        "color": "#1e1e1e"
                    },
                    {
                        "type": "separator",
                        "margin": "lg"
                    },
                    {
                        "type": "box",
                        "layout": "vertical",
                        "margin": "lg",
                        "spacing": "md",
                        "contents": [
                            {
                                "type": "box",
                                "layout": "baseline",
                                "spacing": "sm",
                                "contents": [
                                    {"type": "text", "text":  "📍 Site:", "color": "#aaaaaa", "size": "sm", "flex": 2},
                                    {"type":  "text", "text": str(site), "wrap": True, "color": "#333333", "size": "sm", "flex": 5, "weight": "bold"}
                                ]
                            },
                            {
                                "type": "box",
                                "layout": "baseline",
                                "spacing": "sm",
                                "contents": [
                                    {"type": "text", "text": "🏢 Location:", "color": "#aaaaaa", "size": "sm", "flex": 2},
                                    {"type": "text", "text": str(location), "wrap": True, "color":  "#333333", "size": "sm", "flex": 5, "weight": "bold"}
                                ]
                            },
                            {
                                "type":  "box",
                                "layout": "baseline",
                                "spacing": "sm",
                                "contents": [
                                    {"type": "text", "text": "⏰ Duration:", "color":  "#aaaaaa", "size":  "sm", "flex": 2},
                                    {"type":  "text", "text": f"{duration:. 0f} minutes", "wrap": True, "color": "#FF4444", "size": "md", "flex": 5, "weight": "bold"}
                                ]
                            },
                            {
                                "type": "box",
                                "layout":  "baseline",
                                "spacing": "sm",
                                "contents": [
                                    {"type": "text", "text":  "🕐 Time:", "color": "#aaaaaa", "size": "sm", "flex": 2},
                                    {"type": "text", "text": datetime.now().strftime('%d/%m/%Y %H:%M:%S'), "wrap": True, "color": "#666666", "size": "sm", "flex": 5}
                                ]
                            }
                        ]
                    }
                ],
                "paddingAll": "20px"
            },
            "footer": {
                "type": "box",
                "layout": "vertical",
                "spacing": "sm",
                "contents": [
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {
                                "type": "text",
                                "text": "⚠️ Please check and remove the pallet immediately! ",
                                "color": "#FF4444",
                                "size": "sm",
                                "wrap": True,
                                "weight": "bold",
                                "align": "center"
                            }
                        ],
                        "backgroundColor": "#FFF3F3",
                        "paddingAll": "15px",
                        "cornerRadius": "10px"
                    }
                ],
                "paddingAll": "20px"
            }
        }
        
        # ✅ ถ้ามีรูปภาพ → เพิ่ม Hero
        if image_url:
            flex_content["hero"] = {
                "type":  "image",
                "url":  image_url,
                "size": "full",
                "aspectRatio": "20:13",
                "aspectMode": "cover"
            }
        
        flex_message = {
            "type": "flex",
            "altText":  f"⚠️ Pallet #{pallet_id} Overtime Alert ({duration:.0f} min)",
            "contents": flex_content
        }
        
        messages = [flex_message]
        return self.push_to_group(messages)
    
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
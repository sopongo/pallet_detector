"""
utils/line_messaging.py - LINE Official Account Messaging API
ส่ง message ผ่าน LINE OA เข้า Group
"""

import requests
import json
from datetime import datetime, timedelta
import config
from utils.logger import setup_logger

logger = setup_logger()

class LineMessagingAPI: 
    """Class สำหรับส่งข้อความผ่าน LINE OA"""
    
    def __init__(self):
        """Initialize LINE Messaging API"""
        self.cfg = config.load_config()
        self.channel_access_token = self.cfg['network']['lineNotify']['token']
        self.group_id = self.cfg['network']['lineNotify'].get('groupId', '')
        self.api_url = 'https://api.line.me/v2/bot/message'
        
        if self.group_id and not self.group_id.startswith('C'):
            logger.warning(f"⚠️ Group ID should start with 'C', got:  {self.group_id[: 5]}...")
    
    def get_headers(self):
        """สร้าง headers สำหรับ API request"""
        return {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.channel_access_token}'
        }
    
    def push_to_group(self, messages):
        """ส่งข้อความเข้า Group (Push Message)"""
        try:
            if not self.group_id:
                logger.error("❌ Group ID not configured")
                return {'success':  False, 'message': 'Group ID not set'}
            
            url = f'{self.api_url}/push'
            payload = {'to':  self.group_id, 'messages': messages}
            
            logger.info(f"📤 Sending to Group: {self.group_id[: 10]}...")
            
            response = requests.post(url, headers=self.get_headers(), data=json.dumps(payload), timeout=10)
            
            if response.status_code == 200:
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
                    return {'success': False, 'message': 'Bot not in group'}
                else:
                    return {'success': False, 'message': f'HTTP {response.status_code}'}
                
        except requests.exceptions.Timeout:
            logger.error("❌ LINE API timeout")
            return {'success': False, 'message': 'Timeout'}
        except Exception as e: 
            logger.error(f"❌ LINE error: {e}")
            return {'success': False, 'message': str(e)}
    
    def send_text_message(self, pallet_data):
        """
        ส่งข้อความแบบ Flex Message เข้า Group
        
        Args:
            pallet_data (dict): ข้อมูลพาเลท
        
        Returns:
            dict:  result
        """
        try:
            # ✅ ดึงข้อมูลจาก pallet_data
            pallet_id = pallet_data.get('pallet_id', 'N/A')
            pallet_name = pallet_data.get('pallet_name', 'N/A')
            site = pallet_data.get('site', 'N/A')
            location = pallet_data.get('location', 'N/A')
            first_detected_at = pallet_data.get('first_detected_at')
            last_detected_at = pallet_data.get('last_detected_at')
            duration = pallet_data.get('duration', 0)

            # ✅ ถ้าไม่มี first_detected_at → คำนวณจาก duration
            if not first_detected_at:
                now = datetime.now()
                first_detected_at = now - timedelta(minutes=duration)
                logger.debug(f"🕐 Calculated first_detected_at: {first_detected_at}")
            
            # ✅ ถ้าไม่มี last_detected_at → ใช้ now
            if not last_detected_at:
                last_detected_at = datetime. now()
                logger.debug(f"Using current time as last_detected_at:  {last_detected_at}")
            
            # ✅ แปลงเวลาเป็น format 08/01/2026 15:00
            if isinstance(first_detected_at, datetime):
                first_str = first_detected_at.strftime('%d/%m/%Y %H:%M')
            else:
                first_str = 'N/A'
            
            if isinstance(last_detected_at, datetime):
                last_str = last_detected_at.strftime('%d/%m/%Y %H:%M')
            else:
                last_str = 'N/A'
            
            # ✅ แปลง duration เป็นจำนวนเต็ม
            dur_int = int(round(duration))
            dur_text = str(dur_int) + " Minute"
            if dur_int != 1:
                dur_text = dur_text + "s"
            
            # ✅ แปลง site, location เป็น string
            site_str = str(site)
            loc_str = str(location)
            
            # ✅ ใช้รูป default ตลอด (ไม่ใช้รูปพาเลท)
            image_url = "https://ebooking.jwdcoldchain.com/sopon_test/IMG_20260108_003143_detected.jpg"
            
            logger.info(f"📤 Sending Flex Message for Pallet #{pallet_id}")
            
            # ✅ Flex Message
            flex_message = {
                "type": "bubble",
                "size": "mega",
                "hero": {
                    "type":  "image",
                    "url": image_url,
                    "size": "full",
                    "aspectRatio": "20:13",
                    "aspectMode": "fit",
                    "margin": "none",
                    "flex": 0,
                    "offsetTop": "xxl"                    
                },
                "body": {
                    "type":  "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "text",
                            "text": "Overdue Pallet Alert",
                            "weight": "bold",
                            "size": "xl",
                            "color": "#8c0013",
                            "margin": "md"
                        },
                        {
                            "type": "box",
                            "layout": "vertical",
                            "margin": "sm",
                            "spacing": "sm",
                            "contents": [
                                {
                                    "type": "box",
                                    "layout":  "baseline",
                                    "spacing": "sm",
                                    "contents": [
                                        {
                                            "type":  "text",
                                            "text": "Site",
                                            "color": "#aaaaaa",
                                            "size": "sm",
                                            "flex": 3
                                        },
                                        {
                                            "type": "text",
                                            "text": site_str,
                                            "wrap": True,
                                            "color": "#666666",
                                            "size": "sm",
                                            "flex": 5
                                        }
                                    ]
                                },
                                {
                                    "type": "box",
                                    "layout":  "baseline",
                                    "spacing": "sm",
                                    "contents": [
                                        {
                                            "type": "text",
                                            "text": "Location",
                                            "color": "#aaaaaa",
                                            "size": "sm",
                                            "flex": 3
                                        },
                                        {
                                            "type": "text",
                                            "text":  loc_str,
                                            "wrap": True,
                                            "color": "#666666",
                                            "size": "sm",
                                            "flex": 5
                                        }
                                    ]
                                },
                                {
                                    "type": "box",
                                    "layout": "baseline",
                                    "spacing":  "sm",
                                    "contents": [
                                        {
                                            "type": "text",
                                            "text": "Detected at",
                                            "color": "#aaaaaa",
                                            "size": "sm",
                                            "flex": 3
                                        },
                                        {
                                            "type": "text",
                                            "text": first_str,
                                            "wrap": True,
                                            "color":  "#666666",
                                            "size": "sm",
                                            "flex": 5
                                        }
                                    ]
                                },
                                {
                                    "type":  "box",
                                    "layout": "baseline",
                                    "spacing": "sm",
                                    "contents": [
                                        {
                                            "type": "text",
                                            "text": "Last detected",
                                            "color":  "#aaaaaa",
                                            "size": "sm",
                                            "flex": 3
                                        },
                                        {
                                            "type": "text",
                                            "text": last_str,
                                            "wrap": True,
                                            "color": "#666666",
                                            "size": "sm",
                                            "flex": 5
                                        }
                                    ]
                                },
                                {
                                    "type": "box",
                                    "layout": "baseline",
                                    "spacing": "sm",
                                    "contents": [
                                        {
                                            "type": "text",
                                            "text": "Over time",
                                            "color":  "#aaaaaa",
                                            "size": "sm",
                                            "flex": 3
                                        },
                                        {
                                            "type": "text",
                                            "text": dur_text,
                                            "wrap": True,
                                            "color": "#666666",
                                            "size": "sm",
                                            "flex": 5
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                },
                "footer": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "text",
                            "text": "Please check and put away.",
                            "weight": "bold",
                            "style": "normal",
                            "align":  "center",
                            "color": "#FFFFFF"
                        }
                    ],
                    "backgroundColor": "#00108c",
                    "spacing": "md"
                },
                "styles": {
                    "header": {
                        "backgroundColor": "#CCDDAA",
                        "separator": True,
                        "separatorColor": "#CCDDAA"
                    }
                }
            }

            # ✅ ส่ง Flex Message
            messages = [{'type': 'flex', 'altText': 'Overdue Pallet Alert', 'contents': flex_message}]
            return self.push_to_group(messages)
            
        except Exception as e:
            logger.error(f"❌ Error in send_text_message: {e}", exc_info=True)
            return {'success': False, 'message': str(e)}
    
    def send_overtime_alert(self, pallet_info):
        """ส่ง alert พาเลทเกินเวลา"""
        try:
            logger.info(f"📤 Overtime alert for Pallet #{pallet_info.get('pallet_id', 'N/A')}")
            result = self.send_text_message(pallet_info)
            
            if result['success']: 
                logger.info(f"✅ Alert sent")
            else:
                logger.error(f"❌ Alert failed: {result['message']}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Exception:  {e}", exc_info=True)
            return {'success': False, 'message': str(e)}
    
    def test_connection(self):
        """ทดสอบการเชื่อมต่อ LINE OA"""
        if not self.group_id:
            return {'success': False, 'message': '❌ Group ID not configured'}
        if not self.channel_access_token:
            return {'success': False, 'message': '❌ Token not configured'}
        
        # ✅ ส่ง text message ธรรมดา
        test_msg = f"🧪 Test\n\n✅ OK!\n\n📅 {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
        messages = [{'type': 'text', 'text': test_msg}]
        return self.push_to_group(messages)


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
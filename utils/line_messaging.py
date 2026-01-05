"""
utils/line_messaging.py - LINE Official Account Messaging API
ส่ง message ผ่าน LINE OA
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
        self. cfg = config.load_config()
        self.channel_access_token = self.cfg['network']['lineNotify']['token']
        self.api_url = 'https://api.line.me/v2/bot/message'
    
    def get_headers(self):
        """สร้าง headers สำหรับ API request"""
        return {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.channel_access_token}'
        }
    
    def push_message(self, user_id, messages):
        """
        ส่งข้อความถึง user เฉพาะคน (Push Message)
        
        Args: 
            user_id (str): LINE User ID (U...)
            messages (list): รายการข้อความ [{'type':   'text', 'text':   '.. .'}, ...]
            
        Returns:
            dict:  {'success': bool, 'message': str}
        """
        try: 
            url = f'{self.api_url}/push'
            payload = {
                'to': user_id,
                'messages':  messages
            }
            
            response = requests.post(
                url,
                headers=self.get_headers(),
                data=json.dumps(payload),
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info(f"✅ LINE message sent to {user_id}")
                return {'success': True, 'message':  'Sent successfully'}
            else:
                logger.error(f"❌ LINE API error: {response.status_code} - {response.text}")
                return {'success': False, 'message': f'HTTP {response.status_code}'}
                
        except Exception as e:
            logger.error(f"❌ LINE Messaging error: {e}")
            return {'success': False, 'message': str(e)}
    
    def broadcast_message(self, messages):
        """
        ส่งข้อความถึงทุกคนที่ Add Friend (Broadcast)
        
        Args:
            messages (list): รายการข้อความ
            
        Returns:
            dict: result
        """
        try: 
            url = f'{self.api_url}/broadcast'
            payload = {'messages': messages}
            
            response = requests.post(
                url,
                headers=self. get_headers(),
                data=json.dumps(payload),
                timeout=10
            )
            
            if response.status_code == 200:
                logger. info("✅ LINE broadcast sent")
                return {'success': True, 'message': 'Broadcast sent'}
            else:
                logger. error(f"❌ LINE API error: {response.status_code} - {response.text}")
                return {'success': False, 'message': f'HTTP {response.status_code}'}
                
        except Exception as e: 
            logger.error(f"❌ LINE Broadcast error:  {e}")
            return {'success': False, 'message': str(e)}
    
    def multicast_message(self, user_ids, messages):
        """
        ส่งข้อความถึงหลายคน (Multicast)
        
        Args:
            user_ids (list): รายการ User IDs
            messages (list): รายการข้อความ
            
        Returns:
            dict: result
        """
        try:
            url = f'{self.api_url}/multicast'
            payload = {
                'to': user_ids,
                'messages': messages
            }
            
            response = requests.post(
                url,
                headers=self.get_headers(),
                data=json.dumps(payload),
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info(f"✅ LINE multicast sent to {len(user_ids)} users")
                return {'success': True, 'message': 'Multicast sent'}
            else:
                logger.error(f"❌ LINE API error: {response.status_code} - {response.text}")
                return {'success': False, 'message': f'HTTP {response.status_code}'}
                
        except Exception as e:
            logger.error(f"❌ LINE Multicast error: {e}")
            return {'success':  False, 'message': str(e)}
    
    def send_overtime_alert(self, pallet_info, user_ids=None):
        """
        ส่ง alert พาเลทค้างเกินเวลา (Flex Message)
        
        Args: 
            pallet_info (dict): ข้อมูลพาเลท
            user_ids (list): รายการ User IDs (ถ้าไม่ระบุจะ broadcast)
            
        Returns: 
            dict: result
        """
        pallet_id = pallet_info. get('pallet_id', 'N/A')
        duration = pallet_info.get('duration', 0)
        site = pallet_info.get('site', 'N/A')
        location = pallet_info.get('location', 'N/A')
        
        # สร้าง Flex Message
        flex_message = {
            "type": "flex",
            "altText": f"⚠️ Pallet #{pallet_id} Overtime Alert! ",
            "contents": {
                "type": "bubble",
                "header": {
                    "type":  "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "text",
                            "text": "⚠️ PALLET OVERTIME",
                            "color": "#ffffff",
                            "weight": "bold",
                            "size": "lg"
                        }
                    ],
                    "backgroundColor": "#FF4444"
                },
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {
                            "type": "text",
                            "text": f"Pallet ID: #{pallet_id}",
                            "weight": "bold",
                            "size": "xl",
                            "margin": "md"
                        },
                        {
                            "type": "separator",
                            "margin": "md"
                        },
                        {
                            "type":  "box",
                            "layout": "vertical",
                            "margin": "lg",
                            "spacing": "sm",
                            "contents": [
                                {
                                    "type": "box",
                                    "layout":  "baseline",
                                    "spacing": "sm",
                                    "contents": [
                                        {
                                            "type": "text",
                                            "text": "Site:",
                                            "color":  "#aaaaaa",
                                            "size": "sm",
                                            "flex": 2
                                        },
                                        {
                                            "type": "text",
                                            "text": str(site),
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
                                            "text": "Location:",
                                            "color":  "#aaaaaa",
                                            "size": "sm",
                                            "flex": 2
                                        },
                                        {
                                            "type": "text",
                                            "text": str(location),
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
                                            "text": "Duration:",
                                            "color": "#aaaaaa",
                                            "size": "sm",
                                            "flex": 2
                                        },
                                        {
                                            "type": "text",
                                            "text": f"{duration:. 1f} minutes",
                                            "wrap":  True,
                                            "color": "#FF4444",
                                            "size": "sm",
                                            "flex": 5,
                                            "weight": "bold"
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
                                            "text":  "Time:",
                                            "color":  "#aaaaaa",
                                            "size": "sm",
                                            "flex": 2
                                        },
                                        {
                                            "type": "text",
                                            "text": datetime.now().strftime('%H:%M:%S'),
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
                    "spacing": "sm",
                    "contents": [
                        {
                            "type": "text",
                            "text": "⚠️ Please check and remove the pallet immediately! ",
                            "color": "#FF4444",
                            "size": "xs",
                            "wrap": True
                        }
                    ]
                }
            }
        }
        
        messages = [flex_message]
        
        # ส่งข้อความ
        if user_ids: 
            return self.multicast_message(user_ids, messages)
        else:
            return self.broadcast_message(messages)
    
    def send_text_message(self, text, user_ids=None):
        """
        ส่งข้อความธรรมดา
        
        Args:
            text (str): ข้อความ
            user_ids (list): รายการ User IDs (ถ้าไม่ระบุจะ broadcast)
        """
        messages = [{'type': 'text', 'text': text}]
        
        if user_ids:
            return self.multicast_message(user_ids, messages)
        else:
            return self.broadcast_message(messages)
    
    def test_connection(self):
        """
        ทดสอบการเชื่อมต่อ LINE OA
        
        Returns:
            dict: result
        """
        message = f"🧪 LINE OA Test\n\nConnection successful!\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        return self.send_text_message(message)
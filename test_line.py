# test_line_oa.py
from utils.line_messaging import LineMessagingAPI

line = LineMessagingAPI()

# ทดสอบ broadcast
result = line.test_connection()
print(result)

# ทดสอบ alert
pallet_info = {
    'pallet_id': 123,
    'duration': 35.5,
    'site': 'PACJ',
    'location': 'Building 1'
}

result = line.send_overtime_alert(pallet_info)
print(result)
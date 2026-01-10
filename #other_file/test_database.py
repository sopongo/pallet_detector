# test_database.py
from utils.database import DatabaseManager
from datetime import datetime

db = DatabaseManager()

# ทดสอบการเชื่อมต่อ
result = db.test_connection()
print(result)

# ทดสอบบันทึกรูป
image_data = {
    'image_date': datetime.now(),
    'image_name': 'TEST_IMG.jpg',
    'pallet_detected': 2,
    'site': 1,
    'location': 2
}

id_img = db.save_image_record(image_data)
print(f"Saved image record:  {id_img}")

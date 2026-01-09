import requests

url = "https://jaiangelbot.jwdcoldchain.com/console/jai_receive_photo.php"
api_key = "PiPcs@1234"  # เปลี่ยนตรงนี้! 

# หารูปทดสอบ (ใช้รูปไหนก็ได้)
image_path = "test_upload.png"  # หรือ path รูปจริง

with open(image_path, 'rb') as f:
    files = {'image': f}
    headers = {'X-API-Key':  api_key}
    
    response = requests.post(url, files=files, headers=headers, timeout=10)
    
    print(f"Status: {response. status_code}")
    print(f"Response: {response.text}")
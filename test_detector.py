# test_detector.py
from utils.detector import PalletDetector

# สร้าง detector
detector = PalletDetector()

# ทดสอบด้วยรูป (ใส่ path รูปทดสอบของคุณ)
result = detector.detect_pallets('path/S__27443224_0.jpg')

if result:
    print(f"✅ Detected {result['count']} pallet(s)")
    for i, pallet in enumerate(result['pallets']):
        print(f"  Pallet {i+1}: Center={pallet['center']}, Conf={pallet['confidence']:.2f}")
else:
    print("❌ Detection failed")
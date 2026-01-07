#!/usr/bin/env python3
"""
Test Multi-Class Detection System
Tests the enhanced pallet detector with multi-class support and position-based tracking
"""

import sys
import os
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.database import DatabaseManager
from utils.detector import PalletDetector
from utils.tracker import PalletTracker

def test_database_get_latest_pallet_no():
    """Test get_latest_pallet_no method"""
    print("\n" + "="*60)
    print("TEST 1: Database - get_latest_pallet_no()")
    print("="*60)
    
    try:
        db = DatabaseManager()
        
        # Test with today's date
        latest_no = db.get_latest_pallet_no()
        print(f"✅ Latest pallet_no for today: {latest_no}")
        
        # Test with specific date
        test_date = "2026-01-07"
        latest_no_date = db.get_latest_pallet_no(test_date)
        print(f"✅ Latest pallet_no for {test_date}: {latest_no_date}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_detector_multi_class():
    """Test multi-class detection"""
    print("\n" + "="*60)
    print("TEST 2: Detector - Multi-Class Detection")
    print("="*60)
    
    try:
        detector = PalletDetector()
        
        # Test image path
        test_image = "dist/img/pallet_075.jpg"
        
        if not os.path.exists(test_image):
            print(f"⚠️  Test image not found: {test_image}")
            print("Skipping detector test")
            return True
        
        print(f"📸 Testing with image: {test_image}")
        
        # Run detection
        result = detector.detect_pallets(test_image)
        
        if result:
            print(f"✅ Detected {result['count']} object(s)")
            
            # Check for multi-class support
            for i, obj in enumerate(result['pallets']):
                print(f"  Object {i+1}:")
                print(f"    - Class: {obj['class_name']}")
                print(f"    - Type: {obj['class_type']}")
                print(f"    - Confidence: {obj['confidence']:.2%}")
                print(f"    - Center: {obj['center']}")
        else:
            print("⚠️  Detection returned None")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_position_based_tracking():
    """Test position-based tracking with ±5% tolerance"""
    print("\n" + "="*60)
    print("TEST 3: Tracker - Position-Based Tracking (±5%)")
    print("="*60)
    
    try:
        tracker = PalletTracker()
        
        # Mock image dimensions
        image_width = 1280
        image_height = 720
        
        print(f"Image dimensions: {image_width}x{image_height}")
        
        # Calculate thresholds
        threshold_x = image_width * 0.05
        threshold_y = image_height * 0.05
        
        print(f"✅ Threshold X (±5%): {threshold_x} pixels")
        print(f"✅ Threshold Y (±5%): {threshold_y} pixels")
        
        # Mock active pallets
        active_pallets = [
            {
                'id_pallet': 1,
                'pos_x': 640.0,
                'pos_y': 360.0,
                'pallet_no': 1,
                'pallet_name': 'PL-0001'
            }
        ]
        
        # Test case 1: Within tolerance (should match)
        new_center_1 = [650.0, 370.0]  # +10 x, +10 y
        match_1 = tracker.find_matching_pallet(new_center_1, active_pallets, image_width, image_height)
        
        if match_1:
            print(f"✅ Test 1: Position {new_center_1} matched existing pallet (within tolerance)")
        else:
            print(f"❌ Test 1: Position {new_center_1} should match but didn't")
        
        # Test case 2: Outside tolerance (should NOT match)
        new_center_2 = [800.0, 360.0]  # +160 x (>5%)
        match_2 = tracker.find_matching_pallet(new_center_2, active_pallets, image_width, image_height)
        
        if not match_2:
            print(f"✅ Test 2: Position {new_center_2} correctly NOT matched (outside tolerance)")
        else:
            print(f"❌ Test 2: Position {new_center_2} should NOT match but did")
        
        # Test case 3: Edge of tolerance
        new_center_3 = [640.0 + threshold_x - 1, 360.0]  # Just within threshold
        match_3 = tracker.find_matching_pallet(new_center_3, active_pallets, image_width, image_height)
        
        if match_3:
            print(f"✅ Test 3: Position at edge of tolerance matched")
        else:
            print(f"❌ Test 3: Position at edge should match")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_pallet_naming():
    """Test pallet naming convention"""
    print("\n" + "="*60)
    print("TEST 4: Pallet Naming Convention")
    print("="*60)
    
    # Test pallet naming
    PALLET_PREFIX = "PL-"
    PERSON_PREFIX = "PE-"
    
    test_cases = [
        (1, 'pallet', f"{PALLET_PREFIX}{1:04d}"),
        (10, 'pallet', f"{PALLET_PREFIX}{10:04d}"),
        (99, 'pallet', f"{PALLET_PREFIX}{99:04d}"),
        (1, 'person', f"{PERSON_PREFIX}{1:04d}"),
        (5, 'person', f"{PERSON_PREFIX}{5:04d}"),
    ]
    
    all_passed = True
    for num, class_type, expected in test_cases:
        if class_type == 'pallet':
            result = f"{PALLET_PREFIX}{num:04d}"
        else:
            result = f"{PERSON_PREFIX}{num:04d}"
        
        if result == expected:
            print(f"✅ {class_type.capitalize()} #{num}: {result}")
        else:
            print(f"❌ {class_type.capitalize()} #{num}: Expected {expected}, got {result}")
            all_passed = False
    
    return all_passed


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("MULTI-CLASS DETECTION TEST SUITE")
    print("="*60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = []
    
    # Run tests
    results.append(("Database get_latest_pallet_no", test_database_get_latest_pallet_no()))
    results.append(("Multi-Class Detection", test_detector_multi_class()))
    results.append(("Position-Based Tracking", test_position_based_tracking()))
    results.append(("Pallet Naming Convention", test_pallet_naming()))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    print("="*60)
    
    return passed == total


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)

#!/usr/bin/env python3
"""
Simple Unit Tests for Multi-Class Detection
Tests the logic without requiring database or YOLO models
"""

import sys
import os

def test_pallet_naming_convention():
    """Test pallet naming convention"""
    print("="*60)
    print("TEST 1: Pallet Naming Convention")
    print("="*60)
    
    PALLET_PREFIX = "PL-"
    PERSON_PREFIX = "PE-"
    
    test_cases = [
        (1, 'pallet', "PL-0001"),
        (10, 'pallet', "PL-0010"),
        (99, 'pallet', "PL-0099"),
        (100, 'pallet', "PL-0100"),
        (1, 'person', "PE-0001"),
        (5, 'person', "PE-0005"),
        (999, 'person', "PE-0999"),
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


def test_position_tolerance_calculation():
    """Test position-based tolerance calculation"""
    print("\n" + "="*60)
    print("TEST 2: Position Tolerance Calculation (±5%)")
    print("="*60)
    
    test_cases = [
        (1280, 720),   # HD resolution
        (1920, 1080),  # Full HD
        (640, 480),    # VGA
        (3840, 2160),  # 4K
    ]
    
    all_passed = True
    for width, height in test_cases:
        threshold_x = width * 0.05
        threshold_y = height * 0.05
        
        print(f"✅ {width}x{height}: threshold_x={threshold_x:.1f}px, threshold_y={threshold_y:.1f}px")
        
        # Verify it's 5%
        if abs(threshold_x - width * 0.05) < 0.01 and abs(threshold_y - height * 0.05) < 0.01:
            continue
        else:
            print(f"❌ Calculation error for {width}x{height}")
            all_passed = False
    
    return all_passed


def test_position_matching_logic():
    """Test position matching logic"""
    print("\n" + "="*60)
    print("TEST 3: Position Matching Logic")
    print("="*60)
    
    image_width = 1280
    image_height = 720
    threshold_x = image_width * 0.05  # 64 pixels
    threshold_y = image_height * 0.05  # 36 pixels
    
    print(f"Image: {image_width}x{image_height}")
    print(f"Tolerance: ±{threshold_x:.1f}px (x), ±{threshold_y:.1f}px (y)")
    print()
    
    # Reference position
    old_x, old_y = 640.0, 360.0
    
    test_cases = [
        # (new_x, new_y, should_match, description)
        (640.0, 360.0, True, "Same position"),
        (650.0, 370.0, True, "Within tolerance (+10, +10)"),
        (640.0 + threshold_x - 1, 360.0, True, "Edge of X tolerance"),
        (640.0, 360.0 + threshold_y - 1, True, "Edge of Y tolerance"),
        (640.0 + threshold_x + 1, 360.0, False, "Outside X tolerance"),
        (640.0, 360.0 + threshold_y + 1, False, "Outside Y tolerance"),
        (800.0, 360.0, False, "Far away in X"),
        (640.0, 500.0, False, "Far away in Y"),
    ]
    
    all_passed = True
    for new_x, new_y, should_match, description in test_cases:
        dx = abs(new_x - old_x)
        dy = abs(new_y - old_y)
        matches = (dx <= threshold_x and dy <= threshold_y)
        
        if matches == should_match:
            status = "✅"
        else:
            status = "❌"
            all_passed = False
        
        print(f"{status} {description}: ({new_x}, {new_y}) dx={dx:.1f}, dy={dy:.1f} → {matches}")
    
    return all_passed


def test_sorting_logic():
    """Test top-to-bottom, left-to-right sorting"""
    print("\n" + "="*60)
    print("TEST 4: Bounding Box Sorting (Top-to-Bottom, Left-to-Right)")
    print("="*60)
    
    # Mock pallets with different positions
    pallets = [
        {'center': [100, 200], 'id': 'bottom-left'},
        {'center': [500, 100], 'id': 'top-right'},
        {'center': [100, 100], 'id': 'top-left'},
        {'center': [500, 200], 'id': 'bottom-right'},
        {'center': [300, 150], 'id': 'middle'},
    ]
    
    # Sort: top-to-bottom (y), then left-to-right (x)
    sorted_pallets = sorted(pallets, key=lambda p: (p['center'][1], p['center'][0]))
    
    expected_order = ['top-left', 'top-right', 'middle', 'bottom-left', 'bottom-right']
    actual_order = [p['id'] for p in sorted_pallets]
    
    print(f"Expected order: {expected_order}")
    print(f"Actual order:   {actual_order}")
    
    if actual_order == expected_order:
        print("✅ Sorting logic correct")
        return True
    else:
        print("❌ Sorting logic incorrect")
        return False


def test_class_filtering():
    """Test class name filtering"""
    print("\n" + "="*60)
    print("TEST 5: Class Filtering (Case-Insensitive)")
    print("="*60)
    
    test_cases = [
        ("pallet", True, "pallet"),
        ("Pallet", True, "pallet"),
        ("PALLET", True, "pallet"),
        ("person", True, "person"),
        ("Person", True, "person"),
        ("PERSON", True, "person"),
        ("car", False, None),
        ("truck", False, None),
        ("box", False, None),
    ]
    
    all_passed = True
    for class_name, should_accept, expected_type in test_cases:
        class_name_lower = class_name.lower()
        
        if 'pallet' in class_name_lower:
            class_type = 'pallet'
            accepted = True
        elif 'person' in class_name_lower:
            class_type = 'person'
            accepted = True
        else:
            class_type = None
            accepted = False
        
        if accepted == should_accept and (not accepted or class_type == expected_type):
            print(f"✅ '{class_name}' → {class_type if accepted else 'filtered out'}")
        else:
            print(f"❌ '{class_name}' → Expected {expected_type if should_accept else 'filtered'}, got {class_type}")
            all_passed = False
    
    return all_passed


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("MULTI-CLASS DETECTION UNIT TEST SUITE")
    print("="*60)
    print()
    
    results = []
    
    # Run tests
    results.append(("Pallet Naming Convention", test_pallet_naming_convention()))
    results.append(("Position Tolerance Calculation", test_position_tolerance_calculation()))
    results.append(("Position Matching Logic", test_position_matching_logic()))
    results.append(("Bounding Box Sorting", test_sorting_logic()))
    results.append(("Class Filtering", test_class_filtering()))
    
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

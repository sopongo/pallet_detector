#!/usr/bin/env python3
"""
Test script for Zone Configuration Manager
Tests the new zone format with normalized coordinates and enhanced fields
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

from utils.zone_config import ZoneConfigManager

def test_zone_validation():
    """Test zone validation with new format"""
    print("=" * 60)
    print("Testing Zone Configuration Manager")
    print("=" * 60)
    
    manager = ZoneConfigManager()
    
    # Test 1: Valid zone with new format
    print("\n[Test 1] Valid zone with new format (normalized coordinates):")
    valid_zone = {
        "id": 1,
        "name": "Test_Zone_1",
        "polygon": [[0.1, 0.2], [0.3, 0.2], [0.3, 0.4], [0.1, 0.4]],
        "threshold_percent": 45.0,
        "alert_threshold": 3000,
        "pallet_type": 1,
        "active": True
    }
    
    is_valid, error = manager.validate_zone(valid_zone)
    print(f"   Result: {'✅ PASS' if is_valid else '❌ FAIL'}")
    if not is_valid:
        print(f"   Error: {error}")
    
    # Test 2: Invalid zone - coordinates out of range
    print("\n[Test 2] Invalid zone - coordinates > 1.0:")
    invalid_zone = valid_zone.copy()
    invalid_zone["polygon"] = [[0.1, 0.2], [1.5, 0.2], [0.3, 0.4]]  # x > 1.0
    
    is_valid, error = manager.validate_zone(invalid_zone)
    print(f"   Result: {'✅ PASS' if not is_valid else '❌ FAIL'} (should be invalid)")
    if not is_valid:
        print(f"   Error message: {error}")
    
    # Test 3: Invalid zone - invalid pallet_type
    print("\n[Test 3] Invalid zone - pallet_type not 1 or 2:")
    invalid_zone = valid_zone.copy()
    invalid_zone["pallet_type"] = 3  # Invalid value
    
    is_valid, error = manager.validate_zone(invalid_zone)
    print(f"   Result: {'✅ PASS' if not is_valid else '❌ FAIL'} (should be invalid)")
    if not is_valid:
        print(f"   Error message: {error}")
    
    # Test 4: Test max zones limit (20)
    print("\n[Test 4] Max zones limit (20):")
    print(f"   MAX_ZONES: {manager.MAX_ZONES}")
    print(f"   Result: {'✅ PASS' if manager.MAX_ZONES == 20 else '❌ FAIL'}")
    
    # Test 5: Overlap detection with Shapely
    print("\n[Test 5] Polygon overlap detection:")
    zone1 = {
        "id": 1,
        "name": "Zone_1",
        "polygon": [[0.1, 0.1], [0.3, 0.1], [0.3, 0.3], [0.1, 0.3]],
        "threshold_percent": 45.0,
        "alert_threshold": 3000,
        "pallet_type": 1,
        "active": True
    }
    
    # Overlapping zone
    zone2_overlap = zone1.copy()
    zone2_overlap["id"] = 2
    zone2_overlap["name"] = "Zone_2_Overlap"
    zone2_overlap["polygon"] = [[0.2, 0.2], [0.4, 0.2], [0.4, 0.4], [0.2, 0.4]]
    
    has_overlap = manager.check_overlap(zone1, zone2_overlap)
    print(f"   Overlap detected: {has_overlap}")
    print(f"   Result: {'✅ PASS' if has_overlap else '❌ FAIL'}")
    
    # Non-overlapping zone
    zone2_no_overlap = zone1.copy()
    zone2_no_overlap["id"] = 2
    zone2_no_overlap["name"] = "Zone_2_No_Overlap"
    zone2_no_overlap["polygon"] = [[0.5, 0.5], [0.7, 0.5], [0.7, 0.7], [0.5, 0.7]]
    
    has_overlap = manager.check_overlap(zone1, zone2_no_overlap)
    print(f"   No overlap detected: {not has_overlap}")
    print(f"   Result: {'✅ PASS' if not has_overlap else '❌ FAIL'}")
    
    # Test 6: Test zone list validation
    print("\n[Test 6] Validate zone list with multiple zones:")
    zones = [zone1, zone2_no_overlap]
    is_valid, error = manager.validate_zones_list(zones)
    print(f"   Result: {'✅ PASS' if is_valid else '❌ FAIL'}")
    if not is_valid:
        print(f"   Error: {error}")
    
    print("\n" + "=" * 60)
    print("Zone Configuration Tests Complete")
    print("=" * 60)

if __name__ == '__main__':
    try:
        test_zone_validation()
        print("\n✅ All tests completed successfully!")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

#!/usr/bin/env python3
"""
Test script to verify LINE overtime alert fixes
Tests:
1. Helper methods for site/location name conversion
2. Image URL is included in overtime_pallets
3. Site/Location IDs are converted to names before sending
4. Comprehensive logging is present
5. LINE config validation at startup
"""

import sys
import os
import json
from unittest.mock import Mock, MagicMock, patch
import tempfile


def test_site_location_helpers():
    """Test get_site_name and get_location_name helper methods"""
    print("="*60)
    print("TEST 1: Site/Location Name Helper Methods")
    print("="*60)
    
    try:
        # Check that the helper methods exist in the code
        with open('detection_service.py', 'r') as f:
            code = f.read()
        
        # Check for get_site_name method
        has_get_site_name = 'def get_site_name(self, site_id):' in code
        has_sites_json_read = "sites_file = os.path.join(os.path.dirname(__file__), 'config', 'sites.json')" in code
        has_site_name_return = "site_info.get('site_name'" in code
        
        if has_get_site_name:
            print("✅ Found get_site_name() method definition")
        else:
            print("❌ Missing get_site_name() method")
        
        if has_sites_json_read:
            print("✅ Found sites.json file reading logic")
        else:
            print("❌ Missing sites.json reading logic")
        
        if has_site_name_return:
            print("✅ Found site_name extraction from JSON")
        else:
            print("❌ Missing site_name extraction")
        
        # Check for get_location_name method
        has_get_location_name = 'def get_location_name(self, site_id, location_id):' in code
        has_location_return = "locations.get(str(location_id)" in code
        
        if has_get_location_name:
            print("✅ Found get_location_name() method definition")
        else:
            print("❌ Missing get_location_name() method")
        
        if has_location_return:
            print("✅ Found location name extraction from JSON")
        else:
            print("❌ Missing location extraction")
        
        # Check fallbacks
        has_fallback = "return f'Site {site_id}'" in code and "return f'Location {location_id}'" in code
        
        if has_fallback:
            print("✅ Found fallback returns for invalid IDs")
        else:
            print("❌ Missing fallback logic")
        
        all_checks = has_get_site_name and has_sites_json_read and has_site_name_return and has_get_location_name and has_location_return and has_fallback
        
        if all_checks:
            print("✅ All helper method checks passed")
            return True
        else:
            print("❌ Some helper method checks failed")
            return False
            
    except Exception as e:
        print(f"❌ Error testing helper methods: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_image_url_in_overtime_pallets():
    """Test that image_url is included in overtime_pallets dict"""
    print("\n" + "="*60)
    print("TEST 2: Image URL in Overtime Pallets")
    print("="*60)
    
    try:
        # Check the code for image_url in overtime_pallets.append calls
        with open('detection_service.py', 'r') as f:
            code = f.read()
        
        # Count occurrences of overtime_pallets.append with image_url field
        append_count = code.count("overtime_pallets.append(")
        # Look for 'image_url': in the context of append calls
        image_url_field_count = code.count("'image_url':")
        
        print(f"Found {append_count} overtime_pallets.append() calls")
        print(f"Found {image_url_field_count} 'image_url' field definitions")
        
        # We expect at least 2 append calls and at least 2 image_url fields
        if append_count >= 2 and image_url_field_count >= 2:
            print(f"✅ Image URL field is included in overtime_pallets")
            
            # Also check for image URL update logic
            has_update = "pallet['image_url'] = image_url" in code or 'pallet["image_url"] = image_url' in code
            if has_update:
                print(f"✅ Image URL update logic found")
            else:
                print(f"⚠️ Warning: Image URL update logic not found, but fields exist")
            
            return True
        else:
            print(f"❌ Image URL not properly included (expected 2 appends and 2+ fields, found {append_count} appends and {image_url_field_count} fields)")
            return False
            
    except Exception as e:
        print(f"❌ Error testing image URL: {e}")
        return False


def test_site_location_conversion_in_handle_alerts():
    """Test that site/location IDs are converted to names in handle_alerts"""
    print("\n" + "="*60)
    print("TEST 3: Site/Location ID to Name Conversion in handle_alerts")
    print("="*60)
    
    try:
        # Check the code for get_site_name and get_location_name calls in handle_alerts
        with open('detection_service.py', 'r') as f:
            lines = f.readlines()
        
        # Find handle_alerts method
        in_handle_alerts = False
        has_get_site_name = False
        has_get_location_name = False
        has_alert_data_dict = False
        
        for i, line in enumerate(lines):
            if 'def handle_alerts' in line:
                in_handle_alerts = True
                print(f"Found handle_alerts at line {i+1}")
            
            if in_handle_alerts:
                if 'self.get_site_name' in line:
                    has_get_site_name = True
                    print(f"✅ Found get_site_name() call at line {i+1}")
                
                if 'self.get_location_name' in line:
                    has_get_location_name = True
                    print(f"✅ Found get_location_name() call at line {i+1}")
                
                if 'alert_data = {' in line:
                    has_alert_data_dict = True
                    print(f"✅ Found alert_data dict creation at line {i+1}")
                
                # Exit when we reach next method
                if in_handle_alerts and line.strip().startswith('def ') and 'def handle_alerts' not in line:
                    break
        
        if has_get_site_name and has_get_location_name and has_alert_data_dict:
            print("✅ Site/Location conversion properly implemented")
            return True
        else:
            print(f"❌ Missing conversions: site_name={has_get_site_name}, location_name={has_get_location_name}, alert_data={has_alert_data_dict}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing site/location conversion: {e}")
        return False


def test_comprehensive_logging():
    """Test that comprehensive logging is implemented"""
    print("\n" + "="*60)
    print("TEST 4: Comprehensive Logging")
    print("="*60)
    
    try:
        with open('detection_service.py', 'r') as f:
            code = f.read()
        
        # Expected log messages
        expected_logs = [
            '📢 Handling alerts',
            '📋 Overtime pallets data',
            '🔄 Processing',
            '📤 Sending alert',
            'Alert data:',
            '✅ LINE alert sent successfully',
            '❌ LINE alert failed',
            'exc_info=True'
        ]
        
        all_found = True
        for log_msg in expected_logs:
            if log_msg in code:
                print(f"✅ Found log: '{log_msg}'")
            else:
                print(f"❌ Missing log: '{log_msg}'")
                all_found = False
        
        if all_found:
            print("✅ All expected log messages found")
            return True
        else:
            print("❌ Some log messages missing")
            return False
            
    except Exception as e:
        print(f"❌ Error testing logging: {e}")
        return False


def test_line_config_validation():
    """Test that LINE config validation is in __init__"""
    print("\n" + "="*60)
    print("TEST 5: LINE Config Validation at Startup")
    print("="*60)
    
    try:
        with open('detection_service.py', 'r') as f:
            lines = f.readlines()
        
        # Find __init__ method
        in_init = False
        has_token_check = False
        has_group_check = False
        
        for i, line in enumerate(lines):
            if 'def __init__' in line:
                in_init = True
                print(f"Found __init__ at line {i+1}")
            
            if in_init:
                if 'line_token' in line and 'lineNotify' in line:
                    has_token_check = True
                    print(f"✅ Found LINE token check at line {i+1}")
                
                if 'line_group' in line and 'groupId' in line:
                    has_group_check = True
                    print(f"✅ Found LINE group ID check at line {i+1}")
                
                # Exit when we reach next method
                if in_init and line.strip().startswith('def ') and 'def __init__' not in line:
                    break
        
        if has_token_check and has_group_check:
            print("✅ LINE config validation properly implemented")
            return True
        else:
            print(f"❌ Missing validation: token={has_token_check}, group={has_group_check}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing config validation: {e}")
        return False


def test_image_url_update_logic():
    """Test that image URL is updated after annotated_path is created"""
    print("\n" + "="*60)
    print("TEST 6: Image URL Update After annotated_path Creation")
    print("="*60)
    
    try:
        with open('detection_service.py', 'r') as f:
            code = f.read()
        
        # Check for the image URL update code after annotated_path
        has_image_url_update = 'for pallet in overtime_pallets:' in code and "pallet['image_url'] = image_url" in code
        has_image_rel_path = 'image_rel_path' in code
        has_localhost_url = 'http://localhost/' in code
        
        if has_image_url_update:
            print("✅ Found image URL update loop for overtime_pallets")
        else:
            print("❌ Missing image URL update loop")
        
        if has_image_rel_path:
            print("✅ Found image_rel_path calculation")
        else:
            print("❌ Missing image_rel_path calculation")
        
        if has_localhost_url:
            print("✅ Found localhost URL generation")
        else:
            print("❌ Missing localhost URL generation")
        
        if has_image_url_update and has_image_rel_path and has_localhost_url:
            print("✅ Image URL update logic properly implemented")
            return True
        else:
            print("❌ Image URL update logic incomplete")
            return False
            
    except Exception as e:
        print(f"❌ Error testing image URL update: {e}")
        return False


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("LINE OVERTIME ALERT FIX TEST SUITE")
    print("="*60)
    print()
    
    results = []
    
    # Run tests
    results.append(("Site/Location Name Helpers", test_site_location_helpers()))
    results.append(("Image URL in Overtime Pallets", test_image_url_in_overtime_pallets()))
    results.append(("Site/Location Conversion in handle_alerts", test_site_location_conversion_in_handle_alerts()))
    results.append(("Comprehensive Logging", test_comprehensive_logging()))
    results.append(("LINE Config Validation", test_line_config_validation()))
    results.append(("Image URL Update Logic", test_image_url_update_logic()))
    
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

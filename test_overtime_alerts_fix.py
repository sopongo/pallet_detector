"""
Test script to verify overtime alert fixes
Tests the key functionality changes made to fix LINE overtime alerts
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
import json

def test_update_pallet_returns_correct_status():
    """Test that update_pallet returns status=1 when overtime"""
    print("\n" + "="*60)
    print("TEST 1: update_pallet returns correct status")
    print("="*60)
    
    # Mock config
    with patch('config.load_config') as mock_config:
        mock_config.return_value = {
            'network': {'database': {'host': 'localhost', 'user': 'test', 'password': 'test', 'database': 'test', 'port': 3306}},
            'detection': {'alertThreshold': 0.12}  # 7.2 seconds
        }
        
        from utils.tracker import PalletTracker
        tracker = PalletTracker()
        
        # Mock database connection
        with patch.object(tracker, 'get_db_connection') as mock_db:
            mock_conn = Mock()
            mock_cursor = Mock()
            mock_db.return_value = mock_conn
            mock_conn.cursor.return_value = mock_cursor
            
            # Simulate pallet that's been there for 0.4 minutes (24 seconds) - OVERTIME
            first_detected = datetime.now() - timedelta(minutes=0.4)
            mock_cursor.fetchone.return_value = {
                'id_pallet': 17,
                'first_detected_at': first_detected,
                'over_time': None
            }
            
            # Call update_pallet
            detection_time = datetime.now()
            result = tracker.update_pallet(17, detection_time)
            
            # Verify result
            print(f"✅ Result: {result}")
            assert result is not None, "Result should not be None"
            assert result['pallet_id'] == 17, "Pallet ID should be 17"
            assert result['duration'] >= 0.3, f"Duration should be >= 0.3 min, got {result['duration']}"
            assert result['status'] == 1, f"Status should be 1 (overtime), got {result['status']}"
            
            print("✅ TEST PASSED: update_pallet returns status=1 for overtime pallet")
            print(f"   - Duration: {result['duration']:.2f} minutes")
            print(f"   - Threshold: {tracker.alert_threshold} minutes")
            print(f"   - Status: {result['status']} (1=overtime)")
            return True

def test_line_message_simplified():
    """Test that LINE message is simplified to plain text"""
    print("\n" + "="*60)
    print("TEST 2: LINE message simplified to plain text")
    print("="*60)
    
    with patch('config.load_config') as mock_config:
        mock_config.return_value = {
            'network': {'lineNotify': {'token': 'test_token', 'groupId': 'C123456789'}}
        }
        
        from utils.line_messaging import LineMessagingAPI
        line_api = LineMessagingAPI()
        
        # Mock send_text_message
        with patch.object(line_api, 'send_text_message') as mock_send:
            mock_send.return_value = {'success': True, 'message': 'Sent'}
            
            # Call send_overtime_alert
            pallet_info = {
                'pallet_id': 17,
                'duration': 0.4,
                'site': 'PCS',
                'location': 'Building 1'
            }
            
            result = line_api.send_overtime_alert(pallet_info)
            
            # Verify
            print(f"✅ Result: {result}")
            mock_send.assert_called_once()
            call_args = mock_send.call_args[0][0]
            print(f"   - Message sent: '{call_args}'")
            assert call_args == "มีพาเลทเกินเวลา", f"Message should be 'มีพาเลทเกินเวลา', got '{call_args}'"
            
            print("✅ TEST PASSED: LINE message is plain text 'มีพาเลทเกินเวลา'")
            return True

def test_gpio_wrapped_in_try_except():
    """Test that GPIO errors don't block alert handling"""
    print("\n" + "="*60)
    print("TEST 3: GPIO errors don't block alert handling")
    print("="*60)
    
    with patch('config.load_config') as mock_config:
        mock_config.return_value = {
            'network': {
                'database': {'host': 'localhost', 'user': 'test', 'password': 'test', 'database': 'test', 'port': 3306},
                'lineNotify': {'token': 'test_token', 'groupId': 'C123456789'}
            },
            'detection': {'alertThreshold': 0.12},
            'general': {'imagePath': '/tmp', 'siteCompany': 1, 'siteLocation': 1},
            'gpio': {'redLightPin': 17, 'greenLightPin': 27}
        }
        
        # Mock the imports
        with patch('detection_service.PalletDetector'), \
             patch('detection_service.PalletTracker'), \
             patch('detection_service.DatabaseManager'), \
             patch('detection_service.LineMessagingAPI'), \
             patch('detection_service.LightController') as mock_lights_class:
            
            # Make GPIO throw an error
            mock_lights = Mock()
            mock_lights.test_red.side_effect = Exception("GPIO not available")
            mock_lights_class.return_value = mock_lights
            
            from detection_service import DetectionService
            service = DetectionService()
            
            # Mock the dependencies
            service.line = Mock()
            service.line.send_overtime_alert.return_value = {'success': True, 'message': 'Sent'}
            service.db = Mock()
            service.db.save_notification_log = Mock()
            service.db.increment_notify_count = Mock()
            service.get_site_name = Mock(return_value='PCS')
            service.get_location_name = Mock(return_value='Building 1')
            
            # Call handle_alerts with overtime pallet
            overtime_pallets = [{
                'pallet_id': 17,
                'duration': 0.4,
                'site': 1,
                'location': 1,
                'image_url': 'http://example.com/image.jpg'
            }]
            
            # Should not raise exception even though GPIO fails
            try:
                service.handle_alerts(overtime_pallets, '/tmp/image.jpg')
                print("✅ handle_alerts completed without exception despite GPIO error")
            except Exception as e:
                print(f"❌ handle_alerts raised exception: {e}")
                raise
            
            # Verify LINE alert was sent despite GPIO error
            assert service.line.send_overtime_alert.called, "LINE alert should be sent"
            assert service.db.save_notification_log.called, "Notification log should be saved"
            
            print("✅ TEST PASSED: GPIO error doesn't block LINE alerts")
            print("   - GPIO error occurred but was caught")
            print("   - LINE alert was still sent")
            print("   - Database log was still saved")
            return True

def test_log_api_returns_objects_with_class():
    """Test that /api/detection/logs returns objects with CSS class"""
    print("\n" + "="*60)
    print("TEST 4: Log API returns objects with CSS class")
    print("="*60)
    
    # Create a temporary log file
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as f:
        f.write("[INFO] Normal log line\n")
        f.write("[WARNING] ⚠️ Overtime detected: Pallet #17 (0.4 min)\n")
        f.write("[ERROR] ❌ Something went wrong\n")
        f.write("[INFO] 🔴 Pallet #17 OVERTIME: 0.40m > 0.12m\n")
        log_file = f.name
    
    try:
        # Mock the log file location
        with patch('os.path.join', return_value=log_file):
            with patch('os.path.exists', return_value=True):
                with patch('os.path.getsize', return_value=500):
                    # Import after patching
                    import importlib
                    import app as app_module
                    importlib.reload(app_module)
                    
                    from app import app
                    client = app.test_client()
                    
                    # Call API
                    response = client.get('/api/detection/logs?limit=10')
                    data = json.loads(response.data)
                    
                    print(f"✅ API Response: {data['success']}")
                    print(f"   - Total logs: {len(data['logs'])}")
                    
                    # Verify structure
                    assert data['success'], "API should return success"
                    assert isinstance(data['logs'], list), "Logs should be a list"
                    
                    # Check each log is an object with text and class
                    for i, log in enumerate(data['logs']):
                        print(f"   - Log {i+1}: class='{log.get('class', '')}' | text='{log['text'][:50]}...'")
                        assert isinstance(log, dict), "Each log should be a dict"
                        assert 'text' in log, "Log should have 'text' field"
                        assert 'class' in log, "Log should have 'class' field"
                    
                    # Verify overtime logs have error class
                    overtime_logs = [log for log in data['logs'] if 'overtime' in log['text'].lower() or '⚠️' in log['text']]
                    if overtime_logs:
                        for log in overtime_logs:
                            assert log['class'] in ['log-error', 'log-warning'], \
                                f"Overtime log should have error/warning class, got '{log['class']}'"
                            print(f"   ✅ Overtime log has class: {log['class']}")
                    
                    print("✅ TEST PASSED: Log API returns objects with CSS classes")
                    return True
    finally:
        # Clean up temp file
        os.unlink(log_file)

def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("OVERTIME ALERTS FIX - TEST SUITE")
    print("="*70)
    
    tests = [
        test_update_pallet_returns_correct_status,
        test_line_message_simplified,
        test_gpio_wrapped_in_try_except,
        test_log_api_returns_objects_with_class
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"\n❌ TEST FAILED: {test.__name__}")
            print(f"   Error: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("\n" + "="*70)
    print(f"TEST RESULTS: {passed} passed, {failed} failed")
    print("="*70)
    
    if failed == 0:
        print("✅ ALL TESTS PASSED!")
        return 0
    else:
        print(f"❌ {failed} TEST(S) FAILED")
        return 1

if __name__ == '__main__':
    sys.exit(main())

# LINE Overtime Alerts Fix - Verification Guide

## 🎯 Overview
This guide helps you verify that the LINE overtime alerts are now working correctly.

## ✅ Changes Summary

### 1. Enhanced Logging (utils/tracker.py)
**What Changed:**
- Added detailed logging in `update_pallet()` method
- Logs now show:
  - Duration vs threshold comparison
  - Overtime detection warnings (🔴)
  - Return values with status

**How to Verify:**
Look for these logs in `logs/detection.log`:
```
⏱️ Pallet #17: duration=0.40m, threshold=0.12m
🔴 Pallet #17 OVERTIME: 0.40m > 0.12m
✅ Updated pallet #17 (duration: 0.4 min, status: 1)
📤 Returning: {'pallet_id': 17, 'duration': 0.4, 'status': 1}
```

### 2. Simplified LINE Message (utils/line_messaging.py)
**What Changed:**
- Replaced 145-line Flex Message with simple text
- Now sends: "มีพาเลทเกินเวลา"
- Uses proven `send_text_message()` method

**How to Verify:**
1. Check logs for:
   ```
   📤 Sending overtime alert: มีพาเลทเกินเวลา
   ✅ Overtime alert sent successfully
   ```
2. Check LINE group for simple text message

### 3. GPIO Error Handling (detection_service.py)
**What Changed:**
- Wrapped `self.lights.test_red()` in try-except
- Wrapped `self.lights.test_green()` in try-except
- GPIO errors logged as warnings, not errors

**How to Verify:**
If running on Windows or without GPIO:
```
⚠️ GPIO error (ignored): [GPIO not available]
📤 Sending alert 1/1: Pallet #17 (duration: 0.4 min)
✅ LINE alert sent successfully
```

### 4. Database Logging (detection_service.py)
**What Changed:**
- `save_notification_log()` called for each alert
- Alert count tracked and reported

**How to Verify:**
1. Check logs:
   ```
   ⚠️ Sent 1/1 overtime alert(s)
   ```
2. Check database:
   ```sql
   SELECT * FROM tb_notifications 
   WHERE DATE(sent_at) = CURDATE()
   ORDER BY sent_at DESC;
   ```
   Should show new records with:
   - `ref_id_pallet`: pallet ID
   - `notify_type`: 'LINE'
   - `message`: 'Overtime alert: X.X min'
   - `success`: 1 (if sent successfully)

### 5. Visual Feedback (app.py + monitor.inc.php)
**What Changed:**
- Logs API returns objects with CSS classes
- Added red text for overtime logs
- Added orange text for warnings

**How to Verify:**
1. Open monitoring page in browser
2. Wait for overtime detection
3. Look at "System Logs (Live Feed)" section
4. Overtime logs should appear in **RED** color

## 🧪 Testing Steps

### Test 1: Verify Overtime Detection Logic
```bash
# 1. Set short alert threshold (e.g., 0.12 minutes = 7.2 seconds)
# 2. Start detection service
# 3. Place a pallet in camera view
# 4. Wait ~8-10 seconds
# 5. Check logs for:
```
**Expected Logs:**
```
⏱️ Pallet #17: duration=0.13m, threshold=0.12m
🔴 Pallet #17 OVERTIME: 0.13m > 0.12m
✅ Updated pallet #17 (duration: 0.1 min, status: 1)
🔍 Overtime check complete: 1 alert(s) pending
```

### Test 2: Verify LINE Alert Sent
```bash
# Continue from Test 1
# Check logs for:
```
**Expected Logs:**
```
📢 Handling alerts: 1 overtime pallet(s)
🔄 Processing 1 alert(s)...
📤 Sending alert 1/1: Pallet #17 (duration: 0.1 min)
📤 Sending overtime alert: มีพาเลทเกินเวลา
✅ Overtime alert sent successfully
   ✅ LINE alert sent successfully
⚠️ Sent 1/1 overtime alert(s)
```

### Test 3: Verify Database Records
```sql
-- Check notification logs
SELECT 
    id,
    ref_id_pallet,
    notify_type,
    message,
    sent_at,
    success
FROM tb_notifications
WHERE DATE(sent_at) = CURDATE()
ORDER BY sent_at DESC
LIMIT 5;
```

**Expected Result:**
```
id | ref_id_pallet | notify_type | message                 | sent_at             | success
---|---------------|-------------|-------------------------|---------------------|--------
1  | 17            | LINE        | Overtime alert: 0.1 min | 2026-01-07 23:48:16 | 1
```

### Test 4: Verify Summary Counts
```bash
# Open monitoring page
# Check "Detect Summary" panel
```

**Expected Values:**
- Pallet Over Time: 1 (incremented)
- Notifications: 1 (incremented)

### Test 5: Verify Red Text in UI
```bash
# Open monitoring page
# Look at "System Logs (Live Feed)" section
# Lines containing "overtime" should be RED
```

**Expected UI:**
- Normal logs: Green text
- Overtime logs: **RED text, bold**
- Warning logs: Orange text

## 🐛 Troubleshooting

### Issue: Status always 0, no alerts
**Check:**
1. Config `alertThreshold` is set correctly (in minutes)
2. Pallet duration is being calculated (check logs)
3. Look for: `⏱️ Pallet #X: duration=...`

### Issue: LINE alert not sent
**Check:**
1. LINE token configured in config.json
2. GROUP ID starts with 'C'
3. Bot is member of the group
4. Check logs for LINE API errors

### Issue: GPIO blocking alerts
**Fixed!** GPIO errors now logged as warnings and don't block alerts.
Look for: `⚠️ GPIO error (ignored): ...`

### Issue: No database records
**Check:**
1. Database connection working
2. `tb_notifications` table exists
3. Check logs for database errors

### Issue: No red text in UI
**Check:**
1. Browser cache cleared
2. Monitor page reloaded
3. API endpoint `/api/detection/logs` returning objects with 'class' field

## 📊 Success Criteria

All of these should work:
- ✅ Overtime detected when duration > threshold
- ✅ Status = 1 returned from `update_pallet()`
- ✅ `overtime_pallets` list populated
- ✅ LINE message "มีพาเลทเกินเวลา" sent
- ✅ Database record created in `tb_notifications`
- ✅ Notification count incremented
- ✅ Red text in monitoring UI
- ✅ GPIO errors don't block alerts

## 📝 Logs to Monitor

**Key Log Files:**
1. `logs/detection.log` - Main detection service logs
2. `logs/detection_service.log` - Service startup/shutdown logs
3. Browser console - UI/API errors

**Key Log Patterns to Watch:**
```bash
# Good patterns (success)
grep "OVERTIME" logs/detection.log
grep "alert sent successfully" logs/detection.log
grep "Sent.*overtime alert" logs/detection.log

# Bad patterns (problems)
grep "ERROR" logs/detection.log | grep -v GPIO
grep "alert failed" logs/detection.log
grep "0 alert(s) pending" logs/detection.log
```

## 🔍 Database Queries

```sql
-- Today's overtime pallets
SELECT 
    p.id_pallet,
    p.pallet_name,
    TIMESTAMPDIFF(MINUTE, p.first_detected_at, p.last_detected_at) as duration_min,
    p.status,
    p.in_over,
    p.notify_count
FROM tb_pallet p
JOIN tb_image i ON p.ref_id_img = i.id_img
WHERE DATE(i.image_date) = CURDATE()
AND p.in_over = 1
ORDER BY p.first_detected_at DESC;

-- Today's notifications
SELECT 
    n.*,
    p.pallet_name
FROM tb_notifications n
LEFT JOIN tb_pallet p ON n.ref_id_pallet = p.id_pallet
WHERE DATE(n.sent_at) = CURDATE()
ORDER BY n.sent_at DESC;

-- Summary for today
SELECT 
    COUNT(DISTINCT i.id_img) as total_photos,
    COUNT(p.id_pallet) as total_pallets,
    SUM(CASE WHEN p.in_over = 0 THEN 1 ELSE 0 END) as in_time,
    SUM(CASE WHEN p.in_over = 1 THEN 1 ELSE 0 END) as over_time,
    (SELECT COUNT(*) FROM tb_notifications WHERE DATE(sent_at) = CURDATE()) as notifications
FROM tb_image i
LEFT JOIN tb_pallet p ON p.ref_id_img = i.id_img
WHERE DATE(i.image_date) = CURDATE();
```

## 🎉 Expected Results

After this fix, you should see:

1. **Console Logs** (logs/detection.log):
```
[23:48:03] INFO: Created new pallet #17 (PL-0017)
[23:48:16] INFO: ⏱️ Pallet #17: duration=0.40m, threshold=0.12m
[23:48:16] WARNING: 🔴 Pallet #17 OVERTIME: 0.40m > 0.12m
[23:48:16] INFO: ✅ Updated pallet #17 (duration: 0.4 min, status: 1)
[23:48:16] WARNING: ⚠️ Overtime detected: Pallet #17 (0.4 min)
[23:48:16] INFO: 🔍 Overtime check complete: 1 alert(s) pending
[23:48:16] INFO: 📢 Handling alerts: 1 overtime pallet(s)
[23:48:16] INFO: 📤 Sending alert 1/1: Pallet #17 (duration: 0.4 min)
[23:48:16] INFO: 📤 Sending overtime alert: มีพาเลทเกินเวลา
[23:48:16] INFO: ✅ Overtime alert sent successfully
[23:48:16] INFO:    ✅ LINE alert sent successfully
[23:48:16] WARNING: ⚠️ Sent 1/1 overtime alert(s)
```

2. **LINE Group Message**:
```
มีพาเลทเกินเวลา
```

3. **Database Records**:
```sql
tb_notifications: 1 new row
tb_pallet: notify_count incremented
```

4. **Monitoring UI**:
- Pallet Over Time: 1+
- Notifications: 1+
- System logs show RED text for overtime lines

## 💡 Tips

1. **During Testing**: Set `alertThreshold` to 0.12 (7.2 seconds) for quick testing
2. **Production**: Set appropriate threshold (e.g., 5 minutes = 5.0)
3. **Debugging**: Enable DEBUG logging in logger.py for more details
4. **Monitoring**: Keep browser console open to see API calls

## 🚨 Common Mistakes to Avoid

1. ❌ Don't set threshold too high during testing (won't trigger)
2. ❌ Don't forget to start detection service
3. ❌ Don't forget to add bot to LINE group
4. ❌ Don't use wrong GROUP ID format (should start with 'C')
5. ❌ Don't ignore GPIO warnings (they're expected on Windows)

---

**Last Updated**: 2026-01-07
**Version**: 1.0
**Status**: Ready for Testing ✅

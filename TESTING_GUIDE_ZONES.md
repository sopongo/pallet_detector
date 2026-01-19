# Zone Detection System - Testing Guide

## Overview
This guide provides step-by-step instructions for testing the complete Zone Detection System implementation covering all 13 issues.

## Prerequisites

1. **Database Migration**: Execute the SQL from `DATABASE_MIGRATION_ZONES.md` first
2. **Backend Running**: Flask app.py running on port 5000
3. **Frontend Access**: Access to config.inc.php via web browser
4. **Test Images**: Warehouse photos for zone configuration

## Testing Checklist

### Phase 1: UI & Configuration Testing (Issues 1-7)

#### ✅ Issue 1: Overlap Detection
**Test**: Draw two zones that have slightly overlapping bounding boxes

**Steps**:
1. Navigate to Config → Zone Configuration tab
2. Upload a reference image
3. Click "Add New Zone" and draw Zone 1 (e.g., 4 points forming a polygon)
4. Right-click to finish Zone 1
5. Click "Add New Zone" and draw Zone 2 near/slightly overlapping Zone 1
6. Right-click to finish Zone 2

**Expected Result**: 
- ❌ OLD: "Zone overlaps with Zone 1" error
- ✅ NEW: Both zones created successfully (backend validation only)

---

#### ✅ Issue 2-3: Coordinate System
**Test**: Verify zones use normalized coordinates (0.0-1.0)

**Steps**:
1. Draw a zone and save it
2. Check browser DevTools → Network → zones API call
3. Inspect the JSON payload

**Expected Result**:
```json
{
  "points": [
    {"x": 0.1234, "y": 0.5678},  // ✅ Values between 0.0-1.0
    {"x": 0.8901, "y": 0.3456}   // NOT 12.34, 56.78 (0-100)
  ]
}
```

---

#### ✅ Issue 4-5: Reference Image Upload
**Test**: Verify reference image is saved to server

**Steps**:
1. Upload a reference image
2. Click "Save Zones"
3. Check `upload_image/` directory

**Expected Result**:
- File exists: `upload_image/img_configzone_DD-MM-YYYY.jpg` (today's date)
- File size > 0 bytes
- Console shows: "✅ Reference image saved: upload_image/..."

---

#### ✅ Issue 6: Reference Image Display
**Test**: Verify reference image is displayed on tab open

**Steps**:
1. Upload and save a reference image (Issue 4-5 test)
2. Navigate away from Zone Configuration tab
3. Return to Zone Configuration tab

**Expected Result**:
- Image preview card shows the uploaded image
- "No reference image uploaded yet" message is hidden
- Image has cache-busting URL parameter `?t=timestamp`

---

#### ✅ Issue 7: Flask API Endpoint
**Test**: Verify `/api/zones/image` endpoint works

**Steps**:
```bash
# Test upload via curl
curl -X POST http://localhost:5000/api/zones/image \
  -F "image=@test_image.jpg"
```

**Expected Result**:
```json
{
  "success": true,
  "message": "Reference image uploaded successfully",
  "filepath": "upload_image/img_configzone_19-01-2026.jpg",
  "filename": "img_configzone_19-01-2026.jpg"
}
```

---

### Phase 2: Detection Integration Testing (Issues 8-13)

#### ✅ Issue 8-9: Zone Filtering with 50% Overlap
**Test**: Verify only detections with ≥50% bbox overlap are tracked

**Setup**:
1. Draw 2 zones: Zone A (left side) and Zone B (right side)
2. Set different thresholds: Zone A = 30 min, Zone B = 10 min
3. Enable zone system

**Test Cases**:

**Case 1: 60% Overlap (Should Track)**
- Place pallet with center clearly inside Zone A
- Expected: Pallet tracked to Zone A

**Case 2: 40% Overlap (Should NOT Track)**
- Place pallet on edge with only 40% inside Zone A
- Expected: Pallet NOT tracked (filtered out)

**Case 3: Multiple Zones**
- Place pallet overlapping both zones (30% in A, 70% in B)
- Expected: Pallet tracked to Zone B (highest overlap)

**Verification**:
```bash
# Check logs
tail -f logs/detection_service.log | grep "zone\|overlap\|Filtered"

# Expected logs:
# "Detection bbox=[...] → Zone 'Zone A' (overlap: 60.2%)"
# "Detection bbox=[...] → Outside zones (best overlap: 40.0%)"
# "🗺️ Filtered: 2/3 detections in zones"
```

---

#### ✅ Issue 10-11: Zone-Specific Thresholds
**Test**: Verify each zone uses its own alert threshold

**Setup**:
1. Zone A: threshold = 30 minutes
2. Zone B: threshold = 10 minutes

**Test Steps**:
1. Place pallet in Zone A → wait 11 minutes
   - Expected: NO alert (11 < 30)
2. Place pallet in Zone B → wait 11 minutes
   - Expected: ALERT (11 > 10)

**Verification**:
```bash
# Check database
mysql -u user -p database -e "SELECT pallet_name, zone_name, zone_threshold, 
  TIMESTAMPDIFF(MINUTE, first_detected_at, last_detected_at) as duration, 
  status FROM tb_pallet WHERE is_active=1;"

# Expected output:
# PL-0001 | Zone A | 30 | 11 | 0 (normal)
# PL-0002 | Zone B | 10 | 11 | 1 (overtime)
```

---

#### ✅ Issue 12: Detection Service Integration
**Test**: Verify detection service loads and uses zones

**Steps**:
1. Configure zones and save
2. Restart detection service: `python3 detection_service.py`
3. Check startup logs

**Expected Logs**:
```
✅ Detection service initialized
🗺️ Zone detection enabled: 2 zone(s)
  - Zone A: 4 points, threshold=30m
  - Zone B: 4 points, threshold=10m
```

**During Detection**:
```
🗺️ After zone filter: 2/3 detection(s)
✅ Created pallet #5 (PL-0005) in zone 'Zone A' (threshold: 30m)
```

---

#### ✅ Issue 13: Database Schema
**Test**: Verify zone columns exist and work

**Steps**:
```sql
-- Check columns exist
DESCRIBE tb_pallet;

-- Check indexes
SHOW INDEX FROM tb_pallet WHERE Key_name LIKE 'idx_zone%';

-- Insert test record
INSERT INTO tb_pallet (pallet_no, pallet_name, zone_id, zone_name, zone_threshold, 
  pos_x, pos_y, is_active, status, detector_count, first_detected_at, last_detected_at)
VALUES (9999, 'TEST-0001', 1, 'Zone A', 30, 100, 100, 1, 0, 1, NOW(), NOW());

-- Verify data
SELECT zone_id, zone_name, zone_threshold FROM tb_pallet WHERE pallet_no=9999;

-- Cleanup
DELETE FROM tb_pallet WHERE pallet_no=9999;
```

**Expected**: All queries execute successfully, zone columns populated correctly.

---

## End-to-End Integration Test

### Scenario: Complete Zone Detection Flow

**Setup**:
1. Draw 2 zones with different thresholds (Zone A: 30m, Zone B: 10m)
2. Enable zone system
3. Start detection service

**Test Flow**:

1. **T=0min**: Detection runs
   - 3 pallets detected
   - 2 inside zones (≥50% overlap) → tracked
   - 1 outside zones (40% overlap) → filtered out
   - Log: "🗺️ Filtered: 2/3 detections in zones"

2. **T=11min**: Detection runs
   - Zone B pallet still present
   - Alert triggered: "🔴 Pallet #2 OVERTIME: 11.0m > 10.0m (Zone: Zone B)"
   - LINE notification sent

3. **T=31min**: Detection runs
   - Zone A pallet still present
   - Alert triggered: "🔴 Pallet #1 OVERTIME: 31.0m > 30.0m (Zone: Zone A)"
   - LINE notification sent

**Database Verification**:
```sql
SELECT pallet_name, zone_name, zone_threshold,
  TIMESTAMPDIFF(MINUTE, first_detected_at, last_detected_at) as duration,
  status, over_time
FROM tb_pallet
WHERE is_active=1
ORDER BY zone_name;
```

**Expected**:
```
PL-0001 | Zone A | 30 | 31 | 1 | 2026-01-19 16:51:00
PL-0002 | Zone B | 10 | 11 | 1 | 2026-01-19 16:31:00
```

---

## Troubleshooting

### Issue: Zones not filtering detections
**Check**:
1. Zone system enabled? (toggle in UI)
2. Zones saved? (click "Save Zones")
3. Detection service restarted after saving zones?
4. Check logs: `grep "Zone detection" logs/detection_service.log`

### Issue: Wrong threshold used
**Check**:
1. Database: `SELECT zone_threshold FROM tb_pallet WHERE id_pallet=X;`
2. Zone config: Check alertThreshold in saved zones
3. Logs: `grep "threshold=" logs/detection_service.log`

### Issue: Reference image not displaying
**Check**:
1. File exists: `ls -lh upload_image/img_configzone_*.jpg`
2. Correct date format: `img_configzone_DD-MM-YYYY.jpg`
3. Browser console for 404 errors
4. File permissions: `chmod 644 upload_image/*.jpg`

---

## Success Criteria

All 13 issues resolved:
- [x] Client-side overlap check disabled
- [x] Coordinates normalized (0.0-1.0)
- [x] Reference image saves automatically
- [x] Reference image displays on tab open
- [x] Zone filtering works (50% overlap)
- [x] Zone-specific thresholds respected
- [x] Detection service integrates zones
- [x] Database schema supports zones

## Performance Notes

- Zone filtering adds ~5-10ms per detection
- Shapely polygon intersection is efficient for typical warehouse zones
- Indexes on zone_id improve query performance
- Reference images should be <10MB (enforced by upload handler)

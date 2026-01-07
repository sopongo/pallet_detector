# Multi-Class Detection Enhancement

This document describes the enhancements made to the pallet detection system to support multi-class detection, custom labeling, and position-based tracking.

## Overview

The pallet detection system has been enhanced to:
1. **Detect multiple object classes** (Pallet + Person)
2. **Draw custom bounding boxes** with sequential labels (PL-0001, PE-0001)
3. **Implement position-based tracking** (±5% tolerance) instead of IoU-based tracking
4. **Auto-increment pallet/person numbers** daily with database integration
5. **Support overtime alerts** via LINE messaging

## Key Changes

### 1. Database Enhancement (`utils/database.py`)

#### New Method: `get_latest_pallet_no(date=None)`

Queries the latest pallet number for a specific date (defaults to today).

```python
def get_latest_pallet_no(self, date=None):
    """
    Get the latest pallet_no for today (or specified date)
    Returns: int (e.g., 5 → next will be 6)
    """
    if date is None:
        date = datetime.now().strftime('%Y-%m-%d')
    
    # Query MAX(pallet_no) WHERE DATE(pallet_date_in) = date
    # Return 0 if no records found
```

**Features:**
- Returns 0 if no records exist for the day
- Enables daily reset of pallet numbers
- Uses date-based filtering via JOIN with tb_image

### 2. Multi-Class Detection (`utils/detector.py`)

#### Enhanced `detect_pallets()` Method

Now detects both pallets and persons with case-insensitive filtering.

**Changes:**
- Removed class filtering in YOLO prediction (`classes=None`)
- Added `class_type` field to detection results ('pallet' or 'person')
- Returns `original_image` instead of annotated image for custom drawing

**Example Detection Result:**
```python
{
    'count': 3,
    'pallets': [
        {
            'bbox': [100, 200, 300, 400],
            'center': [200.0, 300.0],
            'confidence': 0.95,
            'class_name': 'pallet',
            'class_type': 'pallet'  # New field
        },
        {
            'bbox': [500, 100, 600, 300],
            'center': [550.0, 200.0],
            'confidence': 0.89,
            'class_name': 'person',
            'class_type': 'person'  # New field
        }
    ],
    'image_path': 'path/to/image.jpg',
    'original_image': numpy.ndarray
}
```

#### Rewritten `save_annotated_image()` Method

Draws custom bounding boxes with sequential labels.

**Features:**
1. **Sorting**: Top-to-bottom (Y), then left-to-right (X)
   ```python
   sorted_pallets = sorted(pallets, key=lambda p: (p['center'][1], p['center'][0]))
   ```

2. **Sequential Numbering**:
   - Queries latest number from database
   - Auto-increments for new detections
   - Preserves numbers for existing detections

3. **Custom Labels**:
   - Format: `PL-0001 (95.2%)` or `PE-0001 (89.5%)`
   - Includes confidence percentage

4. **Color Coding**:
   - Green `(0, 255, 0)` for pallets
   - Blue `(255, 0, 0)` for persons (BGR format)

**Visual Example:**
```
┌─────────────────┐
│ PL-0001 (95.0%) │  ← Green box (top-left pallet)
└─────────────────┘

      ┌─────────────────┐
      │ PE-0001 (89.5%) │  ← Blue box (top-right person)
      └─────────────────┘

┌─────────────────┐
│ PL-0002 (92.3%) │  ← Green box (bottom-left pallet)
└─────────────────┘
```

### 3. Position-Based Tracking (`utils/tracker.py`)

#### Removed Fixed Distance Threshold

The fixed `distance_threshold = 50` has been removed in favor of dynamic calculation.

#### Enhanced `find_matching_pallet()` Method

Now uses ±5% tolerance based on image dimensions.

**Algorithm:**
```python
def find_matching_pallet(self, new_center, active_pallets, image_width, image_height):
    # Calculate dynamic thresholds (±5%)
    threshold_x = image_width * 0.05
    threshold_y = image_height * 0.05
    
    for pallet in active_pallets:
        dx = abs(new_center[0] - old_center[0])
        dy = abs(new_center[1] - old_center[1])
        
        if dx <= threshold_x and dy <= threshold_y:
            return pallet  # Match found
    
    return None  # No match
```

**Example Thresholds:**
| Resolution | Threshold X | Threshold Y |
|------------|-------------|-------------|
| 1280x720   | 64.0 px     | 36.0 px     |
| 1920x1080  | 96.0 px     | 54.0 px     |
| 640x480    | 32.0 px     | 24.0 px     |
| 3840x2160  | 192.0 px    | 108.0 px    |

#### Updated `create_new_pallet()` Method

Now accepts `pallet_no` and `pallet_name` parameters.

**New Signature:**
```python
def create_new_pallet(self, ref_id_img, pallet_data, detection_time, pallet_no, pallet_name):
```

**Database Fields:**
- `pallet_no`: INT (1, 2, 3, ...)
- `pallet_name`: VARCHAR ("PL-0001", "PE-0002")
- `pallet_date_in`: DATETIME (detection date)

### 4. Service Integration (`detection_service.py`)

#### Enhanced `process_detection()` Method

Integrates all the new features.

**Processing Flow:**

1. **Detect Objects**
   ```python
   detection_result = self.detector.detect_pallets(image_path)
   original_image = detection_result['original_image']
   image_height, image_width = original_image.shape[:2]
   ```

2. **Save Image Record**
   ```python
   ref_id_img = self.db.save_image_record(image_data)
   ```

3. **Track Existing vs New Objects**
   ```python
   matching_pallet = self.tracker.find_matching_pallet(
       center, active_pallets, image_width, image_height
   )
   
   if matching_pallet:
       # Update existing pallet
       self.tracker.update_pallet(matching_pallet['id_pallet'], datetime.now())
   else:
       # Mark as new (will be created after drawing)
       new_pallets_to_create.append(pallet_data)
   ```

4. **Draw Custom Bounding Boxes**
   ```python
   annotated_path = self.detector.save_annotated_image(
       original_image, detected_pallets, image_path, self.db
   )
   ```

5. **Create New Pallets in Database**
   ```python
   for pallet_data in new_pallets_to_create:
       new_id = self.tracker.create_new_pallet(
           ref_id_img, pallet_data, datetime.now(),
           pallet_data['pallet_no'], pallet_data['pallet_name']
       )
   ```

## Testing

### Unit Tests (`test_logic.py`)

Comprehensive test suite covering:

1. **Pallet Naming Convention**
   - Tests: PL-0001, PL-0010, PE-0001, etc.
   - Result: ✅ PASS

2. **Position Tolerance Calculation**
   - Tests: Multiple resolutions (1280x720, 1920x1080, etc.)
   - Verifies: ±5% calculation
   - Result: ✅ PASS

3. **Position Matching Logic**
   - Tests: Same position, within tolerance, outside tolerance, edge cases
   - Result: ✅ PASS

4. **Bounding Box Sorting**
   - Tests: Top-to-bottom, left-to-right ordering
   - Result: ✅ PASS

5. **Class Filtering**
   - Tests: Case-insensitive matching for 'pallet' and 'person'
   - Result: ✅ PASS

**Test Results:**
```
============================================================
TEST SUMMARY
============================================================
✅ PASS: Pallet Naming Convention
✅ PASS: Position Tolerance Calculation
✅ PASS: Position Matching Logic
✅ PASS: Bounding Box Sorting
✅ PASS: Class Filtering

Total: 5/5 tests passed
============================================================
```

### Running Tests

```bash
cd /home/runner/work/pallet_detector/pallet_detector
python test_logic.py
```

## Configuration

### Model Configuration

Update `config/pallet_config.json`:

```json
{
    "detection": {
        "modelPath": "models/best8s.pt",  // For person detection
        // OR
        "modelPath": "models/pallet_best.pt",  // For pallet detection
        "confidenceThreshold": 0.65,
        "iouThreshold": 0.55,
        "alertThreshold": 15  // Minutes for overtime alert
    }
}
```

### Database Schema

The system uses these tables:

**tb_pallet:**
```sql
CREATE TABLE tb_pallet (
    id_pallet INT AUTO_INCREMENT PRIMARY KEY,
    pallet_no INT,                    -- 1, 2, 3, ...
    pallet_name VARCHAR(50),          -- "PL-0001", "PE-0002"
    ref_id_img INT,
    pos_x DECIMAL(10,2),              -- Center X
    pos_y DECIMAL(10,2),              -- Center Y
    bbox_x1 DECIMAL(10,2),
    bbox_y1 DECIMAL(10,2),
    bbox_x2 DECIMAL(10,2),
    bbox_y2 DECIMAL(10,2),
    accuracy DECIMAL(5,2),            -- Confidence (0.95 → 95.0)
    pallet_date_in DATETIME,          -- Detection date
    first_detected_at DATETIME,
    last_detected_at DATETIME,
    is_active TINYINT DEFAULT 1,
    status TINYINT DEFAULT 0,         -- 0=Normal, 1=Overtime, 2=Removed
    detector_count INT DEFAULT 1,
    notify_count INT DEFAULT 0
);
```

## Usage

### Running the Detection Service

```bash
python detection_service.py
```

The service will:
1. Capture images at configured intervals
2. Detect pallets and persons
3. Draw custom bounding boxes with sequential labels
4. Track objects using position-based matching
5. Send overtime alerts via LINE when threshold exceeded

### Expected Output

**Console:**
```
✅ YOLOv8 model loaded: models/best8s.pt
📋 Model classes: {0: 'person', 1: 'pallet'}
📸 Captured: /path/to/images/2026-01-07/IMG_20260107_093000.jpg
Image dimensions: 1280x720
Detected 3 object(s) in IMG_20260107_093000.jpg
Created new pallet #1 (PL-0001)
Created new pallet #2 (PE-0001)
Saved annotated image: /path/to/images/2026-01-07/IMG_20260107_093000_detected.jpg
✅ Cycle completed: 3 pallet(s) detected
```

**Annotated Image:**
- Saved as `{timestamp}_detected.jpg`
- Shows green boxes for pallets
- Shows blue boxes for persons
- Labels: PL-0001, PE-0001, etc.

**Database:**
```sql
SELECT pallet_no, pallet_name, pos_x, pos_y FROM tb_pallet ORDER BY pallet_no;
```
```
+----------+-------------+--------+--------+
| pallet_no| pallet_name | pos_x  | pos_y  |
+----------+-------------+--------+--------+
|        1 | PL-0001     | 200.00 | 300.00 |
|        2 | PE-0001     | 550.00 | 200.00 |
|        3 | PL-0002     | 400.00 | 450.00 |
+----------+-------------+--------+--------+
```

## Backward Compatibility

The enhancements maintain backward compatibility:

- **Single-class models** still work (only pallet detection)
- **Non-relevant classes** are automatically filtered out
- **Existing database records** remain untouched
- **Configuration** is backward compatible (new fields optional)

## Security

- ✅ CodeQL analysis passed with **0 alerts**
- ✅ No SQL injection vulnerabilities (parameterized queries used)
- ✅ No hardcoded credentials
- ✅ Proper error handling and logging

## Performance

- **Position-based tracking** is faster than IoU calculation
- **Dynamic thresholds** adapt to different camera resolutions
- **Efficient sorting** using Python's built-in sort with lambda

## Troubleshooting

### Issue: Objects not being tracked correctly

**Solution:** Check image dimensions and verify ±5% tolerance is appropriate for your setup.

```python
# Debug tolerance values
image_width = 1280
image_height = 720
threshold_x = image_width * 0.05   # 64.0 pixels
threshold_y = image_height * 0.05  # 36.0 pixels
```

### Issue: Pallet numbers not resetting daily

**Solution:** Verify `pallet_date_in` is being set correctly in database.

```python
# Check query
latest_no = db_manager.get_latest_pallet_no('2026-01-07')
```

### Issue: Wrong colors on bounding boxes

**Solution:** Verify BGR color format (OpenCV uses BGR, not RGB).

```python
# Correct colors (BGR format)
COLOR_PALLET = (0, 255, 0)   # Green
COLOR_PERSON = (255, 0, 0)   # Blue
```

## Future Enhancements

Possible improvements:
1. Support for additional object classes (e.g., forklift, box)
2. Configurable tolerance percentage (not fixed at 5%)
3. Advanced tracking algorithms (Kalman filter, Hungarian algorithm)
4. Real-time visualization dashboard
5. Export detection history to CSV/Excel

## Contributors

- Enhanced by GitHub Copilot AI Assistant
- Original codebase by sopongo team

## License

Same as the main pallet_detector project.

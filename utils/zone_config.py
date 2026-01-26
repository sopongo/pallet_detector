"""
Zone Configuration Manager
Manages detection zones with polygon shapes for pallet detection system.

Features:
- CRUD operations for zones
- Overlap detection using Shapely polygon intersection
- Validation (max 4 zones, max 8 points per zone)
- Percentage-based coordinates for responsive sizing
"""

import os
import json
from typing import List, Dict, Optional, Tuple
from shapely.geometry import Polygon, Point
from shapely.validation import make_valid


class ZoneConfigManager:
    """Manager class for zone configuration"""
    
    # Constants
    MAX_ZONES = 20  # Updated to support up to 20 zones
    MAX_POINTS_PER_ZONE = 8
    MIN_POINTS_PER_ZONE = 3
    
    def __init__(self, config_file: str = None):
        """
        Initialize zone config manager
        
        Args:
            config_file: Path to zones.json file
        """
        if config_file is None:
            config_file = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                'config',
                'zones.json'
            )
        self.config_file = config_file
        self._ensure_config_file()
    
    def _ensure_config_file(self):
        """Ensure zones.json exists with default structure"""
        if not os.path.exists(self.config_file):
            default_config = {
                "zones": [],
                "enabled": False
            }
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, indent=2)
    
    def load_zones(self) -> Dict:
        """
        Load zones from JSON file
        
        Returns:
            Dict with 'zones' and 'enabled' keys
        """
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Ensure structure
                if 'zones' not in data:
                    data['zones'] = []
                if 'enabled' not in data:
                    data['enabled'] = False
                return data
        except Exception as e:
            print(f"Error loading zones: {e}")
            return {"zones": [], "enabled": False}
    
    def save_zones(self, zones_data: Dict) -> bool:
        """
        Save zones to JSON file
        
        Args:
            zones_data: Dict with 'zones' and 'enabled' keys
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(zones_data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving zones: {e}")
            return False
    
    def validate_zone(self, zone: Dict) -> Tuple[bool, str]:
        """
        Validate a single zone structure
        
        Args:
            zone: Zone dict with 'id', 'name', 'polygon', 'threshold_percent', 'alert_threshold', 'pallet_type', 'active'
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check required fields - Updated for new format
        required_fields = ['id', 'name', 'polygon', 'threshold_percent', 'alert_threshold', 'pallet_type', 'active']
        for field in required_fields:
            if field not in zone:
                return False, f"Missing required field: {field}"
        
        # Validate name
        if not zone['name'] or not zone['name'].strip():
            return False, "Zone name cannot be empty"
        
        # Validate polygon (new field name, replaces 'points')
        polygon = zone['polygon']
        if not isinstance(polygon, list):
            return False, "Polygon must be a list"
        
        if len(polygon) < self.MIN_POINTS_PER_ZONE:
            return False, f"Zone must have at least {self.MIN_POINTS_PER_ZONE} points"
        
        if len(polygon) > self.MAX_POINTS_PER_ZONE:
            return False, f"Zone cannot have more than {self.MAX_POINTS_PER_ZONE} points"
        
        # Validate each point - coordinates must be normalized 0.0-1.0
        for i, point in enumerate(polygon):
            if not isinstance(point, list) or len(point) != 2:
                return False, f"Point {i} must be a list with 2 elements [x, y]"
            
            # Check normalized range (0.0-1.0)
            try:
                x = float(point[0])
                y = float(point[1])
                if not (0.0 <= x <= 1.0) or not (0.0 <= y <= 1.0):
                    return False, f"Point {i} coordinates must be between 0.0 and 1.0 (normalized)"
            except (ValueError, TypeError):
                return False, f"Point {i} coordinates must be numeric"
        
        # Validate threshold_percent (new field)
        try:
            threshold_pct = float(zone['threshold_percent'])
            if threshold_pct <= 0 or threshold_pct > 100:
                return False, "Threshold percent must be between 0 and 100"
        except (ValueError, TypeError):
            return False, "Threshold percent must be numeric"
        
        # Validate alert_threshold (renamed from alertThreshold, represents milliseconds)
        try:
            alert_threshold = float(zone['alert_threshold'])
            if alert_threshold <= 0:
                return False, "Alert threshold must be positive"
        except (ValueError, TypeError):
            return False, "Alert threshold must be numeric"
        
        # Validate pallet_type (1=Inbound, 2=Outbound)
        try:
            pallet_type = int(zone['pallet_type'])
            if pallet_type not in [1, 2]:
                return False, "Pallet type must be 1 (Inbound) or 2 (Outbound)"
        except (ValueError, TypeError):
            return False, "Pallet type must be an integer"
        
        # Validate active flag (replaces 'enabled')
        if not isinstance(zone['active'], bool):
            return False, "Active must be a boolean"
        
        return True, ""
    
    def validate_zones_list(self, zones: List[Dict]) -> Tuple[bool, str]:
        """
        Validate entire zones list
        
        Args:
            zones: List of zone dicts
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not isinstance(zones, list):
            return False, "Zones must be a list"
        
        if len(zones) > self.MAX_ZONES:
            return False, f"Cannot have more than {self.MAX_ZONES} zones"
        
        # Validate each zone
        for i, zone in enumerate(zones):
            is_valid, error = self.validate_zone(zone)
            if not is_valid:
                return False, f"Zone {i+1}: {error}"
        
        # Check for duplicate IDs
        zone_ids = [z['id'] for z in zones]
        if len(zone_ids) != len(set(zone_ids)):
            return False, "Duplicate zone IDs found"
        
        # Check for duplicate names
        zone_names = [z['name'] for z in zones]
        if len(zone_names) != len(set(zone_names)):
            return False, "Duplicate zone names found"
        
        # Check for overlaps
        for i in range(len(zones)):
            for j in range(i + 1, len(zones)):
                if self.check_overlap(zones[i], zones[j]):
                    return False, f"Zones '{zones[i]['name']}' and '{zones[j]['name']}' overlap"
        
        return True, ""
    
    def _points_to_polygon(self, points: List) -> Polygon:
        """
        Convert list of point arrays to Shapely Polygon
        แปลงรายการพิกัดจุดเป็น Polygon ของ Shapely
        
        Args:
            points: List of [x, y] arrays (normalized 0.0-1.0)
                   รายการพิกัด [x, y] (ค่าปกติ 0.0-1.0)
            
        Returns:
            Shapely Polygon object
        
        Technical Details:
        - Shapely is a Python library for geometric operations
        - Polygon represents a closed shape defined by vertices
        - Used for accurate intersection and containment checks
        """
        # Convert list of [x, y] arrays to list of (x, y) tuples
        # แปลง [[x1, y1], [x2, y2]] เป็น [(x1, y1), (x2, y2)]
        coords = [(float(p[0]), float(p[1])) for p in points]
        
        # Create Shapely Polygon object from coordinates
        # สร้าง Polygon object จากพิกัด
        polygon = Polygon(coords)
        
        # Ensure polygon is valid (handles edge cases like self-intersection)
        # ตรวจสอบและแก้ไข polygon ให้ถูกต้อง (จัดการกรณีพิเศษเช่นเส้นตัดกัน)
        if not polygon.is_valid:
            polygon = make_valid(polygon)
        
        return polygon
    
    def check_overlap(self, zone1: Dict, zone2: Dict) -> bool:
        """
        Check if two zones overlap using Shapely polygon intersection
        ตรวจสอบว่าโซนสองโซนทับซ้อนกันหรือไม่โดยใช้ Shapely polygon intersection
        
        Args:
            zone1: First zone dict (with 'polygon' field)
                   โซนแรก (มีฟิลด์ 'polygon')
            zone2: Second zone dict (with 'polygon' field)
                   โซนที่สอง (มีฟิลด์ 'polygon')
            
        Returns:
            True if zones overlap, False otherwise
            True ถ้าโซนทับซ้อนกัน, False ถ้าไม่ทับ
        
        Technical Details / รายละเอียดทางเทคนิค:
        
        1. Shapely Polygon Intersection Algorithm
           อัลกอริทึมตรวจสอบการตัดกันของรูปหลายเหลี่ยมด้วย Shapely
           
           - Uses computational geometry to find intersection area
             ใช้เรขาคณิตเชิงคำนวณหาพื้นที่ที่ตัดกัน
           
           - Handles complex polygons (concave, self-intersecting)
             จัดการรูปหลายเหลี่ยมที่ซับซ้อน (เว้า, ตัดกันเอง)
        
        2. Intersection Area Calculation
           การคำนวณพื้นที่ที่ตัดกัน
           
           - poly1.intersection(poly2) returns a Polygon/MultiPolygon
             poly1.intersection(poly2) คืนค่า Polygon หรือ MultiPolygon
           
           - intersection.area gives the overlapping area
             intersection.area ให้พื้นที่ที่ทับซ้อนกัน
        
        3. Overlap Threshold: 0.1%
           เกณฑ์การทับซ้อน: 0.1%
           
           - Small threshold to avoid false positives from floating point errors
             เกณฑ์เล็กเพื่อหลีกเลี่ยงผลบวกลวงจากข้อผิดพลาดทศนิยม
           
           - Formula: (intersection_area / min_polygon_area) * 100 > 0.1
             สูตร: (พื้นที่ตัดกัน / พื้นที่โซนที่เล็กกว่า) * 100 > 0.1
           
           - Uses smaller polygon area to ensure sensitivity
             ใช้พื้นที่โซนที่เล็กกว่าเพื่อความไวต่อการตรวจจับ
        
        Example / ตัวอย่าง:
        - Zone A: 100 sq units, Zone B: 50 sq units
        - Intersection: 1 sq unit
        - Overlap %: (1 / 50) * 100 = 2% > 0.1% → Overlap detected!
        """
        try:
            # Convert zone polygons to Shapely Polygon objects
            # แปลงโซนเป็น Shapely Polygon objects
            poly1 = self._points_to_polygon(zone1['polygon'])
            poly2 = self._points_to_polygon(zone2['polygon'])
            
            # Calculate intersection using Shapely's geometric engine
            # คำนวณการตัดกันโดยใช้ geometric engine ของ Shapely
            # This uses advanced computational geometry algorithms
            # ใช้อัลกอริทึมเรขาคณิตเชิงคำนวณขั้นสูง
            intersection = poly1.intersection(poly2)
            
            # Check if there's any intersection area
            # ตรวจสอบว่ามีพื้นที่ตัดกันหรือไม่
            if intersection.area > 0:
                # Calculate overlap percentage relative to the smaller polygon
                # คำนวณเปอร์เซ็นต์การทับซ้อนเทียบกับโซนที่เล็กกว่า
                min_area = min(poly1.area, poly2.area)
                overlap_percentage = (intersection.area / min_area) * 100
                
                # Return True if overlap exceeds threshold (0.1%)
                # คืนค่า True ถ้าการทับซ้อนเกินเกณฑ์ (0.1%)
                return overlap_percentage > 0.1
            
            # No intersection found
            # ไม่พบการตัดกัน
            return False
            
        except Exception as e:
            print(f"Error checking overlap: {e}")
            # Return False on error to allow operation to continue
            # คืนค่า False เมื่อเกิดข้อผิดพลาดเพื่อให้ดำเนินการต่อได้
            return False
    
    def point_in_zone(self, x: float, y: float, zone: Dict) -> bool:
        """
        Check if a point (x, y) is inside a zone
        
        Args:
            x: X coordinate (normalized, 0.0-1.0)
            y: Y coordinate (normalized, 0.0-1.0)
            zone: Zone dict with 'polygon' and 'active'
            
        Returns:
            True if point is in zone, False otherwise
        """
        try:
            if not zone.get('active', False):
                return False
            
            polygon = self._points_to_polygon(zone['polygon'])
            point = Point(x, y)
            
            return polygon.contains(point)
        except Exception as e:
            print(f"Error checking point in zone: {e}")
            return False
    
    def get_zone_for_point(self, x: float, y: float) -> Optional[Dict]:
        """
        Find which zone contains the given point
        
        Args:
            x: X coordinate (normalized, 0.0-1.0)
            y: Y coordinate (normalized, 0.0-1.0)
            
        Returns:
            Zone dict if point is in a zone, None otherwise
        """
        zones_data = self.load_zones()
        
        if not zones_data.get('enabled', False):
            return None
        
        for zone in zones_data['zones']:
            if self.point_in_zone(x, y, zone):
                return zone
        
        return None
    
    def add_zone(self, zone: Dict) -> Tuple[bool, str]:
        """
        Add a new zone
        
        Args:
            zone: Zone dict to add
            
        Returns:
            Tuple of (success, message)
        """
        zones_data = self.load_zones()
        
        # Check max zones limit
        if len(zones_data['zones']) >= self.MAX_ZONES:
            return False, f"Cannot add more than {self.MAX_ZONES} zones"
        
        # Validate zone
        is_valid, error = self.validate_zone(zone)
        if not is_valid:
            return False, error
        
        # Check for ID conflict
        for existing_zone in zones_data['zones']:
            if existing_zone['id'] == zone['id']:
                return False, f"Zone with ID {zone['id']} already exists"
        
        # Check for name conflict
        for existing_zone in zones_data['zones']:
            if existing_zone['name'] == zone['name']:
                return False, f"Zone with name '{zone['name']}' already exists"
        
        # Check for overlaps with existing zones
        for existing_zone in zones_data['zones']:
            if self.check_overlap(zone, existing_zone):
                return False, f"Zone overlaps with '{existing_zone['name']}'"
        
        # Add zone
        zones_data['zones'].append(zone)
        
        if self.save_zones(zones_data):
            return True, "Zone added successfully"
        else:
            return False, "Failed to save zone"
    
    def update_zone(self, zone_id: int, updated_zone: Dict) -> Tuple[bool, str]:
        """
        Update an existing zone
        
        Args:
            zone_id: ID of zone to update
            updated_zone: Updated zone dict
            
        Returns:
            Tuple of (success, message)
        """
        zones_data = self.load_zones()
        
        # Find zone
        zone_index = None
        for i, zone in enumerate(zones_data['zones']):
            if zone['id'] == zone_id:
                zone_index = i
                break
        
        if zone_index is None:
            return False, f"Zone with ID {zone_id} not found"
        
        # Validate updated zone
        is_valid, error = self.validate_zone(updated_zone)
        if not is_valid:
            return False, error
        
        # Check for name conflict (excluding current zone)
        for i, existing_zone in enumerate(zones_data['zones']):
            if i != zone_index and existing_zone['name'] == updated_zone['name']:
                return False, f"Zone with name '{updated_zone['name']}' already exists"
        
        # Check for overlaps with other zones (excluding current zone)
        for i, existing_zone in enumerate(zones_data['zones']):
            if i != zone_index and self.check_overlap(updated_zone, existing_zone):
                return False, f"Zone overlaps with '{existing_zone['name']}'"
        
        # Update zone
        zones_data['zones'][zone_index] = updated_zone
        
        if self.save_zones(zones_data):
            return True, "Zone updated successfully"
        else:
            return False, "Failed to save zone"
    
    def delete_zone(self, zone_id: int) -> Tuple[bool, str]:
        """
        Delete a zone
        
        Args:
            zone_id: ID of zone to delete
            
        Returns:
            Tuple of (success, message)
        """
        zones_data = self.load_zones()
        
        # Find and remove zone
        initial_count = len(zones_data['zones'])
        zones_data['zones'] = [z for z in zones_data['zones'] if z['id'] != zone_id]
        
        if len(zones_data['zones']) == initial_count:
            return False, f"Zone with ID {zone_id} not found"
        
        if self.save_zones(zones_data):
            return True, "Zone deleted successfully"
        else:
            return False, "Failed to save changes"
    
    def get_zone_by_id(self, zone_id: int) -> Optional[Dict]:
        """
        Get a zone by ID
        
        Args:
            zone_id: Zone ID
            
        Returns:
            Zone dict if found, None otherwise
        """
        zones_data = self.load_zones()
        
        for zone in zones_data['zones']:
            if zone['id'] == zone_id:
                return zone
        
        return None
    
    def set_enabled(self, enabled: bool) -> bool:
        """
        Enable or disable zone system
        
        Args:
            enabled: True to enable, False to disable
            
        Returns:
            True if successful
        """
        zones_data = self.load_zones()
        zones_data['enabled'] = enabled
        return self.save_zones(zones_data)


# Global instance
# Note: This singleton pattern is safe for the current Flask use case where:
# - Zone operations are infrequent and file-based
# - Flask handles request isolation
# - File system provides natural locking for concurrent access
_zone_manager = None

def get_zone_manager() -> ZoneConfigManager:
    """Get global zone manager instance"""
    global _zone_manager
    if _zone_manager is None:
        _zone_manager = ZoneConfigManager()
    return _zone_manager

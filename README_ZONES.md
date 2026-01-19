# Zone Configuration System - User Guide

## Overview

The Zone Configuration System allows you to define up to 4 detection zones in your warehouse with custom alert thresholds for each zone. Each zone is a polygon that can have 3-8 points, allowing you to create complex shapes that match your warehouse layout.

## Features

- ✅ **Up to 4 Zones**: Define up to 4 separate detection zones
- ✅ **Flexible Polygons**: Each zone can have 3-8 points for complex shapes
- ✅ **Per-Zone Alerts**: Set different alert thresholds for each zone
- ✅ **Overlap Detection**: System prevents overlapping zones
- ✅ **Percentage Coordinates**: Works with different image resolutions
- ✅ **Visual Editor**: Interactive canvas-based zone drawing
- ✅ **Enable/Disable**: Turn zones on/off without deleting them

## Getting Started

### 1. Access Zone Configuration

1. Log in to the system
2. Navigate to **Configuration** page
3. Click on the **Zone Configuration** tab

### 2. Upload Reference Image

1. Click **Upload Reference Image**
2. Select a clear photo of your warehouse
3. The image will be displayed on the canvas

### 3. Create a Zone

1. Click **Add New Zone** button
2. Click on the canvas to add points (minimum 3, maximum 8)
3. Right-click or double-click to finish the zone
4. The zone will be validated for overlaps

### 4. Edit Zone Properties

1. Find the zone in the **Configured Zones** list
2. Click **Edit** button
3. Update:
   - **Zone Name**: Give it a meaningful name (e.g., "Loading Area")
   - **Alert Threshold**: Set how long (in minutes) before an alert is sent

### 5. Save Configuration

1. Click **Save Zones** to save all zones to the server
2. The system will validate all zones before saving
3. A success message will confirm the save

## Zone Drawing Tips

### Adding Points
- **Left Click**: Add a new point to the current zone
- **Double Click**: Finish the current zone (minimum 3 points required)
- **Right Click**: Alternative way to finish the zone

### Editing Points
- **Drag**: Click and drag any point to adjust its position
- Points are numbered to help you identify them
- Points are automatically constrained to the canvas bounds

### Visual Indicators
- **Red**: Zone 1
- **Blue**: Zone 2
- **Green**: Zone 3
- **Yellow**: Zone 4
- **White Circles**: Point markers with numbers
- **Zone Name**: Displayed in the center of each zone

## Zone Management

### Enable/Disable Zone System

Toggle the **Enable Zone System** switch at the top of the page:
- **Enabled**: System uses zone-based detection with per-zone alerts
- **Disabled**: System falls back to global detection (backward compatible)

### Managing Individual Zones

For each zone, you can:
- **Edit**: Change name and alert threshold
- **Delete**: Remove the zone permanently
- **Enable/Disable**: Turn the zone on/off temporarily

### Clear All Zones

Click **Clear All Zones** to delete all configured zones at once. This action requires confirmation.

## Alert Thresholds

Each zone can have its own alert threshold:

- **Minimum**: 1 minute
- **Maximum**: 1440 minutes (24 hours)
- **Recommended**: 15-60 minutes for most use cases

**Example:**
- Loading Area: 15 minutes (fast-moving zone)
- Storage Zone: 60 minutes (slower-moving zone)
- Inspection Area: 30 minutes (medium-paced zone)

## Validation Rules

The system enforces these rules:

### Zone Limits
- ✅ Maximum 4 zones per system
- ✅ Minimum 3 points per zone
- ✅ Maximum 8 points per zone

### Zone Names
- ✅ Must be unique
- ✅ Cannot be empty
- ✅ Recommended: Use descriptive names

### Overlap Detection
- ✅ Zones cannot overlap
- ✅ System checks automatically before saving
- ✅ Error message shows which zones overlap

### Coordinates
- ✅ Stored as percentages (0-100%)
- ✅ Automatically scaled to image size
- ✅ Works with different image resolutions

## Backward Compatibility

The zone system is fully backward compatible:

- **Without Zones**: System works exactly as before
- **Zone System Disabled**: Falls back to global detection
- **No Database Changes**: Existing data is unaffected
- **Progressive Enhancement**: Add zones when ready

## Troubleshooting

### Canvas Not Showing

**Problem**: Canvas appears blank after uploading image  
**Solution**: 
- Ensure image file is a valid format (JPG, PNG)
- Try a smaller image file (< 5MB)
- Refresh the page and try again

### Cannot Add More Points

**Problem**: "Cannot add more than 8 points" message  
**Solution**: 
- Finish current zone (right-click or double-click)
- Each zone is limited to 8 points
- Start a new zone if you need more coverage

### Overlap Error

**Problem**: "Zones overlap" error when saving  
**Solution**: 
- Adjust zone boundaries to avoid overlap
- Use the visual editor to see where zones overlap
- Delete and recreate zones if necessary

### Zones Not Saving

**Problem**: Zones disappear after refresh  
**Solution**: 
- Click **Save Zones** button before leaving the page
- Check browser console for error messages
- Verify network connection to the server

### Zone System Not Working

**Problem**: Detections not respecting zones  
**Solution**: 
- Ensure **Enable Zone System** is toggled ON
- Verify at least one zone has **Enabled** status
- Check that zones cover your detection areas
- Restart detection service after zone changes

## Best Practices

### Planning Your Zones

1. **Take a Clear Photo**: Use good lighting and capture the full area
2. **Identify Key Areas**: Mark loading, storage, and inspection zones
3. **Set Realistic Thresholds**: Consider typical workflow times
4. **Test and Adjust**: Start with conservative thresholds

### Zone Design

1. **Keep It Simple**: Use 4-6 points for most zones
2. **Avoid Thin Zones**: Make zones wide enough for pallets
3. **Leave Gaps**: Don't make zones touch at boundaries
4. **Cover Detection Areas**: Ensure zones cover where pallets appear

### Maintenance

1. **Regular Review**: Check if zones match current layout
2. **Update Photos**: Replace reference image when layout changes
3. **Adjust Thresholds**: Fine-tune based on actual alert patterns
4. **Document Changes**: Keep notes on why zones were modified

## Advanced Features

### Percentage-Based Coordinates

Zones use percentage coordinates (0-100%) instead of pixels:

**Benefits:**
- Works with any image resolution
- Scales automatically
- No recalculation needed

**Example:**
```json
{
  "x": 25.5,  // 25.5% from left
  "y": 30.2   // 30.2% from top
}
```

### Zone Data Structure

Each zone is stored as:

```json
{
  "id": 1,
  "name": "Loading Area",
  "alertThreshold": 15,
  "points": [
    {"x": 10.5, "y": 20.3},
    {"x": 30.2, "y": 22.1},
    {"x": 28.5, "y": 45.8},
    {"x": 8.2, "y": 43.5}
  ],
  "enabled": true
}
```

### API Integration

For developers integrating with the zone system:

- **GET** `/api/zones` - Get all zones
- **POST** `/api/zones` - Create new zone
- **PUT** `/api/zones/<id>` - Update zone
- **DELETE** `/api/zones/<id>` - Delete zone
- **POST** `/api/zones/validate` - Validate zones

See `API_ZONES.md` for detailed API documentation.

## FAQ

**Q: Can I have more than 4 zones?**  
A: No, the system is limited to 4 zones for performance reasons.

**Q: Can zones overlap?**  
A: No, the system prevents overlapping zones to avoid ambiguity.

**Q: What happens if a pallet is outside all zones?**  
A: The system will still detect it but won't apply zone-specific alerts.

**Q: Can I export/import zones?**  
A: Zone data is stored in `config/zones.json` which can be backed up.

**Q: Do zones work with multiple cameras?**  
A: Each camera uses the same zone configuration currently.

**Q: How do I disable zones temporarily?**  
A: Toggle the **Enable Zone System** switch to OFF.

## Support

For issues or questions:

1. Check the **Troubleshooting** section above
2. Review `API_ZONES.md` for technical details
3. Contact system administrator
4. Submit issue on GitHub repository

---

**Version:** 1.0  
**Last Updated:** January 2026  
**Documentation:** README_ZONES.md

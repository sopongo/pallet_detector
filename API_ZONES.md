# Zone Configuration API Documentation

## Overview

This document describes the REST API endpoints for managing detection zones in the Pallet Detection System.

**Base URL:** `http://<host>:5000/api`

All endpoints return JSON responses with the following structure:

```json
{
  "success": true,
  "message": "Operation completed successfully",
  "data": {...}  // Optional
}
```

## Authentication

Currently, the API does not require authentication. This may change in future versions.

## Endpoints

### Get All Zones

Retrieve all configured zones and system status.

**Endpoint:** `GET /zones`

**Response:**

```json
{
  "success": true,
  "zones": [
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
  ],
  "enabled": true
}
```

**Status Codes:**
- `200 OK` - Success
- `500 Internal Server Error` - Server error

---

### Create Zone

Create a new detection zone.

**Endpoint:** `POST /zones`

**Request Body:**

```json
{
  "zone": {
    "id": 1,
    "name": "Loading Area",
    "alertThreshold": 15,
    "points": [
      {"x": 10.5, "y": 20.3},
      {"x": 30.2, "y": 22.1},
      {"x": 28.5, "y": 45.8}
    ],
    "enabled": true
  }
}
```

**Validation Rules:**
- Maximum 4 zones total
- Minimum 3 points, maximum 8 points
- Unique zone ID and name
- Alert threshold: 1-1440 minutes
- Points: x and y must be 0-100 (percentage)
- No overlaps with existing zones

**Response:**

Success:
```json
{
  "success": true,
  "message": "Zone added successfully"
}
```

Error:
```json
{
  "success": false,
  "message": "Cannot add more than 4 zones"
}
```

**Status Codes:**
- `200 OK` - Zone created successfully
- `400 Bad Request` - Validation failed
- `500 Internal Server Error` - Server error

---

### Update Zone

Update an existing zone.

**Endpoint:** `PUT /zones/<zone_id>`

**URL Parameters:**
- `zone_id` (integer) - ID of the zone to update

**Request Body:**

```json
{
  "zone": {
    "id": 1,
    "name": "Updated Loading Area",
    "alertThreshold": 30,
    "points": [
      {"x": 10.5, "y": 20.3},
      {"x": 30.2, "y": 22.1},
      {"x": 28.5, "y": 45.8},
      {"x": 8.2, "y": 43.5}
    ],
    "enabled": true
  }
}
```

**Response:**

Success:
```json
{
  "success": true,
  "message": "Zone updated successfully"
}
```

Error:
```json
{
  "success": false,
  "message": "Zone with ID 1 not found"
}
```

**Status Codes:**
- `200 OK` - Zone updated successfully
- `400 Bad Request` - Validation failed
- `404 Not Found` - Zone not found
- `500 Internal Server Error` - Server error

---

### Delete Zone

Delete a zone.

**Endpoint:** `DELETE /zones/<zone_id>`

**URL Parameters:**
- `zone_id` (integer) - ID of the zone to delete

**Response:**

Success:
```json
{
  "success": true,
  "message": "Zone deleted successfully"
}
```

Error:
```json
{
  "success": false,
  "message": "Zone with ID 1 not found"
}
```

**Status Codes:**
- `200 OK` - Zone deleted successfully
- `404 Not Found` - Zone not found
- `500 Internal Server Error` - Server error

---

### Validate Zones

Validate a list of zones for overlaps and other issues.

**Endpoint:** `POST /zones/validate`

**Request Body:**

```json
{
  "zones": [
    {
      "id": 1,
      "name": "Zone A",
      "alertThreshold": 15,
      "points": [
        {"x": 10.5, "y": 20.3},
        {"x": 30.2, "y": 22.1},
        {"x": 28.5, "y": 45.8}
      ],
      "enabled": true
    },
    {
      "id": 2,
      "name": "Zone B",
      "alertThreshold": 30,
      "points": [
        {"x": 50.5, "y": 20.3},
        {"x": 70.2, "y": 22.1},
        {"x": 68.5, "y": 45.8}
      ],
      "enabled": true
    }
  ]
}
```

**Response:**

Valid:
```json
{
  "success": true,
  "message": "Zones are valid",
  "valid": true
}
```

Invalid:
```json
{
  "success": true,
  "message": "Zones 'Zone A' and 'Zone B' overlap",
  "valid": false
}
```

**Status Codes:**
- `200 OK` - Validation completed (check `valid` field)
- `400 Bad Request` - Invalid request format
- `500 Internal Server Error` - Server error

---

### Enable/Disable Zone System

Enable or disable the entire zone system.

**Endpoint:** `POST /zones/enabled`

**Request Body:**

```json
{
  "enabled": true
}
```

**Response:**

Success:
```json
{
  "success": true,
  "message": "Zone system enabled"
}
```

**Status Codes:**
- `200 OK` - System status updated
- `400 Bad Request` - Missing 'enabled' parameter
- `500 Internal Server Error` - Server error

---

## Data Models

### Zone Object

```typescript
{
  id: number;              // Unique zone ID (1-4)
  name: string;            // Zone name (unique, non-empty)
  alertThreshold: number;  // Alert threshold in minutes (1-1440)
  points: Point[];         // Array of 3-8 points
  enabled: boolean;        // Whether zone is active
}
```

### Point Object

```typescript
{
  x: number;  // X coordinate as percentage (0-100)
  y: number;  // Y coordinate as percentage (0-100)
}
```

### Zones Data Object

```typescript
{
  zones: Zone[];    // Array of zone objects (max 4)
  enabled: boolean; // Whether zone system is enabled
}
```

---

## Error Handling

All endpoints follow consistent error handling:

### Validation Errors (400)

```json
{
  "success": false,
  "message": "Detailed error message explaining the validation failure"
}
```

Common validation errors:
- "Cannot add more than 4 zones"
- "Zone must have at least 3 points"
- "Zone cannot have more than 8 points"
- "Zones cannot overlap"
- "Zone name cannot be empty"
- "Alert threshold must be between 1 and 1440 minutes"

### Not Found Errors (404)

```json
{
  "success": false,
  "message": "Zone with ID <id> not found"
}
```

### Server Errors (500)

```json
{
  "success": false,
  "message": "Internal server error: <details>"
}
```

---

## Integration Examples

### Python

```python
import requests

API_BASE = "http://localhost:5000/api"

# Get all zones
response = requests.get(f"{API_BASE}/zones")
data = response.json()
print(f"Zones: {data['zones']}")

# Create a zone
new_zone = {
    "zone": {
        "id": 1,
        "name": "Loading Area",
        "alertThreshold": 15,
        "points": [
            {"x": 10.5, "y": 20.3},
            {"x": 30.2, "y": 22.1},
            {"x": 28.5, "y": 45.8}
        ],
        "enabled": True
    }
}

response = requests.post(f"{API_BASE}/zones", json=new_zone)
print(response.json())

# Update a zone
updated_zone = {
    "zone": {
        "id": 1,
        "name": "Updated Loading Area",
        "alertThreshold": 30,
        "points": [
            {"x": 10.5, "y": 20.3},
            {"x": 30.2, "y": 22.1},
            {"x": 28.5, "y": 45.8},
            {"x": 8.2, "y": 43.5}
        ],
        "enabled": True
    }
}

response = requests.put(f"{API_BASE}/zones/1", json=updated_zone)
print(response.json())

# Delete a zone
response = requests.delete(f"{API_BASE}/zones/1")
print(response.json())

# Enable zone system
response = requests.post(f"{API_BASE}/zones/enabled", json={"enabled": True})
print(response.json())
```

### JavaScript (Browser)

```javascript
const API_BASE = `http://${window.location.hostname}:5000/api`;

// Get all zones
async function getZones() {
    const response = await fetch(`${API_BASE}/zones`);
    const data = await response.json();
    console.log('Zones:', data.zones);
    return data;
}

// Create a zone
async function createZone(zone) {
    const response = await fetch(`${API_BASE}/zones`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ zone })
    });
    const result = await response.json();
    console.log(result.message);
    return result;
}

// Update a zone
async function updateZone(zoneId, zone) {
    const response = await fetch(`${API_BASE}/zones/${zoneId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ zone })
    });
    const result = await response.json();
    console.log(result.message);
    return result;
}

// Delete a zone
async function deleteZone(zoneId) {
    const response = await fetch(`${API_BASE}/zones/${zoneId}`, {
        method: 'DELETE'
    });
    const result = await response.json();
    console.log(result.message);
    return result;
}

// Validate zones
async function validateZones(zones) {
    const response = await fetch(`${API_BASE}/zones/validate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ zones })
    });
    const result = await response.json();
    return result.valid;
}

// Enable/disable zone system
async function setZoneSystemEnabled(enabled) {
    const response = await fetch(`${API_BASE}/zones/enabled`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ enabled })
    });
    const result = await response.json();
    console.log(result.message);
    return result;
}
```

### curl

```bash
# Get all zones
curl http://localhost:5000/api/zones

# Create a zone
curl -X POST http://localhost:5000/api/zones \
  -H "Content-Type: application/json" \
  -d '{
    "zone": {
      "id": 1,
      "name": "Loading Area",
      "alertThreshold": 15,
      "points": [
        {"x": 10.5, "y": 20.3},
        {"x": 30.2, "y": 22.1},
        {"x": 28.5, "y": 45.8}
      ],
      "enabled": true
    }
  }'

# Update a zone
curl -X PUT http://localhost:5000/api/zones/1 \
  -H "Content-Type: application/json" \
  -d '{
    "zone": {
      "id": 1,
      "name": "Updated Loading Area",
      "alertThreshold": 30,
      "points": [
        {"x": 10.5, "y": 20.3},
        {"x": 30.2, "y": 22.1},
        {"x": 28.5, "y": 45.8},
        {"x": 8.2, "y": 43.5}
      ],
      "enabled": true
    }
  }'

# Delete a zone
curl -X DELETE http://localhost:5000/api/zones/1

# Validate zones
curl -X POST http://localhost:5000/api/zones/validate \
  -H "Content-Type: application/json" \
  -d '{
    "zones": [
      {
        "id": 1,
        "name": "Zone A",
        "alertThreshold": 15,
        "points": [
          {"x": 10.5, "y": 20.3},
          {"x": 30.2, "y": 22.1},
          {"x": 28.5, "y": 45.8}
        ],
        "enabled": true
      }
    ]
  }'

# Enable zone system
curl -X POST http://localhost:5000/api/zones/enabled \
  -H "Content-Type: application/json" \
  -d '{"enabled": true}'
```

---

## Best Practices

### Performance

1. **Batch Operations**: When creating multiple zones, validate them together using `/zones/validate` before creating them individually
2. **Caching**: Cache zone data on the client side and only refresh when necessary
3. **Throttling**: Avoid rapid successive API calls when dragging points in the UI

### Error Handling

1. **Always Check `success`**: Don't assume success based on HTTP status code alone
2. **Display Error Messages**: Show the `message` field to users for better UX
3. **Retry Logic**: Implement exponential backoff for transient failures

### Security

1. **Input Validation**: Always validate data on both client and server
2. **Sanitization**: Sanitize zone names to prevent XSS attacks
3. **Rate Limiting**: Consider implementing rate limiting in production

---

## File Storage

Zone data is stored in `config/zones.json`:

```json
{
  "zones": [
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
  ],
  "enabled": true
}
```

**Backup Recommendation:** Regularly backup this file before making changes.

---

## Changelog

### Version 1.0 (January 2026)

- Initial release
- Support for up to 4 zones
- Polygon-based zones with 3-8 points
- Overlap detection using Shapely
- Percentage-based coordinates
- Enable/disable functionality
- Full CRUD operations

---

## Support

For API issues or questions:

1. Check error messages in response
2. Review validation rules above
3. Test with curl or Postman
4. Check server logs in `logs/`
5. Submit issue on GitHub

---

**Version:** 1.0  
**Last Updated:** January 2026  
**Documentation:** API_ZONES.md

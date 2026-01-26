/**
 * Zone Manager - Canvas-based polygon drawing for detection zones
 * Supports up to 20 zones with up to 8 points each
 * Uses normalized coordinates (0.0-1.0) for responsive sizing
 */

class ZoneManager {
    constructor(canvasId, options = {}) {
        this.canvas = document.getElementById(canvasId);
        if (!this.canvas) {
            console.error(`Canvas with id ${canvasId} not found`);
            return;
        }
        
        this.ctx = this.canvas.getContext('2d');
        this.zones = [];
        this.currentZone = null;
        this.selectedZone = null;
        this.draggedPoint = null;
        this.referenceImage = null;
        
        // Configuration - Updated to support 20 zones
        this.maxZones = 20;
        this.maxPoints = 8;
        this.pointRadius = 6;
        this.lineWidth = 2;
        this.colors = [
            '#FF0000', '#0000FF', '#00FF00', '#FFFF00', '#FF00FF',
            '#00FFFF', '#FFA500', '#800080', '#008000', '#FFC0CB',
            '#A52A2A', '#DEB887', '#5F9EA0', '#7FFF00', '#D2691E',
            '#DC143C', '#00CED1', '#9400D3', '#FF1493', '#FFD700'
        ]; // 20 distinct colors
        
        // API URL
        this.apiUrl = options.apiUrl || `http://${window.location.hostname}:5000/api`;
        
        // Bind event handlers
        this.canvas.addEventListener('click', this.handleClick.bind(this));
        this.canvas.addEventListener('dblclick', this.handleDoubleClick.bind(this));
        this.canvas.addEventListener('contextmenu', this.handleRightClick.bind(this));
        this.canvas.addEventListener('mousedown', this.handleMouseDown.bind(this));
        this.canvas.addEventListener('mousemove', this.handleMouseMove.bind(this));
        this.canvas.addEventListener('mouseup', this.handleMouseUp.bind(this));
        
        console.log('✅ ZoneManager initialized (max 20 zones)');
    }
    
    /**
     * Load reference image onto canvas (from file or base64)
     */
    loadImage(source) {
        return new Promise((resolve, reject) => {
            const img = new Image();
            img.onload = () => {
                this.referenceImage = img;
                
                // Resize canvas to fit image (max 1200px width)
                const maxWidth = 1200;
                const scale = Math.min(1, maxWidth / img.width);
                this.canvas.width = img.width * scale;
                this.canvas.height = img.height * scale;
                
                this.redraw();
                resolve();
            };
            img.onerror = reject;
            
            // Check if source is a File or base64 string
            if (source instanceof File) {
                const reader = new FileReader();
                reader.onload = (e) => {
                    img.src = e.target.result;
                };
                reader.onerror = reject;
                reader.readAsDataURL(source);
            } else if (typeof source === 'string') {
                // Assume base64 data URL
                img.src = source;
            } else {
                reject(new Error('Invalid image source'));
            }
        });
    }
    
    /**
     * Capture image from camera
     */
    async captureImage() {
        try {
            this.showMessage('Capturing image from camera...', 'info');
            
            const response = await fetch(`${this.apiUrl}/zones/capture`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });
            
            const result = await response.json();
            
            if (result.success) {
                // Load captured image onto canvas
                await this.loadImage(result.image);
                this.showMessage('Image captured successfully!', 'success');
                return true;
            } else {
                this.showMessage(`Capture failed: ${result.message}`, 'error');
                return false;
            }
        } catch (error) {
            console.error('Capture image error:', error);
            this.showMessage(`Capture error: ${error.message}`, 'error');
            return false;
        }
    }
    
    /**
     * Convert pixel coordinates to normalized coordinates (0.0-1.0)
     */
    pixelToNormalized(x, y) {
        return [
            Math.round(x / this.canvas.width * 10000) / 10000,
            Math.round(y / this.canvas.height * 10000) / 10000
        ];
    }
    
    /**
     * Convert normalized coordinates (0.0-1.0) to pixels
     */
    normalizedToPixel(x, y) {
        return {
            x: Math.round(x * this.canvas.width),
            y: Math.round(y * this.canvas.height)
        };
    }
    
    /**
     * Get mouse position relative to canvas
     */
    getMousePos(event) {
        const rect = this.canvas.getBoundingClientRect();
        return {
            x: event.clientX - rect.left,
            y: event.clientY - rect.top
        };
    }
    
    /**
     * Handle canvas click - add point to current zone
     */
    handleClick(event) {
        if (!this.currentZone) return;
        
        const pos = this.getMousePos(event);
        const normalizedPos = this.pixelToNormalized(pos.x, pos.y);
        
        // Check if we can add more points
        if (this.currentZone.polygon.length >= this.maxPoints) {
            this.showMessage(`Cannot add more than ${this.maxPoints} points per zone`, 'warning');
            return;
        }
        
        // Add point as [x, y] array
        this.currentZone.polygon.push(normalizedPos);
        this.redraw();
        
        // Update UI
        this.updatePointCount();
    }
    
    /**
     * Handle double-click - finish current zone
     */
    handleDoubleClick(event) {
        event.preventDefault();
        if (this.currentZone && this.currentZone.polygon.length >= 3) {
            this.finishZone();
        }
    }
    
    /**
     * Handle right-click - finish current zone
     */
    handleRightClick(event) {
        event.preventDefault();
        if (this.currentZone && this.currentZone.polygon.length >= 3) {
            this.finishZone();
        }
        return false;
    }
    
    /**
     * Handle mouse down - start dragging point
     */
    handleMouseDown(event) {
        const pos = this.getMousePos(event);
        
        // Check if clicking on existing point
        for (let zone of this.zones) {
            for (let i = 0; i < zone.polygon.length; i++) {
                const point = zone.polygon[i];
                const pixelPos = this.normalizedToPixel(point[0], point[1]);
                const dx = pos.x - pixelPos.x;
                const dy = pos.y - pixelPos.y;
                const distance = Math.sqrt(dx * dx + dy * dy);
                
                if (distance <= this.pointRadius + 2) {
                    this.draggedPoint = { zone, index: i };
                    this.canvas.style.cursor = 'grab';
                    return;
                }
            }
        }
    }
    
    /**
     * Handle mouse move - drag point
     */
    handleMouseMove(event) {
        if (this.draggedPoint) {
            const pos = this.getMousePos(event);
            const normalizedPos = this.pixelToNormalized(pos.x, pos.y);
            
            // Clamp to canvas bounds (0.0-1.0)
            normalizedPos[0] = Math.max(0, Math.min(1.0, normalizedPos[0]));
            normalizedPos[1] = Math.max(0, Math.min(1.0, normalizedPos[1]));
            
            // Update point
            this.draggedPoint.zone.polygon[this.draggedPoint.index] = normalizedPos;
            this.redraw();
        }
    }
    
    /**
     * Handle mouse up - stop dragging
     */
    handleMouseUp(event) {
        if (this.draggedPoint) {
            this.draggedPoint = null;
            this.canvas.style.cursor = 'default';
        }
    }
    
    /**
     * Start new zone
     */
    startNewZone() {
        // Check max zones
        if (this.zones.length >= this.maxZones) {
            this.showMessage(`Cannot create more than ${this.maxZones} zones`, 'error');
            return false;
        }
        
        // Generate new zone with updated field names
        const nextId = this.zones.length > 0 ? Math.max(...this.zones.map(z => z.id)) + 1 : 1;
        
        this.currentZone = {
            id: nextId,
            name: `Zone_${nextId}`,
            polygon: [],  // Changed from 'points'
            threshold_percent: 45.0,  // New field
            alert_threshold: 3000,  // Renamed from alertThreshold, in milliseconds
            pallet_type: 1,  // New field: 1=Inbound, 2=Outbound
            active: true  // Changed from 'enabled'
        };
        
        this.showMessage('Click to add points (3-8 points). Right-click or double-click to finish.', 'info');
        return true;
    }
    
    /**
     * Finish current zone
     */
    finishZone() {
        if (!this.currentZone) return;
        
        if (this.currentZone.polygon.length < 3) {
            this.showMessage('Zone must have at least 3 points', 'warning');
            return;
        }
        
        // Check for overlap with existing zones (backend will do accurate validation)
        // Client-side check is disabled to rely on backend Shapely validation
        
        // Add zone
        this.zones.push(this.currentZone);
        this.currentZone = null;
        
        this.redraw();
        this.updateZoneList();
        this.showMessage('Zone created successfully!', 'success');
    }
    
    /**
     * Check if two zones overlap
     * Note: Client-side check disabled - backend performs accurate validation using Shapely
     */
    checkOverlap(zone1, zone2) {
        // Disable client-side check
        // Let backend (Shapely) perform accurate polygon intersection
        return false;
    }
    
    /**
     * Get bounding box of points
     */
    getBoundingBox(points) {
        const xs = points.map(p => p.x);
        const ys = points.map(p => p.y);
        
        return {
            minX: Math.min(...xs),
            maxX: Math.max(...xs),
            minY: Math.min(...ys),
            maxY: Math.max(...ys)
        };
    }
    
    /**
     * Delete zone
     */
    deleteZone(zoneId) {
        this.zones = this.zones.filter(z => z.id !== zoneId);
        this.redraw();
        this.updateZoneList();
    }
    
    /**
     * Redraw canvas
     */
    redraw() {
        // Clear canvas
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        
        // Draw reference image
        if (this.referenceImage) {
            this.ctx.drawImage(this.referenceImage, 0, 0, this.canvas.width, this.canvas.height);
        } else {
            // Draw background
            this.ctx.fillStyle = '#f0f0f0';
            this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
        }
        
        // Draw all zones
        this.zones.forEach((zone, index) => {
            this.drawZone(zone, this.colors[index % this.colors.length], false);
        });
        
        // Draw current zone being created
        if (this.currentZone && this.currentZone.polygon.length > 0) {
            const colorIndex = this.zones.length % this.colors.length;
            this.drawZone(this.currentZone, this.colors[colorIndex], true);
        }
    }
    
    /**
     * Draw a single zone
     */
    drawZone(zone, color, isCurrent) {
        if (zone.polygon.length === 0) return;
        
        const alpha = isCurrent ? 0.3 : 0.2;
        
        // Convert points to pixels - points are now [x, y] arrays
        const pixelPoints = zone.polygon.map(p => this.normalizedToPixel(p[0], p[1]));
        
        // Draw polygon
        this.ctx.beginPath();
        this.ctx.moveTo(pixelPoints[0].x, pixelPoints[0].y);
        for (let i = 1; i < pixelPoints.length; i++) {
            this.ctx.lineTo(pixelPoints[i].x, pixelPoints[i].y);
        }
        if (!isCurrent || zone.polygon.length >= 3) {
            this.ctx.closePath();
        }
        
        // Fill
        this.ctx.fillStyle = color + Math.floor(alpha * 255).toString(16).padStart(2, '0');
        this.ctx.fill();
        
        // Stroke
        this.ctx.strokeStyle = color;
        this.ctx.lineWidth = this.lineWidth;
        this.ctx.stroke();
        
        // Draw points
        pixelPoints.forEach((point, index) => {
            this.ctx.beginPath();
            this.ctx.arc(point.x, point.y, this.pointRadius, 0, 2 * Math.PI);
            this.ctx.fillStyle = '#ffffff';
            this.ctx.fill();
            this.ctx.strokeStyle = color;
            this.ctx.lineWidth = 2;
            this.ctx.stroke();
            
            // Draw point number
            this.ctx.fillStyle = '#000000';
            this.ctx.font = '10px Arial';
            this.ctx.textAlign = 'center';
            this.ctx.textBaseline = 'middle';
            this.ctx.fillText((index + 1).toString(), point.x, point.y);
        });
        
        // Draw zone name
        if (!isCurrent && pixelPoints.length > 0) {
            const centerX = pixelPoints.reduce((sum, p) => sum + p.x, 0) / pixelPoints.length;
            const centerY = pixelPoints.reduce((sum, p) => sum + p.y, 0) / pixelPoints.length;
            
            this.ctx.fillStyle = color;
            this.ctx.font = 'bold 14px Arial';
            this.ctx.textAlign = 'center';
            this.ctx.textBaseline = 'middle';
            this.ctx.fillText(zone.name, centerX, centerY);
        }
    }
    
    /**
     * Update zone list UI
     */
    updateZoneList() {
        const container = document.getElementById('zoneList');
        if (!container) return;
        
        container.innerHTML = '';
        
        this.zones.forEach((zone, index) => {
            const palletTypeLabel = zone.pallet_type === 1 ? 'Inbound' : 'Outbound';
            const card = document.createElement('div');
            card.className = 'card mb-2';
            card.innerHTML = `
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-8">
                            <h5 style="color: ${this.colors[index % this.colors.length]}">
                                <i class="fas fa-draw-polygon"></i> ${zone.name}
                            </h5>
                            <p class="mb-1"><strong>Points:</strong> ${zone.polygon.length}</p>
                            <p class="mb-1"><strong>Threshold:</strong> ${zone.threshold_percent}%</p>
                            <p class="mb-1"><strong>Alert Time:</strong> ${zone.alert_threshold}ms</p>
                            <p class="mb-1"><strong>Pallet Type:</strong> ${palletTypeLabel}</p>
                            <p class="mb-0">
                                <strong>Status:</strong> 
                                <span class="badge ${zone.active ? 'badge-success' : 'badge-secondary'}">
                                    ${zone.active ? 'Active' : 'Inactive'}
                                </span>
                            </p>
                        </div>
                        <div class="col-md-4 text-right">
                            <button class="btn btn-sm btn-info mb-1" onclick="zoneManager.editZone(${zone.id})">
                                <i class="fas fa-edit"></i> Edit
                            </button>
                            <button class="btn btn-sm btn-danger mb-1" onclick="zoneManager.deleteZone(${zone.id})">
                                <i class="fas fa-trash"></i> Delete
                            </button>
                            <button class="btn btn-sm btn-${zone.active ? 'warning' : 'success'}" 
                                    onclick="zoneManager.toggleZone(${zone.id})">
                                <i class="fas fa-power-off"></i> ${zone.active ? 'Deactivate' : 'Activate'}
                            </button>
                        </div>
                    </div>
                </div>
            `;
            container.appendChild(card);
        });
        
        // Update zone usage badge
        const usedZonesEl = document.getElementById('usedZones');
        if (usedZonesEl) {
            usedZonesEl.textContent = `${this.zones.length}/${this.maxZones} zones used`;
        }
    }
    
    /**
     * Update point count for current zone
     */
    updatePointCount() {
        if (!this.currentZone) return;
        
        const remaining = this.maxPoints - this.currentZone.polygon.length;
        const pointCountEl = document.getElementById('currentZonePoints');
        if (pointCountEl) {
            pointCountEl.textContent = `${this.currentZone.polygon.length}/${this.maxPoints} points (${remaining} remaining)`;
        }
    }
    
    /**
     * Edit zone
     */
    editZone(zoneId) {
        const zone = this.zones.find(z => z.id === zoneId);
        if (!zone) return;
        
        // Show edit modal with enhanced fields
        Swal.fire({
            title: 'Edit Zone',
            html: `
                <div class="form-group text-left">
                    <label>Zone Name</label>
                    <input id="editZoneName" class="form-control" value="${zone.name}">
                </div>
                <div class="form-group text-left">
                    <label>Threshold Percent (%)</label>
                    <input id="editThresholdPercent" type="number" class="form-control" 
                           value="${zone.threshold_percent}" min="0" max="100" step="0.1">
                    <small class="form-text text-muted">Detection threshold percentage (0-100)</small>
                </div>
                <div class="form-group text-left">
                    <label>Alert Threshold (ms)</label>
                    <input id="editAlertThreshold" type="number" class="form-control" 
                           value="${zone.alert_threshold}" min="1">
                    <small class="form-text text-muted">Alert time threshold in milliseconds</small>
                </div>
                <div class="form-group text-left">
                    <label>Pallet Type</label>
                    <div class="form-check">
                        <input class="form-check-input" type="radio" name="palletType" id="palletInbound" 
                               value="1" ${zone.pallet_type === 1 ? 'checked' : ''}>
                        <label class="form-check-label" for="palletInbound">
                            Inbound
                        </label>
                    </div>
                    <div class="form-check">
                        <input class="form-check-input" type="radio" name="palletType" id="palletOutbound" 
                               value="2" ${zone.pallet_type === 2 ? 'checked' : ''}>
                        <label class="form-check-label" for="palletOutbound">
                            Outbound
                        </label>
                    </div>
                </div>
            `,
            showCancelButton: true,
            confirmButtonText: 'Save',
            width: '500px',
            preConfirm: () => {
                const name = document.getElementById('editZoneName').value;
                const thresholdPercent = parseFloat(document.getElementById('editThresholdPercent').value);
                const alertThreshold = parseInt(document.getElementById('editAlertThreshold').value);
                const palletType = parseInt(document.querySelector('input[name="palletType"]:checked').value);
                
                if (!name) {
                    Swal.showValidationMessage('Please enter a zone name');
                    return false;
                }
                
                if (isNaN(thresholdPercent) || thresholdPercent < 0 || thresholdPercent > 100) {
                    Swal.showValidationMessage('Threshold percent must be between 0 and 100');
                    return false;
                }
                
                if (isNaN(alertThreshold) || alertThreshold < 1) {
                    Swal.showValidationMessage('Alert threshold must be at least 1ms');
                    return false;
                }
                
                return { name, thresholdPercent, alertThreshold, palletType };
            }
        }).then((result) => {
            if (result.isConfirmed) {
                zone.name = result.value.name;
                zone.threshold_percent = result.value.thresholdPercent;
                zone.alert_threshold = result.value.alertThreshold;
                zone.pallet_type = result.value.palletType;
                this.redraw();
                this.updateZoneList();
                this.showMessage('Zone updated successfully', 'success');
            }
        });
    }
    
    /**
     * Toggle zone active/inactive
     */
    toggleZone(zoneId) {
        const zone = this.zones.find(z => z.id === zoneId);
        if (!zone) return;
        
        zone.active = !zone.active;
        this.updateZoneList();
    }
    
    /**
     * Save all zones to backend
     */
    async saveZones() {
        try {
            if (!this.referenceImage) {
                this.showMessage('Please capture an image first', 'warning');
                return;
            }
            
            // Step 1: Save master and polygon images
            // Master image: original camera capture
            // Polygon image: canvas with zones drawn
            const masterImageData = await this.getCanvasImageData(false);  // Without zones
            const polygonImageData = await this.getCanvasImageData(true);  // With zones
            
            const imageResponse = await fetch(`${this.apiUrl}/zones/save-image`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    master_image: masterImageData,
                    polygon_image: polygonImageData
                })
            });
            
            const imageResult = await imageResponse.json();
            if (!imageResult.success) {
                this.showMessage(`Failed to save images: ${imageResult.message}`, 'error');
                return;
            }
            
            console.log('✅ Images saved:', imageResult.master_path, imageResult.polygon_path);
            
            // Step 2: Validate zones on backend
            const validateResponse = await fetch(`${this.apiUrl}/zones/validate`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ zones: this.zones })
            });
            
            const validateResult = await validateResponse.json();
            
            if (!validateResult.valid) {
                this.showMessage(`Validation error: ${validateResult.message}`, 'error');
                return;
            }
            
            // Step 3: Save zones configuration
            const saveResponse = await fetch(`${this.apiUrl}/zones/save`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ zones: this.zones })
            });
            
            const saveResult = await saveResponse.json();
            
            if (saveResult.success) {
                this.showMessage('Zones saved successfully!', 'success');
                console.log('✅ Zones configuration saved');
            } else {
                this.showMessage(`Save failed: ${saveResult.message}`, 'error');
            }
            
        } catch (error) {
            console.error('Save zones error:', error);
            this.showMessage('Failed to save zones: ' + error.message, 'error');
        }
    }
    
    /**
     * Get canvas image as base64 data URL
     * @param {boolean} withZones - Include zone overlays or just master image
     */
    async getCanvasImageData(withZones) {
        // Create temporary canvas
        const tempCanvas = document.createElement('canvas');
        tempCanvas.width = this.canvas.width;
        tempCanvas.height = this.canvas.height;
        const tempCtx = tempCanvas.getContext('2d');
        
        // Draw reference image
        if (this.referenceImage) {
            tempCtx.drawImage(this.referenceImage, 0, 0, tempCanvas.width, tempCanvas.height);
        }
        
        // Draw zones if requested
        if (withZones) {
            this.zones.forEach((zone, index) => {
                this.drawZoneOnContext(tempCtx, zone, this.colors[index % this.colors.length]);
            });
        }
        
        // Convert to data URL
        return tempCanvas.toDataURL('image/jpeg', 0.9);
    }
    
    /**
     * Draw zone on a specific context (helper for image export)
     */
    drawZoneOnContext(ctx, zone, color) {
        if (zone.polygon.length === 0) return;
        
        const alpha = 0.2;
        const pixelPoints = zone.polygon.map(p => this.normalizedToPixel(p[0], p[1]));
        
        // Draw polygon
        ctx.beginPath();
        ctx.moveTo(pixelPoints[0].x, pixelPoints[0].y);
        for (let i = 1; i < pixelPoints.length; i++) {
            ctx.lineTo(pixelPoints[i].x, pixelPoints[i].y);
        }
        ctx.closePath();
        
        // Fill
        ctx.fillStyle = color + Math.floor(alpha * 255).toString(16).padStart(2, '0');
        ctx.fill();
        
        // Stroke
        ctx.strokeStyle = color;
        ctx.lineWidth = this.lineWidth;
        ctx.stroke();
        
        // Draw points
        pixelPoints.forEach((point, index) => {
            ctx.beginPath();
            ctx.arc(point.x, point.y, this.pointRadius, 0, 2 * Math.PI);
            ctx.fillStyle = '#ffffff';
            ctx.fill();
            ctx.strokeStyle = color;
            ctx.lineWidth = 2;
            ctx.stroke();
            
            ctx.fillStyle = '#000000';
            ctx.font = '10px Arial';
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            ctx.fillText((index + 1).toString(), point.x, point.y);
        });
        
        // Draw zone name
        if (pixelPoints.length > 0) {
            const centerX = pixelPoints.reduce((sum, p) => sum + p.x, 0) / pixelPoints.length;
            const centerY = pixelPoints.reduce((sum, p) => sum + p.y, 0) / pixelPoints.length;
            
            ctx.fillStyle = color;
            ctx.font = 'bold 14px Arial';
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            ctx.fillText(zone.name, centerX, centerY);
        }
    }
    
    /**
     * Load zones from backend
     */
    async loadZones() {
        try {
            const response = await fetch(`${this.apiUrl}/zones`);
            const data = await response.json();
            
            if (data.success) {
                this.zones = data.zones || [];
                this.redraw();
                this.updateZoneList();
                console.log(`✅ Loaded ${this.zones.length} zones`);
                return this.zones;
            } else {
                throw new Error(data.message);
            }
        } catch (error) {
            console.error('Load zones error:', error);
            this.showMessage('Failed to load zones: ' + error.message, 'error');
            return [];
        }
    }
    
    /**
     * Load latest zone images from backend
     */
    async loadLatestImages() {
        try {
            const response = await fetch(`${this.apiUrl}/zones/latest-images`);
            const data = await response.json();
            
            if (data.success && data.master_image) {
                // Load the master image
                const imagePath = `${window.location.origin}/${data.master_image}`;
                await this.loadImage(imagePath);
                console.log('✅ Loaded latest zone image:', data.master_image);
                return true;
            } else {
                console.log('No previous zone images found');
                return false;
            }
        } catch (error) {
            console.error('Load latest images error:', error);
            return false;
        }
    }
    
    /**
     * Show message to user
     */
    showMessage(message, type = 'info') {
        const icons = {
            success: 'success',
            error: 'error',
            warning: 'warning',
            info: 'info'
        };
        
        Swal.fire({
            icon: icons[type] || 'info',
            title: message,
            toast: true,
            position: 'top-end',
            showConfirmButton: false,
            timer: 3000,
            timerProgressBar: true
        });
    }
}

// Global instance
let zoneManager;

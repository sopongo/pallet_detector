/**
 * Zone Manager - Canvas-based polygon drawing for detection zones
 * Supports up to 20 zones with 3-8 points each
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
        
        // Configuration - Read maxZones from dropdown, default to 20
        const maxZonesSelect = document.getElementById('maxZonesSelect');
        this.maxZones = maxZonesSelect ? parseInt(maxZonesSelect.value) : 20;
        this.maxPoints = 8;
        this.minPoints = 3;
        this.pointRadius = 6;
        this.lineWidth = 2;
        this.colors = ['#FF0000', '#0000FF', '#00FF00', '#FFFF00', '#FF00FF', '#00FFFF', 
                       '#FFA500', '#800080', '#008080', '#FFC0CB', '#A52A2A', '#FFD700',
                       '#4B0082', '#FF1493', '#00FF7F', '#DC143C', '#7FFF00', '#FF6347',
                       '#4682B4', '#D2691E']; // 20 colors for up to 20 zones
        
        // API URL
        this.apiUrl = options.apiUrl || `http://${window.location.hostname}:5000/api`;
        
        // Bind event handlers
        this.canvas.addEventListener('click', this.handleClick.bind(this));
        this.canvas.addEventListener('dblclick', this.handleDoubleClick.bind(this));
        this.canvas.addEventListener('contextmenu', this.handleRightClick.bind(this));
        this.canvas.addEventListener('mousedown', this.handleMouseDown.bind(this));
        this.canvas.addEventListener('mousemove', this.handleMouseMove.bind(this));
        this.canvas.addEventListener('mouseup', this.handleMouseUp.bind(this));
        
        console.log('✅ ZoneManager initialized with maxZones:', this.maxZones);
    }
    
    /**
     * Load reference image onto canvas
     */
    loadImage(imageFile) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            reader.onload = (e) => {
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
                img.src = e.target.result;
            };
            reader.onerror = reject;
            reader.readAsDataURL(imageFile);
        });
    }
    
    /**
     * Load image from server path
     */
    async loadImageFromPath(imagePath) {
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
            img.src = imagePath + '?t=' + Date.now(); // Cache bust
        });
    }
    
    /**
     * Capture image from camera
     */
    async captureImageFromCamera() {
        const response = await fetch(`${this.apiUrl}/zones/capture`, {
            method: 'POST'
        });
        
        if (!response.ok) {
            throw new Error('Failed to capture image from camera');
        }
        
        const result = await response.json();
        
        if (result.success && result.image_path) {
            await this.loadImageFromPath(result.image_path);
        } else {
            throw new Error(result.message || 'Failed to capture image');
        }
    }
    
    /**
     * Convert pixel coordinates to normalized coordinates (0.0-1.0)
     */
    pixelToPercent(x, y) {
        return {
            x: Math.round(x / this.canvas.width * 10000) / 10000,
            y: Math.round(y / this.canvas.height * 10000) / 10000
        };
    }
    
    /**
     * Convert normalized coordinates (0.0-1.0) to pixels
     */
    percentToPixel(x, y) {
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
        const percentPos = this.pixelToPercent(pos.x, pos.y);
        
        // Check if we can add more points
        if (this.currentZone.polygon.length >= this.maxPoints) {
            this.showMessage(`Cannot add more than ${this.maxPoints} points per zone`, 'warning');
            return;
        }
        
        // Add point - store as array [x, y]
        this.currentZone.polygon.push([percentPos.x, percentPos.y]);
        this.redraw();
        
        // Update UI
        this.updatePointCount();
    }
    
    /**
     * Handle double-click - finish current zone
     */
    handleDoubleClick(event) {
        event.preventDefault();
        if (this.currentZone && this.currentZone.polygon.length >= this.minPoints) {
            this.finishZone();
        }
    }
    
    /**
     * Handle right-click - finish current zone
     */
    handleRightClick(event) {
        event.preventDefault();
        if (this.currentZone && this.currentZone.polygon.length >= this.minPoints) {
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
                const pixelPos = this.percentToPixel(point[0], point[1]);
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
            const percentPos = this.pixelToPercent(pos.x, pos.y);
            
            // Clamp to canvas bounds (0.0-1.0)
            percentPos.x = Math.max(0, Math.min(1.0, percentPos.x));
            percentPos.y = Math.max(0, Math.min(1.0, percentPos.y));
            
            // Update point - store as array [x, y]
            this.draggedPoint.zone.polygon[this.draggedPoint.index] = [percentPos.x, percentPos.y];
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
        
        // Generate new zone
        const nextId = this.zones.length > 0 ? Math.max(...this.zones.map(z => z.id)) + 1 : 1;
        
        this.currentZone = {
            id: nextId,
            name: `Zone_${nextId}`,
            polygon: [], // Array of [x, y] normalized coordinates
            threshold_percent: 45.0,
            alert_threshold: 3000,
            pallet_type: 1,
            active: true
        };
        
        this.showMessage('Click to add points (3-8 points). Right-click or double-click to finish.', 'info');
        return true;
    }
    
    /**
     * Finish current zone
     */
    finishZone() {
        if (!this.currentZone) return;
        
        if (this.currentZone.polygon.length < this.minPoints) {
            this.showMessage(`Zone must have at least ${this.minPoints} points`, 'warning');
            return;
        }
        
        if (this.currentZone.polygon.length > this.maxPoints) {
            this.showMessage(`Zone cannot have more than ${this.maxPoints} points`, 'warning');
            return;
        }
        
        // Check for overlap with existing zones - backend will validate
        // Client-side check is disabled
        
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
        
        // Convert points to pixels
        const pixelPoints = zone.polygon.map(p => this.percentToPixel(p[0], p[1]));
        
        // Draw polygon
        this.ctx.beginPath();
        this.ctx.moveTo(pixelPoints[0].x, pixelPoints[0].y);
        for (let i = 1; i < pixelPoints.length; i++) {
            this.ctx.lineTo(pixelPoints[i].x, pixelPoints[i].y);
        }
        if (!isCurrent || zone.polygon.length >= this.minPoints) {
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
            const card = document.createElement('div');
            card.className = 'card mb-2';
            const palletTypeText = zone.pallet_type === 1 ? 'Inbound' : 'Outbound';
            card.innerHTML = `
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-8">
                            <h5 style="color: ${this.colors[index % this.colors.length]}">
                                <i class="fas fa-draw-polygon"></i> ${zone.name}
                            </h5>
                            <p class="mb-1"><strong>Points:</strong> ${zone.polygon.length}</p>
                            <p class="mb-1"><strong>Threshold:</strong> ${zone.threshold_percent}%</p>
                            <p class="mb-1"><strong>Alert Threshold:</strong> ${zone.alert_threshold} seconds</p>
                            <p class="mb-1"><strong>Pallet Type:</strong> ${palletTypeText}</p>
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
        
        // Update remaining zones count
        const used = this.zones.length;
        const remainingEl = document.getElementById('remainingZones');
        if (remainingEl) {
            remainingEl.textContent = `${used}/${this.maxZones} zones used`;
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
                           value="${zone.threshold_percent}" min="1" max="100">
                    <small class="form-text text-muted">Detection threshold percentage (1-100%)</small>
                </div>
                <div class="form-group text-left">
                    <label>Alert Threshold (seconds)</label>
                    <input id="editAlertThreshold" type="number" class="form-control" 
                           value="${zone.alert_threshold}" min="1">
                    <small class="form-text text-muted">Time before alert is triggered</small>
                </div>
                <div class="form-group text-left">
                    <label>Pallet Type</label><br>
                    <div class="form-check form-check-inline">
                        <input class="form-check-input" type="radio" name="palletType" id="palletType1" 
                               value="1" ${zone.pallet_type === 1 ? 'checked' : ''}>
                        <label class="form-check-label" for="palletType1">1 - Inbound</label>
                    </div>
                    <div class="form-check form-check-inline">
                        <input class="form-check-input" type="radio" name="palletType" id="palletType2" 
                               value="2" ${zone.pallet_type === 2 ? 'checked' : ''}>
                        <label class="form-check-label" for="palletType2">2 - Outbound</label>
                    </div>
                </div>
            `,
            showCancelButton: true,
            confirmButtonText: 'Save',
            width: '500px',
            preConfirm: () => {
                const name = document.getElementById('editZoneName').value;
                const threshold_percent = parseFloat(document.getElementById('editThresholdPercent').value);
                const alert_threshold = parseInt(document.getElementById('editAlertThreshold').value);
                const pallet_type = parseInt(document.querySelector('input[name="palletType"]:checked').value);
                
                if (!name || !name.trim()) {
                    Swal.showValidationMessage('Please enter a zone name');
                    return false;
                }
                
                if (!threshold_percent || threshold_percent < 1 || threshold_percent > 100) {
                    Swal.showValidationMessage('Threshold percent must be between 1 and 100');
                    return false;
                }
                
                if (!alert_threshold || alert_threshold < 1) {
                    Swal.showValidationMessage('Alert threshold must be at least 1 second');
                    return false;
                }
                
                return { name, threshold_percent, alert_threshold, pallet_type };
            }
        }).then((result) => {
            if (result.isConfirmed) {
                zone.name = result.value.name;
                zone.threshold_percent = result.value.threshold_percent;
                zone.alert_threshold = result.value.alert_threshold;
                zone.pallet_type = result.value.pallet_type;
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
     * Create master image blob (without polygons)
     */
    async createMasterImageBlob() {
        // Create temporary canvas with just the reference image
        const tempCanvas = document.createElement('canvas');
        tempCanvas.width = this.canvas.width;
        tempCanvas.height = this.canvas.height;
        const tempCtx = tempCanvas.getContext('2d');
        
        if (this.referenceImage) {
            tempCtx.drawImage(this.referenceImage, 0, 0, tempCanvas.width, tempCanvas.height);
        }
        
        return new Promise(resolve => {
            tempCanvas.toBlob(resolve, 'image/jpeg', 0.9);
        });
    }
    
    /**
     * Create polygon image blob (with polygons drawn)
     */
    async createPolygonImageBlob() {
        // Current canvas already has polygons drawn
        return new Promise(resolve => {
            this.canvas.toBlob(resolve, 'image/jpeg', 0.9);
        });
    }
    
    /**
     * Save all zones to backend
     */
    async saveZones() {
        try {
            if (!this.referenceImage) {
                this.showMessage('Please capture an image first', 'error');
                return;
            }
            
            // Generate date components for filenames
            const date = new Date();
            const dd = date.getDate().toString().padStart(2, '0');
            const mm = (date.getMonth() + 1).toString().padStart(2, '0');
            const yyyy = date.getFullYear();
            
            // Create both images
            const masterBlob = await this.createMasterImageBlob();
            const polygonBlob = await this.createPolygonImageBlob();
            
            // Upload master image: img_master_configzone_dd-mm-yyyy.jpg
            const masterFilename = `img_master_configzone_${dd}-${mm}-${yyyy}.jpg`;
            const masterFormData = new FormData();
            masterFormData.append('image', masterBlob, masterFilename);
            
            const masterResponse = await fetch(`${this.apiUrl}/zones/save-image`, {
                method: 'POST',
                body: masterFormData
            });
            
            if (!masterResponse.ok) {
                throw new Error('Failed to save master image');
            }
            
            // Upload polygon image: img_polygon_configzone_dd-mm-yyyy.jpg
            const polygonFilename = `img_polygon_configzone_${dd}-${mm}-${yyyy}.jpg`;
            const polygonFormData = new FormData();
            polygonFormData.append('image', polygonBlob, polygonFilename);
            
            const polygonResponse = await fetch(`${this.apiUrl}/zones/save-image`, {
                method: 'POST',
                body: polygonFormData
            });
            
            if (!polygonResponse.ok) {
                throw new Error('Failed to save polygon image');
            }
            
            console.log('✅ Images saved:', masterFilename, polygonFilename);
            
            // Validate zones on backend using Shapely
            const validateResponse = await fetch(`${this.apiUrl}/zones/validate`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ zones: this.zones })
            });
            
            const validateResult = await validateResponse.json();
            
            if (!validateResult.valid) {
                this.showMessage(validateResult.message, 'error');
                return;
            }
            
            // Save zones JSON
            const saveResponse = await fetch(`${this.apiUrl}/zones/save`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ zones: this.zones })
            });
            
            const saveResult = await saveResponse.json();
            
            if (saveResult.success) {
                this.showMessage('Zones and images saved successfully!', 'success');
            } else {
                this.showMessage(saveResult.message || 'Failed to save zones', 'error');
            }
            
        } catch (error) {
            console.error('Save zones error:', error);
            this.showMessage('Failed to save zones: ' + error.message, 'error');
        }
    }
    
    /**
     * Load zones from backend
     */
    async loadZones() {
        try {
            const response = await fetch(`${this.apiUrl}/zones/load`);
            const data = await response.json();
            
            if (data.success && data.zones) {
                this.zones = data.zones;
                this.redraw();
                this.updateZoneList();
                console.log('✅ Zones loaded:', this.zones.length);
                return this.zones;
            } else {
                console.warn('No zones found or failed to load');
                return [];
            }
        } catch (error) {
            console.error('Load zones error:', error);
            this.showMessage('Failed to load zones: ' + error.message, 'error');
            return [];
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

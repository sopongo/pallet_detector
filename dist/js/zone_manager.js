/**
 * Zone Manager - Canvas-based polygon drawing for detection zones
 * Supports up to 4 zones with up to 8 points each
 * Uses percentage-based coordinates for responsive sizing
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
        
        // Configuration
        this.maxZones = 4;
        this.maxPoints = 8;
        this.pointRadius = 6;
        this.lineWidth = 2;
        this.colors = ['#FF0000', '#0000FF', '#00FF00', '#FFFF00']; // Red, Blue, Green, Yellow
        
        // API URL
        this.apiUrl = options.apiUrl || `http://${window.location.hostname}:5000/api`;
        
        // Bind event handlers
        this.canvas.addEventListener('click', this.handleClick.bind(this));
        this.canvas.addEventListener('dblclick', this.handleDoubleClick.bind(this));
        this.canvas.addEventListener('contextmenu', this.handleRightClick.bind(this));
        this.canvas.addEventListener('mousedown', this.handleMouseDown.bind(this));
        this.canvas.addEventListener('mousemove', this.handleMouseMove.bind(this));
        this.canvas.addEventListener('mouseup', this.handleMouseUp.bind(this));
        
        console.log('✅ ZoneManager initialized');
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
        if (this.currentZone.points.length >= this.maxPoints) {
            this.showMessage(`Cannot add more than ${this.maxPoints} points per zone`, 'warning');
            return;
        }
        
        // Add point
        this.currentZone.points.push(percentPos);
        this.redraw();
        
        // Update UI
        this.updatePointCount();
    }
    
    /**
     * Handle double-click - finish current zone
     */
    handleDoubleClick(event) {
        event.preventDefault();
        if (this.currentZone && this.currentZone.points.length >= 3) {
            this.finishZone();
        }
    }
    
    /**
     * Handle right-click - finish current zone
     */
    handleRightClick(event) {
        event.preventDefault();
        if (this.currentZone && this.currentZone.points.length >= 3) {
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
            for (let i = 0; i < zone.points.length; i++) {
                const point = zone.points[i];
                const pixelPos = this.percentToPixel(point.x, point.y);
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
            
            // Clamp to canvas bounds
            percentPos.x = Math.max(0, Math.min(100, percentPos.x));
            percentPos.y = Math.max(0, Math.min(100, percentPos.y));
            
            // Update point
            this.draggedPoint.zone.points[this.draggedPoint.index] = percentPos;
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
            name: `Zone ${nextId}`,
            points: [],
            alertThreshold: 30,
            enabled: true
        };
        
        this.showMessage('Click to add points (3-8 points). Right-click or double-click to finish.', 'info');
        return true;
    }
    
    /**
     * Finish current zone
     */
    finishZone() {
        if (!this.currentZone) return;
        
        if (this.currentZone.points.length < 3) {
            this.showMessage('Zone must have at least 3 points', 'warning');
            return;
        }
        
        // Check for overlap with existing zones
        for (let zone of this.zones) {
            if (this.checkOverlap(this.currentZone, zone)) {
                this.showMessage(`Zone overlaps with "${zone.name}"`, 'error');
                return;
            }
        }
        
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
        if (this.currentZone && this.currentZone.points.length > 0) {
            const colorIndex = this.zones.length % this.colors.length;
            this.drawZone(this.currentZone, this.colors[colorIndex], true);
        }
    }
    
    /**
     * Draw a single zone
     */
    drawZone(zone, color, isCurrent) {
        if (zone.points.length === 0) return;
        
        const alpha = isCurrent ? 0.3 : 0.2;
        
        // Convert points to pixels
        const pixelPoints = zone.points.map(p => this.percentToPixel(p.x, p.y));
        
        // Draw polygon
        this.ctx.beginPath();
        this.ctx.moveTo(pixelPoints[0].x, pixelPoints[0].y);
        for (let i = 1; i < pixelPoints.length; i++) {
            this.ctx.lineTo(pixelPoints[i].x, pixelPoints[i].y);
        }
        if (!isCurrent || zone.points.length >= 3) {
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
            card.innerHTML = `
                <div class="card-body">
                    <div class="row">
                        <div class="col-md-8">
                            <h5 style="color: ${this.colors[index % this.colors.length]}">
                                <i class="fas fa-draw-polygon"></i> ${zone.name}
                            </h5>
                            <p class="mb-1"><strong>Points:</strong> ${zone.points.length}</p>
                            <p class="mb-1"><strong>Alert Threshold:</strong> ${zone.alertThreshold} minutes</p>
                            <p class="mb-0">
                                <strong>Status:</strong> 
                                <span class="badge ${zone.enabled ? 'badge-success' : 'badge-secondary'}">
                                    ${zone.enabled ? 'Enabled' : 'Disabled'}
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
                            <button class="btn btn-sm btn-${zone.enabled ? 'warning' : 'success'}" 
                                    onclick="zoneManager.toggleZone(${zone.id})">
                                <i class="fas fa-power-off"></i> ${zone.enabled ? 'Disable' : 'Enable'}
                            </button>
                        </div>
                    </div>
                </div>
            `;
            container.appendChild(card);
        });
        
        // Update remaining zones count
        const remaining = this.maxZones - this.zones.length;
        const remainingEl = document.getElementById('remainingZones');
        if (remainingEl) {
            remainingEl.textContent = `${remaining} zone${remaining !== 1 ? 's' : ''} remaining`;
        }
    }
    
    /**
     * Update point count for current zone
     */
    updatePointCount() {
        if (!this.currentZone) return;
        
        const remaining = this.maxPoints - this.currentZone.points.length;
        const pointCountEl = document.getElementById('currentZonePoints');
        if (pointCountEl) {
            pointCountEl.textContent = `${this.currentZone.points.length}/${this.maxPoints} points (${remaining} remaining)`;
        }
    }
    
    /**
     * Edit zone
     */
    editZone(zoneId) {
        const zone = this.zones.find(z => z.id === zoneId);
        if (!zone) return;
        
        // Show edit modal or inline edit
        Swal.fire({
            title: 'Edit Zone',
            html: `
                <div class="form-group text-left">
                    <label>Zone Name</label>
                    <input id="editZoneName" class="form-control" value="${zone.name}">
                </div>
                <div class="form-group text-left">
                    <label>Alert Threshold (minutes)</label>
                    <input id="editZoneThreshold" type="number" class="form-control" value="${zone.alertThreshold}" min="1" max="1440">
                </div>
            `,
            showCancelButton: true,
            confirmButtonText: 'Save',
            preConfirm: () => {
                const name = document.getElementById('editZoneName').value;
                const threshold = parseInt(document.getElementById('editZoneThreshold').value);
                
                if (!name) {
                    Swal.showValidationMessage('Please enter a zone name');
                    return false;
                }
                
                if (!threshold || threshold < 1 || threshold > 1440) {
                    Swal.showValidationMessage('Alert threshold must be between 1 and 1440 minutes');
                    return false;
                }
                
                return { name, threshold };
            }
        }).then((result) => {
            if (result.isConfirmed) {
                zone.name = result.value.name;
                zone.alertThreshold = result.value.threshold;
                this.redraw();
                this.updateZoneList();
                this.showMessage('Zone updated successfully', 'success');
            }
        });
    }
    
    /**
     * Toggle zone enabled/disabled
     */
    toggleZone(zoneId) {
        const zone = this.zones.find(z => z.id === zoneId);
        if (!zone) return;
        
        zone.enabled = !zone.enabled;
        this.updateZoneList();
    }
    
    /**
     * Save reference image to server
     */
    async saveReferenceImage() {
        if (!this.referenceImage) return null;
        
        try {
            // Convert canvas to blob
            const blob = await new Promise(resolve => {
                this.canvas.toBlob(resolve, 'image/jpeg', 0.9);
            });
            
            // Generate filename: img_configzone_dd-mm-yyyy.jpg
            const now = new Date();
            const dd = now.getDate().toString().padStart(2, '0');
            const mm = (now.getMonth() + 1).toString().padStart(2, '0');
            const yyyy = now.getFullYear();
            const filename = `img_configzone_${dd}-${mm}-${yyyy}.jpg`;
            
            // Upload via FormData
            const formData = new FormData();
            formData.append('image', blob, filename);
            
            const response = await fetch(`${this.apiUrl}/zones/image`, {
                method: 'POST',
                body: formData
            });
            
            const result = await response.json();
            return result.success ? result.filepath : null;
        } catch (error) {
            console.error('Error saving reference image:', error);
            return null;
        }
    }
    
    /**
     * Save all zones to backend
     */
    async saveZones() {
        try {
            // Save reference image first
            const imagePath = await this.saveReferenceImage();
            if (imagePath) {
                console.log('✅ Reference image saved:', imagePath);
            }
            
            // Validate zones on backend
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
            
            // Save each zone
            const existingZones = await this.loadZones();
            
            // Delete zones that no longer exist
            for (let existingZone of existingZones) {
                if (!this.zones.find(z => z.id === existingZone.id)) {
                    await fetch(`${this.apiUrl}/zones/${existingZone.id}`, { method: 'DELETE' });
                }
            }
            
            // Create or update zones
            for (let zone of this.zones) {
                const exists = existingZones.find(z => z.id === zone.id);
                
                if (exists) {
                    // Update
                    await fetch(`${this.apiUrl}/zones/${zone.id}`, {
                        method: 'PUT',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ zone })
                    });
                } else {
                    // Create
                    await fetch(`${this.apiUrl}/zones`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ zone })
                    });
                }
            }
            
            this.showMessage('Zones saved successfully!', 'success');
            
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
            const response = await fetch(`${this.apiUrl}/zones`);
            const data = await response.json();
            
            if (data.success) {
                this.zones = data.zones || [];
                this.redraw();
                this.updateZoneList();
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

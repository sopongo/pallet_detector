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
            
            // ✅ Enable CORS
            img.crossOrigin = "anonymous";
            
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
            
            // Check if source is a File or URL string
            if (source instanceof File) {
                const reader = new FileReader();
                reader.onload = (e) => {
                    img.src = e.target.result;
                };
                reader.onerror = reject;
                reader.readAsDataURL(source);
            } else if (typeof source === 'string') {
                // Assume URL or base64 data URL
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
        // ✅ Check max zones limit
        if (this.zones.length >= this.maxZones) {
            Swal.fire({
                icon: 'warning',
                title: 'Maximum Zones Reached',
                html: `
                    <p>You have reached the maximum of <strong>${this.maxZones} zones</strong>.</p>
                    <p>Please delete an existing zone or increase the maximum zones limit.</p>
                `,
                confirmButtonColor: '#ffc107'
            });
            return false;
        }
        
        // Generate new zone
        const nextId = this.zones.length > 0 ? Math.max(...this.zones.map(z => z.id)) + 1 : 1;
        
        this.currentZone = {
            id: nextId,
            name: `Zone_${nextId}`,
            polygon: [],
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
     *  * ✅ FIXED: Delete zone with confirmation
     */
    deleteZone(zoneId) {
        const zone = this.zones.find(z => z.id === zoneId);
        if (!zone) return;
        
        Swal.fire({
            title: 'Delete Zone?',
            text: `Are you sure you want to delete "${zone.name}"?`,
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#d33',
            confirmButtonText: 'Yes, delete it'
        }).then((result) => {
            if (result.isConfirmed) {
                this.zones = this.zones.filter(z => z.id !== zoneId);
                this.redraw();
                this.updateZoneList();
                this.showMessage('Zone deleted successfully', 'success');
            }
        });
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
     * ✅ FIXED: Update zone list UI with proper event listeners
     */
    updateZoneList() {
        const container = document.getElementById('zoneList');
        if (!container) return;
        
        container.innerHTML = '';
        
        if (this.zones.length === 0) {
            container.innerHTML = '<p class="text-muted">No zones configured yet.</p>';
            
            // Update badge
            const usedZonesEl = document.getElementById('usedZones');
            if (usedZonesEl) {
                usedZonesEl.textContent = `0/${this.maxZones} zones used`;
                usedZonesEl.className = 'badge badge-secondary';
            }
            return;
        }
        
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
                            <button class="btn btn-sm btn-info mb-1 btn-edit-zone" data-zone-id="${zone.id}">
                                <i class="fas fa-edit"></i> Edit
                            </button>
                            <button class="btn btn-sm btn-danger mb-1 btn-delete-zone" data-zone-id="${zone.id}">
                                <i class="fas fa-trash"></i> Delete
                            </button>
                            <button class="btn btn-sm btn-${zone.active ? 'warning' : 'success'} btn-toggle-zone" data-zone-id="${zone.id}">
                                <i class="fas fa-power-off"></i> ${zone.active ? 'Deactivate' : 'Activate'}
                            </button>
                        </div>
                    </div>
                </div>
            `;
            container.appendChild(card);
        });
        
        // ✅ Add event listeners to buttons (not inline onclick)
        container.querySelectorAll('.btn-edit-zone').forEach(btn => {
            btn.addEventListener('click', () => {
                const zoneId = parseInt(btn.getAttribute('data-zone-id'));
                this.editZone(zoneId);
            });
        });
        
        container.querySelectorAll('.btn-delete-zone').forEach(btn => {
            btn.addEventListener('click', () => {
                const zoneId = parseInt(btn.getAttribute('data-zone-id'));
                this.deleteZone(zoneId);
            });
        });
        
        container.querySelectorAll('.btn-toggle-zone').forEach(btn => {
            btn.addEventListener('click', () => {
                const zoneId = parseInt(btn.getAttribute('data-zone-id'));
                this.toggleZone(zoneId);
            });
        });
        
        // Update zone usage badge
        const usedZonesEl = document.getElementById('usedZones');
        if (usedZonesEl) {
            usedZonesEl.textContent = `${this.zones.length}/${this.maxZones} zones used`;
            
            // Change badge color based on usage
            if (this.zones.length === 0) {
                usedZonesEl.className = 'badge badge-secondary';
            } else if (this.zones.length >= this.maxZones) {
                usedZonesEl.className = 'badge badge-danger';
            } else if (this.zones.length >= this.maxZones * 0.8) {
                usedZonesEl.className = 'badge badge-warning';
            } else {
                usedZonesEl.className = 'badge badge-info';
            }
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
        
        const status = zone.active ? 'activated' : 'deactivated';
        this.showMessage(`Zone "${zone.name}" ${status}`, 'success');
    }
    
    /**
     * Save all zones to backend
     */
/**
 * ✅ COMPLETE: Save all zones to backend with full validation
 */
async saveZones() {
    try {
        // ✅ Validation 1-4 (unchanged)
        if (this.zones.length === 0) {
            this.showMessage('No zones to save. Please create at least one zone.', 'warning');
            return;
        }
        
        if (this.zones.length > this.maxZones) {
            Swal.fire({
                icon: 'error',
                title: 'Too Many Zones',
                html: `<p>You have <strong>${this.zones.length} zones</strong> but maximum is <strong>${this.maxZones}</strong>.</p>`,
                confirmButtonColor: '#dc3545'
            });
            return;
        }
        
        if (!this.referenceImage) {
            this.showMessage('Please capture an image first', 'warning');
            return;
        }
        
        for (let zone of this.zones) {
            if (zone.polygon.length < 3) {
                Swal.fire({
                    icon: 'error',
                    title: 'Invalid Zone',
                    html: `<p>Zone "<strong>${zone.name}</strong>" has only <strong>${zone.polygon.length} points</strong>.</p>`,
                    confirmButtonColor: '#dc3545'
                });
                return;
            }
        }
        
        // ✅ สำเนา zones ก่อนเคลียร์ (สำหรับแสดงใน table)
        const zonesToSave = JSON.parse(JSON.stringify(this.zones));
        
        // Show loading
        Swal.fire({
            title: 'Saving Zones...',
            html: 'Please wait while saving zones and images',
            allowOutsideClick: false,
            didOpen: () => { Swal.showLoading(); }
        });
        
        // Step 1: Save images
        console.log('📸 Step 1/3: Saving images...');
        
        const masterImageData = await this.getCanvasImageData(false);
        const polygonImageData = await this.getCanvasImageData(true);
        
        const imageResponse = await fetch(`${this.apiUrl}/zones/save-image`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                master_image: masterImageData,
                polygon_image: polygonImageData
            })
        });
        
        if (!imageResponse.ok) {
            throw new Error(`Image save failed: HTTP ${imageResponse.status}`);
        }
        
        const imageResult = await imageResponse.json();
        if (!imageResult.success) {
            throw new Error(`Failed to save images: ${imageResult.message}`);
        }
        
        console.log('✅ Images saved');
        
        // Step 2: Validate zones
        console.log('🔍 Step 2/3: Validating zones...');
        
        const validateResponse = await fetch(`${this.apiUrl}/zones/validate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ zones: this.zones })
        });
        
        if (!validateResponse.ok) {
            throw new Error(`Validation failed: HTTP ${validateResponse.status}`);
        }
        
        const validateResult = await validateResponse.json();
        
        // ✅ เพิ่ม detailed logging
        console.log('🔍 Validation response:', JSON.stringify(validateResult, null, 2));
        
        // เช็ค success ก่อน
        if (!validateResult.success) {
            throw new Error(validateResult.message || 'Validation failed');
        }
        
        // แล้วเช็ค valid
        if (validateResult.valid === false) {
            Swal.close();
            
            console.error('❌ Validation failed:', validateResult.message);
            
            Swal.fire({
                icon: 'error',
                title: 'Zone Overlap Detected',
                html: `
                    <p><strong>Validation Error:</strong></p>
                    <p>${validateResult.message}</p>
                    <hr>
                    <p><small>Please adjust your zones so they don't overlap.</small></p>
                `,
                confirmButtonColor: '#dc3545'
            });
            return;
        }
        
        console.log('✅ Zones validated (no overlaps)');
        
        // Step 3: Save zones config
        console.log('💾 Step 3/3: Saving zones configuration...');
        
        const saveResponse = await fetch(`${this.apiUrl}/zones/save`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ zones: this.zones })
        });
        
        if (!saveResponse.ok) {
            throw new Error(`Save failed: HTTP ${saveResponse.status}`);
        }
        
        const saveResult = await saveResponse.json();
        
        if (saveResult.success) {
            console.log('✅ Zones saved successfully');
            
            // เคลียร์ canvas
            this.zones = [];
            this.currentZone = null;
            this.referenceImage = null;
            
            const ctx = this.canvas.getContext('2d');
            ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
            ctx.fillStyle = '#f0f0f0';
            ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
            
            // ✅ แสดง Success alert แบบธรรมดา (ไม่มี table)
            Swal.fire({
                icon: 'success',
                title: 'Zones Saved Successfully!',
                text: `${saveResult.zones ? saveResult.zones.length : 'All'} zones saved to zones.json`,
                confirmButtonColor: '#28a745',
                timer: 2000
            });
            
            // ✅ รอ 1 วินาที แล้วอัพเดท table + รูป
            setTimeout(async () => {
                try {
                    await this.displaySavedZoneSummary();
                    console.log('✅ Table and image updated');
                } catch (error) {
                    console.error('❌ Update error:', error);
                }
            }, 1000);
            
        } else {
            throw new Error(saveResult.message || 'Save failed');
        }
        
    } catch (error) {
        console.error('❌ Save error:', error);
        Swal.close();
        Swal.fire({
            icon: 'error',
            title: 'Save Failed',
            html: `<p><strong>Error:</strong> ${error.message}</p>`,
            confirmButtonColor: '#dc3545'
        });
    }
}

    /**
     * Get canvas image as base64 data URL
     * @param {boolean} withZones - Include zone overlays or just master image
     */
    async getCanvasImageData(withZones) {
        try {
            // Create temporary canvas
            const tempCanvas = document.createElement('canvas');
            tempCanvas.width = this.canvas.width;
            tempCanvas.height = this.canvas.height;
            const tempCtx = tempCanvas.getContext('2d');
            
            // Draw reference image
            if (this.referenceImage) {
                tempCtx.drawImage(this.referenceImage, 0, 0, tempCanvas.width, tempCanvas.height);
            } else {
                throw new Error('No reference image loaded');
            }
            
            // Draw zones if requested
            if (withZones) {
                this.zones.forEach((zone, index) => {
                    this.drawZoneOnContext(tempCtx, zone, this.colors[index % this.colors.length]);
                });
            }
            
            // ✅ Try to convert to data URL
            try {
                const dataUrl = tempCanvas.toDataURL('image/jpeg', 0.9);
                console.log(`✅ Canvas exported (${withZones ? 'with' : 'without'} zones):`, dataUrl.substring(0, 50) + '...');
                return dataUrl;
            } catch (error) {
                console.error('❌ Canvas export error:', error);
                throw new Error('Canvas export failed: Image may be tainted. Please ensure CORS is enabled on the server.');
            }
            
        } catch (error) {
            console.error('❌ getCanvasImageData error:', error);
            throw error;
        }
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
     * ✅ NEW: Capture image from camera
     */
    async captureImageFromCamera() {
        try {
            // แสดง loading
            const loadingEl = document.getElementById('captureLoading');
            if (loadingEl) loadingEl.style.display = 'block';
            
            // เรียก API capture
            const response = await fetch(`${this.apiUrl}/zones/capture`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const result = await response.json();
            
            if (!result.success) {
                throw new Error(result.message || 'Capture failed');
            }
            
            // แปลง path → absolute URL
            const imagePath = result.image_path;
            const imageUrl = `http://localhost:5000/${imagePath}`;
            
            console.log('📷 Loading captured image:', imageUrl);
            
            // โหลดรูป
            await this.loadImageFromPath(imageUrl);
            
            Swal.fire({
                icon: 'success',
                title: 'Success!',
                text: 'Image captured successfully',
                timer: 2000
            });
            
            console.log('✅ Captured:', {
                path: imagePath,
                camera: result.camera_id,
                size: `${result.width}x${result.height}`
            });
            
        } catch (error) {
            console.error('❌ Capture error:', error);
            
            Swal.fire({
                icon: 'error',
                title: 'Camera Capture Failed',
                html: `
                    <p><strong>Error:</strong> ${error.message}</p>
                    <hr>
                    <p><strong>Solutions:</strong></p>
                    <ul style="text-align: left;">
                        <li>Stop camera stream in Camera tab first</li>
                        <li>Check camera connection</li>
                    </ul>
                `,
                confirmButtonColor: '#dc3545'
            });
            
        } finally {
            // ซ่อน loading
            const loadingEl = document.getElementById('captureLoading');
            if (loadingEl) loadingEl.style.display = 'none';
        }
    }

    /**
     * ✅ NEW: Load image from server path/URL
     */
    async loadImageFromPath(imagePath) {
        return new Promise((resolve, reject) => {
            const img = new Image();
            
            // ✅ CRITICAL: Enable CORS to prevent canvas tainting
            img.crossOrigin = "anonymous";
            
            img.onload = () => {
                this.referenceImage = img;
                
                // Resize canvas (max 1200px width)
                const maxWidth = 1200;
                const scale = Math.min(1, maxWidth / img.width);
                this.canvas.width = img.width * scale;
                this.canvas.height = img.height * scale;
                
                // Store original dimensions
                this.originalImageWidth = img.width;
                this.originalImageHeight = img.height;
                
                this.redraw();
                console.log('✅ Image loaded:', imagePath, `(${img.width}x${img.height})`);
                resolve();
            };
            
            img.onerror = (error) => {
                console.error('❌ Image load error:', error);
                reject(new Error(`Failed to load image: ${imagePath}`));
            };
            
            // Add cache buster + ensure full URL
            const fullUrl = imagePath.startsWith('http') 
                ? imagePath 
                : `${window.location.protocol}//${window.location.hostname}:5000/${imagePath}`;
            
            img.src = `${fullUrl}?t=${Date.now()}`;
            
            console.log('📷 Loading image from:', img.src);
        });
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
    
    /**
     * ✅ NEW: Create HTML table summarizing all zones
     */
    createZoneSummaryTable(zones) {
        if (!zones || zones.length === 0) {
            return '<p class="text-muted">No zones configured.</p>';
        }
        
        let html = `
            <div style="max-height: 400px; overflow-y: auto; text-align: left;">
                <table class="table table-sm table-bordered table-hover" style="font-size: 12px;">
                    <thead style="position: sticky; top: 0; background: #f8f9fa; z-index: 1;">
                        <tr>
                            <th style="width: 5%">#</th>
                            <th style="width: 20%">Zone Name</th>
                            <th style="width: 10%">Points</th>
                            <th style="width: 15%">Threshold</th>
                            <th style="width: 15%">Alert Time</th>
                            <th style="width: 15%">Type</th>
                            <th style="width: 10%">Status</th>
                            <th style="width: 10%">Color</th>
                        </tr>
                    </thead>
                    <tbody>
        `;
        
        zones.forEach((zone, index) => {
            const color = this.colors[index % this.colors.length];
            const palletType = zone.pallet_type === 1 ? '📦 Inbound' : '📤 Outbound';
            const status = zone.active 
                ? '<span class="badge badge-success">Active</span>' 
                : '<span class="badge badge-secondary">Inactive</span>';
            const alertTimeSec = (zone.alert_threshold / 1000).toFixed(1);
            
            html += `
                <tr>
                    <td><strong>${zone.id}</strong></td>
                    <td><strong>${zone.name}</strong></td>
                    <td>${zone.polygon.length} pts</td>
                    <td>${zone.threshold_percent}%</td>
                    <td>${alertTimeSec}s</td>
                    <td>${palletType}</td>
                    <td>${status}</td>
                    <td>
                        <div style="width: 30px; height: 20px; background: ${color}; border: 1px solid #333; display: inline-block; border-radius: 3px;"></div>
                    </td>
                </tr>
            `;
        });
        
        html += `
                    </tbody>
                </table>
            </div>
        `;
        
        return html;
    }
    
    /**
     * ✅ NEW: Update table-listzone with zone data
     */
    updateZoneSummaryTable(zones) {
        const tableBody = document.querySelector('#table-listzone tbody');
        const tableSection = document.getElementById('zoneSummarySection');
        
        if (!tableBody) {
            console.warn('⚠️ table-listzone not found');
            return;
        }
        
        // ถ้าไม่มี zones → ซ่อน table
        if (!zones || zones.length === 0) {
            tableSection.style.display = 'none';
            tableBody.innerHTML = '';
            return;
        }
        
        // แสดง table
        tableSection.style.display = 'block';
        
        // สร้าง rows
        let html = '';
        zones.forEach((zone, index) => {
            const color = this.colors[index % this.colors.length];
            const palletType = zone.pallet_type === 1 ? '📦 Inbound' : '📤 Outbound';
            const status = zone.active 
                ? '<span class="badge badge-success">Active</span>' 
                : '<span class="badge badge-secondary">Inactive</span>';
            const alertTimeSec = (zone.alert_threshold / 1000).toFixed(1);
            
            html += `
                <tr>
                    <td><strong>${zone.id}</strong></td>
                    <td><strong>${zone.name}</strong></td>
                    <td>${zone.polygon.length} pts</td>
                    <td>${zone.threshold_percent}%</td>
                    <td>${alertTimeSec}s</td>
                    <td>${palletType}</td>
                    <td>${status}</td>
                    <td>
                        <div style="width: 30px; height: 20px; background: ${color}; border: 1px solid #333; display: inline-block; border-radius: 3px;"></div>
                    </td>
                </tr>
            `;
        });
        
        tableBody.innerHTML = html;
        console.log(`✅ Updated table-listzone with ${zones.length} zones`);
    }
    
    /**
     * ✅ NEW: Display saved zone summary (polygon image + table)
     */
    async displaySavedZoneSummary() {
        try {
            console.log('📋 Loading saved zones...');
            
            // 1. Load zones from backend
            const zonesResponse = await fetch(`${this.apiUrl}/zones`);
            const zonesData = await zonesResponse.json();
            
            if (!zonesData.success || !zonesData.zones || zonesData.zones.length === 0) {
                console.log('⚠️ No saved zones found');
                
                // Show message that no data is available
                const imgEl = document.getElementById('currentReferenceImage');
                const noImgEl = document.getElementById('noReferenceImage');
                if (imgEl && noImgEl) {
                    imgEl.style.display = 'none';
                    noImgEl.style.display = 'block';
                }
                
                const zoneListContainer = document.getElementById('zoneList');
                if (zoneListContainer) {
                    zoneListContainer.innerHTML = '<p class="text-muted">No zones configured yet. Click "Capture Image" and "Add New Zone" to start.</p>';
                }
                
                return;
            }
            
            const savedZones = zonesData.zones;
            console.log(`✅ Found ${savedZones.length} saved zones`);
            
            // 2. Load polygon image
            const imgResponse = await fetch(`${this.apiUrl}/zones/latest-images`);
            const imgData = await imgResponse.json();
            
            const imgEl = document.getElementById('currentReferenceImage');
            const noImgEl = document.getElementById('noReferenceImage');
            
            if (imgEl && noImgEl && imgData.success && imgData.polygon_image) {
                const imageUrl = `/${imgData.polygon_image}?t=${Date.now()}`;
                imgEl.src = imageUrl;
                imgEl.style.display = 'block';
                noImgEl.style.display = 'none';
                console.log('✅ Polygon image loaded:', imageUrl);
            }
            
            // 3. Update table-listzone (แทน popup)
            this.updateZoneSummaryTable(savedZones);
            
            // 4. Update Configured Zones (canvas section)
            const zoneListContainer = document.getElementById('zoneList');
            if (zoneListContainer) {
                const zoneListHtml = this.createZoneSummaryTable(savedZones);
                zoneListContainer.innerHTML = `
                    <div class="alert alert-info">
                        <i class="fas fa-info-circle"></i> <strong>Saved Configuration:</strong> 
                        ${savedZones.length} zone(s) loaded from <code>config/zones.json</code>
                    </div>
                    ${zoneListHtml}
                `;
            }
            
            console.log(`✅ Displayed ${savedZones.length} saved zones in table`);
            
        } catch (error) {
            console.error('❌ Error displaying saved zones:', error);
        }
    }
}

// Global instance
let zoneManager;

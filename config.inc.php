
<!-- Default box -->
      <div class="card">
        <div class="card-header">
          <h3 class="card-title"><i class="fas fa-cogs"></i> System Configuration</h3>
        </div>
        <div class="card-body">
<!-- Main Content -->
        <section class="content">
            <div class="container-fluid">
                
                <!-- Tabs Card -->
                <div class="card card-secondary card-outline card-tabs">
                    <div class="card-header p-0 pt-1 border-bottom-0">
                        <ul class="nav nav-tabs" id="configTabs" role="tablist">
                            
                            <!-- Tab 1: General -->
                            <li class="nav-item">
                                <a class="nav-link active" id="general-tab" data-toggle="pill" href="#general" role="tab" aria-controls="general" aria-selected="true">
                                    <i class="fas fa-cog"></i> General
                                </a>
                            </li>
                            
                            <!-- Tab 2: Network -->
                            <li class="nav-item">
                                <a class="nav-link" id="network-tab" data-toggle="pill" href="#network" role="tab" aria-controls="network" aria-selected="false">
                                    <i class="fas fa-database"></i> Database
                                </a>
                            </li>
                            
                            <!-- Tab 3: Detection -->
                            <li class="nav-item">
                                <a class="nav-link" id="detection-tab" data-toggle="pill" href="#detection" role="tab" aria-controls="detection" aria-selected="false">
                                    <i class="fas fa-robot"></i> Detection
                                </a>
                            </li>
                            
                            <!-- Tab 4: System -->
                            <li class="nav-item">
                                <a class="nav-link" id="system-tab" data-toggle="pill" href="#system" role="tab" aria-controls="system" aria-selected="false">
                                    <i class="fas fa-server"></i> System
                                </a>
                            </li>
                            
                            <!-- Tab 5: Camera -->
                            <li class="nav-item">
                                <a class="nav-link" id="camera-tab" data-toggle="pill" href="#camera" role="tab" aria-controls="camera" aria-selected="false">
                                    <i class="fas fa-video"></i> Camera
                                </a>
                            </li>
                            
                            <!-- Tab 6: Light Signal -->
                            <li class="nav-item">
                                <a class="nav-link" id="light-tab" data-toggle="pill" href="#light" role="tab" aria-controls="light" aria-selected="false">
                                    <i class="fas fa-lightbulb"></i> Light Signal
                                </a>
                            </li>
                            
                        </ul>
                    </div>
                    
                    <div class="card-body">
                        <div class="tab-content" id="configTabsContent">
                            
                            <!-- ========================================
                                 TAB 1: GENERAL
                                 ======================================== -->
                            <div class="tab-pane fade show active" id="general" role="tabpanel" aria-labelledby="general-tab">
                                
                                <h4><i class="fas fa-lock"></i> Change Password</h4>
                                <hr>
                                <div class="row">
                                    <div class="col-md-6">
                                        <div class="form-group">
                                            <label for="currentPassword">Current Password</label>
                                            <input type="password" class="form-control" id="currentPassword" placeholder="Enter current password">
                                        </div>
                                        <div class="form-group">
                                            <label for="newPassword">New Password</label>
                                            <input type="password" class="form-control" id="newPassword" placeholder="Enter new password">
                                        </div>
                                        <div class="form-group">
                                            <label for="confirmPassword">Confirm Password</label>
                                            <input type="password" class="form-control" id="confirmPassword" placeholder="Confirm new password">
                                        </div>
                                        <button class="btn btn-primary">
                                            <i class="fas fa-save"></i> Change Password
                                        </button>
                                    </div>
                                </div>
                                
                                <br>
                                <h4><i class="fas fa-map-marker-alt"></i> Site & Location</h4>
                                <hr>
                                <div class="row">
                                    <div class="col-md-4">
                                        <div class="form-group">
                                            <label for="siteCompany">Site / Company</label>
                                            <div class="input-group">
                                                <!---<input type="text" class="form-control" id="siteCompany" value="">-->
                                                <select class="custom-select" id="siteCompany">
                                                    <option value="" selected>-- Select Site / Company --</option>
                                                    <?PHP
                                                    foreach($arr_site as $site_id => $site_info) {
                                                        echo '<option value="' . htmlspecialchars($site_id) . '">' . htmlspecialchars($site_info['site_name']) . '</option>';
                                                    }
                                                    ?>
                                                </select>   
                                            </div>
                                            <small class="form-text text-muted">Name of the site or company</small>
                                        </div>
                                    </div>

                                    <div class="col-md-4">
                                        <div class="form-group">
                                            <label for="siteLocation">Location</label>
                                            <div class="input-group">
                                                <!--<input type="text" class="form-control" id="siteLocation" value="">-->
                                                <select class="custom-select" id="siteLocation" disabled>
                                                    <option value="">-- Please select Site first --</option>
                                                </select>
                                            </div>
                                            <small class="form-text text-muted">Specific location within the site</small>
                                        </div>
                                    </div>
                                </div>
                                
                                <br>
                                <h4><i class="fas fa-folder"></i> Save Image Path</h4>
                                <hr>
                                <div class="row">
                                    <div class="col-md-8">
                                        <div class="form-group">
                                            <label for="imagePath">Image Storage Path</label>
                                            <div class="input-group"><input type="text" class="form-control" id="imagePath" value=""></div>
                                            <small class="form-text text-muted">Path where captured images will be saved</small>
                                        </div>
                                    </div>
                                </div>
                                
                                <br>
                                <h4><i class="fas fa-info-circle"></i> System Information</h4>
                                <hr>
                                <div class="row">
                                    <div class="col-md-6">
                                        <table class="table table-bordered">
                                            <tr>
                                                <td><strong>Version</strong></td>
                                                <td>1.0</td>
                                            </tr>
                                            <tr>
                                                <td><strong>Last Update</strong></td>
                                                <td>24-12-2025</td>
                                            </tr>
                                            <tr>
                                                <td><strong>Device</strong></td>
                                                <td>Raspberry Pi 5</td>
                                            </tr>
                                        </table>
                                    </div>
                                </div>
                                
                            </div>
                            
                            <!-- ========================================
                                 TAB 2: NETWORK
                                 ======================================== -->
                            <div class="tab-pane fade" id="network" role="tabpanel" aria-labelledby="network-tab">
                                
                                <!-- Database Config -->
                                <h4><i class="fas fa-database"></i> Database Configuration</h4>
                                <hr>
                                <div class="row">
                                    <div class="col-md-6">
                                        <div class="form-group">
                                            <label for="dbHost">Hostname / IP Address</label>
                                            <input type="text" class="form-control" id="dbHost" placeholder="localhost or 192.168.1.100">
                                        </div>
                                        <div class="form-group">
                                            <label for="dbUser">Username</label>
                                            <input type="text" class="form-control" id="dbUser" placeholder="root">
                                        </div>
                                        <div class="form-group">
                                            <label for="dbPass">Password</label>
                                            <input type="password" class="form-control" id="dbPass" placeholder="••••••••">
                                        </div>
                                        <div class="form-group">
                                            <label for="dbPort">Port (Optional)</label>
                                            <input type="number" class="form-control" id="dbPort" placeholder="3306">
                                        </div>
                                        <div class="form-group">
                                            <label for="dbName">Database Name</label>
                                            <input type="text" class="form-control" id="dbName" placeholder="pallet_db">
                                        </div>
                                        <button class="btn btn-info">
                                            <i class="fas fa-plug"></i> Test Connection
                                        </button>
                                    </div>
                                </div>
                                
                                <br>
                                <!-- LINE Notify Config -->
                                <h4><i class="fab fa-line"></i> LINE Notify Configuration</h4>
                                <hr>
                                <div class="row">
                                    <div class="col-md-6">
                                        <div class="form-group">
                                            <label for="lineToken">LINE Chatbot Token</label>
                                            <input type="text" class="form-control" id="lineToken" placeholder="Enter LINE Notify Token">
                                            <small class="form-text text-muted">Get token from <a href="https://notify-bot.line.me/" target="_blank">notify-bot.line.me</a></small>
                                        </div>
                                        <div class="form-group">
                                            <label for="lineGroup">Group ID (Optional)</label>
                                            <input type="text" class="form-control" id="lineGroup" placeholder="Enter Group ID">
                                        </div>
                                        <button class="btn btn-info">
                                            <i class="fas fa-paper-plane"></i> Test Send Message
                                        </button>
                                    </div>
                                </div>
                                
                            </div>
                            
                            <!-- ========================================
                                 TAB 3: DETECTION
                                 ======================================== -->
                            <div class="tab-pane fade" id="detection" role="tabpanel" aria-labelledby="detection-tab">
                                
                                <h4><i class="fas fa-brain"></i> YOLOv8 Model Configuration</h4>
                                <hr>
                                <div class="row">
                                    <div class="col-md-8">
                                        <div class="form-group">
                                            <label for="modelPath">Model Path</label>
                                            <div class="input-group">
                                                <input type="text" class="form-control" id="modelPath" value="runs/detect/pallet_v35/weights/best.pt">
                                            </div>
                                        </div>
                                        
                                        <div class="form-group">
                                            <label for="confThreshold">Confidence Threshold:  <span id="confValue">0.75</span></label>
                                            <input type="range" class="custom-range" id="confThreshold" min="0" max="1" step="0.01" value="0.75" oninput="document.getElementById('confValue').innerText = this.value">
                                            <small class="form-text text-muted">Minimum confidence for detection (0.0 - 1.0)</small>
                                        </div>
                                        
                                        <div class="form-group">
                                            <label for="iouThreshold">IoU Threshold: <span id="iouValue">0.45</span></label>
                                            <input type="range" class="custom-range" id="iouThreshold" min="0" max="1" step="0.01" value="0.45" oninput="document.getElementById('iouValue').innerText = this.value">
                                            <small class="form-text text-muted">Intersection over Union threshold (0.0 - 1.0)</small>
                                        </div>
                                        
                                        <div class="form-group">
                                            <label for="imageSize">Image Size (Width)</label>
                                            <select class="custom-select" id="imageSize">
                                                <option value="640">640px</option>
                                                <option value="1280" selected>1280px</option>
                                                <option value="1920">1920px</option>
                                            </select>
                                            <small class="form-text text-muted">Input image size for model inference</small>
                                        </div>
                                        
                                        <div class="form-group">
                                            <label>Device Mode</label><br>
                                            <div class="custom-control custom-radio custom-control-inline">
                                                <input type="radio" id="deviceCPU" name="deviceMode" class="custom-control-input" value="cpu" checked>
                                                <label class="custom-control-label" for="deviceCPU">
                                                    <i class="fas fa-microchip"></i> CPU Mode
                                                </label>
                                            </div>
                                            <div class="custom-control custom-radio custom-control-inline">
                                                <input type="radio" id="deviceGPU" name="deviceMode" class="custom-control-input" value="gpu">
                                                <label class="custom-control-label" for="deviceGPU">
                                                    <i class="fas fa-memory"></i> GPU Mode
                                                </label>
                                            </div>
                                        </div>
                                        
                                        <div class="form-group">
                                            <label for="captureInterval">Interval Take Photo (Seconds)</label>
                                            <input type="number" class="form-control" id="captureInterval" value="600" min="1">
                                            <small class="form-text text-muted">Time between automatic captures (600s = 10 minutes)</small>
                                        </div>
                                        
                                        <div class="form-group">
                                            <label for="alertThreshold">Alert Threshold (Minutes)</label>
                                            <select class="custom-select" id="alertThreshold">
                                                <option value="15">15 minutes</option>
                                                <option value="30" selected>30 minutes</option>
                                                <option value="45">45 minutes</option>
                                                <option value="60">60 minutes</option>
                                            </select>
                                            <small class="form-text text-muted">Send alert when pallet stays longer than this duration</small>
                                        </div>

                                        <!-- Time Range Slider -->
                                        <div class="form-group">
                                            <label><i class="fas fa-clock"></i> System Operating Hours</label>
                                            <div class="mx-3 mt-4 mb-4">
                                                <input id="timeRangeSlider" type="text" name="time_range" value="">
                                            </div>
                                            <small id="timeRangeDisplay" class="form-text text-muted">
                                                System will operate from: <b class="text-primary">08:00 to 17:00</b>
                                            </small>
                                        </div>

                                        <!---<button class="btn btn-info">
                                            <i class="fas fa-check-circle"></i> Test Model
                                        </button>--->
                                    </div>
                                </div>
                                
                            </div>
                            
                            <!-- ========================================
                                 TAB 4: SYSTEM
                                 ======================================== -->
                            <div class="tab-pane fade" id="system" role="tabpanel" aria-labelledby="system-tab">
                                <h4><i class="fas fa-hdd"></i> Storage Information</h4>
                                    <hr>
                                    <div class="row">
                                        <div class="col-md-6">
                                            <div class="card">
                                                <div class="card-body">
                                                    <h5>Storage Usage</h5>
                                                    <p><strong>Used: </strong> 0 MB</p>
                                                    <p><strong>Total Files:</strong> 0</p>
                                                    <p><strong>Path:</strong> <code>-</code></p>
                                                    <div class="progress">
                                                        <div class="progress-bar bg-info" role="progressbar" 
                                                            style="width: 0%" 
                                                            aria-valuenow="0" 
                                                            aria-valuemin="0" 
                                                            aria-valuemax="100">0%</div>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                
                                
                                <br>
                                <h4><i class="fas fa-tools"></i> System Actions</h4>
                                <hr>
                                <div class="row">
                                    <div class="col-md-6">
                                        <button class="btn btn-warning btn-block btn-clear-old-images">
                                            <i class="fas fa-trash-alt"></i> Clear Old Images (>7 days)
                                        </button>
                                        <button class="btn btn-danger btn-block">
                                            <i class="fas fa-sync-alt"></i> Restart Detection Service
                                        </button>
                                        <button class="btn btn-secondary btn-block">
                                            <i class="fas fa-file-alt"></i> View System Logs
                                        </button>
                                    </div>
                                </div>
                                
                            </div>
                            
                            <!-- ========================================
                                 TAB 5: CAMERA
                                 ======================================== -->
                            <div class="tab-pane fade" id="camera" role="tabpanel" aria-labelledby="camera-tab">
                                
                                <h4><i class="fas fa-video"></i> Camera Configuration</h4>
                                <hr>
                                <div class="row">
                                    <div class="col-md-6">
                                        <div class="form-group">
                                            <label for="cameraSelect">Select Camera</label>
                                            <select class="custom-select" id="cameraSelect">
                                                <option value="" disabled selected>-- Select Camera --</option>
                                            </select>
                                        </div>

                                        
                                        
                                        <div class="form-group">
                                            <button class="btn btn-info">
                                                <i class="fas fa-search"></i> Auto Detect Cameras
                                            </button>
                                            <button class="btn btn-success ml-2">
                                                <i class="fas fa-camera"></i> Test Capture
                                            </button>
                                        </div>
                                    </div>
                                </div>

<div class="card">
    <div class="card-header">
        <h5><i class="fas fa-eye"></i> Live Camera Preview</h5>
    </div>
    <div class="card-body text-center">
        <!-- ✅ เพิ่ม id="cameraFeed" -->
        <img id="cameraFeed" 
             src="" 
             alt="Camera Feed" 
             style="width: 100%; max-width:  640px; height: 480px; background: #000; border:  2px solid #ddd; border-radius: 8px; object-fit: contain;">
        
        <p id="cameraStatus" class="text-muted mt-2">
            Select a camera to start streaming
        </p>
        
        <!-- ✅ เพิ่มปุ่ม Stop Stream -->
        <button class="btn btn-danger btn-sm mt-2" id="btnStopStream" style="display: none;">
            <i class="fas fa-stop"></i> Stop Stream
        </button>
    </div>
</div>

                                
                            </div>
                            
                            <!-- ========================================
                                 TAB 6: LIGHT SIGNAL
                                 ======================================== -->
                            <div class="tab-pane fade" id="light" role="tabpanel" aria-labelledby="light-tab">
                                
                                <h4><i class="fas fa-lightbulb"></i> GPIO Light Signal Configuration</h4>
                                <hr>
                                
                                <!-- Red Light -->
                                <div class="row mb-4">
                                    <div class="col-md-6">
                                        <div class="card">
                                            <div class="card-body">
                                                <h5><i class="fas fa-circle text-danger"></i> Red Light</h5>
                                                <p><strong>GPIO Pin:</strong> 17</p>
                                                <p><strong>Status:</strong> <span class="badge badge-secondary">OFF</span></p>
                                                <button class="btn btn-danger">
                                                    <i class="fas fa-power-off"></i> Test ON
                                                </button>
                                                <button class="btn btn-outline-secondary ml-2">
                                                    <i class="fas fa-times"></i> Turn OFF
                                                </button>
                                            </div>
                                        </div>
                                    </div>
                                    <div class="col-md-6 text-center">
                                        <div class="light-indicator light-off" id="redLight"></div>
                                    </div>
                                </div>
                                
                                <!-- Green Light -->
                                <div class="row mb-4">
                                    <div class="col-md-6">
                                        <div class="card">
                                            <div class="card-body">
                                                <h5><i class="fas fa-circle text-success"></i> Green Light</h5>
                                                <p><strong>GPIO Pin:</strong> 27</p>
                                                <p><strong>Status:</strong> <span class="badge badge-secondary">OFF</span></p>
                                                <button class="btn btn-success">
                                                    <i class="fas fa-power-off"></i> Test ON
                                                </button>
                                                <button class="btn btn-outline-secondary ml-2">
                                                    <i class="fas fa-times"></i> Turn OFF
                                                </button>
                                            </div>
                                        </div>
                                    </div>
                                    <div class="col-md-6 text-center">
                                        <div class="light-indicator light-off" id="greenLight"></div>
                                    </div>
                                </div>
                                
                                <div class="alert alert-info">
                                    <i class="fas fa-info-circle"></i> <strong>Note:</strong> Light signals are used to indicate system status. Red = Alert/Error, Green = Normal Operation.
                                </div>
                                
                            </div>
                            
                        </div>
                    </div>
                    
                    <!-- Card Footer:  Save Button -->
                    <div class="card-footer">
                        <button class="btn btn-success btn-lg" id="btnSaveConfig"><i class="fas fa-save"></i> Save All Changes</button>
                        <button class="btn btn-secondary btn-lg ml-2"><i class="fas fa-undo"></i> Reset to Default</button>
                    </div>
                </div>
                
            </div>
        </section>
        </div><!-- /.card-body -->

      </div>
      <!-- /.card -->


<!-- SweetAlert2 CDN -->
<script src="https://cdn.jsdelivr.net/npm/sweetalert2@11"></script>

<!-- Custom Script -->
<script>
$(document).ready(function() {
    // สร้าง Time Range Slider
    var slider = $("#timeRangeSlider").ionRangeSlider({
        type: "double",
        min: 0,
        max:  1440,
        from: 480,   // 08:00
        to: 1020,    // 17:00
        step: 30,
        grid: true,
        grid_num: 12,
        prettify: function(num) {
            return minutesToTime(num);
        },
        onStart: function(data) {
            updateTimeDisplay(data.from, data.to);
        },
        onChange: function(data) {
            updateTimeDisplay(data.from, data. to);
        }
    });

    // เก็บ instance ไว้ใช้ global
    window.timeRangeSliderInstance = slider. data("ionRangeSlider");
}); //document.ready

// แปลงนาทีเป็น HH:mm
function minutesToTime(totalMinutes) {
    var hours = Math.floor(totalMinutes / 60);
    var minutes = totalMinutes % 60;
    return hours. toString().padStart(2, '0') + ":" + minutes.toString().padStart(2, '0');
}

// แปลง HH:mm เป็นนาที
function timeToMinutes(timeStr) {
    var parts = timeStr.split(':');
    return parseInt(parts[0]) * 60 + parseInt(parts[1]);
}

// อัพเดทข้อความแสดงผล
function updateTimeDisplay(from, to) {
    $('#timeRangeDisplay b').text(minutesToTime(from) + " to " + minutesToTime(to));
}



// ========================================
// API Base URL
// ========================================
const API_URL = 'http://localhost:5000/api';

// ========================================
// SweetAlert2 Helper Functions
// ========================================
function showSuccess(message) {
    Swal.fire({
        icon: 'success',
        title: 'Success!',
        text: message,
        confirmButtonColor: '#28a745'
    });
}

function showError(message) {
    Swal.fire({
        icon: 'error',
        title: 'Error! ',
        text: message,
        confirmButtonColor: '#dc3545'
    });
}

function showLoading(message = 'Processing...') {
    Swal.fire({
        title: message,
        allowOutsideClick: false,
        didOpen: () => {
            Swal.showLoading();
        }
    });
}

// ========================================
// 1. Load Config เมื่อเปิดหน้า
// ========================================
window.addEventListener('DOMContentLoaded', function() {
    loadConfig();
});

// ========================================
// Dynamic Location Dropdown
// ========================================

// Event:  เมื่อเปลี่ยน Site
document.getElementById('siteCompany').addEventListener('change', function() {
    const siteId = this.value;
    const locationSelect = document.getElementById('siteLocation');
    
    // Reset location dropdown
    locationSelect.innerHTML = '<option value="">-- Loading...  --</option>';
    locationSelect.disabled = true;
    
    if(! siteId || siteId === '') {
        // ถ้าไม่เลือก Site
        locationSelect.innerHTML = '<option value="">-- Please select Site first --</option>';
        locationSelect.disabled = true;
        return;
    }
    
    // ดึง locations จาก API
    fetch(`${API_URL}/config/locations?site_id=${siteId}`)
        .then(r => r.json())
        .then(data => {
            if(data.success && data.locations) {
                // สร้าง options
                let html = '<option value="">-- Select Location --</option>';
                
                Object.keys(data.locations).forEach(locId => {
                    html += `<option value="${locId}">${data.locations[locId]}</option>`;
                });
                
                locationSelect.innerHTML = html;
                locationSelect. disabled = false;
                
                console.log(`✅ Loaded ${Object.keys(data.locations).length} locations for Site ${siteId}`);
            } else {
                locationSelect.innerHTML = '<option value="">No locations available</option>';
                locationSelect. disabled = true;
                showError('Failed to load locations');
            }
        })
        .catch(err => {
            console.error('❌ Load locations error:', err);
            locationSelect. innerHTML = '<option value="">Error loading locations</option>';
            locationSelect.disabled = true;
            showError('Failed to load locations:  ' + err.message);
        });
});

// Validation: ตรวจสอบก่อน Save
document.getElementById('btnSaveConfig').addEventListener('click', function(e) {
    const siteId = document.getElementById('siteCompany').value;
    const locationId = document.getElementById('siteLocation').value;
    
    // ถ้าเลือก Site แต่ไม่เลือก Location
    if(siteId && siteId !== '' && (! locationId || locationId === '')) {
        e.preventDefault(); // หยุดการ save
        e.stopImmediatePropagation();
        
        Swal.fire({
            icon: 'warning',
            title: 'Please Select Location',
            text: 'You must select a location for the selected site',
            confirmButtonColor: '#ffc107'
        });
        
        return false;
    }
    
    // ถ้าไม่เลือกทั้ง Site และ Location
    if((! siteId || siteId === '') && (!locationId || locationId === '')) {
        e.preventDefault();
        e.stopImmediatePropagation();
        
        Swal.fire({
            icon: 'warning',
            title: 'Please Select Site & Location',
            text: 'Please select both site and location before saving',
            confirmButtonColor:  '#ffc107'
        });
        
        return false;
    }
}, true); // ใช้ capture phase

// Load locations เมื่อ load config (สำหรับ edit)
function loadLocationForSite(siteId, selectedLocationId = null) {
    if(!siteId) return;
    
    const locationSelect = document.getElementById('siteLocation');
    locationSelect. innerHTML = '<option value="">-- Loading... --</option>';
    locationSelect.disabled = true;
    
    fetch(`${API_URL}/config/locations?site_id=${siteId}`)
        .then(r => r.json())
        .then(data => {
            if(data.success && data.locations) {
                let html = '<option value="">-- Select Location --</option>';
                
                Object.keys(data. locations).forEach(locId => {
                    const selected = (locId == selectedLocationId) ? 'selected' : '';
                    html += `<option value="${locId}" ${selected}>${data.locations[locId]}</option>`;
                });
                
                locationSelect.innerHTML = html;
                locationSelect.disabled = false;
            }
        });
}

// แก้ไข loadConfig() เพื่อโหลด Location ด้วย
const originalLoadConfig = loadConfig;
loadConfig = function() {
    originalLoadConfig();
    
    // รอ config โหลดเสร็จแล้วโหลด locations
    setTimeout(function() {
        const siteId = document.getElementById('siteCompany').value;
        const locationId = document.getElementById('siteLocation').value;
        
        if(siteId && siteId !== '') {
            loadLocationForSite(siteId, locationId);
        }
    }, 500);
};

function loadConfig() {
    fetch(`${API_URL}/config`)
        .then(r => r.json())
        .then(data => {
            // General
            if(document.getElementById('imagePath')) {
                document.getElementById('imagePath').value = data.general.imagePath;
            }
            if(document.getElementById('siteCompany')) {
                //alert('Site / Company: ' + data.general.siteCompany);
                document.getElementById('siteCompany').value = data.general.siteCompany || '';
            }
            if(document.getElementById('siteLocation')) {
                document.getElementById('siteLocation').value = data.general.siteLocation || '';
            }
            
            // Network - Database
            if(document.getElementById('dbHost')) {
                document.getElementById('dbHost').value = data.network.database.host;
                document.getElementById('dbUser').value = data.network.database.user;
                document.getElementById('dbPass').value = data.network.database.password;
                document.getElementById('dbPort').value = data.network.database.port;
                document.getElementById('dbName').value = data.network.database.database;
            }
                        
            // Network - LINE
            if(document.getElementById('lineToken')) {
                document. getElementById('lineToken').value = data.network.lineNotify.token;
                document.getElementById('lineGroup').value = data.network.lineNotify.groupId;
            }
            
            // Detection
            if(document.getElementById('modelPath')) {
                document.getElementById('modelPath').value = data.detection.modelPath;
                document.getElementById('confThreshold').value = data.detection. confidenceThreshold;
                document.getElementById('confValue').innerText = data.detection.confidenceThreshold;
                document.getElementById('iouThreshold').value = data.detection.iouThreshold;
                document.getElementById('iouValue').innerText = data.detection. iouThreshold;
                document.getElementById('imageSize').value = data.detection. imageSize;
                document.getElementById('captureInterval').value = data.detection.captureInterval;
                document.getElementById('alertThreshold').value = data.detection. alertThreshold;
                // Device Mode
                if(data.detection. deviceMode === 'gpu') {
                    document.getElementById('deviceGPU').checked = true;
                } else {
                    document.getElementById('deviceCPU').checked = true;
                }
                // Operating Hours (ใหม่)
                if(data.detection.operatingHours && window.timeRangeSliderInstance) {
                    window.timeRangeSliderInstance.update({
                        from: timeToMinutes(data.detection. operatingHours.start),
                        to: timeToMinutes(data.detection.operatingHours.end)
                    });
                }                
            }
            
            // Camera
            if(document.getElementById('cameraSelect')) {
                document.getElementById('cameraSelect').value = data.camera.selectedCamera;
            }
            
            console.log('✅ Config loaded');
        })
        .catch(err => {
            console.error('❌ Load config error:', err);
            showError('Failed to load configuration');
        });
}


// Save Config โดยอ้างอิง id btnSaveConfig แทนการใช้ class
document.getElementById('btnSaveConfig').addEventListener('click', function() {
    const config = {
        general: {
            imagePath: document.getElementById('imagePath').value,
            version: "1.0",
            lastUpdate: new Date().toISOString().split('T')[0],
            device: "Raspberry Pi 5",
            siteCompany: document.getElementById('siteCompany').value,
            siteLocation: document.getElementById('siteLocation').value 
        },
        network: {
            database: {
                host: document. getElementById('dbHost').value,
                user: document.getElementById('dbUser').value,
                password: document.getElementById('dbPass').value,
                port: parseInt(document.getElementById('dbPort').value) || 3306,
                database: document.getElementById('dbName').value
            },
            lineNotify: {
                token: document. getElementById('lineToken').value,
                groupId: document.getElementById('lineGroup').value
            }
        },
        detection: {
            modelPath: document.getElementById('modelPath').value,
            confidenceThreshold: parseFloat(document. getElementById('confThreshold').value),
            iouThreshold: parseFloat(document.getElementById('iouThreshold').value),
            imageSize: parseInt(document.getElementById('imageSize').value),
            deviceMode: document.querySelector('input[name="deviceMode"]:checked').value,
            captureInterval: parseInt(document.getElementById('captureInterval').value),
            alertThreshold: parseInt(document.getElementById('alertThreshold').value),
            operatingHours: {
                start: minutesToTime(window.timeRangeSliderInstance.result.from),
                end: minutesToTime(window.timeRangeSliderInstance.result.to)
            } 
        },
        camera: {
            selectedCamera: document.getElementById('cameraSelect').value,
            resolution: { width: 1280, height: 720 }
        },
        gpio: { redLightPin: 17, greenLightPin: 27 },
        system: { storageUsedMB: 0, totalFiles: 0, autoCleanupDays: 7 }
    };
    
    showLoading('Saving.. .');
    fetch(`${API_URL}/config`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON. stringify(config)
    })
    .then(r => r. json())
    .then(data => {
        Swal. close();
        data.success ? showSuccess(data. message) : showError(data.message);
    });
});


// ========================================
// 2. Save All Changes (แก้ selector)
// ========================================

document.addEventListener('DOMContentLoaded', function() {
    // หาปุ่ม Save All Changes
    const saveButton = document.querySelector('.card-footer .btn-success .btn-lg');
    
    if(saveButton) {
        saveButton.addEventListener('click', function() {
            const config = {
                general: {
                    imagePath: document.getElementById('imagePath')?.value || '',
                    version: "1.0",
                    lastUpdate: new Date().toISOString().split('T')[0],
                    device: "Raspberry Pi 5",
                    siteCompany: document.getElementById('siteCompany')?.value || '',
                    siteLocation: document.getElementById('siteLocation')?.value || ''
                },
                network: {
                    database: {
                        host: document.getElementById('dbHost')?.value || '',
                        user: document.getElementById('dbUser')?.value || '',
                        password: document.getElementById('dbPass')?.value || '',
                        port: parseInt(document.getElementById('dbPort')?.value) || 3306,
                        database: document.getElementById('dbName')?.value || ''
                    },
                    wifi: {
                        ssid: document.getElementById('wifiSSID')?.value || '',
                        username: document.getElementById('wifiUser')?.value || '',
                        password: document.getElementById('wifiPass')?.value || ''
                    },
                    lineNotify: {
                        token: document.getElementById('lineToken')?.value || '',
                        groupId: document.getElementById('lineGroup')?.value || ''
                    }
                },
                detection: {
                    modelPath:  document.getElementById('modelPath')?.value || '',
                    confidenceThreshold: parseFloat(document. getElementById('confThreshold')?.value) || 0.75,
                    iouThreshold: parseFloat(document.getElementById('iouThreshold')?.value) || 0.45,
                    imageSize: parseInt(document.getElementById('imageSize')?.value) || 1280,
                    deviceMode: document.querySelector('input[name="deviceMode"]:checked')?.value || 'cpu',
                    captureInterval: parseInt(document.getElementById('captureInterval')?.value) || 600,
                    alertThreshold:  parseInt(document.getElementById('alertThreshold')?.value) || 30,
                    operatingHours: {
                        start: minutesToTime(window.timeRangeSliderInstance.result.from),
                        end: minutesToTime(window.timeRangeSliderInstance.result.to)
                    }
                },
                camera: {
                    selectedCamera: document. getElementById('cameraSelect')?.value || '0',
                    resolution: {
                        width: 1280,
                        height:  720
                    }
                },
                gpio: {
                    redLightPin: 17,
                    greenLightPin: 27
                },
                system: {
                    storageUsedMB: 0,
                    totalFiles: 0,
                    autoCleanupDays: 7
                }
            };
            
            showLoading('Saving configuration...');
            
            fetch(`${API_URL}/config`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON. stringify(config)
            })
            .then(r => r. json())
            .then(data => {
                Swal.close();
                if(data.success) {
                    showSuccess(data.message);
                    loadConfig();
                } else {
                    showError(data.message);
                }
            })
            .catch(err => {
                Swal.close();
                showError('Save failed:  ' + err.message);
            });
        });
    }
});

// ========================================
// 3. Test Database Connection
// ========================================
document. addEventListener('DOMContentLoaded', function() {
    // หาปุ่ม Test Connection ใน Database section
    const dbTestBtn = document.querySelector('#network .btn-info');
    
    if(dbTestBtn && dbTestBtn.textContent.includes('Test Connection')) {
        dbTestBtn.addEventListener('click', function() {
            const data = {
                host: document.getElementById('dbHost').value,
                user: document. getElementById('dbUser').value,
                password: document.getElementById('dbPass').value,
                database: document.getElementById('dbName').value,
                port: document.getElementById('dbPort').value || 3306
            };
            
            showLoading('Testing database connection...');
            
            fetch(`${API_URL}/test/database`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(data)
            })
            .then(r => r.json())
            .then(result => {
                Swal. close();
                if(result. success) {
                    showSuccess(result.message);
                } else {
                    showError(result.message);
                }
            })
            .catch(err => {
                Swal. close();
                showError('Connection test failed: ' + err.message);
            });
        });
    }
});

// ========================================
// 4. Test WiFi
// ========================================
document.addEventListener('DOMContentLoaded', function() {
    
});

// ========================================
// 4. Clean Up Old Images
// ========================================
document.querySelector('.btn-clear-old-images').addEventListener('click', function() {
    Swal.fire({
        title: 'Delete old images?',
        text: 'Files older than 7 days will be deleted',
        icon: 'warning',
        showCancelButton: true,
        confirmButtonText: 'Yes, delete'
    }).then(result => {
        if(result.isConfirmed) {
            showLoading('Cleaning up.. .');
            fetch(`${API_URL}/system/cleanup`, {method: 'POST'})
                .then(r => r.json())
                .then(data => {
                    Swal.close();
                    if(data.success) {
                        showSuccess(data.message);
                        loadStorageInfo();
                    } else {
                        showError(data.message);
                    }
                });
        }
    });
});


// ========================================
// 4. Load Storage Info
// ========================================
function loadStorageInfo() {
    fetch(`${API_URL}/system/storage`)
        .then(r => r.json())
        .then(result => {
            if(result.success) {
                const data = result.data;
                
                // อัพเดทข้อมูลใน UI
                const storageCard = document.querySelector('#system .card-body');
                if(storageCard) {
                    // Used MB
                    const usedElem = storageCard.querySelector('p:nth-of-type(1) strong');
                    if(usedElem && usedElem.nextSibling) {
                        usedElem.nextSibling.textContent = ` ${data.usedMB} MB`;
                    }
                    
                    // Total Files
                    const filesElem = storageCard.querySelector('p:nth-of-type(2) strong');
                    if(filesElem && filesElem.nextSibling) {
                        filesElem.nextSibling.textContent = ` ${data.totalFiles}`;
                    }
                    
                    // Path
                    const pathElem = storageCard.querySelector('p:nth-of-type(3) code');
                    if(pathElem) {
                        pathElem. textContent = data.path;
                    }
                    
                    // Progress Bar
                    const progressBar = storageCard.querySelector('.progress-bar');
                    if(progressBar) {
                        const percent = (data.usedMB / (data.totalDiskGB * 1024)) * 100;
                        progressBar. style.width = Math.min(percent, 100) + '%';
                        progressBar.setAttribute('aria-valuenow', Math.round(percent));
                        progressBar.textContent = Math.round(percent) + '%';
                    }
                }
                
                console.log('✅ Storage info loaded:', data);
            } else {
                console.error('❌ Storage error:', result.message);
            }
        })
        .catch(err => {
            console.error('❌ Fetch storage error:', err);
        });
}

// เรียกทุกครั้งที่เปิด System tab
document.getElementById('system-tab').addEventListener('shown.bs.tab', function() {
    loadStorageInfo();
});

// เรียกตอน load หน้า
window.addEventListener('DOMContentLoaded', function() {
    loadStorageInfo();
});

// Refresh ทุก 30 วินาที (ถ้าอยู่ที่ System tab)
setInterval(function() {
    if(document.getElementById('system').classList.contains('active')) {
        loadStorageInfo();
    }
}, 30000);



// ========================================
// 5. Test LINE Notify
// ========================================
document.addEventListener('DOMContentLoaded', function() {
    const lineSection = document.querySelector('#network');
    if(lineSection) {
        const lineTestBtn = Array.from(lineSection.querySelectorAll('.btn-info')).find(btn => 
            btn.textContent.includes('Test Send')
        );
        
        if(lineTestBtn) {
            lineTestBtn.addEventListener('click', function() {
                const token = document.getElementById('lineToken').value;
                if(!token) {
                    showError('Please enter LINE Notify Token first');
                    return;
                }
                showSuccess('LINE Notify test will be implemented soon');
            });
        }
    }
});

// ========================================
// 6. Test Camera
// ========================================
document.addEventListener('DOMContentLoaded', function() {
    const cameraTab = document.querySelector('#camera');
    if(cameraTab) {
        const testCaptureBtn = Array.from(cameraTab.querySelectorAll('.btn-success')).find(btn => 
            btn.textContent.includes('Test Capture')
        );
        
        if(testCaptureBtn) {
            testCaptureBtn.addEventListener('click', function() {
                const camera = document.getElementById('cameraSelect').value;
                if(!camera) {
                    showError('Please select a camera first');
                    return;
                }
                
                showLoading('Testing camera.. .');
                
                fetch(`${API_URL}/test/camera`, {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({camera: camera})
                })
                .then(r => r.json())
                .then(result => {
                    Swal.close();
                    if(result.success) {
                        showSuccess(result. message + (result.details ? `\n\nResolution: ${result.details.resolution}` : ''));
                    } else {
                        showError(result.message);
                    }
                });
            });
        }
    }
});

// ========================================
// 7. Auto Detect Cameras
// ========================================
document.addEventListener('DOMContentLoaded', function() {
    const cameraTab = document.querySelector('#camera');
    if(cameraTab) {
        const autoDetectBtn = Array.from(cameraTab. querySelectorAll('.btn-info')).find(btn => 
            btn.textContent.includes('Auto Detect')
        );
        
        if(autoDetectBtn) {
            autoDetectBtn.addEventListener('click', function() {
                showLoading('Detecting cameras...');
                
                fetch(`${API_URL}/camera/detect`)
                    .then(r => r.json())
                    . then(data => {
                        Swal.close();
                        const select = document.getElementById('cameraSelect');
                        select.innerHTML = '<option value="">-- Select Camera --</option>';
                        
                        if(data. cameras && data.cameras.length > 0) {
                            data.cameras.forEach(cam => {
                                select.innerHTML += `<option value="${cam}">USB Camera ${cam}</option>`;
                            });
                            showSuccess(`Found ${data.cameras.length} camera(s)`);
                        } else {
                            showError('No cameras detected');
                        }
                    })
                    . catch(err => {
                        Swal.close();
                        showError('Detection failed: ' + err.message);
                    });
            });
        }
    }
});

// ========================================
// Live Camera Preview Update 05-01-2025
// ========================================
document.getElementById('cameraSelect').addEventListener('change', function() {
    const camera = this.value;
    const feedImg = document.getElementById('cameraFeed');
    const status = document.getElementById('cameraStatus');
    
    if(camera && camera !== '') {
        // ✅ หยุด stream เก่าก่อน
        feedImg. src = '';
        
        // รอ 500ms แล้วเริ่ม stream ใหม่
        setTimeout(function() {
            feedImg.src = `${API_URL}/camera/stream/${camera}`;
            feedImg.onerror = function() {
                status.innerHTML = `<br />❌ Cannot stream from Camera ${camera}`;
                status.className = 'text-danger';
            };
            feedImg.onload = function() {
                status.innerHTML = `<br />✅ Streaming from Camera ${camera}`;
                status.className = 'text-success';
            };
        }, 500);
    } else {
        feedImg.src = '';
        status.textContent = 'No camera selected';
        status.className = 'text-muted';
    }
});

// Stop Stream Button
document.getElementById('btnStopStream').addEventListener('click', function() {
    const feedImg = document.getElementById('cameraFeed');
    const status = document.getElementById('cameraStatus');
    
    feedImg.src = '';
    status.textContent = 'Stream stopped';
    status.className = 'text-warning';
    this.style.display = 'none';
});

// แสดงปุ่ม Stop เมื่อ stream เริ่ม
document.getElementById('cameraFeed').addEventListener('load', function() {
    document.getElementById('btnStopStream').style.display = 'inline-block';
});


// ========================================
// 8. GPIO Test Buttons
// ========================================
document.addEventListener('DOMContentLoaded', function() {
    const lightTab = document.querySelector('#light');
    if(lightTab) {
        // Red Light ON
        const redOnBtn = Array.from(lightTab.querySelectorAll('.btn-danger')).find(btn => 
            btn.textContent.includes('Test ON') && btn.closest('.card-body').textContent.includes('Red')
        );
        if(redOnBtn) {
            redOnBtn.addEventListener('click', function() {
                fetch(`${API_URL}/gpio/red/on`, {method: 'POST'})
                    .then(r => r.json())
                    .then(data => {
                        if(data.success) {
                            document.getElementById('redLight').className = 'light-indicator light-red';
                            showSuccess(data.message);
                        } else {
                            showError(data.message);
                        }
                    });
            });
        }
        
        // Red Light OFF
        const redOffBtn = Array.from(lightTab. querySelectorAll('.btn-outline-secondary')).find(btn => 
            btn.textContent.includes('Turn OFF') && btn.closest('.card-body').textContent.includes('Red')
        );
        if(redOffBtn) {
            redOffBtn.addEventListener('click', function() {
                fetch(`${API_URL}/gpio/red/off`, {method: 'POST'})
                    .then(r => r.json())
                    .then(data => {
                        document.getElementById('redLight').className = 'light-indicator light-off';
                        showSuccess('Red light turned OFF');
                    });
            });
        }
        
        // Green Light ON
        const greenOnBtn = Array.from(lightTab.querySelectorAll('.btn-success')).find(btn => 
            btn.textContent.includes('Test ON') && btn.closest('.card-body').textContent.includes('Green')
        );
        if(greenOnBtn) {
            greenOnBtn.addEventListener('click', function() {
                fetch(`${API_URL}/gpio/green/on`, {method: 'POST'})
                    . then(r => r.json())
                    .then(data => {
                        if(data. success) {
                            document. getElementById('greenLight').className = 'light-indicator light-green';
                            showSuccess(data. message);
                        } else {
                            showError(data. message);
                        }
                    });
            });
        }
        
        // Green Light OFF
        const greenOffBtn = Array.from(lightTab.querySelectorAll('.btn-outline-secondary')).find(btn => 
            btn.textContent.includes('Turn OFF') && btn.closest('.card-body').textContent.includes('Green')
        );
        if(greenOffBtn) {
            greenOffBtn.addEventListener('click', function() {
                fetch(`${API_URL}/gpio/green/off`, {method: 'POST'})
                    .then(r => r.json())
                    .then(data => {
                        document.getElementById('greenLight').className = 'light-indicator light-off';
                        showSuccess('Green light turned OFF');
                    });
            });
        }
    }
});

</script>
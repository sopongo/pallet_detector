<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Pallet Detection - Configuration</title>
    
    <!-- ========================================
         CDN Links - AdminLTE v3 + Dependencies
         ======================================== -->
    
    <!-- Google Font: Kanit -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Kanit:wght@400&display=swap" rel="stylesheet">
    
    <!-- Font Awesome (Icons) -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    
    <!-- AdminLTE v3.2 -->
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/admin-lte@3.2/dist/css/adminlte. min.css">
    
    <!-- Bootstrap 4.6 (required by AdminLTE v3) -->
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@4.6.2/dist/css/bootstrap.min.css">
    
    <!-- Custom CSS -->
    <style>
        /* Apply Kanit font globally */
        body {
            font-family: 'Kanit', sans-serif;
        }
        
        /* Dark Mode Variables */
        body.dark-mode {
            background-color: #1a1a1a;
            color: #e0e0e0;
        }
        
        body.dark-mode .card {
            background-color: #2a2a2a;
            color: #e0e0e0;
        }
        
        body.dark-mode .nav-tabs .nav-link {
            color: #b0b0b0;
            background-color: #2a2a2a;
        }
        
        body.dark-mode .nav-tabs .nav-link.active {
            background-color: #3a3a3a;
            color: #fff;
            border-color: #444;
        }
        
        body.dark-mode .form-control,
        body.dark-mode .custom-select {
            background-color: #3a3a3a;
            color: #e0e0e0;
            border-color: #555;
        }
        
        body.dark-mode .btn-outline-secondary {
            color: #b0b0b0;
            border-color: #555;
        }
        
        body.dark-mode .btn-outline-secondary:hover {
            background-color: #444;
            color: #fff;
        }
        
        /* Camera Preview */
        .camera-preview {
            width: 100%;
            max-width: 640px;
            height: 480px;
            background-color: #000;
            border:  2px solid #ddd;
            border-radius:  8px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #888;
            font-size: 18px;
            margin:  20px auto;
        }
        
        body.dark-mode .camera-preview {
            border-color: #555;
        }
        
        /* Light Signal Indicator */
        .light-indicator {
            width: 100px;
            height: 100px;
            border-radius: 50%;
            margin: 10px;
            display: inline-block;
            box-shadow: 0 0 20px rgba(0,0,0,0.3);
        }
        
        .light-red {
            background:  radial-gradient(circle, #ff4444, #cc0000);
        }
        
        .light-yellow {
            background: radial-gradient(circle, #ffff44, #cccc00);
        }
        
        .light-green {
            background: radial-gradient(circle, #44ff44, #00cc00);
        }
        
        .light-off {
            background: #333;
        }
        
        /* Status Bar */
        .status-bar {
            background-color: #f8f9fa;
            padding:  10px 20px;
            border-top: 1px solid #dee2e6;
            font-size: 14px;
        }
        
        body.dark-mode .status-bar {
            background-color: #2a2a2a;
            border-top-color: #444;
        }
        
        /* Slider Custom Styles */
        .custom-range::-webkit-slider-thumb {
            background: #007bff;
        }
        
        .custom-range::-moz-range-thumb {
            background: #007bff;
        }
        
        /* Tab Icons */
        .nav-tabs .nav-link i {
            margin-right: 8px;
        }
        
        /* Header Actions */
        .header-actions {
            display: flex;
            gap: 10px;
            align-items: center;
        }
    </style>
</head>
<body class="hold-transition sidebar-mini layout-fixed">

<div class="wrapper">
    
    <!-- ========================================
         Main Content
         Note: Paste this inside your AdminLTE content-wrapper
         ======================================== -->
    
    <div class="content-wrapper">
        <!-- Content Header -->
        <section class="content-header">
            <div class="container-fluid">
                <div class="row mb-2">
                    <div class="col-sm-6">
                        <h1><i class="fas fa-cogs"></i> System Configuration</h1>
                    </div>
                    <div class="col-sm-6">
                        <div class="header-actions float-right">
                            <!-- Dark Mode Toggle -->
                            <button class="btn btn-outline-secondary" id="darkModeToggle" title="Toggle Dark Mode">
                                <i class="fas fa-moon"></i>
                            </button>
                            
                            <!-- Export Config Button -->
                            <button class="btn btn-success" id="exportConfig">
                                <i class="fas fa-download"></i> Export Config
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </section>

        <!-- Main Content -->
        <section class="content">
            <div class="container-fluid">
                
                <!-- Tabs Card -->
                <div class="card card-primary card-outline card-tabs">
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
                                    <i class="fas fa-network-wired"></i> Network
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
                                <h4><i class="fas fa-folder"></i> Save Image Path</h4>
                                <hr>
                                <div class="row">
                                    <div class="col-md-8">
                                        <div class="form-group">
                                            <label for="imagePath">Image Storage Path</label>
                                            <div class="input-group">
                                                <input type="text" class="form-control" id="imagePath" value="D:\python_project\pallet_detection\#data_source">
                                                <div class="input-group-append">
                                                    <button class="btn btn-outline-secondary" type="button">
                                                        <i class="fas fa-folder-open"></i> Browse
                                                    </button>
                                                </div>
                                            </div>
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
                                <!-- WiFi Config -->
                                <h4><i class="fas fa-wifi"></i> WiFi Configuration</h4>
                                <hr>
                                <div class="row">
                                    <div class="col-md-6">
                                        <div class="form-group">
                                            <label for="wifiSSID">Network Name (SSID)</label>
                                            <input type="text" class="form-control" id="wifiSSID" placeholder="WH-PACJ">
                                        </div>
                                        <div class="form-group">
                                            <label for="wifiUser">Username (Optional)</label>
                                            <input type="text" class="form-control" id="wifiUser" placeholder="username">
                                        </div>
                                        <div class="form-group">
                                            <label for="wifiPass">Password</label>
                                            <input type="password" class="form-control" id="wifiPass" placeholder="••••••••">
                                        </div>
                                        <button class="btn btn-info">
                                            <i class="fas fa-signal"></i> Test WiFi
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
                                                <div class="input-group-append">
                                                    <button class="btn btn-outline-secondary" type="button">
                                                        <i class="fas fa-folder-open"></i> Browse
                                                    </button>
                                                </div>
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
                                        
                                        <button class="btn btn-info">
                                            <i class="fas fa-check-circle"></i> Test Model
                                        </button>
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
                                                <p><strong>Used: </strong> 274 MB</p>
                                                <p><strong>Total Files:</strong> 1,452</p>
                                                <p><strong>Path:</strong> <code>D:\python_project\pallet_detection\#data_source</code></p>
                                                <div class="progress">
                                                    <div class="progress-bar bg-info" role="progressbar" style="width:  27%" aria-valuenow="27" aria-valuemin="0" aria-valuemax="100">27%</div>
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
                                        <button class="btn btn-warning btn-block">
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
                                                <option value="0">USB Camera 0</option>
                                                <option value="1">USB Camera 1</option>
                                                <option value="2">USB Camera 2</option>
                                                <option value="rtsp">IP Camera (RTSP)</option>
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
                                
                                <br>
                                <h4><i class="fas fa-eye"></i> Live Camera Preview</h4>
                                <hr>
                                <div class="camera-preview">
                                    <span><i class="fas fa-video-slash"></i> No camera feed</span>
                                    <!-- TODO: Replace with <img id="cameraFeed" src=""> or <canvas> for real-time feed -->
                                </div>
                                <div class="text-center">
                                    <button class="btn btn-primary">
                                        <i class="fas fa-redo"></i> Refresh Feed
                                    </button>
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
                        <button class="btn btn-success btn-lg">
                            <i class="fas fa-save"></i> Save All Changes
                        </button>
                        <button class="btn btn-secondary btn-lg ml-2">
                            <i class="fas fa-undo"></i> Reset to Default
                        </button>
                    </div>
                </div>
                
            </div>
        </section>
        
    </div>
    
    <!-- ========================================
         Status Bar (Footer)
         ======================================== -->
    <footer class="status-bar">
        <div class="row">
            <div class="col-md-3">
                <strong>Version: </strong> 1.0 | Last Update: 24-12-2025
            </div>
            <div class="col-md-3">
                <strong>Network:</strong> <span class="badge badge-success">Online</span> (WiFi:  WH-PACJ)
            </div>
            <div class="col-md-3">
                <strong>Last Sending:</strong> 24/12/2025 15:10: 00
            </div>
            <div class="col-md-3">
                <strong>Storage:</strong> 274 MB (1,452 Files)
            </div>
        </div>
    </footer>

</div>

<!-- ========================================
     JavaScript - jQuery, Bootstrap, AdminLTE
     ======================================== -->

<!-- jQuery -->
<script src="https://code.jquery.com/jquery-3.6.0.min. js"></script>

<!-- Bootstrap 4.6 JS -->
<script src="https://cdn.jsdelivr.net/npm/bootstrap@4.6.2/dist/js/bootstrap.bundle.min.js"></script>

<!-- AdminLTE v3.2 -->
<script src="https://cdn.jsdelivr.net/npm/admin-lte@3.2/dist/js/adminlte.min.js"></script>

<!-- Custom JavaScript -->
<script>
    // ========================================
    // Dark Mode Toggle
    // ========================================
    document.getElementById('darkModeToggle').addEventListener('click', function() {
        document.body.classList.toggle('dark-mode');
        
        // Change icon
        const icon = this.querySelector('i');
        if (document.body. classList.contains('dark-mode')) {
            icon.classList.remove('fa-moon');
            icon.classList.add('fa-sun');
        } else {
            icon.classList.remove('fa-sun');
            icon.classList. add('fa-moon');
        }
        
        // TODO: Save preference to localStorage
        localStorage.setItem('darkMode', document.body.classList.contains('dark-mode'));
    });
    
    // Load dark mode preference on page load
    if (localStorage.getItem('darkMode') === 'true') {
        document.body.classList.add('dark-mode');
        document.getElementById('darkModeToggle').querySelector('i').classList.replace('fa-moon', 'fa-sun');
    }
    
    // ========================================
    // Export Config as JSON
    // ========================================
    document.getElementById('exportConfig').addEventListener('click', function() {
        // TODO: Collect all form values and create JSON object
        const config = {
            general: {
                imagePath: document.getElementById('imagePath').value,
                version: "1.0",
                lastUpdate: "24-12-2025"
            },
            network: {
                database: {
                    host: document.getElementById('dbHost').value,
                    user: document.getElementById('dbUser').value,
                    password: document.getElementById('dbPass').value,
                    port: document.getElementById('dbPort').value,
                    database: document.getElementById('dbName').value
                },
                wifi: {
                    ssid:  document.getElementById('wifiSSID').value,
                    username: document.getElementById('wifiUser').value,
                    password: document.getElementById('wifiPass').value
                },
                lineNotify: {
                    token: document.getElementById('lineToken').value,
                    groupId: document.getElementById('lineGroup').value
                }
            },
            detection: {
                modelPath: document.getElementById('modelPath').value,
                confidenceThreshold: parseFloat(document.getElementById('confThreshold').value),
                iouThreshold: parseFloat(document.getElementById('iouThreshold').value),
                imageSize: parseInt(document.getElementById('imageSize').value),
                deviceMode: document.querySelector('input[name="deviceMode"]:checked').value,
                captureInterval: parseInt(document.getElementById('captureInterval').value),
                alertThreshold: parseInt(document.getElementById('alertThreshold').value)
            },
            camera: {
                selectedCamera: document.getElementById('cameraSelect').value
            },
            gpio: {
                redLightPin: 17,
                greenLightPin: 27
            }
        };
        
        // Create downloadable JSON file
        const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(config, null, 4));
        const downloadAnchor = document.createElement('a');
        downloadAnchor.setAttribute("href", dataStr);
        downloadAnchor.setAttribute("download", "pallet_config.json");
        document.body.appendChild(downloadAnchor);
        downloadAnchor.click();
        downloadAnchor.remove();
        
        alert('Configuration exported successfully!');
    });
    
    // ========================================
    // Light Signal Test Buttons (Demo)
    // ========================================
    // TODO: Connect to backend API for real GPIO control
    
    // Example: Red light test
    document.querySelectorAll('.btn-danger').forEach(btn => {
        if (btn.textContent.includes('Test ON')) {
            btn.addEventListener('click', function() {
                document.getElementById('redLight').classList.remove('light-off');
                document.getElementById('redLight').classList.add('light-red');
                // TODO: Send API request to turn on GPIO pin 17
            });
        }
    });
    
</script>

</body>
</html>
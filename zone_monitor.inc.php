<div class="card shadow-lg">
  <div class="card-header">
    <h3 class="card-title">
      <i class="fas fa-cogs mr-2"></i> Monitoring (Zone)
      <span class="ml-2 text-muted" style="font-size: 0.9rem;">
        (Date: <span id="header-clock" class="text-dark font-weight-bold"><?PHP echo date("d/m/Y H:i:s");?></span>)
      </span>
    </h3>
  </div>
  
  <div class="card-body bg-light">
    <div class="container-fluid">
      <div class="row">
        
        <div class="col-md-9">
          
          <div class="card card-dark shadow">
            <div class="card-header">
              <h3 class="card-title"><i class="fas fa-desktop mr-2"></i> Live Detection - <span class="summary-site"></span> <i class="fas fa-angle-double-right text-sm" aria-hidden="true"></i>
 <span class="summary-location"></span></h3>
            </div>
            <div class="card-body bg-gray-light">
              <div class="row">
                <div class="col-md-12">
                  <div class="detection-wrapper border bg-white p-2 mb-2">
                    <div class="pallet-image-container position-relative">
                      <img id="live-stream" src="dist/img/no-signal-on-tv-screen_2.jpg" class="img-fluid rounded border" alt="Live Stream">
                      <!-- ✅ SVG overlay (ทับบนวิดีโอ) -->
                      <svg id="zone-overlay" viewBox="0 0 1280 720">
                          <!-- Zones จะถูกวาดที่นี่ -->
                          <polygon points="100,100 200,100 200,200 100,200" />
                      </svg>
                    </div>
                  </div>
                </div>
                

              </div>
            </div>
            <div class="card-footer py-2 border-top">
               <!-- แก้ไข: เพิ่ม span id="system-status" เพื่อแสดง Online/Offline ของระบบ -->
               <small class="text-muted"><i class="fas fa-network-wired text-success mr-1"></i> Status: <span id="system-status" class="ml-2 text-info">Checking...</span></small>
            </div>
          </div>

          <div class="card card-outline card-secondary shadow-sm">
            <div class="card-header py-2">
              <h3 class="card-title text-sm font-weight-bold"><i class="fas fa-list-ul mr-2"></i> System Logs (Live Feed)</h3>
            </div>
            <div class="card-body p-0">
              <div id="log-container">
                <div class="text-muted p-3">System ready. Waiting for Monitoring to start...</div>
              </div>
            </div>
          </div>

        </div> 
        
        <div class="col-md-3">
          <div class="card card-gray-dark card-outline shadow-sm">
            <div class="card-header bg-white">
              <h3 class="card-title text-bold">Detect Summary (<span id="header-date"><?php echo date("d/m/Y"); ?></span>)</h3>
            </div>
            <div class="card-body p-0">
              <ul class="list-group list-group-flush">
                <li class="list-group-item pt-2 pb-2"><b>Site:</b> <span class="float-right summary-site">-</span></li>
                <li class="list-group-item pt-2 pb-2"><b>Location:</b> <span class="float-right summary-location" >-</span></li>
                <li class="list-group-item pt-2 pb-2 text-primary"><b>Total Photos:</b> <span class="float-right text-bold" id="summary-photos">0</span></li>
                <li class="list-group-item pt-2 pb-2"><b>Total Detected:</b> <span class="float-right text-bold" id="summary-detected">0</span></li>
                <li class="list-group-item pt-2 pb-2 text-success"><b>Pallet In Time:</b> <span class="float-right text-bold" id="summary-in-time">0</span></li>
                <li class="list-group-item pt-2 pb-2 text-danger"><b>Pallet Over Time:</b> <span class="float-right text-bold" id="summary-over-time">0</span></li>
                <li class="list-group-item pt-2 pb-2 text-purple" style="color: #6f42c1 !important;"><b>Notifications:</b> <span class="float-right text-bold" id="summary-notifications">0</span></li>
              </ul>
            </div>
            <div class="card-footer p-2 bg-white border-top-0">
                <!-- ปรับปรุง: ปุ่มจะถูก disable ขณะเรียก API และแสดง spinner ระหว่างรอ -->
                <button id="btn-toggle-monitor" class="btn btn-lg btn-danger btn-block text-bold shadow">
                  <i class="fas fa-play-circle mr-2"></i> Start Monitoring
                </button>

                <!-- ปรับปรุง: แสดง PID ของ detection service เมื่อรัน -->
                <!--<div id="service-pid" class="text-center mt-2 small text-muted"></div>-->
            </div>
          </div>

          <div class="card card-outline card-info shadow-sm mt-3">
            <div class="card-header py-2">
              <h3 class="card-title text-sm text-bold"><i class="fas fa-sliders-h mr-2"></i> System Information</h3>
            </div>
            <div class="card-body p-0">
              <table class="table table-sm table-striped mb-0 text-sm">
                <tbody>
                  <tr><td><b>Working time Detection:</b></td><td class="text-right">-</td></tr>
                  <tr><td><b>Inbound Zone:</b></td><td class="text-right text-info font-weight-bold">-</td></tr>
                  <tr><td><b>Outbound Zone:</b></td><td class="text-right text-info font-weight-bold">-</td></tr>
                  <tr><td><b>Mode:</b></td><td class="text-right text-success"><i class="fas fa-microchip mr-1"></i> -</td></tr>
                  <tr><td><b>Ram:</b></td><td class="text-right text-success"><i class="fas fa-memory mr-1"></i> -</td></tr>
                  <tr><td><b>Temp box enclosure:</b></td><td class="text-right">- <sup>°C</sup></td></tr>
                </tbody>
              </table>
            </div>
          </div>
          

        </div> </div> </div> </div> </div> 
        
<style type="text/css">
.pallet-image-container {
    position: relative;
    width: 100%;
    aspect-ratio: 16 / 9;
    background: #eaeaea;
    overflow: hidden;
}

.pallet-image-container img {
    width: 100%;
    height: 100%;
    object-fit: contain;
}

/* ✅ SVG Overlay */
#zone-overlay {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    pointer-events: none;
    z-index: 10;
    display: none; /* ซ่อน SVG โดยค่าเริ่มต้น */
}

/* ✅ Zone Polygon Styles */
.zone-polygon {
    fill: rgba(0, 255, 0, 0.1); /* สีเขียวโปร่งแสง */
    stroke: #00ff00; /* เส้นขอบสีเขียว */
    stroke-width: 2;
    transition: all 0.3s ease;
}

.zone-polygon.inbound {
    fill: rgba(0, 120, 255, 0.15);
    stroke: #0078ff;
    stroke-width: 2;
}

.zone-polygon.outbound {
    fill: rgba(255, 120, 0, 0.15);
    stroke: #ff7800;
    stroke-width: 2;
}

.zone-polygon.inactive {
    fill: rgba(128, 128, 128, 0.1);
    stroke: #808080;
    stroke-width: 1;
    stroke-dasharray: 5, 5; /* เส้นประ */
}

/* Zone Label */
.zone-label {
    font-size: 14px;
    font-weight: bold;
    fill: white;
    text-shadow: 1px 1px 2px rgba(0,0,0,0.8);
    pointer-events: none;
}
  
  .ai-box { 
    position: absolute; 
    border: 2px solid #ff0000; 
    pointer-events: none; 
    box-shadow: 0 0 8px rgba(255, 0, 0, 0.6); 
    border-radius: 2px; 
    z-index: 5; 
  }
  
  .ai-label-tag { 
    position: absolute; 
    top: -24px; 
    left: -2px; 
    font-size: 11px !important; 
    padding: 2px 6px !important; 
    border-radius: 3px 3px 0 0 !important; 
    background-color: rgba(220, 53, 69, 0.95) !important; 
    color: white !important; 
    font-weight: bold !important; 
  }
  
  #log-container { 
    height: 130px; 
    overflow-y: auto; 
    background: #1e1e1e; 
    color: #00ff00; 
    font-family: Arial, Helvetica, sans-serif;
    padding: 12px; 
    font-size: 13px; 
  }
  
  .detection-wrapper img { 
    width: 100%; 
    transition: opacity 0.5s ease; 
  }
  
  .log-error { 
    color: #ff4444 !important; 
    font-weight: bold; 
  }
  
  .log-warning { 
    color: #ffaa00 !important; 
  }
</style>

<script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/bootstrap@4.6.1/dist/js/bootstrap.bundle.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<!-- SweetAlert2 CDN -->
<script src="https://cdn.jsdelivr.net/npm/sweetalert2@11"></script>

<script type="text/javascript">
// ========================================
// Zone Overlay Functions
// ========================================

let zonesData = [];
let cameraResolution = { width: 1280, height: 720 };

/**
 * Load camera resolution from config
 */
async function loadCameraResolution() {
    const API_URL = `http://${window.location.hostname}:5000/api`;
    try {
        const response = await fetch(`${API_URL}/config`);
        const data = await response.json();
        
        if (data.camera && data.camera.resolution) {
            cameraResolution = data.camera.resolution;
            console.log(`📷 Camera resolution: ${cameraResolution.width}x${cameraResolution.height}`);
            
            // Update SVG viewBox
            $('#zone-overlay').attr('viewBox', `0 0 ${cameraResolution.width} ${cameraResolution.height}`);
        }
    } catch (error) {
        console.error('❌ Error loading config:', error);
    }
}

/**
 * Load zones from API
 */
async function loadZones() {
    const API_URL = `http://${window.location.hostname}:5000/api`;
    try {
        const response = await fetch(`${API_URL}/zones`);
        const data = await response.json();
        
        if (data.success) {
            zonesData = data.zones;
            console.log(`✅ Loaded ${zonesData.length} zones`);
            drawZones();
        } else {
            console.error('❌ Failed to load zones:', data.message);
        }
    } catch (error) {
        console.error('❌ Error loading zones:', error);
    }
}

/**
 * Draw zones on SVG overlay
 */
function drawZones() {
    const svg = $('#zone-overlay');
    svg.empty();
    
    if (!zonesData || zonesData.length === 0) {
        console.warn('⚠️ No zones to draw');
        return;
    }
    
    zonesData.forEach(zone => {
        if (!zone.active) {
            return;
        }
        
        // Convert normalized coordinates (0-1) to pixel coordinates
        const points = zone.polygon.map(point => {
            const x = point[0] * cameraResolution.width;
            const y = point[1] * cameraResolution.height;
            return `${x},${y}`;
        }).join(' ');
        
        // Determine class by pallet_type
        let zoneClass = 'zone-polygon';
        if (zone.pallet_type === 1) {
            zoneClass += ' inbound';
        } else if (zone.pallet_type === 2) {
            zoneClass += ' outbound';
        }
        
        // Create polygon element
        const polygon = document.createElementNS('http://www.w3.org/2000/svg', 'polygon');
        polygon.setAttribute('points', points);
        polygon.setAttribute('class', zoneClass);
        polygon.setAttribute('data-zone-id', zone.id);
        polygon.setAttribute('data-zone-name', zone.name);
        
        // Add tooltip
        const title = document.createElementNS('http://www.w3.org/2000/svg', 'title');
        title.textContent = `${zone.name} (Threshold: ${zone.threshold_percent}%, Alert: ${zone.alert_threshold}ms)`;
        polygon.appendChild(title);
        
        svg.append(polygon);
        
        // Draw label
        drawZoneLabel(svg, zone);
    });
    
    console.log(`✅ Drew ${zonesData.length} zones`);
}

/**
 * Draw zone label at center
 */
function drawZoneLabel(svg, zone) {
    let sumX = 0, sumY = 0;
    zone.polygon.forEach(point => {
        sumX += point[0] * cameraResolution.width;
        sumY += point[1] * cameraResolution.height;
    });
    
    const centerX = sumX / zone.polygon.length;
    const centerY = sumY / zone.polygon.length;
    
    const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
    text.setAttribute('x', centerX);
    text.setAttribute('y', centerY);
    text.setAttribute('class', 'zone-label');
    text.setAttribute('text-anchor', 'middle');
    text.setAttribute('dominant-baseline', 'middle');
    text.textContent = zone.name;
    
    svg.append(text);
}

/**
 * Highlight zone (when object detected)
 */
function highlightZone(zoneId, hasObject) {
    const polygon = $(`#zone-overlay polygon[data-zone-id="${zoneId}"]`);
    
    if (polygon.length === 0) {
        console.warn(`⚠️ Zone ${zoneId} polygon not found`);
        return;
    }
    
    if (hasObject) {
        // ✅ มีวัตถุใน zone → เปลี่ยนเป็นสีแดง
        console.log(`🔴 Zone ${zoneId}: Object detected`);
        
        polygon.css({
            'fill': 'rgba(255, 0, 0, 0.3)',
            'stroke': '#ff0000',
            'stroke-width': '4'
        });
    } else {
        // ✅ ไม่มีวัตถุ → คืนสีเดิม
        console.log(`🟢 Zone ${zoneId}: No object`);
        
        polygon.removeAttr('style');
    }
}


/**
 * Show alert animation on zone
 */
function showZoneAlert(zoneId) {
    const polygon = $(`#zone-overlay polygon[data-zone-id="${zoneId}"]`);
    
    polygon.css({
        'fill': 'rgba(255, 0, 0, 0.5)',
        'stroke': '#ff0000',
        'stroke-width': '4'
    });
    
    let count = 0;
    const flashInterval = setInterval(() => {
        polygon.css('fill', count % 2 === 0 ? 'rgba(255, 0, 0, 0.5)' : 'rgba(255, 0, 0, 0.2)');
        count++;
        if (count >= 6) {
            clearInterval(flashInterval);
        }
    }, 500);
}

/**
 * Fetch zone status from API
 */
/**
 * Fetch zone status and update highlights
 */
function fetchZoneStatus() {
    $.get(API_URL + '/detection/zone-status', function(data) {
        console.log('📊 Zone status:', data); // ✅ Debug log
        
        if (data.success && data.zones && data.zones.length > 0) {
            data.zones.forEach(function(zoneStatus) {
                // Highlight zone if has object
                highlightZone(zoneStatus.zone_id, zoneStatus.has_object);
                
                // Show alert animation if needed
                if (zoneStatus.alert) {
                    showZoneAlert(zoneStatus.zone_id);
                }
            });
            
            console.log(`✅ Updated ${data.zones.length} zones`);
        } else {
            console.warn('⚠️ No zone status data');
        }
    }).fail(function(xhr) {
        console.error('❌ Cannot fetch zone status:', xhr.status, xhr.responseText);
    });
}

const API_URL = `http://${window.location.hostname}:5000/api`;
const POLLING_INTERVAL = 3000;

console.log('🔗 API_URL:', API_URL);

$(function () {
// ========================================
// API Base URL / Configuration
// ========================================
// ✅ Auto-detect hostname (works on any device)
//const API_URL = `http://${window.location.hostname}:5000/api`;
//const POLLING_INTERVAL = 3000;

// Debug: แสดง API_URL ที่ใช้
//console.log('🔗 API_URL:', API_URL);
  
  let isRunning = false;
  let pollingTimer = null;

  // ========================================
  // 1. Real-time Header Clock
  // ========================================
  function updateHeaderClock() {
      const now = new Date();

      // 1. สร้าง String สำหรับ วันที่และเวลา (DD/MM/YYYY HH:mm:ss)
      const formattedFull = now.toLocaleString('en-GB', { 
          day: '2-digit', 
          month: '2-digit', 
          year: 'numeric',
          hour: '2-digit', 
          minute: '2-digit', 
          second: '2-digit', 
          hour12: false
      }).replace(',', '');

      // 2. สร้าง String สำหรับ เฉพาะวันที่ (DD/MM/YYYY)
      const onlyDate = now.toLocaleDateString('en-GB', {
          day: '2-digit',
          month: '2-digit',
          year: 'numeric'
      });

      // 3. ส่งค่าไปแสดงผลตาม ID ที่กำหนด
      $('#header-clock').text(formattedFull); // แสดงทั้งวันที่และเวลา
      $('#header-date').text(onlyDate);       // แสดงเฉพาะวันที่ 06/01/2026
  }
  setInterval(updateHeaderClock, 1000);

  // ========================================
  // Helper: อัพเดตข้อความ Online/Offline ตรง Status
  // - ฟังก์ชันนี้จะถูกเรียกจาก fetchDetectionStatus และเมื่อเริ่ม/หยุด
  // ========================================
  function updateSystemStatus(online, running, pid) {
    const $status = $('#system-status');
    if (!online) {
      // ถ้าเรียก API ไม่ได้ -> Offline
      $status.text('Offline').removeClass('text-success text-info').addClass('text-danger');
      $('#service-pid').text(''); // ล้าง pid
      return;
    }

    // ถ้าถึง API ได้ ให้แสดงสถานะการรันของ detection service
    if (running) {
      $status.text('Online (Detection running)').removeClass('text-danger text-info').addClass('text-success');
      if (pid) {
        $('#service-pid').text('PID: ' + pid);
      } else {
        $('#service-pid').text('PID: —');
      }
    } else {
      $status.text('Online (Idle)').removeClass('text-danger text-success').addClass('text-info');
      $('#service-pid').text('PID: —');
    }
  }

  // ========================================
  // Video Stream Control Functions
  // ========================================
  function startVideoStream() {
    $('#live-stream').attr('src', `${API_URL}/camera/stream/0?t=${Date.now()}`);
  }

  function stopVideoStream() {
    $('#live-stream').attr('src', 'dist/img/no-signal-on-tv-screen_2.jpg');
  }

  // ========================================
  // 2. Fetch Detection Status
  // - ปรับให้ call updateSystemStatus เพื่ออัพเดต Status และ PID
  // - ถ้า backend รายงาน running=true ให้เริ่ม polling อัตโนมัติ (เติม behavior ที่ผู้ใช้ต้องการ)
  // ========================================
  function fetchDetectionStatus() {
    $.get(API_URL + '/detection/status', function(data) {
      if (data && data.success) {
        // อัพเดตปุ่มและสถานะระบบ
        updateButtonState(!!data.running);
        updateSystemStatus(true, !!data.running, data.pid);

        // ถ้า backend ระบุว่ากำลังรัน ให้เริ่ม poll ข้อมูล (เหมือนกด Start)
        if (data.running) {
          // ถ้ายังไม่ polling ให้เริ่ม
          if (!pollingTimer) {
            // เรียกข้อมูลทันทีเพื่อเติม UI (images, logs, summary)
            //fetchLatestDetection();
            fetchSummary();
            fetchLogs();
            // เริ่ม polling แบบต่อเนื่อง
            startPolling();
          }
        } else {
          // ถ้า backend บอกว่าไม่รัน ให้หยุด polling และแสดงค่า default (ถ้าต้องการ)
          stopPolling();
          // ไม่ล้างรูป/summary ให้ผู้ใช้ยังเห็นค่าล่าสุด (ถ้าต้องการล้าง ให้ uncomment)
          // $('#img-before').attr('src', 'dist/img/wait.png');
          // $('#img-after').attr('src', 'dist/img/wait.png');
        }
      } else {
        updateButtonState(false);
        updateSystemStatus(true, false, null);
      }
    }).fail(function() {
      console.error('Cannot fetch detection status');
      // ถ้าเรียกไม่ได้ ถือว่า Offline
      updateButtonState(false);
      updateSystemStatus(false, false, null);
      // หยุด polling ถ้าเคยรัน
      stopPolling();
    });
  }

  // ========================================
  // 3.  Fetch Latest Detection (2 images)
  // ========================================
  /*function fetchLatestDetection() {
    $.get(API_URL + '/detection/latest', function(data) {
      if (data.success) {
        // Update Before image
        if (data.before) {
          $('#img-before').attr('src', data.before.image_url + '?t=' + Date.now());
          $('#mock-time-before').text(data.before.date);
          $('#file-before').text(data.before.filename + ' | Result: ' + data.before.count + ' Pallets');
        }
        
        // Update After image
        if (data.after) {
          $('#img-after').attr('src', data.after.image_url + '?t=' + Date. now());
          $('#mock-time-after').text(data.after.date);
          $('#file-after').text(data.after.filename + ' | Result: ' + data.after.count + ' Pallets');
        }
      }
    }).fail(function() {
      console.error('Cannot fetch latest detection');
    });
  }*/

  // ========================================
  // 4. Fetch Summary (แบบใหม่ - ใช้ ID)
  // ========================================
function fetchSummary() {
  $.get(API_URL + '/detection/summary/today', function(data) {
    if (data.success) {
      // Update โดยใช้ ID
      $('.summary-site').text(data.site);
      $('.summary-location').text(data.location);
      $('#summary-photos').text(data.total_photos);
      $('#summary-detected').text(data.total_detected);
      $('#summary-in-time').text(data.in_time);
      $('#summary-over-time').text(data.over_time);
      $('#summary-notifications').text(data.notifications);
      
      console.log('✅ Summary updated:', data);
    }
  }).fail(function(xhr) {
    console.error('❌ Cannot fetch summary:', xhr.responseText);
  });
}



  // ========================================
  // 5.  Fetch System Logs
  // - note: fixed previous spacing bug (parameter 'limit' passing)
  // - ✅ Updated to handle log objects with class
  // ========================================
  function fetchLogs() {
    $.get(API_URL + '/detection/logs?limit=15', function(data) {
      if (data.success && data.logs.length > 0) {
        // Clear placeholder
        if ($('#log-container').find('.text-muted').length) {
          $('#log-container').empty();
        }
        
        // Clear old logs first
        $('#log-container').empty();
        
        // ✅ Add new logs (now handling objects with class)
        data.logs.forEach(function(log) {
          // Check if log is object or string (backward compatibility)
          if (typeof log === 'object' && log.text) {
            const logHtml = '<div class="' + (log.class || '') + '">' + log.text + '</div>';
            $('#log-container').append(logHtml);
          } else {
            // Fallback for old format
            const logHtml = '<div>' + log + '</div>';
            $('#log-container').append(logHtml);
          }
        });
        
        // Auto scroll to bottom
        $('#log-container').scrollTop($('#log-container')[0].scrollHeight);
        
        console.log('✅ Logs updated:   ' + data.logs.length + ' lines');
      } else {
        console.log('⚠️ No logs found');
      }
    }).fail(function(xhr) {
      console.error('❌ Cannot fetch logs:', xhr.responseText);
    });
  }

  // ========================================
  // 6. Fetch System Info
  // Note: Uses table row indices (tr:eq(N)) - ensure HTML table matches this order:
  // Row 0: Working time Detection, Row 1: Inbound Zone, Row 2: Outbound Zone,
  // Row 3: Mode (CPU), Row 4: Ram, Row 5: Temp box enclosure
  // ========================================
  function fetchSystemInfo() {
    $.get(API_URL + '/system/info', function(data) {
      if (data.success) {
        // Update system info table
        $('table.table-sm tbody tr:eq(0) td:last').text(data.operating_hours);
        $('table.table-sm tbody tr:eq(1) td:last').text(data.inbound_zones);
        $('table.table-sm tbody tr:eq(2) td:last').text(data.outbound_zones);
        $('table.table-sm tbody tr:eq(3) td:last').html('<i class="fas fa-microchip mr-1"></i> ' + data.cpu_usage);
        $('table.table-sm tbody tr:eq(4) td:last').html('<i class="fas fa-memory mr-1"></i> ' + data.ram_total + ' (Used: ' + data.ram_usage + ')');
        $('table.table-sm tbody tr:eq(5) td:last').text(data.temperature);
      }
    }).fail(function() {
      console.error('Cannot fetch system info');
    });
  }

  // ========================================
  // 7. Start/Stop Button Handler
  // - ปรับป���ุง: disable ปุ่มขณะรอ request และแสดง spinner / คืนค่าปุ่มเมื่อเสร็จ
  // - เพิ่ม error handling ที่ชัดเจน
  // ========================================
    $('#btn-toggle-monitor').click(function() {
      const $btn = $(this);
      
      if (! isRunning) {
          // START
          console.log('🟢 Starting detection...');
          
          // ปิดปุ่มระหว่างเรียก เพื่อป้องกันกดซ้ำ
          $btn.prop('disabled', true);
          const originalHtml = $btn.html();
          $btn.html('<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Starting...');

          $.post(API_URL + '/detection/start', function(response) {
              console.log('📥 Start response:', response);
              
              if (response.success) {
                  updateButtonState(true);
                  startVideoStream();
                  $('#zone-overlay').show(); // ← แสดง SVG
                  startPolling();
                  updateSystemStatus(true, true, response.pid); // อัพเดต status และ PID
                  
                  // ✅ Reload zones when starting
                  loadZones();
                  
                  Swal.fire({
                      icon: 'success',
                      title:  'Success!',
                      text: response.message,
                      confirmButtonColor: '#28a745',
                      timer: 1000, // Time in milliseconds
                      timerProgressBar: true,
                    }).then((result) => {                
                      if (result.dismiss === Swal.DismissReason.timer || result.isConfirmed) {
                          Swal.close();
                      }
                  });
              } else {
                  console.error('❌ Start failed:', response.message);
                  Swal.fire({
                      icon: 'error',
                      title: 'Error!',
                      text: response.message,
                      confirmButtonColor:  '#dc3545'
                  });
              }
          }).fail(function(xhr, status, error) {
              console.error('❌ Start request failed:', {
                  status: xhr.status,
                  responseText: xhr.responseText,
                  error: error
              });
              
              Swal.fire({
                  icon: 'error',
                  title: 'Error!',
                  text: 'Cannot start detection service:  ' + error,
                  confirmButtonColor: '#dc3545'
              });
          }).always(function() {
              // คืนค่าปุ่มไม่ว่าจะสำเร็จหรือไม่
              $btn.prop('disabled', false);
              $btn.html(originalHtml);
              // รีเช็คสถานะจริง (fallback)
              fetchDetectionStatus();
          });
          
      } else {
          // STOP
          // ✅ เช็ค status ก่อน stop
          console.log('🔴 Checking status before stop...');
          
          // ปิดปุ่มขณะรอ
          $btn.prop('disabled', true);
          const origHtml = $btn.html();
          $btn.html('<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Stopping...');

          $.get(API_URL + '/detection/status', function(statusData) {
              console.log('📊 Current status:', statusData);
              
              if (! statusData.running) {
                  console.warn('⚠️ Service not running, updating UI');
                  updateButtonState(false);
                  stopPolling();
                  updateSystemStatus(true, false, null);
                  
                  Swal.fire({
                      icon: 'warning',
                      title: 'Already Stopped',
                      text: 'Detection service is not running',
                      confirmButtonColor: '#ffc107'
                  });
                  $btn.prop('disabled', false);
                  $btn.html(origHtml);
                  return;
              }
              
              // ✅ ถ้ากำลังรันอยู่ → หยุด
              console.log('🛑 Stopping detection...');
              
              $.post(API_URL + '/detection/stop', function(response) {
                  console.log('📥 Stop response:', response);
                  
                  if (response.success) {
                      updateButtonState(false);
                      stopPolling();
                      stopVideoStream();                      
                      $('#zone-overlay').hide(); // ← ซ่อน SVG
                      updateSystemStatus(true, false, null);
                      Swal.fire({
                          icon: 'success',
                          title: 'Success!',
                          text: response.message,
                          confirmButtonColor: '#28a745',
                          timer: 1000, // Time in milliseconds
                          timerProgressBar: true,
                        }).then((result) => {                
                          if (result.dismiss === Swal.DismissReason.timer || result.isConfirmed) {
                              Swal.close();
                          }
                      });
                  } else {
                      console.error('❌ Stop failed:', response.message);
                      Swal.fire({
                          icon: 'error',
                          title: 'Error!',
                          text: response.message,
                          confirmButtonColor: '#dc3545',
                          timer: 1000, // Time in milliseconds
                          timerProgressBar: true,
                        }).then((result) => {                
                          if (result.dismiss === Swal.DismissReason.timer || result.isConfirmed) {
                              Swal.close();
                          }
                      });
                  }
              }).fail(function(xhr, status, error) {
                  console.error('❌ Stop request failed:', {
                      status: xhr.status,
                      responseText: xhr.responseText,
                      error: error
                  });
                  
                  Swal.fire({
                      icon: 'error',
                      title:  'Error!',
                      text: `Cannot stop detection service\n\nStatus: ${xhr.status}\nError: ${error}`,
                      confirmButtonColor: '#dc3545'
                  });
              }).always(function() {
                  // คืนค่าปุ่ม
                  $btn.prop('disabled', false);
                  $btn.html(origHtml);
                  // รีเช็คสถานะจริง
                  fetchDetectionStatus();
              });
              
          }).fail(function() {
              console.error('❌ Cannot check status');
              $btn.prop('disabled', false);
              $btn.html(origHtml);
          });
      }
  });

  // ========================================
  // 8. Helper Functions
  // ========================================
  function updateButtonState(running) {
    const $btn = $('#btn-toggle-monitor');
    isRunning = running;
    
    if (running) {
      $btn.removeClass('btn-danger').addClass('btn-success')
          .html('<i class="fas fa-stop-circle mr-2"></i> Stop Monitoring');
    } else {
      $btn.removeClass('btn-success').addClass('btn-danger')
          .html('<i class="fas fa-play-circle mr-2"></i> Start Monitoring');
    }
  }

function startPolling() {
    if (pollingTimer) return;
    
    console.log('🔄 Starting polling (Zone Monitoring)...');
    
    // ✅ Zone monitoring ไม่ต้องใช้ fetchLatestDetection
    fetchSummary();
    fetchLogs();
    fetchZoneStatus();
    
    pollingTimer = setInterval(function() {
        fetchSummary();
        fetchLogs();
        fetchZoneStatus();
    }, POLLING_INTERVAL);
}

  function stopPolling() {
    if (pollingTimer) {
      clearInterval(pollingTimer);
      pollingTimer = null;
    }
  }

  // ========================================
  // 9. Initialize on Page Load
  // - ตอนเข้าเพจให้เช็คสถานะจาก backend ก่อน (fetchDetectionStatus)
  // - ถ้า backend บอกว่ากำลังรัน จะเริ่ม poll และเติมข้อมูลหน้าอัตโนมัติ
  // - ถ้า backend ไม่รัน จะไม่เริ่ม poll (ผู้ใช้ต้องกด Start)
  // ========================================
  
  // ✅ Initialize Zone Overlay
  (async function initZoneOverlay() {
      console.log('📋 Initializing Zone Overlay...');
      await loadCameraResolution();
      await loadZones();
      $(window).on('resize', drawZones);
      console.log('✅ Zone Overlay initialized');
  })();
  
  fetchDetectionStatus();  // Check if already running (will start polling if running)
  fetchSystemInfo();        // Load system info once
  // Fetch system info every 3 seconds
  setInterval(fetchSystemInfo, 3000);
});
</script>
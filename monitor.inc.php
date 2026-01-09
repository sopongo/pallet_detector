<div class="card shadow-lg">
  <div class="card-header">
    <h3 class="card-title">
      <i class="fas fa-cogs mr-2"></i> Monitoring 
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
                <div class="col-md-6">
                  <div class="detection-wrapper border bg-white p-2 mb-2">
                    <span class="badge badge-success position-absolute m-2" style="z-index:10;">Before: <span id="mock-time-before">-</span></span>
                    <div class="pallet-image-container position-relative">
                      <img id="img-before" src="dist/img/before.png" class="img-fluid rounded border" alt="Before">
                      
                      <!--<div class="ai-box mock-box-1" style="top: 60%; left: 15%; width: 15%; height: 20%;">
                        <span class="ai-label-tag badge badge-danger">PL-001</span>
                      </div>
                      <div class="ai-box mock-box-2" style="top: 45%; left: 35%; width: 15%; height: 20%;">
                        <span class="ai-label-tag badge badge-danger">PL-002</span>
                      </div>-->
                    </div>
                    <div class="mt-2 text-xs text-muted">
                      File: <span id="file-before">-</span>
                    </div>
                  </div>
                </div>
                
                <div class="col-md-6">
                  <div class="detection-wrapper border bg-white p-2 mb-2">
                    <span class="badge badge-primary position-absolute m-2" style="z-index:10;">After: <span id="mock-time-after">-</span></span>
                    <div class="pallet-image-container position-relative">
                      <img id="img-after" src="dist/img/after.png" class="img-fluid rounded border" alt="After">
                      
                      <!---<div class="ai-box mock-box-3" style="top: 45%; left: 35%; width: 15%; height: 20%;">
                        <span class="ai-label-tag badge badge-danger">PL-002</span>
                      </div>
                      <div class="ai-box mock-box-4" style="top: 48%; left: 55%; width: 15%; height: 20%;">
                        <span class="ai-label-tag badge badge-danger">PL-003</span>
                      </div>-->
                    </div>
                    <div class="mt-2 text-xs text-muted">
                      File: <span id="file-after">-</span>
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
                  <tr><td><b>Confidence:</b></td><td class="text-right text-info font-weight-bold">-</td></tr>
                  <tr><td><b>IoU Threshold:</b></td><td class="text-right text-info font-weight-bold">-</td></tr>
                  <tr><td><b>Image Size:</b></td><td class="text-right">-</td></tr>
                  <tr><td><b>Interval take photo:</b></td><td class="text-right">-</td></tr>
                  <tr><td><b>Alert Threshold:</b></td><td class="text-right text-danger">-</td></tr>
                  <tr><td><b>Alignment Tolerance:</b></td><td class="text-right">-</td></tr> <!-- ปิดการแสดงผลชั่วคราว รอแก้ backend รองรับ-->
                  <tr><td><b>Mode:</b></td><td class="text-right text-success"><i class="fas fa-microchip mr-1"></i> -</td></tr>
                  <tr><td><b>Ram:</b></td><td class="text-right text-success"><i class="fas fa-memory mr-1"></i> -</td></tr>
                  <tr><td><b>Temp box enclosure:</b></td><td class="text-right">- <sup>°C</sup></td></tr>
                </tbody>
              </table>
            </div>
          </div>
          

        </div> </div> </div> </div> </div> 
        
<style type="text/css">
  .pallet-image-container { background: #eaeaea; min-height: 250px; display: flex; align-items: center; justify-content: center; overflow: hidden; position: relative; }
    .ai-box { position: absolute; border: 2px solid #ff0000; pointer-events: none; box-shadow: 0 0 8px rgba(255, 0, 0, 0.6); border-radius: 2px; z-index: 5; }
  .ai-label-tag { position: absolute; top: -24px; left: -2px; font-size: 11px !important; padding: 2px 6px !important; border-radius: 3px 3px 0 0 !important; background-color: rgba(220, 53, 69, 0.95) !important; font-weight: bold; color: #fff; }
    #log-container { height: 130px; overflow-y: auto; background: #1e1e1e; color: #00ff00; 
      /*font-family: 'Courier New', monospace; */
      font-family: Arial, Helvetica, sans-serif;
      padding: 12px; font-size: 13px; }
    .detection-wrapper img { width: 100%; transition: opacity 0.5s ease; }
    /* ✅ เพิ่ม style สำหรับ log error (สีแดง) */
    .log-error { color: #ff4444 !important; font-weight: bold; }
    .log-warning { color: #ffaa00 !important; }
</style>

<script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/bootstrap@4.6.1/dist/js/bootstrap.bundle.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<!-- SweetAlert2 CDN -->
<script src="https://cdn.jsdelivr.net/npm/sweetalert2@11"></script>

<script type="text/javascript">
$(function () {
// ========================================
// API Base URL / Configuration
// ========================================
// ✅ Auto-detect hostname (works on any device)
const API_URL = `http://${window.location.hostname}:5000/api`;
const POLLING_INTERVAL = 3000;

// Debug: แสดง API_URL ที่ใช้
console.log('🔗 API_URL:', API_URL);
  
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
            fetchLatestDetection();
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
  function fetchLatestDetection() {
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
  }

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
  // ========================================
  function fetchSystemInfo() {
    $.get(API_URL + '/system/info', function(data) {
      if (data.success) {
        // Update system info table
        $('table.table-sm tbody tr:eq(0) td:last').text(data.working_hours);
        $('table.table-sm tbody tr:eq(1) td:last').text(data.confidence);
        $('table.table-sm tbody tr:eq(2) td:last').text(data.iou_threshold);
        $('table.table-sm tbody tr:eq(3) td:last').text(data.image_size);
        $('table.table-sm tbody tr:eq(4) td:last').text(data.interval);
        $('table.table-sm tbody tr:eq(5) td:last').text(data.alert_threshold);
        $('table.table-sm tbody tr:eq(6) td:last').text(data.alignment_tolerance);
        $('table.table-sm tbody tr:eq(7) td:last').html('<i class="fas fa-microchip mr-1"></i> ' + data.device_mode + ' Mode (Used: ' + data.cpu_usage + ')');
        $('table.table-sm tbody tr:eq(8) td:last').html('<i class="fas fa-memory mr-1"></i> ' + data.ram_total + ' (Used: ' + data.ram_usage + ')');
        $('table.table-sm tbody tr:eq(9) td:last').text(data.temperature);
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
                  startPolling();
                  updateSystemStatus(true, true, response.pid); // อัพเดต status และ PID
                  Swal.fire({
                      icon: 'success',
                      title:  'Success!',
                      text: response.message,
                      confirmButtonColor: '#28a745'
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
                      updateSystemStatus(true, false, null);
                      Swal.fire({
                          icon: 'success',
                          title: 'Success!',
                          text: response.message,
                          confirmButtonColor: '#28a745'
                      });
                  } else {
                      console.error('❌ Stop failed:', response.message);
                      Swal.fire({
                          icon: 'error',
                          title: 'Error!',
                          text: response.message,
                          confirmButtonColor: '#dc3545'
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
    
    // Fetch immediately
    fetchLatestDetection();
    fetchSummary();
    fetchLogs();
    
    // Then poll every 3 seconds
    pollingTimer = setInterval(function() {
      fetchLatestDetection();
      fetchSummary();
      fetchLogs();
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
  fetchDetectionStatus();  // Check if already running (will start polling if running)
  fetchSystemInfo();        // Load system info once
  // Fetch system info every 3 seconds
  setInterval(fetchSystemInfo, 3000);
});
</script>
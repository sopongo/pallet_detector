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
              <h3 class="card-title"><i class="fas fa-desktop mr-2"></i> Live Detection (CAM 0) - Building 1</h3>
            </div>
            <div class="card-body bg-gray-light">
              <div class="row">
                <div class="col-md-6">
                  <div class="detection-wrapper border bg-white p-2 mb-2">
                    <span class="badge badge-secondary position-absolute m-2" style="z-index:10;">Before: <span id="mock-time-before">24/12/2025 15:00:00</span></span>
                    <div class="pallet-image-container position-relative">
                      <img id="img-before" src="dist/img/pallet_071.jpg" class="img-fluid rounded border" alt="Before">
                      
                      <div class="ai-box mock-box-1" style="top: 60%; left: 15%; width: 15%; height: 20%;">
                        <span class="ai-label-tag badge badge-danger">PL-001</span>
                      </div>
                      <div class="ai-box mock-box-2" style="top: 45%; left: 35%; width: 15%; height: 20%;">
                        <span class="ai-label-tag badge badge-danger">PL-002</span>
                      </div>
                    </div>
                    <div class="mt-2 text-xs text-muted">
                      File: <span id="file-before">IMG20251224_150000.jpg</span> | Result: 4 Pallets
                    </div>
                  </div>
                </div>
                
                <div class="col-md-6">
                  <div class="detection-wrapper border bg-white p-2 mb-2">
                    <span class="badge badge-primary position-absolute m-2" style="z-index:10;">After: <span id="mock-time-after">24/12/2025 15:10:00</span></span>
                    <div class="pallet-image-container position-relative">
                      <img id="img-after" src="dist/img/pallet_070.jpg" class="img-fluid rounded border" alt="After">
                      
                      <div class="ai-box mock-box-3" style="top: 45%; left: 35%; width: 15%; height: 20%;">
                        <span class="ai-label-tag badge badge-danger">PL-002</span>
                      </div>
                      <div class="ai-box mock-box-4" style="top: 48%; left: 55%; width: 15%; height: 20%;">
                        <span class="ai-label-tag badge badge-danger">PL-003</span>
                      </div>
                    </div>
                    <div class="mt-2 text-xs text-muted">
                      File: <span id="file-after">IMG20251224_151000.jpg</span> | Result: 2 Pallets
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <div class="card-footer py-2 border-top">
               <small class="text-muted">
                 <i class="fas fa-network-wired text-success mr-1"></i> Status: Online (Home_WiFi) | 
                 <i class="fas fa-database ml-3 mr-1"></i> Storage: 274 Mb (1,452 Files)
               </small>
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
              <h3 class="card-title text-bold">Detect Summary (<?PHP echo date("d/m/Y");?>)</h3>
            </div>
            <div class="card-body p-0">
              <ul class="list-group list-group-flush">
                <li class="list-group-item pt-2 pb-2"><b>Site:</b> <span class="float-right">PACJ</span></li>
                <li class="list-group-item pt-2 pb-2"><b>Location:</b> <span class="float-right">Building 1</span></li>
                <li class="list-group-item pt-2 pb-2 text-primary"><b>Total Photos:</b> <span class="float-right text-bold">45</span></li>
                <li class="list-group-item pt-2 pb-2"><b>Total Detected:</b> <span class="float-right text-bold">154</span></li>
                <li class="list-group-item pt-2 pb-2 text-success"><b>Pallet In Time:</b> <span class="float-right text-bold">130</span></li>
                <li class="list-group-item pt-2 pb-2 text-danger"><b>Pallet Over Time:</b> <span class="float-right text-bold">24</span></li>
                <li class="list-group-item pt-2 pb-2 text-purple" style="color: #6f42c1 !important;"><b>Notifications:</b> <span class="float-right text-bold">31</span></li>
              </ul>
            </div>
            <div class="card-footer p-2 bg-white border-top-0">
                <button id="btn-toggle-monitor" class="btn btn-lg btn-danger btn-block text-bold shadow">
                  <i class="fas fa-play-circle mr-2"></i> Start Monitoring
                </button>
            </div>
          </div>

          <div class="card card-outline card-info shadow-sm mt-3">
            <div class="card-header py-2">
              <h3 class="card-title text-sm text-bold"><i class="fas fa-sliders-h mr-2"></i> System Information</h3>
            </div>
            <div class="card-body p-0">
              <table class="table table-sm table-striped mb-0 text-sm">
                <tbody>
                  <tr><td><b>Working time Detection:</b></td><td class="text-right">08.00 - 18.00</td></tr>
                  <tr><td><b>Confidence:</b></td><td class="text-right text-info font-weight-bold">0.77</td></tr>
                  <tr><td><b>IoU Threshold:</b></td><td class="text-right text-info font-weight-bold">0.60</td></tr>
                  <tr><td><b>Image Size:</b></td><td class="text-right">1280px</td></tr>
                  <tr><td><b>Interval take photo:</b></td><td class="text-right">600s (10m)</td></tr>
                  <tr><td><b>Alert Threshold:</b></td><td class="text-right text-danger">15m</td></tr>
                  <tr><td><b>Mode:</b></td><td class="text-right text-success"><i class="fas fa-microchip mr-1"></i> CPU Mode (Used: 75%)</td></tr>
                  <tr><td><b>Ram:</b></td><td class="text-right text-success"><i class="fas fa-memory mr-1"></i> 16 GB (Used: 68%)</td></tr>
                  <tr><td><b>Temp box enclosure:</b></td><td class="text-right">8.74 <sup>°C</sup></td></tr>
                </tbody>
              </table>
            </div>
          </div>
          

        </div> </div> </div> </div> </div> 
        
<style type="text/css">
  .pallet-image-container { background: #000; min-height: 250px; display: flex; align-items: center; justify-content: center; overflow: hidden; position: relative; }
    .ai-box { position: absolute; border: 2px solid #ff0000; pointer-events: none; box-shadow: 0 0 8px rgba(255, 0, 0, 0.6); border-radius: 2px; z-index: 5; }
    .ai-label-tag { position: absolute; top: -24px; left: -2px; font-size: 11px !important; padding: 2px 6px !important; border-radius: 3px 3px 0 0 !important; background-color: rgba(220, 53, 69, 0.95) !important; font-weight: bold; color: #fff; }
    #log-container { height: 130px; overflow-y: auto; background: #1e1e1e; color: #00ff00; 
      /*font-family: 'Courier New', monospace; */
      font-family: Arial, Helvetica, sans-serif;
      padding: 12px; font-size: 13px; }
    .detection-wrapper img { width: 100%; transition: opacity 0.5s ease; }
</style>

<script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/bootstrap@4.6.1/dist/js/bootstrap.bundle.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

<script type="text/javascript">
$(function () {
  // --- 1. Global Variables for Mockup ---
  const mockImages = [
    'dist/img/pallet_070.jpg', 'dist/img/pallet_071.jpg', 'dist/img/pallet_072.jpg',
    'dist/img/pallet_073.jpg', 'dist/img/pallet_074.jpg', 'dist/img/pallet_075.jpg', 'dist/img/pallet_076.jpg'
  ];
  const mockLogs = [
    "Capturing photo from CAM 0...",
    "Sending frame to YOLOv8 inference engine...",
    "Detected 4 pallets (PL-001, PL-002, PL-003, PL-004)",
    "Comparison complete: No movement detected.",
    "Updating status to Dashboard database...",
    "Heartbeat: Camera online, storage 85% free.",
    "Detection result: 1 pallet approaching Alert Threshold."
  ];
  
  let isRunning = false;
  let logTimer, imgTimer;

  // --- 2. Requirement 1: Real-time Header Clock ---
  function updateHeaderClock() {
    const now = new Date();
    // ใช้ 'en-GB' เพื่อให้ได้รูปแบบ วัน/เดือน/ปี ค.ศ.
    const formatted = now.toLocaleString('en-GB', { 
      day: '2-digit', 
      month: '2-digit', 
      year: 'numeric',
      hour: '2-digit', 
      minute: '2-digit', 
      second: '2-digit', 
      hour12: false
    }).replace(',', '');
    $('#header-clock').text(formatted);
  }
  setInterval(updateHeaderClock, 1000);


  // --- 4. Mockup Functions (Log Feed & Image Swap) ---
  
  function addMockLog() {
    const now = new Date();
    const timeStr = now.getHours().toString().padStart(2, '0') + ":" + 
                    now.getMinutes().toString().padStart(2, '0') + ":" + 
                    now.getSeconds().toString().padStart(2, '0');
    const msg = mockLogs[Math.floor(Math.random() * mockLogs.length)];
    const logHtml = `<div><span class="text-white">[${timeStr}]</span> : ${msg}</div>`;
    
    if($('#log-container .text-muted').length) $('#log-container').empty();
    
    $('#log-container').append(logHtml);
    $('#log-container').scrollTop($('#log-container')[0].scrollHeight);
    
    // Keep logs manageable
    if ($('#log-container div').length > 30) $('#log-container div:first').remove();
  }

  function swapMockImages() {
    // Pick random images
    const bImg = mockImages[Math.floor(Math.random() * mockImages.length)];
    const aImg = mockImages[Math.floor(Math.random() * mockImages.length)];
    
    // Fade effect for images
    $('#img-before, #img-after').css('opacity', '0.3');
    
    setTimeout(() => {
      $('#img-before').attr('src', bImg);
      $('#img-after').attr('src', aImg);
      $('#img-before, #img-after').css('opacity', '1');
      
      // Slightly move AI boxes to look dynamic
      $('.ai-box').each(function() {
         const newTop = (Math.random() * 40 + 20) + '%';
         const newLeft = (Math.random() * 50 + 10) + '%';
         $(this).animate({ top: newTop, left: newLeft }, 600);
      });
    }, 500);
  }

  // --- 5. Requirement 3: Toggle Start/Stop Button ---
  $('#btn-toggle-monitor').click(function() {
    const $btn = $(this);
    if (!isRunning) {
      // START
      isRunning = true;
      $btn.removeClass('btn-danger').addClass('btn-success')
          .html('<i class="fas fa-stop-circle mr-2"></i> Stop Monitoring');
      
      logTimer = setInterval(addMockLog, 2500);   // Feed log every 2.5s
      imgTimer = setInterval(swapMockImages, 3000); // Swap image every 3s
      addMockLog(); // Trigger once immediately
    } else {
      // STOP
      isRunning = false;
      $btn.removeClass('btn-success').addClass('btn-danger')
          .html('<i class="fas fa-play-circle mr-2"></i> Start Monitoring');
      
      clearInterval(logTimer);
      clearInterval(imgTimer);
    }
  });
});
</script>
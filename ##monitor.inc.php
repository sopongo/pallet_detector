<div class="card">
  <div class="card-header">
    <h3 class="card-title">
      <i class="fas fa-cogs mr-2"></i> Monitoring 
      (Date: <span id="header-clock">24/12/2025 15:12:13</span>)
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
                    <span class="badge badge-secondary position-absolute m-2" style="z-index:10;">Before: 24/12/2025 15:00:00</span>
                    <div class="pallet-image-container position-relative">
                      <img src="dist/img/pallet_071.jpg" class="img-fluid rounded border" alt="Before">
                      <div class="ai-box" style="top: 60%; left: 15%; width: 15%; height: 20%;">
                        <span class="ai-label-tag badge badge-danger">PL-001</span>
                      </div>
                      <div class="ai-box" style="top: 45%; left: 35%; width: 15%; height: 20%;">
                        <span class="ai-label-tag badge badge-danger">PL-002</span>
                      </div>
                    </div>
                    <div class="mt-2 text-xs text-muted">
                      File: IMG20251224_150000.jpg | Result: 4 Pallets
                    </div>
                  </div>
                </div>
                
                <div class="col-md-6">
                  <div class="detection-wrapper border bg-white p-2 mb-2">
                    <span class="badge badge-primary position-absolute m-2" style="z-index:10;">After: 24/12/2025 15:10:00</span>
                    <div class="pallet-image-container position-relative">
                      <img src="dist/img/pallet_070.jpg" class="img-fluid rounded border" alt="After">
                      <div class="ai-box" style="top: 45%; left: 35%; width: 15%; height: 20%;">
                        <span class="ai-label-tag badge badge-danger">PL-002</span>
                      </div>
                      <div class="ai-box" style="top: 48%; left: 55%; width: 15%; height: 20%;">
                        <span class="ai-label-tag badge badge-danger">PL-003</span>
                      </div>
                    </div>
                    <div class="mt-2 text-xs text-muted">
                      File: IMG20251224_151000.jpg | Result: 2 Pallets
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <div class="card-footer py-2">
               <small class="text-muted">
                 <i class="fas fa-network-wired text-success mr-1"></i> Status: Online (Home_WiFi) | 
                 <i class="fas fa-database ml-3 mr-1"></i> Storage: 274 Mb (1,452 Files)
               </small>
            </div>
          </div>

          <div class="card card-outline card-secondary shadow-sm">
            <div class="card-header py-2">
              <h3 class="card-title text-sm font-weight-bold"><i class="fas fa-list-ul mr-2"></i> System Logs</h3>
            </div>
            <div class="card-body p-0">
              <div id="log-container" style="height: 120px; overflow-y: auto; background: #1e1e1e; color: #00ff00; font-family: 'Courier New', Courier, monospace; padding: 10px; font-size: 13px;">
                <div>[2025-12-25 15:48:50] : Take photo... Done.</div>
                <div>[2025-12-25 15:48:55] : Processing Image with YOLOv8...</div>
                <div>[2025-12-25 15:48:59] : Detection Pallet... Found 3 Pallets.</div>
                <div>[2025-12-25 15:49:05] : Comparing Before/After... No Over-time detected.</div>
                <div>[2025-12-25 15:50:00] : Waiting for next interval (600s)...</div>
              </div>
            </div>
          </div>

        </div> <div class="col-md-3">
          
          <div class="card card-gray-dark card-outline shadow">
            <div class="card-header">
              <h3 class="card-title text-bold">Detect Summary (24/12/2025)</h3>
            </div>
            <div class="card-body p-0">
              <ul class="list-group list-group-flush">
                <li class="list-group-item"><b>Site:</b> <span class="float-right">PACJ</span></li>
                <li class="list-group-item"><b>Location:</b> <span class="float-right">Building 1</span></li>
                <li class="list-group-item text-primary"><b>Total Photos:</b> <span class="float-right text-bold">45</span></li>
                <li class="list-group-item"><b>Total Detected:</b> <span class="float-right text-bold">154</span></li>
                <li class="list-group-item text-success"><b>Pallet In Time:</b> <span class="float-right text-bold">130</span></li>
                <li class="list-group-item text-danger"><b>Pallet Over Time:</b> <span class="float-right text-bold">24</span></li>
                <li class="list-group-item text-purple"><b>Notifications:</b> <span class="float-right text-bold">31</span></li>
              </ul>
            </div>
            <div class="card-footer p-2">
                <button id="btn-toggle-monitor" class="btn btn-lg btn-danger btn-block text-bold shadow">
                  <i class="fas fa-play-circle mr-2"></i> Start Monitoring
                </button>
            </div>
          </div>

          <div class="card card-outline card-gray-dark shadow-sm">
            <div class="card-header py-2">
              <h3 class="card-title text-sm text-bold"><i class="fas fa-sliders-h mr-2"></i> System Info</h3>
            </div>
            <div class="card-body p-0">
              <table class="table table-sm table-striped mb-0 text-sm">
                <tbody>
                  <tr><td><b>Model:</b></td><td class="text-right">YOLOv8 v.35</td></tr>
                  <tr><td><b>Conf:</b></td><td class="text-right text-info">0.77</td></tr>
                  <tr><td><b>IoU:</b></td><td class="text-right text-info">0.60</td></tr>
                  <tr><td><b>Size:</b></td><td class="text-right">1280px</td></tr>
                  <tr><td><b>Interval:</b></td><td class="text-right">600s (10m)</td></tr>
                  <tr><td><b>Alert:</b></td><td class="text-right text-danger">15m</td></tr>
                  <tr><td><b>Mode:</b></td><td class="text-right text-success"><i class="fas fa-microchip mr-1"></i> CPU Mode (Used: 75%)</td></tr>
                  <tr><td><b>Ram:</b></td><td class="text-right text-success"><i class="fas fa-memory mr-1"></i> 16 GB (Used: 68%)</td></tr>
                </tbody>
              </table>
            </div>
          </div>
          

        </div> </div> </div> </div> </div> <style>
  .pallet-image-container { overflow: hidden; }
  .ai-box {
    position: absolute;
    border: 2px solid #ff0000;
    pointer-events: none;
    box-shadow: 0 0 5px rgba(255, 0, 0, 0.5);
    border-radius: 2px;
  }
  .ai-label-tag {
    position: absolute;
    top: -22px;
    left: -2px;
    font-size: 10px !important;
    padding: 2px 5px !important;
    border-radius: 2px 2px 0 0 !important;
    background-color: rgba(220, 53, 69, 0.9) !important;
  }
  #log-container div {
    margin-bottom: 2px;
    line-height: 1.4;
  }
</style>

<script type="text/javascript">
$(function () {
  // Requirement 1: Real-time Header Clock
  function updateClock() {
    const now = new Date();
    const formatted = now.toLocaleString('th-TH', { 
      day: '2-digit', month: '2-digit', year: 'numeric',
      hour: '2-digit', minute: '2-digit', second: '2-digit'
    });
    $('#header-clock').text(formatted);
  }
  setInterval(updateClock, 1000);

  // Requirement 3: Toggle Button Logic
  $('#btn-toggle-monitor').click(function() {
    $(this).toggleClass('btn-danger btn-success');
    const isActive = $(this).hasClass('btn-success');
    $(this).html(isActive ? '<i class="fas fa-stop-circle mr-2"></i> Stop Monitoring' : '<i class="fas fa-play-circle mr-2"></i> Start Monitoring');
  });

  // Sidebar Donut Chart
  var sideCtx = $('#sideDonut').get(0).getContext('2d');
  new Chart(sideCtx, {
    type: 'doughnut',
    data: {
      labels: ['In Time', 'Over Time'],
      datasets: [{
        data: [130, 24],
        backgroundColor: ['#28a745', '#dc3545'],
      }]
    },
    options: {
      maintainAspectRatio: false,
      legend: { display: false },
      cutoutPercentage: 70
    }
  });

  // Auto-scroll Log to bottom
  const logDiv = document.getElementById('log-container');
  logDiv.scrollTop = logDiv.scrollHeight;
});
</script>
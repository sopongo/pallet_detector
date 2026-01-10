<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/daterangepicker/daterangepicker.css">

<div class="card shadow">
    <div class="card-header">
        <h3 class="card-title">
            <i class="fas fa-chart-line"></i> Detection Performance Analysis</h3>
        <div class="card-tools">
            <div class="input-group input-group-sm">
                <select class="form-control mr-2" id="viewMode" style="width: 120px; border-radius: 4px;">
                    <option value="hourly">Hourly</option>
                    <option value="daily" selected>Daily</option>
                    <option value="monthly">Monthly</option>
                    <option value="yearly">Yearly</option>
                </select>
    <button type="button" class="btn btn-default btn-sm mr-2" id="daterange-btn">
        <i class="far fa-calendar-alt mr-1"></i>
        <span>Select Date Range</span>
        <i class="fas fa-caret-down ml-1"></i>
    </button>
   
            </div>
        </div>
    </div>

    <div class="card-body p-0 pb-3">
      <div class="content-header">
        <div class="container-fluid">
          <div class="row">
            <div class="col-sm-6">
              <h4 class="text-muted"><i class="fas fa-map-marker-alt"></i> Site: <?php echo $_SESSION['siteName']; ?> <i class="fas fas fa-angle-double-right text-sm"></i> <i class="fas fa-industry"></i> <?php echo $_SESSION['locationName']; ?></h4>
            </div>
          </div>
        </div>
      </div>

            <div class="card card-outline card-primary m-auto mb-4" style="max-width: 98%;">
              <div class="card-header">
                <h3 class="card-title"><i class="far fa-chart-bar mr-1"></i> Detail</h3>
              </div>
              <div class="card-body">

        <div class="row">
            <div class="col-md-8 border-right">
                <p class="text-center"><strong>Performance Trend</strong></p>
                <div class="chart">
                    <canvas id="performanceChart" style="min-height: 350px; height: 350px; max-height: 400px; max-width: 100%;"></canvas>
                </div>
            </div>

            <div class="col-md-4">
                <p class="text-center"><strong>Pallet Status Distribution</strong></p>
                <div class="chart-responsive">
                    <canvas id="distributionChart" style="min-height: 250px; height: 250px; max-height: 250px;"></canvas>
                </div>
                
                <div class="mt-4 px-2">
                    <div class="info-box mb-2 bg-light shadow-sm">
                        <span class="info-box-icon text-success"><i class="fas fa-clock"></i></span>
                        <div class="info-box-content">
                            <span class="info-box-text text-sm">Avg. Processing Time</span>
                            <span class="info-box-number" id="stat-avg-time">18.5 Min</span>
                        </div>
                    </div>
                    <div class="mt-3">
                        <h6><i class="fas fa-info-circle text-info"></i> Insight:</h6>
                        <p class="text-muted text-sm" id="insight-text">
                            The data is being displayed in a daily format. The average detection rate is within the normal range.
                        </p>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <div class="card-footer bg-white border-top">
        <div class="row">
            <div class="col-sm-3 col-6 border-right">
                <div class="description-block">
                    <span class="description-percentage text-primary"><i class="fas fa-caret-up"></i> Total</span>
                    <h5 class="description-header text-xl" id="stat-total-move">0</h5>
                    <span class="description-text text-sm">WH TOTAL MOVEMENTS</span>
                </div>
            </div>
            <div class="col-sm-3 col-6 border-right">
                <div class="description-block">
                    <span class="description-percentage text-dark"><i class="fas fa-box"></i> Detected</span>
                    <h5 class="description-header text-xl" id="stat-detected">0</h5>
                    <span class="description-text text-sm">PALLETS DETECTED</span>
                </div>
            </div>
            <div class="col-sm-3 col-6 border-right">
                <div class="description-block">
                    <span class="description-percentage text-success"><i class="fas fa-percent"></i> Accuracy</span>
                    <h5 class="description-header text-xl" id="stat-rate">0%</h5>
                    <span class="description-text text-sm">DETECTION RATE</span>
                </div>
            </div>
            <div class="col-sm-3 col-6">
                <div class="description-block">
                    <span class="description-percentage text-warning"><i class="fas fa-bell"></i> Alerts</span>
                    <h5 class="description-header text-xl" id="stat-alerts">0</h5>
                    <span class="description-text text-sm">TOTAL NOTIFICATIONS</span>
                </div>
            </div>
        </div>
    </div>

              </div><!-- /.card-body -->
            </div><!-- /.card -->




</div>

<script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/moment/moment.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/daterangepicker/daterangepicker.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/chart.js@2.9.4"></script>
<script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-datalabels@0.7.0"></script>

<script>
// ใช้ jQuery แบบปลอดภัยเพื่อป้องกันความขัดแย้งกับ Library อื่น
(function($) {
    $(document).ready(function() {
        
        // ตรวจสอบก่อนว่า daterangepicker พร้อมใช้งานหรือไม่
        if (typeof $.fn.daterangepicker !== 'function') {
            console.error("Daterangepicker library is missing! Please check script sequence.");
            return; 
        }

        // --- 1. MOCK DATA (Data Store) ---
        // --- 1. CONFIGURATION & MOCK DATA (Updated with Monthly & Yearly) ---
        const mockDataStore = {
            hourly: {
                labels: ['08:00', '09:00', '10:00', '11:00', '12:00', '13:00', '14:00', '15:00', '16:00', '17:00'],
                detected: [8, 7, 6, 3, 4, 8, 7, 10, 9, 8],
                movements: [22, 28, 35, 20, 12, 25, 20, 18, 35, 20],
                inTime: 60, 
                overTime: 10, 
                alerts: 13
            },
            daily: {
                labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
                detected: [85, 92, 78, 110, 105, 45, 30],
                movements: [210, 230, 195, 280, 260, 95, 80],
                inTime: 475, 
                overTime: 70, 
                alerts: 45
            },
            // ข้อมูลรายเดือน (ย้อนหลัง 12 เดือน)
            monthly: {
                labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
                detected: [1250, 1100, 1420, 1300, 1550, 1400, 1350, 1600, 1480, 1520, 1380, 1200],
                movements: [3200, 2900, 3500, 3100, 3800, 3400, 3300, 4000, 3600, 3700, 3300, 3000],
                inTime: 14200, // ผลรวมทั้งปี (In Time)
                overTime: 2550, // ผลรวมทั้งปี (Over Time)
                alerts: 840     // ผลรวมการแจ้งเตือนทั้งปี
            },
            // ข้อมูลรายปี (ย้อนหลัง 4 ปี)
            yearly: {
                labels: ['2022', '2023', '2024', '2025'],
                detected: [14500, 16200, 17800, 18500],
                movements: [38000, 41000, 44500, 46000],
                inTime: 58500,  // ผลรวมสะสม
                overTime: 8500,  // ผลรวมสะสม
                alerts: 3200    // ผลรวมสะสม
            }
        };

        let perfChart, distChart;

        // --- 2. INITIALIZE CHARTS ---
        function initCharts() {
            const perfCtx = document.getElementById('performanceChart').getContext('2d');
            perfChart = new Chart(perfCtx, {
                type: 'bar',
                data: {
                    datasets: [
                        { 
                          data: [],
                          label: 'Detected Pallets', 
                          backgroundColor: '#004085',  
                          datalabels: {
                            align: 'end',
                            anchor: 'end',
                            backgroundColor: '#EEEEEE',
                            color: '#000080',
                            offset: 4
                          }
                        },
                        { 
                          label: 'Total Movements', 
                          type: 'line', 
                          borderColor: '#dc3545', 
                          fill: false, 
                          data: [],
                          datalabels: {
                            align: 'middle',
                            color: '#FF0000',
                            backgroundColor: 'rgba(255,255,255,0.9)',
                            display: true 
                          }
                        }
                    ]
                },
                options: {
                    maintainAspectRatio: false,
                    scales: { yAxes: [{ ticks: { beginAtZero: true } }] }
                }
            });

            const distCtx = document.getElementById('distributionChart').getContext('2d');
            distChart = new Chart(distCtx, {
                type: 'doughnut',
                data: {
                    labels: ['In Time', 'Over Time'],
                    datasets: [{ backgroundColor: ['#28a745', '#dc3545'], data: [] }]
                },
                options: { maintainAspectRatio: false, cutoutPercentage: 70 }
            });
        }

        // --- 3. UPDATE FUNCTION ---
        function updateDashboard(mode) {
            const data = mockDataStore[mode] || mockDataStore.daily;
            
            perfChart.data.labels = data.labels;
            perfChart.data.datasets[0].data = data.detected;
            perfChart.data.datasets[1].data = data.movements;
            perfChart.update();

            distChart.data.datasets[0].data = [data.inTime, data.overTime];
            distChart.update();

            // คำนวณเลขสถิติ
            const totalMove = data.movements.reduce((a, b) => a + b, 0);
            const totalDetect = data.detected.reduce((a, b) => a + b, 0);
            const rate = totalMove > 0 ? ((totalDetect / totalMove) * 100).toFixed(1) : 0;

            $('#stat-total-move').text(totalMove.toLocaleString());
            $('#stat-detected').text(totalDetect.toLocaleString());
            $('#stat-rate').text(rate + '%');
            $('#stat-alerts').text(data.alerts.toLocaleString());
        }

        // --- 4. DATE RANGE PICKER INITIALIZATION ---
        $('#daterange-btn').daterangepicker({
            ranges: {
                'Today': [moment(), moment()],
                'Last 7 Days': [moment().subtract(6, 'days'), moment()],
                'This Month': [moment().startOf('month'), moment().endOf('month')]
            },
            startDate: moment().subtract(29, 'days'),
            endDate: moment()
        }, function (start, end) {
            $('#daterange-btn span').html(start.format('MMMM D, YYYY') + ' - ' + end.format('MMMM D, YYYY'));
            updateDashboard($('#viewMode').val()); 
        });

        // --- 5. START SYSTEM ---
        initCharts();
        updateDashboard('daily');

        // Event for Mode Switch
        $('#viewMode').on('change', function() {
            updateDashboard($(this).val());
        });

    });
})(jQuery);
</script>

<style>
    /* ปรับแต่งความสวยงามเพิ่มเติม */
    .description-block { margin: 10px 0; }
    .description-header { font-weight: 700; margin-bottom: 5px; }
    .card-tools select:focus { outline: none; box-shadow: none; border-color: #007bff; }
    #performanceChart { transition: all 0.5s ease; }
</style>
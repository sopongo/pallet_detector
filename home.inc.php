<style>
.sarabun-regular {
  font-family: "Sarabun", sans-serif;
  font-weight: 400;
  font-style: normal;
}

.sarabun-medium {
  font-family: "Sarabun", sans-serif;
  font-weight: 500;
  font-style: normal;
}
</style>
<?PHP
//print_r($_SESSION['admin_config']);
//print_r($_SESSION['site_config']);
//echo $_SESSION['pallet_config']['general']['siteCompany'];
//echo $_SESSION['pallet_config']['general']['siteLocation'];
//$siteName = $_SESSION['site_config'][$_SESSION['pallet_config']['general']['siteCompany']]['site_name'];
//$locationName = $_SESSION['site_config'][$_SESSION['pallet_config']['general']['siteCompany']]['location'][$_SESSION['pallet_config']['general']['siteLocation']];
/*echo "<br>Site ID: " . $siteName;
echo "<br>Location: " . $locationName;
echo '<pre>';
print_r($_SESSION['site_config']);
echo '</pre>';
echo '<pre>';
print_r($_SESSION['pallet_config']);
echo '</pre>';*/

$rowData = $obj->customSelect("SELECT 
    -- 1. Total Pallets Detected: นับจำนวนพาเลททั้งหมดของวันนี้
    COUNT(id_pallet) AS total_detected,
    -- 2. Total Pallets In Time: นับเฉพาะรายการที่ in_over = 0
    SUM(CASE WHEN in_over = 0 THEN 1 ELSE 0 END) AS total_in_time,
    -- 3. Total Pallets Over Time: นับเฉพาะรายการที่ in_over = 1
    SUM(CASE WHEN in_over = 1 THEN 1 ELSE 0 END) AS total_over_time,
    -- 4. Total Notifications Sent: รวมจำนวนครั้งที่แจ้งเตือนทั้งหมด
    -- ใช้ COALESCE เพื่อให้ถ้าไม่มีข้อมูลเลยจะแสดงเลข 0 แทนค่า NULL
    COALESCE(SUM(notify_count), 0) AS total_notifications
    FROM tb_pallet WHERE pallet_date_in >= CURDATE() AND pallet_date_in < CURDATE() + INTERVAL 1 DAY");


// 1. สร้าง Array เปล่า 24 ช่อง (0-23) เริ่มต้นด้วยเลข 0 ทั้งหมด
$data_total = array_fill(0, 24, 0);
$data_in    = array_fill(0, 24, 0);
$data_over  = array_fill(0, 24, 0);

// 2. Query ดึงข้อมูลสรุปแยกรายชั่วโมงของวันนี้
$chartData = $obj->fetchRows("SELECT 
                    HOUR(pallet_date_in) as hr, 
                    COUNT(id_pallet) as total,
                    SUM(CASE WHEN in_over = 0 THEN 1 ELSE 0 END) as in_time,
                    SUM(CASE WHEN in_over = 1 THEN 1 ELSE 0 END) as over_time
               FROM tb_pallet 
               WHERE pallet_date_in >= CURDATE()   AND pallet_date_in < CURDATE() + INTERVAL 1 DAY
               GROUP BY HOUR(pallet_date_in)
               ORDER BY hr ASC");

//echo '<pre>'; print_r($chartData); echo '</pre>';

foreach($chartData as $key=>$value){
    $h = $chartData[$key]['hr'];
    $data_total[$h] = $chartData[$key]['total'];
    $data_in[$h]    = $chartData[$key]['in_time'];
    $data_over[$h]  = $chartData[$key]['over_time'];
}

// 3. แปลงเป็น String เพื่อส่งให้ JavaScript (เช่น 0,0,5,10...)
$str_total = implode(',', $data_total);
$str_in    = implode(',', $data_in);
$str_over  = implode(',', $data_over);

/*echo '<br>--- Debug Data Arrays ---<br>';
echo '<pre>';print_r($data_total);echo '</pre>';
echo '<pre>';print_r($data_in);echo '</pre>';
echo '<pre>';print_r($data_over);echo '</pre>';
*/

// 4. ส่วนของ Doughnut (ใช้ Query เดิมจากครั้งก่อน)
$chartDoughnut = $obj->customSelect("SELECT  
SUM(CASE WHEN in_over = 0 THEN 1 ELSE 0 END) as total_in, 
SUM(CASE WHEN in_over = 1 THEN 1 ELSE 0 END) as total_over 
FROM tb_pallet WHERE pallet_date_in >= CURDATE()   AND pallet_date_in < CURDATE() + INTERVAL 1 DAY;");

$val_in = $chartDoughnut['total_in'] ?? 0;
$val_over = $chartDoughnut['total_over'] ?? 0;


// Additional metrics for the footer section
$rowDataFooter = $obj->customSelect("SELECT 
    -- 1. Moved: จำนวนที่ยกออกแล้ว
    SUM(CASE WHEN is_active = 0 THEN 1 ELSE 0 END) AS total_moved,
    -- 2. Putting away: จำนวนที่ยังวางอยู่
    SUM(CASE WHEN is_active = 1 THEN 1 ELSE 0 END) AS total_putting_away,
    -- 3. Avg. Dwell Time: เวลาแช่เฉลี่ย (นาที)
    ROUND(AVG(TIMESTAMPDIFF(MINUTE, first_detected_at, last_detected_at)), 1) AS avg_dwell_time,
    -- 4. Avg. Accuracy: ค่าความแม่นยำเฉลี่ยของวันนั้น (0.00 - 1.00)
    -- คูณ 100 เพื่อแปลงเป็นเปอร์เซ็นต์ (เช่น 0.95 -> 95.00%)
    ROUND(AVG(accuracy) * 100, 2) AS avg_accuracy
FROM tb_pallet WHERE pallet_date_in >= CURDATE()   AND pallet_date_in < CURDATE() + INTERVAL 1 DAY;");

$rowData['total_moved'] = $rowDataFooter['total_moved'] ?? 0;
$rowData['total_putting_away'] = $rowDataFooter['total_putting_away'] ?? 0;
$rowData['avg_dwell_time'] = $rowDataFooter['avg_dwell_time'] ?? 0;
$rowData['avg_accuracy'] = $rowDataFooter['avg_accuracy'] ?? 0;




// คำนวณหาค่าต่างๆ
$total_all = $rowData['total_detected'] ?? 0; // จาก Query เดิมที่คุณมี

$active_now =$obj->customSelect("SELECT COUNT(id_pallet) AS active FROM tb_pallet WHERE is_active = 1 AND pallet_date_in >= CURDATE()   AND pallet_date_in < CURDATE() + INTERVAL 1 DAY;");

$total_scans = $obj->customSelect("SELECT COUNT(id_img) AS scans FROM tb_image WHERE image_date >= CURDATE()   AND image_date < CURDATE() + INTERVAL 1 DAY;");


// คำนวณ Efficiency %
$efficiency = ($total_all > 0) ? ($rowData['total_in_time'] / $total_all) * 100 : 0;
$timeduration = 30; // นาที
// สรุป Insight Text
if($efficiency >= 90) {
    $insight_msg = " การจัดการพาเลททำได้รวดเร็วมาก";
    $status_color = "text-success";
} elseif($efficiency >= 70) {
    $insight_msg = " ประสิทธิภาพการจัดเก็บอยู่ในเกณฑ์มาตรฐาน";
    $status_color = "text-warning";
} else {
    $insight_msg = " พบพาเลทตกค้างเกิน 30 นาที สูงกว่าเกณฑ์";
    $status_color = "text-danger";
}
?>
<div class="card">
  <div class="card-header">
    <h3 class="card-title"><i class="fas fa-cogs"></i> Dashboard summary (Date: 24/12/2025)</h3>
  </div>
  <div class="card-body p-0">
    <div class="content-header">
      <div class="container-fluid">
        <div class="row">
          <div class="col-sm-6">
            <h4 class="text-muted"><i class="fas fa-map-marker-alt"></i> Site: <?php echo $_SESSION['siteName']; ?> <i class="fas fas fa-angle-double-right text-sm"></i> <i class="fas fa-industry"></i> <?php echo $_SESSION['locationName']; ?></h4>
          </div>
        </div>
      </div>
    </div>

    <section class="content">
      <div class="container-fluid">
        <div class="row">
          <div class="col-lg-3 col-6">
            <div class="small-box bg-gray">
              <div class="inner">
                <h3><?php echo $rowData['total_detected']; ?></h3> <p>Total Pallets Detected</p>
              </div>
              <div class="icon"><i class="fas fa-boxes"></i></div>
            </div>
          </div>
          <div class="col-lg-3 col-6">
            <div class="small-box bg-success">
              <div class="inner">
                <h3><?php echo $rowData['total_in_time']; ?></h3> <p>Pallets In Time</p>
              </div>
              <div class="icon"><i class="fas fa-check-circle"></i></div>
            </div>
          </div>
          <div class="col-lg-3 col-6">
            <div class="small-box bg-danger">
              <div class="inner">
                <h3><?php echo $rowData['total_over_time']; ?></h3> <p>Pallets Over Time</p>
              </div>
              <div class="icon"><i class="fas fa-exclamation-triangle"></i></div>
            </div>
          </div>
          <div class="col-lg-3 col-6">
            <div class="small-box bg-warning">
              <div class="inner">
                <h3><?php echo $rowData['total_notifications']; ?></h3> <p>Total Notifications Sent</p>
              </div>
              <div class="icon"><i class="fas fa-bell"></i></div>
            </div>
          </div>
        </div>

        <div class="row">
          <div class="col-md-8">
            <div class="card card-outline card-primary">
              <div class="card-header">
                <h3 class="card-title"><i class="far fa-chart-bar mr-1"></i> Detection Performance (Hourly)</h3>
              </div>
              <div class="card-body">
                <div class="chart">
                  <canvas id="hourlyChart" style="min-height: 300px; height: 300px; max-height: 300px; max-width: 100%;"></canvas>
                </div>
              </div>
              <div class="card-footer bg-white">
                <div class="row">
                  <div class="col-sm-3 border-right">
                    <div class="description-block">
                      <h5 class="description-header text-primary text-lg"><?php echo $rowData['avg_accuracy']; ?>%</h5> <span class="text-sm">Avg. Accuracy</span>
                    </div>
                  </div>

                  <div class="col-sm-3 border-right">
                    <div class="description-block">
                      <h5 class="description-header text-primary text-lg"><?php echo $rowData['total_moved']; ?></h5> <span class="text-sm">Moved</span>
                    </div>
                  </div>
                  <div class="col-sm-3 border-right">
                    <div class="description-block">
                      <h5 class="description-header text-gray-dark text-lg"><?php echo $rowData['total_putting_away']; ?></h5> <span class="text-sm">Putting away</span>
                    </div>
                  </div>                  
                  <div class="col-sm-3 border-right">
                    <div class="description-block">
                      <h5 class="description-header text-danger text-lg"><?php echo $rowData['avg_dwell_time']; ?> Minutes</h5> <span class="text-sm">Avg. Dwell Time</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>


          <div class="col-md-4">
            <div class="card card-outline card-danger">
              <div class="card-header">
                <h3 class="card-title"><i class="fas fa-chart-pie mr-1"></i> Time Distribution</h3>
              </div>
              <div class="card-body">
                <canvas id="distributionChart" style="min-height: 300px; height: 300px; max-height: 300px; max-width: 100%;"></canvas>
                <hr>
                <div class="mt-3">
                  <h6><i class="fas fa-info-circle text-info"></i> Insight:</h6>
                  <p class="text-sm sarabun-medium">ประสิทธิภาพการจัดเก็บอยู่ที่ <?PHP echo number_format($efficiency, 2); ?> %, <?php echo $insight_msg; ?></p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  </div>
</div>

<script src="plugins/jquery/jquery.min.js"></script>
<script src="plugins/bootstrap/js/bootstrap.bundle.min.js"></script>
<script src="plugins/chart.js/Chart.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-datalabels@0.7.0"></script>

<script type="text/javascript">
$(function () {
  // Global config for datalabels
  Chart.helpers.merge(Chart.defaults.global.plugins.datalabels, {
    display: function(context) {
      return context.dataset.data[context.dataIndex] > 0; // แสดงตัวเลขเฉพาะแท่งที่มีค่า > 0
    },
    font: { weight: 'bold', size: 10 }
  });

  // --- 1. Hourly Detection Chart (24 Hours - 3 Bars) ---
  var hourlyCtx = $('#hourlyChart').get(0).getContext('2d');
  new Chart(hourlyCtx, {
    type: 'bar',
    data: {
      labels: ['00:00','01:00','02:00','03:00','04:00','05:00','06:00','07:00','08:00','09:00','10:00','11:00','12:00','13:00','14:00','15:00','16:00','17:00','18:00','19:00','20:00','21:00','22:00','23:00'],
      datasets: [
        {
          label: 'Total Detected',
          backgroundColor: '#000080', // น้ำเงิน
          data: [<?php echo $str_total; ?>],
          datalabels: { align: 'end', anchor: 'end', color: '#000080', offset: -2 }
        },
        {
          label: 'In Time',
          backgroundColor: '#28a745', // เขียว
          data: [<?php echo $str_in; ?>],
          datalabels: { align: 'end', anchor: 'end', color: '#28a745', offset: -2 }
        },
        {
          label: 'Over Time',
          backgroundColor: '#FF0000', // แดง
          data: [<?php echo $str_over; ?>],
          datalabels: { align: 'end', anchor: 'end', color: '#FF0000', offset: -2 }
        }
      ]
    },
    options: {
      maintainAspectRatio: false,
      responsive: true,
      legend: { position: 'top' },
      scales: {
        xAxes: [{
          barPercentage: 0.8,   // ปรับความกว้างแท่ง
          categoryPercentage: 0.7 
        }],
        yAxes: [{ ticks: { beginAtZero: true } }]
      }
    }
  });

  // --- 2. Distribution Pie Chart ---
  var distCtx = $('#distributionChart').get(0).getContext('2d');
  new Chart(distCtx, {
    type: 'doughnut',
    data: {
      labels: ['In Time', 'Over Time'],
      datasets: [{
        data: [<?php echo $val_in; ?>, <?php echo $val_over; ?>],
        backgroundColor: ['#28a745', '#FF0000'],
      }]
    },
    options: {
      maintainAspectRatio: false,
      responsive: true,
      cutoutPercentage: 65,
      legend: { position: 'bottom' },
      plugins: {
        datalabels: {
          formatter: (value, ctx) => {
            let sum = 0;
            let dataArr = ctx.chart.data.datasets[0].data;
            dataArr.map(data => { sum += data; });
            let percentage = (sum > 0) ? (value * 100 / sum).toFixed(1) + "%" : "0%";
            return value + "\n(" + percentage + ")";
          }
        }
      }
    }
  });
});
</script>
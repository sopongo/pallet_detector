<?php
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
                <h3>70</h3> <p>Total Pallets Detected</p>
              </div>
              <div class="icon"><i class="fas fa-boxes"></i></div>
            </div>
          </div>
          <div class="col-lg-3 col-6">
            <div class="small-box bg-success">
              <div class="inner">
                <h3>60</h3> <p>Pallets In Time (&lt; 30m)</p>
              </div>
              <div class="icon"><i class="fas fa-check-circle"></i></div>
            </div>
          </div>
          <div class="col-lg-3 col-6">
            <div class="small-box bg-danger">
              <div class="inner">
                <h3>10</h3> <p>Pallets Over Time (&gt; 30m)</p>
              </div>
              <div class="icon"><i class="fas fa-exclamation-triangle"></i></div>
            </div>
          </div>
          <div class="col-lg-3 col-6">
            <div class="small-box bg-warning">
              <div class="inner">
                <h3>13</h3> <p>Total Notifications Sent</p>
              </div>
              <div class="icon"><i class="fas fa-bell"></i></div>
            </div>
          </div>
        </div>

        <div class="row">
          <div class="col-md-7">
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
                      <h5 class="description-header text-primary text-lg">235</h5> <span class="text-sm">WH Total Movements</span>
                    </div>
                  </div>
                  <div class="col-sm-3 border-right">
                    <div class="description-block">
                      <h5 class="description-header text-gray-dark text-lg">70</h5> <span class="text-sm">Pallets Detected</span>
                    </div>
                  </div>                  
                  <div class="col-sm-3 border-right">
                    <div class="description-block">
                      <h5 class="description-header text-danger text-lg">29.8%</h5> <span class="text-sm">Detection Rate</span>
                    </div>
                  </div>
                  <div class="col-sm-3">
                    <div class="description-block">
                      <h5 class="description-header text-lg">45</h5>
                      <span class="text-sm">Total Photos</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div class="col-md-5">
            <div class="card card-outline card-danger">
              <div class="card-header">
                <h3 class="card-title"><i class="fas fa-chart-pie mr-1"></i> Time Distribution</h3>
              </div>
              <div class="card-body">
                <canvas id="distributionChart" style="min-height: 300px; height: 300px; max-height: 300px; max-width: 100%;"></canvas>
                <hr>
                <div class="mt-3">
                  <h6><i class="fas fa-info-circle text-info"></i> Insight:</h6>
                  <p class="text-muted text-sm">
                    Current Detection Rate is <b>29.8%</b> of total warehouse movements.
                    Average alert frequency is 1.3 per over-time pallet.
                  </p>
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
    color: '#fff',
    font: { weight: 'normal', size: 11 }
  });

  // --- 1. Hourly Detection Chart ---
  var hourlyCtx = $('#hourlyChart').get(0).getContext('2d');
  new Chart(hourlyCtx, {
    type: 'bar',
    data: {
      labels: ['08:00', '09:00', '10:00', '11:00', '12:00', '13:00', '14:00', '15:00', '16:00', '17:00'],
      datasets: [
        {
          label: 'Detected Pallets',
          backgroundColor: '#000080',
          data: [8, 7, 6, 3, 4, 8, 7, 10, 9, 8],
          datalabels: {
            align: 'end',
            anchor: 'end',
            backgroundColor: '#EEEEEE',
            color: '#000080',
            offset: 4
          }
        },
        {
          label: 'WH Total Movements',
          type: 'line',
          borderColor: '#FF0000',
          pointBackgroundColor: '#9E2A3A',
          fill: false,
          data: [22, 28, 35, 20, 12, 25, 20, 18, 35, 20],
          datalabels: {
            align: 'top',
            color: '#FF0000',
            backgroundColor: 'rgba(255,255,255,0.9)',
            display: true 
          }
        }
      ]
    },
    options: {
      maintainAspectRatio: false,
      responsive: true,
      layout: { padding: { top: 5 } },
      scales: {
        yAxes: [{ ticks: { beginAtZero: true } }]
      }
    }
  });

  // --- 2. Distribution Pie Chart ---
  var distCtx = $('#distributionChart').get(0).getContext('2d');
  new Chart(distCtx, {
    type: 'doughnut',
    data: {
      labels: ['In Time (<30m)', 'Over Time (>30m)'],
      datasets: [{
        data: [60, 10], // ปรับให้รวมกันได้ 70 ตามข้อมูลจริง
        backgroundColor: ['#28a745', '#FF0000'],
      }]
    },
    options: {
      maintainAspectRatio: false,
      responsive: true,
      cutoutPercentage: 60,
      legend: { position: 'bottom' },
      plugins: {
        datalabels: {
          formatter: (value, ctx) => {
            let sum = 0;
            let dataArr = ctx.chart.data.datasets[0].data;
            dataArr.map(data => { sum += data; });
            let percentage = (value * 100 / sum).toFixed(1) + "%";
            return value + " Pallets\n(" + percentage + ")";
          },
          font: { size: 11 }
        }
      }
    }
  });
});
</script>
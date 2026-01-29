<?PHP
session_start();
ini_set('error_reporting', E_ALL);
ini_set('display_errors', true);
error_reporting(error_reporting() & ~E_NOTICE);
date_default_timezone_set('Asia/Bangkok');	

include_once('config/config.php');
require_once ('include/connect_db.inc.php');        //คอนเน็คฐานข้อมูล 
$obj = new CRUD(); ##สร้างออปเจค $obj เพื่อเรียกใช้งานคลาส,ฟังก์ชั่นต่างๆ

if(empty($_SESSION['admin_config']) || $_SESSION['admin_config'] !== 1){
  session_destroy();
  die(include_once('login.inc.php'));
}




$module = $_GET['module'] ?? '';
switch($module) {
    case 'blank':
        $include_page = 'blank.inc.php';
        break;
    case 'monitoring':
        $include_page = 'monitor.inc.php';
        break;
    case 'zone-monitoring':
        $include_page = 'zone_monitor.inc.php';
        break;
    case 'config':
        $include_page = 'config.inc.php';
        break;
    case 'system-logs':
        $include_page = 'module/system_logs/system_logs.inc.php';
        break;
    case 'pallet-logs':
        $include_page = 'module/pallet_logs/pallet_logs.inc.php';
        break;
    case 'logout':
        session_destroy();
        header('Location: ./');
        break;
    case 'dashboard':
        $include_page = 'dashboard.inc.php';
        break;
    default:
        $include_page = 'home.inc.php';
        break;
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Pallet detector | Page Name</title>

  <!-- Google Font: Source Sans Pro -->
<link rel="stylesheet" href="https://fonts.googleapis.com/css?family=Source+Sans+Pro:300,400,400i,700&display=fallback">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+Thai:wght@100..900&family=Sarabun:ital,wght@0,100;0,200;0,300;0,400;0,500;0,600;0,700;0,800;1,100;1,200;1,300;1,400;1,500;1,600;1,700;1,800&display=swap" rel="stylesheet">

  <style>
    /* ปรับแต่งเพิ่มเติมถ้าต้องการให้ Dark Mode ดูเข้มข้นขึ้น */
    .dark-mode .card {
        background-color: #000;
        color: #000;
    }

    .dark-mode .content-wrapper {
        background-color: #000;
    }
  </style>
  
  <!-- jQuery -->
<script src="plugins/jquery/jquery.min.js"></script>
<!-- Bootstrap 4 -->
<script src="plugins/bootstrap/js/bootstrap.bundle.min.js"></script>
<!-- AdminLTE App -->
<script src="dist/js/adminlte.min.js"></script>

<!-- AdminLTE for demo purposes -->
<!--<script src="dist/js/demo.js"></script>-->

<!-- Bootstrap JS -->
<!--<script src="https://cdn.jsdelivr.net/npm/bootstrap@4.6.2/dist/js/bootstrap.bundle.min.js"></script>-->

  <!-- Font Awesome -->
  <!-- <link rel="stylesheet" href="plugins/fontawesome-free/css/all.min.css">-->
    <!-- Font Awesome (Icons) -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">

  <!-- Theme style -->
  <link rel="stylesheet" href="dist/css/adminlte.css?v=1">

   <!-- Ion Slider CSS -->
<link rel="stylesheet" href="plugins/ion-rangeslider/css/ion.rangeSlider.min.css">
<!-- Ion RangeSlider JS -->
<script src="plugins/ion-rangeslider/js/ion.rangeSlider.min.js"></script>


</head>
<body class="hold-transition sidebar-mini">
<!-- Site wrapper -->
<div class="wrapper">
  <!-- Navbar -->
  <nav class="main-header navbar navbar-expand navbar-white navbar-light">
    <!-- Left navbar links -->
    <ul class="navbar-nav">
      <li class="nav-item"><a class="nav-link" data-widget="pushmenu" href="#" role="button"><i class="fas fa-bars"></i></a></li>
      <!--<li class="nav-item d-none d-sm-inline-block"><a href="./" class="nav-link">Home</a></li>-->
    </ul>

    <!-- Right navbar links -->
    <ul class="navbar-nav ml-auto">
      <li class="nav-item"><a class="nav-link" data-widget="darkmode" href="#" role="button"><i class="fas fa-moon"></i></a></li>
      <li class="nav-item"><a class="nav-link" data-widget="fullscreen" href="#" role="button"><i class="fas fa-expand-arrows-alt"></i></a></li>
    </ul>
  </nav>
  <!-- /.navbar -->

  <!-- Main Sidebar Container -->
  <aside class="main-sidebar sidebar-dark-primary elevation-4">
    <!-- Brand Logo -->
    <a href="./" class="brand-link">
      <img src="dist/img/raspberry-pi-logo.png" alt="AdminLTE Logo" class="brand-image img-circle elevation-3" style="opacity: .8">
      <span class="brand-text font-weight-light">MDES</span>
    </a>

    <!-- Sidebar -->
    <div class="sidebar">

      <!-- Sidebar Menu -->
      <nav class="mt-2">
        <ul class="nav nav-pills nav-sidebar flex-column" data-widget="treeview" role="menu" data-accordion="false">
          <!-- Add icons to the links using the .nav-icon class with font-awesome or any other icon font library -->
          <li class="nav-item">
            <a href="./" class="nav-link <?PHP echo ($module === '') ? 'active' : ''; ?>">
              <i class="nav-icon fa-solid fa-house-laptop"></i>
              <p>Home</p>
            </a>
          </li>
          <li class="nav-item">
            <a href="?module=zone-monitoring" class="nav-link <?PHP echo ($_GET['module'] ?? '') === 'zone-monitoring' ? 'active' : ''; ?>">
              <i class="nav-icon fa-solid fa-object-ungroup"></i>
              <p>Monitoring (Zone)</p>
            </a>
          </li>
          <li class="nav-item">
            <a href="?module=monitoring" class="nav-link <?PHP echo ($_GET['module'] ?? '') === 'monitoring' ? 'active' : ''; ?>">
              <i class="nav-icon fa-solid fa-camera-rotate"></i>
              <p>Monitoring</p>
            </a>
          </li>
          <li class="nav-item">
            <a href="?module=dashboard" class="nav-link <?PHP echo ($_GET['module'] ?? '') === 'dashboard' ? 'active' : ''; ?>">
              <i class="nav-icon fas fa-area-chart"></i>
              <p>Dashboard</p>
            </a>
          </li>
          <li class="nav-item">
            <a href="?module=config" class="nav-link <?PHP echo ($_GET['module'] ?? '') === 'config' ? 'active' : ''; ?>">
              <i class="nav-icon fa-solid fa-gears"></i>
              <p>Config</p>
            </a>
          </li>
          <li class="nav-item <?PHP echo in_array(($_GET['module'] ?? ''), ['pallet-logs', 'system-logs']) ? 'menu-is-opening menu-open' : ''; ?>">
            <a href="#" class="nav-link">
              <i class="nav-icon far fa-folder-open"></i>
              <p>Logs<i class="fas fa-angle-left right"></i></p>
            </a>
            <ul class="nav nav-treeview" style="display: <?PHP echo in_array(($_GET['module'] ?? ''), ['pallet-logs', 'system-logs']) ? 'block' : 'none'; ?>;">
              <li class="nav-item">
                <a href="?module=pallet-logs" class="nav-link <?php echo ($_GET['module'] ?? '') === 'pallet-logs' ? 'active' : ''; ?>">
                  <i class="far fa-file-text nav-icon"></i>
                  <p>Pallet Logs</p>
                </a>
              </li>
              <li class="nav-item">
                <a href="?module=system-logs" class="nav-link <?php echo ($_GET['module'] ?? '') === 'system-logs' ? 'active' : ''; ?>">
                  <i class="far fa-file-text nav-icon"></i>
                  <p>System Logs</p>
                </a>
              </li>
            </ul>
          </li>          
          <!---<li class="nav-item">
            <a href="?module=blank" class="nav-link">
              <i class="nav-icon fa-regular fa-file"></i>
              <p>Blank Page</p>
            </a>
          </li>---->
          <li class="nav-item">
            <a href="?module=logout" class="nav-link">
              <i class="nav-icon fas fa-sign-out-alt"></i>
              <p>Logout</p>
            </a>
          </li>          
        </ul>
      </nav>
      <!-- /.sidebar-menu -->
    </div>
    <!-- /.sidebar -->
  </aside>

  <!-- Content Wrapper. Contains page content -->
  <div class="content-wrapper">
    <!-- Content Header (Page header) -->
    <section class="content-header">

    </section>

    <!-- Main content -->
    <section class="content">

    <?PHP
        include_once($include_page);
    ?>

    </section>
    <!-- /.content -->
  </div>
  <!-- /.content-wrapper -->

  <footer class="main-footer">
    <div class="float-right d-none d-sm-block">
      <b>Version</b> 1.0.0
    </div>
    <strong>Copyright &copy; 2025-2026 <a href="https://adminlte.io">SCGJWD Cold Chain</a>.</strong> All rights reserved.
  </footer>

  <!-- Control Sidebar -->
  <aside class="control-sidebar control-sidebar-dark">
    <!-- Control sidebar content goes here -->
  </aside>
  <!-- /.control-sidebar -->
</div>
<!-- ./wrapper -->

<script>
$(function () {
  // ฟังก์ชันสลับโหมด
  function toggleDarkMode() {
    const isDark = $('body').hasClass('dark-mode');
    
    if (isDark) {
      // เปลี่ยนเป็น Light Mode
      $('body').removeClass('dark-mode');
      $('.main-header').removeClass('navbar-dark').addClass('navbar-white navbar-light');
      $('.main-sidebar').removeClass('sidebar-dark-primary').addClass('sidebar-dark-primary');
      localStorage.setItem('theme', 'light');
    } else {
      // เปลี่ยนเป็น Dark Mode
      $('body').addClass('dark-mode');
      $('.main-header').removeClass('navbar-white navbar-light').addClass('navbar-dark');
      $('.main-sidebar').removeClass('sidebar-light-primary').addClass('sidebar-dark-primary');
      localStorage.setItem('theme', 'dark');
    }
  }

  // คลิกที่ปุ่ม Moon
  $('[data-widget="darkmode"]').on('click', function (e) {
    e.preventDefault();
    toggleDarkMode();
    
    // เปลี่ยนไอคอน (Optional)
    $(this).find('i').toggleClass('fa-moon fa-sun');
  });

  // ตรวจสอบค่าที่บันทึกไว้ใน LocalStorage เมื่อโหลดหน้าเว็บ
  const savedTheme = localStorage.getItem('theme');
  if (savedTheme === 'dark') {
    // ถ้าเคยตั้งเป็น Dark ไว้ ให้เปิดทันที
    $('body').addClass('dark-mode');
    $('.main-header').removeClass('navbar-white navbar-light').addClass('navbar-dark');
    $('.main-sidebar').removeClass('sidebar-light-primary').addClass('sidebar-dark-primary');
    $('[data-widget="darkmode"] i').removeClass('fa-moon').addClass('fa-sun');
  }
});  
</script>

</body>
</html>

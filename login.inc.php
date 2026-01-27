<?PHP 
session_start();
ini_set('error_reporting', E_ALL);
ini_set('display_errors', true);
error_reporting(error_reporting() & ~E_NOTICE);
date_default_timezone_set('Asia/Bangkok');
//$_SESSION['admin_config'] = 'xxx';
//echo sha1('1234');

$_POST['action'] = $_POST['action'] ?? '';

if($_POST['action'] === 'login'){
    include_once('config/config.php');
    $pwd = $_POST['pwd'] ?? '';
    if(sha1($pwd) === $config_admin_password){
        $_SESSION['admin_config'] = 1;

        $json_site = file_get_contents($site_config);
        $_SESSION['site_config'] = json_decode($json_site, true);

        $json_pallet = file_get_contents($pallet_config);
        $_SESSION['pallet_config'] = json_decode($json_pallet, true);

        $_SESSION['siteName'] = $_SESSION['site_config'][$_SESSION['pallet_config']['general']['siteCompany']]['site_name'];
        $_SESSION['locationName'] = $_SESSION['site_config'][$_SESSION['pallet_config']['general']['siteCompany']]['location'][$_SESSION['pallet_config']['general']['siteLocation']];        

        echo 'success';
    }else{
        echo 'fail';
    }
    exit();
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Pallet Detector | Login</title>

  <!-- Google Font: Source Sans Pro -->
  <link rel="stylesheet" href="https://fonts.googleapis.com/css?family=Source+Sans+Pro:300,400,400i,700&display=fallback">
  <!-- Font Awesome -->
  <link rel="stylesheet" href="plugins/fontawesome-free/css/all.min.css">
  <!-- Theme style -->
  <link rel="stylesheet" href="dist/css/adminlte.min.css">
  <style>
    .swal2-title {
        padding: 0;
    }
    .swal2-icon{ font-size: 0.9em;}
    .swal2-html-container{ padding: 0;}
</style>
</head>
<body class="hold-transition lockscreen">
<!-- Automatic element centering -->
<div class="lockscreen-wrapper">
  <div class="lockscreen-logo">
    <a href="./"><b>Motionless detector <br /> for energy saving (MDES)</b></a>
  </div>
  <!-- User name -->
  <div class="lockscreen-name">SCGJWD Cold Chain</div>

  <!-- START LOCK SCREEN ITEM -->
  <div class="lockscreen-item">
    <!-- lockscreen image -->
    <div class="lockscreen-image">
      <img src="dist/img/raspberry-pi-logo.png" alt="User Image">
    </div>
    <!-- /.lockscreen-image -->

    <!-- lockscreen credentials (contains the form) -->
    <form class="lockscreen-credentials" method="post" enctype="multipart/form-data">
      <div class="input-group">
        <input type="password" id="pwd" name="pwd" class="form-control" placeholder="password">

        <div class="input-group-append">
          <button type="button" class="btn">
            <i class="fas fa-arrow-right text-muted"></i>
          </button>
        </div>
      </div>
    </form>
    <!-- /.lockscreen credentials -->

  </div>
  <!-- /.lockscreen-item -->
  <div class="help-block text-center">
    Enter your password to retrieve your session
  </div>
  <div class="text-center">
    <a href="login.html">Project by EN-PACJ & IT PCS</a>
  </div>
  <div class="lockscreen-footer text-center">
    Copyright &copy; 2025-2026 <b><a href="https://adminlte.io" class="text-black">SCGJWD Cold Chain</a></b><br>
    All rights reserved
  </div>
</div>
<!-- /.center -->

<!-- jQuery -->
<!--<script src="plugins/jquery/jquery.min.js"></script>-->
<script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
<!-- SweetAlert2 CDN -->
<script src="https://cdn.jsdelivr.net/npm/sweetalert2@11"></script>
<!-- Bootstrap 4 -->
<script src="plugins/bootstrap/js/bootstrap.bundle.min.js"></script>

<script type="text/javascript"> 
  $(document).ready(function(){
    $('.btn').click(function(){
      var pwd = $('#pwd').val().trim();
      if(pwd === ''){
        Swal.fire({
          width: '25%',
          icon: 'warning',
          title: 'Warning',
          confirmButtonColor: '#007bff', // Example color
          confirmButtonText: 'OK',
          text: 'Please enter your password.',
        });
        return;
      }else{
        $.ajax({
          method: 'post',
          url: 'login.inc.php',
          type: 'post',
          data: {pwd: pwd, action: 'login'},
          success: function(response){
            console.log(response);
            if(response === 'success'){
              Swal.fire({
                width: '25%',
                icon: 'success',
                title: 'Success',
                confirmButtonColor: '#007bff', // Example color
                confirmButtonText: 'OK',
                text: 'Login successful.',
                timer: 1000, // Time in milliseconds
                timerProgressBar: true,
              }).then((result) => {                
                if (result.dismiss === Swal.DismissReason.timer || result.isConfirmed) {
                    window.location.href = './';
                }
              });
            }else{
              Swal.fire({
                width: '25%',
                icon: 'error',
                title: 'Error',
                confirmButtonColor: '#007bff', // Example color
                confirmButtonText: 'OK',
                text: 'Incorrect password. Please try again.',
              });
            }
          }
        });
        //window.location.href = './';
      }
    });

  });
  
</script>

</body>
</html>

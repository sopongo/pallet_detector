<?PHP
//ajax_query_data.php   ไฟล์นี้ใช้สำหรับดึงข้อมูลกราฟจากฐานข้อมูลแบบ AJAX
session_start();
header('Content-Type: application/json');
ini_set('error_reporting', E_ALL);
ini_set('display_errors', true);
error_reporting(error_reporting() & ~E_NOTICE);
date_default_timezone_set('Asia/Bangkok');

    if(empty($_SESSION['admin_config']) || $_SESSION['admin_config'] !== 1){
        session_destroy();
        header('HTTP/1.1 403 Forbidden');
        echo json_encode(['error' => 'Unauthorized']);
        exit;
    }

include_once('config/config.php');
require_once ('include/connect_db.inc.php');        //คอนเน็คฐานข้อมูล 
$obj = new CRUD(); ##สร้างออปเจค $obj เพื่อเรียกใช้งานคลาส,ฟังก์ชั่นต่างๆ

$sqlGrouprow = $obj->fetchRows("SET sql_mode=(SELECT REPLACE(@@sql_mode,'ONLY_FULL_GROUP_BY','')); "); //คำสั่ง ONLY_FULL_GROUP_BY

$mode = $_POST['mode'] ?? 'daily';
$start_date = $_POST['start_date'] ?? date('Y-m-d');
$end_date = $_POST['end_date'] ?? date('Y-m-d');

// เงื่อนไขการเลือกช่วงเวลาแบบ Optimized (SARGable)
$where_date = "WHERE pallet_date_in >= '".$start_date." 00:00:00' AND pallet_date_in <= '".$end_date." 23:59:59'";

// --- 1. กำหนดรูปแบบกราฟตามโหมดที่เลือก ---
switch ($mode) {
    case 'hourly':
        $label_format = "DATE_FORMAT(pallet_date_in, '%H:00')";
        $group_by = "HOUR(pallet_date_in)";
        break;
    case 'monthly':
        $label_format = "DATE_FORMAT(pallet_date_in, '%b %Y')";
        $group_by = "YEAR(pallet_date_in), MONTH(pallet_date_in)";
        break;
    case 'yearly':
        $label_format = "YEAR(pallet_date_in)";
        $group_by = "YEAR(pallet_date_in)";
        break;
    default: // daily
        $label_format = "DATE_FORMAT(pallet_date_in, '%d %b')";
        $group_by = "DATE(pallet_date_in)";
        break;
}

/*echo json_encode("SELECT ".$label_format." as label,
                COUNT(id_pallet) as total,
                SUM(CASE WHEN in_over = 0 THEN 1 ELSE 0 END) as in_time,
                SUM(CASE WHEN in_over = 1 THEN 1 ELSE 0 END) as over_time
              FROM tb_pallet ".$where_date."
              GROUP BY ".$group_by." ORDER BY pallet_date_in ASC");
               exit; // DEBUG*/

// Query ข้อมูลกราฟ 3 แท่ง: Total, In Time, Over Time
$chartData = $obj->fetchRows("SELECT ".$label_format." as label,
                COUNT(id_pallet) as total,
                SUM(CASE WHEN in_over = 0 THEN 1 ELSE 0 END) as in_time,
                SUM(CASE WHEN in_over = 1 THEN 1 ELSE 0 END) as over_time
              FROM tb_pallet ".$where_date."
              GROUP BY ".$group_by." ORDER BY pallet_date_in ASC");

$chart_data = ['labels' => [], 'total' => [], 'in_time' => [], 'over_time' => []];

foreach($chartData as $row) {
    $chart_data['labels'][] = $row['label'];
    $chart_data['total'][] = (int)$row['total'];
    $chart_data['in_time'][] = (int)$row['in_time'];
    $chart_data['over_time'][] = (int)$row['over_time'];
}

// --- 2. Query ข้อมูล Summary ด้านล่าง ---
$summary = $obj->customSelect("SELECT 
    SUM(CASE WHEN is_active = 0 THEN 1 ELSE 0 END) as moved,
    SUM(CASE WHEN is_active = 1 THEN 1 ELSE 0 END) as putting_away,
    -- Dwell Time เฉลี่ย เฉพาะตัวที่ยกออกแล้ว (Moved) ตามที่คุณเลือก
    ROUND(AVG(CASE WHEN is_active = 0 THEN TIMESTAMPDIFF(MINUTE, first_detected_at, last_detected_at) END), 1) as avg_dwell,
    ROUND(AVG(accuracy) * 100, 1) as avg_acc,
    SUM(notify_count) as total_notis
FROM tb_pallet ".$where_date."");


echo json_encode([
    'chart' => $chart_data,
    'summary' => [
        'moved' => $summary['moved'] ?? 0,
        'putting_away' => $summary['putting_away'] ?? 0,
        'avg_dwell' => $summary['avg_dwell'] ?? 0,
        'avg_acc' => $summary['avg_acc'] ?? 0,
        'total_notis' => $summary['total_notis'] ?? 0
    ]
]);



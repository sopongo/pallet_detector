<?php
// config/get_locations. php
header('Content-Type:  application/json');

// ใช้ DOCUMENT_ROOT
$config_file = $_SERVER['DOCUMENT_ROOT'] . '/pallet_detector/config/config.php';

if (!file_exists($config_file)) {
    echo json_encode([
        'success' => false,
        'message' => 'Config file not found',
        'path' => $config_file,
        'document_root' => $_SERVER['DOCUMENT_ROOT']
    ]);
    exit;
}

require_once $config_file;

$site_id = isset($_GET['site_id']) ? intval($_GET['site_id']) : 0;

if ($site_id > 0 && isset($arr_site[$site_id])) {
    echo json_encode([
        'success' => true,
        'locations' => $arr_site[$site_id]['location']
    ]);
} else {
    echo json_encode([
        'success' => false,
        'message' => 'Site not found'
    ]);
}
?>
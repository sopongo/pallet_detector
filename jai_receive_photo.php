<?php
header('Content-Type: application/json');

$valid_api_key = "PiPcs@1234";

// ✅ แก้:  รองรับหลาย server
$api_key = '';
if (function_exists('getallheaders')) {
    $headers = getallheaders();
    $api_key = $headers['X-API-Key'] ?? '';
}
if (empty($api_key)) {
    $api_key = $_SERVER['HTTP_X_API_KEY'] ??  '';
}

if ($api_key !== $valid_api_key) {
    http_response_code(401);
    echo json_encode([
        "success" => false,
        "message" => "Unauthorized",
        "received_key" => $api_key  // Debug
    ]);
    exit;
}

if ($_SERVER['REQUEST_METHOD'] !== 'POST' || ! isset($_FILES['image'])) {
    http_response_code(400);
    echo json_encode(["success" => false, "message" => "Bad request"]);
    exit;
}

try {
    $date = date('Y-m-d');
    $dir = "uploads-temp/line_push/$date/";
    if (!is_dir($dir)) mkdir($dir, 0755, true);
    
    $file = $_FILES['image'];
    
    // ✅ รองรับ PNG
    $allowed = ['image/jpeg', 'image/jpg', 'image/png'];
    $finfo = finfo_open(FILEINFO_MIME_TYPE);
    $mime = finfo_file($finfo, $file['tmp_name']);
    finfo_close($finfo);
    
    if (!in_array($mime, $allowed)) {
        throw new Exception("Invalid type:  $mime");
    }
    
    if ($file['size'] > 5 * 1024 * 1024) {
        throw new Exception("File too large");
    }
    
    $name = basename($file['name']);
    $path = $dir . $name;
    
    if (! move_uploaded_file($file['tmp_name'], $path)) {
        throw new Exception("Failed to save");
    }
    
    echo json_encode([
        "success" => true,
        "url" => "https://jaiangelbot.jwdcoldchain.com/$path"
    ]);
    
} catch (Exception $e) {
    http_response_code(500);
    echo json_encode(["success" => false, "message" => $e->getMessage()]);
}
?>
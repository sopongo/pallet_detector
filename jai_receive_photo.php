<?php
header('Content-Type: application/json');

$valid_api_key = "PiPcs@1234";

// API Key check
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
        "message" => "Unauthorized"
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
    
    // สร้างโฟลเดอร์
    if (!is_dir($dir)) {
        if (!mkdir($dir, 0755, true)) {
            throw new Exception("Cannot create directory");
        }
    }
    
    $file = $_FILES['image'];
    
    // Validate file type
    $allowed = ['image/jpeg', 'image/jpg', 'image/png'];
    $finfo = finfo_open(FILEINFO_MIME_TYPE);
    $mime = finfo_file($finfo, $file['tmp_name']);
    finfo_close($finfo);
    
    if (!in_array($mime, $allowed)) {
        throw new Exception("Invalid file type:  $mime");
    }
    
    // Validate file size (max 5MB)
    if ($file['size'] > 5 * 1024 * 1024) {
        throw new Exception("File too large");
    }
    
    $name = basename($file['name']);
    $path = $dir .  $name;
    
    // ✅ เปลี่ยนเป็น file_get_contents + file_put_contents
    $content = file_get_contents($file['tmp_name']);
    if ($content === false) {
        throw new Exception("Cannot read uploaded file");
    }
    
    $result = file_put_contents($path, $content);
    if ($result === false) {
        throw new Exception("Cannot write file to:  $path");
    }
    
    // ตรวจสอบว่าไฟล์ถูกสร้างจริง
    if (!file_exists($path)) {
        throw new Exception("File not created");
    }
    
    // Success
    echo json_encode([
        "success" => true,
        "url" => "https://jaiangelbot.jwdcoldchain.com/console/$path",
        "size" => filesize($path),
        "date" => $date
    ]);
    
} catch (Exception $e) {
    http_response_code(500);
    echo json_encode([
        "success" => false,
        "message" => $e->getMessage()
    ]);
}
?>
<?php
/**
 * Image Upload Endpoint
 * รับรูปจาก Python API และบันทึกลง uploads-temp/line_push/{date}/
 */

header('Content-Type: application/json');

// ✅ API Key Authentication
$valid_api_key = "your-secret-api-key-12345";  // ⚠️ เปลี่ยนเป็น key จริง!

$headers = getallheaders();
$api_key = isset($headers['X-API-Key']) ? $headers['X-API-Key'] : '';

if ($api_key !== $valid_api_key) {
    http_response_code(401);
    echo json_encode([
        "success" => false,
        "message" => "Unauthorized: Invalid API Key"
    ]);
    exit;
}

// ✅ รับไฟล์
if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode([
        "success" => false,
        "message" => "Method not allowed"
    ]);
    exit;
}

if (!isset($_FILES['image'])) {
    http_response_code(400);
    echo json_encode([
        "success" => false,
        "message" => "No file uploaded"
    ]);
    exit;
}

try {
    // ✅ สร้างโฟลเดอร์ตามวันที่
    $date_folder = date('Y-m-d');
    $base_dir = "uploads-temp/line_push/";
    $target_dir = $base_dir . $date_folder . "/";
    
    if (!is_dir($target_dir)) {
        mkdir($target_dir, 0755, true);
    }
    
    // ✅ ตรวจสอบไฟล์
    $file = $_FILES['image'];
    $file_name = basename($file['name']);
    
    // Validate file type (เฉพาะ jpg/jpeg)
    $allowed_types = ['image/jpeg', 'image/jpg'];
    $finfo = finfo_open(FILEINFO_MIME_TYPE);
    $mime_type = finfo_file($finfo, $file['tmp_name']);
    finfo_close($finfo);
    
    if (!in_array($mime_type, $allowed_types)) {
        throw new Exception("Invalid file type. Only JPEG allowed.");
    }
    
    // Validate file size (max 5MB)
    if ($file['size'] > 5 * 1024 * 1024) {
        throw new Exception("File too large. Max 5MB allowed.");
    }
    
    // ✅ บันทึกไฟล์ (ใช้ชื่อเดิม)
    $target_file = $target_dir . $file_name;
    
    if (!move_uploaded_file($file['tmp_name'], $target_file)) {
        throw new Exception("Failed to save file");
    }
    
    // ✅ สร้าง URL
    $base_url = "https://jaiangelbot.jwdcoldchain.com/";
    $file_url = $base_url . $target_dir . $file_name;
    
    // ✅ Return success
    echo json_encode([
        "success" => true,
        "url" => $file_url,
        "message" => "File uploaded successfully",
        "filename" => $file_name,
        "size" => $file['size'],
        "date" => $date_folder
    ]);
    
} catch (Exception $e) {
    http_response_code(500);
    echo json_encode([
        "success" => false,
        "message" => $e->getMessage()
    ]);
}
?>
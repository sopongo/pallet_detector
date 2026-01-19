<?php
header('Content-Type: application/json');

$target_dir = "upload_image/";
$allowed_types = ['image/jpeg', 'image/jpg', 'image/png'];

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    echo json_encode(['success' => false, 'message' => 'Invalid request method']);
    exit;
}

if (!isset($_FILES['image'])) {
    echo json_encode(['success' => false, 'message' => 'No image uploaded']);
    exit;
}

$file = $_FILES['image'];

// Validate file type
if (!in_array($file['type'], $allowed_types)) {
    echo json_encode(['success' => false, 'message' => 'Invalid file type. Only JPEG/PNG allowed.']);
    exit;
}

// Validate file size (max 10MB)
if ($file['size'] > 10 * 1024 * 1024) {
    echo json_encode(['success' => false, 'message' => 'File too large. Max 10MB.']);
    exit;
}

// Generate filename
$date = date('d-m-Y');
$filename = "img_configzone_{$date}.jpg";
$target_file = $target_dir . $filename;

// Ensure directory exists
if (!is_dir($target_dir)) {
    mkdir($target_dir, 0755, true);
}

// Move uploaded file
if (move_uploaded_file($file['tmp_name'], $target_file)) {
    echo json_encode([
        'success' => true,
        'message' => 'Reference image uploaded successfully',
        'filepath' => $target_file,
        'filename' => $filename
    ]);
} else {
    echo json_encode(['success' => false, 'message' => 'Failed to save image']);
}
?>

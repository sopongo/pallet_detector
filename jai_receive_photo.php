<?php
// รับข้อมูลจาก API
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $target_dir = "uploads/"; // โฟลเดอร์ที่ต้องการเก็บรูป
    
    if (isset($_FILES['image'])) {
        $file_name = basename($_FILES["image"]["name"]);
        $target_file = $target_dir . date('Ymd_His') . "_" . $file_name;

        // ตรวจสอบและย้ายไฟล์จาก Temp ไปยังโฟลเดอร์ที่ต้องการ
        if (move_uploaded_file($_FILES["image"]["tmp_name"], $target_file)) {
            echo json_encode([
                "status" => "success",
                "message" => "File uploaded successfully",
                "path" => $target_file
            ]);
        } else {
            echo json_encode(["status" => "error", "message" => "Failed to move file"]);
        }
    } else {
        echo json_encode(["status" => "error", "message" => "No file uploaded"]);
    }
}
?>
<?php
// Configuration file for the Pallet Detector

$isCapturing = false;

// Debounce function to prevent rapid clicks
function debounce($callback, $delay) {
    // Logic for debounce
}

// Keeping only one event listener for the button
function setupEventListener() {
    if (document.getElementById('btnCaptureImage')) {
        document.getElementById('btnCaptureImage').addEventListener('click', function() {
            if (!$isCapturing) {
                $isCapturing = true;
                debounce(captureImageFromCamera, 300);
            }
        });
    }
}

setupEventListener();
?>
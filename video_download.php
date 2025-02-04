<?php

// The URL of the video (from which the video will be downloaded)
$video_url = $_GET['url'];// Your video URL

// Set headers to force the download and make it efficient
header('Content-Type: video/mp4');
header('Content-Disposition: attachment; filename="downloaded_video.mp4"');
header('Content-Transfer-Encoding: binary');
header('Cache-Control: no-cache');
header('Expires: 0');
header('Pragma: public');

// Open the video URL using cURL
$ch = curl_init($video_url);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true); // Get the response as a string
curl_setopt($ch, CURLOPT_FOLLOWLOCATION, true); // Follow any redirects
curl_setopt($ch, CURLOPT_USERAGENT, "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"); // Emulate a browser
curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, false); // Ignore SSL verification
curl_setopt($ch, CURLOPT_BUFFERSIZE, 8192); // Set a reasonable buffer size for streaming
curl_setopt($ch, CURLOPT_NOPROGRESS, false); // Allow cURL to show progress

// Start output buffering and download in chunks to the user
curl_setopt($ch, CURLOPT_WRITEFUNCTION, function($ch, $data) {
    echo $data; // Output the data directly to the user
    flush(); // Immediately send data to the client
    return strlen($data); // Return the number of bytes sent
});

// Execute the cURL request
curl_exec($ch);

// Check for errors
if(curl_errno($ch)) {
    echo 'Error: ' . curl_error($ch);
    exit;
}

// Close the cURL handle
curl_close($ch);

?>

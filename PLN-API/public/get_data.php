<?php

// Your obtained bearer token
$accessToken = 'eyJhbGciOiJSUzI1NiIsImtpZCI6IlNIQTI1NjpzS3dsMnlsV0VtMjVmcXhwTU40cWY4MXE2OWFFdWFyMnpLMUdhVGxjdWNZIiwidHlwIjoiSldUIn0.eyJzdWIiOiJ1c2VyIiwiZXhwIjoxNzE0NTA3NDg5LjMyMjAxNCwiaWF0IjoxNzE0NDIxMDg5LjMyMjAxNCwianRpIjoibXpTbzJxeW5MWFRweFRYTU1lYnVaT3pSS1lRTURRIiwiY2lkIjoieWl5XzQ5UGNNVmFMcElBM2gxXy1NZyIsImxpZCI6InQyX3piejBrem8wZCIsImFpZCI6InQyX3piejBrem8wZCIsImxjYSI6MTcxNDQxMTk0MTc0OCwic2NwIjoiZUp5S1Z0SlNpZ1VFQUFEX193TnpBU2MiLCJmbG8iOjl9.ojbL5YhbPQ9mQxcbcn_7fUEnTKHio7E6KQV-sBffrIlN3j8bRUSVDOgpqPBT_EBQyMQ2X0qFLZXKyq-G_ENevEdpYX8Ias4ulXlAn3kJ_rUe9gC9ZtVyOSODrdAmb8b7Vg3gsZxPRFwX-sZ7x5fTOAoP7Y-n0qsee0FPkmhyPcw1HFF9XvqoXCI5FIpwhw738lr41ea2RUgHNbcE25FxiklwvTx5bLhGg9aAyaTvqHyqCAqI7hz7c5-pq-4q7S799P7RvaTNwfHqM27F7ZhuA5b8-e58lujQEuJ4jRMuDxio3r3Mt_fKSxMThxJaIUDAfxJ5Ho1JtvHkYaNUAxGabg'; // Replace with your actual access token

// The search query parameters
$query = 'simp';
$limit = 10;
$sort = 'relevance';

// Initialize cURL session
$ch = curl_init("https://oauth.reddit.com/search?q=$query&limit=$limit&sort=$sort");

// Set the header with the bearer token
curl_setopt($ch, CURLOPT_HTTPHEADER, array('Authorization: Bearer ' . $accessToken));

// Set other cURL options
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_USERAGENT, 'PLN Test/0.1 by PLN_user1'); // Set your user agent

// Execute the cURL session
$response_raw = curl_exec($ch);
$info = curl_getinfo($ch);

// Error checking
if ($response_raw === false) {
    echo 'Curl error: ' . curl_error($ch);
} else {
    $response = json_decode($response_raw, true);
    echo '<pre>';
    print_r($response);
    echo '</pre>';
}

// Close cURL session
curl_close($ch);

// Print cURL info if needed
echo 'CURL Info:';
echo '<pre>';
print_r($info);
echo '</pre>';

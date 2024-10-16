<?php

$username = 'PLN_user1';
$password = 'plnteste';
$clientId = 'yiy_49PcMVaLpIA3h1_-Mg';
$clientSecret = '6Y4I9Rq_B1_S9SA-l1Sv5AI4pnoa3w';

$params = array(
    'grant_type' => 'password',
    'username' => $username,
    'password' => $password
);

$ch = curl_init('https://www.reddit.com/api/v1/access_token');

$authorization = base64_encode("$clientId:$clientSecret");

curl_setopt($ch, CURLOPT_HTTPHEADER, array('Authorization: Basic ' . $authorization));
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_POST, true);
curl_setopt($ch, CURLOPT_USERAGENT, 'PLN Test/0.1 by PLN_user1');
curl_setopt($ch, CURLOPT_POSTFIELDS, http_build_query($params));
curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, true); // Keep this true in production
curl_setopt($ch, CURLOPT_VERBOSE, true); // For debugging purposes

$response_raw = curl_exec($ch);
$info = curl_getinfo($ch);

if ($response_raw === false) {
    echo 'Curl error: ' . curl_error($ch);
} else {
    $response = json_decode($response_raw, true);
    echo '<pre>';
    print_r($response);
    echo '</pre>';
}

curl_close($ch);

echo 'CURL Info:';
echo '<pre>';
print_r($info);
echo '</pre>';

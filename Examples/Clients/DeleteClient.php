<?php
require '../../vendor/autoload.php';

use BrightLocal\Api;

$clientId = 1;
$api = new Api('<YOUR_API_KEY>', '<YOUR_API_SECRET>');
$response = $api->delete("/v1/clients-and-locations/clients/$clientId");
var_dump($response->getResult());
if (!empty($response->getResult()['success'])) {
    echo 'Successfully deleted client.' . PHP_EOL;
}

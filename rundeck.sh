#!/bin/bash

url="http://localhost:5000/api/jobs/summary"

response=$(curl -X POST --write-out "%{http_code}\n" --silent --output /dev/null "$url")
echo $response
if [[ $response == 200 ]];  then
    echo "result: success"
    exit 0
else
    echo "result: $response"
    echo "check /var/log/statistics/server.log for details"
    exit 1
fi

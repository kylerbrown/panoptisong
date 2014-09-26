#!/bin/bash

reset_time="12:00"

cd "$(dirname "$0")"
./panoptisong.sh

function sleep_day (){
    startTime=$(date +%s)
    endTime=$(date -d "$reset_time tomorrow" +%s)
    timeToWait=$(($endTime- $startTime))
    sleep $timeToWait
}

while :
do
    sleep_day
    ./panoptisong.sh
done

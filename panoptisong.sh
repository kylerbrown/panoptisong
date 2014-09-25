#!/bin/bash

######## global variables ########
bird_file="~/panoptisong/birds"
recordings="~/panoptisong"
mkdir -p "$recordings"
date="$(date +%y%m%d)"
experimenter="kjbrown"
room="010a"
species="zf"
lightson="18"
lightsoff="10"

global_attributes="-a experimenter=$experimenter -a room=$room -a species=$species -a lightson=$lightson -a lightsoff=$lightsoff -a datatype=1"

# jdetect params
closeperiod="3000"
closethresh="0.02"
closerate="5"

######## kill old processes ########
killall jrecord
killall jdetect
killall jackd
sleep 3

######## start jackd ########
jackd -R -d alsa -d hw:0 -r 22050 -p 2048 &
sleep 5


function record_bird {
    # starts a jdetect and jrecord session
    bird_attributes="-a bird=$bird -a box=$box -a mic_channel=$mic_channel"
    filename="${bird}_$date"
    mkdir -p "$bird"
    echo "$bird"
    cd "$bird"
    jdetect --close-period $closeperiod --close-rate $closerate --close-thresh $closethresh --name detect_$bird --in $mic_channel &#2>&1 | tee ${filename}_jdetect.log &
    sleep 1
    jrecord --name record_$bird --in $mic_channel --trig detect_${bird}:trig_out $global_attributes $bird_attributes ${filename}.arf &#2>&1 | tee ${filename}_jrecord.log &
    cd ..
}


# read file, send to record_bird function
while read line || [[ -n $line ]]; do
    if ! [[ "$line" =~ ^(#|$) ]]; then
	arr=($line)
	bird="${arr[0]}"
	box="${arr[1]}"
	mic_channel="${arr[2]}"
	record_bird
    fi
done <"$bird_file"

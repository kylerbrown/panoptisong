#!/bin/bash

######## global variables ########
date="$(date +%y%m%d)"
bird_file="/home/kjbrown/panoptisong/birds"
recordings="/home/kjbrown/recordings"

experimenter="kjbrown"
room="009"
species="zf"
lightson="18"
lightsoff="10"
global_attributes="-a experimenter=$experimenter -a room=$room -a species=$species -a lightson=$lightson -a lightsoff=$lightsoff"

# jdetect params
closeperiod="3000"
closethresh="0.02"
closerate="5"
jdetect_params="--close-period $closeperiod --close-rate $closerate --close-thresh $closethresh"


######## move to recordings folder ########
mkdir -p "$recordings"
cd "$recordings"

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
    # arguments: bird box trig_channel [other channels to record]
    local bird="$1"
    local box="$2"
    local trig_channel="$3"
    local NPosArgs=2
    local Nothers=$(( $# - NPosArgs))
    local inChannels="${@:$(( NPosArgs + 1 )):Nothers}"
    local channelstring=""
    for channel in $inChannels
    do
	channelstring="$channelstring --in $channel"
    done
    bird_attributes="-a bird=$bird -a box=$box -a trig_channel=$trig_channel"
    filename="${bird}_$date"
    mkdir -p "$bird"
    echo "$bird"
    cd "$bird"
    jdetect_string="jdetect  ${jdetect_params} --name detect_$bird --in $trig_channel"
    echo "${jdetect_string}"
    ${jdetect_string} &#2>&1 | tee ${filename}_jdetect.log &
    sleep 1
    jrecord_string="jrecord --name record_${bird} $channelstring --trig detect_${bird}:trig_out $global_attributes $bird_attributes ${filename}.arf"
    echo "${jrecord_string}"
    ${jrecord_string} &#2>&1 | tee ${filename}_jrecord.log &
    cd ..
}


# read file, send to record_bird function
while read line || [[ -n $line ]]; do
    if ! [[ "$line" =~ ^(#|$) ]]; then
	record_bird $line
    fi
done <"$bird_file"

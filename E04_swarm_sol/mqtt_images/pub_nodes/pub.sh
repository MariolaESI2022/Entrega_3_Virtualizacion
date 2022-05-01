#!/bin/sh

while true; do
    if [ $# -eq 0 ]; then
        mosquitto_pub -h brokerSvc -p 2883 -t docker/$HOSTNAME -m "default message"
    else
        mosquitto_pub -h brokerSvc -p 2883 -t docker/$HOSTNAME -m "[$HOSTNAME] $@"
    fi
    sleep 5
done

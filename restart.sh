#!/bin/bash

# I over complicated this as practice.

stop_server () {
    echo "Killing server..."
    pkill python3
}

start_server () {
    echo "Starting Server..."
    nohup python3 server.py > log.txt 2>&1 &
}

if [[ $1 == "stop" || $1 == "restart" ]]; then
    stop_server
    sleep 0.25
fi

if [[ $1 == "start" || $1 == "restart" ]]; then
    start_server
fi
    

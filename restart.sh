#!/bin/bash

echo "Killing server..."
pkill python3

echo "Restarting server..."
nohup python3 server.py > log.txt 2>&1 &
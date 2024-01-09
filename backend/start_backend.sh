#!/bin/bash

pip install -r requirements.txt
LOG_FILE="./logs"
APP_CMD="nice -n-20 /usr/bin/python3 main.py >> $LOG_FILE 2>&1 &"
pkill 'python3'
start_app() {
    eval $APP_CMD
    echo "App started"
}

start_app
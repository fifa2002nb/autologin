#!/bin/sh

APP=appLogin.py
BASE_DIR=/Users/yexu/dev/fastorz
running=`ps aux|grep $APP|grep -c python`

echo "`date` => check $APP alive."
if [ 0 -eq $running ];then
    echo "`date` => restart app. " 
    cd $BASE_DIR; python $APP 
fi


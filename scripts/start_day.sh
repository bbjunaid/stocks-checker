#!/usr/bin/env bash

echo "Downloading engagement file if exists"
source /Users/bilaljunaid/Dropbox/Full_Time_Jobs/code_practice/stocks/virtualenv/bin/activate
python /Users/bilaljunaid/Dropbox/Full_Time_Jobs/code_practice/stocks/download_engagement.py

echo "Flushing redis"
/usr/local/bin/redis-cli flushall

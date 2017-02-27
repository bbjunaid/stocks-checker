#!/usr/bin/env bash

# Check if gedit is running
if pgrep "redis-server" > /dev/null
then
    echo "Redis is running"
else
    echo "Starting Redis"
    /usr/local/bin/redis-server --daemonize yes || sudo redis-server /etc/redis.conf
fi

echo "Flushing redis"
/usr/local/bin/redis-cli flushall

echo "Downloading engagement file if exists"
source /Users/bilaljunaid/Dropbox/Full_Time_Jobs/code_practice/stocks/virtualenv/bin/activate
python /Users/bilaljunaid/Dropbox/Full_Time_Jobs/code_practice/stocks/download_engagement.py

#!/usr/bin/env bash

# Check if gedit is running
if pgrep "redis-server" > /dev/null
then
    echo "Redis is running"
else
    echo "Starting Redis"
    /usr/local/bin/redis-server --daemonize yes || sudo redis-server /etc/redis.conf
fi

echo `date`
source /home/ubuntu/fitzstock-checker/virtualenv/bin/activate
python /home/ubuntu/fitzstock-checker/stocks_dano.py

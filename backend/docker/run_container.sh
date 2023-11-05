#!/bin/bash
mkdir -p /dcef/cache/preprocess
mkdir -p /dcef/cache/db
mkdir -p /dcef/cache/nginx/logs
mongod --dbpath "/dcef/cache/db/" --wiredTigerCacheSizeGB 1.5 &
cd /dcef/backend/preprocess
python3.11 main_mongo.py ../../exports/ ../../cache/preprocess/
cd /dcef/backend/fastapi
python3.11 -m uvicorn app:app --host "0.0.0.0" --port 58000 --workers 1 &
echo "############################################################"
echo "# Open http://127.0.0.1:21011/ in your browser to view GUI #"
echo "############################################################"
nginx -c /dcef/backend/nginx/conf/nginx-docker.conf
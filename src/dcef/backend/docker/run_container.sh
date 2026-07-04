#!/bin/bash
mkdir -p /dcef/cache/preprocess
mkdir -p /dcef/cache/db
mongod --dbpath "/dcef/cache/db/" --wiredTigerCacheSizeGB 1.5 &
cd /dcef/backend/preprocess
python3.12 main_mongo.py docker
cd /dcef/backend/fastapi
python3.12 prod.py &
echo "############################################################"
echo "# Open http://127.0.0.1:21011/ in your browser to view GUI #"
echo "############################################################"
nginx -c /dcef/backend/nginx/conf/nginx-docker.conf
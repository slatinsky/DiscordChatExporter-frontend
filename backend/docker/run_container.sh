cd backend/preprocess
python3 main.py ../../exports/ ../../cache/
cd ../..
echo "############################################################"
echo "# Open http://127.0.0.1:21011/ in your browser to view GUI #"
echo "############################################################"
nginx -c /dcef/backend/nginx/conf/nginx-docker.conf
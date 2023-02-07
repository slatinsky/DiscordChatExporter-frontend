pushd "%~dp0"
cd backend/preprocess
start "preprocess" nodemon --exec py --ext py --ignore "temp/" "main_mongo.py" "../../exports/" "temp/"
cd ../nginx/
if not exist logs mkdir logs
if not exist temp mkdir temp
start "nginx" nginx.exe -c conf/nginx-dev.conf
cd ../../frontend
start "sveltekit" npm run dev
cd ../backend/fastapi
start "fastapi" py -m uvicorn app:app --host "0.0.0.0" --port 8000 --workers 1 --reload
cd ../mongodb
start "mongodb" mongod --dbpath "db/"
start "browser" rundll32 url.dll,FileProtocolHandler http://localhost:21012/
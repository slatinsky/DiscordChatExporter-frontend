pushd "%~dp0"
cd backend/preprocess
start "preprocess" nodemon --exec py --ext py --ignore "temp/" "main.py" "../../exports/" "temp/"
cd ../nginx/
if not exist logs mkdir logs
if not exist temp mkdir temp
start "nginx" nginx.exe -c conf/nginx-dev.conf
cd ../../frontend
start "sveltekit" npm run dev
start "browser" rundll32 url.dll,FileProtocolHandler http://localhost:7070/
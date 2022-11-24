pushd "%~dp0"
cd preprocess
start "preprocess" nodemon --exec py --ext py --ignore "temp/" "main.py"
cd ../releases/dcef/bin/nginx
start "nginx" nginx.exe -c .\conf\nginx-dev.conf
cd ../../../../frontend
start "sveltekit" npm run dev
start "browser" rundll32 url.dll,FileProtocolHandler http://localhost:7070/
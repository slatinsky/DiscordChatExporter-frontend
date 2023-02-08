pushd "%~dp0"

cd dcef/backend/mongodb
if not exist db mkdir db
start "mongodb" mongod --dbpath "db/"
cd ../../..

cd dcef/backend/nginx
if not exist logs mkdir logs
if not exist temp mkdir temp
cd ../../..
if not exist logs mkdir logs
start "nginx" ./dcef/backend/nginx/nginx.exe -c ./dcef/backend/nginx/conf/nginx-prod.conf

cd dcef/backend/fastapi
start "fastapi" fastapi.exe
cd ../../..

timeout /t 1 /nobreak >nul

cd dcef/backend/preprocess
preprocess.exe ../../../exports/ temp/
cd ../../..

timeout /t 1 /nobreak >nul
if exist "C:\Program Files\Google\Chrome\Application\chrome.exe" (
    start "" "C:\Program Files\Google\Chrome\Application\chrome.exe" --app="http://127.0.0.1:21011/" --enable-precise-memory-info
) else (
    if exist "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" (
        start "" "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" --app="http://127.0.0.1:21011/" --enable-precise-memory-info
    ) else (
        start "" rundll32 url.dll,FileProtocolHandler http://127.0.0.1:21011/
    )
)
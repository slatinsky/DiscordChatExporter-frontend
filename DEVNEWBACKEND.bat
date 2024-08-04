pushd "%~dp0"


cd backend/nginx/
if not exist logs mkdir logs
if not exist temp mkdir temp
cd ../mongodb
if not exist db mkdir db
cd ../..


start wt --maximized -d %~dp0/backend/fastapi cmd /k py rundev.py; ^
split-pane -V -d %~dp0/backend/preprocess cmd /k nodemon --exec py --ext py --ignore "temp/" "main_mongo.py" "../../exports/" "temp/"; ^
move-focus left; ^
split-pane -H -d %~dp0/newfrontend cmd /k npm run dev; ^
move-focus right; ^
split-pane -H -d %~dp0/backend/nginx cmd /k nginx.exe -c conf/nginx-dev.conf; ^
move-focus right; ^
split-pane -H  -d %~dp0/backend/mongodb cmd /k mongod --dbpath "db/"


timeout /t 5 /nobreak >nul


start "browser" rundll32 url.dll,FileProtocolHandler http://127.0.0.1:21012/
pushd "%~dp0"

@REM kill running dcef processes
taskkill /f /im dcefmongod.exe


@REM run python in venv windows
if not exist "_temp\fastapi\venv" (
    call py -m venv _temp/fastapi/venv
    call "_temp\fastapi\venv\Scripts\python.exe" -m pip install -r dcef/backend/fastapi/requirements.txt
)

if not exist "_temp\preprocess\venv" (
    call py -m venv _temp/preprocess/venv
    call "_temp\preprocess\venv\Scripts\python.exe" -m pip install -r dcef/backend/preprocess/requirements.txt
)

@REM install frontend dependencies
cd dcef\frontend
if not exist "node_modules" (
    call npm install
)
cd ..\..


@REM create required folders
if not exist logs mkdir logs
if not exist temp mkdir temp
if not exist "_temp\mongodb\" mkdir "_temp\mongodb\"

@REM start the scripts
start wt --maximized -d %~dp0\dcef\backend\fastapi cmd /k "..\..\..\_temp\fastapi\venv\Scripts\python.exe" dev.py; ^
split-pane -V -d %~dp0\dcef\backend\preprocess cmd /k nodemon -e py --ignore "__pycache__"  --exec "..\..\..\_temp\preprocess\venv\Scripts\python.exe" main_mongo.py; ^
move-focus left; ^
split-pane -H -d %~dp0\dcef\frontend cmd /k npm run dev; ^
move-focus right; ^
split-pane -H -d %~dp0 cmd /k "dcef\backend\nginx\dcefnginx.exe" -c "dcef\backend\nginx\conf\nginx-dev.conf"; ^
move-focus right; ^
split-pane -H  -d %~dp0\dcef\backend\mongodb cmd /k "dcefmongod.exe" --dbpath "..\..\..\_temp\mongodb"

timeout /t 5 /nobreak >nul

start "browser" rundll32 url.dll,FileProtocolHandler http://127.0.0.1:21012/
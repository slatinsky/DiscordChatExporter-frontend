pushd "%~dp0"

@REM delete old release
rmdir "release/dcef/" /s /q
del release\dcef.exe

@REM create folder struture
mkdir "release\exports"
mkdir "release/dcef/backend/preprocess"
mkdir "release\dcef\backend\nginx\conf\"
mkdir "release\dcef\backend\nginx\logs\"
mkdir "release\dcef\backend\nginx\temp\"
mkdir "release\dcef\backend\fastapi\"
mkdir "release\dcef\backend\http-server\"
mkdir "release\dcef\backend\mongodb\"
mkdir "release\dcef\backend\mongodb\db\"

@REM build static frontend
cd frontend
call npm run build
@echo on
cd ..
move "frontend/build" "release/dcef/frontend"


@REM Build pyinstaller
cd backend/preprocess
py -m PyInstaller main_mongo.py -F
cd ../..
copy "backend\preprocess\emojiIndex.json" "release\dcef\backend\preprocess\emojiIndex.json" /y
move "backend\preprocess\dist\main_mongo.exe" "release\dcef\backend\preprocess\preprocess.exe"
del backend\preprocess\main_mongo.spec
rmdir "backend/preprocess/dist/" /s /q
rmdir "backend/preprocess/build/" /s /q

cd backend/windows-runner
py -m PyInstaller .\windows-runner.py --onefile --icon=icon.ico --name dcef
cd ../..
move "backend\windows-runner\dist\dcef.exe" "release\dcef.exe"
del backend\windows-runner\dcef.spec
rmdir "backend/windows-runner/dist/" /s /q
rmdir "backend/windows-runner/build/" /s /q

cd backend/fastapi
py -m PyInstaller main.py -F --hidden-import "uvicorn.logging" --hidden-import "uvicorn.loops" --hidden-import "uvicorn.loops.auto" --hidden-import "uvicorn.protocols" --hidden-import "uvicorn.protocols.http" --hidden-import "uvicorn.protocols.http.auto" --hidden-import "uvicorn.protocols.websockets" --hidden-import "uvicorn.protocols.websockets.auto" --hidden-import "uvicorn.lifespan" --hidden-import "uvicorn.lifespan.on" --hidden-import "app"
cd ../..
move "backend\fastapi\dist\main.exe" "release\dcef\backend\fastapi\fastapi.exe"
del backend\fastapi\main.spec
rmdir "backend/fastapi/dist/" /s /q
rmdir "backend/fastapi/build/" /s /q


call pkg backend/http-server/node_modules/http-server/bin/http-server --target node16-win-x64
move "http-server.exe" "release\dcef\backend\http-server\http-server.exe"


@REM copy nginx
copy "backend\nginx\conf\nginx-prod.conf" "release\dcef\backend\nginx\conf\nginx-prod.conf" /y
copy "backend\nginx\conf\mime.types" "release\dcef\backend\nginx\conf\mime.types" /y
copy "backend\nginx\nginx.exe" "release\dcef\backend\nginx\nginx.exe" /y
copy "backend\mongodb\mongod.exe" "release\dcef\backend\mongodb\mongod.exe" /y
copy "backend\mongodb\msvcp140.dll" "release\dcef\backend\mongodb\msvcp140.dll" /y
copy "backend\mongodb\vcruntime140_1.dll" "release\dcef\backend\mongodb\vcruntime140_1.dll" /y

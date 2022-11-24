pushd "%~dp0"

@REM delete old release
rmdir "release/dcef/" /s /q

@REM create folder struture
mkdir "release\exports"
mkdir "release/dcef/backend/preprocess"
mkdir "release\dcef\backend\nginx\conf\"
mkdir "release\dcef\backend\nginx\logs\"
mkdir "release\dcef\backend\nginx\temp\"

@REM build static frontend
cd frontend
call npm run build
@echo on
cd ..
move "frontend/build" "release/dcef/frontend"


@REM Build pyinstaller
cd backend/preprocess
pyinstaller main.py -F
cd ../..
copy "backend\preprocess\emojiIndex.json" "release\dcef\backend\preprocess\emojiIndex.json" /y
move "backend\preprocess\dist\main.exe" "release\dcef\backend\preprocess\preprocess.exe"
del backend\preprocess\main.spec
rmdir "backend/preprocess/dist/" /s /q
rmdir "backend/preprocess/build/" /s /q

@REM copy nginx
copy "backend\nginx\conf\nginx-prod.conf" "release\dcef\backend\nginx\conf\nginx-prod.conf" /y
copy "backend\nginx\conf\mime.types" "release\dcef\backend\nginx\conf\mime.types" /y
copy "backend\nginx\nginx.exe" "release\dcef\backend\nginx\nginx.exe" /y

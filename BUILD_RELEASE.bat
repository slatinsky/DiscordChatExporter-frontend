pushd "%~dp0"
@REM Move user files outside static directory to speed up build time
move "static/input" "_temp_input"
move "static/data" "_temp_data"

@REM Relete old build
rmdir "releases/static/" /s /q
del releases\bin\preprocess.exe

@REM Build pyinstaller
cd preprocess
pyinstaller preprocess.py -F
cd ..
call pkg server/node_modules/http-server/bin/http-server --target node16-win-x64
@REM Move build to releases
move "preprocess\dist\preprocess.exe" "releases\bin\preprocess.exe"
move "http-server.exe" "releases\bin\http-server.exe"

@REM Build sveltekit frontend
call npm run build
@echo on
@REM Copy build to releases
move "build" "releases/static"

@REM Create input directory for user files
mkdir "releases\static\input"

@REM Move user files back
move "_temp_input" "static/input"
move "_temp_data" "static/data"

@REM Remove not needed files and folders
del preprocess\preprocess.spec
rmdir "preprocess/dist/" /s /q
rmdir "preprocess/build/" /s /q
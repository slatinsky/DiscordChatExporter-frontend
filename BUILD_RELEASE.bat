pushd "%~dp0"

del releases\dcef\bin\nginx\logs\access.log
del releases\dcef\bin\nginx\logs\error.log

@REM build static frontend
rmdir "releases/dcef/frontend/" /s /q
cd frontend
call npm run build
@echo on
move "build" "../releases/dcef/frontend"
cd ..


@REM Build pyinstaller
cd preprocess
pyinstaller main.py -F
cd ..
del releases\dcef\bin\preprocess.exe
copy "preprocess\emojiIndex.json" "releases\dcef\bin\emojiIndex.json" /y
move "preprocess\dist\main.exe" "releases\dcef\bin\preprocess.exe"

@REM Create input directory for user files
mkdir "releases\exports"

@REM Remove not needed files and folders
del preprocess\main.spec
rmdir "preprocess/dist/" /s /q
rmdir "preprocess/build/" /s /q
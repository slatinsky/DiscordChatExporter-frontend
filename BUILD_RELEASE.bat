pushd "%~dp0"
@REM Move user files outside build directory
move "releases/static/input" "releases/input"
move "releases/static/data" "releases/data"

@REM Relete old build
rmdir "releases/static/" /s /q
del releases\bin\preprocess.exe

@REM Build pyinstaller
cd preprocess
pyinstaller preprocess.py -F
cd ..
@REM Move build to releases
move "preprocess\dist\preprocess.exe" "releases\bin\preprocess.exe"

@REM Build sveltekit frontend
call npm run build
@echo on
@REM Copy build to releases
move "build" "releases/static"

@REM Move user files back
move "releases/input" "releases/static/input"
move "releases/data" "releases/static/data"

@REM Remove not needed files and folders
del preprocess\preprocess.spec
rmdir "preprocess/dist/" /s /q
rmdir "preprocess/build/" /s /q
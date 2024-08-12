@REM Instructions to build the release version of the application

@REM You need to have Python3 and Node.js v18.17.1+ installed on your system before running this script
@REM   Python dependencies are installed automatically in a virtual environment
@REM Tip: You can run these commands one by one to debug it if something breaks the build
@REM To remove build cache, delete the _temp folder
@REM This is a Windows builder script. For Linux, use Dockerfile located in the root directory

@REM Don't forget to install pyinstaller first:
@REM py -m pip install pyinstaller==6.10.0


@REM always start in this src directory
pushd "%~dp0"



@REM kill running dcef processes
taskkill /f /im dceffastapi.exe
taskkill /f /im dcefpreprocess.exe
taskkill /f /im dcefnginx.exe
taskkill /f /im dcefmongod.exe
taskkill /f /im dcef.exe



@REM create build artifacts folder
mkdir "_temp"

@REM install windows-runner dependencies
if not exist "_temp\dcef\venv" (
    call py -m venv _temp\dcef\venv
    call _temp\dcef\venv\Scripts\activate
    call pip install -r requirements.txt
    call deactivate
)
@REM Build windows-runner
py -m PyInstaller --onefile --name dcef       --icon "../../icon.ico"  --distpath "_temp/dcef/"       --specpath "_temp/dcef/"       --workpath "_temp/dcef/"       ./dcef.py  --paths "_temp\dcef\venv\Lib\site-packages"
del "..\release\dcef.exe"
move "_temp\dcef\dcef.exe" "..\release\dcef.exe"



@REM install preprocess dependencies
if not exist "_temp\preprocess\venv" (
    call py -m venv _temp\preprocess\venv
    call _temp\preprocess\venv\Scripts\activate
    call pip install -r dcef\backend\preprocess\requirements.txt
    call deactivate
)
@REM Build preprocess
py -m PyInstaller --onefile --name preprocess --icon "../../icon.ico"  --distpath "_temp/preprocess/" --specpath "_temp/preprocess/" --workpath "_temp/preprocess/" ./dcef/backend/preprocess/main_mongo.py --paths "_temp\preprocess\venv\Lib\site-packages"
rmdir "..\release\dcef\backend\preprocess\" /s /q
mkdir "..\release\dcef\backend\preprocess"
move "_temp\preprocess\preprocess.exe" "..\release\dcef\backend\preprocess\dcefpreprocess.exe"
copy "dcef\backend\preprocess\emojiIndex.json" "..\release\dcef\backend\preprocess\emojiIndex.json" /y


@REM install api-backend dependencies
if not exist "_temp\fastapi\venv" (
    call py -m venv _temp\fastapi\venv
    call _temp\fastapi\venv\Scripts\activate
    call pip install -r dcef\backend\fastapi\requirements.txt
    call deactivate
)
@REM build api-backend
py -m PyInstaller --onefile --name fastapi    --icon "../../icon.ico"  --distpath "_temp/fastapi/"    --specpath "_temp/fastapi/"    --workpath "_temp/fastapi/"    ./dcef/backend/fastapi/prod.py           -F --hidden-import "uvicorn.logging" --hidden-import "uvicorn.loops" --hidden-import "uvicorn.loops.auto" --hidden-import "uvicorn.protocols" --hidden-import "uvicorn.protocols.http" --hidden-import "uvicorn.protocols.http.auto" --hidden-import "uvicorn.protocols.websockets" --hidden-import "uvicorn.protocols.websockets.auto" --hidden-import "uvicorn.lifespan" --hidden-import "uvicorn.lifespan.on" --hidden-import "src.main"  --paths "_temp\fastapi\venv\Lib\site-packages"
rmdir "..\release\dcef\backend\fastapi\" /s /q
mkdir "..\release\dcef\backend\fastapi\"
mkdir "..\release\dcef\backend\fastapi\src\"
mkdir "..\release\dcef\backend\fastapi\src\search\"
copy "_temp\fastapi\fastapi.exe" "..\release\dcef\backend\fastapi\dceffastapi.exe"
copy "dcef\backend\fastapi\src\search\search_categories.json" "..\release\dcef\backend\fastapi\src\search\search_categories.json" /y



@REM static-frontend
cd dcef\frontend

@REM install static-frontend dependencies
if not exist "node_modules" (
    call npm install
)
@REM build static-frontend
call npm run build
cd ..\..
rmdir "..\release\dcef\frontend\" /s /q
move "_temp\frontend" "..\release\dcef\frontend"



@REM copy nginx
mkdir "..\release\dcef\backend\nginx\conf\"
copy "dcef\backend\nginx\conf\nginx-prod.conf" "..\release\dcef\backend\nginx\conf\nginx-prod.conf" /y
copy "dcef\backend\nginx\conf\mime.types" "..\release\dcef\backend\nginx\conf\mime.types" /y
copy "dcef\backend\nginx\dcefnginx.exe" "..\release\dcef\backend\nginx\dcefnginx.exe" /y



@REM copy mongodb
mkdir "..\release\dcef\backend\mongodb\"
mkdir "..\release\dcef\backend\mongodb\db\"
copy "dcef\backend\mongodb\dcefmongod.exe" "..\release\dcef\backend\mongodb\dcefmongod.exe" /y
copy "dcef\backend\mongodb\msvcp140.dll" "..\release\dcef\backend\mongodb\msvcp140.dll" /y
copy "dcef\backend\mongodb\vcruntime140_1.dll" "..\release\dcef\backend\mongodb\vcruntime140_1.dll" /y



@REM clean up files from old releases
rmdir "..\release\logs\" /s /q
mkdir "..\release\logs\"
rmdir "..\release\temp\" /s /q
mkdir "..\release\temp\"



@REM create exports folder
if not exist "..\release\exports" (
    mkdir "..\release\exports"
)
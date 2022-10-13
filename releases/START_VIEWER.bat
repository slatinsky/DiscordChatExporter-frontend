pushd "%~dp0"
cd bin
preprocess.exe
if exist "C:\Program Files\Google\Chrome\Application\chrome.exe" ("C:\Program Files\Google\Chrome\Application\chrome.exe" --app="http://127.0.0.1:1337/index.html") else (rundll32 url.dll,FileProtocolHandler http://127.0.0.1:1337/index.html)
binserve.exe
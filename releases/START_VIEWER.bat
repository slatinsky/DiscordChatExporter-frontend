pushd "%~dp0"
cd bin
preprocess.exe
if exist "C:\Program Files\Google\Chrome\Application\chrome.exe" ("C:\Program Files\Google\Chrome\Application\chrome.exe" --app="http://127.0.0.1:21011/index.html") else (rundll32 url.dll,FileProtocolHandler http://127.0.0.1:21011/index.html)
http-server.exe "../static" --port 21011 -c-1 --silent -P http://127.0.0.1:21011?
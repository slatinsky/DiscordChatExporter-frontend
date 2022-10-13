pushd "%~dp0"
cd bin
preprocess.exe
rundll32 url.dll,FileProtocolHandler http://127.0.0.1:1337/index.html
binserve.exe
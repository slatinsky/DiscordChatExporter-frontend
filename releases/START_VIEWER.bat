pushd "%~dp0"
cd bin
preprocess.exe
start "DiscordChatExporter-staticServer" http-server.exe "../static" --port 21011 -c-1 --silent -P http://127.0.0.1:21011?
timeout /t 1 /nobreak >nul
if exist "C:\Program Files\Google\Chrome\Application\chrome.exe" (
    start "" "C:\Program Files\Google\Chrome\Application\chrome.exe" --app="http://127.0.0.1:21011/index.html" --enable-precise-memory-info
) else (
    if exist "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" (
        start "" "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" --app="http://127.0.0.1:21011/index.html" --enable-precise-memory-info
    ) else (
        start "" rundll32 url.dll,FileProtocolHandler http://127.0.0.1:21011/index.html
    )
)
cd ..
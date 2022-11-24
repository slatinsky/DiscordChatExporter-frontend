pushd "%~dp0"
DiscordChatExporter.Cli.exe export --token TOKEN --channel CHANNEL_ID --output "exports/TEST" --format Json --media --reuse-media
cd backend/preprocess
py main.py ../../exports/ temp/
cd ../..
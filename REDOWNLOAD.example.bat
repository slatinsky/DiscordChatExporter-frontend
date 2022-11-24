pushd "%~dp0"
DiscordChatExporter.Cli.exe export --token TOKEN --channel CHANNEL_ID --output "releases/exports/TEST" --format Json --media --reuse-media
cd preprocess
py main.py
cd ..
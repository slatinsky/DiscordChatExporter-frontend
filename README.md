# DiscordChatExporter-jsonViewer
View your JSON DiscordChatExporter exports as if you were using Discord interface

## Why it was made
Tyrrrz/DiscordChatExporter is a well maintained tool to export Discord chat logs. But I felt that it was missing a few things:
- ability to view exported JSON files in a browser
- ability to merge multiple JSON exports and view them in the browser
- discord like user interface to switch between exported guilds, channels, threads
- threads support
- message lazy loading (original html export of large channel crashes the browser)

So I made this tool to fill those gaps.

# Features
- View your JSON exports as if you were using Discord interface
- Advanced message lazy loading (only messages that are visible in the viewport are loaded) - Even channels with 100k+ messages are loaded under a second
- Threads support
- In channel search


## Using prebuilt binary release
Using prebuilt binaries is the easiest way to use this tool. Builds are Windows only, because Tyrrrz/DiscordChatExporter is Windows only too.

1. Download the latest release from releases
2. Extract the archive
3. Move your exported JSON and media files (exported by Tyrrrz/DiscordChatExporter) to `/static/input/` folder (if you don't see input folder, create it). Folder structure inside doesn't matter, script will find everything it needs.
4. Run `START_VIEWER.bat` - DiscordChatExporter-jsonViewer will open in your default browser


# Building release from source
## Requirements
- Node.js 16
- Python 3.9+
- pyinstaller (installled globally)
```
py -m pip install pyinstaller
```

## Steps
1. Clone this repository
```bash
git clone URL
```
2. Install dependencies
```bash
npm install
```
3. Make sure you have Python3.9+ Node.js 16 and pyinstaller installed:
```
>py --version
Python 3.10.2
```
```
>node --version
v16.14.2
```
```
>pyinstaller --version
5.5
```

4. Kill `npm run dev` if it is running

5. Run the build script
```bash
BUILD_RELEASE.bat
```

## Tested on

```
>winver
Windows 10, 21H2
Os build: 19044.1766

>py --version
Python 3.10.2

>node --version
v16.14.2

>pyinstaller --version
5.5

Binserve version:
binserve-v0.2.0-i686-pc-windows-msvc

Processor:
AMD Ryzen™ 7 5800H

400k messages with 18GB of media files
```


But should work on any Windows 10 / Windows 11 x64 computer

# Development
This tool consists of two parts:
- Frontend - Sveltekit app
- Backend - Python3 script to preprocess JSON exports for frontend
## Preprocessor
For development make sure you have nodemon installed globally (used for hot reloading)
```
npm install -g nodemon
```

Then run
```
cd preprocessor
WATCH_DEV.bat
```

preprocess script will:
- merge JSON files by guilds
- deduplicate messages, authors and reactions to reduce used memory footprint
- pair messages with their media files
- save processed data to `/static/data/` folder. You can delete this folder at any time, original JSON files in `/static/input/` will never be changed.

After running preprocess script, don't remove `/static/input/` folder - it's needed to serve media files.

## Frontend
Run dev webserver:
```
npm run dev -- --open
```

6. If everything was done correctly, DiscordChatExporter-jsonViewer will open in your browser.




# Which JSON exports are supported?
Supported are JSON exports exported with media
```
DiscordChatExporter.Cli export --token DISCORD_TOKEN  --media True --reuse-media True --output OUTPUT_FOLDER_PATH --format Json --channel CHANNEL_OR_THREAD_ID
```

Or exported without media, but coupled with another html export with media
```
DiscordChatExporter.Cli export --token DISCORD_TOKEN --output OUTPUT_FOLDER_PATH --format Json --channel CHANNEL_OR_THREAD_ID
DiscordChatExporter.Cli export --token DISCORD_TOKEN --output OUTPUT_FOLDER_PATH --media True --reuse-media True --format HtmlDark --channel CHANNEL_OR_THREAD_ID
```

The main requirement now is that media files (`--media True --reuse-media True`) are exported.

Tested with DiscordChatExporter v2.36.1 exports

## How to view threads
- This viewer supports viewing threads, but they need to be exported by Tyrrrz/DiscordChatExporter. Export them the same way you export channels (`--channel`), but instead of CHANNEL_ID, use THREAD_ID. Because threads are channels.

## Roadmap:
- Better handling of edge cases (if something is missing in the backup)
- Support Direct messages
- Screenshots in documentation
- Message markdown rendering support
- Better GUI
- Better search (by author, by date)
- Guild-wide search
- Improve code readability
- Discord forums support

## Thanks
- Tyrrrz/DiscordChatExporter - for a great tool. Many CSS definitions from this tool are used in our viewer.
- Discord - for a great chat app
- mufeedvh/binserve - for local webserver binary
- pyinstaller - for python to binary converter

## License
GNU GENERAL PUBLIC LICENSE

included binserve binary uses MIT license

## Contributing
Feel free to open issues and pull requests.
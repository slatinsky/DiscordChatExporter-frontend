![](docs/screenshot.png)


# DiscordChatExporter-frontend
View your JSON [DiscordChatExporter](https://github.com/Tyrrrz/DiscordChatExporter) exports as if you were using Discord interface

## Features
- View JSON exports using web interface
- Message deduplication - merge multiple JSON exports and view them as if they were one
- Advanced message lazy loading and grouping (infinite scroll without pagination) - even channels with 100k+ messages are loaded almost instantly
- Threads support (go to thread, go back to channel where thread was created)
- Forums support (view forum posts as if they were threads)
- Guild search with autocomplete and filters
- View assets files locally or from remote servers
- Browse guild or direct messages
- Discord Markdown rendering support
- Command generator to extend your export with more messages (backup helper)
- Right click message and select "Open in discord" to jump to message in Discord


### System requirements (per guild)
- You will need ~1 GB of RAM to process 100k messages. So if your guild export contains 1 million messages, you will need ~10 GB of RAM.
- The viewer can handle at least ~2-4 million messages (4 GB of ram) in the browser
- Chromium based browsers are recommended (Chrome, Edge, Opera, Brave, Vivaldi, etc.)

Note: Discord servers are known internally as guilds



## Quick start (Windows)
Using prebuilt binaries is the easiest way to use this tool on Windows.
1. Download the latest release from [releases page](https://github.com/slatinsky/DiscordChatExporter-frontend/releases)
2. Extract the archive
3. Move your JSON+assets [DiscordChatExporter](https://github.com/Tyrrrz/DiscordChatExporter) exports to `/static/input/` folder ([supported exports](#supported-exports)). Folder structure inside this folder doesn't matter, script will find everything it needs.
4. Run `START_VIEWER.bat` - DiscordChatExporter-frontend will open in your default browser

## Docker version (Linux+Mac)
You need docker and git installed. Tested on non-snap version of docker on Ubuntu 22.04. @levithomason tested it on M1 MacBook (Apple Silicon) in issue [#5](https://github.com/slatinsky/DiscordChatExporter-frontend/issues/5)
1. Build image
```bash
git clone https://github.com/slatinsky/DiscordChatExporter-frontend
cd DiscordChatExporter-frontend
docker build -t dce-f .
```
2. Navigate to folder with your exports
```bash
cd [path to your exports]
```

3. Run container
```bash
docker run --volume "$(pwd):/dce-f/static/input" --volume dcef_data:/dce-f/static/data --rm -p 21011:21011 -it dce-f
```

4. Open `http://127.0.0.1:21011/` in your browser

## Upgrade guide
Want to upgrade from previous version? Follow these steps:

1. Download the latest release from [releases page](https://github.com/slatinsky/DiscordChatExporter-frontend/releases)
2. Extract the archive
3. Move your `/static/input/` folder to the new release folder. `/static/data/` folder is no longer needed.
4. Delete old release folder


<a name="supported-exports"></a>
# Which exports are supported?
The main requirement is that JSON export format (`--format Json`) is used. Archiving assets is recomended (`--media --reuse-media`), but not required. There are some examples:

Export all accessible channels from guild:
```
DiscordChatExporter.Cli.exe exportguild --token DISCORD_TOKEN -g GUILD_ID --media --reuse-media --format Json --output OUTPUT_FOLDER_PATH
```
Export all dms (sadly, exporting dms can't be done without selfboting):
```
DiscordChatExporter.Cli.exe exportdm --token DISCORD_TOKEN --media --reuse-media --format Json --output OUTPUT_FOLDER_PATH
```
Export channel:
```
DiscordChatExporter.Cli export --token DISCORD_TOKEN  --media --reuse-media --output OUTPUT_FOLDER_PATH --format Json --channel CHANNEL_OR_THREAD_ID
```
- disadvantage of export with media files is, that original URLs are not archived

<details><summary>I want to export HTML</summary>
<p>
You do not need HTML exports (you can view JSON exports in this viewer), but if you need them, they are supported too:

```
DiscordChatExporter.Cli export --token DISCORD_TOKEN --output OUTPUT_FOLDER_PATH --format Json --channel CHANNEL_OR_THREAD_ID

DiscordChatExporter.Cli export --token DISCORD_TOKEN --output OUTPUT_FOLDER_PATH --media --reuse-media --format HtmlDark --channel CHANNEL_OR_THREAD_ID
```

- disadvantage is, that thumbnails for embeds will not be working in this viewer if you export this way (workaround by html parsing is made, but it doesn't work for all embeds)

**another method**

```
DiscordChatExporter.Cli export --token DISCORD_TOKEN --output OUTPUT_FOLDER_PATH --media --reuse-media --format Json --channel CHANNEL_OR_THREAD_ID

[replace in folder name `.json_Files` to `.html_Files`]

DiscordChatExporter.Cli export --token DISCORD_TOKEN --output OUTPUT_FOLDER_PATH --media --reuse-media --format HtmlDark --channel CHANNEL_OR_THREAD_ID
```
- original URLs are not archived, but embeds will work in this viewer


</p>
</details>



## Viewing threads and forums
It is not possible to batch export threads using Tyrrrz/DiscordChatExporter. That's why I created helper tool [DiscordChatExporter-incrementalBackup](https://github.com/slatinsky/DiscordChatExporter-incrementalBackup) to do it automatically for you. And it does backups incrementally, so you don't need to export everything again if you want to extend your export.

Tool is in BETA for now. It will be better integrated into this viewer in the future.

<details><summary>I want to export threads and forums manually</summary>
<p>

## How to view threads
- This viewer supports viewing threads, but they need to be exported by [DiscordChatExporter](https://github.com/Tyrrrz/DiscordChatExporter). Export them the same way you export channels (`--channel`), but instead of CHANNEL_ID, use THREAD_ID. Because threads are channels.

Don't know how to get THREAD_IDs? Handy backup helper is included to extend your backup and to find missing threads. You can find it at the end of channel list.

**BACKUP HELPER IS DEPRECATED, BECAUSE IT IS NOT POSSIBLE TO GET ALL THREAD IDS USING THIS METHOD. YOU SHOULD USE [DiscordChatExporter-incrementalBackup](https://github.com/slatinsky/DiscordChatExporter-incrementalBackup) instead.**

![](docs/backup_helper.png)

## How to view forums
Viewing forums is supported by this viewer, but exporting them with DiscordChatExporter is harder than with other channel types, because export of main forum channel is not supported.

Workaround is to export individual forum threads. I made a script to get forum IDs automatically:

### Steps
1. Open discord in browser
2. Navigate to channel with forum post list
3. press F12 and paste this script to the console:

```js
len = 0
ids = []
previouseScrollTop = 0

function scrollToPosition(offset) {
    scrollDiv = document.querySelector('div[class*="chat-"] > div > div > div[class*="scrollerBase-"]')
    scrollDiv.scroll(0, offset)
}

function captureIds() {
    document.querySelectorAll('div[data-item-id]').forEach((e) => ids.push(e.dataset.itemId))
    ids = [...new Set(ids)]  //deduplicate
    if (ids.length > len) {
        len = ids.length
        console.log('Found', len, 'IDs')
    }
}

function printIds() {
    // print all ids, comma separated
    console.log('found IDs:',ids.join(','))
}

scrollToPosition(0)
interval = setInterval(() => {
    scrollToPosition(scrollDiv.scrollTop + window.innerHeight / 3)
    setTimeout(() => {
        captureIds()
        if (previouseScrollTop === scrollDiv.scrollTop) {
            clearInterval(interval)
            printIds()
        }
        previouseScrollTop = scrollDiv.scrollTop
    }, 1000)
}, 1542)
```

4. script will scroll the page. At the the end, it will print all IDs to the console
5. download each id with DiscordChatExporter as if you would download channel (--channel FORUM_POST_ID)
</p>
</details>

# Development
You don't need to follow development steps if you don't need to modify the code.



This tool consists of two parts:
- Frontend - Sveltekit app
- Parser - Python3 script to preprocess JSON exports for frontend
## Preprocessor
For development make sure you have nodemon installed globally (used for hot reloading)
```
nvm use 16.16.0
npm install -g nodemon
```

Then install python3 dependencies
```
py -m pip install imagesize
```

Then run
```
cd preprocessor
WATCH_DEV.bat
```

preprocess script will:
- merge JSON files by guilds
- deduplicate messages, authors and reactions to reduce used memory footprint
- pair messages with their assets
- save processed data to `/static/data/` folder. You can delete this folder at any time, original JSON files in `/static/input/` will never be changed.

After running preprocess script, don't remove `/static/input/` folder - it's needed to serve media files.

## Frontend
Run dev webserver:
```
npm run dev -- --open
```

6. If everything was done correctly, DiscordChatExporter-frontend will open in your browser.


# Building release binaries from source (Windows)
## Requirements
- Node.js 16
- Python 3.9+
- pyinstaller (installled globally)
```
py -m pip install pyinstaller
```
pkg (installed globally)
```
npm install -g pkg
```

## Steps
1. Clone this repository
```bash
git clone https://github.com/slatinsky/DiscordChatExporter-frontend
```
2. Install dependencies
```bash
npm install
cd server
npm install
cd ..
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

6. Release binaries will be in `/release/` folder



<details><summary>Tested on</summary>
<p>

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

>pkg --version
5.8.0

DiscordChatExporter version:
v2.36.1

Processor:
AMD Ryzen™ 7 5800H

400k messages with 18GB of media files
```


But should work on any Windows 10 / Windows 11 x64 computer.

</p>
</details>


## Why this tool was made
[DiscordChatExporter](https://github.com/Tyrrrz/DiscordChatExporter) is a well made tool to export Discord chats. But I felt that browsing viewing experience was not that great after threads and forums were introduced. Also you had to download them in HTML format, which made it impossible to parse like JSON format and with no ability to extend them without splitting them into multiple files - which makes it even more inconvenient to browse them.
## Thanks
- [Tyrrrz/DiscordChatExporter](https://github.com/Tyrrrz/DiscordChatExporter) - for a great tool. This project is based on some parts of it's code.
- Discord - for a great chat app
- [brussell98/discord-markdown](https://github.com/brussell98/discord-markdown) - for discord markdown rendering

And for other technologies used in this project - sveltekit, docker, nodejs, nvm, pkg, pyinstaller, http-server.


## License
GNU GENERAL PUBLIC LICENSE

## Contributing
Feel free to open issues and pull requests.

The best way to support this project is to star it here on GitHub.
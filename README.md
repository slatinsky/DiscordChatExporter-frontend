![](docs/screenshot.png)


# DiscordChatExporter-frontend
View your JSON [DiscordChatExporter](Tyrrrz/DiscordChatExporter) exports as if you were using Discord interface

## Features
- View JSON exports using web interface
- Message deduplication - merge multiple JSON exports and view them as if they were one
- Advanced message lazy loading and grouping (infinite scroll without pagination) - even channels with 100k+ messages are loaded almost instantly
- Threads support (go to thread, go back to channel where thread was created)
- Simple channel content search (because lazy loading makes it hard to use browser search)
- View media files locally



## Quick start (Windows)
Using prebuilt binaries is the easiest way to use this tool on Windows.
1. Download the latest release from [releases page](https://github.com/slatinsky/DiscordChatExporter-frontend/releases)
2. Extract the archive
3. Move your JSON+media [DiscordChatExporter](Tyrrrz/DiscordChatExporter) exports to `/static/input/` folder ([supported exports](#custom_anchor_name)). Folder structure inside this folder doesn't matter, script will find everything it needs.
4. Run `START_VIEWER.bat` - DiscordChatExporter-frontend will open in your default browser

## Linux
This tool uses Sveltekit and Python3 as main dependencies. You won't be able to run premade Windows batch scripts, but running this tool on Linux is possible. Linux support is WIP.

<a name="supported-exports"></a>
# Which exports are supported?
Supported are JSON exports exported with media. (The main disadvantage of this export type is that URLs in JSON point to local files - original URLs are not archived)
```
DiscordChatExporter.Cli export --token DISCORD_TOKEN  --media True --reuse-media True --output OUTPUT_FOLDER_PATH --format Json --channel CHANNEL_OR_THREAD_ID
```

Or exported without media, but coupled with another html export with media
```
DiscordChatExporter.Cli export --token DISCORD_TOKEN --output OUTPUT_FOLDER_PATH --format Json --channel CHANNEL_OR_THREAD_ID

DiscordChatExporter.Cli export --token DISCORD_TOKEN --output OUTPUT_FOLDER_PATH --media True --reuse-media True --format HtmlDark --channel CHANNEL_OR_THREAD_ID
```

The main requirement is that media files (`--media True --reuse-media True`) are exported and JSON export format (`--format Json`) is used.



## How to view threads
- This viewer supports viewing threads, but they need to be exported by [DiscordChatExporter](https://github.com/Tyrrrz/DiscordChatExporter). Export them the same way you export channels (`--channel`), but instead of CHANNEL_ID, use THREAD_ID. Because threads are channels.

# Development
You don't need to follow development steps if you don't need to modify the code.



This tool consists of two parts:
- Frontend - Sveltekit app
- Parser - Python3 script to preprocess JSON exports for frontend
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

6. If everything was done correctly, DiscordChatExporter-frontend will open in your browser.


# Building release binaries from source (Windows)
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

Binserve version:
binserve-v0.2.0-i686-pc-windows-msvc

DiscordChatExporter version:
v2.36.1

Processor:
AMD Ryzen™ 7 5800H

400k messages with 18GB of media files
```


But should work on any Windows 10 / Windows 11 x64 computer.

</p>
</details>







## Roadmap / planned features:
- rerun preprocess only if it is needed
- Better handling of edge cases (if something is missing in the backup)
- Support Direct messages
- Screenshots in documentation
- Message markdown rendering support
- Better GUI
- Better search (by author, by date)
- make readme easy to understand
- Guild-wide search
- Linux support (docker?)
- Improve code readability
- Discord forums support

## Why this tool was made
[DiscordChatExporter](https://github.com/Tyrrrz/DiscordChatExporter) is a well made tool to export Discord chats. But to actually view them, you had to download them in HTML format, which more inconvenient to parse than JSON. And If you wanted to extend your backup, it would be broken into multiple files, which is not very convenient.
## Thanks
- [Tyrrrz/DiscordChatExporter](https://github.com/Tyrrrz/DiscordChatExporter) - for a great tool. Many CSS definitions from this tool are used in our viewer.
- Discord - for a great chat app
- pyinstaller - for python to binary converter
- [mufeedvh/binserve](https://github.com/mufeedvh/binserve) - for local webserver binary
- [brussell98/discord-markdown](https://github.com/brussell98/discord-markdown) - for discord markdown rendering


## License
GNU GENERAL PUBLIC LICENSE

included binserve binary uses MIT license

## Contributing
Feel free to open issues and pull requests.
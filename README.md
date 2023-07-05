![](docs/screenshot.png)

# DiscordChatExporter-frontend (DCEF)
View your JSON [DiscordChatExporter](https://github.com/Tyrrrz/DiscordChatExporter) exports as if you were using Discord interface. Also supports other exporters like [Roachbones/discordless](https://github.com/Roachbones/discordless) exporting in the same JSON format as DiscordChatExporter.

## Why JSON exports are better than HTML exports?
- better-suited for long-term preservation
- contain more information than HTML exports
- readable by third-party applications like this one or [chat-analytics](https://github.com/mlomb/chat-analytics), not just browsers
- smaller in size

This project aims to provide you with better experience than what you get by just opening HTML exports in your browser. In one place and with many more features, like search, message deduplication, etc. And it will get even better in the future :).

## Features
- View JSON exports in Discord like interface
- Message deduplication - merge multiple JSON exports and view them as one
- Lazy loaded virtual list - load only messages you need to see
- Forums and threads support
- Search with filters and autocomplete
- Load assets locally or from Discord servers
- Private messages or guild exports are supported
- Discord Markdown rendering
- Right click message and select "Open in discord" to view message in Discord
- Windows and Linux support


### System requirements
- You need 1.5+ GB of free RAM for the mongodb database to work correctly
- The browser viewer has almost no requirements, but it's recommended to have at least 1 GB of free RAM
- Chromium based browsers and Firefox are supported, but most of the testing was done on Chromium.
- Small viewports (mobile phones) are not supported yet

Note: Discord servers are known internally as guilds

## Quick start (Windows)
Using prebuilt binaries is the easiest way to use this tool on Windows.

if you don't have any exports yet, you can try out the viewer with example exports included in the release. Just skip step 3.

1. Download the latest release from [releases page](https://github.com/slatinsky/DiscordChatExporter-frontend/releases)
2. Extract the archive
3. Move your [DiscordChatExporter](https://github.com/Tyrrrz/DiscordChatExporter) exports to `/exports/` folder ([supported exports](#supported-exports)). Folder structure inside this folder doesn't matter, script will find everything it needs.
4. Run `dcef.exe`

**Important:** files in exports folder may exceed Windows path length limit of 260 characters. If you have any issues with loading your assets you can choose one of the following solutions:
- move your exports to a folder with shorter path
- or run `registry_tweaks/change_260_character_path_limit_to_32767.reg` to increase the limit to 32767 characters (requires admin privileges) and restart your computer


### Beta builds (Windows)
If you want to try out the latest features, you can use [beta builds](https://github.com/slatinsky/DiscordChatExporter-frontend/actions/workflows/windows-build.yml). They are automatically built from the latest commit on `master` branch or from pull requests.

## Docker (cross-platform)
**Info**: Tested on Ubuntu 22.04 and WSL2 on Windows 10. **Not** tested on arm based systems like Raspberry Pi or Apple M1.

This verion is the best way to [host the viewer on a server](docs/Server-hosting.md) for others to use.

1. pull the image from docker hub

```bash
docker pull slada/dcef:main
```

2. Navigate to a folder with your exports

```bash
cd /path/to/your/exports
```

3. Run the container
```bash
docker run --volume "$(pwd):/dcef/exports" --volume dcef_cache:/dcef/cache --rm --name dcef -p 21011:21011 -it slada/dcef:main
```

4. Open `http://127.0.0.1:21011/` in your browser


<details><summary>Build docker image from source code</summary>
<p>

You need docker and git installed. Tested on non-snap version of docker on Ubuntu 22.04.
1. Build image

```bash
git clone https://github.com/slatinsky/DiscordChatExporter-frontend
cd DiscordChatExporter-frontend
docker build -t dcef .
```
Then use the same instructions as for the docker hub version, but replace `slada/dcef:main` with `dcef` in step 3.
</p>
</details>

<details><summary>Debugging containers</summary>
<p>

To debug a running container, run `docker exec -it $(docker ps | grep 'dcef' | awk '{ print $1 }') sh`. This will open a shell inside the container.

To remove volume `dcef_cache` with temporary files, run `docker volume rm dcef_cache`

</p>
</details>

## Upgrade guide (Windows)
Want to upgrade from previous version? Follow these steps:

1. Download the latest release from [releases page](https://github.com/slatinsky/DiscordChatExporter-frontend/releases).
2. Delete everything (except `exports` folder) in your discordchatexporter-frontend folder.
3. Move everything (except `exports` folder) from the new release to your discordchatexporter-frontend folder.

Info: since release 1.10.0, exports folder was changed from `/static/input/` to `/exports/`.


## Upgrade guide (Docker)

Stop the container and clear the cache volume by running `docker volume rm dcef_cache`. Then pull the latest version from git (`git pull`) and build the image again using linux instructions.


<a name="supported-exports"></a>
## Which exports are supported?

Exports are done by [DiscordChatExporter](https://github.com/Tyrrrz/DiscordChatExporter).

- JSON export format (`--format Json`) is required
- Including assets (`--media --reuse-media`) is highly recommended, but not required
- Skipping markdown prerendering (`--markdown false`) is highly recommended, but not required
- Don't forget to export **threads and forums**, because they **are not included in the main export** (see examples below for a guide on how to export them)

<details><summary>CLI examples</summary>
<p>

Export all accessible channels from guild:
```
DiscordChatExporter.Cli.exe exportguild --token DISCORD_TOKEN -g GUILD_ID --media --reuse-media --markdown false --format Json --output OUTPUT_FOLDER_PATH
```
Export all dms (sadly, exporting dms can't be done without selfboting):
```
DiscordChatExporter.Cli.exe exportdm --token DISCORD_TOKEN --media --reuse-media --markdown false --format Json --output OUTPUT_FOLDER_PATH
```
Export channel/thread/forum posts:
```
DiscordChatExporter.Cli export --token DISCORD_TOKEN  --media --reuse-media --markdown false --output OUTPUT_FOLDER_PATH --format Json --channel CHANNEL_OR_THREAD_ID_OR_FORUM_POST_ID_1 CHANNEL_OR_THREAD_ID_OR_FORUM_POST_ID_2 CHANNEL_OR_THREAD_ID_OR_FORUM_POST_ID_3 CHANNEL_OR_THREAD_ID_OR_FORUM_POST_ID_4
```

</p>
</details>



[Helper script to export archived threads in a channel](docs/Exporting-threads.md)

[Helper script to export forum posts in a channel](docs/Exporting-threads.md)

### Settings for GUI version of DiscordChatExporter
Make sure that export format is set to `JSON`. Optionally, you can enable `Download assets` option to download images, videos and other types of assets.

![](docs/dce-export-more.png)

**NOTE**: You can't export threads and forums using GUI version of DCE. You need to use CLI version for that.

## Development

[Architecture choices](docs/Architecture.md)

[Setting up a development environment on Windows](docs/Development-env.md)

[Compile the Windows release from source code](docs/Compile.md)

[Supporting other exporters](docs/Supporting-other-exporters.md)


## Thanks
- [Tyrrrz/DiscordChatExporter](https://github.com/Tyrrrz/DiscordChatExporter) - for a great export tool
- [brussell98/discord-markdown](https://github.com/brussell98/discord-markdown) - for discord markdown rendering library

And for other technologies used in this project - sveltekit, docker, nodejs, nvm, pyinstaller, nginx, mongodb

## License
GNU GENERAL PUBLIC LICENSE. See [LICENSE](LICENSE) for more details.

This product contains software provided by NGINX and its contributors.

DiscordChatExporter-frontend is not affiliated with Discord. Discord is a registered trademark of Discord Inc.

## Contributing
Feel free to open issues and pull requests.
### Short guide, how to contribute
- Fork the repository
- Create a new branch
- Implement your changes
- Commit and push the changes
- Create a pull request

If you find this project useful, please consider starring it here on GitHub :)
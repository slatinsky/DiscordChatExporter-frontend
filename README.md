![](docs/screenshot.png)

# DiscordChatExporter-frontend (DCEF)

Browse your [Discord chat exports](https://github.com/Tyrrrz/DiscordChatExporter) in a familiar discord like user interface. [Try a demo in your browser :)](https://dcef.slada.sk/).

> Want to chat? Join [Tyrrrz's discord server](https://discord.gg/2SUWKFnHSm). I usually hang out in `#dce-frontend` channel

## Downloads

[Windows (stable binary release)](https://github.com/slatinsky/DiscordChatExporter-frontend/releases)

[Linux (docker image)](https://hub.docker.com/r/slada/dcef)

## Quick start (Windows)

1. Download the latest release from [releases page](https://github.com/slatinsky/DiscordChatExporter-frontend/releases)
2. Extract the archive
3. Move your [DiscordChatExporter](https://github.com/Tyrrrz/DiscordChatExporter) JSON exports to `/exports/` folder ([supported exports](#supported-exports)).
4. Run `dcef.exe`

## Quick start (Linux)


Docker version is the best way to [host the viewer on a server](docs/Server-hosting.md) for others to use.

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
docker run --restart=always --volume "$(pwd):/dcef/exports" --volume dcef_cache:/dcef/cache --rm --name dcef -p 21011:21011 -it slada/dcef:main
```

4. Open `http://127.0.0.1:21011/` in your browser

**Note:** arm based systems like Raspberry Pi or Apple M1 are not officially supported. Pull requests are welcome :)


## Other ways to run DCEF

<details><summary><b>Windows beta builds</b></summary>

If you want to try out the latest features, you can use [beta builds](https://github.com/slatinsky/DiscordChatExporter-frontend/actions/workflows/windows-build.yml). They are automatically built from the latest commit on `main` branch. You need to be logged in to Github account to download them.

</details>

<details><summary><b>Build docker image from source code</b></summary>

You need docker and git installed. Then run:

```bash
git clone https://github.com/slatinsky/DiscordChatExporter-frontend
cd DiscordChatExporter-frontend
docker build -t dcef .
```
Then use the same instructions as for the Linux docker version, but replace in commands `slada/dcef:main` with `dcef`.

</details>


## Upgrade guide

<details><summary><b>Upgrade windows binary release</b></summary>

Want to upgrade from previous version? Follow these steps:

1. Download the latest release from [releases page](https://github.com/slatinsky/DiscordChatExporter-frontend/releases).
2. Delete everything (except `exports` folder) in your discordchatexporter-frontend folder.
3. Move everything (except `exports` folder) from the new release to your discordchatexporter-frontend folder.

</details>

<details><summary><b>Upgrade docker image</b></summary>

```bash
cd path/to/your/exports/
docker rm dcef --force
docker image rm slada/dcef:main
docker pull slada/dcef:main
docker run --restart=always --volume "$(pwd):/dcef/exports" --volume dcef_cache:/dcef/cache --rm --name dcef -p 21011:21011 -it slada/dcef:main
```

</details>

## Uninstall

<details><summary><b>Windows (binary release)</b></summary>

DCEF does not create any files outside of its folder, so you can just delete the folder to uninstall it.

Move your `exports` folder somewhere else if you want to keep your exports.

</details>

<details><summary><b>Linux (docker)</b></summary>

1. kill and delete the container

```bash
docker rm dcef --force
```

2. remove the volume

```bash
docker volume rm dcef_cache
```

3. remove the image

```bash
docker image rm slada/dcef:main
```

</details>



<a name="supported-exports"></a>
## How to export data from Discord to view it in DCEF?

JSON exports are created using [DiscordChatExporter](https://github.com/Tyrrrz/DiscordChatExporter).

<details><summary><b>Partial export using GUI version of DiscordChatExporter</b></summary>

Make sure that export format is set to `JSON` and `Format markdown` is disabled. Optionally, you should also enable `Download assets`+`Reuse assets` option to download images, videos and other types of assets.

![](docs/dce-export-more.png)

**NOTE**: You can't export threads and forums using GUI version of DCE. You need to use CLI version for that.

</details>



<details><summary><b>Full guild export using CLI version of DiscordChatExporter</b></summary>

> - JSON export format (`--format Json`) is required
> - Downloading assets (`--media --reuse-media`) is highly recommended, but not required
> - Skipping markdown prerendering (`--markdown false`) is highly recommended, but not required

Export all accessible channels in a guild (**without threads and forum posts**):
```bash
DiscordChatExporter.Cli.exe exportguild --token DISCORD_TOKEN -g GUILD_ID --media --reuse-media --markdown false --format Json --output OUTPUT_FOLDER_PATH
```

Export threads/forum posts (you can pass multiple thread/forum post ids):
```bash
DiscordChatExporter.Cli export --token DISCORD_TOKEN  --media --reuse-media --markdown false --output OUTPUT_FOLDER_PATH --format Json --channel THREAD_ID_OR_FORUM_POST_ID_1 THREAD_ID_OR_FORUM_POST_ID_2 THREAD_ID_OR_FORUM_POST_ID_3 THREAD_ID_OR_FORUM_POST_ID_4
```

Don't want to manually right click all threads/forums post and copy their ids? These helper scripts can help you:

[Helper script to export archived threads in a channel](docs/Exporting-threads.md)

[Helper script to export forum posts in a channel](docs/Exporting-threads.md)



</details>

<details><summary><b>Export private messages using CLI version of DiscordChatExporter</b></summary>

Export all dms (sadly, exporting dms can't be done without selfboting):
```bash
DiscordChatExporter.Cli.exe exportdm --token DISCORD_TOKEN --media --reuse-media --markdown false --format Json --output OUTPUT_FOLDER_PATH
```

</details>





## FAQ

<details><summary><b>Some assets are not showing on Windows</b></summary>

Files in `/exports/` folder may exceed Windows path length limit of 260 characters. If you have any issues with loading your assets you can choose one of the following solutions:
- move DCEF to a folder with shorter path
- or run `registry_tweaks/change_260_character_path_limit_to_32767.reg` to increase the limit to 32767 characters (requires admin privileges) and restart your computer. To revert this change, run `registry_tweaks/restore_260_character_path_limit.reg` and restart your computer.

</details>


<details><summary><b>DCEF hangs and prints `Slow SessionWorkflow loop` to the console</b></summary>

`Slow SessionWorkflow loop` messages are completely normal - if you see them, you know that data is pushed to mongodb database and the process is not stuck. Just be patient and wait for the process to finish. If you have a lot of exports, it may take a while.

DCEF is not just an simple viewer. This process enriches your exports with additional data and stores them in a database for search and other features to work.

</details>


<details><summary><b>DCEF won't run on M1 mac</b></summary>

[This pull request](https://github.com/slatinsky/DiscordChatExporter-frontend/pull/30) may help you

</details>


## For developers

[Architecture choices](docs/Architecture.md)

[Setting up a development environment on Windows](docs/Development-env.md)

[Compile the Windows release from source code](docs/Compile.md)

[Supporting other exporters](docs/Supporting-other-exporters.md)


## Thanks
- [Tyrrrz/DiscordChatExporter](https://github.com/Tyrrrz/DiscordChatExporter) - for a great export tool
- [brussell98/discord-markdown](https://github.com/brussell98/discord-markdown) - for discord markdown rendering library

And for other technologies used in this project - sveltekit, docker, nodejs, nvm, pyinstaller, nginx, mongodb

## Related projects

- [Roachbones/discordless](https://github.com/Roachbones/discordless) - real time man-in-the-middle exporter
- [mlomb/chat-analytics](https://github.com/mlomb/chat-analytics) - analytics for your Discord chats.

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
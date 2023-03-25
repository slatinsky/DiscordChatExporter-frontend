# Architecture choices

The project is divided into two main parts: the server and the client.

## Used port numbers

- 21011 - nginx (reverse proxy)
- 21013 - http-server (static files)
- 27017 - mongodb (database)
- 58000 - fastapi (backend api)

All specified port numbers are required to be free.

## Server (Backend)

### Preprocess

The purpose of the preprocess process is to process data exported by [DiscordChatExporter](https://github.com/Tyrrrz/DiscordChatExporter) into the mongodb database.

It doesn't matter, where the exported files are located. The preprocess will recursively search for all files in the `exports` directory and process them.

Specifically, the process does the following:
- processes all JSON channel exports
- while processing, it also processes all referenced assets and convert urls to local paths
- downloads ggsans font from discord cdn.


### mongodb

Database used to store data. The database is divided into multiple collections:
- assets - precomputed assets with local paths and dimensions
- authors - used only for searching
- channels - used for searching and channel list. It also includes threads and forum posts, because they are treated by discord as channels too.
- emojis - used only for searching
- guilds - used for guild list.
- jsons - stores sha256 hashes of processed files. This way, the preprocessor can skip already processed files.
- messages - stores all messages, including authors, emojis, attachments, etc.

### fastapi

Middleman between the client and the mongo database. Provides JSON api for the client (search, guild list, channel list, and messages).

Search and channel endpoints return message ids. Those ids are then fetched by the client when needed.

### http-server

http-server is used to server static files for the frontend. Nginx could be used instead, but sometimes paths exceed the maximum path length of 260 characters on Windows and nginx fails to serve the files.

http-server is used as a workaround for that bug in nginx. But it is also needed to apply registry patch to increase the maximum path length (use `change_260_character_path_limit_to_32767.reg`).

### windows runner (Windows only)

Windows runner is the main entry point of the program on Windows. This script is compiled into `dcef.exe` in the release.

- writes logs from other services to `logs.txt` file for easier debugging.

- checks if all required ports are free on startup

- enforces single instance of the program (opens another window if already running)

- hides console window if the main window is open

- cleans up all services on window close

### nginx

Nginx combines multiple services into one. See `nginx-prod.conf`.

1. First is server frontend files needed for the client to load (paths `/_app/`, `/css/`, `/js/`, `/fonts/`, `/`).

2. Then it proxies static files from http-server from port 21013 (path `/input/`).

3. Then it serves static files created by preprocess (path `/data/`) - now used only for ggsans font.

4. Finally, it proxies api requests from fastapi from port 58000 (path `/api/`).


## Client (Frontend)

Frontend is written in Svelte. It is a statically compiled sveltekit app.




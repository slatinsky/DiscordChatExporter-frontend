# Architecture

The project is divided into two main parts: the server and the client.

## Used port numbers

- 21011 - nginx (reverse proxy)
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


### Mongodb

Database used to store data. The database is divided into multiple collections:
- assets - precomputed assets with local paths and dimensions
- authors - used only for searching
- channels - used for searching and channel list. It also includes threads and forum posts, because they are treated by discord as channels too.
- emojis - used only for searching
- guilds - used for guild list.
- jsons - stores sha256 hashes of processed files. This way, the preprocessor can skip already processed files.
- messages - stores all messages, including authors, emojis, attachments, etc.

Collections are sharded by guilds.

### Fastapi

Middleman between the client and the mongo database. Provides JSON api for the frontend client (search, guild list, channel list, and messages).


### Windows runner (Windows only)

Windows runner is the main entry point of the program on Windows. This script is compiled into `dcef.exe` in the release.

- writes logs from other services to `logs/dcef.log` file for easier debugging.

- checks if all required ports are free on startup

- enforces single instance of the program (opens another window if already running)

- hides console window if the main window is open

- cleans up all services on window close


### Nginx

Nginx combines fastapi backend and static frontend into one. See `nginx-prod.conf`.


## Client (Frontend)

Frontend is written in Svelte. It is a statically compiled sveltekit app.




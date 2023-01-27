from pymongo import MongoClient
from fastapi import FastAPI

URI = "mongodb://127.0.0.1:27017"
client = MongoClient(URI)
db = client["dcef"]
collection_messages = db["messages"]
collection_channels = db["channels"]
collection_guilds = db["guilds"]

app = FastAPI(
	title="DCEF backend api",
	description="This is the backend api for the DCEF viewer.",
	version="0.1.0",
	root_path="/api"
)


@app.get("/")
async def api_status():
	"""
	Returns a message to indicate that the api is running.
	"""
	return {"message": "DCEF api backend is online"}


@app.get("/guilds")
async def get_all_guilds():
	"""
	Returns a list of all guilds.
	"""
	cursor = collection_guilds.find({})
	return list(cursor)

@app.get("/channels")
async def get_all_channels():
	"""
	Returns a list of all channels.
	That includes channels, threads and forum posts.
	"""
	cursor = collection_channels.find({})
	return list(cursor)

@app.get("/channels/{guild_id}")
async def get_channels_by_guild_id(guild_id):
	"""
	Returns a list of channels for a given guild id.
	"""
	cursor = collection_channels.find({"guildId": guild_id})
	return list(cursor)

@app.get("/channel/{channel_id}")
async def get_message_ids_by_channel_id(channel_id):
	"""
	Returns a list of message ids for a given channel id.
	"""
	ids = collection_messages.find({"channelId": channel_id}, {"_id": 1})
	ids = [str(id["_id"]) for id in ids]
	return ids

@app.get("/message/{message_id}")
async def get_message_content_by_id(message_id):
	"""
	Returns the content of a message by its id.
	"""
	message = collection_messages.find_one({"_id": message_id})
	if not message:
		return {"message": "Not found"}
	return message
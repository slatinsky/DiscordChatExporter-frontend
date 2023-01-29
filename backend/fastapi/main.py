import pymongo
from fastapi import FastAPI, Query

URI = "mongodb://127.0.0.1:27017"
client = pymongo.MongoClient(URI)
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
	Returns the status of the api and the database.
	"""
	try:
		database_status = "online" if client.server_info()["ok"] == 1 else "offline"
	except:
		database_status = "offline"
	return {
		"api_backend": "online",  # it api_backend is offline, the api would not respond
		"database": database_status
	}


@app.get("/guilds")
async def get_guilds(guild_id:str = None):
	"""
	Returns a list of guilds
	or a single guild if a guild_id query parameter is provided.
	"""
	if guild_id:
		guild = collection_guilds.find_one({"_id": guild_id})
		if not guild:
			return {"message": "Not found"}
		return guild

	cursor = collection_guilds.find({})
	return list(cursor)

@app.get("/channels")
async def get_channels(guild_id:str = None, channel_id:str = None):
	"""
	Returns a list of all channels.
	That includes channels, threads and forum posts.

	Optionally, a guild_id query parameter can be provided to filter by guild.
	Optionally, a channel_id query parameter can be provided to get only specific channel.
	"""
	if guild_id:
		cursor = collection_channels.find({"guildId": guild_id})
		return list(cursor)

	if channel_id:
		channel = collection_channels.find_one({"_id": channel_id})
		if not channel:
			return {"message": "Not found"}
		return channel


	cursor = collection_channels.find({})
	return list(cursor)

@app.get("/message-ids")
async def get_message_ids(channel_id:str = None):
	"""
	Returns a list of message ids.
	Optionally, a channel_id query parameter can be provided to filter by channel.
	"""
	query = {}
	if channel_id:
		query["channelId"] = channel_id

	ids = collection_messages.find(query, {"_id": 1})
	new_ids = [str(id["_id"]) for id in ids]
	return new_ids

@app.get("/message")
async def get_message_content(message_id:str):
	"""
	Returns the content of a message by its id.
	"""
	message = collection_messages.find_one({"_id": message_id})
	if not message:
		return {"message": "Not found"}
	return message

@app.post("/messages")
async def get_multiple_message_content(message_ids:list):
	"""
	Returns the content of multiple messages by their ids.
	"""
	messages = collection_messages.find({"_id": {"$in": message_ids}})
	return list(messages)


@app.get("/search")
async def search_messages(prompt:str = None, guild_id:str = None, only_ids:bool = True, order_by: str = Query("newest", enum=["newest", "oldest"])):
	"""
	Searches for messages that contain the prompt.
	"""
	# if no prompt, return all messages
	query = {}
	limited_fields = {}

	if prompt:
		query["content.content"] = {"$regex": prompt}

	if guild_id:
		query["guildId"] = guild_id

	if only_ids:
		limited_fields["_id"] = 1

	cursor = collection_messages.find(query, limited_fields)

	if order_by == "newest":
		cursor.sort([("timestamp", pymongo.DESCENDING)])
	else:
		cursor.sort([("timestamp", pymongo.ASCENDING)])

	if only_ids:
		ids = [str(id["_id"]) for id in cursor]
		return ids
	return list(cursor)
from pymongo import MongoClient
from fastapi import FastAPI

URI = "mongodb://127.0.0.1:27017"
client = MongoClient(URI)
db = client["dcef"]
collection_messages = db["messages"]
collection_channels = db["channels"]

app = FastAPI()


@app.get("/")
async def get_root():
	"""
	Returns a message to indicate that the api is running.
	"""
	return {"message": "DCEF api backend is online"}


@app.get("/channels")
async def get_all_channels():
	"""
	Returns a list of all channels.
	That includes channels, threads and forum posts.
	"""
	cursor = collection_channels.find({})
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
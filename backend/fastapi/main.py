from pymongo import MongoClient
from fastapi import FastAPI

URI = "mongodb://127.0.0.1:27017"
client = MongoClient(URI)
db = client["dcef"]
collection_messages = db["messages"]
collection_channels = db["channels"]

app = FastAPI()


@app.get("/")
async def root():
	return {"message": "DCEF api backend"}


@app.get("/channels")
async def channels():
	cursor = collection_channels.find({})
	return list(cursor)

@app.get("/message/{message_id}")
async def message(message_id):
	message = collection_messages.find_one({"_id": message_id})
	if not message:
		return {"message": "Not found"}
	return message
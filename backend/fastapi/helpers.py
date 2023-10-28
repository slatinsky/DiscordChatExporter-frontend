import pymongo

URI = "mongodb://127.0.0.1:27017"
client = pymongo.MongoClient(URI)
db = client["dcef"]
collection_messages = db["messages"]
collection_guilds = db["guilds"]
collection_authors = db["authors"]
collection_emojis = db["emojis"]
collection_assets = db["assets"]
collection_roles = db["roles"]

def get_guild_collection(guild_id, collection_name):
	return db[f"g{pad_id(guild_id)}_{collection_name}"]

def get_global_collection(collection_name):
	return db[collection_name]

def pad_id(id):
	if id == None:
		return None
	return str(id).zfill(24)
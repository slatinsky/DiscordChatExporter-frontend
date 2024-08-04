import pymongo

def pad_id(id):
	if id == None:
		return None
	return str(id).zfill(24)



URI = "mongodb://127.0.0.1:27017"
client = pymongo.MongoClient(URI)
db = client["dcef"]
collection_guilds = db["guilds"]
collection_config = db["config"]

def get_allowlisted_guild_ids():
	allowlisted_guild_ids = collection_config.find_one({"key": "allowlisted_guild_ids"})["value"]
	allowlisted_guild_ids = [pad_id(id) for id in allowlisted_guild_ids]
	return allowlisted_guild_ids

def get_denylisted_user_ids():
	denylisted_user_ids = collection_config.find_one({"key": "denylisted_user_ids"})["value"]
	denylisted_user_ids = [pad_id(id) for id in denylisted_user_ids]
	return denylisted_user_ids


def get_guild_collection(guild_id, collection_name):
	allowlisted_guild_ids = get_allowlisted_guild_ids()
	padded_guild_id = pad_id(guild_id)
	if len(allowlisted_guild_ids) > 0 and padded_guild_id not in allowlisted_guild_ids:
		raise Exception(f"Guild {guild_id} not allowlisted")

	return db[f"g{padded_guild_id}_{collection_name}"]

def get_global_collection(collection_name):
	return db[collection_name]



def is_db_online():
	try:
		client.server_info()
		return True
	except:
		return False
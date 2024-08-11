
import functools
from pymongo import MongoClient
from helpers import pad_id

print = functools.partial(print, flush=True)


class MongoDatabase():
	"""
	Connects to the MongoDB database
	"""
	def __init__(self):
		print("Connecting to database...")
		URI = "mongodb://127.0.0.1:27017"
		DATABASE = "dcef"
		self.client = MongoClient(URI)
		self.database = self.client[DATABASE]

		self.col = {  # collections
			"guilds": self.database["guilds"],
			"jsons": self.database["jsons"],
			"config": self.database["config"],
		}

	def get_guild_collections(self, guild_id):
		"""
		Returns a list of collections that are guild specific
		they are prefixed with the guild id and _ (underscore)
		"""
		padded_guild_id = pad_id(guild_id)
		return {
			"messages": self.database[f"g{padded_guild_id}_messages"],
			"channels": self.database[f"g{padded_guild_id}_channels"],
			"authors":  self.database[f"g{padded_guild_id}_authors"],
			"emojis":   self.database[f"g{padded_guild_id}_emojis"],
			"assets":   self.database[f"g{padded_guild_id}_assets"],
			"roles":    self.database[f"g{padded_guild_id}_roles"],
			"guilds":   self.database["guilds"],
			"jsons":    self.database["jsons"],
			"config":   self.database["config"],
		}

	def create_indexes(self, guild_id):
		# create case insensitive text indexes
		# self.col["messages"].create_index("content.content", default_language="none")
		self.get_guild_collections(guild_id)["messages"].create_index("channelId", default_language="none")



	def clear_database(self, guild_ids):
		"""
		Clears the database to start fresh
		"""
		for guild_id in guild_ids:
			print(f"Wiping guild {guild_id}...")
			collections = self.get_guild_collections(guild_id)

			# key, value
			for collection_name, collection in collections.items():
				if collection_name in ["config", "guilds", "jsons"]:
					continue
				print(f"  Wiping collection {collection_name}...")
				collection.drop()

		print(f"Wiping global...")
		# this list contains old collections too, that are not used anymore
		global_collections = [
			"messages",
			"channels",
			"authors",
			"emojis",
			"assets",
			"roles",
			"jsons",
			"guilds",
		]

		for collection_name in global_collections:
			print(f"  Wiping collection {collection_name}...")
			self.database[collection_name].drop()

	def get_collection(self, collection_name):
		"""
		returns global collection by name
		"""
		return self.col[collection_name]


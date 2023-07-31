
from pymongo import MongoClient

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
			"messages": self.database["messages"],
			"channels": self.database["channels"],
			"guilds": self.database["guilds"],
			"authors": self.database["authors"],
			"emojis": self.database["emojis"],
			"jsons": self.database["jsons"],
			"assets": self.database["assets"],
			"roles": self.database["roles"],
			"jsons": self.database["jsons"],
			"config": self.database["config"],
		}

		self.create_indexes()

	def create_indexes(self):
		# create case insensitive text indexes
		# self.col["messages"].create_index("content.content", default_language="none")
		self.col["messages"].create_index("channelId", default_language="none")



	def clear_database_except_assets(self):
		"""
		Clears the database
		Useful for debugging
		Assets are not cleared, because they are expensive to recompute
		"""
		for collection_name in self.col:
			if collection_name == "assets": # assets are expensive to recompute
				continue
			if collection_name == "config":
				continue
			self.col[collection_name].delete_many({})

	def clear_assets(self):
		self.col["assets"].delete_many({})

	def get_collection(self, collection_name):
		return self.col[collection_name]


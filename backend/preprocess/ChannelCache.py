
import functools
import os

from MongoDatabase import MongoDatabase
from helpers import is_compiled

print = functools.partial(print, flush=True)

class ChannelCache:
	"""
	channels are cached in json files
	this class invalidates the channel cache if you call invalidate_all()
	"""
	def __init__(self):
		if is_compiled():
			self.cache_folder_path = "../../storage/cache/message-ids"
		else:
			self.cache_folder_path = "../../cache/message-ids"

		if not os.path.exists(self.cache_folder_path):
			os.makedirs(self.cache_folder_path)

	def invalidate_all(self):
		"""
		We need to invalidate cache to update
		"""
		print("invalidating cache")
		for filename in os.listdir(self.cache_folder_path):
			if filename.endswith(".json"):
				print("    invalidating cache: " + filename)
				os.remove(self.cache_folder_path + "/" + filename)


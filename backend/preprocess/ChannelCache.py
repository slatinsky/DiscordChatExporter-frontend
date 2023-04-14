
import os

from MongoDatabase import MongoDatabase
from helpers import is_compiled


class ChannelCache:
	"""
	channels are cached in json files
	this class invalidates the cache when a channel is updated
	if you update any channel, call invalidate_channel_id(channel_id)
	"""
	def __init__(self, database: MongoDatabase):
		if is_compiled():
			self.cache_folder_path = "../../storage/cache/message-ids"
		else:
			self.cache_folder_path = "../../release/dcef/storage/cache/message-ids"

		if not os.path.exists(self.cache_folder_path):
			os.makedirs(self.cache_folder_path)

		self.database = database
		self.cached_channel_ids = self._cached_channels_ids_from_db()


	def _get_cache_file_path(self, channel_id: str):
		return self.cache_folder_path + "/" + channel_id + ".json"

	def _delete_cache_file(self, channel_id: str):
		path = self._get_cache_file_path(channel_id)
		if os.path.exists(path):
			os.remove(path)

	def _cached_channels_ids_from_db(self):
		"""
		fetch cached channel ids from database
		this should done before processing files
		"""
		cached_channel_ids = set()
		database_channel_ids = set()
		for channel in self.database.get_collection("channels").find():
			database_channel_ids.add(channel["_id"])

		# if cache json exists with that channel id, mark it as cached
		for channel_id in database_channel_ids:
			path = self._get_cache_file_path(channel_id)

			if os.path.exists(path):
				cached_channel_ids.add(channel_id)

		# remove cache files that don't have a channel in the database
		for filename in os.listdir(self.cache_folder_path):
			if filename.endswith(".json"):
				channel_id = filename[:-5]
				if channel_id not in database_channel_ids:
					print("removing cache file for channel id", channel_id, "because this channel doesn't exist in the database")
					self._delete_cache_file(channel_id)


		return cached_channel_ids


	def invalidate_channel_id(self, channel_id: str):
		"""
		if we make any changes to a channel, we should invalidate the cache
		"""
		if channel_id in self.cached_channel_ids:
			print("invalidating cache for channel id", channel_id, "because it was updated and the cache is now invalid")
			self.cached_channel_ids.remove(channel_id)
			self._delete_cache_file(channel_id)

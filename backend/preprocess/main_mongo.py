import glob
from hashlib import sha256
import hashlib
import os
import re
import sys

import imagesize
import requests
from pymongo import MongoClient
import json
from pprint import pprint
from colorthief import ColorThief
import functools

# fix PIPE encoding error on Windows, auto flush print
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')
print = functools.partial(print, flush=True)


def pad_id(id):
	if id == None:
		return None
	return str(id).zfill(24)


with open('emojiIndex.json', 'r', encoding='utf8') as f:
    emoji_index = json.load(f)

# read emojiIndex.json
# emojiIndex from https://github.com/Tyrrrz/DiscordChatExporter/blob/5b1b7205037662bb28dc5e541f0950586d4b8a22/DiscordChatExporter.Core/Utils/EmojiIndex.cs
def get_emoji_code(name):
    if name in emoji_index:
        return emoji_index[name]
    else:
        return name


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
			"jsons": self.database["jsons"]
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
			self.col[collection_name].delete_many({})

	def clear_assets(self):
		self.col["assets"].delete_many({})

	def get_collection(self, collection_name):
		return self.col[collection_name]


class FileFinder():
	"""
	Find all files in a directory
	"""
	def __init__(self, directory: str):
		self.base_directory = self.normalize_path(directory)

	def find_channel_exports(self):
		print("finding channel exports in " + self.base_directory)
		directory = self.base_directory
		files = []
		for filename in glob.glob(directory + '**/*.json', recursive=True):
			if filename.endswith('.json'):
				# ignore attachment files - they are made by users, not DiscordChatExporter
				if re.search(r"([A-F0-9]{5})\.json$", filename) != None:
					continue

				# ignore channel_info.json
				if filename.endswith('channel_info.json'):
					continue

				# quick check if file is a export made by DiscordChatExporter
				with open(filename, encoding='utf-8') as file:
					first_16_bytes = file.read(16)
					if first_16_bytes.find("guild") == -1:
						print("invalid file " + filename)
						continue
				filename_without_base_directory = self.remove_base_directory(filename)
				files.append(filename_without_base_directory)

		return files

	def find_local_assets(self):
		input_directory = self.base_directory
		all_files = {}
		regex_pattern = re.compile(r'.+\-[A-F0-9]{5}\..+')
		for path in glob.glob(input_directory + '**/*', recursive=True):
			if regex_pattern.match(path):
				filename = os.path.basename(path)
				all_files[filename] = path.replace('\\', '/')

		return all_files

	def remove_base_directory(self, path: str):
		"""
		remove base directory from the start of the path
		ignore if path doesn't start with base directory
		"""
		if path == None:
			return None

		path = self.normalize_path(path)
		if not path.startswith(self.base_directory):
			print("path doesn't start with base directory: " + path)
			return path

		return path[len(self.base_directory):]

	def add_base_directory(self, path: str):
		"""
		add base directory to the start of the path
		if path already starts with base directory, do nothing
		"""
		path = self.normalize_path(path)
		if path.startswith(self.base_directory):
			print("path already starts with base directory: " + path)
			return path

		return self.base_directory + path

	def normalize_path(self, path: str):
		"""
		replace all \ with /
		"""
		return path.replace("\\", "/")


class AssetProcessor:
	def __init__(self, file_finder: FileFinder, database: MongoDatabase):
		self.file_finder = file_finder
		self.collection_assets = database.get_collection("assets")
		self.local_assets = file_finder.find_local_assets()
		self.fast_mode = False

	def set_fast_mode(self, fast_mode: bool):
		self.fast_mode = fast_mode

	def is_remote(self, path: str) -> bool:
		"""
		returns True if path is a remote url
		"""
		if re.match(r'^https?://', path):
			return True

		return False

	def get_extension(self, path: str) -> str:
		"""
		returns file extension of path
		"""
		# strip query string
		path = path.split('?')[0]

		return os.path.splitext(path)[-1].replace('.', '').lower()

	def get_file_type(self, path: str, extension) -> str:
		if extension is None:
			return None
		elif extension in ('png', 'jpg', 'jpeg', 'gif', 'webp'):
			return 'image'
		elif extension in ('mp4', 'webm', 'mov'):
			return 'video'
		elif extension in('mp3', 'ogg', 'wav'):
			return 'audio'
		else:
			return 'unknown'


	def get_image_size(self, path: str, local_path_exists: bool, filetype: str) -> tuple:
		"""
		returns image size as tuple (width, height)
		"""
		# we don't know the size of remote images without downloading them
		if not local_path_exists:
			return None, None

		# file has no known image extension
		if filetype != 'image':
			return None, None

		try:
			return imagesize.get(path)
		except:
			print("Error: Could not get image size of " + path)
			return None, None

	def get_file_size(self, local_path_exists: bool, path: str) -> int:
		"""
		returns file size in bytes
		"""
		if not local_path_exists:
			return None

		return os.path.getsize(path)

	def get_filename_with_hash(self, path: str, is_remote: bool) -> str:
		# local path
		if not is_remote:
			return os.path.basename(path)

		# remote path (url)
		filename = re.match(r'.+/([^?]*)', path).groups()[0]
		filename_without_ext, filename_ext = os.path.splitext(filename)

		if len(filename_ext) > 41:
			filename_without_ext = filename
			filename_ext = ""

		# hashed filename must contain get parameters
		hash_sha256 = sha256(path.encode('utf-8')).hexdigest()[:5].upper()

		# remove get parameters
		# filename = filename.split('?')[0]
		# base, extension = os.path.splitext(filename)
		filename = filename_without_ext[:42] + "-" + hash_sha256 + filename_ext
		return filename

	def strip_hash_from_filename(self, filename: str) -> str:
		"""
		removes hash from filename
		"""
		return re.sub(r'-[A-F0-9]{5}(?=\..+$)', '', filename)

	def get_colors(self, path: str, local_path_exists: bool, filetype: str):
		"""
		returns dominant color and palette of image
		this is very slow, so do it only if fast mode is disabled
		"""
		if self.fast_mode:
			return None, None

		if not local_path_exists:
			return None, None

		if filetype != 'image':
			return None, None

		try:
			color_thief = ColorThief(path)
			dominant_color = color_thief.get_color(quality=1)
			palette = color_thief.get_palette(color_count=6)
			return dominant_color, palette
		except:
			print("Error: Could not get colors of " + path)
			return None, None

	def get_cached_asset(self, filename_with_hash: str) -> bool:
		"""
		returns asset content if asset has already been processed (fetch from database)
		if asset not found in database returns None
		"""
		cached_asset = self.collection_assets.find_one({"_id": filename_with_hash})
		if cached_asset is None:
			return None

		return cached_asset

	def insert_asset(self, asset: dict):
		"""
		inserts asset into database
		"""
		self.collection_assets.insert_one(asset)

	def get_local_path(self, filename_with_hash: str) -> str:
		"""
		returns local path of asset
		"""
		if filename_with_hash in self.local_assets:
			return self.local_assets[filename_with_hash]
		else:
			print("Error: Could not find local path of " + filename_with_hash)
			return None

	def process(self, original_filepath: str):
		"""
		provide filepath without base directory
		original_filepath is the path from json file, but is not necessarily a valid path
		"""
		if original_filepath == None:
			return
		original_filepath = self.file_finder.normalize_path(original_filepath)

		is_remote = self.is_remote(original_filepath)
		filename_with_hash = self.get_filename_with_hash(original_filepath, is_remote)

		cached_asset = self.get_cached_asset(filename_with_hash)
		if cached_asset is not None:
			return cached_asset

		remote_url = original_filepath if is_remote else None
		local_path = self.get_local_path(filename_with_hash)
		local_path_exists = True if local_path is not None else False

		extension = self.get_extension(original_filepath)
		filetype = self.get_file_type(original_filepath, extension)
		width, height = self.get_image_size(local_path, local_path_exists, filetype)
		size_bytes = self.get_file_size(local_path_exists, local_path)
		filename_without_hash = self.strip_hash_from_filename(filename_with_hash)
		dominant_color, palette = self.get_colors(local_path, local_path_exists, filetype)

		local_path_without_base = self.file_finder.remove_base_directory(local_path)
		if local_path_without_base is not None:
			path = local_path_without_base
		elif remote_url is not None:
			path = remote_url
		else:
			path = None

		asset = {
			"_id": filename_with_hash,
			"originalPath": original_filepath,
			"localPath": local_path_without_base,
			"remotePath": remote_url,
			"path": path,
			"extension": extension,
			"type": filetype,
			"width": width,
			"height": height,
			"sizeBytes": size_bytes,
			"filenameWithHash": filename_with_hash,
			"filenameWithoutHash": filename_without_hash,
			"colorDominant": dominant_color,
			"colorPalette": palette,
		}

		self.insert_asset(asset)
		return asset

class JsonProcessor:
	def __init__(self, database: MongoDatabase, file_finder: FileFinder, json_path:str, asset_processor: AssetProcessor):
		self.json_path = json_path
		self.database = database
		self.collection_guilds = self.database.get_collection("guilds")
		self.collection_channels = self.database.get_collection("channels")
		self.collection_messages = self.database.get_collection("messages")
		self.collection_authors = self.database.get_collection("authors")
		self.collection_emojis = self.database.get_collection("emojis")
		self.collection_assets = self.database.get_collection("assets")
		self.collection_jsons = self.database.get_collection("jsons")
		self.file_finder = file_finder
		self.asset_processor = asset_processor

	def read_json_file(self, file_path):
		file_path_with_base_directory = self.file_finder.add_base_directory(file_path)
		with open(file_path_with_base_directory, "r", encoding='utf-8') as f:
			try:
				data = json.load(f)
			except json.decoder.JSONDecodeError:
				# probably media file too
				print("JSONDecodeError: " + file_path)
				return None

			if 'guild' not in data:  # this is not a channel export, but a downloaded media json file
				return None
		return data
	def process_guild(self, guild):
		guild["_id"] = pad_id(guild.pop("id"))
		guild["icon"] = self.asset_processor.process(guild.pop("iconUrl"))
		return guild

	def process_channel(self, channel, guild_id):
		"""
		process channel info
		does not contain messages
		"""
		channel["_id"] = pad_id(channel.pop("id"))
		channel["categoryId"] = pad_id(channel["categoryId"])
		channel["guildId"] = guild_id
		return channel

	def process_messages(self, messages, guild_id, channel_id, channel_name):
		"""
		rename id to mongo _id
		pad ids to 24 digits
		delete empty lists
		reference to guild_id and channel_id
		convert content to array
		"""
		for message in messages:
			# pad ids so they are easier to sort
			message["_id"] = pad_id(message.pop("id"))
			if "author" in message:
				message["author"]["_id"] = pad_id(message["author"].pop("id"))
			if "stickers" in message:
				for sticker in message["stickers"]:
					sticker["_id"] = pad_id(sticker.pop("id"))
			if "mentions" in message:
				for mention in message["mentions"]:
					mention["_id"] = pad_id(mention.pop("id"))
			if "reference" in message:
				message["reference"]["messageId"] = pad_id(message["reference"]["messageId"])
				message["reference"]["channelId"] = pad_id(message["reference"]["channelId"])
				message["reference"]["guildId"] = pad_id(message["reference"]["guildId"])

			if "attachments" in message:
				for attachment in message["attachments"]:
					attachment["_id"] = pad_id(attachment.pop("id"))

			# remove empty lists
			if len(message["attachments"]) == 0:
				del message["attachments"]

			if len(message["embeds"]) == 0:
				del message["embeds"]

			if len(message["mentions"]) == 0:
				del message["mentions"]

			if len(message["stickers"]) == 0:
				del message["stickers"]

			if len(message["reactions"]) == 0:
				del message["reactions"]

			# reference to guild and channel
			message["guildId"] = guild_id
			message["channelId"] = channel_id
			message["channelName"] = channel_name

			# because content may be edited, we need to change content field to an array
			latest_timestamp = message["timestampEdited"] if message["timestampEdited"] != None else message["timestamp"]
			message["content"] = [
				{
					"timestamp": latest_timestamp,
					"content": message["content"]
				}
			]


			# process assets
			if "embeds" in message:
				for embed in message["embeds"]:
					if "thumbnail" in embed:
						if "width" in embed["thumbnail"] and "height" in embed["thumbnail"]:
							original_width = embed["thumbnail"]["width"]
							original_height = embed["thumbnail"]["height"]
						embed["thumbnail"] = self.asset_processor.process(embed["thumbnail"]["url"])

						# restore some fields, because we are losing them in the asset preprocess if url is remote
						if "originalWidth" in locals():
							embed["thumbnail"]["width"] = original_width
							embed["thumbnail"]["height"] = original_height

					if "images" in embed:
						new_images = []
						for image in embed["images"]:
							if "width" in image and "height" in image:
								original_width = image["width"]
								original_height = image["height"]
							image = self.asset_processor.process(image["url"])  # does this work?

							# restore some fields, because we are losing them in the asset preprocess if url is remote
							if "originalWidth" in locals():
								image["width"] = original_width
								image["height"] = original_height

							new_images.append(image)

						embed["images"] = new_images

					if "image" in embed:
						if "width" in embed["image"] and "height" in embed["image"]:
							original_width = embed["image"]["width"]
							original_height = embed["image"]["height"]
						embed["image"] = self.asset_processor.process(embed["image"]["url"])

						# restore some fields, because we are losing them in the asset preprocess if url is remote
						if "originalWidth" in locals():
							embed["image"]["width"] = original_width
							embed["image"]["height"] = original_height

					if "footer" in embed and "iconUrl" in embed["footer"]:
						embed["footer"]["icon"] = self.asset_processor.process(embed["footer"].pop("iconUrl"))

					if "author" in embed and "iconUrl" in embed["author"]:
						embed["author"]["icon"] = self.asset_processor.process(embed["author"].pop("iconUrl"))

			if "reactions" in message:
				for reaction in message["reactions"]:
					if "emoji" in reaction:
						reaction["emoji"]["guildId"] = guild_id
						reaction["emoji"]["source"] = "custom"
						reaction["emoji"]["_id"] = pad_id(reaction["emoji"].pop("id"))
						if reaction["emoji"]["_id"] == pad_id(0):
							reaction["emoji"]["name"] = get_emoji_code(reaction["emoji"]["name"]).replace(":", "")
							reaction["emoji"]["_id"] = reaction["emoji"]["name"]
							del reaction["emoji"]["guildId"]
							reaction["emoji"]["source"] = "default"

						reaction["emoji"]["image"] = self.asset_processor.process(reaction["emoji"].pop("imageUrl"))

			new_attachments = []
			if "attachments" in message:
				for attachment in message["attachments"]:
					new_attachment = self.asset_processor.process(attachment.pop("url"))

					# restore some fields, because we are losing them in the asset preprocess if url is remote
					if "fileSizeBytes" in attachment:
						new_attachment["sizeBytes"] = attachment["fileSizeBytes"]

					if "id" in attachment:
						new_attachment["id"] = attachment["_id"]

					new_attachments.append(new_attachment)

				message["attachments"] = new_attachments

			if "stickers" in message:
				for sticker in message["stickers"]:
					sticker["source"] = self.asset_processor.process(sticker.pop("sourceUrl"))

		return messages

	def process_authors(self, messages: list) -> list:
		"""
		Extracts all authors from messages and returns a list of authors
		"""
		# extract all authors. Dictionary is used to remove duplicates
		authors = {}
		for message in messages:
			if "author" in message:
				author = message["author"]

				if author["_id"] in authors:
					# save new nickname if different
					if message["author"]["nickname"] not in authors[author["_id"]]["nicknames"]:
						authors[author["_id"]]["nicknames"].append(message["author"]["nickname"])
					continue

				author["avatar"] = self.asset_processor.process(author.pop("avatarUrl"))
				author["nicknames"] = [author.pop("nickname")]
				authors[author["_id"]] = author  # new author

		authors_list = []
		for author_id in authors:
			author = authors[author_id]
			authors_list.append(author)

		# add authors back to messages
		for message in messages:
			if "author" in message:
				message["author"] = authors[message["author"]["_id"]]

		return authors_list

	def process_emojis(self, messages: list, guild_id) -> list:
		"""
		extracts all emojis from messages and returns a list of emojis
		"""
		emojis = {}
		for message in messages:
			if "reactions" in message:
				for reaction in message["reactions"]:
					emoji = reaction["emoji"]

					if emoji["_id"] in emojis:
						# emoji already exists, ignore
						continue

					emojis[emoji["_id"]] = emoji

		emojis_list = []
		for emoji_id in emojis:
			emojis_list.append(emojis[emoji_id])

		return emojis_list


	def insert_guild(self, guild):
		database_document = self.collection_guilds.find_one({"_id": guild["_id"]})

		if database_document != None:
			# guild already exists, ignore
			return

		self.collection_guilds.insert_one(guild)

	def insert_channel(self, channel):
		database_document = self.collection_channels.find_one({"_id": channel["_id"]})

		if database_document != None:
			# channel already exists
			return

		self.collection_channels.insert_one(channel)

	def insert_author(self, author):
		database_document = self.collection_authors.find_one({"_id": author["_id"]})

		if database_document != None:
			# author already exists
			return

		self.collection_authors.insert_one(author)

	def insert_emoji(self, emoji):
		database_document = self.collection_emojis.find_one({"_id": emoji["_id"]})

		if database_document != None:
			# emoji already exists
			return

		self.collection_emojis.insert_one(emoji)

	def insert_message(self, message):
		"""
		Inserts a message into the database if it doesn't exist yet.
		Merges the message content with the existing message if it already exists.
		"""

		content = message["content"][0]['content']
		latest_timestamp = message["timestamp"]
		if message["timestampEdited"] != None:
			latest_timestamp = message["timestampEdited"]

		# check if message already exists. If so, get the existing message
		database_document = self.collection_messages.find_one({"_id": message["_id"]})

		if database_document != None:  # message already exists
			# print("ID exists: " + str(message["id"]))

			# if message was edited, add new content
			has_timestamp = False
			for database_document_content in database_document["content"]:
				# print(database_document_content["timestamp"] + " == " + latest_timestamp)
				if database_document_content["timestamp"] == latest_timestamp:
					has_timestamp = True
					break

			if not has_timestamp:
				database_document["content"].append({
					"timestamp": latest_timestamp,
					"content": content
				})
				print(database_document["content"])
				# update database
				self.collection_messages.update_one({"_id": message["_id"]}, {"$set": database_document})
			return

		self.collection_messages.insert_one(message)

	def check_if_processed(self, json_path):
		"""
		Checks if a file has already been processed
		"""

		json_path_with_base_dir = self.file_finder.add_base_directory(json_path)

		# read from database
		json = self.collection_jsons.find_one({"_id": json_path})

		if json == None:
			return False

		# check if file size is the same
		file_size = os.path.getsize(json_path_with_base_dir)
		if json["size"] != file_size:
			# delete from database
			self.collection_jsons.delete_one({"_id": json_path})
			return False

		# check if file hash is the same
		file_hash = hashlib.sha256()
		with open(json_path_with_base_dir, "rb") as f:
			for byte_block in iter(lambda: f.read(4096), b""):
				file_hash.update(byte_block)
		hex_hash = file_hash.hexdigest()

		if json["sha256_hash"] != hex_hash:
			# delete from database
			self.collection_jsons.delete_one({"_id": json_path})
			return False

		return True

	def mark_as_processed(self, json_path):
		"""
		Marks a file as processed by adding it to the jsons collection
		"""

		json_path_with_base_dir = self.file_finder.add_base_directory(json_path)

		# get file size
		file_size = os.path.getsize(json_path_with_base_dir)

		# get file hash of file content
		file_hash = hashlib.sha256()
		with open(json_path_with_base_dir, "rb") as f:
			for byte_block in iter(lambda: f.read(4096), b""):
				file_hash.update(byte_block)

		hex_hash = file_hash.hexdigest()

		self.collection_jsons.insert_one({
			"_id": json_path,
			"size": file_size,
			"sha256_hash": hex_hash
		})

	def process(self):
		if self.check_if_processed(self.json_path):
			print("already processed " + self.json_path)
			return

		print("processing " + self.json_path)

		json_data = self.read_json_file(self.json_path)

		if json_data == None:
			print("invalid file " + self.json_path)
			return

		guild = self.process_guild(json_data["guild"])
		channel = self.process_channel(json_data["channel"], guild["_id"])
		messages = self.process_messages(json_data["messages"], guild["_id"], channel["_id"], channel["name"])
		authors = self.process_authors(json_data["messages"])
		emojis = self.process_emojis(json_data["messages"], guild["_id"])

		self.insert_guild(guild)
		self.insert_channel(channel)
		for message in messages:
			self.insert_message(message)

		for author in authors:
			self.insert_author(author)

		for emoji in emojis:
			self.insert_emoji(emoji)

		self.mark_as_processed(self.json_path)



def download_gg(output_directory):
        """
        download gg sans if not already downloaded
        we cannot directly include it, because it is not open source
        """
        paths = {
            "ggsans-normal-400.woff2": "https://discord.com/assets/a798bb95e0f5a69c8ab85e53103ba6b2.woff2",
            "ggsans-italic-400.woff2": "https://discord.com/assets/8ca69301ef43643d9c7e14036f80061d.woff2",
            "ggsans-normal-500.woff2": "https://discord.com/assets/637ce9c046bf63b68fa35412518822d5.woff2",
            "ggsans-italic-500.woff2": "https://discord.com/assets/e8f55fa2303208454eaa0fbde8920d3f.woff2",
            "ggsans-normal-600.woff2": "https://discord.com/assets/4f2e4275143211c2492a31ca2c9669fb.woff2",
            "ggsans-italic-600.woff2": "https://discord.com/assets/fb1134f6438f4d0610260294891aa56e.woff2",
            "ggsans-normal-700.woff2": "https://discord.com/assets/bd88a0d8f72ec18529956748c2e00547.woff2",
            "ggsans-italic-700.woff2": "https://discord.com/assets/4893950fe590addffb6515237f1d1014.woff2",
            "ggsans-normal-800.woff2": "https://discord.com/assets/ec68b736b0006bb42d8a44528aafe796.woff2",
            "ggsans-italic-800.woff2": "https://discord.com/assets/ba1f0a8f593aa3c705d8de718f7c8d9a.woff2"
        }
        save_dir = os.path.join(output_directory, "fonts")
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

        for filename, url in paths.items():
            save_path = os.path.join(save_dir, filename)
            if not os.path.exists(save_path):
                print("   Downloading", filename)
                try:
                    r = requests.get(url)
                    with open(save_path, 'wb') as f:
                        f.write(r.content)
                except:  # discord may change the url
                    print("   Error downloading", filename)


def main(input_dir, output_dir):
	print("main_mongo loaded")

	database = MongoDatabase()
	# DEBUG clear database
	# database.clear_database_except_assets()

	file_finder = FileFinder(input_dir)

	jsons = file_finder.find_channel_exports()
	print("found " + str(len(jsons)) + " json channel exports")

	# DEBUG get only first n files
	# jsons = jsons[:400]

	asset_processor = AssetProcessor(file_finder, database)
	asset_processor.set_fast_mode(True)  # don't process slow actions

	for json_path in jsons:
		p = JsonProcessor(database, file_finder, json_path, asset_processor)
		p.process()

	download_gg(output_dir)

	print("done")



if __name__ == "__main__":
	input_dir = sys.argv[1]
	output_dir = sys.argv[2]
	main(input_dir, output_dir)


from pprint import pprint
import re
import pymongo
from fastapi import FastAPI, Query

URI = "mongodb://127.0.0.1:27017"
client = pymongo.MongoClient(URI)
db = client["dcef"]
collection_messages = db["messages"]
collection_channels = db["channels"]
collection_guilds = db["guilds"]
collection_authors = db["authors"]
collection_emojis = db["emojis"]

app = FastAPI(
	title="DCEF backend api",
	description="This is the backend api for the DCEF viewer.",
	version="0.1.0",
	root_path="/api"
)


def pad_id(id):
	if id == None:
		return None
	return str(id).zfill(24)


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
async def get_guilds(guild_id: str = None):
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
async def get_channels(guild_id: str = None, channel_id: str = None):
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
async def get_message_ids(channel_id: str = None):
	"""
	Returns a list of message ids.
	Optionally, a channel_id query parameter can be provided to filter by channel.
	"""
	query = {}
	if channel_id:
		query["channelId"] = channel_id

	ids = collection_messages.find(query, {"_id": 1}).sort([("_id", pymongo.ASCENDING)])
	new_ids = [str(id["_id"]) for id in ids]
	return new_ids


@app.get("/message")
async def get_message_content(message_id: str):
	"""
	Returns the content of a message by its id.
	"""
	message = collection_messages.find_one({"_id": message_id})
	if not message:
		return {"message": "Not found"}
	return message


@app.post("/messages")
async def get_multiple_message_content(message_ids: list):
	"""
	Returns the content of multiple messages by their ids.
	"""
	messages = collection_messages.find({"_id": {"$in": message_ids}})
	list_of_messages = list(messages)
	list_of_messages = enrich_messages(list_of_messages)
	return list_of_messages


def extend_channels(channels: list):
	"""
	Extend a list of channels with thread ids and forum post ids.

	Can be also used to extend a list of categories with channel ids.
	In this case, we will not clean category ids from the list, but it causes no problems except for a little bit of performance loss.
	"""
	if len(channels) == 0:
		return channels

	channels = channels.copy()
	new_channels_cursor = collection_channels.find(
	    {"categoryId": {"$in": channels}})
	channels.extend([channel["_id"] for channel in new_channels_cursor])
	channels = list(set(channels))  # remove duplicates
	return channels

def extend_users(user_ids: list, usernames: list):
	"""
	Find new user ids by user names.
	"""
	if len(usernames) == 0:
		return usernames

	user_ids = user_ids.copy()
	# partial match

	or_ = []
	for username in usernames:
		or_.append({"name": {"$regex": username, "$options": "i"}})

	query = {"$or": or_}

	new_user_ids_cursor = collection_authors.find(query, {"_id": 1})
	new_user_ids = [user["_id"] for user in new_user_ids_cursor]
	user_ids.extend(new_user_ids)
	user_ids = list(set(user_ids))  # remove duplicates
	return user_ids


def extend_reactions(reaction_ids: list, reactions: list):
	"""
	Find new reaction ids by reaction names.
	Support partial or lowercase match.

	"""
	if len(reactions) == 0:
		return reactions

	reaction_ids = reaction_ids.copy()
	# partial match

	or_ = []
	for reaction in reactions:
		or_.append({"name": {"$regex": reaction, "$options": "i"}})

	query = {"$or": or_}

	new_reaction_ids_cursor = collection_emojis.find(query, {"_id": 1})
	new_reaction_ids = [reaction["_id"] for reaction in new_reaction_ids_cursor]
	reaction_ids.extend(new_reaction_ids)
	reaction_ids = list(set(reaction_ids))  # remove duplicates
	return reaction_ids



def get_emotes_from_db(emote_names: list) -> dict:
	"""
	try to find emotes from DB by their name
	use exact match only
	"""
	if len(emote_names) == 0:
		return {}

	or_ = []
	for emote_name in emote_names:
		or_.append({"name": emote_name})

	query = {"$or": or_}

	emotes = collection_emojis.find(query)
	emotes = {emote["name"]: emote for emote in emotes}
	return emotes

def get_channel_info(channel_id):
	"""
	get channel info by id
	'channel' can be thread or channel or forum post
	"""

	# print("get_channel_info", channel_id)
	channel = collection_channels.find_one({"_id": channel_id})
	if not channel:
		return {
			"type": "GuildPublicThread",
			"name": "Not found",
		}

	# print("get_channel_info", channel)
	msg_count = collection_messages.count_documents({"channelId": channel_id})
	channel["msgCount"] = msg_count
	return channel


def enrich_messages(list_of_messages: list) -> list:
	regex = re.compile(r':([^ ]+):')

	possible_emotes = []
	for message in list_of_messages:
		for content in message["content"]:
			message_content = content["content"]
			# match all
			search = regex.findall(message_content)
			possible_emotes.extend(search)

	possible_emotes = list(set(possible_emotes))


	# get all emotes from db
	emotes = get_emotes_from_db(emote_names=possible_emotes)

	# replace emotes in messages
	for message in list_of_messages:
		message_emotes = []
		for content in message["content"]:
			message_content = content["content"]
			search = regex.findall(message_content)
			for emote_name in search:
				if emote_name in emotes:
					emote = emotes[emote_name]
					message_emotes.append(emote)

		if len(message_emotes) > 0:
			message["emotes"] = message_emotes

	for message in list_of_messages:
		if message["type"] == "ThreadCreated":
			message["thread"] = get_channel_info(message["reference"]["channelId"])

	return list_of_messages

def parse_prompt(prompt: str):
	"""
	Parses a prompt into categories.
	"""
	search = {
		"message_contains": [],          # words that must be in the message content (and)
		"message_ids": [],               # message ids (strings) (or)
		"from_user_ids": [],             # user ids (strings) (or)
		"from_users": [],                # user names (or)
		"mentions_user_ids": [],         # user ids (strings) (or)
		"mentions_users": [],            # user names (or)
		"reaction_ids": [],              # emoji ids (strings) (or)
		"reactions": [],                 # emoji names (or)
		"extensions": [],                # file extensions like "pdf", "java" (or)
		"filenames": [],                 # file names (or)
		"in_channel_ids": [],            # channel ids (strings) (or)
		"in_category_ids": [],           # category ids (strings) (or)
		"is_pinned": None,               # boolean (None means both)
		"attachment_is_audio": None,     # boolean (None means both) (or in group attachment_is)
		"attachment_is_image": None,     # boolean (None means both) (or in group attachment_is)
		"attachment_is_video": None,     # boolean (None means both) (or in group attachment_is)
		"attachment_is_other": None,     # boolean (None means both) (or in group attachment_is)
		"containing_links": None,        # boolean (None means both)
		"is_edited": None,               # boolean (None means both)
		"limit": 100000                  # max number of messages to return (int)
	}

	# loop throught all characters
	inside_quotes = False
	word = ""
	valid_search_keys = ["message_id", "user_id", "user", "mentions_user_id", "mentions_user", "reaction_id", "reaction" ,"extension", "filename", "in_channel_id", "in_category_id",
	"is_pinned", "has_audio", "has_image", "has_video", "has_other", "has_link", "is_edited", "limit"]
	current_key = None

	for i, char in enumerate(prompt.strip() + " "):
		if char == '"':
			inside_quotes = not inside_quotes
			continue

		if char == ":" and not inside_quotes and word in valid_search_keys:
			current_key = word
			word = ""
			continue

		if char == ' ' and not inside_quotes:
			if (current_key == "message_id"):
				search["message_ids"].append(word)
			elif (current_key == "user_id"):
				search["from_user_ids"].append(word)
			elif (current_key == "user"):
				search["from_users"].append(word)
			elif (current_key == "mentions_user_id"):
				search["mentions_user_ids"].append(word)
			elif (current_key == "mentions_user"):
				search["mentions_users"].append(word)
			elif (current_key == "reaction_id"):
				search["reaction_ids"].append(word)
			elif (current_key == "reaction"):
				search["reactions"].append(word)
			elif (current_key == "extension"):
				search["extensions"].append(word)
			elif (current_key == "filename"):
				search["filenames"].append(word)
			elif (current_key == "in_channel_id"):
				search["in_channel_ids"].append(word)
			elif (current_key == "in_category_id"):
				search["in_category_ids"].append(word)
			elif (current_key == "is_pinned"):
				if word == "true":
					search["is_pinned"] = True
				elif word == "false":
					search["is_pinned"] = False
			elif (current_key == "has_audio"):
				if word == "true":
					search["attachment_is_audio"] = True
				elif word == "false":
					search["attachment_is_audio"] = False
			elif (current_key == "has_image"):
				if word == "true":
					search["attachment_is_image"] = True
				elif word == "false":
					search["attachment_is_image"] = False
			elif (current_key == "has_video"):
				if word == "true":
					search["attachment_is_video"] = True
				elif word == "false":
					search["attachment_is_video"] = False
			elif (current_key == "has_other"):
				if word == "true":
					search["attachment_is_other"] = True
				elif word == "false":
					search["attachment_is_other"] = False
			elif (current_key == "has_link"):
				if word == "true":
					search["containing_links"] = True
				elif word == "false":
					search["containing_links"] = False
			elif (current_key == "is_edited"):
				if word == "true":
					search["is_edited"] = True
				elif word == "false":
					search["is_edited"] = False
			elif (current_key == "limit"):
				search["limit"] = int(word)
			else:
				if word != "":
					search["message_contains"].append(word)

			if current_key in valid_search_keys:
				current_key = None

			word = ""
			continue

		word += char

	print(search)
	return search




@app.get("/search")
async def search_messages(prompt: str = None, guild_id: str = None, only_ids: bool = True, order_by: str = Query("newest", enum=["newest", "oldest"])):
	"""
	Searches for messages that contain the prompt.
	"""

	# todo: parse prompt
	search = parse_prompt(prompt)
	message_contains = search["message_contains"]
	message_ids = search["message_ids"]
	from_user_ids = search["from_user_ids"]
	from_users = search["from_users"]
	mentions_user_ids = search["mentions_user_ids"]
	mentions_users = search["mentions_users"]
	reaction_ids = search["reaction_ids"]
	reactions = search["reactions"]
	extensions = search["extensions"]
	filenames = search["filenames"]
	in_channel_ids = search["in_channel_ids"]
	in_category_ids = search["in_category_ids"]
	is_pinned = search["is_pinned"]
	attachment_is_audio = search["attachment_is_audio"]
	attachment_is_image = search["attachment_is_image"]
	attachment_is_video = search["attachment_is_video"]
	attachment_is_other = search["attachment_is_other"]
	containing_links = search["containing_links"]
	is_edited = search["is_edited"]
	limit = search["limit"]

	# clean up
	message_contains = [word.lower() for word in message_contains]
	message_ids = [pad_id(id) for id in message_ids]
	from_user_ids = [pad_id(id) for id in from_user_ids]
	from_users = [user.lower() for user in from_users]
	from_user_ids = extend_users(from_user_ids, from_users)
	mentions_user_ids = [pad_id(id) for id in mentions_user_ids]
	mentions_users = [user.lower() for user in mentions_users]
	mentions_user_ids = extend_users(mentions_user_ids, mentions_users)
	reaction_ids = [pad_id(id) for id in reaction_ids]
	reactions = [reaction.lower() for reaction in reactions]
	reaction_ids = extend_reactions(reaction_ids, reactions)
	extensions = [ext.lower() for ext in extensions]
	in_channel_ids = [pad_id(id) for id in in_channel_ids]
	in_channel_ids = extend_channels(in_channel_ids)      # extend channels with threads and forum posts
	in_category_ids = [pad_id(id) for id in in_category_ids]
	in_category_ids = extend_channels(in_category_ids)  # extend categories with channels
	in_category_ids = extend_channels(in_category_ids)  # extend channels with threads and forum posts



	# query builder
	query = {}
	limited_fields = {}

	query["$and"] = []

	if len(message_ids) > 0:
		query["_id"] = {"$in": message_ids}

	if len(from_user_ids) > 0:
		query["author._id"] = {"$in": from_user_ids}

	if len(mentions_user_ids) > 0:
		query["mentions._id"] = {"$in": mentions_user_ids}

	if len(reaction_ids) > 0:
		query["reactions.emoji._id"] = {"$in": reaction_ids}

	if len(extensions) > 0:
		# extension can be in attachments or embeds
		query["$and"].append(
			{
				"$or":
				[
					{"attachments.extension": {"$in": extensions}},
					{"embeds.thumbnail.extension": {"$in": extensions}}
				]
			}
		)

	if len(filenames) > 0:
		# filename can be in attachments or embeds
		# case insensitive search
		# match partial filenames
		or_ = []
		for filename in filenames:
			or_.append({"attachments.filenameWithoutHash": {"$regex": filename, "$options": "i"}})
			or_.append({"embeds.thumbnail.filenameWithoutHash": {"$regex": filename, "$options": "i"}})

		query["$and"].append({"$or": or_})


	if len(in_channel_ids) > 0:
		query["channelId"] = {"$in": in_channel_ids}

	if len(in_category_ids) > 0:
		query["channelId"] = {"$in": in_category_ids}

	if is_pinned is not None:
		query["isPinned"] = is_pinned

	if attachment_is_audio is not None or attachment_is_image is not None or attachment_is_video is not None or attachment_is_other is not None:
		or_ = []
		if attachment_is_audio is not None:
			or_.append({
				"$or": [
					{"attachments.type": "audio"},
					{"embeds.thumbnail.type": "audio"}
				]
			})

		if attachment_is_image is not None:
			or_.append({
				"$or": [
					{"attachments.type": "image"},
					{"embeds.thumbnail.type": "image"}
				]
			})

		if attachment_is_video is not None:
			or_.append({
				"$or": [
					{"attachments.type": "video"},
					{"embeds.thumbnail.type": "video"}
				]
			})

		if attachment_is_other is not None:
			or_.append({
				"$or": [
					{"attachments.type": {"$nin": ["audio", "image", "video"]}},
					{"embeds.thumbnail.type": {"$nin": ["audio", "image", "video"]}}
				]
			})

		query["$and"].append({"$or": or_})

	if containing_links is not None:
		# todo: check if we can really use ^ for faster search without removing valid results
		if containing_links:
			query["content.content"] = {"$regex": "^http|^www"}
		else:
			query["content.content"] = {"$not": {"$regex": "^http|^www"}}

	if is_edited is not None:
		# if message is edited, timestampEdited is not null
		if is_edited:
			query["timestampEdited"] = {"$ne": None}
		else:
			query["timestampEdited"] = None


	if len(message_contains) > 0:
		and_ = []
		for message_should_contain in message_contains:
			and_.append({"content.content": {"$regex": message_should_contain, "$options": "i"}})

		query["$and"].append({"$and": and_})



	if guild_id:
		query["guildId"]=guild_id

	if only_ids:
		limited_fields["_id"]=1

	if query["$and"] == []:
		del query["$and"]

	print(query)

	cursor=collection_messages.find(query, limited_fields)

	if limit > 0:
		cursor.limit(limit)

	if order_by == "newest":
		cursor.sort([("_id", pymongo.DESCENDING)])
	else:
		cursor.sort([("_id", pymongo.ASCENDING)])

	if only_ids:
		ids=[str(id["_id"]) for id in cursor]
		return ids
	else:
		list_of_messages = list(cursor)
		list_of_messages = enrich_messages(list_of_messages)
		return list_of_messages

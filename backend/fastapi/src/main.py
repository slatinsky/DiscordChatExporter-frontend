import datetime
import shutil
from dateutil.relativedelta import relativedelta
import functools
import json
import os
from pprint import pprint
import re
import sys
import traceback
import pymongo
from fastapi import FastAPI, Query
from pydantic import BaseModel

import src.Autocomplete
from .status import get_status
from .guilds import get_guilds
from .channels import get_channels
from .roles import get_roles
from .helpers import get_denylisted_user_ids, get_global_collection, get_allowlisted_guild_ids, is_db_online, pad_id, get_guild_collection

# fix PIPE encoding error on Windows, auto flush print
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')
print = functools.partial(print, flush=True)



app = FastAPI(
	title="DCEF backend api",
	description="This is the backend api for the DCEF viewer.",
	version="0.1.0",
	root_path="/api"
)



def is_compiled():
	if os.path.exists(__file__):
		return False
	else:
		return True


app.include_router(get_status.router)
app.include_router(get_guilds.router)
app.include_router(get_channels.router)
app.include_router(get_roles.router)




def sort_ids_asc(ids: list):
	"""
	Sort ids in ascending order.
	Because sometimes we are querying messages in descending order, we need to reverse the list.
	"""
	return sorted(ids, key=lambda x: int(x))

@app.get("/message-ids-paginated")
async def get_message_ids(channel_id: str, guild_id: str, message_id: str = None, direction="around", limit=100):
	"""
	Returns a subset of message ids for a channel.
	User supplies a message id, for which we return a subset of message ids around it
	- special message id "first" returns the first messages
	- special message id "last" returns the last messages

	Direction can be "around", "before" or "after"
	- "around" returns messages before and after the message id
		- requires message id
	- "before" returns messages before the message id
		- requires message id
	- "after" returns messages after the message id
		- requires message id

	Message id can be 24 long id or special id "first" or "last"


	The endpoint returns special message ids "first" and "last" if there are more messages to load in that direction.

	no cache
	"""
	if not message_id:
		raise Exception("Message id is required")

	if message_id != 'first' and message_id != 'last':
		message_id = pad_id(message_id)

	channel_id = pad_id(channel_id)
	guild_id = pad_id(guild_id)

	limit = int(limit)
	collection_messages = get_guild_collection(guild_id, "messages")

	ids_before = []
	ids_after = []

	denylisted_user_ids = get_denylisted_user_ids()

	if direction == "around" and (message_id != "first" and message_id != "last"):
		limit = limit // 2

	if message_id == "first":
		query = {
			"channelId": channel_id,
			"author._id": {
				"$nin": denylisted_user_ids
			}
		}
		ids_before = ['first']
		ids_after = collection_messages.find(query, {"_id": 1}).sort([("_id", pymongo.ASCENDING)]).limit(limit)
		ids_after = [str(id["_id"]) for id in ids_after]
		if len(ids_after) != limit:
			ids_after.append('last')
		ids = ids_before + ids_after

	elif message_id == "last":
		query = {
			"channelId": channel_id,
			"author._id": {
				"$nin": denylisted_user_ids
			}
		}
		ids_after = ['last']
		ids_before = collection_messages.find(query, {"_id": 1}).sort([("_id", pymongo.DESCENDING)]).limit(limit)
		ids_before = sort_ids_asc([str(id["_id"]) for id in ids_before])
		if len(ids_before) != limit:
			ids_before.insert(0, 'first')
		ids = ids_before + ids_after
	else:
		if direction == "around" or direction == "before":
			ids_before = collection_messages.find(
				{
					"channelId": channel_id,
					"_id": {
						"$lt": message_id
					},
					"author._id": {
						"$nin": denylisted_user_ids
					}
				},
				{"_id": 1}
			).sort([("_id", pymongo.DESCENDING)]).limit(limit)
			ids_before = sort_ids_asc([str(id["_id"]) for id in ids_before])

		if direction == "around" or direction == "after":
			ids_after = collection_messages.find(
				{
					"channelId": channel_id,
					"_id": {
						"$gt": message_id
					},
					"author._id": {
						"$nin": denylisted_user_ids
					}
				},
				{"_id": 1}
			).sort([("_id", pymongo.ASCENDING)]).limit(limit)
			ids_after = [str(id["_id"]) for id in ids_after]

		if direction == "around":
			if len(ids_before) != limit:
				ids_before.insert(0, 'first')
			if len(ids_after) != limit:
				ids_after.append('last')
			if len(ids_before) + len(ids_after) > 2:  # found anything?
				ids = ids_before + [message_id] + ids_after
			else:
				ids = ids_before + ids_after
		elif direction == "before":
			if len(ids_before) != limit:
				ids_before.insert(0, 'first')
			ids = ids_before

		elif direction == "after":
			if len(ids_after) != limit:
				ids_after.append('last')
			ids = ids_after
		else:
			raise Exception("Invalid direction")

	return ids






class MessageRequest(BaseModel):
	message_ids: list
	guild_id: str


@app.post("/messages")
async def get_multiple_message_content(message_req_obj: MessageRequest):
	"""
	Returns the content of multiple messages by their ids.
	All ids must be from the same guild.
	"""
	message_ids = message_req_obj.message_ids
	guild_id = message_req_obj.guild_id

	collection_messages = get_guild_collection(guild_id, "messages")
	denylisted_user_ids = get_denylisted_user_ids()

	messages = collection_messages.find(
		{
			"_id": {
				"$in": message_ids
			},
			"author._id": {
				"$nin": denylisted_user_ids
			}
		}
	)
	list_of_messages = list(messages)
	list_of_messages = enrich_messages(list_of_messages, guild_id)
	return list_of_messages


def channel_names_to_ids(in_channel_ids: list, in_channels: list, guild_id: str):
	"""
	Convert channel names to ids.
	"""
	collection_channels = get_guild_collection(guild_id, "channels")

	if len(in_channels) == 0:
		return in_channel_ids

	out_channel_ids = in_channel_ids.copy()
	for channel in in_channels:
		if channel in out_channel_ids:
			continue

		channel_id = collection_channels.find_one(
			{
				"name": channel
			},
			{
				"_id": 1
			}
		)
		if channel_id:
			out_channel_ids.append(channel_id["_id"])

	return out_channel_ids

def category_names_to_ids(in_category_ids: list, in_categories: list, guild_id: str):
	"""
	Convert category names to ids
	"""
	collection_channels = get_guild_collection(guild_id, "channels")

	if len(in_categories) == 0:
		return in_category_ids

	out_category_ids = in_category_ids.copy()
	for category in in_categories:
		if category in out_category_ids:
			continue

		channel_id = collection_channels.find_one({"category": category}, {"categoryId": 1})
		if channel_id:
			out_category_ids.append(channel_id["categoryId"])

	return out_category_ids


def extend_channels(channels: list, guild_id: str):
	"""
	Extend a list of channels with thread ids and forum post ids.

	Can be also used to extend a list of categories with channel ids.
	In this case, we will not clean category ids from the list, but it causes no problems except for a little bit of performance loss.
	"""
	collection_channels = get_guild_collection(guild_id, "channels")

	if len(channels) == 0:
		return channels

	channels = channels.copy()
	new_channels_cursor = collection_channels.find(
	    {"categoryId": {"$in": channels}})
	channels.extend([channel["_id"] for channel in new_channels_cursor])
	channels = list(set(channels))  # remove duplicates
	return channels

def extend_users(user_ids: list, usernames: list, guild_id: str):
	"""
	Find new user ids by user names.
	exactly match user names
	"""
	collection_authors = get_guild_collection(guild_id, "authors")
	if len(usernames) == 0:
		return user_ids

	user_ids = user_ids.copy()

	or_ = []
	for username in usernames:
		or_.append({"names": username})

	query = {"$or": or_}

	new_user_ids_cursor = collection_authors.find(query, {"_id": 1})
	new_user_ids = [user["_id"] for user in new_user_ids_cursor]
	user_ids.extend(new_user_ids)
	user_ids = list(set(user_ids))  # remove duplicates
	return user_ids


def extend_reactions(reaction_ids: list, reactions: list, guild_id: str):
	"""
	Find new reaction ids by reaction names.
	Support partial or lowercase match.

	"""
	collection_emojis = get_guild_collection(guild_id, "emojis")

	if len(reactions) == 0:
		return reaction_ids

	reaction_ids = reaction_ids.copy()

	or_ = []
	for reaction in reactions:
		or_.append({"name": {"$regex": reaction, "$options": "i"}})

	query = {"$or": or_}

	new_reaction_ids_cursor = collection_emojis.find(query, {"_id": 1})
	new_reaction_ids = [reaction["_id"] for reaction in new_reaction_ids_cursor]
	reaction_ids.extend(new_reaction_ids)
	reaction_ids = list(set(reaction_ids))  # remove duplicates
	return reaction_ids



def get_emotes_from_db(emotes_ids: list, guild_id: str) -> dict:
	"""
	try to find emotes from DB by their name
	use exact match only
	"""
	collection_emojis = get_guild_collection(guild_id, "emojis")
	if len(emotes_ids) == 0:
		return {}

	or_ = []
	for emote_id in emotes_ids:
		or_.append({"_id": emote_id})

	query = {"$or": or_}

	emotes = list(collection_emojis.find(query))
	return emotes

def get_roles_from_db(role_ids: list, guild_id: str) -> dict:
	"""
	try to find roles from DB by their name
	use exact match only
	"""
	collection_roles = get_guild_collection(guild_id, "roles")
	if len(role_ids) == 0:
		return {}

	or_ = []
	for role_id in role_ids:
		or_.append({"_id": role_id})

	query = {"$or": or_}

	roles = list(collection_roles.find(query))
	return roles

def get_channels_from_db(channel_ids: list, guild_id: str) -> dict:
	"""
	try to find channels from DB by their name
	use exact match only
	"""
	collection_channels = get_guild_collection(guild_id, "channels")
	if len(channel_ids) == 0:
		return {}

	or_ = []
	for channel_id in channel_ids:
		or_.append({"_id": channel_id})

	query = {"$or": or_}

	channels = list(collection_channels.find(query))
	return channels

def get_channel_info(channel_id: str, guild_id: str):
	"""
	get channel info by id
	'channel' can be thread or channel or forum post
	"""
	collection_channels = get_guild_collection(guild_id, "channels")
	collection_messages = get_guild_collection(guild_id, "messages")

	channel = collection_channels.find_one(
		{
			"_id": channel_id
		}
	)
	if not channel:
		return {
			"type": "GuildPublicThread",
			"name": "Not found",
		}

	msg_count = collection_messages.count_documents({"channelId": channel_id})
	channel["msgCount"] = msg_count
	return channel


def enrich_messages(list_of_messages: list, guild_id: str) -> list:
	# /^<(a)?:(\w{2,32}):(\d{17,24})>/
	regex = re.compile(r'<(a)?:(\w{2,32}):(\d{17,24})>')

	# add emotes mentioned in message content to messages
	messageid_emoteids = {}  # message id -> list of emote ids
	emotes_ids = []
	for message in list_of_messages:
		for content in message["content"]:
			message_content = content["content"]
			search = regex.findall(message_content)
			messageid_emoteids[message["_id"]] = []
			for emote in search:
				emotes_ids.append(pad_id(emote[2]))
				messageid_emoteids[message["_id"]].append(pad_id(emote[2]))

	emotes_ids = list(set(emotes_ids))

	emotes = get_emotes_from_db(emotes_ids=emotes_ids, guild_id=guild_id)

	for message in list_of_messages:
		message["emotes"] = []
		if message["_id"] in messageid_emoteids:
			for emote_id in messageid_emoteids[message["_id"]]:
				for emote in emotes:
					if emote["_id"] == emote_id:
						message["emotes"].append(emote)
	# END add emotes

	# add roles mentioned in message content to messages
	regex = re.compile(r'<@&(\d{17,24})>')
	role_ids = []
	for message in list_of_messages:
		for content in message["content"]:
			message_content = content["content"]
			search = regex.findall(message_content)
			for role_id in search:
				role_ids.append(pad_id(role_id))

	role_ids = list(set(role_ids))
	roles = get_roles_from_db(role_ids=role_ids, guild_id=guild_id)
	for message in list_of_messages:
		message["roles"] = []
		message_role_ids = []
		for content in message["content"]:
			message_content = content["content"]
			search = regex.findall(message_content)
			for role_id in search:
				message_role_ids.append(pad_id(role_id))

		for role_id in message_role_ids:
			for role in roles:
				if role["_id"] == role_id:
					message["roles"].append(role)
	# END add roles

	# add channels
	# <#123>
	regex = re.compile(r'<#(\d{17,24})>')
	channel_ids = []
	for message in list_of_messages:
		for content in message["content"]:
			message_content = content["content"]
			search = regex.findall(message_content)
			for channel_id in search:
				channel_ids.append(pad_id(channel_id))

	channel_ids = list(set(channel_ids))
	channels = get_channels_from_db(channel_ids=channel_ids, guild_id=guild_id)
	for message in list_of_messages:
		message["channels"] = []
		message_channel_ids = []
		for content in message["content"]:
			message_content = content["content"]
			search = regex.findall(message_content)
			for channel_id in search:
				message_channel_ids.append(pad_id(channel_id))

		for channel_id in message_channel_ids:
			for channel in channels:
				if channel["_id"] == channel_id:
					message["channels"].append(channel)
	# END add channels


	for message in list_of_messages:
		if message["type"] == "ThreadCreated":
			message["thread"] = get_channel_info(message["reference"]["channelId"], guild_id)

	return list_of_messages

SEARCH_CATEGORIES = [
	{
		"key": 'from',
		"description": 'user',
		"description2": 'exact string match',
		"type": 'string',
		"multiple": True,
		"mapTo": "from_users",
		"autocompleteApi": "users",
	},
	{
		"key": 'mentions',
		"description": 'user',
		"description2": 'exact string match',
		"type": 'string',
		"multiple": True,
		"mapTo": "mentions_users",
		"autocompleteApi": "users",
	},
	{
		"key": 'has',
		"description": 'link, embed or file',
		"description2": 'choice',
		"type": 'choice',
		"multiple": True,
		"mapTo": "has",
		"autocompleteApi": "has",
	},
	{
		"key": 'before',
		"description": 'specific date',
		"description2": 'in format YYYY-MM-DD, YYYY-MM or YYYY (UTC)',
		"type": 'date',
		"multiple": True,
		"mapTo": "before",
		"autocompleteApi": None,
	},
	{
		"key": 'during',
		"description": 'specific date',
		"description2": 'in format YYYY-MM-DD, YYYY-MM or YYYY (UTC)',
		"type": 'date',
		"multiple": True,
		"mapTo": "during",
		"autocompleteApi": None,
	},
	{
		"key": 'after',
		"description": 'specific date',
		"description2": 'in format YYYY-MM-DD, YYYY-MM or YYYY (UTC)',
		"type": 'date',
		"multiple": True,
		"mapTo": "after",
		"autocompleteApi": None,
	},
	{
		"key": 'in',
		"description": 'channel',
		"description2": "exact string match",
		"type": 'string',
		"multiple": True,
		"mapTo": "in_channels",
		"autocompleteApi": "channels",
	},
	{
		"key": 'pinned',
		"description": 'true or false',
		"description2": "boolean",
		"type": 'boolean',
		"multiple": False,
		"mapTo": "is_pinned",
		"autocompleteApi": None,
	},
	{
		"key": 'edited',
		"description": 'true or false',
		"description2": "boolean",
		"type": 'boolean',
		"multiple": False,
		"mapTo": "is_edited",
		"autocompleteApi": None,
	},
	{
		"key": 'deleted',
		"description": 'true or false',
		"description2": "boolean",
		"type": 'boolean',
		"multiple": False,
		"mapTo": "is_deleted",
		"autocompleteApi": None,
	},
	{
		"key": 'reaction_from',
		"description": 'user',
		"description2": "exact string match",
		"type": 'string',
		"multiple": True,
		"mapTo": "reaction_from",
		"autocompleteApi": "users",
	},
	{
		"key": 'reaction',
		"description": 'emoji',
		"description2": "partial regex match",
		"type": 'string',
		"multiple": True,
		"mapTo": "reactions",
		"autocompleteApi": "reactions",
	},
	{
		"key": 'extension',
		"description": 'pdf/png/jpg/etc',
		"description2": "exact match",
		"type": 'string',
		"multiple": True,
		"mapTo": "extensions",
		"autocompleteApi": "extensions",
	},
	{
		"key": 'file',
		"description": 'file',
		"description2": "partial regex match",
		"type": 'string',
		"multiple": True,
		"mapTo": "filenames",
		"autocompleteApi": "filenames",
	},
	{
		"key": 'category',
		"description": 'category',
		"description2": "exact string match",
		"type": 'string',
		"multiple": True,
		"mapTo": "in_categories",
		"autocompleteApi": "categories",
	},
	{
		"key": 'limit',
		"description": 'number',
		"description2": "default 100000, 0 disables limit",
		"type": 'number',
		"multiple": False,
		"mapTo": "limit",
		"autocompleteApi": None,
	},
		{
		"key": 'message_id',
		"description": 'message id',
		"description2": "discord snowflake",
		"type": 'discord_snowflake',
		"multiple": True,
		"mapTo": "message_ids",
		"autocompleteApi": None,
	},
	{
		"key": 'in_id',
		"description": 'channel id',
		"description2": "discord snowflake",
		"type": 'discord_snowflake',
		"multiple": True,
		"mapTo": "in_channel_ids",
		"autocompleteApi": None,
	},
	{
		"key": 'category_id',
		"description": 'category id',
		"description2": "discord snowflake",
		"type": 'discord_snowflake',
		"multiple": True,
		"mapTo": "in_category_ids",
		"autocompleteApi": None,
	},
	{
		"key": 'from_id',
		"description": 'author id',
		"description2": "discord snowflake",
		"type": 'discord_snowflake',
		"multiple": True,
		"mapTo": "from_user_ids",
		"autocompleteApi": None,
	},
	{
		"key": 'mentions_id',
		"description": 'author id',
		"description2": "discord snowflake",
		"type": 'discord_snowflake',
		"multiple": True,
		"mapTo": "mentions_user_ids",
		"autocompleteApi": None,
	},
	{
		"key": 'reaction_from_id',
		"description": 'user id',
		"description2": "discord snowflake",
		"type": 'discord_snowflake',
		"multiple": True,
		"mapTo": "reaction_from_ids",
		"autocompleteApi": None,
	},
	{
		"key": 'reaction_id',
		"description": 'emoji id',
		"description2": "discord snowflake",
		"type": 'discord_snowflake',
		"multiple": True,
		"mapTo": "reaction_ids",
		"autocompleteApi": None,
	},
]



@app.get("/search-autocomplete")
def search_autocomplete(guild_id: str, key: str = None, value: str = None, limit: int = 100):
	if (key == None or value == None):
		return []

	padded_guild_id = pad_id(guild_id)

	if (key == "users"):
		return Autocomplete.autocomplete_users(padded_guild_id, value, limit)
	elif (key == "filenames"):
		return Autocomplete.autocomplete_filenames(padded_guild_id, value, limit)
	elif (key == "extensions"):
		return Autocomplete.autocomplete_extensions(padded_guild_id, value, limit)
	elif (key == "reactions"):
		return Autocomplete.autocomplete_reactions(padded_guild_id, value, limit)
	elif (key == "channels"):
		return Autocomplete.autocomplete_channels(padded_guild_id, value, limit)
	elif (key == "categories"):
		return Autocomplete.autocomplete_categories(padded_guild_id, value, limit)
	elif (key == "has"):
		return Autocomplete.autocomplete_has(padded_guild_id, value, limit)
	else:
		return []


@app.get("/search-categories")
def search_categories():
	return SEARCH_CATEGORIES


def username_discriminate_user(username: str):
	"""
	if username doesn't end with #xxxx, add #0000
	"""
	if re.match(r'.+#\d{4}$', username):
		return username
	else:
		return f"{username}#0000"


def parse_prompt(prompt: str):
	"""
	Parses a prompt into categories.
	"""
	search = {
		"message_contains": [],          # words that must be in the message content (and)
		"message_ids": [],               # message ids (strings) (or)
		"from_user_ids": [],             # user ids (strings) (or)
		"from_users": [],                # user names (or)
		"reaction_from_ids": [],         # user ids (strings) (or)
		"reaction_from": [],             # user names (or)
		"mentions_user_ids": [],         # user ids (strings) (or)
		"mentions_users": [],            # user names (or)
		"reaction_ids": [],              # emoji ids (strings) (or)
		"reactions": [],                 # emoji names (or)
		"extensions": [],                # file extensions like "pdf", "java" (or)
		"filenames": [],                 # file names (or)
		"in_channel_ids": [],            # channel ids (strings) (or)
		"in_channels": [],               # channel names (or)
		"in_category_ids": [],           # category ids (strings) (or)
		"in_categories": [],             # category names (or)
		"is_pinned": None,               # boolean (None means both)
		"attachment_is_audio": None,     # boolean (None means both) (or in group attachment_is)
		"attachment_is_image": None,     # boolean (None means both) (or in group attachment_is)
		"attachment_is_video": None,     # boolean (None means both) (or in group attachment_is)
		"containing_links": None,        # boolean (None means both)
		"containing_attachments": None,  # TODO: implement
		"containing_embeds": None,       # TODO: implement
		"containing_stickers": None,
		"is_edited": None,               # boolean (None means both)
		"is_deleted": None,              # boolean (None means both)
		"limit": 100000,                 # max number of messages to return (int)
		"before": None,
		"after" : None,
	}

	# loop throught all characters
	inside_quotes = False
	word = ""
	valid_search_keys = [x["key"] for x in SEARCH_CATEGORIES]
	current_key = None

	searchCategoriesMap = {x["key"]: x for x in SEARCH_CATEGORIES}

	stripped_prompt = prompt.strip() + " "

	for i, char in enumerate(stripped_prompt):
		# ignore escaped quote
		if char == '\\' and (i == len(stripped_prompt) - 1 or stripped_prompt[i + 1] == '"'):
			continue

		# ignore escaped quote, flip inside_quotes
		if char == '"' and (i == 0 or stripped_prompt[i - 1] != "\\"):
			inside_quotes = not inside_quotes
			continue

		if char == ":" and not inside_quotes and word in valid_search_keys:
			current_key = word
			word = ""
			continue

		if char == ' ' and not inside_quotes:
			if current_key in valid_search_keys:
				search_category = searchCategoriesMap[current_key]

				if search_category["type"] == "boolean":
					if word.lower() == "true":
						word = True
						search[search_category["mapTo"]] = True
					elif word.lower() == "false":
						word = False
						search[search_category["mapTo"]] = False
					else:
						word = None
				elif search_category["type"] == "number":
					try:
						word = int(word)
						search[search_category["mapTo"]] = word
					except ValueError:
						word = None
						print("Invalid number")
				elif search_category["type"] == "choice":
					if current_key.lower() == "has":
						if word.lower() == "link":
							search["containing_links"] = True
						elif word == "embed":
							search["containing_embeds"] = True
						elif word == "file":
							search["containing_attachments"] = True
						elif word == "video":
							search["attachment_is_video"] = True
						elif word == "image":
							search["attachment_is_image"] = True
						elif word == "sound":
							search["attachment_is_audio"] = True
						elif word == "sticker":
							search["containing_stickers"] = True
				elif search_category["type"] == "date":
					yyy_mm_dd_regex = re.compile(r"^(\d{4})-(\d{1,2})-(\d{1,2})$")
					yyy_mm_regex = re.compile(r"^(\d{4})-(\d{1,2})$")
					yyy_regex = re.compile(r"^(\d{4})$")
					year = None
					month = None
					day = None

					match_found = False

					if yyy_mm_dd_regex.match(word):
						match = yyy_mm_dd_regex.match(word)
						year = int(match.group(1))
						month = int(match.group(2))
						day = int(match.group(3))
						match_found = True
						date_from = datetime.date(year, month, day)
						date_to = date_from + relativedelta(days=1)


					elif yyy_mm_regex.match(word):
						match = yyy_mm_regex.match(word)
						year = int(match.group(1))
						month = int(match.group(2))
						match_found = True
						date_from = datetime.date(year, month, 1)
						date_to = date_from + relativedelta(months=1)

					elif yyy_regex.match(word):
						match = yyy_regex.match(word)
						year = int(match.group(1))
						match_found = True
						date_from = datetime.date(year, 1, 1)
						date_to = date_from + relativedelta(years=1)

					if match_found:
						if current_key.lower() == "before":
							search["before"] = f"{date_from.year}-{str(date_from.month).zfill(2)}-{str(date_from.day).zfill(2)}T00:00:00"
						if current_key.lower() == "after":
							search["after"] = f"{date_to.year}-{str(date_to.month).zfill(2)}-{str(date_to.day).zfill(2)}T00:00:00"
						if current_key.lower() == "during":
							search["after"] = f"{date_from.year}-{str(date_from.month).zfill(2)}-{str(date_from.day).zfill(2)}T00:00:00"
							search["before"] = f"{date_to.year}-{str(date_to.month).zfill(2)}-{str(date_to.day).zfill(2)}T00:00:00"


				elif search_category["type"] == "string" or search_category["type"] == "discord_snowflake":
					search[search_category["mapTo"]].append(word)
				else:
					print("Invalid search category type", search_category["type"])

				current_key = None

			elif word != "":
				search["message_contains"].append(word)

			word = ""
			continue

		word += char

	print("search", search)
	return search




@app.get("/search")
async def search_messages(guild_id: str, prompt: str = None, only_ids: bool = True, order_by: str = Query("newest", enum=["newest", "oldest"])):
	"""
	Searches for messages that contain the prompt.
	"""

	collection_messages = get_guild_collection(guild_id, "messages")

	try:
		# todo: parse prompt
		search = parse_prompt(prompt)
		message_contains = search["message_contains"]
		message_ids = search["message_ids"]
		from_user_ids = search["from_user_ids"]
		from_users = search["from_users"]
		from_users = [username_discriminate_user(username) for username in from_users]
		reaction_from_ids = search["reaction_from_ids"]
		reaction_from = search["reaction_from"]
		reaction_from = [username_discriminate_user(username) for username in reaction_from]
		mentions_user_ids = search["mentions_user_ids"]
		mentions_users = search["mentions_users"]
		mentions_users = [username_discriminate_user(username) for username in mentions_users]
		reaction_ids = search["reaction_ids"]
		reactions = search["reactions"]
		extensions = search["extensions"]
		filenames = search["filenames"]
		in_channel_ids = search["in_channel_ids"]
		in_channels = search["in_channels"]
		in_category_ids = search["in_category_ids"]
		in_categories = search["in_categories"]
		is_pinned = search["is_pinned"]
		attachment_is_audio = search["attachment_is_audio"]
		attachment_is_image = search["attachment_is_image"]
		attachment_is_video = search["attachment_is_video"]

		containing_attachments = search["containing_attachments"]
		containing_embeds = search["containing_embeds"]
		containing_stickers = search["containing_stickers"]

		containing_links = search["containing_links"]
		is_edited = search["is_edited"]
		is_deleted = search["is_deleted"]
		limit = search["limit"]

		before = search["before"]
		after = search["after"]

		# clean up
		message_contains = [word.lower() for word in message_contains]
		message_ids = [pad_id(id) for id in message_ids]

		denylisted_user_ids = get_denylisted_user_ids()
		from_user_ids = [pad_id(id) for id in from_user_ids]
		from_user_ids = extend_users(from_user_ids, from_users, guild_id)
		from_user_ids = [user_id for user_id in from_user_ids if user_id not in denylisted_user_ids]  # remove denylisted users

		print("from_user_ids", from_user_ids)

		reaction_from_ids = [pad_id(id) for id in reaction_from_ids]
		reaction_from_ids = extend_users(reaction_from_ids, reaction_from, guild_id)
		reaction_from_ids = [user_id for user_id in reaction_from_ids if user_id not in denylisted_user_ids]    # remove denylisted users

		mentions_user_ids = [pad_id(id) for id in mentions_user_ids]
		mentions_user_ids = extend_users(mentions_user_ids, mentions_users, guild_id)
		mentions_user_ids = [user_id for user_id in mentions_user_ids if user_id not in denylisted_user_ids]    # remove denylisted users

		reaction_ids = [pad_id(id) for id in reaction_ids]
		reactions = [reaction.lower() for reaction in reactions]
		reaction_ids = extend_reactions(reaction_ids, reactions, guild_id)
		extensions = [ext.lower() for ext in extensions]
		in_channel_ids = channel_names_to_ids(in_channel_ids, in_channels, guild_id)
		in_channel_ids = [pad_id(id) for id in in_channel_ids]
		in_channel_ids = extend_channels(in_channel_ids, guild_id)      # extend channels with threads and forum posts
		in_category_ids = [pad_id(id) for id in in_category_ids]
		in_category_ids = category_names_to_ids(in_category_ids, in_categories, guild_id)
		in_category_ids = [pad_id(id) for id in in_category_ids]
		in_category_ids = extend_channels(in_category_ids, guild_id)  # extend categories with channels
		in_category_ids = extend_channels(in_category_ids, guild_id)  # extend channels with threads and forum posts



		# query builder
		query = {}
		limited_fields = {}

		query["$and"] = []

		# assuming that timestamp is always in UTC (comparing strings)
		# it that will be an issue, there is always an option to compare using discord snowflakes (message id)
		if before is not None:
			query["$and"].append({"timestamp": {"$lt": before}})

		if after is not None:
			query["$and"].append({"timestamp": {"$gt": after}})

		if len(message_ids) > 0:
			query["_id"] = {"$in": message_ids}

		if len(from_user_ids) > 0 or len(denylisted_user_ids) > 0:
			query["author._id"] = {}
			if len(from_user_ids) > 0:
				query["author._id"]["$in"] = from_user_ids
			if len(denylisted_user_ids) > 0:
				query["author._id"]["$nin"] = denylisted_user_ids

		if len(reaction_from_ids) > 0:
			query["reactions.users._id"] = {"$in": reaction_from_ids}

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

		if attachment_is_audio is not None or attachment_is_image is not None or attachment_is_video is not None:
			or_ = []
			if attachment_is_audio is not None:
				if not attachment_is_audio:
					or_.append({
						"$and": [
							{"attachments.type": {"$nin": ["audio"]}},
							{"embeds.thumbnail.type": {"$nin": ["audio"]}}
						]
					})
				else:
					or_.append({
						"$or": [
							{"attachments.type": "audio"},
							{"embeds.thumbnail.type": "audio"}
						]
					})

			if attachment_is_image is not None:
				if not attachment_is_image:
					or_.append({
						"$and": [
							{"attachments.type": {"$nin": ["image"]}},
							{"embeds.thumbnail.type": {"$nin": ["image"]}}
						]
					})
				else:
					or_.append({
						"$or": [
							{"attachments.type": "image"},
							{"embeds.thumbnail.type": "image"}
						]
					})

			if attachment_is_video is not None:
				if not attachment_is_video:
					or_.append({
						"$and": [
							{"attachments.type": {"$nin": ["video"]}},
							{"embeds.thumbnail.type": {"$nin": ["video"]}}
						]
					})
				else:
					or_.append({
						"$or": [
							{"attachments.type": "video"},
							{"embeds.thumbnail.type": "video"}
						]
					})

			query["$and"].append({"$or": or_})


		if containing_links is not None:
			# todo: check if we can really use ^ for faster search without removing valid results
			if containing_links:
				query["content.content"] = {"$regex": "^http|^www"}
			# else:
			# 	query["content.content"] = {"$not": {"$regex": "^http|^www"}}

		if containing_stickers is not None:
			if containing_stickers:
				query["stickers"] = {"$exists": True}

		if containing_embeds is not None:
			if containing_embeds:
				query["embeds"] = {"$exists": True}

		if containing_attachments is not None:
			if containing_attachments:
				query["attachments"] = {"$exists": True}


		if is_edited is not None:
			# if message is edited, timestampEdited is not null
			if is_edited:
				query["timestampEdited"] = {"$ne": None}
			else:
				query["timestampEdited"] = None

		if is_deleted is not None:
			if is_deleted:
				query["isDeleted"] = True
			else:
				query["$or"] = [{"isDeleted": False}, {"isDeleted": None}]


		if len(message_contains) > 0:
			and_ = []
			for message_should_contain in message_contains:
				and_.append({
					"$or": [
						{
							"content.content": {
								"$regex": message_should_contain,
								"$options": "i"
							}
						},
						{
							"embeds.title": {
								"$regex": message_should_contain,
								"$options": "i"
							},
						},
						{
							"embeds.description": {
								"$regex": message_should_contain,
								"$options": "i"
							},
						},
					]
				})

			query["$and"].append({"$and": and_})

		if only_ids:
			limited_fields["_id"]=1

		if query["$and"] == []:
			del query["$and"]

		print("query")
		pprint(query)

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
			list_of_messages = enrich_messages(list_of_messages, guild_id)
			return list_of_messages
	except Exception as e:
		print("/search error:")
		traceback.print_exc()
		return ["error"]

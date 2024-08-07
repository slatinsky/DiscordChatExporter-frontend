import datetime
import json
import traceback
import re
from dateutil.relativedelta import relativedelta

from ..common.cursor_pagination import cursor_pagination

from ..common.enrich_messages import enrich_messages_with_referenced
from ..common.helpers import pad_id, print_json, simplify_mongo_query
from ..common.Database import Database

from fastapi import APIRouter, Query

from ..common.Database import Database


router = APIRouter(
	prefix="",
	tags=["search"]
)


SEARCH_CATEGORIES = []
with open("src/search/search_categories.json", "r", encoding="utf-8") as f:
    SEARCH_CATEGORIES = json.load(f)




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
		# "limit": 100000,                 # max number of messages to return (int)
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

	print("search")
	print_json(search)
	return search


def category_names_to_ids(in_category_ids: list, in_categories: list, guild_id: str):
	"""
	Convert category names to ids
	"""
	collection_channels = Database.get_guild_collection(guild_id, "channels")

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
	collection_channels = Database.get_guild_collection(guild_id, "channels")

	if len(channels) == 0:
		return channels

	channels = channels.copy()
	new_channels_cursor = collection_channels.find(
	    {"categoryId": {"$in": channels}})
	channels.extend([channel["_id"] for channel in new_channels_cursor])
	channels = list(set(channels))  # remove duplicates
	return channels


def channel_names_to_ids(in_channel_ids: list, in_channels: list, guild_id: str):
	"""
	Convert channel names to ids.
	"""
	collection_channels = Database.get_guild_collection(guild_id, "channels")

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

def extend_reactions(reaction_ids: list, reactions: list, guild_id: str):
	"""
	Find new reaction ids by reaction names.
	Support partial or lowercase match.

	"""
	collection_emojis = Database.get_guild_collection(guild_id, "emojis")

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


def extend_users(user_ids: list, usernames: list, guild_id: str):
	"""
	Find new user ids by user names.
	exactly match user names
	"""
	collection_authors = Database.get_guild_collection(guild_id, "authors")
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





@router.get("/guild/search")
async def search_messages(guild_id: str, prompt: str = None, prev_page_cursor: str | None = None, around_page_cursor: str | None = None, next_page_cursor: str | None = None, limit=100):
	return await search_messages_(guild_id, prompt, prev_page_cursor, around_page_cursor, next_page_cursor, limit, return_count=False)

@router.get("/guild/search/count")
async def count_messages(guild_id: str, prompt: str = None, prev_page_cursor: str | None = None, around_page_cursor: str | None = None, next_page_cursor: str | None = None, limit=100):
	return await search_messages_(guild_id, prompt, prev_page_cursor, around_page_cursor, next_page_cursor, limit, return_count=True)


async def search_messages_(guild_id: str, prompt: str = None, prev_page_cursor: str | None = None, around_page_cursor: str | None = None, next_page_cursor: str | None = None, limit=100, return_count: bool = False):
	"""
	Searches for messages that contain the prompt.
	"""

	collection_messages = Database.get_guild_collection(guild_id, "messages")

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
		# limit = search["limit"]

		before = search["before"]
		after = search["after"]

		# clean up
		message_contains = [word.lower() for word in message_contains]
		message_ids = [pad_id(id) for id in message_ids]

		denylisted_user_ids = Database.get_denylisted_user_ids()
		from_user_ids = [pad_id(id) for id in from_user_ids]
		from_user_ids = extend_users(from_user_ids, from_users, guild_id)
		from_user_ids = [user_id for user_id in from_user_ids if user_id not in denylisted_user_ids]  # remove denylisted users

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
		query["$and"] = []

		# assuming that timestamp is always in UTC (comparing strings)
		# it that will be an issue, there is always an option to compare using discord snowflakes (message id)
		if before is not None:
			query["$and"].append({"timestamp": {"$lt": before}})

		if after is not None:
			query["$and"].append({"timestamp": {"$gt": after}})

		if len(message_ids) > 0:
			query["_id"] = {"$in": message_ids}

		if len(from_user_ids) > 0:
			query["author._id"] = {"$in": from_user_ids}
		elif len(denylisted_user_ids) > 0:
			query["author._id"] = {"$nin": denylisted_user_ids}

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


		if containing_links is not None and containing_links:
			query["content.content"] = {"$regex": "^http|^www"}

		if containing_stickers is not None and containing_stickers:
			query["stickers"] = {"$exists": True}

		if containing_embeds is not None and containing_embeds:
			query["embeds"] = {"$exists": True}

		if containing_attachments is not None and containing_attachments:
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

		query = simplify_mongo_query(query)

		print("query")
		print_json(query)

		if return_count:
			return collection_messages.count_documents(query)
		else:
			return cursor_pagination(collection_messages, query, prev_page_cursor, around_page_cursor, next_page_cursor, limit)



	except Exception as e:
		print("/search error:")
		traceback.print_exc()
		return ["error"]


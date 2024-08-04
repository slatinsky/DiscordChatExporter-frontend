import re
from .Database import Database
from .helpers import pad_id


def get_emotes_from_db(emotes_ids: list, guild_id: str) -> dict:
	"""
	try to find emotes from DB by their name
	use exact match only
	"""
	collection_emojis = Database.get_guild_collection(guild_id, "emojis")
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
	collection_roles = Database.get_guild_collection(guild_id, "roles")
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
	collection_channels = Database.get_guild_collection(guild_id, "channels")
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
	collection_channels = Database.get_guild_collection(guild_id, "channels")
	collection_messages = Database.get_guild_collection(guild_id, "messages")

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
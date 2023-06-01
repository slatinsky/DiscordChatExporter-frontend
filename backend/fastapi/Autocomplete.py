def autocomplete_categories(db, guild_id: str, partial_category: str, limit: int):
	"""
	Searches for categories.
	limited to {limit} results * 10
	"""
	collection_channels = db["channels"]

	limit = limit * 10

	# type is not "GuildPublicThread" or "GuildPrivateThread"
	query = {
		"category": {
			"$regex": partial_category,
			"$options": "i"
		},
		"guildId": guild_id,
		"type": {
			"$nin": [
				"GuildPublicThread",
				"GuildPrivateThread"
			]
		}
	}
	cursor = collection_channels.find(query, {"category": 1}).limit(limit).sort([("category", 1)])
	category_names = []
	for category in cursor:
		category_names.append(category['category'])

	# remove duplicates
	category_names = list(set(category_names))
	return category_names

def autocomplete_channels(db, guild_id: str, partial_channel: str, limit: int):
	"""
	Searches for channels.
	limited to {limit} results
	"""
	collection_channels = db["channels"]

	query = {"name": {"$regex": partial_channel, "$options": "i"}, "guildId": guild_id}
	cursor = collection_channels.find(query, {"name": 1}).limit(limit).sort([("name", 1)])
	channel_names = []
	for channel in cursor:
		channel_names.append(channel['name'])

	# remove duplicates
	channel_names = list(set(channel_names))
	return channel_names

def autocomplete_reactions(db, guild_id: str, partial_reaction: str, limit: int):
	"""
	Searches for reactions.
	limited to {limit} results
	"""
	collection_emojis = db["emojis"]

	query = {"name": {"$regex": partial_reaction, "$options": "i"}, "$or": [{"guild_id": guild_id}, {"guild_id": None}]}
	cursor = collection_emojis.find(query, {"name": 1}).limit(limit).sort([("name", 1)])
	reaction_names = []
	for reaction in cursor:
		reaction_names.append(reaction['name'])

	# remove duplicates
	reaction_names = list(set(reaction_names))
	# TODO: by removing duplicates, we are not respecting the limit anymore (more results could exist)
	return reaction_names


def autocomplete_filenames(db, guild_id: str, partial_filename: str, limit: int):
	"""
	Searches for filenames.
	limited to {limit} results
	"""
	collection_assets = db["assets"]

	query = {"filenameWithoutHash": {"$regex": partial_filename, "$options": "i"}}
	cursor = collection_assets.find(query, {"filenameWithoutHash": 1}).limit(limit).sort([("filenameWithoutHash", 1)])
	filenames = []
	for filename in cursor:
		filenames.append(filename['filenameWithoutHash'])

	# remove duplicates
	filenames = list(set(filenames))
	# TODO: by removing duplicates, we are not respecting the limit anymore (more results could exist)
	return filenames


def autocomplete_users(db, guild_id: str, partial_user_name: str, limit: int):
	"""
	Searches for users by name.
	limited to {limit} results
	only shows users that have messages in the guild {guild_id}
	"""
	collection_authors = db["authors"]

	query = {
		"guildIds": guild_id,
		"names": {
			"$regex": partial_user_name, "$options": "i"
		}
	}
	cursor = collection_authors.find(query, {"names": 1}).limit(limit).sort([("names", 1)])
	authors= []
	for author in cursor:
		authors.append(author['names'][0])
	return authors
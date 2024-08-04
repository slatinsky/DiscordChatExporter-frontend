import pymongo
from fastapi import APIRouter

from ..common.Database import Database, pad_id

router = APIRouter(
	prefix="",
	tags=["messages"]
)


def sort_ids_asc(ids: list):
	"""
	Sort ids in ascending order.
	Because sometimes we are querying messages in descending order, we need to reverse the list.
	"""
	return sorted(ids, key=lambda x: int(x))

@router.get("/message-ids-paginated")
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
	collection_messages = Database.get_guild_collection(guild_id, "messages")

	ids_before = []
	ids_after = []

	denylisted_user_ids = Database.get_denylisted_user_ids()

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

import pymongo
from fastapi import APIRouter

from ..common.Database import Database

router = APIRouter(
	prefix="",
	tags=["guilds"]
)

@router.get("/guilds")
async def get_guilds():
	"""
	Returns a list of guilds
	If allowlist is enabled (by not being an empty list), only allowlisted guilds will be returned.

	all other allowlist logic is handled by get_guild_collection() method - it won't return a collection for non-allowlisted guilds
	"""
	collection_guilds = Database.get_global_collection("guilds")
	allowlisted_guild_ids = Database.get_allowlisted_guild_ids()

	if len(allowlisted_guild_ids) == 0:
		cursor = collection_guilds.find().sort([("msg_count", pymongo.DESCENDING)])
	else:
		cursor = collection_guilds.find(
			{
				"_id": {
					"$in": allowlisted_guild_ids
				}
			}
		).sort([("msg_count", pymongo.DESCENDING)])
	return list(cursor)
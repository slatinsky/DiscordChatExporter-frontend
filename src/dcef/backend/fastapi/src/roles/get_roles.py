import pymongo
from fastapi import APIRouter

from ..common.Database import Database

router = APIRouter(
	prefix="",
	tags=["guild"]
)


@router.get("/guild/roles")
async def get_roles(guild_id: str):
	"""
	Returns a list of all roles in a guild.
	"""
	collection_roles = Database.get_guild_collection(guild_id, "roles")
	cursor = collection_roles.find().sort([("position", pymongo.DESCENDING)])
	return list(cursor)

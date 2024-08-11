from fastapi import APIRouter

from ..common.Database import Database

router = APIRouter(
	prefix="",
	tags=["guild"]
)


@router.get("/guild/channels")
async def get_channels(guild_id: str):
	"""
	Returns a list of all channels in a guild.
	That includes channels, threads and forum posts.
	"""
	collection_channels = Database.get_guild_collection(guild_id, "channels")
	cursor = collection_channels.find()
	return list(cursor)

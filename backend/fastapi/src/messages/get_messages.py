import re
from fastapi import APIRouter
from pydantic import BaseModel
from ..common.helpers import pad_id
from ..common.cursor_pagination import cursor_pagination


from ..common.Database import Database

router = APIRouter(
	prefix="",
	tags=["messages"]
)

class MessageRequest(BaseModel):
	message_ids: list
	guild_id: str


@router.get("/guild/messages")
# async def get_message_ids(channel_id: str, guild_id: str, message_id: str = None, direction="around", limit=100):
async def get_messages_cursor_pagination(channel_id: str, guild_id: str, prev_page_cursor: str | None = None, around_page_cursor: str | None = None, next_page_cursor: str | None = None, limit=100):
	"""
	Returns a subset of messages for a channel.
	Cursor based pagination.
	Returns cursor for the next and previous page.
	"""

	#### ------------ INPUT VALIDATION ------------ ####
	if re.match(r"^\d+$", guild_id) is None:
		raise Exception("guild_id is not numeric")
	if re.match(r"^\d+$", channel_id) is None:
		raise Exception("channel_id is not numeric")
	#### ------------ end INPUT VALIDATION ------------ ####

	guild_id = pad_id(guild_id)
	channel_id = pad_id(channel_id)

	collection_messages = Database.get_guild_collection(guild_id, "messages")
	denylisted_user_ids = Database.get_denylisted_user_ids()

	base_query = {
		"channelId": channel_id,
		"author._id": {
			"$nin": denylisted_user_ids
		}
	}

	return cursor_pagination(collection_messages, base_query, prev_page_cursor, around_page_cursor, next_page_cursor, limit)
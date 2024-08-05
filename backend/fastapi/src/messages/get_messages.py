from fastapi import APIRouter
from pydantic import BaseModel
from ..common.enrich_messages import enrich_messages_with_referenced


from ..common.Database import Database

router = APIRouter(
	prefix="",
	tags=["messages"]
)

class MessageRequest(BaseModel):
	message_ids: list
	guild_id: str


@router.post("/messages")
async def get_multiple_message_content(message_req_obj: MessageRequest):
	"""
	Returns the content of multiple messages by their ids.
	All ids must be from the same guild.
	"""
	message_ids = message_req_obj.message_ids
	guild_id = message_req_obj.guild_id

	collection_messages = Database.get_guild_collection(guild_id, "messages")
	denylisted_user_ids = Database.get_denylisted_user_ids()

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
	list_of_messages_enriched = enrich_messages_with_referenced(list_of_messages, guild_id)
	return list_of_messages_enriched



from fastapi import APIRouter
from ..common.helpers import pad_id
from . import Autocomplete

router = APIRouter(
	prefix="",
	tags=["search"]
)


@router.get("/guild/search/autocomplete")
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
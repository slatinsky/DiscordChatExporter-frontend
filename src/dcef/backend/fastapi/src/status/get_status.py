
from fastapi import APIRouter

from ..common.Database import Database

router = APIRouter(
	prefix="",
	tags=["status"]
)

@router.get("/")
async def api_status():
	"""
	Returns the status of the api and the database.
	"""
	try:
		database_status = "online" if Database.is_online() else "offline"
	except:
		database_status = "offline"
	return {
		"api_backend": "online",  # it api_backend is offline, the api would not respond
		"database": database_status
	}
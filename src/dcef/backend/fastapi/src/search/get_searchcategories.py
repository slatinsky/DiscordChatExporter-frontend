import json
from fastapi import APIRouter

from ..common.Database import Database

router = APIRouter(
	prefix="",
	tags=["messages"]
)


SEARCH_CATEGORIES = []
with open("src/search/search_categories.json", "r", encoding="utf-8") as f:
    SEARCH_CATEGORIES = json.load(f)

@router.get("/guild/search/search-categories")
def search_categories():
	return SEARCH_CATEGORIES
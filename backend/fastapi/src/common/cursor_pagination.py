import pymongo
import re

from ..common.Database import pad_id


def cursor_pagination(collection_messages, query: dict, prev_page_cursor: str | None = None, around_page_cursor: str | None = None, next_page_cursor: str | None = None, limit=100):
	#### ------------ INPUT VALIDATION ------------ ####
	# only one of prev_id or next_id can be provided
	if prev_page_cursor is None and next_page_cursor is None and around_page_cursor is None:
		next_page_cursor = pad_id(0) # by default start from the beginning
		# raise Exception("Either prev_page_cursor, around_page_cursor or next_page_cursor must be provided")
	if prev_page_cursor is not None and next_page_cursor is not None and around_page_cursor is not None:
		raise Exception("Only one of around_page_cursor, prev_page_cursor or next_page_cursor can be provided")

	# validate message_id is numeric
	if prev_page_cursor is not None and re.match(r"^\d+$", prev_page_cursor) is None:
		raise Exception("prev_page_cursor is not numeric")

	if next_page_cursor is not None and re.match(r"^\d+$", next_page_cursor) is None:
		raise Exception("next_page_cursor  is not numeric")

	if around_page_cursor is not None and re.match(r"^\d+$", around_page_cursor) is None:
		raise Exception("around_page_cursor is not numeric")
	#### ------------ end INPUT VALIDATION ------------ ####


	if prev_page_cursor is not None:
		prev_page_cursor = pad_id(prev_page_cursor)
	if next_page_cursor is not None:
		next_page_cursor = pad_id(next_page_cursor)
	if around_page_cursor is not None:
		around_page_cursor = pad_id(around_page_cursor)
	prevpage = None
	nextpage = None
	limit = int(limit)
	msgs = []

	print("LIMIT", limit)

	if prev_page_cursor is not None:
		query["_id"] = {
			"$lt": prev_page_cursor
		}
		cursor = collection_messages.find(query).sort("_id", pymongo.DESCENDING).limit(limit + 1)
		msgs = list(cursor)
		if len(msgs) > 0:
			msgs = msgs[::-1]  # DESC -> ASC sort

		if limit + 1 == len(msgs):
			msgs = msgs[1:]
			prevpage = msgs[0]["_id"]

		if len(msgs) > 0:
			nextpage = msgs[-1]["_id"]
		else:
			if (int(prev_page_cursor) - 1) > 0:
				nextpage =  pad_id(int(prev_page_cursor) - 1)
			else:
				nextpage = pad_id(0)
		query["_id"] = {
			"$gt": nextpage
		}
		cursor = collection_messages.find(query).sort("_id", pymongo.ASCENDING).limit(1)
		if len(list(cursor)) == 0:
			nextpage = None

	elif next_page_cursor is not None:
		query["_id"] = {
			"$gt": next_page_cursor
		}
		cursor = collection_messages.find(query).sort("_id", pymongo.ASCENDING).limit(limit + 1)
		msgs = list(cursor)

		if limit + 1 == len(msgs):
			msgs = msgs[:-1]
			nextpage = msgs[-1]["_id"]

		if len(msgs) > 0:
			prevpage = msgs[0]["_id"]
		else:
			prevpage = pad_id(int(next_page_cursor) + 1)

		query["_id"] = {
			"$lt": prevpage
		}
		cursor = collection_messages.find(query).sort("_id", pymongo.DESCENDING).limit(1)
		if len(list(cursor)) == 0:
			prevpage = None

	elif around_page_cursor is not None:
		query["_id"] = {
			"$lte": around_page_cursor
		}
		cursor = collection_messages.find(query).sort("_id", pymongo.DESCENDING).limit(limit // 2 + 1)
		msgsl = list(cursor)
		if len(msgsl) > 0:
			msgsl = msgsl[::-1]  # fix order
		if limit // 2 + 1 == len(msgsl):
			msgsl = msgsl[1:]
			prevpage = msgsl[0]["_id"]

		query["_id"] = {
			"$gt": around_page_cursor
		}
		cursor = collection_messages.find(query).sort("_id", pymongo.ASCENDING).limit(limit // 2 + 1)
		msgsg = list(cursor)
		if limit // 2 + 1 == len(msgsg):
			msgsg = msgsg[:-1]
			nextpage = msgsg[-1]["_id"]
		msgs = msgsl + msgsg


	ids = [msg["_id"] for msg in msgs]

	return {
		"prevPage": prevpage,
		"messageIds": ids,
		"nextPage": nextpage,
		"messages": msgs
	}
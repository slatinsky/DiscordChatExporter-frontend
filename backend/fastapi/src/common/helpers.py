import json


def pad_id(id):
	if id == None:
		return None
	return str(id).zfill(24)


def print_json(json_obj):
	print(json.dumps(json_obj, indent=4))


def simplify_mongo_query(query: dict | list):
	"""
	- recursively removes nested $and and $or if they are the only element in the list
	- also removes empty $and and $or lists
	- also removes empty objects from the list
	"""
	if isinstance(query, list):
		# other lists we are not simplifying
		return query

	# remove nested $and and $or if they are the only element in the list
	if "$and" in query:
		query["$and"] = [simplify_mongo_query(q) for q in query["$and"]]
		# remove empty objects
		query["$and"] = [q for q in query["$and"] if q]

		# if there is only one element in the list, remove the list
		if len(query["$and"]) == 1:
			query = query["$and"][0]

	if "$or" in query:
		query["$or"] = [simplify_mongo_query(q) for q in query["$or"]]
		# remove empty objects
		query["$or"] = [q for q in query["$or"] if q]

		# if there is only one element in the list, remove the list
		if len(query["$or"]) == 1:
			query = query["$or"][0]

	# remove empty $and and $or
	if "$or" in query and len(query["$or"]) == 0:
		del query["$or"]
	if "$and" in query and len(query["$and"]) == 0:
		del query["$and"]

	return query
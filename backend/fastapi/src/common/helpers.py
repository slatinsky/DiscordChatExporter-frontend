import json


def pad_id(id):
	if id == None:
		return None
	return str(id).zfill(24)


def print_json(json_obj):
	print(json.dumps(json_obj, indent=4))

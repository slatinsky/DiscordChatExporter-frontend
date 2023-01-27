import glob
from pymongo import MongoClient
import json
from pprint import pprint

URI = "mongodb://127.0.0.1:27017"
client = MongoClient(URI)
db = client["dcef"]
collection_messages = db["messages"]
collection_channels = db["channels"]

# def read_data():
# 	data = collection_messages.find_one({"name": "test"})
# 	return data

# def read_all_data():
# 	data = collection_messages.find({})
# 	return data

# def update_data(data):
# 	collection_messages.update_one({"name": "test"}, {"$set": data})

# def delete_data():
# 	collection_messages.delete_one({"name": "test"})

def clear_database():
	collection_messages.delete_many({})
	collection_channels.delete_many({})

def read_json_file(file_path):
	with open(file_path, "r", encoding='utf-8') as f:
		try:
			data = json.load(f)
		except json.decoder.JSONDecodeError:
			# probably media file too
			print("JSONDecodeError: " + filename)
			return None

		if 'guild' not in data:  # this is not a channel export, but a downloaded media json file
			return None
	return data

def _find_json_files(directory):
	files = []
	for filename in glob.glob(directory + '**/*.json', recursive=True):
		if filename.endswith('.json'):
			files.append(filename)

	return files

def insert_message(message, guild, channel):
	"""
	Inserts a message into the database if it doesn't exist yet.
	"""

	content = message["content"]
	latest_timestamp = message["timestamp"]
	if message["timestampEdited"] != None:
		latest_timestamp = message["timestampEdited"]

	# check if message already exists. If so, get the existing message
	database_document = collection_messages.find_one({"_id": message["id"]})

	if database_document != None:  # message already exists
		# print("ID exists: " + str(message["id"]))

		# if message was edited, add new content
		has_timestamp = False
		for database_document_content in database_document["content"]:
			# print(database_document_content["timestamp"] + " == " + latest_timestamp)
			if database_document_content["timestamp"] == latest_timestamp:
				has_timestamp = True
				break

		if not has_timestamp:
			database_document["content"].append({
				"timestamp": latest_timestamp,
				"content": content
			})
			print(database_document["content"])
			# update database
			collection_messages.update_one({"_id": message["id"]}, {"$set": database_document})
		return

	# set mongo object id to discord id
	object_id = message["id"]
	message["_id"] = object_id
	del message["id"]



	message["content"] = [
		{
			"timestamp": latest_timestamp,
			"content": content
		},
	]

	# reference to guild and channel
	message["guildId"] = guild["id"]
	message["channelId"] = channel["id"]

	# remove empty lists
	if len(message["attachments"]) == 0:
		del message["attachments"]

	if len(message["embeds"]) == 0:
		del message["embeds"]

	if len(message["mentions"]) == 0:
		del message["mentions"]

	if len(message["stickers"]) == 0:
		del message["stickers"]

	if len(message["reactions"]) == 0:
		del message["reactions"]

	collection_messages.insert_one(message)

def insert_channel(guild, channel):
	database_document = collection_channels.find_one({"_id": channel["id"]})

	if database_document != None:
		# channel already exists
		return

	# set mongo object id to discord id
	object_id = channel["id"]
	channel["_id"] = object_id
	del channel["id"]

	channel["guildId"] = guild["id"]

	collection_channels.insert_one(channel)


def process_json_file(json_path, messages_count):
	json_data = read_json_file(json_path)

	if json_data == None:
		print("invalid file " + json_path)
		return messages_count


	guild = json_data["guild"]
	channel = json_data["channel"]
	messages = json_data["messages"]

	messages_count += len(messages)
	print("processing messages " + str(len(messages)).rjust(5, ' ') + ", total " +  str(messages_count).rjust(9, ' ') + " - " + json_path)
	# print(json_path)

	insert_channel(guild, channel.copy())

	for message in messages:
		insert_message(message, guild, channel)

	return messages_count + len(messages)

def main():
	print("main_mongo loaded")

	# DEBUG clear database
	clear_database()

	jsons = _find_json_files("../../exports/")
	print("found " + str(len(jsons)) + " json files")

	# DEBUG get only first n files
	jsons = jsons[:200]

	messages_count = 0
	for json_path in jsons:
		messages_count = process_json_file(json_path, messages_count)


	# cursor = read_all_data()
	# for document in cursor:
	# 	pass
	print("main_mongo done")



if __name__ == "__main__":
	main()


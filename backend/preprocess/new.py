import json
import sys

from Database import Database
from Progress import Progress


def process_json_files(database: Database):
	json_files = database.storage.json_files.copy()

	# get processed files
	processed_files = processed_files = database.get_processed_files()

	# remove processed files from json_files
	for processed_file in processed_files:
		if processed_file[0] in json_files:
			json_files.remove(processed_file[0])

	print('Found {} new json files'.format(len(json_files)))

	progress = Progress(json_files)
	for file in json_files:
		with open(file, 'r', encoding='utf-8') as f:
			try:
				data = json.load(f)
			except json.decoder.JSONDecodeError:
				# probably media file too
				print("JSONDecodeError: " + file)
				continue
			if 'guild' not in data:  # this is not a channel export, but a downloaded media json file
				continue

			channel_id = data['channel']['id']
			guild_id = data['guild']['id']
			category_id = data['channel']['categoryId']
			channel_name = data['channel']['name']
			channel_type = data['channel']['type']
			channel_position = None
			channel_topic = data['channel']['topic']

			database.new_channel(channel_id, guild_id, category_id, channel_name, channel_type, channel_position, channel_topic)

			guild_name = data['guild']['name']
			guild_icon_path = data['guild']['iconUrl']
			database.new_guild(guild_id, guild_name, guild_icon_path)

			category_name = data['channel']['category']
			category_position = None
			database.new_category(category_id, guild_id, category_name, category_position)

			# insert messages to messages table
			for message in data['messages']:
				author_id = message['author']['id']
				author_name = message['author']['name']
				author_discriminator = message['author']['discriminator']
				author_nickname = message['author']['nickname']
				author_is_bot = message['author']['isBot']
				author_avatar_url = message['author']['avatarUrl']
				database.new_author(author_id, guild_id, author_name, author_discriminator, author_nickname, author_is_bot, author_avatar_url)


				message_id = message['id']
				message_type = message['type']
				message_timestamp = message['timestamp']
				message_timestamp_edited = message['timestampEdited']
				message_is_pinned = message['isPinned']
				message_is_deleted = False
				message_content = message['content']
				message_author_id = message['author']['id']

				database.new_message(message_id, guild_id, category_id, channel_id, message_type, message_timestamp, message_timestamp_edited, message_is_pinned, message_is_deleted, message_content, message_author_id)

				# insert message reactions to message_reaction table
				for reaction in message['reactions']:
					emoji_id = reaction['emoji']['id']
					emoji_name = reaction['emoji']['name']
					emoji_is_animated = reaction['emoji']['isAnimated']
					emoji_url = reaction['emoji']['imageUrl']

					reaction_count = reaction['count']
					database.new_message_reaction(message_id, reaction_count, emoji_id, emoji_name, emoji_url, emoji_is_animated, guild_id)



				# # insert message attachments to messages_attachments table
				for attachment in message['attachments']:
					attachment_url = attachment['url']
					attachment_size = attachment['fileSizeBytes']
					database.new_message_attachment(message_id, attachment_url, attachment_size)


				# # insert message embeds to messages_embeds table
				for embed in message['embeds']:
					# todo: add embeds
					pass

				for mention in message['mentions']:
					# todo: add embeds
					pass



		database.new_processed_file(file)
		database.commit()
		progress.increment()

	progress.finish()






def process_assets(database: Database):
	media_filepaths = database.storage.media_files.copy()

	# get processed files
	processed_files = database.get_processed_files()

	# remove processed files from media_filepaths
	for processed_file in processed_files:
		if processed_file[0] in media_filepaths:
			del media_filepaths[processed_file[0]]

	print('Found {} new media files'.format(len(media_filepaths)))

	progress = Progress(media_filepaths)

	for filename, path in media_filepaths.items():
		asset_id = database.new_asset(path)
		progress.increment()

	progress.finish()

	database.commit()




# main
if __name__ == '__main__':
	input_directory = sys.argv[1]
	output_directory = sys.argv[2]

	database = Database('database.sqlite3', input_directory)

	process_assets(database)
	process_json_files(database)
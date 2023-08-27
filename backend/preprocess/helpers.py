from itertools import islice
import json
import os


with open('emojiIndex.json', 'r', encoding='utf8') as f:
    emoji_index = json.load(f)

# read emojiIndex.json
# emojiIndex from https://github.com/Tyrrrz/DiscordChatExporter/blob/5b1b7205037662bb28dc5e541f0950586d4b8a22/DiscordChatExporter.Core/Utils/EmojiIndex.cs
def get_emoji_code(name):
    if name in emoji_index:
        return emoji_index[name]
    else:
        return name


def pad_id(id):
	if id == None:
		return None
	return str(id).zfill(24)


def is_compiled():
	if os.path.exists(__file__):
		return False
	else:
		return True


def batched(iterable, n):
	"Batch data into tuples of length n. The last batch may be shorter."
	# batched('ABCDEFG', 3) --> ABC DEF G
	if n < 1:
		raise ValueError('n must be at least one')
	it = iter(iterable)
	while (batch := tuple(islice(it, n))):
		yield batch



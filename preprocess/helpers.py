import os
import json

def is_compiled():
    if os.path.exists(__file__):
        return False
    elif os.path.exists('preprocess.exe'):
        return True
    else:
        raise Exception('Cannot determine if compiled or not')

def pad_id(id):
    return str(id).zfill(24)
    # return str(id).rjust(24, '0')

with open('emojiIndex.json', 'r', encoding='utf8') as f:
    emoji_index = json.load(f)

# read emojiIndex.json
# emojiIndex from https://github.com/Tyrrrz/DiscordChatExporter/blob/5b1b7205037662bb28dc5e541f0950586d4b8a22/DiscordChatExporter.Core/Utils/EmojiIndex.cs
def get_emoji_code(name):
    if name in emoji_index:
        return emoji_index[name]
    else:
        return name
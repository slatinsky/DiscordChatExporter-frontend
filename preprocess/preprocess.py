import glob
import json
import os
from pprint import pprint
import re
import shutil
from hashlib import sha256

class GuildPreprocess:
    def __init__(self, guild_id, input_dir, json_filepaths, media_filepaths):
        self.input_dir = input_dir
        self.guild_id = guild_id
        self.json_filepaths = json_filepaths
        self.media_filepaths = media_filepaths


    def read_channels_messages_from_files(self):
        channels = {}
        messages = {}
        for path in self.json_filepaths:
            with open(path, 'r', encoding="utf8") as f:
                data = json.load(f)
                channel = data['channel']

                if channel['id'] not in channels:
                    channels[channel['id']] = channel

                # Copy messages temporarily to the guild
                for message in data['messages']:
                    message['channelId'] = channel['id']  # temporary marker for channel id
                    messages[message['id']] = message
        return channels, messages

    def cleanup_empty_fields(self, messages):
        for message in messages.values():
            # cleanup unused fields
            if message['attachments'] == []:
                del message['attachments']

            if message['embeds'] == []:
                del message['embeds']

            if message['stickers'] == []:
                del message['stickers']

            if message['mentions'] == []:
                del message['mentions']

            if 'reactions' in message and message['reactions'] == []:
                del message['reactions']

            if message['timestampEdited'] is None:
                del message['timestampEdited']

            # if message['mentionIds'] == []:
                # del message['mentionIds']
        return messages

    def extract_authors(self, messages):
        authors = {}
        for message in messages.values():
            author = message['author']
            author['message_id'] = message['id']
            if author['id'] not in authors:  # new author
                authors[author['id']] = author
            elif authors[author['id']]['message_id'] < message['id']:  # extract author information from his last message (by message id)
                authors[author['id']] = author

        # cleanup temp message_ids
        for author in authors.values():
            del author['message_id']

        # cleanup author information from messages
        for message in messages.values():
            message['authorId'] = message['author']['id']
            del message['author']

        return messages, authors

    def extract_emoji(self, messages):
        emojis = {}
        for message in messages.values():
            for reaction in message['reactions']:
                if reaction['emoji']['id'] is "":
                    emojis[reaction['emoji']['name']] = reaction['emoji']
                    reaction['emojiName'] = reaction['emoji']['name']
                else:
                    emojis[reaction['emoji']['id']] = reaction['emoji']
                    reaction['emojiId'] = reaction['emoji']['id']

                del reaction['emoji']

        return messages, emojis


    def _calculate_filename(self, url):
        """calculate the filename based on the data"""
        filename = url.split('/')[-1]
        # remove get parameters
        filename = filename.split('?')[0]
        hash_sha256 = sha256(url.encode('utf-8')).hexdigest()[:5].upper()

        base, extension = os.path.splitext(filename)
        filename = base + "-" + hash_sha256 + extension
        return filename

    def _find_filepath(self, filename):
        if filename in self.media_filepaths:
            filepath = self.media_filepaths[filename].replace('\\', '/').replace(self.input_dir, '/input/')
            # print("Found file: " + filepath)
            return filepath
        else:
            print("File not found: " + filename)
            return None
        return None

    def calculate_local_filenames(self, messages, authors, emojis):
        for message in messages.values():
            # calculate attachement filenames
            for attachment in message['attachments']:
                attachment['localFileName'] = self._calculate_filename(attachment['url'])
                attachment['localFilePath'] = self._find_filepath(attachment['localFileName'])

                # if image, tag it as such
                if attachment['localFileName'] is not None and attachment['localFileName'].endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')):
                    attachment['type'] = 'image'

            # calculate embed filenames
            for embed in message['embeds']:
                # if embed['type'] == 'image':
                embed['localFileName'] = self._calculate_filename(embed['url'])
                embed['localFilePath'] = self._find_filepath(embed['localFileName'])

            # calculate sticker filenames
            for sticker in message['stickers']:
                sticker['localFileName'] = self._calculate_filename(sticker['url'])
                sticker['localFilePath'] = self._find_filepath(sticker['localFileName'])

        for emoji in emojis.values():
            emoji['localFileName'] = self._calculate_filename(emoji['imageUrl'])
            emoji['localFilePath'] = self._find_filepath(emoji['localFileName'])

        for author in authors.values():
            author['localFileName'] = self._calculate_filename(author['avatarUrl'])
            author['localFilePath'] = self._find_filepath(author['localFileName'])

        return messages

    def group_messages_and_channels(self, messages, channels):
        # add messages to channels
        # for message in messages.values():
        #     channel_id = message['channelId']
        #     if 'messages' not in channels[channel_id]:
        #         channels[channel_id]['messages'] = []
        #     channels[channel_id]['messages'].append(message)

        # messages by channel
        messages_by_channel = {}
        for message in messages.values():
            channel_id = message['channelId']
            if channel_id not in messages_by_channel:
                messages_by_channel[channel_id] = []
            messages_by_channel[channel_id].append(message)

        # group channels by categories
        categories = {}
        for channel in channels.values():
            if channel['type'] == 4:
                continue
            if channel['categoryId'] not in categories:
                categories[channel['categoryId']] = {
                    'id': channel['categoryId'],
                    'name': channel['category'],
                    'channelIds': []
                }
            categories[channel['categoryId']]['channelIds'].append({
                'id': channel['id'],
                'name': channel['name'],
            })
        return messages_by_channel, categories



    def cleanup_out_directory(self, output_dir):
        if os.path.exists(output_dir):
            shutil.rmtree(output_dir) # delete existing output_dir directory and all its contents
        os.makedirs(output_dir)  # recreate the directory

    def write_json(self, data, filename):
        with open(filename, 'w', encoding="utf8") as f:
            json.dump(data, f, indent=4)

        # minified
        with open(filename.replace('.json', '.min.json'), 'w', encoding="utf8") as f:
            json.dump(data, f)


    def process(self):
        # step 1 - read data from json files
        channels, messages = self.read_channels_messages_from_files()

        # step 2 - extract author information from messages
        messages, authors = self.extract_authors(messages)

        # step 3 - extract emoji information from messages
        messages, emojis = self.extract_emoji(messages)

        messages = self.calculate_local_filenames(messages, authors, emojis)

        # step 4 - cleanup empty fields
        messages = self.cleanup_empty_fields(messages)

        # step 5 - cleanup existing output directory
        output_dir = '../static/data/' + self.guild_id + '/'
        self.cleanup_out_directory(output_dir)

        # step 6 - grouping to single json file
        # group messages by channels
        messages_by_channel, categories = self.group_messages_and_channels(messages, channels)

        # group channels and others attributes to single dict
        guild = {
            'categories': categories,
            'authors': authors,
            'emojis': emojis,
            'channels': channels,
            'messages': messages_by_channel,
            'version': '1.0.0'
        }


        # step 7 - write data to json files
        self.write_json(guild, output_dir + 'guild.json')




class Preprocess:
    def __init__(self, input_directory):
        self.input_directory = input_directory
        self.files = self._find_json_files(self.input_directory)
        self.guilds = {}  # guild id is key
        self.channels = {} # channel id is key
        self.messages = {} # message id is key
        self.authors = {} # author id is key
        self.emojis = {} # emoji id is key
        self.mentions = {} # mention id is key

    # recursively find all json files in the current directory
    # and print the thread ids to stdout
    def _find_json_files(self, directory):
        files = []
        for filename in glob.glob(directory + '**/*.json', recursive=True):
            if filename.endswith('].json'):
                # print(filename)
                files.append(filename)
        return files

    
    def _find_all_mediafiles_paths(self, directory):
        all_files = {}
        regex_pattern = re.compile(r'.+\-[A-F0-9]{5}\..+')
        for path in glob.glob(directory + '**/*', recursive=True):
            if regex_pattern.match(path):
                filename = os.path.basename(path)
                all_files[filename] = path

        return all_files





    # def remove_duplicates(self):
    #     """remove duplicates based on id"""
    #     # pprint(self.messages)
    #     self.channels = list({v['id']: v for v in self.channels}.values())
    #     self.guilds = list({v['id']: v for v in self.guilds}.values())
    #     self.messages = list({v['id']: v for v in self.messages}.values())
    #     return

    # def sort(self):
    #     self.messages = sorted(self.messages, key=lambda d: d['timestamp'])
    #     self.channels = sorted(self.channels, key=lambda d: d['categoryId'])
    #     self.guilds = sorted(self.guilds, key=lambda d: d['name'])
    #     return



    def process(self):
        json_files = self._find_json_files(self.input_directory)
        media_filepaths = self._find_all_mediafiles_paths(self.input_directory)

        guilds = {}

        # sort filenames by guild to attempt to split ram usage
        json_paths_by_guild = {}
        for filename in json_files:  # each filename contains channel/thread dump
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
                guild_id = data['guild']['id']
                guilds[guild_id] = data['guild']
                if guild_id not in json_paths_by_guild:
                    json_paths_by_guild[guild_id] = []

                json_paths_by_guild[guild_id].append(filename)

        # loop through each guild
        for guild_id, json_filepaths in json_paths_by_guild.items():
            gp = GuildPreprocess(guild_id, self.input_directory, json_filepaths, media_filepaths)
            gp.process()

        # write guilds to json file
        with open('../static/data/guilds.json', 'w', encoding="utf8") as f:
            json.dump(guilds, f, indent=4)
        with open('../static/data/guilds.min.json', 'w', encoding="utf8") as f:
            json.dump(guilds, f)
        return


        all_messages = []
        all_filenames = []
        for filename in json_files:
            with open(filename, encoding="utf8") as f:
                data = json.load(f)
                guild = data['guild']
                channel = data['channel']
                messages = data['messages']

                channel['guildId'] = guild['id']

                processed_messages = {}
                for message in messages:
                    message['channelId'] = channel['id']
                    # message['guildId'] = guild['id']

                    processed_messages[message['id']] = message


                    self.authors[message['author']['id']] = message['author']

                    message['authorId'] = message['author']['id']
                    del message['author']

                    # for reaction in message['reactions']:
                    #     if reaction['emoji']['id'] is "":
                    #         self.emojis[reaction['emoji']['name']] = reaction['emoji']
                    #         reaction['emojiName'] = reaction['emoji']['name']
                    #     else:
                    #         self.emojis[reaction['emoji']['id']] = reaction['emoji']
                    #         reaction['emojiId'] = reaction['emoji']['id']

                    #     del reaction['emoji']

                    message['mentionIds'] = []
                    for mention in message['mentions']:
                        self.mentions[mention['id']] = mention
                        message['mentionIds'].append(mention['id'])
                    del message['mentions']

                    # calculate attachement filenames
                    for attachment in message['attachments']:
                        attachment['fileName'] = self.calculate_filename(attachment['url'])
                        all_filenames.append(attachment['fileName'])

                    # # cleanup unused fields
                    # if message['attachments'] == []:
                    #     del message['attachments']

                    # if message['embeds'] == []:
                    #     del message['embeds']

                    # if message['reactions'] == []:
                    #     del message['reactions']

                    # if message['timestampEdited'] is None:
                    #     del message['timestampEdited']

                    # if message['mentionIds'] == []:
                    #     del message['mentionIds']


                self.guilds[guild['id']] = guild
                self.channels[channel['id']] = channel
                self.messages = self.messages | processed_messages  # merge dicts together


        # print(all_filenames)

        # self.sort()
        # self.remove_duplicates()

        # sort channels by guild
        guilds_channels = {}
        for channel in self.channels.values():
            if channel['guildId'] not in guilds_channels:
                guilds_channels[channel['guildId']] = {}
            guilds_channels[channel['guildId']][channel['id']] = channel

        # sort messages by channel
        channels_messages = {}
        for message in self.messages.values():
            if message['channelId'] not in channels_messages:
                channels_messages[message['channelId']] = {}
            channels_messages[message['channelId']][message['id']] = message





        out_dir = '../static/data/'

        # delete contents of out_dir if it exists
        if os.path.exists(out_dir):
            shutil.rmtree(out_dir)

        # create out directory if it doesn't exist
        if not os.path.exists(out_dir):
            print('creating directory: ' + out_dir)
            os.makedirs(out_dir)
        else:
            print('directory exists: ' + out_dir)

        # create emojis directory if it doesn't exist
        emojis_dir = out_dir + 'emojis/'
        if not os.path.exists(emojis_dir):
            os.makedirs(emojis_dir)

        # calculate emoji filenames
        for emoji in self.emojis.values():
            emoji['fileName'] = self.calculate_filename(emoji['imageUrl'])
            all_filenames.append(emoji['fileName'])
            # copy emoji file to emojis_dir directory
            shutil.copyfile(media_filepaths[emoji['fileName']], emojis_dir + emoji['fileName'])


        # save emojis.json
        with open(out_dir + 'emojis.json', 'w') as f:
            json.dump(self.emojis, f, indent=4)

        # save authors.json
        with open(out_dir + 'authors.json', 'w') as f:
            json.dump(self.authors, f, indent=4)

        with open(out_dir + 'guilds.json', 'w') as f:
            json.dump(self.guilds, f, indent=4)

        # create a directory for each guild
        for guild in self.guilds.values():
            os.mkdir(out_dir + guild['id'])
            # create channels.json
            with open(out_dir + guild['id'] + '/channels.json', 'w') as f:
                json.dump(guilds_channels[guild['id']], f, indent=4)

            # create a directory for each channel
            for channel in guilds_channels[guild['id']].values():
                os.mkdir(out_dir + guild['id'] + '/' + channel['id'])
                # create messages.json
                with open(out_dir + guild['id'] + '/' + channel['id'] + '/messages.json', 'w') as f:
                    json.dump(channels_messages[channel['id']], f, indent=4)

        # with open('channels.json', 'w') as f:

    def get_files(self):
        return self.files


def main():
    p = Preprocess('../static/input/')
    p.process()


if __name__ == '__main__':
    main()

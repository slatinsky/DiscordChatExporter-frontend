from concurrent.futures import thread
import glob
import json
import os
from pprint import pprint
import re
import shutil
from hashlib import sha256
import imagesize

def pad_id(id):
    return str(id).zfill(24)
    # return str(id).rjust(24, '0')


class GuildPreprocess:
    def __init__(self, guild_id, input_dir, json_filepaths, media_filepaths):
        self.input_dir = input_dir
        self.guild_id = guild_id
        self.json_filepaths = json_filepaths
        self.media_filepaths = media_filepaths

    ## if any field in data has key 'id', pad it with zeros for fast sorting
    def pad_ids(self, data):
        data['guild']['id'] = pad_id(data['guild']['id'])
        data['channel']['id'] = pad_id(data['channel']['id'])

        data['channel']['categoryId'] = pad_id(data['channel']['categoryId'])


        # for message in data.messages:
        for message in data['messages']:
            message['id'] = pad_id(message['id'])
            message['author']['id'] = pad_id(message['author']['id'])

            for reaction in message['reactions']:
                reaction['emoji']['id'] = pad_id(reaction['emoji']['id'])

            # mentions
            for mention in message['mentions']:
                mention['id'] = pad_id(mention['id'])

            # attachments
            for attachment in message['attachments']:
                attachment['id'] = pad_id(attachment['id'])

            # sticker
            for sticker in message['stickers']:
                sticker['id'] = pad_id(sticker['id'])

            if 'reference' in message:
                if message['reference']['messageId'] is not None:
                    message['reference']['messageId'] = pad_id(message['reference']['messageId'])
                if message['reference']['channelId'] is not None:
                    message['reference']['channelId'] = pad_id(message['reference']['channelId'])
                if message['reference']['guildId'] is not None:
                    message['reference']['guildId'] = pad_id(message['reference']['guildId'])
        return data


    def read_channels_messages_from_files(self):
        channels = {}
        messages = {}
        for path in self.json_filepaths:
            with open(path, 'r', encoding="utf8") as f:
                print("Reading file: " + path)
                data = json.load(f)
                data = self.pad_ids(data)
                channel = data['channel']

                if channel['id'] not in channels:
                    channels[channel['id']] = channel

                # Copy messages temporarily to the guild
                for message in data['messages']:
                    # temporary marker for channel id
                    message['channelId'] = channel['id']
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
            # extract author information from his last message (by message id)
            elif authors[author['id']]['message_id'] < message['id']:
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

    def _get_extensions(self, messages):
        extensions = set()
        for message in messages.values():
            for attachment in message['attachments']:
                extensions.add(os.path.splitext(attachment['localFileName'])[-1].replace('.', '').lower())
        return list(extensions)


    def _calculate_filename(self, url):
        """calculate the filename based on the data"""
        if url is None:
            return ""
        is_url = re.match(r'^https?://', url)

        filename = url.replace('\\', '/').split('/')[-1]

        if is_url:  # calculate filename for url
            # remove get parameters
            # hashed filename must contain get parameters
            hash_sha256 = sha256(url.encode('utf-8')).hexdigest()[:5].upper()

            filename = filename.split('?')[0]
            base, extension = os.path.splitext(filename)
            filename = base + "-" + hash_sha256 + extension
        else:  # filename already contains hash
            pass
        return filename

    def _find_filepath(self, filename, ignore_not_found=False):
        if filename in self.media_filepaths:
            filepath = self.media_filepaths[filename].replace(
                '\\', '/').replace(self.input_dir, '/input/')
            # print("Found file: " + filepath)
            return filepath
        else:
            if not ignore_not_found:
                print("File not found: " + filename)
            return None

    def calculateGuildFilename(self, guild):
        guild['localFileName'] = self._calculate_filename(guild['iconUrl'])
        guild['localFilePath'] = self._find_filepath(guild['localFileName'])
        return guild

    def calculate_local_filenames(self, messages, authors, emojis):
        for message in messages.values():
            # calculate attachement filenames
            for attachment in message['attachments']:
                attachment['localFileName'] = self._calculate_filename(
                    attachment['url'])
                attachment['localFilePath'] = self._find_filepath(
                    attachment['localFileName'])
                attachment['extension'] = os.path.splitext(attachment['localFileName'])[-1].replace('.', '').lower()


                # if image, tag it as such
                if attachment['localFileName'] is not None and attachment['localFileName'].endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')):
                    attachment['type'] = 'image'
                    try:
                        attachment['width'], attachment['height'] = imagesize.get("../static/" + attachment['localFilePath'])
                    except:
                        pass
                elif attachment['localFileName'] is not None and attachment['localFileName'].endswith(('.mp4', '.webm')):
                    attachment['type'] = 'video'

            # calculate embed filenames
            for embed in message['embeds']:
                if "thumbnail" in embed and embed["thumbnail"] is not None:
                    # image embed is calculated from embed["url"]
                    embed["thumbnail"]["localFileName"] = self._calculate_filename(
                        embed["url"])
                    embed["thumbnail"]["localFilePath"] = self._find_filepath(
                        embed["thumbnail"]["localFileName"], ignore_not_found=True)

                    # non image embeds is calculated from embed["thumbnail"]["url"]
                    if (embed["thumbnail"]["localFilePath"] is None):
                        embed["thumbnail"]["localFileName"] = self._calculate_filename(
                            embed["thumbnail"]["url"])
                        embed["thumbnail"]["localFilePath"] = self._find_filepath(
                            embed["thumbnail"]["localFileName"])
        
                    try:
                        embed["thumbnail"]['width'], embed["thumbnail"]['height'] = imagesize.get("../static/" + embed["thumbnail"]['localFilePath'])
                    except:
                        pass

                if "image" in embed and embed["image"] is not None:
                    embed["image"]["localFileName"] = self._calculate_filename(
                        embed["image"]["url"])
                    embed["image"]["localFilePath"] = self._find_filepath(
                        embed["image"]["localFileName"])

                    try:
                        embed["image"]['width'], embed["image"]['height'] = imagesize.get("../static/" + embed["image"]['localFilePath'])
                    except:
                        pass
                if "images" in embed:
                    for image in embed["images"]:
                        image["localFileName"] = self._calculate_filename(
                            image["url"])
                        image["localFilePath"] = self._find_filepath(
                            image["localFileName"])

                        try:
                            image['width'], image['height'] = imagesize.get("../static/" + image['localFilePath'])
                        except:
                            pass

            # TODO: other embeds and stickers

        for emoji in emojis.values():
            emoji['localFileName'] = self._calculate_filename(
                emoji['imageUrl'])
            emoji['localFilePath'] = self._find_filepath(
                emoji['localFileName'])
            
            try:
                emoji['width'], emoji['height'] = imagesize.get("../static/" + emoji['localFilePath'])
            except:
                pass

        for author in authors.values():
            author['localFileName'] = self._calculate_filename(
                author['avatarUrl'])
            author['localFilePath'] = self._find_filepath(
                author['localFileName'])
            
            try:
                author['width'], author['height'] = imagesize.get("../static/" + author['localFilePath'])
            except:
                pass

        return messages

    def group_messages_and_channels(self, messages, channels):

        # messages by channel
        messages_by_channel = {}
        for message in messages.values():
            channel_id = message['channelId']
            if channel_id not in messages_by_channel:
                messages_by_channel[channel_id] = {}
            messages_by_channel[channel_id][message['id']] = message

        # spli channels into threads or normal channels
        threads = {}
        normal_channels = {}  # non thread channels
        for channel in channels.values():
            if channel['type'] == "GuildTextChat" or channel['type'] == "DirectTextChat" or channel['type'] == "DirectGroupTextChat":
                normal_channels[channel['id']] = channel
            elif channel['type'] == "GuildPublicThread":
                threads[channel['id']] = channel
            else:
                print("Unknown channel type: " + channel['type'])


        # group channels by categories
        categories = {}

        for channel in normal_channels.values():
            # if channel['type'] == 4:
            #     continue
            if channel['categoryId'] not in categories:
                if 'threads' not in channel:
                    channel['threads'] = []

                categories[channel['categoryId']] = {
                    'id': channel['categoryId'],
                    'name': channel['category'],
                    'threads': channel['threads'],

                    'channelIds': []
                }


            categories[channel['categoryId']]['channelIds'].append({
                'id': channel['id'],
                'name': channel['name'],
                'type': "text",
            })

        # pprint(threads)
        for category in categories.values():
            # loop category['channelIds']
            for channel_info in category['channelIds']:
            # for channel_id in category['channelIds']:
                channel_id = channel_info['id']
                for thread in threads.values():
                    if thread['categoryId'] == channel_id:
                        if 'threads' not in channel_info:
                            channel_info['threads'] = []
                        channel_info['threads'].append({
                            'id': thread['id'],
                            'name': thread['name'],
                            'type': "thread",
                        })

        return messages_by_channel, categories, threads

    def cleanup_out_directory(self, output_dir):
        if os.path.exists(output_dir):
            # delete existing output_dir directory and all its contents
            shutil.rmtree(output_dir)
        os.makedirs(output_dir)  # recreate the directory

    def write_json(self, data, filename):
        with open(filename, 'w', encoding="utf8") as f:
            json.dump(data, f, indent=4)

        # minified
        with open(filename.replace('.json', '.min.json'), 'w', encoding="utf8") as f:
            json.dump(data, f)

    def get_thread_id_to_message_id(self, messages, messages_by_channel, threads):
        thread_id_to_message_id = {}
        for message in messages.values():
            if message['type'] == "ThreadCreated":
                newThreadChannelId = message['reference']['channelId']
                thread_id_to_message_id[message['reference']['channelId']] = message['id']
                if message['reference']['channelId'] in threads:
                    message['threadName'] = threads[message['reference']['channelId']]['name']
                    message['threadMsgCount'] = len(threads[message['reference']['channelId']])
                else:
                    message['threadName'] = 'Thread not exported'
                    message['threadMsgCount'] = None  # fallback value
                
                # print("ThreadCreated: " + newThreadChannelId)

        pprint(thread_id_to_message_id)

        return thread_id_to_message_id

    def process(self):
        # step 1 - read data from json files
        channels, messages = self.read_channels_messages_from_files()

        # sort messages dict by key
        messages = dict(sorted(messages.items()))

        # sort channels dict by key
        channels = dict(sorted(channels.items()))

        # print message count
        print("Message count: " + str(len(messages)))

        # step 2 - extract author information from messages
        messages, authors = self.extract_authors(messages)

        # step 3 - extract emoji information from messages
        messages, emojis = self.extract_emoji(messages)

        messages = self.calculate_local_filenames(messages, authors, emojis)

        extensions = self._get_extensions(messages)




        # step 4 - cleanup empty fields
        messages = self.cleanup_empty_fields(messages)

        # step 5 - cleanup existing output directory
        output_dir = '../static/data/' + self.guild_id + '/'
        self.cleanup_out_directory(output_dir)

        # step 6 - grouping to single json file
        # group messages by channels
        messages_by_channel, categories, threads = self.group_messages_and_channels(
            messages, channels)

        # get message ids
        message_ids = list(messages.keys())

        thread_id_to_message_id = self.get_thread_id_to_message_id(messages, messages_by_channel, threads)

        # group channels and others attributes to single dict
        guild = {
            'id': self.guild_id,
            'categories': categories,
            'authors': authors,
            'emojis': emojis,
            # merge channels and threads
            'channels': {**channels, **threads},
            'message_ids': message_ids,
            'threadIdToMessageId': thread_id_to_message_id,
            'extensions': extensions,
            'messages': messages_by_channel,
        }

        # step 7 - write data to json files
        self.write_json(guild, output_dir + 'guild.json')


class Preprocess:
    def __init__(self, input_directory):
        self.input_directory = input_directory
        self.files = self._find_json_files(self.input_directory)
        self.guilds = {}  # guild id is key
        self.channels = {}  # channel id is key
        self.messages = {}  # message id is key
        self.authors = {}  # author id is key
        self.emojis = {}  # emoji id is key
        self.mentions = {}  # mention id is key

    # recursively find all json files in the current directory
    # and print the thread ids to stdout
    def _find_json_files(self, directory):
        files = []
        for filename in glob.glob(directory + '**/*.json', recursive=True):
            if filename.endswith('.json'):
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

    def should_process(self, json_files, media_filepaths):
        file_count = len(json_files) + len(media_filepaths)
        print("Found " + str(file_count) + " files")

        # make directory if it doesn't exist
        if not os.path.exists('../static/data'):
            os.makedirs('../static/data')

        # if data/hash.txt does exists read the hash
        if os.path.exists('../static/data/hash.txt'):
            with open('../static/data/hash.txt', 'r') as f:
                hash_from_file = f.read()
                print("Hash: " + hash_from_file) 
        else:
            print("Hash file does not exist")
            hash_from_file = None

        # create hash of this script
        if os.path.exists(__file__):
            hash_of_script = sha256(open(__file__, 'rb').read()).hexdigest()
        elif os.path.exists('preprocess.exe'):
            hash_of_script = sha256(open('preprocess.exe', 'rb').read()).hexdigest()
        else:
            hash_of_script = ""
            print("Could not find preprocess file")

        # create hash of all files
        # if hash is the same, then we can skip processing
        # because reprocessing takes a lot of time
        new_hash = sha256((str(json_files) + str(media_filepaths) + hash_of_script).encode('utf-8')).hexdigest()

        if hash_from_file == new_hash:
            print("Hash is the same, skipping processing")
            return False
        else:
            # write new hash to file
            with open('../static/data/hash.txt', 'w') as f:
                f.write(new_hash)

            print("Hash is different, processing")
            return True


    def process(self):
        json_files = self._find_json_files(self.input_directory)
        media_filepaths = self._find_all_mediafiles_paths(self.input_directory)

        if not self.should_process(json_files, media_filepaths):
            print("Skipping processing")
            return

        guilds = {}

        # sort filenames by guild to attempt to split ram usage
        json_paths_by_guild = {}
        for filename in json_files:  # each filename contains channel/thread dump
            with open(filename, 'r', encoding='utf-8') as f:
                try:
                    data = json.load(f)
                except json.decoder.JSONDecodeError:
                    print("JSONDecodeError: " + filename)  # probably media file too
                    continue
                if 'guild' not in data:  # this is not a channel export, but a downloaded media json file
                    continue
                guild_id = pad_id(data['guild']['id'])
                data['guild']['id'] = guild_id
                guilds[guild_id] = data['guild']
                if guild_id not in json_paths_by_guild:
                    json_paths_by_guild[guild_id] = []

                json_paths_by_guild[guild_id].append(filename)

        # loop through each guild
        for guild_id, json_filepaths in json_paths_by_guild.items():
            gp = GuildPreprocess(guild_id, self.input_directory,
                                 json_filepaths, media_filepaths)
            guilds[guild_id] = gp.calculateGuildFilename(guilds[guild_id])
            gp.process()

        # write guilds to json file
        with open('../static/data/guilds.json', 'w', encoding="utf8") as f:
            json.dump(guilds, f, indent=4)
        with open('../static/data/guilds.min.json', 'w', encoding="utf8") as f:
            json.dump(guilds, f)

    def get_files(self):
        return self.files


def main():
    p = Preprocess('../static/input/')
    p.process()


if __name__ == '__main__':
    main()

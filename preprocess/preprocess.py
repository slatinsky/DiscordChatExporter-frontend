from concurrent.futures import thread
import glob
import json
import os
from pprint import pprint
import re
import shutil
from hashlib import sha256
import imagesize

def is_compiled():
    if os.path.exists(__file__):
        return False
    elif os.path.exists('preprocess.exe'):
        return True
    else:
        raise Exception('Cannot determine if compiled or not')

if is_compiled():
    print('Running compiled version of preprocess.py')
    # Production settings
    DEV = False
    SKIP_PREPROCESSING_IMAGES = False
else:
    print('Running uncompiled version of preprocess.py')
    # Dev settings
    DEV = True
    SKIP_PREPROCESSING_IMAGES = False

def pad_id(id):
    return str(id).zfill(24)
    # return str(id).rjust(24, '0')

class Progress:
    def __init__(self, objects, name=''):
        self.total = len(objects)
        self.increments = round(self.total / 100)
        self.iteration = 0
        self.name = name

    def increment(self):
        self.iteration += 1
        if self.iteration % self.increments == 0:
            print("  ", self.name, self.iteration, "/", self.total, '(' + str(round(self.iteration / self.total * 100)) + '%)', end="\r") # print progress

    def finish(self):
        print("  ", self.name, "done                                     ")



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
                # print("Reading file: " + path)
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
                if reaction['emoji']['id'] == "":
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
                if 'extension' in attachment:
                    # extensions.add(attachment['extension'])
                    # extensions.add(os.path.splitext(attachment['localFileName'])[-1].replace('.', '').lower())
                    extensions.add(os.path.splitext(attachment['extension']))
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
                pass
                # print("File not found: " + filename)
            return None

    def calculateGuildFilename(self, guild):
        guild['localFileName'] = self._calculate_filename(guild['iconUrl'])
        guild['localFilePath'] = self._find_filepath(guild['localFileName'])
        return guild

    def calculateLocalFileAttributes(self, object, url1, url2=None):
        if url1 is None:  # no url
            return object

        file_name = self._calculate_filename(url1)
        file_path = self._find_filepath(file_name)

        if url2 is None and file_path is None:  # local file for url1 not found
            # print("File not found (url1): " + file_name)
            return object

        if url2 is not None:  # url2 is set, check it
            file_name = self._calculate_filename(url2)
            file_path = self._find_filepath(file_name)

        if file_path is None:  # local file for url2 not found
            # print("File not found (url2): " + file_name)
            return object

        # now we know that the local file exists
        extension = os.path.splitext(file_name)[-1].replace('.', '').lower()

        # if image
        if extension is not None and extension in ('png', 'jpg', 'jpeg', 'gif', 'webp'):
            # calculate dimension
            object_type = 'image'
            if not SKIP_PREPROCESSING_IMAGES:
                try:
                    # imagesize library reads the dimensions from header. It is much faster than by loading the image with PIL
                    object['width'], object['height'] = imagesize.get("../static/" + file_path)
                except:
                    # imagesize doesn't support this image format
                    print("imagesize library doesn't support this image format: " + file_path)
                    pass
        # if video=
        elif extension is not None and extension in ('mp4', 'webm'):
            object_type = 'video'
        elif extension is not None and extension in('mp3', 'ogg', 'wav'):
            # if audio, tag it as such
            object_type = 'audio'
        else:
            # if unknown, tag it as such
            object_type = 'unknown'

        # save found info to object
        object['localFileName'] = file_name
        object['localFilePath'] = file_path
        object['extension'] = extension
        object['type'] = object_type
        return object




    def calculate_local_filenames(self, messages, authors, emojis):
        progress = Progress(messages, 'step 1/3')
        for message in messages.values():
            # calculate attachement filenames
            for attachment in message['attachments']:
                attachment = self.calculateLocalFileAttributes(attachment, attachment['url'])

            # calculate embed filenames
            for embed in message['embeds']:
                if "thumbnail" in embed and embed["thumbnail"] is not None:
                    embed["thumbnail"] = self.calculateLocalFileAttributes(embed["thumbnail"], embed["url"], embed["thumbnail"]["url"])

                if "image" in embed and embed["image"] is not None:
                    embed["image"] = self.calculateLocalFileAttributes(embed["image"], embed["image"]["url"])

                if "images" in embed:
                    for image in embed["images"]:
                        image = self.calculateLocalFileAttributes(image, image["url"])

            progress.increment()
        progress.finish()
            # TODO: other embeds and stickers


        progress = Progress(messages, 'step 2/3')
        for emoji in emojis.values():
            if "imageUrl" in emoji:
                emoji = self.calculateLocalFileAttributes(emoji, emoji["imageUrl"])
            else:
                print("Emoji without imageUrl: " + emoji["name"])

            progress.increment()
        progress.finish()

        progress = Progress(messages, 'step 3/3')
        for author in authors.values():
            author = self.calculateLocalFileAttributes(author, author["avatarUrl"])

            progress.increment()
        progress.finish()

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
        if not is_compiled():
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

        # pprint(thread_id_to_message_id)

        return thread_id_to_message_id

    def process(self):
        print("Step 1 - Reading data from json files...")
        channels, messages = self.read_channels_messages_from_files()

        print("Step 2 - Sorting messages and channels...")
        # sort messages dict by key
        messages = dict(sorted(messages.items()))
        # sort channels dict by key
        channels = dict(sorted(channels.items()))

        # print message count
        print("Message count: " + str(len(messages)))

        print("Step 3 - Deduplicating authors...")
        messages, authors = self.extract_authors(messages)

        print("Step 4 - Deduplicating reactions...")
        messages, emojis = self.extract_emoji(messages)

        print("Step 5 - Finding and preprocessing referenced local filenames...")
        messages = self.calculate_local_filenames(messages, authors, emojis)

        print("Step 6 - Getting file extensions...")
        extensions = self._get_extensions(messages)

        print("Step 7 - Removing unused fields...")
        messages = self.cleanup_empty_fields(messages)

        output_dir = '../static/data/' + self.guild_id + '/'
        print("Step 8 - Deleting cache directory '" + output_dir + "'...")
        self.cleanup_out_directory(output_dir)

        # group messages by channels
        print("Step 9 - Grouping messages by channel...")
        messages_by_channel, categories, threads = self.group_messages_and_channels(
            messages, channels)

        # get message ids
        message_ids = list(messages.keys())

        print("Step 9 - Creating lookup thread ids -> to message ids...")
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

        print("Step 10 - Writing guild JSON...")
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
        print("Found " + str(len(json_files)) + " JSON files")
        print("Found " + str(len(media_filepaths)) + " media files\n")

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
            print("Hash is the same, /static/data is up to date")
            return False
        else:
            # write new hash to file
            with open('../static/data/hash.txt', 'w') as f:
                f.write(new_hash)

            print("Hash is different, /static/data is not up to date")
            return True


    def process(self):
        json_files = self._find_json_files(self.input_directory)
        media_filepaths = self._find_all_mediafiles_paths(self.input_directory)

        if not self.should_process(json_files, media_filepaths):
            return

        guilds = {}

        print("\nSorting JSONs by guild_id...")
        progress = Progress(json_files, '')
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

            progress.increment()
        progress.finish()

        # loop through each guild
        for guild_id, json_filepaths in json_paths_by_guild.items():
            print("\nProcessing guild '" + guilds[guild_id]['name'] + "'")
            gp = GuildPreprocess(guild_id, self.input_directory,
                                 json_filepaths, media_filepaths)
            guilds[guild_id] = gp.calculateGuildFilename(guilds[guild_id])
            gp.process()

        print("\nWriting guild list JSON")
        # write guilds to json file
        if not is_compiled():
            with open('../static/data/guilds.json', 'w', encoding="utf8") as f:
                json.dump(guilds, f, indent=4)
        with open('../static/data/guilds.min.json', 'w', encoding="utf8") as f:
            json.dump(guilds, f)

        print("PREPROCESS DONE")

    def get_files(self):
        return self.files


def main():
    p = Preprocess('../static/input/')
    p.process()


if __name__ == '__main__':
    main()

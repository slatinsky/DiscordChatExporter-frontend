import os
import re
import json
import helpers
import shutil
from hashlib import sha256
from pprint import pprint
import imagesize


from Progress import Progress
from Assets import Assets


class GuildPreprocess:
    def __init__(self, guild_id, input_dir, output_dir, json_filepaths, media_filepaths, ids_from_html, channel_order):
        self.guild_id = guild_id
        self.assets = Assets(input_dir, media_filepaths, ids_from_html)
        self.json_filepaths = json_filepaths
        self.ids_from_html = ids_from_html
        self.channel_order = channel_order
        self.output_dir = output_dir

    ## if any field in data has key 'id', pad it with zeros for fast sorting
    def pad_ids(self, data):
        data['guild']['id'] = helpers.pad_id(data['guild']['id'])
        data['channel']['id'] = helpers.pad_id(data['channel']['id'])

        data['channel']['categoryId'] = helpers.pad_id(data['channel']['categoryId'])


        # for message in data.messages:
        for message in data['messages']:
            message['id'] = helpers.pad_id(message['id'])
            message['author']['id'] = helpers.pad_id(message['author']['id'])

            for reaction in message['reactions']:
                reaction['emoji']['id'] = helpers.pad_id(reaction['emoji']['id'])

            # mentions
            for mention in message['mentions']:
                mention['id'] = helpers.pad_id(mention['id'])

            # attachments
            for attachment in message['attachments']:
                attachment['id'] = helpers.pad_id(attachment['id'])

            # sticker
            for sticker in message['stickers']:
                sticker['id'] = helpers.pad_id(sticker['id'])

            if 'reference' in message:
                if message['reference']['messageId'] is not None:
                    message['reference']['messageId'] = helpers.pad_id(message['reference']['messageId'])
                if message['reference']['channelId'] is not None:
                    message['reference']['channelId'] = helpers.pad_id(message['reference']['channelId'])
                if message['reference']['guildId'] is not None:
                    message['reference']['guildId'] = helpers.pad_id(message['reference']['guildId'])
        return data

    def _merge_messages(self, message1, message2):
        """
        smart merge of two messages
        Keeps most recent data
        Tries to use local URLs if available
        Prefers undeleted author from older message
        """
        # set the latest timestamp as base_message
        if message1['timestamp'] > message2['timestamp']:
            newer_message = message1
            older_message = message2
        else:
            newer_message = message2
            older_message = message1

        # Prefer local media over remote media even if that means that we are working with older data
        # TODO: copy over only URLs, not the whole objects
        if newer_message['author']['avatarUrl'].startswith('http') and not older_message['author']['avatarUrl'].startswith('http'):
            newer_message['author']['avatarUrl'] = older_message['author']['avatarUrl']
            newer_message['attachments'] = older_message['attachments']
            newer_message['embeds'] = older_message['embeds']
            newer_message['stickers'] = older_message['stickers']
            newer_message['reactions'] = older_message['reactions']
            newer_message['mentions'] = older_message['mentions']

        # try to save the author name if deleted in newer backups
        if newer_message['author']['name'] == 'Deleted User' and newer_message['author']['discriminator'] == '0000':
            newer_message['author'] = older_message['author']

        return newer_message

    def read_channels_messages_from_files(self):
        channels = {}
        messages = {}

        message_ids_by_channel_by_files = {}  # key is channelId, value is list of files containing list of message ids

        progress = Progress(self.json_filepaths)
        for path in self.json_filepaths:
            with open(path, 'r', encoding="utf8") as f:
                # print("Reading file: " + path)
                data = json.load(f)
                # message_ids_by_files.append([int(message['id']) for message in data['messages']])
                data = self.pad_ids(data)
                channel = data['channel']

                message_ids_in_file = [int(message['id']) for message in data['messages']]
                if channel['id'] not in message_ids_by_channel_by_files:
                    message_ids_by_channel_by_files[channel['id']] = []
                message_ids_by_channel_by_files[channel['id']].append(message_ids_in_file)


                if channel['category'] == '<unknown category>':
                    channel['categoryId'] = '-2'
                    channel['category'] = "lost channels"


                if channel['id'] not in channels:
                    channels[channel['id']] = channel

                # Copy messages temporarily to the guild
                for message in data['messages']:
                    # temporary marker for channel id
                    message['channelId'] = channel['id']
                    if message['id'] not in messages:
                        messages[message['id']] = message
                    else:
                        messages[message['id']] = self._merge_messages(messages[message['id']], message)
                progress.increment()

        progress.finish()

        return channels, messages, message_ids_by_channel_by_files

    def find_deleted_messages_ids(self, messages, message_ids_by_channel_by_files):
        """
        Find deleted message ids in O(n) time
        """

        deleted_message_ids = set()

        progress = Progress(message_ids_by_channel_by_files)
        for channel_id in message_ids_by_channel_by_files:
            lists = message_ids_by_channel_by_files[channel_id]

            # convert lists to sets
            sets = []
            united_set = set()
            for list_ in lists:
                sets.append(set(list_))
                united_set = united_set.union(set(list_))

            united_list = list(united_set)
            united_list.sort()

            # optimize for slicing in a loop
            united_list_value_lookup = {}
            for i in range(len(united_list)):
                united_list_value_lookup[united_list[i]] = i

            # find missing ids
            for set_ in sets:
                set_min = min(set_)
                set_max = max(set_)
                # united_set_in_range = set([x for x in united_set if x >= set_min and x <= set_max])   # SLOW ALTERNATIVE
                united_set_in_range = set(united_list[united_list_value_lookup[set_min]:united_list_value_lookup[set_max]+1])
                deleted_message_ids = deleted_message_ids.union(united_set_in_range - set_)
            progress.increment()
        progress.finish(f"Found {len(deleted_message_ids)} deleted messages")

        # convert to list
        deleted_message_ids = list(deleted_message_ids)

        # tag messages
        for message_id in deleted_message_ids:
            messages[helpers.pad_id(message_id)]['isDeleted'] = True
        for message_id in messages:
            if 'isDeleted' not in messages[message_id]:
                messages[helpers.pad_id(message_id)]['isDeleted'] = False
        return messages

    def simulate_thread_creation(self, channels, messages):
        """
        Sometimes threads are exported, but original channel is not
        Because forum exports are not supported by DiscordChatExported, this is always the case
        Internally forum posts are Threads
        """

        thread_ids = []  # list of exported thread ids
        for channel in channels.values():
            if channel['type'] == "GuildPublicThread":
                thread_ids.append(channel['id'])

        not_found_thread_ids = thread_ids  # list of thread ids without corresponding message with type 'ThreadCreated' 

        for message in messages.values():
            if message['type'] == "ThreadCreated":
                if message['reference']['channelId'] in not_found_thread_ids:
                    not_found_thread_ids.remove(message['reference']['channelId'])

        first_messages_in_channels = {}
        channel_msg_count = {}
        for message in messages.values():
            if message['channelId'] not in first_messages_in_channels or message['timestamp'] < first_messages_in_channels[message['channelId']]['timestamp']:
                first_messages_in_channels[message['channelId']] = message

            if message['channelId'] not in channel_msg_count:
                channel_msg_count[message['channelId']] = 0
            channel_msg_count[message['channelId']] += 1


        # insert fake "ThreadCreated" message for each thread that does not have one
        for thread_id in not_found_thread_ids:
            thread = channels[thread_id]

            first_message_in_thread = first_messages_in_channels[thread_id]
            thread_id_plus_one = helpers.pad_id(int(thread_id) + 1)  # if we don't increment, we would overwrite the first message before the thread was created
            fake_thread_created_message = {
                'id': thread_id_plus_one,
                'type': "ThreadCreated",
                'timestamp': first_message_in_thread['timestamp'],
                'timestampEdited': None,
                'callEndedTimestamp': None,
                'isPinned': False,
                'content': "Started a thread.",
                'reference': {
                    'messageId': None,
                    'channelId': thread_id,
                    'guildId': self.guild_id,
                },
                'channelId': thread['categoryId'],
                'author': first_message_in_thread['author'],
                'threadName': thread['name'],
                'threadMsgCount': channel_msg_count[thread_id],
                'reactions': [],
                'attachments': [],
                'embeds': [],
                'stickers': [],
                'mentions': [],
            }
            messages[thread_id_plus_one] = fake_thread_created_message

        return channels, messages

    def sort_messages_and_channels(self, messages, channels, channel_order):
        # sort messages dict by key
        messages = dict(sorted(messages.items()))

        # add channel order to channels
        for channel in channels.values():
            channel['order'] = channel_order.get(channel['id'], 999999)

        # self.channel_order key is channel id, value is the order
        # channel's id is channel['id']
        channels = dict(sorted(channels.items(), key=lambda item: item[1]['order']))
        return messages, channels

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
                authors[author['id']]['messagesCount'] = 0

            # extract author information from his last message (by message id)
            elif authors[author['id']]['message_id'] < message['id']:
                messages_count = authors[author['id']]['messagesCount']
                authors[author['id']] = author  # overwrite the same author with more recent data
                authors[author['id']]['messagesCount'] = messages_count

            authors[author['id']]['messagesCount'] += 1

        # cleanup temp message_ids
        for author in authors.values():
            del author['message_id']

        # cleanup author information from messages
        for message in messages.values():
            message['authorId'] = message['author']['id']
            del message['author']

        # order authors by messagesCount desc
        authors = {k: v for k, v in sorted(authors.items(), key=lambda item: item[1]['messagesCount'], reverse=True)}

        return messages, authors

    def extract_emoji(self, messages):
        emojis = {}
        for message in messages.values():
            for reaction in message['reactions']:
                reaction['emoji']['name'] = helpers.get_emoji_code(reaction['emoji']['name'])
                if reaction['emoji']['id'] == "":
                    emoji_id = reaction['emoji']['name']
                else:
                    emoji_id = reaction['emoji']['id'] + "_" + reaction['emoji']['name']

                if emoji_id not in emojis:
                    reaction['emoji']['usedCount'] = reaction['count']
                    emojis[emoji_id] = reaction['emoji']
                else:
                    reaction['emoji']['usedCount'] = emojis[emoji_id]['usedCount'] + reaction['count']
                    emojis[emoji_id] = reaction['emoji']

                emojis[emoji_id]['key'] = emoji_id
                reaction['emojiId'] = emoji_id
                del reaction['emoji']

        # order emojis by usedCount desc
        emojis = {k: v for k, v in sorted(emojis.items(), key=lambda item: item[1]['usedCount'], reverse=True)}

        return messages, emojis

    def _get_extensions(self, messages):
        extensions = set()
        for message in messages.values():
            for attachment in message['attachments']:
                if 'url' in attachment and 'extension' in attachment['url']:
                    # extensions.add(attachment['extension'])
                    # extensions.add(os.path.splitext(attachment['localFileName'])[-1].replace('.', '').lower())
                    extensions.add(os.path.splitext(attachment['url']['extension'])[0])
        exten_list = list(extensions)
        exten_list.sort()
        return exten_list

    def calculate_guild_filename(self, guild):
        guild['localFileName'] = self.assets.filename_from_url_or_path(guild['iconUrl'])
        guild['localFilePath'] = self.assets.get_filepath(guild['localFileName'])
        return guild


    def calculate_local_filenames(self, messages, authors, emojis):
        progress = Progress(messages, 'step 1/3')
        for message in messages.values():
            self.assets.fill_message_with_local_filenames(message)
            progress.increment()
        progress.finish()
            # TODO: other embeds and stickers


        progress = Progress(messages, 'step 2/3')
        for emoji in emojis.values():
            self.assets.fill_emoji_with_local_filenames(emoji)

            progress.increment()
        progress.finish()

        progress = Progress(messages, 'step 3/3')
        for author in authors.values():
            self.assets.fill_author_with_local_filenames(author)
            progress.increment()
        progress.finish()

        return messages

    def group_messages_and_channels(self, messages, channels, channel_order):

        # messages by channel
        messages_by_channel = {}

        for message in messages.values():
            channel_id = message['channelId']
            if channel_id not in messages_by_channel:
                messages_by_channel[channel_id] = {}
            messages_by_channel[channel_id][message['id']] = message

        # add messageCount to channels
        for channel in channels.values():
            channel_id = channel['id']
            if channel_id in messages_by_channel:
                channel['messageCount'] = len(messages_by_channel[channel_id])
            else:
                channel['messageCount'] = 0

        # split channels into threads or normal channels
        threads = {}
        normal_channels = {}  # non thread channels
        for channel in channels.values():
            if channel['type'] == "GuildTextChat" or channel['type'] == "DirectTextChat" or channel['type'] == "DirectGroupTextChat" or channel['type'] == "GuildVoiceChat":
                normal_channels[channel['id']] = channel
            elif channel['type'] == "GuildPublicThread":
                threads[channel['id']] = channel
            else:
                print("Unknown channel type: " + channel['type'])


        # group channels by categories
        categories = {}


        # handle threads without exported channel (FORUMS)
        for channel in threads.values():
            if channel['categoryId'] not in normal_channels:
                print(f"   Found thread '{channel['name']}' without exported channel '{channel['category']}'")

                # add channel to normal channels
                channel_info = {
                    'id': channel['categoryId'],
                    'name': channel['category'],
                    'type': "GuildTextChat",
                    'messageCount': len(messages_by_channel[channel['categoryId']].values()),
                    'categoryId': "-1",
                    'category': "forums/lost threads",
                    'threads': []
                }
                normal_channels[channel['categoryId']] = channel_info
                channels[channel['categoryId']] = channel_info

                # add thread to channel
                normal_channels[channel['categoryId']]['threads'].append(channel)


        for channel in normal_channels.values():
            if channel['categoryId'] not in categories:
                if 'threads' not in channel:
                    channel['threads'] = []

                if channel['categoryId'] in channel_order:  # order may not exist
                    order = channel_order[channel['categoryId']]
                else:
                    order = 99999999

                categories[channel['categoryId']] = {
                    'id': channel['categoryId'],
                    'name': channel['category'],
                    'threads': channel['threads'],
                    'channelIds': [],
                    'order': order,
                }


            # add channel id to category
            categories[channel['categoryId']]['channelIds'].append({
                'id': channel['id'],
                'name': channel['name'],
                'type': "text",
            })

        # order categories by order
        categories = {k: v for k, v in sorted(categories.items(), key=lambda item: item[1]['order'])}


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

        return messages_by_channel, categories, threads, channels

    def cleanup_out_directory(self, output_dir):
        if os.path.exists(output_dir):
            # delete existing output_dir directory and all its contents
            shutil.rmtree(output_dir)
        os.makedirs(output_dir)  # recreate the directory

    def write_json(self, data, filename):
        if not helpers.is_compiled():
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
        print("Step 0 - Reading data from json files...")
        channels, messages, message_ids_by_channel_by_files = self.read_channels_messages_from_files()

        print("Step 1 - Finding deleted messages...")
        messages = self.find_deleted_messages_ids(messages, message_ids_by_channel_by_files)

        print("Step 2 - Recreating forums and missing channels from threads...")
        channels, messages = self.simulate_thread_creation(channels, messages)

        print("Step 3 - Sorting messages and channels...")
        messages, channels = self.sort_messages_and_channels(messages, channels, self.channel_order)

        # print message count
        print("   Message count: " + str(len(messages)))
        print("   Channel+Thread count: " + str(len(channels)))  # includes forum threads

        print("Step 4 - Deduplicating authors...")
        messages, authors = self.extract_authors(messages)

        print("Step 5 - Deduplicating reactions...")
        messages, emojis = self.extract_emoji(messages)

        print("Step 6 - Finding and preprocessing referenced local filenames...")
        messages = self.calculate_local_filenames(messages, authors, emojis)

        print("Step 7 - Getting file extensions...")
        extensions = self._get_extensions(messages)

        print("Step 8 - Removing unused fields...")
        messages = self.cleanup_empty_fields(messages)

        output_dir = self.output_dir + self.guild_id + '/'
        print("Step 9 - Deleting cache directory '" + output_dir + "'...")
        self.cleanup_out_directory(output_dir)

        # group messages by channels
        print("Step 10 - Grouping messages by channel...")
        messages_by_channel, categories, threads, channels = self.group_messages_and_channels(
            messages, channels, self.channel_order)

        # get message ids
        message_ids = list(messages.keys())

        print("Step 11 - Creating lookup thread ids -> to message ids...")
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

        print("Step 12 - Writing guild JSON...")
        self.write_json(guild, output_dir + 'guild.json')


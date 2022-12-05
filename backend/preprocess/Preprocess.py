import glob
import json
from pprint import pprint
import re
from hashlib import sha256
import os

import requests

from Progress import Progress
from GuildPreprocess import GuildPreprocess
import helpers


class Preprocess:
    def __init__(self, input_directory, output_directory):
        self.input_directory = input_directory
        self.output_directory = output_directory
        self.guilds = {}
        self.channels = {}
        self.messages = {}
        self.authors = {}
        self.emojis = {}
        self.mentions = {}

    # recursively find all json files in the current directory
    # and print the thread ids to stdout
    def _find_json_files(self, directory):
        files = []
        for filename in glob.glob(directory + '**/*.json', recursive=True):
            if filename.endswith('.json'):
                # print(filename)
                files.append(filename)
        return files

    def _find_html_files(self, directory):
        files = []
        for filename in glob.glob(directory + '**/*.html', recursive=True):
            if filename.endswith('.html'):
                # print(filename)
                files.append(filename)
        return files

    def _find_all_mediafiles_paths(self, directory):
        all_files = {}
        regex_pattern = re.compile(r'.+\-[A-F0-9]{5}\..+')
        for path in glob.glob(directory + '**/*', recursive=True):
            if regex_pattern.match(path):
                filename = os.path.basename(path)
                all_files[filename] = path.replace('\\', '/')

        return all_files

    def should_process(self, json_files, media_filepaths, html_filepaths):
        print("Found " + str(len(json_files)) + " JSON files")
        print("Found " + str(len(html_filepaths)) + " HTML files\n")
        print("Found " + str(len(media_filepaths)) + " media files\n")

        # make directory if it doesn't exist
        if not os.path.exists(self.output_directory):
            os.makedirs(self.output_directory)

        # if data/hash.txt does exists read the hash
        if os.path.exists(self.output_directory + '/hash.txt'):
            with open(self.output_directory + '/hash.txt', 'r') as f:
                hash_from_file = f.read()
                print("Hash: " + hash_from_file)
        else:
            print("Hash file does not exist")
            hash_from_file = None

        # create hash of this script
        if os.path.exists(__file__):
            filenames = [
                'GuildPreprocess.py',
                'helpers.py',
                'main.py',
                'Preprocess.py',
                'Progress.py',
                'Assets.py',
            ]
            all_content = b''
            for filename in filenames:
                with open(filename, 'rb') as f:
                    all_content += f.read()

            hash_of_script = sha256(all_content).hexdigest()
        elif os.path.exists('preprocess.exe'):
            hash_of_script = sha256(
                open('preprocess.exe', 'rb').read()).hexdigest()
        else:
            hash_of_script = ""
            print("Could not find preprocess file")

        # create hash of all files
        # if hash is the same, then we can skip processing
        # because reprocessing takes a lot of time
        new_hash = sha256((str(json_files) + str(media_filepaths) +
                          str(html_filepaths) + hash_of_script).encode('utf-8')).hexdigest()

        if hash_from_file == new_hash:
            print("Hash is the same, cache is up to date")
            return False
        else:
            # write new hash to file
            with open(self.output_directory + '/hash.txt', 'w') as f:
                f.write(new_hash)

            print("Hash is different, cache is not up to date")
            return True

    def parse_html(self, html_filepaths):
        """
        hacky way to parse html files, because BeautifulSoup is too slow on large HTML files
        Be need theses files to pair embeds with local messages
        """
        ids_from_html = {}
        regex_pattern_message_id = re.compile(r'^(\d+)')
        regex_pattern_files = re.compile(
            r'chatlog__embed.*?html_Files\/([^ >]+)>? (?!alt=Avatar)')

        progress = Progress(html_filepaths)
        for html_filepath in html_filepaths:
            with open(html_filepath, 'r', encoding='utf-8') as f:
                html = f.read()
                messages = html.split('chatlog__message-container-')
                for message in messages:
                    matches = regex_pattern_message_id.findall(message)
                    if len(matches) == 0:
                        continue
                    message_id = matches[0]
                    padded_id = helpers.pad_id(message_id)
                    matches = regex_pattern_files.findall(message)
                    for filename in matches:
                        if padded_id not in ids_from_html:
                            ids_from_html[padded_id] = []

                        ids_from_html[padded_id].append(filename)
                        ids_from_html[padded_id] = list(
                            set(ids_from_html[padded_id]))  # deduplicate

            progress.increment()
        progress.finish("Found " + str(len(ids_from_html)) +
                        " message ids in HTML files")
        return ids_from_html

    def get_channel_order(self, json_files):
        """
        get the order of channels in the guild
        channel_info.json is not created by DiscordChatExporter, it is created by slatinsky/DiscordChatExporter-incrementalBackup
        threat it as optional - it may not be Bratislava
        """

        number_of_files = 0

        channel_infos = []
        for filename in json_files:
            if 'channel_info.json' not in filename:
                continue
            with open(filename, 'r', encoding='utf-8') as f:
                try:
                    data = json.load(f)
                    data.pop('threads', None)  # less memory used
                    channel_infos.append(data)
                    number_of_files += 1
                except:
                    print("   (get_channel_order) Error parsing " + filename)
                    continue

        if number_of_files == 0:
            print(
                "   Could not find any channel_info.json, channels and categories won't be sorted")
            return {}
        else:
            print("   Found " + str(number_of_files) +
                  " channel_info.json files")

        # sort by timestamp
        channel_infos.sort(key=lambda x: x['timestamp'])

        channel_order = {}  # key is channel_id, value is index
        for channel_info in channel_infos:
            for channel in channel_info['channels']:
                position = channel['position']
                if channel['type'] == 2:  # audio channel
                    position += 2000  # penalize audio channels, they should be at the bottom
                channel_order[helpers.pad_id(
                    channel['id'])] = channel['position']

        # add position for null category (TEXT CHANNELS)
        channel_order[helpers.pad_id(0)] = -1
        channel_order[-2] = 99999998  # channels with unknown category
        channel_order[-1] = 99999999  # lost threads and forum channels
        return channel_order

    def download_gg(self):
        """
        download gg sans if not already downloaded
        we cannot directly include it, because it is not open source
        """
        paths = {
            "ggsans-normal-400.woff2": "https://discord.com/assets/a798bb95e0f5a69c8ab85e53103ba6b2.woff2",
            "ggsans-italic-400.woff2": "https://discord.com/assets/8ca69301ef43643d9c7e14036f80061d.woff2",
            "ggsans-normal-500.woff2": "https://discord.com/assets/637ce9c046bf63b68fa35412518822d5.woff2",
            "ggsans-italic-500.woff2": "https://discord.com/assets/e8f55fa2303208454eaa0fbde8920d3f.woff2",
            "ggsans-normal-600.woff2": "https://discord.com/assets/4f2e4275143211c2492a31ca2c9669fb.woff2",
            "ggsans-italic-600.woff2": "https://discord.com/assets/fb1134f6438f4d0610260294891aa56e.woff2",
            "ggsans-normal-700.woff2": "https://discord.com/assets/bd88a0d8f72ec18529956748c2e00547.woff2",
            "ggsans-italic-700.woff2": "https://discord.com/assets/4893950fe590addffb6515237f1d1014.woff2",
            "ggsans-normal-800.woff2": "https://discord.com/assets/ec68b736b0006bb42d8a44528aafe796.woff2",
            "ggsans-italic-800.woff2": "https://discord.com/assets/ba1f0a8f593aa3c705d8de718f7c8d9a.woff2"
        }
        save_dir = os.path.join(self.output_directory, "fonts")
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

        for filename, url in paths.items():
            save_path = os.path.join(save_dir, filename)
            if not os.path.exists(save_path):
                print("   Downloading", filename)
                try:
                    r = requests.get(url)
                    with open(save_path, 'wb') as f:
                        f.write(r.content)
                except:  # discord may change the url
                    print("   Error downloading", filename)

    def process(self):
        json_files = self._find_json_files(self.input_directory)
        html_files = self._find_html_files(self.input_directory)
        media_filepaths = self._find_all_mediafiles_paths(self.input_directory)

        if not self.should_process(json_files, media_filepaths, html_files):
            return

        guilds = {}

        self.download_gg()

        print("\nSorting JSONs by guild_id...")
        progress = Progress(json_files, '')
        # sort filenames by guild to attempt to split ram usage
        json_paths_by_guild = {}
        for filename in json_files:  # each filename contains channel/thread dump
            with open(filename, 'r', encoding='utf-8') as f:
                try:
                    data = json.load(f)
                except json.decoder.JSONDecodeError:
                    # probably media file too
                    print("JSONDecodeError: " + filename)
                    continue
                if 'guild' not in data:  # this is not a channel export, but a downloaded media json file
                    continue
                guild_id = helpers.pad_id(data['guild']['id'])
                data['guild']['id'] = guild_id
                guilds[guild_id] = data['guild']
                if guild_id not in json_paths_by_guild:
                    json_paths_by_guild[guild_id] = []

                json_paths_by_guild[guild_id].append(filename)

            progress.increment()
        progress.finish()

        print("\nGetting channels and categories sort...")
        channel_order = self.get_channel_order(json_files)

        print("\nProcessing HTML...")
        ids_from_html = self.parse_html(html_files)

        # loop through each guild
        for guild_id, json_filepaths in json_paths_by_guild.items():
            print("\nProcessing guild '" + guilds[guild_id]['name'] + "'")
            gp = GuildPreprocess(guild_id, self.input_directory, self.output_directory,
                                 json_filepaths, media_filepaths, ids_from_html, channel_order)
            guilds[guild_id] = gp.calculate_guild_filename(guilds[guild_id])
            gp.process()

        print("\nWriting guild list JSON")
        # write guilds to json file
        if not helpers.is_compiled():
            with open(self.output_directory + 'guilds.json', 'w', encoding="utf8") as f:
                json.dump(guilds, f, indent=4)
        with open(self.output_directory + '/guilds.min.json', 'w', encoding="utf8") as f:
            json.dump(guilds, f)

        print("PREPROCESS DONE")

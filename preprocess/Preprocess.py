import glob
import json
from pprint import pprint
import re
from hashlib import sha256
import os

from Progress import Progress
from GuildPreprocess import GuildPreprocess
import helpers


class Preprocess:
    def __init__(self, input_directory):
        self.input_directory = input_directory
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
            print("Hash is the same, /static/data is up to date")
            return False
        else:
            # write new hash to file
            with open('../static/data/hash.txt', 'w') as f:
                f.write(new_hash)

            print("Hash is different, /static/data is not up to date")
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
        progress.finish("Found " + str(len(ids_from_html)) + " message ids in HTML files")
        return ids_from_html

    def process(self):
        json_files = self._find_json_files(self.input_directory)
        html_files = self._find_html_files(self.input_directory)
        media_filepaths = self._find_all_mediafiles_paths(self.input_directory)

        if not self.should_process(json_files, media_filepaths, html_files):
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

        print("\nProcessing HTML...")
        ids_from_html = self.parse_html(html_files)

        # loop through each guild
        for guild_id, json_filepaths in json_paths_by_guild.items():
            print("\nProcessing guild '" + guilds[guild_id]['name'] + "'")
            gp = GuildPreprocess(guild_id, self.input_directory,
                                 json_filepaths, media_filepaths, ids_from_html)
            guilds[guild_id] = gp.calculate_guild_filename(guilds[guild_id])
            gp.process()

        print("\nWriting guild list JSON")
        # write guilds to json file
        if not helpers.is_compiled():
            with open('../static/data/guilds.json', 'w', encoding="utf8") as f:
                json.dump(guilds, f, indent=4)
        with open('../static/data/guilds.min.json', 'w', encoding="utf8") as f:
            json.dump(guilds, f)

        print("PREPROCESS DONE")

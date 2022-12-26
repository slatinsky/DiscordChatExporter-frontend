from hashlib import sha256
import os
from pprint import pprint
import re

import imagesize

SKIP_PREPROCESSING_IMAGES = False

class Assets:
    def __init__(self, input_dir: str, media_filepaths: dict, ids_from_html) -> None:
        self.input_dir = input_dir

        # key is filename with hash, value is filepath - example:
        # 'unknown-39F95.png': '../exports/.../unknown-39F95.png'
        self.media_filepaths = media_filepaths

        # key is padded message id, value is list of filenames found in the message - example:
        #  '000000925496199990046890': ['unknown-DCBC9.gif'],
        self.ids_from_html = ids_from_html

    def get_filepath(self, filename_with_hash: str) -> str:
        """
        self.media_filepaths contain paths relative to our script. Change urls to be relative to the static directory.
        """
        if filename_with_hash in self.media_filepaths:
            filepath = self.media_filepaths[filename_with_hash].replace(self.input_dir, '/input/')
            # if file empty (file is invalid), don't return path
            try:
                if os.stat(self.media_filepaths[filename_with_hash]).st_size == 0:
                    return None
                return filepath
            except FileNotFoundError:
                print("   File not found: " + self.media_filepaths[filename_with_hash])
                return None
        else:
            return None

    def is_remote_url(self, url):
        return re.match(r'^https?://', url)

    def filename_from_url_or_path(self, url_or_path: str) -> str:
        """
        calculate the filename with hash based on the path.
        Path can be local or remote.
        """
        if url_or_path is None:
            return ""
        is_remote_url = self.is_remote_url(url_or_path)

        if is_remote_url:  # calculate filename for url
            # should be reimplemented the same way as https://github.com/Tyrrrz/DiscordChatExporter/blob/38be44debbd25f73eef4f7c51c6af7420626d261/DiscordChatExporter.Core/Exporting/MediaDownloader.cs#L89 in javascript
            # C#: var fileName = Regex.Match(url, @".+/([^?]*)").Groups[1].Value;
            filename = re.match(r'.+/([^?]*)', url_or_path).groups()[0]
            filename_without_ext, filename_ext = os.path.splitext(filename)

            if len(filename_ext) > 41:
                filename_without_ext = filename
                filename_ext = ""

            # remove get parameters
            # hashed filename must contain get parameters
            hash_sha256 = sha256(url_or_path.encode('utf-8')).hexdigest()[:5].upper()

            # filename = filename.split('?')[0]
            # base, extension = os.path.splitext(filename)
            filename = filename_without_ext[:42] + "-" + hash_sha256 + filename_ext
        else:  # filename already contains hash
            filename = url_or_path.replace('\\', '/').split('/')[-1]
        return filename

    def find_in_html_ids(self, message_id, filename_to_find: str) -> str or None:
        if message_id in self.ids_from_html:
            for filename_from_html in self.ids_from_html[message_id]:
                # get string from filename start to the first '-', without extension
                reduced_fn_from_html = filename_from_html.split('-')[0]
                reduced_fn_to_find = filename_to_find.split('-')[0].split('.')[0]

                if reduced_fn_to_find == 'tenor':
                    return self.get_filepath(filename_from_html)
                if reduced_fn_from_html == reduced_fn_to_find:
                    # print("Found file: " + filename)
                    return self.get_filepath(filename_from_html)
        return None

    def find_local_asset(self, url: str, messageId) -> str or None:
        file_name = self.filename_from_url_or_path(url)
        file_path = self.get_filepath(file_name)
        if file_path is not None:
            return file_path
        else:
            # print("File not found: " + file_name)
            return None

    def resolve_url_or_path(self, url_or_path: str, message_id= None) -> str:
        """
        Convert original url_or_path found in json to local path.
        If local path is not found, return original remote url if available.
        """
        # Return none if url_or_path is None
        if url_or_path is None or url_or_path == "":
            return None

        file_name_with_hash = self.filename_from_url_or_path(url_or_path)

        # url_or_path is remote, try to find local asset file
        # if asset file not found, return remote url as fallback
        if self.is_remote_url(url_or_path):
            remote_url = url_or_path
            local_url = self.get_filepath(file_name_with_hash)
            if local_url is None:
                local_url_from_html = self.find_in_html_ids(message_id, file_name_with_hash)
                if local_url_from_html is None:
                    # print("Local asset not found, using remote asset: ", remote_url)
                    return remote_url
                else:
                    return local_url_from_html
            else:
                return local_url

        # url_or_path is local, verify, if asset file exists
        else:
            local_url = self.get_filepath(file_name_with_hash)
            if local_url is None:
                # don't try to find in html, because conversion to local url already happened
                return None
            else:
                return local_url



    def get_file_type(self, extension: str) -> str:
        if extension is None:
            return None
        elif extension in ('png', 'jpg', 'jpeg', 'gif', 'webp'):
            return 'image'
        elif extension in ('mp4', 'webm', 'mov'):
            return 'video'
        elif extension in('mp3', 'ogg', 'wav'):
            return 'audio'
        else:
            return 'unknown'


    def calculate_local_file_attributes(self, message_id, url_or_path):
        result = {
            # 'original': url_or_path,  # for debug only, not useful in the viewer
        }
        file_name_with_hash = self.filename_from_url_or_path(url_or_path)
        result['hashedFilename'] = file_name_with_hash
        resolved_url_or_path = self.resolve_url_or_path(url_or_path, message_id)
        result['extension'] = os.path.splitext(file_name_with_hash)[-1].replace('.', '').lower()
        result['type'] = self.get_file_type(result['extension'])

        if resolved_url_or_path is None:  # file not found and url is local, file is lost
            return result

        result['url'] = resolved_url_or_path

        if result['type'] == 'image' and not self.is_remote_url(resolved_url_or_path):
            # calculate dimension
            if not SKIP_PREPROCESSING_IMAGES:
                try:
                    # imagesize library reads the dimensions from header. It is much faster than by loading the image with PIL
                    result['width'], result['height'] = imagesize.get(result['url'].replace('/input/', self.input_dir))
                except:
                    # imagesize doesn't support this image format
                    print("   imagesize library doesn't support this image format (is the file corrupted?): ", result['url'])
                    pass

        return result

    def fill_message_with_local_filenames(self, message):
        # calculate attachment filenames
        for attachment in message['attachments']:
            attachment['url'] = self.calculate_local_file_attributes(message['id'], attachment['url'])

        # calculate embed filenames
        for embed in message['embeds']:
            if "thumbnail" in embed and embed["thumbnail"] is not None:
                embed["thumbnail"]["url"] = self.calculate_local_file_attributes(message['id'], embed["thumbnail"]["url"])

            if "image" in embed and embed["image"] is not None:
                embed["image"]["url"] = self.calculate_local_file_attributes(message['id'], embed["image"]["url"])

            if "images" in embed:
                for image in embed["images"]:
                    image["url"] = self.calculate_local_file_attributes(message['id'], image["url"])

    def fill_emoji_with_local_filenames(self, emoji):
        if "imageUrl" in emoji:
                emoji["imageUrl"] = self.calculate_local_file_attributes(None, emoji["imageUrl"])
        else:
            print("Emoji without imageUrl: " + emoji["name"])

    def fill_author_with_local_filenames(self, author):
        author["avatarUrl"] = self.calculate_local_file_attributes(None, author["avatarUrl"])

    def fill_sticker_with_local_filenames(self, sticker):
        sticker["url"] = self.calculate_local_file_attributes(None, sticker["sourceUrl"])


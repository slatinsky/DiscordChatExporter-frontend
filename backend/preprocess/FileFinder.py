import glob
import re
import os

class FileFinder():
	"""
	Find all files in a directory
	"""
	def __init__(self, directory: str):
		self.base_directory = self.normalize_path(directory)

	def find_channel_exports(self):
		print("finding channel exports in " + self.base_directory)
		directory = self.base_directory
		files = []
		for filename in glob.glob(directory + '**/*.json', recursive=True):
			if filename.endswith('.json'):
				# ignore attachment files - they are made by users, not DiscordChatExporter
				if re.search(r"([a-fA-F0-9]{5})\.json$", filename) != None:
					continue

				# ignore channel_info.json
				if filename.endswith('channel_info.json'):
					continue

				# quick check if file is a export made by DiscordChatExporter
				with open(filename, encoding='utf-8') as file:
					first_16_bytes = file.read(16)
					if first_16_bytes.find("guild") == -1:
						print("invalid file " + filename)
						continue
				filename_without_base_directory = self.remove_base_directory(filename)
				files.append(filename_without_base_directory)

		return files

	def find_local_assets(self):
		input_directory = self.base_directory
		all_files = {}
		regex_pattern = re.compile(r'.+\-[a-fA-F0-9]{5}(?:\..+)?')
		for path in glob.glob(input_directory + '**/*', recursive=True):
			if regex_pattern.match(path):
				filename = os.path.basename(path)
				all_files[filename] = path.replace('\\', '/')

		return all_files

	def remove_base_directory(self, path: str):
		"""
		remove base directory from the start of the path
		ignore if path doesn't start with base directory
		"""
		if path == None:
			return None

		path = self.normalize_path(path)
		if not path.startswith(self.base_directory):
			print("path doesn't start with base directory: " + path)
			return path

		return path[len(self.base_directory):]

	def add_base_directory(self, path: str):
		"""
		add base directory to the start of the path
		if path already starts with base directory, do nothing
		"""
		path = self.normalize_path(path)
		if path.startswith(self.base_directory):
			print("path already starts with base directory: " + path)
			return path

		return self.base_directory + path

	def normalize_path(self, path: str):
		"""
		replace all \ with /
		"""
		return path.replace("\\", "/")
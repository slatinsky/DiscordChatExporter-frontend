from functools import cache
import glob
import os
import re

class Storage:
	def __init__(self, input_directory):
		self.input_directory = input_directory
		self.json_files = self._find_json_files(input_directory)
		self.media_files = self._find_media_files(input_directory)

	@cache
	def _find_json_files(self, input_directory):
		files = []
		for filename in glob.glob(input_directory + '**/*.json', recursive=True):
			if filename.endswith('.json'):
				# print(filename)
				files.append(filename.replace('\\', '/'))
		return files

	@cache
	def _find_media_files(self, input_directory):
		all_files = {}
		regex_pattern = re.compile(r'.+\-[A-F0-9]{5}\..+')
		for path in glob.glob(input_directory + '**/*', recursive=True):
			if regex_pattern.match(path):
				filename = os.path.basename(path)
				all_files[filename] = path.replace('\\', '/')

		return all_files

	def remove_input_directory(self, path):
		"""
		strip input directory from path
		used to store relative path in database
		"""
		return path.replace(self.input_directory, '')

	def add_input_directory(self, path):
		"""
		add input directory to path
		used to resolve relative path from database
		"""
		return self.input_directory + path

	def find_asset(self, path):
		"""
		find asset path by filename
		"""
		if re.match(r'^https?://', path):
			return path

		filename = os.path.basename(path)
		if filename in self.media_files:
			return self.media_files[filename]

		# asset not found
		return None
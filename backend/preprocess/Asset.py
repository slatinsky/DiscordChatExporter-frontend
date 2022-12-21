from hashlib import sha256
import os
import re
import imagesize


class Asset:
	def __init__(self, path):
		if path is None:
			self.path = None
			self.filename = None
			self.extension = None
			self.type = None
			self.width = None
			self.height = None
			self.is_online = None
			self.size = None
			return

		self.path = path  # local path or remote url
		self.filename = self._get_filename(path)
		self.extension = self._get_extension(path)
		self.type = self._get_file_type(path)
		self.width = None
		self.height = None
		self.is_online = self._is_remote(path)
		self.width, self.height = self._get_image_size(path)
		self.size = self._get_file_size(path)

	def _resolve_path(self, path: str) -> str:
		"""
		returns absolute path
		"""
		return os.path.abspath(path)

	def _is_remote(self, path: str) -> bool:
		"""
		returns True if path is a remote url
		"""
		# if path is None:
		# 	return None

		if re.match(r'^https?://', path):
			return True

		return False

	def _get_image_size(self, path: str) -> tuple:
		"""
		returns image size as tuple (width, height)
		"""
		# remote path
		if self._is_remote(path):
			return None, None

		# file is not an image
		filetype = self._get_file_type(path)
		if filetype != 'image':
			return None, None

		try:
			return imagesize.get(path)
		except:
			print("Error: Could not get image size of " + path)
			return None, None

	def _get_filename(self, path: str) -> str:
		# local path
		if not self._is_remote(path):
			return os.path.basename(path)

		# remote path (url)
		filename = re.match(r'.+/([^?]*)', path).groups()[0]
		filename_without_ext, filename_ext = os.path.splitext(filename)

		if len(filename_ext) > 41:
			filename_without_ext = filename
			filename_ext = ""

		# hashed filename must contain get parameters
		hash_sha256 = sha256(path.encode('utf-8')).hexdigest()[:5].upper()

		# remove get parameters
		# filename = filename.split('?')[0]
		# base, extension = os.path.splitext(filename)
		filename = filename_without_ext[:42] + "-" + hash_sha256 + filename_ext
		return filename


	def _get_extension(self, path: str) -> str:
		return os.path.splitext(path)[-1].replace('.', '').lower()

	def _get_file_type(self, path: str) -> str:
		extension = self._get_extension(path)
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

	def _get_file_size(self, path: str) -> int:
		if self._is_remote(path):
			return None

		return os.path.getsize(path)
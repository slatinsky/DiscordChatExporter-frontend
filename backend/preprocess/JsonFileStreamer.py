import functools
import ijson
import datetime

from helpers import human_file_size

print = functools.partial(print, flush=True)




class JsonFileStreamer():
	def __init__(self, json_path: str):
		self.json_path = json_path

	def __enter__(self):
		self.file = open(self.json_path, 'rb')
		return self

	def __exit__(self, type, value, traceback):
		self.file.close()

	def get_file_size_human(self) -> str:
		"""
		returns file size in human readable format
		"""
		file_size_bytes = self.get_file_size()

		return human_file_size(file_size_bytes)

	def get_file_pointer_position(self) -> int:
		return self.file.tell()

	def get_file_size(self) -> int:
		"""
		gets file size in bytes
		"""
		self.file.seek(0, 2)
		file_size = self.file.tell()
		return file_size

	def reset_file_pointer(self):
		self.file.seek(0)

	def get_guild(self) -> str:
		"""
		gets guild object from json export file
		"""
		self.reset_file_pointer()
		guild = ijson.items(self.file, 'guild')
		for g in guild:
			return g

	def get_channel(self) -> str:
		"""
		gets channel object from json export file
		"""
		self.reset_file_pointer()
		channel = ijson.items(self.file, 'channel')
		for c in channel:
			return c

	def get_messages_iterator(self):
		"""
		gets messages iterator from json export file
		"""
		self.reset_file_pointer()
		messages = ijson.items(self.file, 'messages.item')
		return messages

	def get_exported_at(self) -> str:
		"""
		gets exportedAt from json export file
		if exportedAt field is not found, estimates it from messages.timestamp and messages.timestampEdited

		returns timestamp as string, for example:
		2023-08-26T04:37:13.8399951+00:00
		"""
		self.reset_file_pointer()
		latestTimestamp = None
		for prefix, event, value in ijson.parse(self.file):

			# print(prefix, event, value)
			if prefix == 'exportedAt':
				exportedAt = value
				print('    found exportedAt field')
				return exportedAt

			if prefix == 'messages.item.timestamp' or prefix == 'messages.item.timestampEdited':
				if value is None:
					continue
				if latestTimestamp is None:
					latestTimestamp = value
				elif value > latestTimestamp:
					latestTimestamp = value

		if latestTimestamp is not None:
			print(f'        warning: exportedAt field not found, using estimated value {latestTimestamp}. Use DCE v2.40.1 or newer')
			return latestTimestamp

		print('    ERROR: exportedAt not found, using current time')
		return datetime.datetime.now().isoformat()
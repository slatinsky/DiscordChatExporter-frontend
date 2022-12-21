import os
import sqlite3

from Asset import Asset
from Storage import Storage


class Database:
	def __init__(self, db_name, input_directory):
		self.input_directory = input_directory
		self.storage = Storage(input_directory)

		# sleep 1 second to prevent database lock
		# time.sleep(1)

		self.db_name = db_name
		# TODO / TEMP: delete database
		if os.path.exists(self.db_name):
			os.remove(self.db_name)
		if os.path.exists(self.db_name + "-shm"):
			os.remove(self.db_name + "-shm")
		if os.path.exists(self.db_name + "-wal"):
			os.remove(self.db_name + "-wal")
		if os.path.exists(self.db_name + "-journal"):
			os.remove(self.db_name + "-journal")
		self.connection = sqlite3.connect(self.db_name)
		self.cursor = self.connection.cursor()
		# set journal size to 4GB
		self.cursor.execute('PRAGMA journal_size_limit=4000000000')
		# set wal mode
		self.cursor.execute('PRAGMA journal_mode=WAL')
		self.create_tables()

		# insert version to config table
		self.cursor.execute('INSERT OR IGNORE INTO config (key, value) VALUES (?, ?)', ('version', '1.0'))


	def commit(self):
		self.connection.commit()

	def create_tables(self):
		# create config table
		self.cursor.execute("""CREATE TABLE IF NOT EXISTS config (
			key TEXT PRIMARY KEY,
			value TEXT
		)""")

		# create messages table
		self.cursor.execute("""CREATE TABLE IF NOT EXISTS messages (
			id TEXT PRIMARY KEY,
			guild_id TEXT,
			category_id TEXT,
			channel_id TEXT,
			type TEXT,
			timestamp TEXT,
			timestamp_edited TEXT,
			is_pinned TEXT,
			is_deleted TEXT,
			content TEXT,
			author_id TEXT
		)""")

		# create users authors
		self.cursor.execute("""CREATE TABLE IF NOT EXISTS authors (
			id TEXT PRIMARY KEY,
			guild_id TEXT,
			name TEXT,
			discriminator TEXT,
			nickname TEXT,
			is_bot TEXT,
			asset_id INTEGER
		)""")
		# message_count INTEGER,

		# create channels table
		self.cursor.execute("""CREATE TABLE IF NOT EXISTS channels (
			id TEXT PRIMARY KEY,
			guild_id TEXT,
			category_id TEXT,
			name TEXT,
			type TEXT,
			position INTEGER,
			topic TEXT
		)""")
		# messageCount INTEGER,

		# create categories table
		self.cursor.execute("""CREATE TABLE IF NOT EXISTS categories (
			id TEXT PRIMARY KEY,
			guild_id TEXT,
			name TEXT,
			position INTEGER
		)""")

		# create guilds table
		self.cursor.execute("""CREATE TABLE IF NOT EXISTS guilds (
			id TEXT PRIMARY KEY,
			name TEXT,
			asset_id INTEGER
		)""")

		# create assets table
		self.cursor.execute("""CREATE TABLE IF NOT EXISTS assets (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			filename TEXT UNIQUE,
			url TEXT,
			extension TEXT,
			type TEXT,
			width INTEGER,
			height INTEGER,
			is_online BOOLEAN,
			size INTEGER
		)""")

		# create emojis table
		self.cursor.execute("""CREATE TABLE IF NOT EXISTS emojis (
			id TEXT PRIMARY KEY,
			guild_id TEXT,
			name TEXT,
			is_animated BOOLEAN,
			asset_id INTEGER
		)""")

		# create messages_emojis table
		self.cursor.execute("""CREATE TABLE IF NOT EXISTS messages_emojis (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			message_id TEXT,
			emoji_id TEXT,
			count INTEGER
		)""")

		# processed files table
		self.cursor.execute("""CREATE TABLE IF NOT EXISTS processed_files (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			path TEXT
		)""")

		# create messages_attachments table
		self.cursor.execute("""CREATE TABLE IF NOT EXISTS messages_attachments (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			message_id TEXT,
			asset_id INTEGER
		)""")

		# create messages_embeds table
		self.cursor.execute("""CREATE TABLE IF NOT EXISTS messages_embeds (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			message_id TEXT,
			asset_id INTEGER
		)""")

	def get_processed_files(self):
		self.cursor.execute('SELECT path FROM processed_files')
		res = self.cursor.fetchall()
		return [self.storage.add_input_directory(path[0]) for path in res]

	def new_processed_file(self, path):
		path = self.storage.remove_input_directory(path)
		self.cursor.execute('INSERT OR IGNORE INTO processed_files (path) VALUES (?)', (path,))



	def new_asset(self, path):
		"""
		creates new asset in database
		if asset already exists, it will be updated
		"""
		asset = Asset(self.storage.find_asset(path))


		# get file size
		# insert assets to assets table and get id
		self.cursor.execute('INSERT OR REPLACE INTO assets (filename, url, extension, type, width, height, is_online, size) VALUES (?, ?, ?, ?, ?, ?, ?, ?)', (
			asset.filename,
			self.storage.remove_input_directory(path),
			asset.extension,
			asset.type,
			asset.width,
			asset.height,
			asset.is_online,
			asset.size
		))

		asset_id = self.cursor.lastrowid

		self.cursor.execute('INSERT INTO processed_files (path) VALUES (?)', (path,))
		# self.cursor.execute('INSERT OR IGNORE INTO assets (filename, url, extension, type, width, height, is_online, size) VALUES (?, ?, ?, ?, ?, ?, ?, ?)', (filename, url, extension, type, width, height, is_online, size))
		# self.connection.commit()

		return asset_id

	def new_channel(self, channel_id, guild_id, category_id, channel_name, channel_type, position, topic):
		"""
		creates new channel in database
		if channel already exists, it will be updated
		"""
		self.cursor.execute('INSERT OR REPLACE INTO channels (id, guild_id, category_id, name, type, position, topic) VALUES (?, ?, ?, ?, ?, ?, ?)', (
			channel_id,
			guild_id,
			category_id,
			channel_name,
			channel_type,
			position,
			topic
		))
		# self.connection.commit()

	def new_guild(self, guild_id, guild_name, guild_icon_path) -> None:
		"""
		creates new guild in database
		if guild already exists, it will be updated
		"""
		asset_id = self.new_asset(guild_icon_path)
		self.cursor.execute('INSERT OR REPLACE INTO guilds (id, name, asset_id) VALUES (?, ?, ?)', (
			guild_id,
			guild_name,
			asset_id
		))
		# self.connection.commit()

	def new_category(self, category_id, guild_id, category_name, position) -> None:
		"""
		creates new category in database
		if category already exists, it will be updated
		"""
		self.cursor.execute('INSERT OR REPLACE INTO categories (id, guild_id, name, position) VALUES (?, ?, ?, ?)', (
			category_id,
			guild_id,
			category_name,
			position
		))
		# self.connection.commit()

	def new_message(self, message_id, guild_id, category_id, channel_id, message_type, message_timestamp, message_timestamp_edited, message_is_pinned, message_is_deleted, message_content, message_author_id) -> None:
		"""
		creates new message in database
		if message already exists, it will be updated
		"""
		self.cursor.execute('INSERT OR REPLACE INTO messages (id, guild_id, category_id, channel_id, type, timestamp, timestamp_edited, is_pinned, is_deleted, content, author_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', (
			message_id,
			guild_id,
			category_id,
			channel_id,
			message_type,
			message_timestamp,
			message_timestamp_edited,
			message_is_pinned,
			message_is_deleted,
			message_content,
			message_author_id
		))
		# self.connection.commit()

	def new_author(self, author_id, guild_id, author_name, author_discriminator, author_nickname, author_is_bot, author_avatar_url) -> None:
		"""
		creates new author in database
		if author already exists, it will be updated
		"""
		asset_id = self.new_asset(author_avatar_url)
		self.cursor.execute('INSERT OR REPLACE INTO authors (id, guild_id, name, discriminator, nickname, is_bot, asset_id) VALUES (?, ?, ?, ?, ?, ?, ?)', (
			author_id,
			guild_id,
			author_name,
			author_discriminator,
			author_nickname,
			author_is_bot,
			asset_id
		))
		# self.connection.commit()

	def new_emoji(self, emoji_id, emoji_name, emoji_url, emoji_is_animated, guild_id) -> None:
		"""
		creates new emoji in database
		if emoji already exists, it will be updated
		"""
		asset_id = self.new_asset(emoji_url)
		self.cursor.execute('INSERT OR REPLACE INTO emojis (id, guild_id, name, is_animated, asset_id) VALUES (?, ?, ?, ?, ?)', (
			emoji_id,
			guild_id,
			emoji_name,
			emoji_is_animated,
			asset_id
		))
		# self.connection.commit()

	def new_message_reaction(self, message_id, reaction_count, emoji_id, emoji_name, emoji_url, emoji_is_animated, guild_id) -> None:
		"""
		creates new message reaction in database
		if message reaction already exists, it will be updated
		"""
		if emoji_id == "":
			emoji_id = emoji_name

		self.new_emoji(emoji_id, emoji_name, emoji_url, emoji_is_animated, guild_id)
		self.cursor.execute('INSERT OR REPLACE INTO messages_emojis (message_id, emoji_id, count) VALUES (?, ?, ?)', (
			message_id,
			emoji_id,
			reaction_count
		))
		# self.connection.commit()

	def new_message_attachment(self, message_id, attachment_url, attachment_size):
		"""
		creates new message attachment in database
		if message attachment already exists, it will be updated
		"""
		asset_id = self.new_asset(attachment_url)
		self.cursor.execute('INSERT OR REPLACE INTO messages_attachments (message_id, asset_id) VALUES (?, ?)', (
			message_id,
			asset_id
		))
		# self.connection.commit()


	# def create_table(self, table_name, columns):
	# 	self.cursor.execute("CREATE TABLE IF NOT EXISTS {}({})".format(table_name, columns))
	# 	self.db.commit()

	# def insert(self, table_name, columns, values):
	# 	self.cursor.execute("INSERT INTO {}({}) VALUES({})".format(table_name, columns, values))
	# 	self.db.commit()

	# def select(self, table_name, columns, condition):
	# 	self.cursor.execute("SELECT {} FROM {} WHERE {}".format(columns, table_name, condition))
	# 	return self.cursor.fetchall()

	# def update(self, table_name, columns, values, condition):
	# 	self.cursor.execute("UPDATE {} SET {}={} WHERE {}".format(table_name, columns, values, condition))
	# 	self.db.commit()

	# def delete(self, table_name, condition):
	# 	self.cursor.execute("DELETE FROM {} WHERE {}".format(table_name, condition))
	# 	self.db.commit()


import os
import sys
import requests
import functools

from pprint import pprint

from FileFinder import FileFinder
from MongoDatabase import MongoDatabase
from ChannelCache import ChannelCache
from AssetProcessor import AssetProcessor
from JsonProcessor import JsonProcessor
from Downloader import download_gg

# fix PIPE encoding error on Windows, auto flush print
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')
print = functools.partial(print, flush=True)


def wipe_database(database):
	"""
	Deletes all collections on version bump (on program update)
	Change EXPECTED_VERSION to force wipe on incompatible schema changes
	"""
	EXPECTED_VERSION = 4    # <---- change this to wipe database
	config = database.get_collection("config")

	version = config.find_one({"key": "version"})
	if version is None:
		version = {"key": "version", "value": 0}
		config.insert_one(version)

	if version["value"] == EXPECTED_VERSION:
		print("Database schema up to date, no wipe needed")
		return

	print("Wiping database...")
	database.clear_database_except_assets()
	database.clear_assets()
	print("Done wiping database")

	version["value"] = EXPECTED_VERSION
	config.update_one({"key": "version"}, {"$set": version})


def main(input_dir, output_dir):
	print("main_mongo loaded")

	database = MongoDatabase()
	wipe_database(database)

	# DEBUG clear database
	# database.clear_database_except_assets()
	# database.clear_assets()

	file_finder = FileFinder(input_dir)

	jsons = file_finder.find_channel_exports()
	print("found " + str(len(jsons)) + " json channel exports")

	channel_cache = ChannelCache()
	channel_cache.invalidate_all()
	asset_processor = AssetProcessor(file_finder, database)
	asset_processor.set_fast_mode(True)  # don't process slow actions

	for json_path in jsons:
		p = JsonProcessor(database, file_finder, json_path, asset_processor)
		p.process()

	download_gg(output_dir)

	print("done")



if __name__ == "__main__":
	input_dir = sys.argv[1]
	output_dir = sys.argv[2]
	main(input_dir, output_dir)


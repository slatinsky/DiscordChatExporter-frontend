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
from Timer import Timer

# fix PIPE encoding error on Windows, auto flush print
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')
print = functools.partial(print, flush=True)


def wipe_database(database):
	"""
	Deletes all collections on version bump (on program update)
	Change EXPECTED_VERSION to force wipe on incompatible schema changes
	"""
	EXPECTED_VERSION = 12    # <---- change this to wipe database
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

def remove_processed_jsons(database, jsons):
	"""
	removes jsons from the list that are already processed
	"""
	database_jsons = database.get_collection("jsons").find()
	for database_json in database_jsons:
		json_path = database_json["_id"]
		if json_path in jsons:
			jsons.remove(json_path)

	# TODO: add these checks back (date modified, file size, file hash)
	# if json == None:
	# 	# file not found in database, it is new file
	# 	return False

	# # do quick checks first (date modified, file size), because hashing is slow

	# date_modified = os.path.getmtime(json_path_with_base_dir)
	# if json["date_modified"] == date_modified:
	# 	# if time modified is the same, file was not modified
	# 	return True

	# file_size = os.path.getsize(json_path_with_base_dir)
	# if json["size"] == file_size:
	# 	# file size is the same, file was not modified
	# 	return True

	# # slow check - file hash
	# file_hash = hashlib.sha256()
	# with open(json_path_with_base_dir, "rb") as f:
	# 	for byte_block in iter(lambda: f.read(4096), b""):
	# 		file_hash.update(byte_block)
	# hex_hash = file_hash.hexdigest()

	# if json["sha256_hash"] == hex_hash:
	# 	# file hash is the same, file was not modified
	# 	return True

	return jsons


def main(input_dir, output_dir):
	print("main_mongo loaded")

	database = MongoDatabase()
	wipe_database(database)

	# DEBUG clear database
	# database.clear_database_except_assets()
	# database.clear_assets()


	file_finder = FileFinder(input_dir)

	jsons = file_finder.find_channel_exports()
	jsons_count_before = len(jsons)
	jsons = remove_processed_jsons(database, jsons)
	jsons_count = len(jsons)
	print("    found " + str(jsons_count) + " new possible json channel exports")
	print("    found " + str(jsons_count_before - jsons_count) + " already processed json channel exports")

	channel_cache = ChannelCache()
	channel_cache.invalidate_all()
	asset_processor = AssetProcessor(file_finder, database)
	asset_processor.set_fast_mode(True)  # don't process slow actions


	for index, json_path in enumerate(jsons):
		p = JsonProcessor(database, file_finder, json_path, asset_processor, index, jsons_count)
		p.process()

	download_gg(output_dir)

	# if user browses exports before they are processed, cached channels may be invalid again
	# so we need to invalidate cache again
	channel_cache = ChannelCache()

	print("preprocess done")



if __name__ == "__main__":
	input_dir = sys.argv[1]
	output_dir = sys.argv[2]
	with Timer("Preprocess"):
		main(input_dir, output_dir)


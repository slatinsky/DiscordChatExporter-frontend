import os
import sys
import functools

from FileFinder import FileFinder
from MongoDatabase import MongoDatabase
from AssetProcessor import AssetProcessor
from JsonProcessor import JsonProcessor
from Timer import Timer
from Eta import Eta
from Formatters import Formatters

# fix PIPE encoding error on Windows, auto flush print
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')
print = functools.partial(print, flush=True)

def rename_config_key(config, old_key: str, new_key: str):
	"""
	Renames config key in config collection
	"""
	old_config = config.find_one({"key": old_key})
	if old_config is None:
		return
	old_config["key"] = new_key
	config.update_one({"key": old_key}, {"$set": old_config})
	print(f"Renamed config key {old_key} --> {new_key}")


def wipe_database(database: MongoDatabase):
	"""
	Deletes all collections on version bump (on program update)
	Change EXPECTED_VERSION to force wipe on incompatible schema changes
	"""
	EXPECTED_VERSION = 16    # <---- change this to wipe database

	# ---- DEBUG force wipe ----
	# import random
	# EXPECTED_VERSION = random.randint(0, 1000)
	# --------------------------


	config = database.get_collection("config")

	# migrate config keys to new names
	rename_config_key(config, "whitelisted_guild_ids", "allowlisted_guild_ids")
	rename_config_key(config, "blacklisted_user_ids", "denylisted_user_ids")

	# add empty allowlisted_guild_ids config if it does not exist
	allowlisted_guild_ids = config.find_one({"key": "allowlisted_guild_ids"})
	if allowlisted_guild_ids is None:
		config.insert_one({"key": "allowlisted_guild_ids", "value": []})

	denylisted_user_ids = config.find_one({"key": "denylisted_user_ids"})
	if denylisted_user_ids is None:
		config.insert_one({"key": "denylisted_user_ids", "value": []})

	version = config.find_one({"key": "version"})
	if version is None:
		version = {"key": "version", "value": 0}
		config.insert_one(version)

	if version["value"] == EXPECTED_VERSION:
		print("Database schema up to date, no wipe needed")
		return

	guild_ids = database.get_collection("guilds").find({}, {"_id": 1})
	guild_ids = [guild["_id"] for guild in guild_ids]

	print("Wiping old database...")
	database.clear_database(guild_ids)
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

	return jsons


def main(input_dir):
	print("main_mongo loaded")

	database = MongoDatabase()
	wipe_database(database)

	file_finder = FileFinder(input_dir)

	jsons = file_finder.find_channel_exports()
	jsons_count_before = len(jsons)
	jsons = remove_processed_jsons(database, jsons)
	jsons_count = len(jsons)
	jsons_size = 0
	invalid_jsons = []
	for json_path in jsons:
		try:
			jsons_size += os.path.getsize(file_finder.add_base_directory(json_path))
		except FileNotFoundError:
			print(f"Warning: file not found '{json_path}', DID YOU APPLY THE REGISTRY TWEAK AND RESTART to allow paths longer than 260 characters?")
			invalid_jsons.append(json_path)

	for invalid_json in invalid_jsons:
		jsons.remove(invalid_json)

	print(f"    found {jsons_count} new possible json channel exports")
	print(f"    found {jsons_count_before - jsons_count} already processed json channel exports")
	print(f"    {Formatters.human_file_size(jsons_size)} is total size of new json exports")

	asset_processor = AssetProcessor(file_finder, database)
	asset_processor.set_fast_mode(True)  # don't process slow actions

	processed_bytes = 0
	with Eta(jsons_size, jsons_count) as eta:
		for index, json_path in enumerate(jsons):
			size = os.path.getsize(file_finder.add_base_directory(json_path))
			processed_bytes += size
			print(f"ETA {eta.calculate_eta().ljust(8)}  {(str(index + 1) + '/' + str(jsons_count)).ljust(9)} ({(str(round(processed_bytes / jsons_size * 100, 2)) + '%)').ljust(7)}  processing {json_path}")

			p = JsonProcessor(database, file_finder, json_path, asset_processor, index, jsons_count)
			p.process()
			eta.increment(size)

	print("preprocess done")


def print_help():
	print("Usage: python main.py <docker|windows>")

if __name__ == "__main__":
	if len(sys.argv) != 2:
		print_help()
		sys.exit(1)

	if sys.argv[1] == "windows":
		input_dir = "../../../exports/"
	elif sys.argv[1] == "docker":
		input_dir = "/dcef/exports/"
	else:
		print_help()
		sys.exit(1)

	with Timer("Preprocess"):
		main(input_dir)


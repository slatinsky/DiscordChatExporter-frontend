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



def main(input_dir, output_dir):
	print("main_mongo loaded")

	database = MongoDatabase()
	# DEBUG clear database
	# database.clear_database_except_assets()
	# database.clear_assets()

	file_finder = FileFinder(input_dir)

	jsons = file_finder.find_channel_exports()
	print("found " + str(len(jsons)) + " json channel exports")

	channel_cache = ChannelCache(database)
	asset_processor = AssetProcessor(file_finder, database)
	asset_processor.set_fast_mode(True)  # don't process slow actions

	for json_path in jsons:
		p = JsonProcessor(database, file_finder, json_path, asset_processor, channel_cache)
		p.process()

	download_gg(output_dir)

	print("done")



if __name__ == "__main__":
	input_dir = sys.argv[1]
	output_dir = sys.argv[2]
	main(input_dir, output_dir)


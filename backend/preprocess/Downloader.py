


import functools
import os

import requests

print = functools.partial(print, flush=True)



def download_gg(output_directory):
		"""
		download gg sans if not already downloaded
		we cannot directly include it, because it is not open source
		"""
		paths = {
			"ggsans-normal-400.woff2": "https://discord.com/assets/a798bb95e0f5a69c8ab85e53103ba6b2.woff2",
			"ggsans-italic-400.woff2": "https://discord.com/assets/8ca69301ef43643d9c7e14036f80061d.woff2",
			"ggsans-normal-500.woff2": "https://discord.com/assets/637ce9c046bf63b68fa35412518822d5.woff2",
			"ggsans-italic-500.woff2": "https://discord.com/assets/e8f55fa2303208454eaa0fbde8920d3f.woff2",
			"ggsans-normal-600.woff2": "https://discord.com/assets/4f2e4275143211c2492a31ca2c9669fb.woff2",
			"ggsans-italic-600.woff2": "https://discord.com/assets/fb1134f6438f4d0610260294891aa56e.woff2",
			"ggsans-normal-700.woff2": "https://discord.com/assets/bd88a0d8f72ec18529956748c2e00547.woff2",
			"ggsans-italic-700.woff2": "https://discord.com/assets/4893950fe590addffb6515237f1d1014.woff2",
			"ggsans-normal-800.woff2": "https://discord.com/assets/ec68b736b0006bb42d8a44528aafe796.woff2",
			"ggsans-italic-800.woff2": "https://discord.com/assets/ba1f0a8f593aa3c705d8de718f7c8d9a.woff2"
		}
		save_dir = os.path.join(output_directory, "fonts")
		if not os.path.exists(save_dir):
			os.makedirs(save_dir)

		for filename, url in paths.items():
			save_path = os.path.join(save_dir, filename)
			if not os.path.exists(save_path):
				print("   Downloading", filename)
				try:
					r = requests.get(url)
					with open(save_path, 'wb') as f:
						f.write(r.content)
				except:  # discord may change the url
					print("   Error downloading", filename)
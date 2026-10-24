"""
Downloads the third-party Windows binaries bundled with DCEF (MongoDB server, nginx) from their
official sites, verifies them against the pinned SHA-256 checksums below and puts them where
RUN_DEV.bat and BUILD_RELEASE.bat expect them.
Also copies the Microsoft Visual C++ runtime DLLs that mongod.exe needs next to it.

To update a binary, change its url, sha256 and member below.
Downloads are skipped if the pinned version is already in place.
"""
import functools
import hashlib
import mmap
import os
import shutil
import struct
import subprocess
import sys
import urllib.request
import zipfile
from pathlib import Path

print = functools.partial(print, flush=True)

BINARIES = [
	{
		"name": "MongoDB server",
		"url": "https://fastdl.mongodb.org/windows/mongodb-windows-x86_64-9.0.4.zip",
		# published by MongoDB as <url>.sha256 and in https://downloads.mongodb.org/full.json
		"sha256": "1e6234c8c33e75de3659a7e1104cb12f1cb68ae41cba60b625537c1ed9256d43",
		"member": "mongodb-win32-x86_64-windows-9.0.4/bin/mongod.exe",
		"dest": "dcef/backend/mongodb/dcefmongod.exe",
	},
	{
		"name": "nginx",
		"url": "https://nginx.org/download/nginx-1.30.6.zip",
		# nginx.org publishes only PGP signatures (<url>.asc) - this is the hash of the zip verified against its signature
		"sha256": "c6ee35edb0a861063323f709192ae50d1eefaf2ea7d00678bd2b22d8542dc61e",
		"member": "nginx-1.30.6/nginx.exe",
		"dest": "dcef/backend/nginx/dcefnginx.exe",
	},
]

DOWNLOAD_DIR = Path("_temp/downloads")


def download(url: str, path: Path, expected_sha256: str):
	"""
	downloads url to path, fails if the checksum doesn't match
	"""
	partial_path = path.with_name(path.name + ".partial")
	sha256 = hashlib.sha256()
	with urllib.request.urlopen(url, timeout=60) as response, open(partial_path, "wb") as f:
		total_size = int(response.headers.get("Content-Length", 0))
		downloaded_size = 0
		last_reported_percent = -10
		while chunk := response.read(1024 * 1024):
			f.write(chunk)
			sha256.update(chunk)
			downloaded_size += len(chunk)
			percent = downloaded_size * 100 // total_size if total_size else 0
			if percent >= last_reported_percent + 10:
				print(f"    {percent}% of {total_size // (1024 * 1024)} MB")
				last_reported_percent = percent

	if sha256.hexdigest() != expected_sha256:
		partial_path.unlink()
		raise SystemExit(f"ERROR: checksum mismatch for {url}\n    expected {expected_sha256}\n    got      {sha256.hexdigest()}")
	partial_path.replace(path)


def fetch(binary: dict):
	dest = Path(binary["dest"])
	stamp_path = DOWNLOAD_DIR / (dest.name + ".sha256")  # checksum of the archive dest was extracted from
	if dest.exists() and stamp_path.exists() and stamp_path.read_text().strip() == binary["sha256"]:
		print(f"{binary['name']}: up to date ({dest})")
		return

	archive_path = DOWNLOAD_DIR / binary["url"].rsplit("/", 1)[-1]
	print(f"{binary['name']}: downloading {binary['url']}")
	download(binary["url"], archive_path, binary["sha256"])

	print(f"{binary['name']}: extracting {binary['member']} to {dest}")
	dest.parent.mkdir(parents=True, exist_ok=True)
	partial_dest = dest.with_name(dest.name + ".partial")
	with zipfile.ZipFile(archive_path) as archive, archive.open(binary["member"]) as src, open(partial_dest, "wb") as dst:
		shutil.copyfileobj(src, dst, 1024 * 1024)
	partial_dest.replace(dest)
	stamp_path.write_text(binary["sha256"])
	archive_path.unlink()  # the MongoDB archive is ~1 GB, the stamp file is enough to skip the next download


def imported_dlls(exe_path: Path) -> list[str]:
	"""
	returns names of the DLLs in the import table of a 64-bit Windows executable
	"""
	with open(exe_path, "rb") as f, mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as pe:
		pe_header = struct.unpack_from("<I", pe, 0x3C)[0]
		section_count, optional_header_size = struct.unpack_from("<2xH12xH", pe, pe_header + 4)
		optional_header = pe_header + 24
		if struct.unpack_from("<H", pe, optional_header)[0] != 0x20B:
			raise SystemExit(f"ERROR: {exe_path} is not a 64-bit executable")
		import_table_rva = struct.unpack_from("<I", pe, optional_header + 120)[0]  # data directory 1

		sections = [struct.unpack_from("<8xIIII", pe, optional_header + optional_header_size + i * 40) for i in range(section_count)]
		def rva_to_offset(rva):
			for virtual_size, virtual_address, raw_size, raw_offset in sections:
				if virtual_address <= rva < virtual_address + max(virtual_size, raw_size):
					return rva - virtual_address + raw_offset
			raise SystemExit(f"ERROR: can't read the import table of {exe_path}")

		dlls = []
		descriptor = rva_to_offset(import_table_rva)
		while name_rva := struct.unpack_from("<I", pe, descriptor + 12)[0]:
			name_offset = rva_to_offset(name_rva)
			dlls.append(pe[name_offset:pe.find(b"\0", name_offset)].decode("ascii"))
			descriptor += 20
		return dlls


def vc_runtime_dirs():
	"""
	yields folders with Microsoft's redistributable Visual C++ runtime DLLs, best first
	"""
	# Visual Studio / Build Tools (preinstalled on GitHub's Windows runners), newest version first
	vswhere = Path(os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)"), "Microsoft Visual Studio", "Installer", "vswhere.exe")
	if vswhere.exists():
		installations = subprocess.run([vswhere, "-products", "*", "-property", "installationPath"], capture_output=True, text=True).stdout.splitlines()
		redist_dirs = [d for installation in installations if installation.strip() for d in Path(installation.strip()).glob("VC/Redist/MSVC/*/x64/Microsoft.VC14*.CRT")]
		yield from sorted(redist_dirs, key=lambda d: [int(part) for part in d.parents[1].name.split(".") if part.isdigit()], reverse=True)

	# Visual C++ Redistributable installed on this computer
	yield Path(os.environ.get("SystemRoot", r"C:\Windows"), "System32")


def copy_vc_runtime(mongod_path: Path):
	"""
	mongod.exe needs the Visual C++ runtime, copy it next to mongod.exe so the app works without installing it
	"""
	dll_names = [dll.lower() for dll in imported_dlls(mongod_path) if dll.lower().startswith(("msvcp", "vcruntime", "concrt"))]
	for runtime_dir in vc_runtime_dirs():
		if all((runtime_dir / dll).exists() for dll in dll_names):
			for dll in dll_names:
				shutil.copy2(runtime_dir / dll, mongod_path.parent / dll)
			print(f"Visual C++ runtime: copied {', '.join(dll_names)} from {runtime_dir}")
			return
	raise SystemExit(f"ERROR: Visual C++ runtime DLLs {', '.join(dll_names)} not found.\n"
	                 "    Install Visual Studio Build Tools (with the C++ workload) or the Visual C++ Redistributable from https://aka.ms/vs/17/release/vc_redist.x64.exe")


def main():
	os.chdir(Path(__file__).parent)  # paths are relative to the src/ folder
	DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)
	for binary in BINARIES:
		fetch(binary)

	if sys.platform == "win32":
		copy_vc_runtime(Path(BINARIES[0]["dest"]))
	else:
		print("Visual C++ runtime: skipped, not running on Windows")


if __name__ == "__main__":
	main()

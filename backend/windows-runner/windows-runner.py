import ctypes
import os
import signal
import sys
import time
import webview
import subprocess
import atexit
import threading


def is_compiled():
    if os.path.exists(__file__):
        return False
    else:
        return True

is_compiled = is_compiled()
processes = []
terminating_now = False

if is_compiled:
	BASE_DIR = os.path.realpath(os.path.dirname(sys.executable))
else:
	BASE_DIR = os.path.realpath(os.path.dirname(__file__) + '/../../release')

LOG_FILE = BASE_DIR + '/dcef/logs.txt'
if os.path.exists(LOG_FILE):
	os.remove(LOG_FILE)

def custom_print(source, *args, **kwargs):

	str_args = [str(arg) for arg in args]

	log_message = source.ljust(15) + ' '.join(str_args)
	if 'end' in kwargs and kwargs['end'] == '':
		log_message = log_message[:-1]

	print(log_message)

	# log to file
	with open(LOG_FILE, 'a') as f:
		f.write(log_message + '\n')

def cleanup():
	global terminating_now
	if not terminating_now:  # Prevents cleanup from being called twice
		terminating_now = True
		custom_print("windows-runner:", "cleaning up")
		for process in processes:
			custom_print("windows-runner:", "killing process", process.pid)
			try:
				os.kill(process.pid, signal.CTRL_C_EVENT)
			except Exception as e:
				custom_print("windows-runner:", "error killing process", process.pid, e)


def create_window():
	custom_print("windows-runner:", "creating window")
	window = webview.create_window('DiscordChatExported-frontend','http://127.0.0.1:21011/',
		width=1280,
		height=720,
		background_color='#36393F',
		text_select=True,
		zoomable=True,
		draggable=True,
	)
	webview.start(debug=False, storage_path=BASE_DIR + '/dcef/storage', private_mode=False)
	custom_print("windows-runner:", "window closed")

def create_dir_if_not_exists(path):
	if not os.path.exists(path):
		os.makedirs(path)

def runner(name, args, cwd):
	custom_print("windows-runner:", name + " started")

	process = subprocess.Popen(args, shell=True, stdout=subprocess.PIPE, bufsize=1, universal_newlines=True, cwd=cwd, stderr=subprocess.STDOUT)
	processes.append(process)
	try:
		for line in process.stdout:
			custom_print(name + ':', line, end='') # process line here

	except Exception as e:
		custom_print("windows-runner:", 'error in ' + name + ' thread')

	custom_print("windows-runner:", name + ' finished')

def start_preprocess():
	cwd = os.path.realpath(BASE_DIR + '/dcef/backend/preprocess')
	args = ['preprocess.exe', '../../../exports/', 'temp/']
	th = threading.Thread(target=runner, args=('preprocess', args, cwd), daemon=False)
	th.start()
	return th

def start_http_server():
	cwd = os.path.realpath(BASE_DIR + '/dcef/backend/http-server')
	args = ['http-server.exe', '../../../exports', '--port', '21013', '-c-1', '--silent', '-P', 'http://127.0.0.1:21013?']
	th = threading.Thread(target=runner, args=('http-server', args, cwd), daemon=False)
	th.start()
	return th

def start_mongodb():
	create_dir_if_not_exists(BASE_DIR + '/dcef/backend/mongodb/db')

	cwd = os.path.realpath(BASE_DIR + '/dcef/backend/mongodb')
	args = ['mongod.exe', '--dbpath', 'db']
	th = threading.Thread(target=runner, args=('mongodb', args, cwd), daemon=False)
	th.start()
	return th

def start_fastapi():
	cwd = os.path.realpath(BASE_DIR + '/dcef/backend/fastapi')
	args = ['fastapi.exe']
	th = threading.Thread(target=runner, args=('fastapi', args, cwd), daemon=False)
	th.start()
	return th

def start_nginx():
	create_dir_if_not_exists(BASE_DIR + '/dcef/backend/nginx/logs')
	create_dir_if_not_exists(BASE_DIR + '/dcef/backend/nginx/temp')
	cwd = os.path.realpath(BASE_DIR + '/dcef/backend/nginx')
	args = ['nginx.exe', '-c', 'conf/nginx-prod.conf']
	th = threading.Thread(target=runner, args=('nginx', args, cwd), daemon=False)
	th.start()
	return th

def hide_console():
	# https://github.com/pyinstaller/pyinstaller/issues/1339#issuecomment-122909830
	if is_compiled:
		whnd = ctypes.windll.kernel32.GetConsoleWindow()
		if whnd != 0:
			ctypes.windll.user32.ShowWindow(whnd, 0)

def show_console():
	if is_compiled:
		whnd = ctypes.windll.kernel32.GetConsoleWindow()
		if whnd != 0:
			ctypes.windll.user32.ShowWindow(whnd, 1)




def main():
	custom_print("windows-runner:", "started")
	atexit.register(cleanup)
	th_nginx = start_nginx()
	time.sleep(1)
	th_mongodb = start_mongodb()
	th_http_server = start_http_server()
	th_fastapi = start_fastapi()
	th_preprocess = start_preprocess()


	th_preprocess.join()  # Wait for preprocess to finish
	hide_console()
	create_window()
	show_console()
	custom_print("windows-runner:", "finished")
	cleanup()


if __name__ == '__main__':
	main()
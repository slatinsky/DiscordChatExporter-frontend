import ctypes
import os
import signal
import sys
import time
import webview
import subprocess
import atexit
import threading

# https://stackoverflow.com/a/65501621
from win32event import CreateMutex
from win32api import CloseHandle, GetLastError
from winerror import ERROR_ALREADY_EXISTS
class SingleInstance:
	""" Limits application to single instance """

	def __init__(self):
		self.mutexname = "dcef-qwertyuiopasdfghjklzxcvbnm1234567890"
		self.mutex = CreateMutex(None, False, self.mutexname)
		self.lasterror = GetLastError()

	def is_secondary_instance(self):
		return (self.lasterror == ERROR_ALREADY_EXISTS)

	def is_primary_instance(self):
		return not self.is_secondary_instance()

	def __del__(self):
		if self.mutex:
			CloseHandle(self.mutex)




def is_compiled():
	if os.path.exists(__file__):
		return False
	else:
		return True




def custom_print(source, *args, **kwargs):

	str_args = [str(arg) for arg in args]

	log_message = source.ljust(16) + ' '.join(str_args)
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

		# kill other instances of dcef.exe except this one
		if is_compiled() and myapp.is_primary_instance():
			custom_print("windows-runner:", "killing other instances of dcef.exe except primary with PID " +  str(os.getpid()))
			os.system('taskkill /f /im dcef.exe /fi "PID ne ' + str(os.getpid()) + '"')

		custom_print("windows-runner:", "cleaning up")
		for process in processes:
			custom_print("windows-runner:", "killing process", process.pid)
			try:
				os.kill(process.pid, signal.CTRL_C_EVENT)
			except Exception as e:
				custom_print("windows-runner:", "error killing process", process.pid, e)



def create_window():
	custom_print("windows-runner:", "creating window")
	title = 'DiscordChatExported-frontend'
	if myapp.is_secondary_instance():
		title += ' (secondary instance)'
	window = webview.create_window(title, 'http://127.0.0.1:21011/',
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
	args = ['cmd.exe', '/u','/c', 'cd', cwd, '&&'] + args
	process = subprocess.Popen(args, stdout=subprocess.PIPE, bufsize=1, cwd=cwd, stderr=subprocess.STDOUT, encoding='utf-8')
	processes.append(process)

	for byte_line in iter(process.stdout.readline, ''):
		try:
			custom_print(name + ':', byte_line, end='') # process line here
		except Exception as e:
			# it looks like the message is printed even if the exception is raised. So we can ignore it
			pass

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
	if is_compiled():
		whnd = ctypes.windll.kernel32.GetConsoleWindow()
		if whnd != 0:
			ctypes.windll.user32.ShowWindow(whnd, 0)

def show_console():
	if is_compiled():
		whnd = ctypes.windll.kernel32.GetConsoleWindow()
		if whnd != 0:
			ctypes.windll.user32.ShowWindow(whnd, 1)




def main():
	if myapp.is_secondary_instance():
		# second instance just needs to open another window, the backend services are already running
		custom_print("windows-runner:", "started secondary instance")
		hide_console()
		create_window()
		show_console()
		custom_print("windows-runner:", "finished secondary instance")

	else:
		if os.path.exists(LOG_FILE):
			os.remove(LOG_FILE)

		custom_print("windows-runner:", "started primary instance")
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

		custom_print("windows-runner:", "finished primary instance")
		cleanup()



myapp = SingleInstance()
processes = []
terminating_now = False

if is_compiled():
	BASE_DIR = os.path.realpath(os.path.dirname(sys.executable))
else:
	BASE_DIR = os.path.realpath(os.path.dirname(__file__) + '/../../release')

LOG_FILE = BASE_DIR + '/dcef/logs.txt'

if __name__ == '__main__':
	main()
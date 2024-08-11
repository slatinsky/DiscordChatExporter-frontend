import ctypes
from datetime import datetime
import os
import shutil
import signal
import sys
import time
import webview
import subprocess
import atexit
import threading
import psutil


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
		return self.lasterror == ERROR_ALREADY_EXISTS

	def is_primary_instance(self):
		return not self.lasterror == ERROR_ALREADY_EXISTS

	def __del__(self):
		if self.mutex:
			CloseHandle(self.mutex)




def is_compiled():
	if os.path.exists(__file__):
		return False
	else:
		return True

def kill_dcef_processes():
	dcef_process_names = ['dceffastapi.exe', 'dcefnginx.exe', 'dcefmongod.exe', 'dcefpreprocess.exe']
	for process in psutil.process_iter(['pid', 'name']):
		if process.info['name'] in dcef_process_names:
			custom_print("windows-runner:", "killing process", process.info['pid'])
			try:
				process.kill()
			except Exception as e:
				custom_print("windows-runner:", "error killing process", process.info['pid'], e)


def custom_print(source, *args, **kwargs):

	str_args = [str(arg) for arg in args]

	datetime_obj = datetime.now()

	log_message = str(datetime_obj) + "  " + source.ljust(16) + ' '.join(str_args)
	if 'end' in kwargs and kwargs['end'] == '':
		log_message = log_message[:-1]

	blacklist = ["Slow SessionWorkflow loop", "Slow query"]  # this just spams the logs and is not useful
	if any([blacklisted in log_message for blacklisted in blacklist]):
		return

	print(log_message)

	# log to file
	with open(LOG_FILE, 'a') as f:
		f.write(log_message + '\n')


def check_used_ports():
	connections = psutil.net_connections()
	used_ports = set()

	for connection in connections:
		if connection.status == 'LISTEN':
			used_ports.add(connection.laddr.port)

	used_ports_list = list(used_ports)
	used_ports_list.sort()

	custom_print("windows-runner:", 'used ports:', " ".join([str(port) for port in used_ports_list]))

	required_port_is_used = False

	if 21011 in used_ports:
		custom_print("windows-runner:", 'WARNING: Needed port 21011 is already in use. This port is required by nginx')
		required_port_is_used = True

	if 27017 in used_ports:
		custom_print("windows-runner:", 'WARNING: Needed port 27017 is already in use. This port is required by mongodb.')
		required_port_is_used = True

	if 58000 in used_ports:
		custom_print("windows-runner:", 'WARNING: Needed port 58000 is already in use. This port is required by fastapi')
		required_port_is_used = True

	if required_port_is_used:
		custom_print("windows-runner:", '##########################################################################################')
		custom_print("windows-runner:", '# WARNING: THE PROGRAM MAY NOT WORK PROPERLY, BECAUSE REQUIRED PORTS ARE ALREADY IN USE! #')
		custom_print("windows-runner:", '##########################################################################################')
		time.sleep(5)
	else:
		custom_print("windows-runner:", 'OK: All required ports are available.')


def cleanup():
	global terminating_now
	if not terminating_now:  # Prevents cleanup from being called twice
		terminating_now = True

		kill_dcef_processes()

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

		# delete temp folder with its contents
		temp_folder = BASE_DIR + '/temp'
		if os.path.exists(temp_folder):
			shutil.rmtree(temp_folder)



def create_window():
	custom_print("windows-runner:", "creating window")
	title = 'DiscordChatExporter-frontend'
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
	args = ['dcefpreprocess.exe']
	th = threading.Thread(target=runner, args=('preprocess', args, cwd), daemon=False)
	th.start()
	return th

def start_mongodb():
	create_dir_if_not_exists(BASE_DIR + '/_temp/mongodb')

	cwd = os.path.realpath(BASE_DIR + '/dcef/backend/mongodb')
	args = ['dcefmongod.exe', '--dbpath', "../../../_temp/mongodb"]
	th = threading.Thread(target=runner, args=('mongodb', args, cwd), daemon=False)
	th.start()
	return th

def start_fastapi():
	cwd = os.path.realpath(BASE_DIR + '/dcef/backend/fastapi')
	args = ['dceffastapi.exe']
	th = threading.Thread(target=runner, args=('fastapi', args, cwd), daemon=False)
	th.start()
	return th

def start_nginx():
	create_dir_if_not_exists(BASE_DIR + '/logs')
	create_dir_if_not_exists(BASE_DIR + '/temp')
	cwd = os.path.realpath(BASE_DIR)
	args = ['dcef\\backend\\nginx\\dcefnginx.exe', '-c', 'dcef/backend/nginx/conf/nginx-prod.conf']
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
		kill_dcef_processes()  # kill any running instances of dcef processes before starting new ones
		create_dir_if_not_exists(BASE_DIR + '/logs')
		if os.path.exists(LOG_FILE):
			os.remove(LOG_FILE)

		custom_print("windows-runner:", "started primary instance")
		check_used_ports()
		atexit.register(cleanup)
		th_nginx = start_nginx()
		time.sleep(1)
		th_mongodb = start_mongodb()
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
	print("DON'T RUN THIS SCRIPT DIRECTLY. RUN compiled dcef.exe in release folder instead.")
	sys.exit(1)

LOG_FILE = BASE_DIR + '/logs/dcef.log'

if __name__ == '__main__':
	main()
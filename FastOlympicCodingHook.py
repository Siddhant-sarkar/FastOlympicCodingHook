import sublime
import sublime_plugin
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import re
import _thread
import threading
import platform
from os import path

def textSplitter(tosplit):
	pattern = r'<(?:[^>]+)>([^<]+)<'
	matches = re.findall(pattern,tosplit)
	rt  = ""
	for match in matches:
		rt= rt+match+"\n"
	print("here is rt " , rt);
	return rt	



def MakeHandlerClassFromFilename(file_full_path, tests_relative_dir, tests_file_suffix):
	if not tests_file_suffix: tests_file_suffix = ":tests"

	class HandleRequests(BaseHTTPRequestHandler):
		def do_POST(self):
			try:
				content_length = int(self.headers['Content-Length'])
				body = self.rfile.read(content_length)
				tests = json.loads(body.decode('utf8'))
				link = tests['url'].split("/")
				# we declare the name
				n_file_name = ""
				if "contest" in link:
					n_file_name = link[len(link) - 3] + link[len(link) - 1]+".cpp"; 
				else:
					n_file_name = link[len(link) - 2] + link[len(link) - 1]+".cpp"; 
				print("n_file_name -> ",n_file_name)
				# we make a new 1883D.cpp file
				tests = tests["tests"]
				ntests = []
				for test in tests:
					ntest = {
						# "test": test["input"],
						"test": textSplitter(test["input"]),
						"correct_answers": [test["output"].strip()]
					}
					ntests.append(ntest)
				file_relative_dir = path.dirname(file_full_path)
				file_name = path.basename(file_full_path)
				nfilename = path.join(file_relative_dir, tests_relative_dir, n_file_name + tests_file_suffix) \
					if tests_relative_dir else path.join(file_relative_dir, n_file_name + tests_file_suffix)
				print("New test case path: " + nfilename)
				cpp_file_name = path.join(file_relative_dir,n_file_name)
				cpp_file_name_temp = cpp_file_name
				with open(nfilename, "w") as f:
					f.write(json.dumps(ntests))
				with open('/Users/siddhantsarkar/templateS.cpp','r') as firstfile, open(cpp_file_name,'w') as secondfile: 
					for line in firstfile: 
						secondfile.write(line)
			except Exception as e:
				print("Error handling POST - " + str(e))
	return HandleRequests

class CompetitiveCompanionServer:
	def startServer(file_full_path, foc_settings):
		host = 'localhost'
		port = 12345
		tests_relative_dir = foc_settings.get("tests_relative_dir")
		tests_file_suffix = foc_settings.get("tests_file_suffix")
		HandlerClass = MakeHandlerClassFromFilename(file_full_path, tests_relative_dir, tests_file_suffix)
		httpd = HTTPServer((host, port), HandlerClass)
		httpd.serve_forever()
		print("Server has been shutdown")


class FastOlympicCodingHookCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		try:
			cpp_file_name_temp = ""
			_thread.start_new_thread(CompetitiveCompanionServer.startServer,
									 (self.view.file_name(),
									  sublime.load_settings("FastOlympicCoding.sublime-settings")))
		except Exception as e:
			print("Error: unable to start thread - " + str(e))

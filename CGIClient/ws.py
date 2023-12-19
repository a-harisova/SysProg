import os, sys, threading, time
from http.server import HTTPServer, CGIHTTPRequestHandler

port = 8080
webdir = '.'

def main():
	os.chdir(webdir)

	HTTPServer(('', port), CGIHTTPRequestHandler).serve_forever()

try:
	main()
except:
	print("bye")
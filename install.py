from __future__ import print_function
import xml.etree.ElementTree as xml
from os.path import exists
from urllib2 import urlopen
from json import dumps
from sys import stdout

url = 'http://tolweb.org/onlinecontributors/app?service=external&page=xml/TreeStructureService&node_id=1'

def console(message, polling=False):
	message = '  ' + message
	if console.length > len(message):
		# Clear characters from previous line.
		message += ' ' * (console.length - len(message))
	if polling:
		# Print on the same line.
		print(message, end='\r')
		stdout.flush()
		console.length = len(message)
	else:
		# Print normal line.
		print(message)
		console.length = 0
console.length = 0

def sizeformat(num):
    for unit in ['B', 'KB', 'MB']:
        if (abs(num) < 1024.0) or (unit == 'MB'):
            return "%3.2f %s" % (num, unit)
        num /= 1024.0

def readfile(file, chunksize=10240):
	size = 0
	while True:
		chunk = file.read(chunksize)
		if chunk:
			size += len(chunk)
			console('Downloading %s' % sizeformat(size), polling=True)
			yield chunk
		else:
			break

name = 'tree.xml'
if not exists(name):
	console('Downloading %s' % name)
	response = urlopen(url)
	with open(name, 'w') as cache:
		for chunk in readfile(response):
			cache.write(chunk)
	response.close()

tree = xml.parse(name)
root = tree.getroot()

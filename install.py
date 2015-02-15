from __future__ import print_function
import xml.etree.ElementTree as xml
from os.path import exists
from urllib2 import urlopen
from shutil import move
from json import loads, dumps
from sys import stdout
from os import mkdir
import re

url = 'http://tolweb.org/onlinecontributors/app?service=external&page=xml/TreeStructureService&node_id=1'
reg = re.compile(r'javascript:popup_window(_[\d]+)?....><img( class="singletillus")? src="([^"]+)"')

scratch = 'scratch.dat'
cache   = 'tree.xml'
output  = 'tree.json'

tree = {}

def console(message, polling=False):
	message = '  ' + message
	if console.length > len(message):
		# Clear characters from previous line.
		message += ' ' * (console.length - len(message))
	if polling:
		# Print on the same line.
		print(message, end='\r')
		console.length = len(message)
	else:
		# Print normal line.
		print(message)
		console.length = 0
	stdout.flush()
console.length = 0

def size_format(num):
    for unit in ['B', 'KB', 'MB']:
        if (abs(num) < 1024.0) or (unit == 'MB'):
            return "%3.2f %s" % (num, unit)
        num /= 1024.0

def read_file(f, chunksize=10240):
	size = 0
	while True:
		chunk = f.read(chunksize)
		if chunk:
			size += len(chunk)
			console('Downloading %s' % size_format(size), polling=True)
			yield chunk
		else:
			break

def scan(branch, parent):
	tid = branch.attrib['ID']
	if branch.attrib['LEAF']:
		if branch.attrib['HASPAGE']:
			if not tid in tree:
				images = []
				request = urlopen('http://tolweb.org/%s' % tid)
				data = request.read()
				request.close()
				for match in reg.findall(data, re.MULTILINE):
					_, _, src = match
					image = src.split('/')[-1]
					images.append(image)
					if not exists('images/%s' % image):
						request = urlopen('http://tolweb.org%s' % src)
						with open(scratch, 'w') as f:
							f.write(request.read())
						request.close()
						move(scratch, 'images/%s' % image)
					scan.images += 1
				if images:
					names = [branch.find('NAME').text]
					if branch.find('OTHERNAMES') is not None:
						for n in branch.findall('OTHERNAMES/OTHERNAME/NAME'):
							names.append(n.text)
					species = {
						'parent': parent,
						'names': names,
						'images': images,
					}
					desc = branch.find('DESCRIPTION').text
					if desc:
						species['desc'] = desc
					if branch.attrib['EXTINCT']:
						species['extinct'] = True
					tree[tid] = species
	scan.nodes += 1
	console('Scanning %d nodes and %d images' % (scan.nodes, scan.images), polling=True)
	nodes = branch.findall('NODES/NODE')
	if nodes is not None:
		for node in nodes:
			scan(node, tid)
scan.nodes = 0
scan.images = 0

if not exists('images'):
	mkdir('images')

if not exists(cache):
	console('Downloading %s' % cache)
	response = urlopen(url)
	with open(scratch, 'w') as f:
		for chunk in read_file(response):
			f.write(chunk)
	move(scratch, cache)
	response.close()

if exists(output):
	console('Opening %s' % output)
	with open(output, 'r') as f:
		tree = loads(f.read())

console('Parsing %s' % cache)
root = xml.parse(cache).getroot()
try:
	scan(root.find('NODE'), 0)
except KeyboardInterrupt:
	pass
with open(output, 'w') as f:
	console('Saving %s' % output)
	f.write(dumps(tree))
console('Done!')

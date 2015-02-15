from __future__ import print_function
import xml.etree.ElementTree as xml
from HTMLParser import HTMLParser
from os.path import exists
from urllib2 import urlopen, quote, HTTPError
from shutil import move
from json import loads, dumps
from time import sleep
from sys import stdout
from os import mkdir
import re

xmlurl = 'http://tolweb.org/onlinecontributors/app?service=external&page=xml/TreeStructureService&node_id=1'
regex = re.compile(r'javascript:popup_window(_[\d]+)?....><img( class="singletillus")? src="([^"]+)"')

scratch = 'scratch.dat'
cache   = 'tree.xml'
output  = 'nodes.json'

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
			console('Downloading %s (%s)' % (cache, size_format(size)), polling=True)
			yield chunk
		else:
			break

def scan(branch, parent):
	scan.count += 1
	console('Scanning %s (%d)' % (cache, scan.count), polling=True)
	tid = int(branch.attrib['ID'])
	if tid not in scan.nodes:
		node = {
			'parent': parent,
			'names': [branch.find('NAME').text],
		}
		if branch.find('OTHERNAMES') is not None:
			for n in branch.findall('OTHERNAMES/OTHERNAME/NAME'):
				node['names'].append(n.text)
		desc = branch.find('DESCRIPTION').text
		if desc:
			node['desc'] = desc
		if int(branch.attrib['LEAF']):
			node['leaf'] = 1
		if int(branch.attrib['HASPAGE']):
			node['haspage'] = True
		if int(branch.attrib['EXTINCT']) == 2:
			node['extinct'] = 1
		scan.nodes[tid] = node
	children = branch.findall('NODES/NODE')
	if children is not None:
		for node in children:
			scan(node, tid)
scan.nodes = {}
scan.count = 0

# Create the images and nodes directories.
if not exists('images'):
	mkdir('images')
if not exists('nodes'):
	mkdir('nodes')

# Download and cache the XML file.
if not exists(cache):
	response = urlopen(xmlurl)
	with open(scratch, 'w') as f:
		for chunk in read_file(response):
			f.write(chunk)
	move(scratch, cache)
	response.close()
	console('Downloaded %s' % cache)

# Parse the XML file and output a JSON file containing all nodes.
if exists(output):
	with open(output, 'r') as f:
		scan.nodes = loads(f.read())
		scan.count = len(scan.nodes)
else:
	console('Parsing %s' % cache, polling=True)
	root = xml.parse(cache).getroot()
	console('Parsed %s' % cache)
	scan(root.find('NODE'), 0)
	console('Scanned %s (%d)' % (cache, scan.count))
	with open(output, 'w') as f:
		console('Saving %s' % output, polling=True)
		f.write(dumps(scan.nodes))
		console('Saved %s' % output)

# Visit pages to look up and download images.
abort = False
try:
	count = 0
	for tid, node in scan.nodes.iteritems():
		count += 1
		console('Loading pages (%d of %d)' % (count, scan.count), polling=True)
		if 'haspage' not in node:
			continue
		node['images'] = []
		request = urlopen('http://tolweb.org/%s' % tid)
		page = request.read()
		request.close()
		sleep(0.25)
		for match in regex.findall(page, re.MULTILINE):
			_, _, src = match
			src = HTMLParser().unescape(src).encode('utf8')
			image = src.split('/')[-1]
			node['images'].append(image)
			if not exists('images/%s' % image):
				request = urlopen('http://tolweb.org%s' % quote(src))
				with open(scratch, 'w') as f:
					f.write(request.read())
				request.close()
				sleep(0.25)
				move(scratch, 'images/%s' % image)
		del node['haspage']
		scan.nodes[tid] = node
	console('Loaded pages')
except KeyboardInterrupt:
	abort = True
finally:
	with open(output, 'w') as f:
		console('Saving %s' % output, polling=True)
		f.write(dumps(scan.nodes))
		console('Saved %s' % output)
if abort:
	exit()

# Write out individual node files.
count = 0
for tid, node in scan.nodes.iteritems():
	count += 1
	console('Saving node files (%d of %d)' % (count, scan.count), polling=True)
	name = 'nodes/%d.json' % tid
	if not exists(name):
		pid = node['parent']
		del node['parent']
		node['parents'] = []
		while pid > 0:
			parent = scan.nodes[pid]
			node['parents'].append(pid)
			pid = parent['parent']
		with open(name, 'w') as f:
			f.write(dumps(node))
console('Saved node files')

# Write out species files.
count = 0
species = []
for tid, node in scan.nodes.iteritems():
	count += 1
	console('Listing species (%d of %d)' % (count, scan.count), polling=True)
	if not (node['images'] and node['leaf']):
		continue # Only play game with leaf nodes having at least one image.
	species.append(tid)
with open('species.json', 'w') as f:
	console('Writing species.json', polling=True)
	f.write(species)
	console('Wrote species.json', polling=True)

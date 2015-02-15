from __future__ import print_function
import xml.etree.ElementTree as xml
from os.path import exists
from urllib2 import urlopen, HTTPError
from shutil import move
from json import loads, dumps
from time import sleep
from sys import stdout
from os import mkdir
import re

url = 'http://tolweb.org/onlinecontributors/app?service=external&page=xml/TreeStructureService&node_id=1'
reg = re.compile(r'javascript:popup_window(_[\d]+)?....><img( class="singletillus")? src="([^"]+)"')

scratch = 'scratch.dat'
cache   = 'tree.xml'
output  = 'data.json'

data = { 'parents': {}, 'leaves': {} }

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
	if int(branch.attrib['LEAF']) and int(branch.attrib['HASPAGE']):
		if tid not in data['leaves']:
			images = []
			request = urlopen('http://tolweb.org/%s' % tid)
			page = request.read()
			request.close()
			for match in reg.findall(page, re.MULTILINE):
				_, _, src = match
				image = src.split('/')[-1]
				images.append(image)
				if not exists('images/%s' % image):
					try:
						request = urlopen('http://tolweb.org%s' % src)
						with open(scratch, 'w') as f:
							f.write(request.read())
						request.close()
						sleep(0.25)
						move(scratch, 'images/%s' % image)
					except HTTPError as e:
						console(e)
						console('http://tolweb.org%s' % src)
					scan.images += 1
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
			if int(branch.attrib['EXTINCT']) == 2:
				species['extinct'] = True
			data['leaves'][tid] = species
		scan.leaves += 1
	if not tid in data['parents']:
		data['parents'][tid] = parent
	scan.parents += 1
	console('Scanning %d parents, %d leaves, and %d images' % (scan.parents, scan.leaves, scan.images), polling=True)
	nodes = branch.findall('NODES/NODE')
	if nodes is not None:
		for node in nodes:
			scan(node, tid)
scan.parents = 0
scan.leaves  = 0
scan.images  = 0

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
		data = loads(f.read())

console('Parsing %s' % cache)
root = xml.parse(cache).getroot()
message = 'Done!'
try:
	scan(root.find('NODE'), 0)
except KeyboardInterrupt:
	message = 'Aborted!'
	console('Aborting', polling=True)
with open(output, 'w') as f:
	console('Saving %s' % output)
	f.write(dumps(data))
console(message)

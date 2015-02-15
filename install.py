from __future__ import print_function
import xml.etree.ElementTree as xml
from os.path import exists
from urllib2 import urlopen
from json import loads, dumps
from sys import stdout
import re

url = 'http://tolweb.org/onlinecontributors/app?service=external&page=xml/TreeStructureService&node_id=1'
reg = re.compile(r'javascript:popup_window(_[\d]+)?....><img( class="singletillus")? src="([^"]+)"')

cache  = 'tree.xml'
output = 'tree.json'

tree = {}

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

def scan(branch, path):
	scan.count += 1
	console('Scanning %d' % scan.count)
	tid = int(branch.attrib['ID'])
	path.append(tid)
	if branch.attrib['LEAF']:
		if branch.attrib['HASPAGE']:
			key = '/'.join(path)
			if not key in tree:
				images = []
				request = urlopen('http://tolweb.org/%d' % bid)
				data = request.read()
				request.close()
				for match in reg.findall(data, re.MULTILINE)
					_, _, src = match
					image = '%d-%d.%s' % (tid, len(images) + 1, src.split('.')[-1])
					images.append(image)
					request = urlopen('http://tolweb.org%s' % src)
					with open('images/%s' % image, 'w') as f:
						f.write(request.read())
					request.close()
				if images:
					names = [branch.find('NAME').text]
					if branch.find('OTHERNAMES'):
						for n in branch.findall('OTHERNAMES/OTHERNAME/NAME'):
							names.append(n.text)
					species = {
						'names': names,
						'images': images,
					}
					desc = branch.find('DESCRIPTION').text
					if desc:
						species['desc'] = desc
					if branch.attrib['EXTINCT']:
						species['extinct'] = True
					tree[key] = species
	else:
		nodes = branch.findall('nodes')
		for node in nodes:
			scan(node, path)
scan.count = 0

if not exists(cache):
	console('Downloading %s' % cache)
	response = urlopen(url)
	with open(cache, 'w') as f:
		for chunk in read_file(response):
			f.write(chunk)
	response.close()

if exists(output):
	console('Opening ' % output)
	with open(output, 'r') as f:
		tree = loads(f)

console('Parsing %s' % cache)
root = xml.parse(cache).getroot()
scan(root.find('NODE'), [])
# TODO save species to file
console('Done!')

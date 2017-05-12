#!/usr/bin/python

import sys, os, datetime
import requests
from os import listdir
from os.path import isfile, join
from hachoir_core.error import HachoirError
from hachoir_core.cmd_line import unicodeFilename
from hachoir_parser import createParser
from hachoir_core.tools import makePrintable
from hachoir_metadata import extractMetadata
from hachoir_core.i18n import getTerminalCharset
from docx import *
from hachoir_core import config as HachoirConfig
import json
def parse_doc(path):
	document = Document(path)

	docText = '\n\n'.join([
	    paragraph.text.encode('utf-8') for paragraph in document.paragraphs
	])
	words = docText.split()
	metadata = {
		"table" : 'doc',
		"type" : 'docx',
		"word_count" : len(words),
		"char_count" : len(docText),
		"author" : document.core_properties.author,
		"created" : document.core_properties.created,
		"modified" : document.core_properties.modified
	}
	return metadata

def parse_image(path):
	metadata = metadata_for(path)
	meta = {
		"table" : "img",
		"type" : metadata['mime_type'],
		"height" : metadata['height'],
		'width' : metadata['width'],
	}
	return meta

def parse_vid(path):
	metadata = metadata_for(path)

	meta = {
		"table" : 'vid',
		"type" : metadata['mime_type'],
		"height" : metadata['height'],
		'width' : metadata['width'],
		"duration" : metadata['duration'],
	}
	if 'frame_rate' in metadata:
		meta['frame_rate'] = metadata['frame_rate']
	return meta

def parse_mp3(path):
	metadata = metadata_for(path)
	meta = {
		"table" : "audio",
		"title" : metadata['title'],
		"type" : metadata['mime_type'],
		"duration" : metadata['duration'],
	}
	if "album" in metadata:
		meta['album'] = metadata['album']
	else:
		meta['album'] = None
	if "author" in metadata:
		meta['composer'] = metadata['author']
	else:
		meta['composer'] = None
	if "track_number" in metadata:
		meta['track_num'] = metadata['track_number']
	else:
		meta['track_num'] = None
	if "music_genre" in metadata:
		meta['genre'] = metadata['music_genre']
	else:
		meta['genre'] = None
	return meta

def metadata_for(filename):

    filename, realname = unicodeFilename(filename), filename
    parser = createParser(filename, realname)
    if not parser:
        print "Unable to parse file"
        exit(1)
    try:
        metadata = extractMetadata(parser)
    except HachoirError, err:
        print "Metadata extraction error: %s" % unicode(err)
        metadata = None
    if not metadata:
        print "Unable to extract metadata"
        exit(1)

    meta = {}
    for k,v in extractMetadata(parser)._Metadata__data.iteritems():
        if v.values:
            meta[v.key] = v.values[0].value
    return meta

def file_metadata(directory, name, a_name, keywords):
	metadata = {}
	file_ext = directory.split('.')
	if len(file_ext) != 2:
		print "unsupported file extension"
		metadata = None
	else:
		file_ext = file_ext[1]
		if file_ext in FILE_EXTS:
			if FILE_EXTS[file_ext] == 'image':
				metadata = parse_image(directory)
			elif FILE_EXTS[file_ext] ==  'vid':
				metadata = parse_vid(directory)
			elif FILE_EXTS[file_ext] == 'mp3':
				metadata = parse_mp3(directory)
			elif FILE_EXTS[file_ext] == 'doc':
				metadata = parse_doc(directory)

			metadata['localpath'] = os.getcwd()+'/'+directory
			metadata['size'] = os.path.getsize(metadata['localpath'])
			metadata['file_name'] = name
			metadata['a_name'] = a_name
			metadata['keywords'] = []
			if keywords != '-nk':
				metadata['keywords'] = keywords.split(':')
			else:
			
				metadata['keywords'] = []
		else:
			print "unsupported file extension"
			metadata = None
	return metadata

def datetime_handler(x):
    if isinstance(x, datetime.datetime):
        return x.isoformat()
    elif isinstance(x, datetime.timedelta):
    	return str(x)

FILE_EXTS = {
	# image files
	'mp3' : 'image',
	'bmp' : 'image',
	'gif' : 'image',
	'jpeg' : 'image',
	'png' : 'image',
	# video files
	'avi' : 'vid',
	'mov' : 'vid',
	'wmv' : 'vid',
	'mp4' : 'vid',

	# audio file,

	'mp3' : 'mp3',

	# documents
	'docx' : 'doc',
}


HachoirConfig.quiet = True

args = sys.argv
print args
last_arg = args.pop()
keywords = args.pop()
annotated_name = args.pop()
print "python metadata_extractor.py dir <annotated_name>  <keywords>/-nk --bulk/--single"
metadata = {
	'data' : []
}
if last_arg == "--bulk":
	print keywords
	print annotated_name
	directory = args[1]
	onlyfiles = [f for f in listdir(directory) if isfile(join(directory, f))]
	for f in onlyfiles:
		meta = file_metadata(directory+f, f, annotated_name, keywords)
		if meta is not None:
			metadata['data'].append(meta)

elif last_arg == "--single":
	file_name = args[1]
	metadata['data'] = [file_metadata(file_name, file_name, annotated_name, keywords)]
d = json.dumps(metadata, ensure_ascii=False, default=datetime_handler)
print d
url = 'http://ericyang24.pythonanywhere.com/add_metadata'
headers = {'Content-type': 'application/json'}
r = requests.post(url, data=d, headers=headers)
f = open('response.html', 'w')
f.write(r.content)
f.close()

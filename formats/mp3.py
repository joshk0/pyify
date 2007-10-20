"""mp3 module for pyify"""

import os
import string
import popen2
import sys
from util import forkexec, copyfileobj

required = { "encode": "lame", "decode": "mpg123" }
format = "mp3"

# return a dictionary file of the metadata
# key names are based on output of vorbiscomment
def getMetadata(path):
	try: import eyeD3
	except:
		sys.stderr.write("Warning: no ID3 support, please install python-eyed3")
		return dict()
	
	tag = eyeD3.Tag()
	tag.link(path)

	tags = { 'ARTIST': tag.getArtist(),
		'ALBUM': tag.getAlbum(),
		'TITLE': tag.getTitle(),
		'DATE': tag.getDate(),
		'GENRE': tag.getGenre(),
		'TRACKNUMBER': tag.getTrackNum()[0] }

	for tag in tags:
		if tag[1] == "" or tag[1] == None:
			del tags[tag[0]]

	return tags

# return open file object with audio stream
def getAudioStream(path):
	subargv = ["mpg123", "-q", "-s", path]
	(i, o) = os.popen2(subargv, 'b')
	i.close()
	return o

def encodeAudioStream(input_stream, destination, metadata=dict()):
	tag_bind = { 'ARTIST': 'a', 
				 'TITLE': 't', 
				 'ALBUM': 'l',
				 'DATE': 'y',
				 'GENRE': 'g',
				 'TRACKNUMBER': 'n' }
	
	encode_command = ["lame", "-V5", "--quiet", "--vbr-new",
		"--ignore-tag-errors", "--add-id3v2"]
	
	# converting *all* metadata keys to upper case equivalents here
	# also, iterating only over the files supported by the encoder is 
	# probably the only way to prevent key errors.
	
	for key, flag in tag_bind.items():
		if key in metadata:
			encode_command.extend(["--t"+ flag, metadata[key]])
	 
	encode_command.extend(['-', destination])

	pid = forkexec(encode_command, file_stdin=input_stream)
	input_stream.close()

	return pid

"""ogg/vorbis module for pyify"""

import os
import string
import popen2
import shutil

format = "mp3"

# return a dictionary file of the metadata
# key names are based on output of vorbiscomment
def getMetadata(path):
	return dict()

# return open file object with audio stream
def getAudioStream(path):
	subargv = ["mpg123", "-s", path]
	return os.popen2(subargv, 'b')[1]

def encodeAudioStream(input_stream, destination, metadata=dict()):
	tag_bind = { 'artist': 'a', \
				 'title': 't', \
				 'album': 'l', \
				 'date': 'y', \
				 'genre': 'g', \
				 'tracknumber': 'n' }
	
	encode_command = ["lame", "--alt-preset", "standard", "--quiet", "--ignore-tag-errors", "--add-id3v2"]
	[encode_command.extend(['--t' + tag_bind[tag[0]], tag[1]]) for tag in metadata.items()]
	encode_command.extend(['-', destination])

	print encode_command
	
	(encode_stream, stdout) = os.popen2(encode_command, 'b')
	shutil.copyfileobj(input_stream, encode_stream)
	encode_stream.close()
	stdout.close()

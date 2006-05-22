"""mp3 module for pyify"""

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
	tag_bind = { 'ARTIST': 'a', 
				 'TITLE': 't', 
				 'ALBUM': 'l',
				 'DATE': 'y',
				 'GENRE': 'g',
				 'TRACKNUMBER': 'n' }
	
	encode_command = ["lame", 
	"--alt-preset", 
	"standard", 
	"--quiet", 
	"--ignore-tag-errors", 
	"--add-id3v2"]
	
	#converting *all* metadata keys to upper case equivilents here
	#also, iteratong only over the files supported by the encoder is 
	#probably the only way to prevent key errors.
	#[encode_command.extend(['--t' + tag_bind[tag[0]], tag[1]]) 
	# for tag in metadata.items()]
	for key, flag in tag_bind.items():
		if metadata.has_key(key):
			encode_command.extend(["--t"+ flag, metadata[key]])
	 
	encode_command.extend(['-', destination])

	print encode_command
	
	(encode_stream, stdout) = os.popen2(encode_command, 'b')
	shutil.copyfileobj(input_stream, encode_stream)
	encode_stream.close()
	stdout.close()

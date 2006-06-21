"""ogg/vorbis module for pyify"""

import os
import string
from util import copyfileobj
format = "ogg"

# return a dictionary file of the metadata
# key names are based on output of vorbiscomment
def getMetadata(path):
	command = ["vorbiscomment", "-l", path]
	tags = os.popen2(command)[1].readlines()
	tags = [(x[0].upper(), x[1].strip()) for x in [x.split("=") for x in tags]]
	tags = dict(tags)
	return tags

# return open file object with audio stream
def getAudioStream(path):
	subargv = ["ogg123", "-d", "wav", "-q", "-f", "-", path]
	return os.popen2(subargv, 'b')[1]

def encodeAudioStream(input_stream, destination, metadata=dict()):
	encode_command = ["oggenc", "-q4.5", "-Q", "-", "-o", destination]
	
	for x in metadata.items():
		encode_command.extend(["-c", string.join(x, "=")])

	forkexec(encode_command, file_stdin=input_stream)
	input_stream.close()

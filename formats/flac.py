"""FLAC module for pyify, nearly identical to ogg"""

import os
import string
from util import forkexec

required = { "encode": "flac",
             "decode": "flac",
             "gettags": "metaflac" }
format = "flac"

# return a dictionary file of the metadata
# key names are based on output of vorbiscomment
def getMetadata(path):
	command = ["metaflac", "--export-tags-to=-", path]
	(o, tagsP) = os.popen2(command)
	tags = [(x[0].upper(), x[1].strip()) for x in [x.split("=") for x in tagsP.readlines()]]
	tagsP.close()
	o.close()
	return tags

# return open file object with audio stream
def getAudioStream(path):
	subargv = ["flac", "-s", "-d", "-c", path]
	(o, i) = os.popen2(subargv, 'b')
	o.close()
	return i

def encodeAudioStream(input_stream, destination, metadata=dict()):
	encode_command = ["flac", "-f", "-s", "-8", "-", "-o", destination]
	for x in metadata.items():
		encode_command.extend(["-T", string.join(x, "=")])

	pid = forkexec(encode_command, file_stdin=input_stream)
	input_stream.close()

	return pid

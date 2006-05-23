"""FLAC module for pyify, nearly identical to ogg"""

import os
import string
from util import copyfileobj
format = "flac"

# return a dictionary file of the metadata
# key names are based on output of vorbiscomment
def getMetadata(path):
	command = ["metaflac", "--export-tags-to=-", path]
	tags = os.popen2(command)[1].readlines()
	tags = [(x[0].upper(), x[1].strip()) for x in [x.split("=") for x in tags]]
	tags = dict(tags)
	return tags

# return open file object with audio stream
def getAudioStream(path):
	subargv = ["flac", "-s", "-d", "-c", path]
	return os.popen2(subargv, 'b')[1]

def encodeAudioStream(input_stream, destination, metadata=dict()):
	encode_command = ["flac", "-f", "-s", "-8", "-", "-o", destination]
	tag_command = ["metaflac", "--import-tags-from=-", destination]
	output_stream = os.popen2(encode_command,"wb")[0]
	copyfileobj(input_stream, output_stream)
	tag, stdout = os.popen2(tag_command, "wt")
	# takes the dictionary, turns it into k=v pairs, and joins the k=v
	# pairs with newlines
	tag.write(string.join([(string.join(x, "=")) for x in metadata.items()], "\n"))
	tag.close()
	stdout.close()


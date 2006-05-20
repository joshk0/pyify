"""ogg/vorbis module for pyify"""

format = "ogg"

# return a dictionary file of the metadata
# key names are based on output of vorbiscomment
def getMetaData(path):
	command = ["vorbiscomment", "-l", path]
	tags = os.popen2(command)[1].readlines()
	tags = [(x[0], x[1].strip()) for x in [x.split("=") for x in tags]]
	tags = dict(tags)
	return tags

# return open file object with audio stream
def getAudioStream(path):
	subargv = "ogg123 -d wav -q -f -".split()
	subargv.append(path)
	return os.popen2(subargv, 'b')[1]

def encodeAudioStream(input_stream, destination, metadata):
	encode_command = ["oggenc", "-q4.5", "-Q", "-", "-o", destination]
	tag_command = ["vorbiscomment", "-a", "-c", "-", destination]

	forkexec(encode_command)
	(i,o) = os.popen2(tag_command, 't')
	# takes the dictionary, turns it into k=v pairs, and joins the k=v
	# pairs with newlines
	o.write(string.join([(string.join(x, "=")) for x in metadata.items()], "\n"))
	o.close()


#! /usr/bin/env python

import os
import sys
import string

class audioFile:
	"""Represents an abstraction of an audio file. Don't
	instantiate this class directly. Instead instantiate
	one of its subclasses.
	"""
	
	# use this constructor to instantiate a file in the
	# source format. metadata is initialized from file tags
	# using whatever method is appropriate.
	def __init__(self, path):
		self.path     = path
		(base, ext)   = os.path.splitext(os.path.basename(path))
		self.type     = ext
		self.name     = base
		self.metadata = self.getMetaData()
	
	#default method simply returns the open file
	def getAudioStream():
		return open(path, "r")
		
# reference audioFile implementation class
class oggFile(audioFile):
	"""ogg/vorbis module"""
	
	#todo -- read this in from config file
	encode_command = "oggenc -q4.5 -Q - %s -o %s"
	
	flags = { 
			"ARTIST" : "-a", 
			"TITLE" : "-t" ,
			"ALBUM" : "-l" ,
			"DATE" : "-d" ,
		    "GENRE" : "-G", 
		    "TRACKNUMBER" : "-N"
	}
	
	# return dictionary of file metadata
	# key names are based on output of vorbiscomment
	def getMetaData(self):
		command = "vorbiscomment -l \"%s\"" % self.path
		tags = os.popen(command).readlines()
		tags = [(x[0], x[1]) for x in [x.split("=") for x in tags]]
		tags = dict(tags)
		return tags
	
	# return open file object with audio stream
	def getAudioStream(self):
		command = "ogg123 -d wav -q -f - %s" % self.path
		return os.popen(command)

	def encodeAudioStream(self, input_stream, destination):
		tagargs = str()
		for (key, value) in self.metadata.items():
			if self.flags.has_key(key):
				tagargs = tagargs + "%s \"%s\" " % (self.flags[key], value)
		command = self.encode_command % (tagargs, destination)
		print "debug: " + command
		
		(child_stdin, child_stdout) = os.popen2(command)
		child_stdin.write(input_stream.read())
		child_stdin.close()

#test
theFile = oggFile("01.Les_Seigneurs.ogg")
audio = theFile.getAudioStream()
theFile.encodeAudioStream(audio, "test.ogg")


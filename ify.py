#! /usr/bin/env python

import os
import sys
import string

class audioFile:
	"""Represents an abstraction of an audio file"""
		
	def __init__(self, path):
		self.path     = path
		self.name     = os.basename(path)
		(base, ext)   = os.split(self.basename)
		self.type     = ext
		self.metadata = self.getMetaData()
	
	def __init__(self, path, metadata):
		self.path     = path
		self.name     = os.basename(path)
		(base, ext)   = os.split(self.basename)
		self.metadata = metadata
		
class oggFile(audioFile):

	# return dictionary of file metadata
	def getMetaData(self):
		command = "vorbiscomment -l \"%s\"" % self.path
		tags = popen(comand).readlines()
		tags = [(x[0], x[1]) for x in [x.split("=") in tags]]
		tags = dict(tags)
		return dict
	
	# return open file object with audio stream
	def getAudioStream(self):
		command = "-d wav -q -f - %s" % self.path
		return os.popen(command)

	def encodeAudioStream(self):
		flags = { 
			"ARTIST" : "-a", 
			"TITLE" : "-t" ,
			"ALBUM" : "-l" ,
			"DATE" : "-d" ,
		    "GENRE" : "-G", 
		    "TRACKNUMBER" : "-N" 
		}
	"
		for (key, value) in self.metadata.items():
			

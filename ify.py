#!/usr/bin/env python

import os
import sys
import string
import getopt

# Local imports.
import util

class audioFile:
	"""Represents an abstraction of an audio file. Don't
	instantiate this class directly. Instead instantiate
	one of its subclasses.
	"""
	
	# use this constructor to instantiate a file in the
	# source format.
	def __init__(self, path, metadata=None):
		self.path     = path
		(base, ext)   = os.path.splitext(os.path.basename(path))
		self.name     = base
		if not metadata:
			self.metadata = self.getMetaData()
	
	#default method simply returns the open file
	def getAudioStream(self):
		return open(path, "r")
	def encodeAudioStream(self, inputStream, destination):
		outputStream = open(destination + self.path, "w")
		outputStream.write(inputStream.read())
		
# reference audioFile implementation class
class oggFile(audioFile):
	"""ogg/vorbis module"""
	
	# return dictionary of file metadata
	# key names are based on output of vorbiscomment
	def getMetaData(self):
		command = "vorbiscomment -l \"%s\"" % self.path
		tags = os.popen(command).readlines()
		tags = [(x[0], x[1].strip()) for x in [x.split("=") for x in tags]]
		tags = dict(tags)
		return tags
	
	# return open file object with audio stream
	def getAudioStream(self):
		subargv = "ogg123 -d wav -q -f -".split()
		subargv.append(self.path)
		return os.popen2(subargv, 'b')[1]

	def encodeAudioStream(self, input_stream, destination):
		encode_command = ["oggenc", "-q4.5", "-Q", "-", "-o", destination]
		tag_command = ["vorbiscomment", "-a", "-c", "-", destination]

		forkexec(encode_command)
		(i,o) = os.popen2(tag_command, 't')
		# takes the dictionary, turns it into k=v pairs, and joins the k=v
		# pairs with newlines
		o.write(string.join([(string.join(x, "=")) for x in self.metadata.items()], "\n"))
		o.close()

def process(files):
	for path in files:
		if os.path.isdir(path):
			print "Can't handle directories yet"
		else:
			basename, ext = os.path.splitext(path)
			ext = ext[1:]
			if not quiet:
				print path
				print "[%s->%s]" % (ext, format)
			inputFile = formats[ext](path)
			outputFile = formats[format](basename + "." + format,
				metadata=inputFile.metadata)
			outputFile.encodeAudioStream(inputFile.getAudioStream(),
				destination)

#note that none of this is compatible of ify.pl
def usage():
	print """usage: ify.py [options] files
	options:
		-h or --help                  this message
		-d or --destionation=PATH     path to output directory
		--convert-formats=FMT,FMT2..  only select files in FMT for conversion
		-o FMT or --format=FMT        convert files to this format
		-f or --force                 convert even if output file is already
	                                  present
		-q or --quiet                 don't print any output
		--delete                      delete originals after converting
		--dry-run                     don't do anything, just print
		                              output"""
									
#uses gnu_getopts...there's also a realllllly nifty optparse module
#lests you specify actions, default values, argument types, etc,
#but this was easier on my brain at 12:00AM wednesday night
destination = ""
convert_regex = None
format = "wav"
force = False
quiet = False
delete = False
dry_run = False

# associates between extensions and conversion modules
formats = {"wav" : audioFile, "ogg" : oggFile}

try:
	shortargs = "hd:o:fq"
	longargs  = ["help", 
	             "destination=", 
				 "convert-regex=", 
				 "format=", 
				 "force",
				 "quiet", 
				 "delete", 
				 "dry-run"]
				 
	opts, args = getopt.gnu_getopt(sys.argv[1:], shortargs, longargs)
	for (option, arg) in opts:
		if option == "--help" or option == "-h":
			usage()
			sys.exit(0)
		if option == "--destination" or option == "-d":
			destination = arg
		elif option == "--convert-regex":
			convert_regex=arg
		elif option == "--format" or option == "-o":
			if formats.has_key(arg):
				output_format = arg
			else:
				s = "Format must be one of {%s}" % string.join(formats.keys(), ", ")
				raise getopt.GetoptError(s)
		elif option == "--force" or "-f":
			pass
		elif option == "--quiet" or "-q":
			quiet = True
		elif option == "--delete" or "-r":
			delete_originals = True
		elif option == "--dry_run":
			dry_run = True
	if len(args) == 0:
		raise getopt.GetoptError("No input files")
	elif False in [os.path.exists(file) for file in args]:
		raise getopt.GetoptError("One or more input files does not exist!")
	
except getopt.GetoptError, error:
	print "Error parsing arguments: %s %s\n" % (error.opt, error.msg)
	print "List of accepted arguments:"
	usage()
	sys.exit(1)

process(args)

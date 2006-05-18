#! /usr/bin/env python

import os
import sys
import string
import getopt

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
		tags = [(x[0], x[1].strip()) for x in [x.split("=") for x in tags]]
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
		command = self.encode_command % (tagargs, destination +
				self.path)
		print "debug: " + command
		
		(child_stdin, child_stdout) = os.popen2(command)
		child_stdin.write(input_stream.read())
		child_stdin.close()

def process(files):
	for path in files:
		if os.path.isdir(path):
			print "Can't handle directories yet"
		else:
			basename, ext = os.path.splitext(path)
			ext = ext[1:]
			if not quiet:
				print path
				print "[%s -> %s]" % (ext, format)
			inputFile = formats[ext](path)
			outputFile = formats[format](basename + "." + format,
				metadata=inputFile.metadata)
			outputFile.encodeAudioStream(inputFile.getAudioStream(),
				destination)

#note that none of this is compatible of ify.pl
def usage():
	print """usage: ify.py [options] files
	options:
		-h or --help                this message
		-d or --destionation=PATH   path to output directory
		--convert-regex=EXPR        *josh, what does this do?*    
		-o FMT or --format=FMT      convert files to this format
		-f or --force               *what does this do?*
		-q or --quiet               don't print any output
		--delete                    delete originals after converting
		--dry-run                   don't do anything, just print
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
				s = "Format must be one of {%s}" \
				% string.join(formats.keys(), ", ")
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
		raise getopt.GetoptError("No input file's")
	elif False in [os.path.exists(file) for file in args]:
		raise getopt.GetoptError("One or more input files does not exist!")
	
except getopt.GetoptError, error:
	print "Error parsing arguments: %s %s" % (error.opt, error.msg)
	print "try -h or --help option"
	sys.exit()

process(args)

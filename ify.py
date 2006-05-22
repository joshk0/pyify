#!/usr/bin/env python

import os
import sys
import string
import getopt
import glob
import imp

# Local imports into current namespace
from util import *

def process(files):
	for path in files:
		if os.path.isdir(path):
			print "Can't handle directories yet, skipping!"
		else:
			basename, ext = os.path.splitext(path)
			ext = ext[1:]
			targetname = basename + "." + format
			ify_print("[%s->%s] %s", ext, format, path)
			if not dry_run:
				decode_plugin = formats[ext]
				encode_plugin = formats[format]
				tags  = decode_plugin.getMetadata(path)
				audio = decode_plugin.getAudioStream(path)
				encode_plugin.encodeAudioStream(audio, targetname, tags)

#note that none of this is compatible of ify.pl
def usage():
	print """usage: ify.py [options] files
	options:
		-h or --help                  this message
		-d or --destination=PATH      path to output directory
		--convert-formats=FMT,FMT2..  only select files in FMT for conversion
		-o FMT or --format=FMT        convert files to this format
		-f or --force                 convert even if output file is already
	                                  present
		-q or --quiet                 don't print any output
		--delete                      delete originals after converting
		--dry-run                     don't do anything, just print actions"""
									
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
#TODO add option to change this default
plugin_dir = "formats"

# build formats data structure
try:
	shortargs = "hd:o:fq"
	longargs  = ["help", 
	             "destination=", 
				 "convert-regex=", 
				 "format=", 
				 "force",
				 "quiet", 
				 "delete", 
				 "dry-run",
				 "plugin-dir="]
				 
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
			format = arg
		elif option == "--force" or option == "-f":
			pass
		elif option == "--quiet" or option == "-q":
			quiet = True
		elif option == "--delete" or option == "-r":
			delete_originals = True
		elif option == "--dry_run":
			dry_run = True
		elif option == "--plugin-dir":
			if os.path.exists(arg):
				plugin_dir = arg
			else:
				print "Error: plugin-dir does not exist"
				sys.exit(-1)
	if len(args) == 0:
		raise getopt.GetoptError("No input files")
	elif False in [os.path.exists(file) for file in args]:
		raise getopt.GetoptError("One or more input files does not exist!")
	
	# build formats data structure
	formats = dict()
		
	try:
		for path in os.listdir(plugin_dir):
			path = os.path.join(plugin_dir, path)
			if os.path.isfile(path):
				name, ext = os.path.splitext(os.path.basename(path))
				file = open(path, "r")
				if ext == ".py":
					ify_print ("Loading module %s...", name)
					plugin = imp.load_source(name, path, file)
					formats[plugin.format] = plugin
				elif ext == ".pyc":
					pass
				else:
					ify_print("Can't load plugin %s, bad suffix \"%s\"", path,
							ext)
		if not formats.has_key(format):
			raise getopt.GetoptError("Format must be one of {%s}" %
					string.join(formats.keys()))

	except ImportError, error:
		print "Import error has occured: %r" % error.args

except getopt.GetoptError, error:
	print "Error parsing arguments: %s %s\n" % (error.opt, error.msg)
	print "List of accepted arguments:"
	usage()
	sys.exit(1)

process(args)

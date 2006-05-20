#!/usr/bin/env python

import os
import sys
import string
import getopt
import glob
import imp

# Local imports into current namespace
from util import *

# prints a message appropriate to verbosity level
#TODO variadic arguments 

def ify_print(message, *args):
	if not quiet:
		print message

def process(files):
	for path in files:
		if os.path.isdir(path):
			print "Can't handle directories yet, skipping!"
		else:
			basename, ext = os.path.splitext(path)
			ext = ext[1:]
			targetname = basename + "." + format
			ify_print("%s\n[%s->%s]" % (path, ext, format))
			#TODO -- rewrite this portion of the code 
			#based on whatever our plugin architecture is

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
#TODO add option to change this default
plugins_dir = "formats"

# build formats data structure
formats = dict()
	
try:
	for path in os.listdir(plugins_dir):
		path = os.path.join(plugins_dir, path)
		if os.path.isfile(path):
			name, ext = os.path.splitext(os.path.basename(path))
			file = open(path, "r")
			if ext == ".py":
				ify_print ("Loading module %s..." % name)
				plugin = imp.load_source(name, path, file)
				formats[plugin.format] = plugin
			elif ext == ".pyc":
				pass
			else:
				ify_print("Invalid suffix %s. for file %s" % (ext, path))

except ImportError, error:
	print "Import error has occured: %r" % error.args
	
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

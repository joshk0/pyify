#!/usr/bin/env python

import os
import sys
import string
import getopt
import glob
import imp

# Local imports into current namespace
from util import *

def process_file(path):
	basename, ext = os.path.splitext(path)
	ext = ext[1:]
	if formats.has_key(ext):
		# Be more vocal about this because the user passed the file in 
		# explicitly, there's more of a chance that a botched --convert-formats
		# arg was at fault.
		if not check_want_convert(ext):
			ify_warn("Skipping %s: not specified in --convert-formats!", 
				os.path.basename(path))
			return 1

		process_audio_file(path, os.path.join(destination, basename +
					"." + format))
	elif ext == "m3u":
		process_playlist(path)
	else:
		ify_print("Error, unsupported file format \"%s\"", ext)
	
# format is already covered
def process_audio_file(from_path, to_path):
	''' Does no more and no less than taking the file in from_path,
	    using its extension to determine its file type, and converting
		it to the format specified in the eponymous variable to the file
		specified in to_path. '''

	old_ext = os.path.splitext(from_path)[1][1:]

	ify_print("[%s->%s] %s", old_ext, format, from_path)
	
	if not dry_run:
		decode_plugin = formats[old_ext]
		encode_plugin = formats[format]
		tags  = decode_plugin.getMetadata(from_path)
		audio = decode_plugin.getAudioStream(from_path)
		try: encode_plugin.encodeAudioStream(audio, to_path, tags)
		except KeyboardInterrupt:
			print "[deleted] %s" % to_path
			os.unlink(to_path)
			sys.exit(1)

def process_playlist(path):
	ify_print("[playlist]")
	print "Playlists are not yet supported!"
	
def process_dir(path, prefix=""):
	containing_dir = os.path.basename(path) # current toplevel path
	target_dir = os.path.join(destination, prefix, containing_dir)
	
	ify_print("[directory] %s" % target_dir)

	if not dry_run and not os.path.isdir(target_dir):
		os.mkdir(target_dir)

	listing = os.listdir(path)
	
	def sort_alpha(a, b):
		if a.lower() < b.lower():
			return -1
		elif a.lower() > b.lower():
			return 1
		else:
			return 0
	
	listing.sort(sort_alpha)
	
	for file in listing:
		file_fullpath = os.path.join(path, file)
		if os.path.isdir(file_fullpath):
			process_dir(file_fullpath, os.path.join(prefix, containing_dir))
		elif os.path.isfile(file_fullpath):
			(basename, ext) = os.path.splitext(file)
			if ext[1:] in formats and check_want_convert(ext[1:]):
				process_audio_file(file_fullpath, os.path.join(destination, prefix, containing_dir, os.path.splitext(file)[0] + "." + format))

def process(arg):
	if os.path.isfile(arg):
		process_file(arg)
	elif os.path.isdir(arg):
		process_dir(arg)
	else:
		ify_print("Error: unrecognized argument \"%s\"", path)

def check_want_convert(ext):
	if convert_formats == None: return True
	elif ext.lower() in convert_formats: return True
	else: return False

# note that none of this is compatible with ify.pl
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
destination = os.getcwd()
convert_formats = None
format = "wav"
force = False
quiet = False
delete = False
dry_run = False
plugin_dir = os.path.join(sys.path[0], "formats")

# build formats data structure
try:
	shortargs = "hd:o:fq"
	longargs  = ["help", 
	             "destination=", 
				 #changed from convert-formats
				 "convert-formats=", 
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
		elif option == "--convert-formats":
			convert_formats = arg.split(",")
		elif option == "--format" or option == "-o":
			format = arg
		elif option == "--force" or option == "-f":
			pass
		elif option == "--quiet" or option == "-q":
			quiet = True
		elif option == "--delete" or option == "-r":
			delete_originals = True
		elif option == "--dry-run":
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
					# ify_print ("Loading module %s...", name)
					plugin = imp.load_source(name, path, file)
					formats[plugin.format] = plugin
				elif ext == ".pyc":
					pass
				else:
					ify_print("Can't load plugin %s, bad suffix \"%s\"", path,
							ext)
		if not format in formats:
			raise getopt.GetoptError("Format must be one of {%s}" %
					string.join(formats.keys()))

	except ImportError, error:
		print "Import error has occured: %r" % error.args

except getopt.GetoptError, error:
	print "Error parsing arguments: %s %s\n" % (error.opt, error.msg)
	print "List of accepted arguments:"
	usage()
	sys.exit(1)

for arg in args:
	process(arg)

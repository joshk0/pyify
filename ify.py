#!/usr/bin/env python

import time
import os
import sys
import string
import getopt
import glob
import imp
import signal
import mutex

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

queue = list()
jobs_running = 0 # XXX
encoder_pids = dict() # XXX

def run_encode_queue():
	global jobs_running, encoder_pids

	# Start as many jobs as specified by concurrency, or as many objects
	# as there are in the queue, whichever is smaller
	for job in range(min(concurrency, len(queue))):
		jobs_running += 1
		process_audio_file_real(*queue.pop(0))
	
	while jobs_running > 0:
		(pid, status) = os.waitpid(-1, os.WNOHANG)

		if pid == 0: # No changes
			time.sleep(1)
			continue

		if pid in encoder_pids:
			del encoder_pids[pid] # and carry on

			if len(queue) == 0: # Clean up if we're done
				jobs_running -= 1
				continue
			else: # Start a new job
				process_audio_file_real(*queue.pop(0))
		
def process_audio_file(from_path, to_path):
	# [6] is filesize in bytes
	if os.path.isfile(to_path) and os.stat(to_path)[6] > 0 and not force:
		ify_print("[up-to-date] %s", to_path)
		return

	queue.append([from_path, to_path])

# format is already covered
def process_audio_file_real(from_path, to_path):
	''' Does no more and no less than taking the file in from_path,
	    using its extension to determine its file type, and converting
		it to the format specified in the eponymous variable to the file
		specified in to_path.
		
		Well, it does do a little bit more - it will not overwrite an 
		existing file if it's larger than 0 bytes, unless --force is
		specified. '''

	old_ext = os.path.splitext(from_path)[1][1:]
		
	ify_print("[%s->%s] %s", old_ext, format, from_path)
	
	if not dry_run:
		decode_plugin = formats[old_ext]
		encode_plugin = formats[format]
		tags  = decode_plugin.getMetadata(from_path)
		audio = decode_plugin.getAudioStream(from_path)
		
		pid = encode_plugin.encodeAudioStream(audio, to_path, tags)
		encoder_pids[pid] = to_path

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
		-j N                          runs N encoding jobs at once 
		-q or --quiet                 don't print any output
		--delete                      delete originals after converting
		--dry-run                     don't do anything, just print actions"""
									
# uses gnu_getopts...there's also a realllllly nifty optparse module
# lets you specify actions, default values, argument types, etc,
# but this was easier on my brain at 12:00AM wednesday night
destination = os.getcwd()
convert_formats = None
format = "wav"
force = False
quiet = False
delete = False
dry_run = False
plugin_dir = os.path.join(sys.path[0], "formats")
concurrency = 1

try:
	shortargs = "hd:o:fqj:"
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
		elif option == "-j":
			concurrency = int(arg)
		elif option == "--convert-formats":
			convert_formats = arg.split(",")
		elif option == "--format" or option == "-o":
			format = arg
		elif option == "--force" or option == "-f":
			force = True
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
				ify_error("plugin directory does not exist")
				sys.exit(1)
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

try: run_encode_queue()
except KeyboardInterrupt:
	for file in encoder_pids.values(): 
		print "[deleted] %s" % file
		os.unlink(file)
	sys.exit(1)

from os import popen2, fork, wait, execvp, pipe, dup2, setpgrp
import sys

# execute child process which will optionally use
# either sdtdin as it's standard input or stdout as it's
# standard output or both
def forkexec(args, file_stdin=None, file_stdout=None):
	pid = fork()
	if pid == 0:
		if file_stdin:
			dup2(file_stdin.fileno(), sys.stdin.fileno())
			#os.close(file_stdin.fileno())
		if file_stdout:
			dup2(file_stdout.fileno(), sys.stdout.fileno())
			#os.close(file_stdout.flieno())
		execvp(args[0], args)
	elif pid > 0:
		return pid # ignored right now

#replacement for shutil.copyfileobj that works
def copyfileobj(src, dst):
	while True:
		buf = src.read(4096)
		if len(buf) > 0: dst.write(buf)
		else: return
		if len(buf) < 4096: return

# we have a global being defined here in util.py...is this bad idea?
quiet = False
def ify_print(message, *args):
	if not quiet:
		print message % tuple(args)

def ify_warn(message, *args):
	sys.stderr.write("Warning: ")
	sys.stderr.write(message % tuple(args))
	sys.stderr.write("\n")

def ify_error(message, *args):
	sys.stderr.write("Error: ")
	sys.stderr.write(message % tuple(args))
	sys.stderr.write("\n")

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
	

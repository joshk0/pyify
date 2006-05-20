from os import popen2

def ify_print(message, *args):
	if not quiet:
		print message

def forkexec(args):
	pid = os.fork()
	if pid == 0:
		os.execvp(args[0], args)
	elif pid > 0:
		os.wait()

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
	

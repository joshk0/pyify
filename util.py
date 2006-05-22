from os import popen2, fork, wait, execvp

def forkexec(args):
	pid = fork()
	if pid == 0:
		execvp(args[0], args)
	elif pid > 0:
		wait()

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
	

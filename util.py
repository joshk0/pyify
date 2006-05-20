from os import popen2

def forkexec(args):
	pid = os.fork()
	if pid == 0:
		os.execvp(args[0], args)
	elif pid > 0:
		os.wait()

""" Wav module for ify"""
from util import copyfileobj

format = "wav"

def getMetadata(path):
	return dict()
	
def getAudioStream(path):
	return open(path, "r")
	
def encodeAudioStream(inputStream, destination, metadata=None):
	outputStream = open(destination, "w")
	copyfileobj(inputStream, outputStream)
	outputStream.close()

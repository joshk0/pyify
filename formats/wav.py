""" Wav module for ify"""
import shutil

format = "wav"

def getMetadata(path):
	return dict()
	
def getAudioStream(path):
	return open(path, "r")
	
def encodeAudioStream(inputStream, destination, metadata=None):
	outputStream = open(destination, "w")
	shutil.copyfileobj(inputStream, outputStream)
	outputStream.close()

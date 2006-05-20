""" Wav module for ify"""
import shutil

format = "wav"

def getAudioStream(self):
	return open(path, "r")
	
def encodeAudioStream(self, inputStream, destination):
	outputStream = open(destination + self.path, "w")
	shutil.copyfileobj(inputStream, outputStream)
	outputStream.close()


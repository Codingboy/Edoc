import argparse
import logging
import sys
import time
import unittest
import os
import math

from archiver import Archiver, Dearchiver
from compressor import Compressor, Decompressor
from encoder import Encoder, Decoder
from filebuffer import WriteBuffer, ReadBuffer


def printProgress():
	now = time.time()
	end = 0
	if (progress != 0):
		end = targetprogress*(float(now-start)/progress)
		end -= (now-start)
	h = math.floor(end/3600)
	m = math.floor((end-h*3600)/60)
	s = math.floor(end-h*3600-m*60)
	h = str(h)
	m = str(m)
	s = str(s)
	if (len(h) == 1):
		h = "0"+h
	if (len(m) == 1):
		m = "0"+m
	if (len(s) == 1):
		s = "0"+s
	print(str(round(progress*1000/targetprogress)/10)+"% "+h+":"+m+":"+s, end="\r")

def getSize(folder):
	if (os.path.isfile(folder)):
		return os.stat(folder).st_size
	size = 0
	files = os.listdir(folder)
	for file in files:
		file = folder+"/"+file
		if (os.path.isfile(file)):
			size += getSize(file)
		elif (os.path.isdir(file)):
			size += getSize(file)
	return size

if __name__ == "__main__":
	PROJECTNAME = "edoc"
	LOGNAME = PROJECTNAME+".log"
	fileLogging = False
	useCurses = True
	profiling = False

	if useCurses:
		import curses
	if profiling:
		import cProfile
		import pstats
		import io

	logger = logging.getLogger(PROJECTNAME)
	logger.setLevel(logging.DEBUG)
	ch = logging.StreamHandler()
	ch.setLevel(logging.DEBUG)
	formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
	ch.setFormatter(formatter)
	logger.addHandler(ch)
	if fileLogging:
		fh = logging.FileHandler(LOGNAME)
		fh.setLevel(logging.DEBUG)
		fh.setFormatter(formatter)
		logger.addHandler(fh)

	parser = argparse.ArgumentParser(description="Encodes or decodes a file or folder.")
	parser.add_argument("-e", "--encode", action="store_true", help="Specify mode: encode")
	parser.add_argument("-d", "--decode", action="store_true", help="Specify mode: decode")
	parser.add_argument("-p", "--password", action="store", metavar="password", help="Specify password.")
	parser.add_argument("-f", "--file", help="Specify file/folder.")
	parser.add_argument("-t", "--test", action="store_true", help="Runs unittests.")
	args = vars(parser.parse_args())
	file = args["file"]
	password = args["password"]
	encodeMode = args["encode"]
	testMode = args["test"]
	root = None
	progress = 0
	targetprogress = getSize(file)
	start = 0
	pr = None
	if testMode:
		unittest.main(argv=[sys.argv[0]])
		input("Press Enter to leave")
		exit()
	else:
		if password is None:
			password = input("Enter password: ")
			if useCurses:
				window = curses.initscr()
				window.clear()
				window.refresh()
		if password is not None:
			if profiling:
				pr = cProfile.Profile()
				pr.enable()
			start = time.time()
			if encodeMode:
				archiver = Archiver(file, True)
				compressor = Compressor()
				encoder = Encoder(password)
				writebuffer = WriteBuffer(file+".edoc")
				while True:
					printProgress()
					breakcondition = False
					data = archiver.read()
					datalen = len(data)
					progress += datalen
					if datalen == 0:
						breakcondition = True
					data = compressor.compress(data)
					data = encoder.encode(data)
					writebuffer.write(data)
					if breakcondition:
						break
				data = compressor.close()
				data = encoder.encode(data)
				data1 = encoder.close()
				writebuffer.write(data)
				writebuffer.write(data1)
				writebuffer.close()
			else:
				readbuffer = ReadBuffer(file)
				decoder = Decoder(password)
				decompressor = Decompressor()
				dearchiver = Dearchiver(file[:-5])
				while True:
					printProgress()
					breakcondition = False
					data = readbuffer.read()
					datalen = len(data)
					progress += datalen
					if datalen == 0:
						breakcondition = True
					data = decoder.decode(data)
					data = decompressor.decompress(data)
					dearchiver.write(data)
					if breakcondition:
						break
				readbuffer.close()
				data = decoder.close()
				data = decompressor.decompress(data)
				data1 = decompressor.close()
				dearchiver.write(data)
				dearchiver.write(data1)
			printProgress()
			if profiling:
				pr.disable()
				s = io.StringIO()
				sortby = "cumulative"
				ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
				ps.print_stats()
				logger.info(s.getvalue())

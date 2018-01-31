import argparse
import logging
import sys
import time
import unittest

from src.archiver import Archiver, Dearchiver
from src.compressor import Compressor, Decompressor
from src.encoder import Encoder, Decoder
from src.filebuffer import WriteBuffer, ReadBuffer

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
			if encodeMode:
				archiver = Archiver(file, True)
				compressor = Compressor()
				encoder = Encoder(password)
				writebuffer = WriteBuffer(file+".edoc")
				while True:
					breakcondition = False
					data = archiver.read()
					if len(breakcondition) == 0:
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
					breakcondition = False
					data = readbuffer.read()
					if len(breakcondition) == 0:
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
			if profiling:
				pr.disable()
				s = io.StringIO()
				sortby = "cumulative"
				ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
				ps.print_stats()
				logger.info(s.getvalue())

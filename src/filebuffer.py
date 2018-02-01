import os
import unittest
from random import randint


class ReadBuffer:
	"""
	ReadBuffer buffers reading of files.

	Attributes:
		fIn: filereference
		bufferSize: size of the buffer
		buffer: buffer
		bufferPos: startposition of the buffer in the open file
		pos: position of the cursor in the open file
		filesize: size of the open file

	Parameters:
		infile: path to file
		buffersize: size of the buffer

	| **Pre:**
	|	os.path.isfile(inFile)
	|	bufferSize > 0

	| **Post:**
	|	self.fIn is open
	|	len(self.buffer) >= 0
	|	len(self.buffer) <= self.bufferSize
	|	isinstance(self.buffer[i], int)
	|	self.buffer[i] >= 0
	|	self.buffer[i] < 256
	|	self.bufferPos == 0
	|	self.pos == 0
	|	self.filesize == os.stat(inFile).st_size
	"""
	def __init__(self, infile: str, buffersize: int=1024):
		self.fIn = open(infile, "rb")#TODO type
		self.bufferSize: int = buffersize
		self.buffer: bytearray = self.fIn.read(self.bufferSize)
		self.bufferPos: int = 0
		self.pos: int = 0
		self.filesize: int = os.stat(infile).st_size

	def seek(self, pos: int):
		"""
		Changes the cursorposition within a file.

		Parameters:
			pos: position

		| **Pre:**
		|	pos >= 0
		|	pos <= self.fileSize
		|	self.fIn is open

		| **Post:**
		|	self.bufferPos = pos

		| **Modifies:**
		|	self.bufferPos
		|	self.buffer[i]
		|	self.fIn
		"""
		self.bufferPos = pos
		self.pos = pos
		self.fIn.seek(pos)
		self.buffer = self.fIn.read(self.bufferSize)

	def read(self, size: int=1024) -> bytearray:
		"""
		Reads data from file into buffer.

		Parameters:
			size: max number of bytes to be read

		Returns:
			read bytes

		| **Pre:**
		|	size > 0
		|	size <= self.bufferSize
		|	self.fIn is open

		| **Post:**
		|	len(return) >= 0
		|	len(return) <= size
		|	isinstance(return[i], int)
		|	return[i] >= 0
		|	return[i] < 256

		| **Modifies:**
		|	self.bufferPos
		|	self.buffer[i]
		|	self.pos
		|	self.fIn
		"""
		ba = bytearray()
		if self.pos+size > self.filesize:
			size = self.filesize-self.pos
		if size == 0:
			return ba
		if self.pos+size > self.bufferPos+self.bufferSize:
			for i in range(self.bufferPos+self.bufferSize-self.pos):
				ba.append(self.buffer[i+self.pos-self.bufferPos])
				size -= 1
			self.seek(self.bufferPos+self.bufferSize)  # TODO ensure buffer contains all data (size<=bufferSize)
			for i in range(self.pos+size-self.bufferPos):
				#print(self.pos+size-self.bufferPos)
				ba.append(self.buffer[i])
		else:
			for i in range(size):
				ba.append(self.buffer[i+self.pos-self.bufferPos])
		self.pos = self.pos+size
		return ba

	def close(self):
		"""
		Closes the file.

		| **Pre:**
		|	self.fIn is open

		| **Post:**
		|	self.fIn is closed

		| **Modifies:**
		|	self.fIn
		"""
		self.fIn.close()


class WriteBuffer:
	"""
	WriteBuffer buffers writing of files.

	Attributes:
		fOut: filereference
		bufferSize: size of the buffer
		buffer: buffer
		size: actual size of the buffer

	Parameters:
		outfile: path to file
		buffersize: size of the buffer

	| **Pre:**
	|	os.path.isfile(outFile)
	|	self.bufferSize > 0

	| **Post:**
	|	self.fOut is open
	|	len(self.buffer) >= 0
	|	len(self.buffer) <= self.bufferSize
	|	isinstance(self.buffer[i], int)
	|	self.buffer[i] >= 0
	|	self.buffer[i] < 256
	|	folders above outFile are created

	Note:
		self.size might be bigger sometimes than self.bufferSize
	"""

	def __init__(self, outfile, buffersize=1024):
		self.bufferSize = buffersize
		self.buffer = bytearray()
		self.size = 0
		index = outfile.rfind("/")
		if index != -1:
			folder = outfile[:index]
			if not os.path.exists(folder):
				os.makedirs(folder)
		self.fOut = open(outfile, "wb")

	def write(self, data: bytearray):
		"""
		Writes data into buffer and file.

		Parameters:
			data: data to be written

		| **Pre:**
		|	self.fIn is open
		|	len(data) > 0
		|	isinstance(data[i], int)
		|	data[i] >= 0
		|	data[i] < 256

		| **Modifies:**
		|	self.size
		|	self.buffer[i]
		|	self.fOut
		"""
		for d in data:
			self.buffer.append(d)
		self.size += len(data)
		if self.size > self.bufferSize:
			self.fOut.write(self.buffer)
			self.size = 0
			self.buffer = bytearray()

	def close(self):
		"""
		Closes the file and flushes the buffer.

		| **Pre:**
		|	self.fOut is open

		| **Post:**
		|	self.fOut is closed

		| **Modifies:**
		|	self.fOut
		"""
		self.fOut.write(self.buffer)
		self.fOut.close()

	def seek(self, pos: int):
		"""
		Changes the cursorposition within a file and flushes buffer.

		Parameters:
			pos: position

		| **Pre:**
		|	pos >= 0
		|	self.fIn is open

		| **Post:**
		|	self.buffer = bytearray()

		| **Modifies:**
		|	self.fOut
		|	self.buffer[i]
		"""
		self.fOut.write(self.buffer)
		self.buffer = bytearray()
		self.fOut.seek(pos)  # TODO preconditions

class FileBufferUnitTest(unittest.TestCase):
	def setUp(self):
		self.srcfile = "../test.txt"

	def tearDown(self):
		pass

	def test_seek(self):
		readbuffer = ReadBuffer(self.srcfile)
		filesize = os.stat(self.srcfile).st_size
		fin = open(self.srcfile, "rb")
		ba = fin.read(filesize)
		pos = randint(0, filesize-1)
		length = randint(0, filesize-pos)
		readbuffer.seek(pos)
		for i in range(length):
			self.assertTrue(ba[pos+i] == readbuffer.read(1)[0])
		readbuffer.seek(0)
		for i in range(filesize):
			self.assertTrue(ba[i] == readbuffer.read(1)[0])
		fin.close()
		readbuffer.close()

	def test_copy(self):
		dstfile = "../test.copy.txt"
		readbuffer = ReadBuffer(self.srcfile)
		writebuffer = WriteBuffer(dstfile)
		while True:
			ba = readbuffer.read(1023)
			if len(ba) == 0:
				break
			writebuffer.write(ba)
		readbuffer.close()
		writebuffer.close()
		self.assertTrue(os.path.isfile(dstfile))
		filesize1 = os.stat(self.srcfile).st_size
		filesize2 = os.stat(dstfile).st_size
		self.assertTrue(filesize1 == filesize2)
		fin1 = open(self.srcfile, "rb")
		fin2 = open(dstfile, "rb")
		ba1 = fin1.read(filesize1)
		ba2 = fin2.read(filesize2)
		for i in range(filesize1):
			self.assertTrue(ba1[i] == ba2[i])
		fin1.close()
		fin2.close()
		os.remove(dstfile)
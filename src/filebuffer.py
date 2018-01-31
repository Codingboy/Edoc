import os


class ReadBuffer:
	"""
	ReadBuffer buffers reading of files.

	Attributes:
		fIn (file): filereference
		bufferSize (int): size of the buffer
		buffer (bytearray): buffer
		bufferPos (int): startposition of the buffer in the open file
		pos (int): position of the cursor in the open file
		filesize (int): size of the open file

	Parameters:
		infile (string): path to file
		buffersize (int): size of the buffer

	| **Pre:**
	|	os.path.isFile(inFile)
	|	self.bufferSize > 0

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

	def __init__(self, infile, buffersize=1024):
		self.fIn = open(infile, "rb")
		self.bufferSize = buffersize
		self.buffer = self.fIn.read(self.bufferSize)
		self.bufferPos = 0
		self.pos = 0
		self.filesize = os.stat(infile).st_size

	def seek(self, pos):
		"""
		Changes the cursorposition within a file.

		Parameters:
			pos (int): position

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
		self.fIn.seek(pos)
		self.buffer = self.fIn.read(self.bufferSize)

	def read(self, size=1024):
		"""
		Reads data from file into buffer.

		Parameters:
			size (int): max number of bytes to be read

		Returns:
			bytearray: read bytes

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
			self.seek(self.bufferPos+self.bufferSize)  # TODO ensure buffer contains all data (size<=bufferSize)
			for i in range(self.pos+size-self.bufferPos):
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
		fOut (file): filereference
		bufferSize (int): size of the buffer
		buffer (bytearray): buffer
		size (int): actual size of the buffer

	Parameters:
		outfile (string): path to file
		buffersize (int): size of the buffer

	| **Pre:**
	|	os.path.isFile(outFile)
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

	def write(self, data):
		"""
		Writes data into buffer and file.

		Parameters:
			data (bytearray): data to be written

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

	def seek(self, pos):
		"""
		Changes the cursorposition within a file and flushes buffer.

		Parameters:
			pos (int): position

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

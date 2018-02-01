import os
from filebuffer import ReadBuffer, WriteBuffer
from typing import List
import unittest
import shutil


class Archiver:
	"""
	Archiver converts files/folders to bytearrays.

	Attributes:
		readBuffer: readBuffer
		files: list of files and folders that need to be processed
		file: path to actual file
		delete: status if the file should be deleted after it is processed
		readSize: number of bytes read in one call
		folder: folder

	Parameters:
		folder: path to file/folder
		delete: status if the file should be deleted after it is processed

	| **Pre:**
	|	os.path.isfile(folder) or os.path.isdir(folder)

	| **Post:**
	|	self.readBuffer = None
	|	self.file = ""
	|	self.readSize = 1024
	|	self.files contains files/folders in folder
	"""
	def __init__(self, folder: str, delete: bool=False):
		self.readBuffer: ReadBuffer = None
		self.files: List[str] = []
		self.folder:str = ""
		index = folder.rfind("/")
		if index != -1:
			index += 1
			self.folder = folder[:index]
		if os.path.isfile(folder):
			if index != -1:
				self.files = [folder[index:]]
			else:
				self.files = [folder]
		elif os.path.isdir(folder):
			files = os.listdir(folder)
			for file in files:
				file = folder+"/"+file
				file = file[len(self.folder):]
				self.files.append(file)
		self.file: str = ""
		self.delete: bool = delete
		self.readSize: int = 1024

	def read(self) -> bytearray:
		"""
		Reads data from file/folder.

		Parameters:

		Returns:
			read bytes

		| **Modifies:**
		|	self.readBuffer
		|	self.files
		"""
		ba = bytearray()
		if self.readBuffer is None:
			while True:
				if len(self.files) == 0:
					break
				else:
					file = self.files.pop(0)
					file = self.folder+file
					if os.path.isdir(file):
						folder = file
						files = os.listdir(folder)
						for file in files:
							file = folder+"/"+file
							self.files.append(file)
					elif os.path.isfile(file):
						self.readBuffer = ReadBuffer(file)
						self.file = file
						file = file[len(self.folder):]
						length = len(file)
						ba.append(length >> 8)
						ba.append(length & 255)
						for c in file:
							ba.append(ord(c))
						filesize = os.stat(self.file).st_size
						for i in range(8):
							ba.append((filesize >> (8*(8-1-i))) & 255)
						break
		else:
			ba = self.readBuffer.read(self.readSize)
			if len(ba) == 0:
				self.readBuffer.close()
				self.readBuffer = None
				if self.delete:
					os.remove(self.file)
				ba = self.read()
		return ba


class Dearchiver:
	"""
	Dearchiver converts bytearrays to files/folders.

	Attributes:
		writeBuffer: writeBuffer
		folder: folder to extract to
		filesize: remaining bytes that belong to the actual file
		buffer: buffer for unprocessed data

	Parameters:
		folder: path to folder

	| **Pre:**
	|	os.path.isdir(folder)

	| **Post:**
	|	self.writeBuffer = None
	|	self.buffer = None
	|	self.filesize = 0
	|	self.folder = folder
	"""
	def __init__(self, folder: str):
		self.writeBuffer: WriteBuffer = None
		self.filesize: int = 0
		self.buffer: bytearray = None
		self.folder: str = folder

	def write(self, data: bytearray):
		"""
		Writes data to file/folder.

		Parameters:
			data: data to be processed

		Returns:

		| **Modifies:**
		|	self.buffer
		|	self.filesize
		|	self.writeBuffer
		"""
		if self.buffer is not None:
			data = self.buffer+data
			self.buffer = None
		datalength = len(data)
		if self.writeBuffer is None:
			if datalength >= 2:
				length = ((data[0]) << 8)+data[1]
				if datalength >= 2+length:
					file = ""
					for i in range(length):
						file += chr(data[2+i])
					self.filesize = 0
					if datalength >= 2+length+8:
						for i in range(8):
							self.filesize += (data[2+length+i]) << (8*(8-1-i))
						self.writeBuffer = WriteBuffer(self.folder+"/"+file)
						maxlength = min(datalength-(2+length+8), self.filesize)
						ba = bytearray()
						for i in range(maxlength):
							ba.append(data[2+length+8+i])
						self.writeBuffer.write(ba)
						self.filesize -= maxlength
					else:
						self.buffer = data
				else:
					self.buffer = data
			else:
				self.buffer = data
		else:
			length = min(datalength, self.filesize)
			ba = bytearray()
			for i in range(length):
				ba.append(data[i])
			self.writeBuffer.write(ba)
			self.filesize -= length
			if self.filesize == 0:
				self.writeBuffer.close()
				self.writeBuffer = None
				self.write(data[length:])

class ArchiverUnitTest(unittest.TestCase):
	def setUp(self):
		pass

	def tearDown(self):
		pass

	def test_file(self):
		testfolder = "../test"
		srcfile = "../test.txt"
		archivefile = testfolder+"/test.archive"
		dstfile = testfolder+"/test.txt"
		archiver = Archiver(srcfile)
		writebuffer = WriteBuffer(archivefile)
		while True:
			ba = archiver.read()
			if len(ba) == 0:
				break
			writebuffer.write(ba)
		writebuffer.close()
		self.assertTrue(os.path.isfile(archivefile))
		filesize1 = os.stat(srcfile).st_size
		filesize2 = os.stat(archivefile).st_size
		self.assertTrue(filesize1 < filesize2)
		dearchiver = Dearchiver(testfolder)
		readbuffer = ReadBuffer(archivefile)
		while True:
			ba = readbuffer.read()
			if len(ba) == 0:
				break
			dearchiver.write(ba)
		readbuffer.close()
		self.assertTrue(os.path.isfile(dstfile))
		filesize3 = os.stat(dstfile).st_size
		self.assertTrue(filesize1 == filesize3)
		fin1 = open(srcfile, "rb")
		fin2 = open(dstfile, "rb")
		ba1 = fin1.read(filesize1)
		ba2 = fin2.read(filesize3)
		for i in range(filesize1):
			self.assertTrue(ba1[i] == ba2[i])
		fin1.close()
		fin2.close()
		shutil.rmtree(testfolder)

	def test_folder(self):
		testfolder = "../test"
		srcfile = "../test.txt"
		os.makedirs("../test/folder")
		shutil.copy(srcfile, "../test/folder/test1.txt")
		shutil.copy(srcfile, "../test/folder/test2.txt")
		archiver = Archiver("../test/folder")
		archivefile = "../test/folder.archive"
		dstfile1 = "../test/output/folder/test1.txt"
		dstfile2 = "../test/output/folder/test2.txt"
		writebuffer = WriteBuffer(archivefile)
		while True:
			ba = archiver.read()
			if len(ba) == 0:
				break
			writebuffer.write(ba)
		writebuffer.close()
		self.assertTrue(os.path.isfile(archivefile))
		filesize1 = os.stat(srcfile).st_size
		filesize2 = os.stat(archivefile).st_size
		self.assertTrue(filesize1*2 < filesize2)
		dearchiver = Dearchiver("../test/output")
		readbuffer = ReadBuffer(archivefile)
		while True:
			ba = readbuffer.read()
			if len(ba) == 0:
				break
			dearchiver.write(ba)
		readbuffer.close()
		self.assertTrue(os.path.isfile(dstfile1))
		filesize3 = os.stat(dstfile1).st_size
		self.assertTrue(filesize1 == filesize3)
		fin1 = open(srcfile, "rb")
		fin2 = open(dstfile1, "rb")
		ba1 = fin1.read(filesize1)
		ba2 = fin2.read(filesize3)
		for i in range(filesize1):
			self.assertTrue(ba1[i] == ba2[i])
		fin1.close()
		fin2.close()
		self.assertTrue(os.path.isfile(dstfile2))
		filesize3 = os.stat(dstfile2).st_size
		self.assertTrue(filesize1 == filesize3)
		fin1 = open(srcfile, "rb")
		fin2 = open(dstfile2, "rb")
		ba1 = fin1.read(filesize1)
		ba2 = fin2.read(filesize3)
		for i in range(filesize1):
			self.assertTrue(ba1[i] == ba2[i])
		fin1.close()
		fin2.close()
		shutil.rmtree(testfolder)
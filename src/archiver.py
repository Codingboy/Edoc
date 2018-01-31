import os
from src.filebuffer import ReadBuffer, WriteBuffer
from typing import List


class Archiver:
	"""
	Archiver converts files/folders to bytearrays.

	Attributes:
		readBuffer: readBuffer
		files: list of files and folders that need to be processed
		file: path to actual file
		delete: status if the file should be deleted after it is processed
		readSize: number of bytes read in one call

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
		if os.path.isfile(folder):
			self.files = [folder]
		elif os.path.isdir(folder):
			files = os.listdir(folder)
			for file in files:
				file = folder+"/"+file
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
					if os.path.isdir(file):
						folder = file
						files = os.listdir(folder)
						for file in files:
							file = folder+"/"+file
							self.files.append(file)
					elif os.path.isfile(file):
						self.readBuffer = ReadBuffer(file)
						self.file = file
						length = len(file)
						ba.append(length >> 8)
						ba.append(length & 255)
						for c in file:
							ba.append(ord(c))
						filesize = os.stat(file).st_size
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
						length = min(datalength-(2+length+8), self.filesize)
						ba = bytearray()
						for i in range(length):
							ba.append(data[2+length+8+i])
						self.writeBuffer.write(ba)
						self.filesize -= length
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

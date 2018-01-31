import os
from src.filebuffer import ReadBuffer, WriteBuffer


class Archiver:
	def __init__(self, folder, delete=False):
		self.readBuffer = None
		self.files = []
		if os.path.isfile(folder):
			self.files = [folder]
		elif os.path.isdir(folder):
			files = os.listdir(folder)
			for file in files:
				file = folder+"/"+file
				self.files.append(file)
		self.file = ""
		self.delete = delete
		self.readSize = 1024

	def read(self):
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
	def __init__(self, folder):
		self.writeBuffer = None
		self.filesize = 0
		self.buffer = None
		self.folder = folder

	def write(self, data):
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

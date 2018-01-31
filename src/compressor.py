from typing import Dict,Tuple,List


class Compressor:
	"""
	Compressor compresses bytearrays.

	Attributes:
		dict: compression-dictionary
		size: actual size of dict
		maxSize: maximum size of dict
		buffer: buffer for unprocessed data

	Parameters:

	| **Pre:**

	| **Post:**
	|	self.size = 256
	|	self.maxSize = 256*256
	|	self.buffer = None
	"""
	def __init__(self):
		self.dict: Dict[Tuple[int], List[int, int]] = {}
		for i in range(256):
			self.dict[(i,)] = [-1, i]
		self.size: int = 256
		self.maxSize: int = 256*256
		self.buffer: Tuple[int] = None

	def compress(self, data: bytearray) -> bytearray:
		"""
		Compresses data.

		Parameters:
			data: data to be compressed

		Returns:
			compressed data

		| **Modifies:**
		|	data
		|	self.dict
		|	self.size
		|	self.buffer
		"""
		bytemessage = ()
		if self.buffer is not None:
			bytemessage = self.buffer
			self.buffer = None
		returnvalue = bytearray()
		while True:
			if len(data) == 0:
				self.buffer = bytemessage
				break
			bytemessage += (data.pop(0),)
			if bytemessage not in self.dict:
				if self.size == self.maxSize:
					prev = self.dict[bytemessage[:-1]][1]
					ba = bytearray()
					ba.append(prev >> 8)
					ba.append(prev & 255)
					returnvalue += ba
					bytemessage = bytemessage[-1:]
				else:
					prev = self.dict[bytemessage[:-1]][1]
					self.dict[bytemessage] = [prev, self.size]
					self.size += 1
					ba = bytearray()
					ba.append(prev >> 8)
					ba.append(prev & 255)
					ba.append(bytemessage[-1:][0])
					returnvalue += ba
					bytemessage = ()
		return returnvalue

	def close(self):#TODO optimize
		"""
		Compresses data and ensures buffer is empty.

		Parameters:

		Returns:
			compressed data

		| **Modifies:**
		|	self.buffer
		"""
		ba = bytearray()
		if self.buffer is not None:
			bytemessage = self.buffer
			self.buffer = None
			if len(bytemessage) > 0:
				prev = self.dict[bytemessage][1]
				ba.append(prev >> 8)
				ba.append(prev & 255)
		return ba


class Decompressor:
	"""
	Decompressor decompresses bytearrays.

	Attributes:
		uncompressDict: uncompress-dictionary
		size: actual size of dict
		maxSize: maximum size of dict
		buffer: buffer for unprocessed data

	Parameters:

	| **Pre:**

	| **Post:**
	|	self.size = 256
	|	self.maxSize = 256*256
	|	self.buffer = None
	"""
	def __init__(self):
		self.uncompressDict: Dict[int, List[int, Tuple[int]]] = {}
		for i in range(256):
			self.uncompressDict[i] = [-1, (i,)]
		self.size: int = 256
		self.maxSize: int = 256*256
		self.buffer: bytearray = None

	def decompress(self, data: bytearray) -> bytearray:
		"""
		Compresses data.

		Parameters:
			data: data to be compressed

		Returns:
			compressed data

		| **Modifies:**
		|	data
		|	self.dict
		|	self.size
		|	self.buffer
		"""
		if self.buffer is not None:
			data = self.buffer+data
			self.buffer = None
		returnvalue = bytearray()
		while True:
			reqiredlength = 3
			if self.size == self.maxSize:
				reqiredlength = 2
			if len(data) >= reqiredlength:
				ba = bytearray()
				ba.append(data.pop(0))
				ba.append(data.pop(0))
				if self.size == self.maxSize:
					index = (ba[0]) << 8
					index += ba[1]
					bytemessage = self.uncompressDict[index][1]
					for b in bytemessage:
						returnvalue.append(b)
				else:
					ba.append(data.pop(0))
					prev = (ba[0]) << 8
					prev += ba[1]
					bytemessage = self.uncompressDict[prev][1]
					bytemessage += (ba[2],)
					self.uncompressDict[self.size] = [prev, bytemessage]
					self.size += 1
					for b in bytemessage:
						returnvalue.append(b)
			else:
				self.buffer = data
				return returnvalue

	def close(self):
		"""
		Decompresses data and ensures buffer is empty.

		Parameters:

		Returns:
			decompressed data

		| **Modifies:**
		|	self.dict
		|	self.size
		|	self.buffer
		"""
		return self.decompress(bytearray())#TODO optimize

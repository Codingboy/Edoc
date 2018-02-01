from random import randint
from copy import deepcopy
import os
import shutil
import time
import math
import unittest
from typing import Dict, Tuple, List

class Encoder:
	def __init__(self):
		pass
	def encode(self, plain):
		pass

class Decoder:
	def __init__(self):
		pass
	def decode(self, encoded):
		pass

class SBox:
	"""
	SBox is a substitution cipher.

	Attributes:
		encodeMap: lookuptable used to encode data
		decodeMap: lookuptable used to decode data

	Parameters:
		pw: password

	| **Pre:**
	|	len(pw) == 256
	|	pw[i] >= 0
	|	pw[i] < 256

	| **Post:**
	|	len(self.encodeMap) == 256
	|	self.encodeMap[i] >= 0
	|	self.encodeMap[i] < 256
	|	len(self.decodeMap) == 256
	|	self.decodeMap[i] >= 0
	|	self.decodeMap[i] < 256
	"""

	def __init__(self, pw: List[int]):
		self.encodeMap: List[int] = [-1]*256
		self.decodeMap: List[int] = [-1]*256
		index = 0
		for i in range(256):
			emptyCounter = 0
			maxEmpty = 256-i
			targetEmpty = 1+(pw[i]%maxEmpty)
			while (emptyCounter < targetEmpty):
				if (self.encodeMap[index] == -1):
					emptyCounter += 1
				if (emptyCounter < targetEmpty):
					index = (index+1)%256
			self.encodeMap[index] = i
		for i in range(256):
			self.decodeMap[self.encodeMap[i]] = i

	def encode(self, plain: int) -> int:
		"""
		Encodes a single plain number.

		Parameters:
			plain: plain number

		Returns:
			encoded number

		| **Pre:**
		|	plain >= 0
		|	plain < 256

		| **Post:**
		|	return >= 0
		|	return < 256
		"""
		return self.encodeMap[plain]

	def decode(self, encoded: int) -> int:
		"""
		Decodes a single encoded number.

		Parameters:
			encoded: encoded number

		Returns:
			decoded number

		| **Pre:**
		|	encoded >= 0
		|	encoded < 256

		| **Post:**
		|	return >= 0
		|	return < 256
		"""
		return self.decodeMap[encoded]

class PBox:
	"""
	PBox is a transposition cipher.

	Attributes:
		encodeMap: lookuptable used to encode data
		decodeMap: lookuptable used to decode data

	Parameters:
		pw: password

	| **Pre:**
	|	len(pw) == 2048
	|	pw[i] >= 0
	|	pw[i] < 256

	| **Post:**
	|	len(self.encodeMap) == 2048
	|	self.encodeMap[i] >= 0
	|	self.encodeMap[i] < 2048
	|	len(self.decodeMap) == 2048
	|	self.decodeMap[i] >= 0
	|	self.decodeMap[i] < 2048
	"""

	def __init__(self, pw: List[int]):
		self.encodeMap: List[int] = [-1]*(256*8)
		self.decodeMap: List[int] = [-1]*(256*8)
		index = 0
		for i in range(256*8):
			emptyCounter = 0
			maxEmpty = 256*8-i
			targetEmpty = 1+(pw[i]%maxEmpty)
			while (emptyCounter < targetEmpty):
				if (self.encodeMap[index] == -1):
					emptyCounter += 1
				if (emptyCounter < targetEmpty):
					index = (index+1)%(256*8)
			self.encodeMap[index] = i
		for i in range(256*8):
			self.decodeMap[self.encodeMap[i]] = i

	def encode(self, plain: List[int], seed: int) -> List[int]:
		"""
		Encodes a block of plain numbers.

		Parameters:
			plain: block of plain numbers
			seed: seed

		Returns:
			block of encoded numbers

		| **Pre:**
		|	len(plain) == 256
		|	plain[i] >= 0
		|	plain[i] < 256
		|	seed >= 0
		|	seed < 256

		| **Post:**
		|	len(return) == 256
		|	return[i] >= 0
		|	return[i] < 256
		"""
		encoded = [0]*256
		for i in range(256):
			indexVar = i*8+seed
			for b in range(8):
				if ((plain[i]) & (1<<b)):
					index = self.encodeMap[(b+indexVar)%2048]
					index8 = int(index/8)
					encoded[index8] = encoded[index8]+(1<<(index%8))
		return encoded

	def decode(self, encoded: List[int], seed: int) -> List[int]:
		"""
		Decodes a block of encoded numbers.

		Parameters:
			encoded: block of encoded numbers
			seed: seed

		Returns:
			block of decoded numbers

		| **Pre:**
		|	len(encoded) == 256
		|	encoded[i] >= 0
		|	encoded[i] < 256
		|	seed >= 0
		|	seed < 256

		| **Post:**
		|	len(return) == 256
		|	return[i] >= 0
		|	return[i] < 256
		"""
		decoded = [0]*256
		for i in range(256):
			indexVar = i*8
			for b in range(8):
				if ((encoded[i]) & (1<<b)):
					index = self.decodeMap[indexVar+b]-seed
					if (index < 0):
						index += 2048
					index8 = int(index/8)
					decoded[index8] = decoded[index8]+(1<<(index%8))
		return decoded

class SPBox:
	"""
	SPBox is a substitution-permutation network.

	Attributes:
		sBoxes: list of SBoxes used for substitution
		seed: seed
		pBox: PBox used for permutation

	Parameters:
		pw: password
		seed: seed

	| **Pre:**
	|	len(pw) == 4096
	|	pw[i] >= 0
	|	pw[i] < 256
	|	len(seed) == 256
	|	seed[i] >= 1
	|	seed[i] < 256

	| **Post:**
	|	len(self.sBoxes) == 8
	|	len(self.seed) == 256
	|	self.seed[i] >= 1
	|	self.seed[i] < 256
	"""

	def __init__(self, pw: List[int], seed: List[int] = None):
		self.sBoxes: List[SBox] = [None]*8
		if (seed is None):
			seed = [0]*256
			for i in range(256):
				seed[i] = randint(1, 255)
		self.seed: List[int] = deepcopy(seed)
		for s in range(8):
			spw = [0]*256
			for i in range(256):
				spw[i] = pw[s*256+i]
			self.sBoxes[s] = SBox(spw)
		ppw = [0]*2048
		for i in range(2048):
			ppw[i] = pw[8*256+i]
		self.pBox: PBox = PBox(ppw)

	def encodeRound(self, plain: List[int], round: int, pSeed: int) -> List[int]:
		"""
		Encodes a block of plain numbers.

		Parameters:
			plain: block of plain numbers
			round: iteration of encode
			pSeed: seed for PBox

		Returns:
			block of encoded numbers

		| **Pre:**
		|	len(plain) == 256
		|	plain[i] >= 0
		|	plain[i] < 256
		|	round >= 0
		|	round < 8
		|	pSeed >= 0
		|	pSeed < 256

		| **Post:**
		|	len(return) == 256
		|	return[i] >= 0
		|	return[i] < 256
		"""
		encoded = [0]*256
		for i in range(256):
			seedAtI = self.seed[i]
			encoded[i] = plain[i] ^ self.sBoxes[round].encodeMap[i] ^ seedAtI
			for j in range(8):
				if ((seedAtI & (1<<j)) != 0):
					encoded[i] = self.sBoxes[j].encodeMap[
						encoded[i]]  # replacement for SBox.encode() to improve performance
		encoded = self.pBox.encode(encoded, pSeed)
		return encoded

	def decodeRound(self, encoded: List[int], round: int, pSeed: int) -> List[int]:
		"""
		Decodes a block of encoded numbers.

		Parameters:
			encoded: block of encoded numbers
			round: iteration of decode
			pSeed: seed for PBox

		Returns:
			block of decoded numbers

		| **Pre:**
		|	len(encoded) == 256
		|	encoded[i] >= 0
		|	encoded[i] < 256
		|	round >= 0
		|	round < 8
		|	pSeed >= 0
		|	pSeed < 256

		| **Post:**
		|	len(return) == 256
		|	return[i] >= 0
		|	return[i] < 256
		"""
		decoded = self.pBox.decode(encoded, pSeed)
		for i in range(256):
			seedAtI = self.seed[i]
			for invertedJ in range(8):
				j = 8-1-invertedJ
				if ((seedAtI & (1<<j)) != 0):
					decoded[i] = self.sBoxes[j].decodeMap[
						decoded[i]]  # replacement for SBox.decode() to improve performance
			decoded[i] = decoded[i] ^ self.sBoxes[round].encodeMap[i] ^ seedAtI
		return decoded

	def encodeRounds(self, plain: List[int]) -> List[int]:  # TODO rename to encode
		"""
		Encodes a block of plain numbers.

		Parameters:
			plain: block of plain numbers

		Returns:
			block of encoded numbers

		| **Pre:**
		|	len(plain) == 256
		|	plain[i] >= 0
		|	plain[i] < 256

		| **Post:**
		|	len(return) == 256
		|	return[i] >= 0
		|	return[i] < 256

		| **Modifies:**
		|	self.seed[i]
		"""
		pSeed = 0
		for i in range(256):
			pSeed = (pSeed+self.seed[i])%256
		encoded = self.encodeRound(plain, 0, pSeed)
		for i in range(7):
			encoded = self.encodeRound(encoded, i+1, pSeed)
		for i in range(256):
			self.seed[i] = plain[i] ^ self.seed[i]
			if (self.seed[i] == 0):
				self.seed[i] = 1
		return encoded

	def decodeRounds(self, encoded: List[int]) -> List[int]:  # TODO rename to decode
		"""
		Decodes a block of encoded numbers.

		Parameters:
			encoded: block of encoded numbers

		Returns:
			block of decoded numbers

		| **Pre:**
		|	len(encoded) == 256
		|	encoded[i] >= 0
		|	encoded[i] < 256

		| **Post:**
		|	len(return) == 256
		|	return[i] >= 0
		|	return[i] < 256

		| **Modifies:**
		|	self.seed[i]
		"""
		pSeed = 0
		for i in range(256):
			pSeed = (pSeed+self.seed[i])%256
		decoded = self.decodeRound(encoded, 7, pSeed)
		for invertedI in range(7):
			i = 6-invertedI
			decoded = self.decodeRound(decoded, i, pSeed)
		for i in range(256):
			self.seed[i] = decoded[i] ^ self.seed[i]
			if (self.seed[i] == 0):
				self.seed[i] = 1
		return decoded

	def encode(self, plain):  # TODO remove
		"""
		Encodes a block of plain numbers.

		Parameters:
			plain (list): block of plain numbers

		Returns:
			{"length":length, "message":encodedNumbers}: container with encoded numbers

		| **Pre:**
		|	len(plain) > 0
		|	isinstance(plain[i], int)
		|	plain[i] >= 0
		|	plain[i] < 256

		| **Post:**
		|	isinstance(return["message"], list)
		|	len(return["message"]) >= return["length"]
		|	len(return["message"]) % 256 == 0
		|	isinstance(return["message"][i], int)
		|	return["message"][i] >= 0
		|	return["message"][i] < 256

		| **Modifies:**
		|	self.seed[i]
		"""
		length = len(plain)
		while (len(plain)%256 != 0):
			plain.append(randint(0, 255))
		encodedBytes = 0
		encoded = []
		while (encodedBytes < len(plain)):
			plainPart = [0]*256
			for i in range(256):
				plainPart[i] = plain[encodedBytes]
				encodedBytes += 1
			encodedPart = self.encodeRounds(plainPart)
			for i in range(256):
				encoded.append(encodedPart[i])
		return {"length": length, "message": encoded}

	def decode(self, encodedJSON):  # TODO remove
		"""
		Decodes a container with encoded numbers.

		Parameters:
			encodedJSON ({"length":length, "message":encodedNumbers}): container with encoded numbers

		Returns:
			list: block of decoded numbers

		| **Pre:**
		|	isinstance(encodedJSON["message"], list)
		|	len(encodedJSON["message"]) >= encodedJSON["length"]
		|	len(encodedJSON["message"]) % 256 == 0
		|	isinstance(encodedJSON["message"][i], int)
		|	encodedJSON["message"][i] >= 0
		|	encodedJSON["message"][i] < 256

		| **Post:**
		|	len(return) == encodedJSON["length"]
		|	isinstance(return[i], int)
		|	return[i] >= 0
		|	return[i] < 256

		| **Modifies:**
		|	self.seed[i]
		"""
		length = encodedJSON["length"]
		encoded = encodedJSON["message"]
		decodedBytes = 0
		decoded = []
		while (decodedBytes < len(encoded)):
			encodedPart = [0]*256
			for i in range(256):
				encodedPart[i] = encoded[decodedBytes]
				decodedBytes += 1
			decodedPart = self.decodeRounds(encodedPart)
			for i in range(256):
				if (len(decoded) < length):
					decoded.append(decodedPart[i])
				else:
					break
		return decoded

	def getSeed(self):
		"""
		Gets the seed.

		Returns:
			list: block of seed numbers

		| **Post:**
		|	len(return) == 256
		|	isinstance(return[i], int)
		|	return[i] >= 1
		|	return[i] < 256
		"""
		seed = [0]*256
		for i in range(256):
			seed[i] = self.seed[i]
		return seed

	def setSeed(self, seed):
		"""
		Sets the seed.

		Parameters:
			seed (list): block of seed numbers

		| **Pre:**
		|	len(seed) == 256
		|	isinstance(seed[i], int)
		|	seed[i] >= 1
		|	seed[i] < 256

		| **Modifies:**
		|	self.seed[i]
		"""
		for i in range(256):
			self.seed[i] = seed[i]

# TODO change general parameter policy: all parameters may be edited by functions, no deepcopy needed
#TODO change to bytearray
class Edoc:
	"""
	"""

	def __init__(self, pw):
		"""
		"""
		asInt = []
		for i in range(len(pw)):
			asInt.append(ord(pw[i]))
		pwIndex = 0
		while (len(asInt) < 4096):
			asInt.append(ord(pw[pwIndex%len(pw)]))
			pwIndex += 1
		self.spBox = SPBox(asInt)

	def encodeString(self, plain):
		"""
		"""
		plainMessage = []
		for i in range(len(plain)):
			if (ord(plain[i]) > 255):
				plainMessage[i] = ord("?"[0])
				logger.info(ord(plain[i])+" is no valid char")
			else:
				plainMessage[i] = ord(plain[i])
		return self.spBox.encode(plainMessage)

	def decodeString(self, encoded):
		"""
		"""
		decoded = self.spBox.decode(encoded)
		decodedStr = ""
		for i in range(len(decoded)):
			decodedStr += chr(decoded[i])
		return decodedStr

	def encode(self, plain):
		"""
		"""
		seed = [0]*256
		for i in range(256):
			seed[i] = randint(1, 255)
		self.spBox.setSeed(seed)
		return {"seed": seed, "message": self.encodeString(plain)}

	def decode(self, container):
		"""
		"""
		seed = container["seed"]
		encoded = container["message"]
		self.spBox.setSeed(seed)
		return self.decodeString(encoded)

	def encodeFile(self, inFile, outFile):
		"""
		"""
		compressor = Compressor()
		compressor.compressFile(inFile, inFile+".compressed")
		inFile = inFile+".compressed"
		fOut = open(outFile, "wb")
		fOut.write(chr(0).encode("utf-8"))
		size = getSize(inFile)
		self.encodeFileStream(inFile, fOut, size)
		now = time.time()
		logger.info(str(round(size/(now-start)))+" B/s")
		fOut.close()
		os.remove(inFile)

	def encodeFileStream(self, inFile, fOut, targetProgress):  # TODO use buffers
		"""
		"""
		global progress
		seed = [1]*256
		for i in range(256):
			seed[i] = randint(1, 255)
		self.spBox.setSeed(seed)
		fIn = open(inFile, "rb")
		ba = bytearray()
		fileSize = os.stat(inFile).st_size
		for i in range(8):
			ba.append((fileSize>>(8*(8-1-i))) & 0xff)
		fOut.write(ba)
		ba = bytearray()
		for i in range(256):
			ba.append(self.spBox.seed[i])
		fOut.write(ba)
		readSize = 0
		while readSize < fileSize:
			now = time.time()
			end = 0
			if (progress != 0):
				end = targetProgress*(float(now-start)/progress)
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
			end = round(end*10)/10
			print(str(round(progress*1000/targetProgress)/10)+"% "+h+":"+m+":"+s, end="\r")
			n = min(fileSize-readSize, 256)
			progress += n
			data = fIn.read(n)
			asInt = []
			for c in data:
				asInt.append(c)
			output = bytearray()
			encoded = self.spBox.encode(asInt)
			for i in range(256):
				output.append(encoded["message"][i])
			fOut.write(output)
			readSize += n
		fIn.close()

	def decodeFile(self, inFile, outFile):
		"""
		"""
		outFile = outFile+".compressed"
		fIn = open(inFile, "rb")
		ord(fIn.read(1).decode("utf-8")[0])  # 0
		size = getSize(inFile)
		self.decodeFileStream(fIn, outFile, size)
		now = time.time()
		logger.info(str(round(size/(now-start)))+" B/s")
		fIn.close()
		os.remove(inFile)
		compressor = Compressor()
		compressor.decompressFile(outFile, outFile[:-11])

	def decodeFileStream(self, fIn, outFile, targetProgress):  # TODO use buffers
		"""
		"""
		global progress
		fOut = open(outFile, "wb")
		fileSize = 0
		for i in range(8):
			fileSize += (fIn.read(1)[0])<<(8*(8-1-i))
		seed = []
		b = fIn.read(256)
		for c in b:
			seed.append(c)
		self.spBox.setSeed(seed)
		readSize = 0
		while readSize < fileSize:
			now = time.time()
			end = 0
			if (progress != 0):
				end = targetProgress*(float(now-start)/progress)
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
			end = round(end*10)/10
			print(str(round(progress*1000/targetProgress)/10)+"% "+h+":"+m+":"+s, end="\r")
			length = min(fileSize-readSize, 256)
			n = 256
			progress += n
			data = fIn.read(n)
			message = []
			for c in data:
				message.append(c)
			encoded = {"length": length, "message": message}
			decoded = self.spBox.decode(encoded)
			output = bytearray()
			for c in decoded:
				output.append(c)
			fOut.write(output)
			readSize += n
		fOut.close()

	def encodeFolder(self, folder, outFile):
		"""
		"""
		fOut = open(outFile, "wb")
		fOut.write(chr(1).encode("utf-8"))
		size = getSize(folder)
		self.encodeFolderStream(folder, fOut, folder+"/", size)
		now = time.time()
		logger.info(str(round(size/(now-start)))+" B/s")
		fOut.close()
		shutil.rmtree(folder)

	def encodeFolderStream(self, folder, fOut, root, targetProgress):
		"""
		"""
		files = os.listdir(folder)
		for file in files:
			file = folder+"/"+file
			if (os.path.isfile(file)):
				compressor = Compressor()
				compressor.compressFile(file, file+".compressed")
				file = file+".compressed"
				fileName = file[len(root):]
				ba = bytearray()
				ba.append(len(fileName))
				for c in fileName:
					ba.append(ord(c))
				fOut.write(ba)
				self.encodeFileStream(file, fOut, targetProgress)
			elif (os.path.isdir(file)):
				self.encodeFolderStream(file, fOut, root, targetProgress)

	def decodeFolder(self, inFile):
		"""
		"""
		fIn = open(inFile, "rb")
		folder = inFile[0:inFile.rfind(".")]+"/"
		fIn.read(1)[0]  # 1
		size = getSize(inFile)
		self.decodeFolderStream(fIn, folder, size)
		now = time.time()
		logger.info(str(round(size/(now-start)))+" B/s")
		fIn.close()
		os.remove(inFile)

	def decodeFolderStream(self, fIn, root, targetProgress):
		"""
		"""
		while True:
			lengthStr = fIn.read(1)
			if (len(lengthStr) == 0):
				break
			length = lengthStr[0]
			data = fIn.read(length)
			outFile = root
			for c in data:
				outFile += chr(c)
			folder = outFile[0:outFile.rfind("/")]
			if (not os.path.exists(folder)):
				os.makedirs(folder)
			self.decodeFileStream(fIn, outFile, targetProgress)
			compressor = Compressor()
			compressor.decompressFile(outFile, outFile[:-11])

def getSize(folder):
	"""
	"""
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

class SBoxUnitTest(unittest.TestCase):
	def setUp(self):
		self.pw = []
		for i in range(256):
			self.pw.append(randint(0, 255))
		self.sBox = SBox(self.pw)

	def tearDown(self):
		self.pw = None
		self.sBox = None

	def test_simple(self):
		decodedMatches = 0
		encodedMatches = 0
		for i in range(256):
			plain = i
			encoded = self.sBox.encode(plain)
			decoded = self.sBox.decode(encoded)
			if (plain == encoded):
				encodedMatches += 1
			if (plain == decoded):
				decodedMatches += 1
		self.assertTrue(encodedMatches < 256/10)
		self.assertTrue(decodedMatches == 256)

class PBoxUnitTest(unittest.TestCase):
	def setUp(self):
		self.pw = []
		for i in range(2048):
			self.pw.append(randint(0, 255))
		self.pBox = PBox(self.pw)

	def tearDown(self):
		self.pw = None
		self.pBox = None

	def test_simple(self):
		plain = []
		for i in range(256):
			plain.append(randint(0, 255))
		for seed in range(256):
			encoded = self.pBox.encode(plain, seed)
			decoded = self.pBox.decode(encoded, seed)
			decodedMatches = 0
			encodedMatches = 0
			for i in range(256):
				if (plain[i] == encoded[i]):
					encodedMatches += 1
				if (plain[i] == decoded[i]):
					decodedMatches += 1
			self.assertTrue(encodedMatches < 256/10)
			self.assertTrue(decodedMatches == 256)

class SPBoxUnitTest(unittest.TestCase):
	def setUp(self):
		self.pw = []
		for i in range(4096):
			self.pw.append(randint(0, 255))
		self.spBox = SPBox(self.pw)

	def tearDown(self):
		self.pw = None
		self.spBox = None

	def test_simple(self):
		plain = []
		for i in range(randint(1, 256)):
			plain.append(randint(0, 255))
		length = len(plain)
		seed = self.spBox.getSeed()
		for i in range(256):
			self.assertTrue(self.spBox.seed[i] != 0)
		encoded = self.spBox.encode(plain)
		for i in range(256):
			self.assertTrue(self.spBox.seed[i] != 0)
		seed2 = self.spBox.getSeed()
		self.spBox.setSeed(seed)
		decoded = self.spBox.decode(encoded)
		decodedMatches = 0
		seedMatches = 0
		for i in range(256):
			if (seed[i] == seed2[i]):
				seedMatches += 1
		for i in range(length):
			if (plain[i] == decoded[i]):
				decodedMatches += 1
		self.assertTrue(decodedMatches == length)  # TODO encodeMatches
		self.assertTrue(seedMatches < 256/10)

# TODO encode 2nd batch#plain is edited

class EdocUnitTest(unittest.TestCase):
	def setUp(self):
		self.pw = ""
		for i in range(randint(1, 4096)):
			self.pw += chr(randint(0, 255))
		self.edoc = Edoc(self.pw)

	def tearDown(self):
		self.pw = None
		self.edoc = None

	def test_simple(self):
		plain = ""
		for i in range(randint(1, 256*4*16)):
			plain += chr(randint(0, 255))
		encoded1 = self.edoc.encode(plain)
		encoded2 = self.edoc.encode(plain)
		decoded1 = self.edoc.decode(encoded1)
		decoded2 = self.edoc.decode(encoded2)
		decodedMatches = 0
		for i in range(len(plain)):
			if (plain[i] == decoded1[i]):
				decodedMatches += 1
			if (plain[i] == decoded2[i]):
				decodedMatches += 1
		self.assertTrue(decodedMatches == 2*len(plain))  # TODO encodeMatches
		self.assertTrue(len(decoded1) == len(plain))
		self.assertTrue(len(decoded2) == len(plain))
from random import randint
from copy import deepcopy
import unittest
from typing import Dict, Tuple, List

class Encoder:
	def __init__(self, pw: str):
		password = []
		for c in pw:
			password.append(ord(c))
		index = 0
		while len(password) < 4096:
			password += ord(pw[index%len(pw)])
			index += 1
		self.spBox = SPBox(password)
		self.buffer = None
		self.seeded = False
	def encode(self, plain: bytearray):
		returnvalue = bytearray
		if self.buffer is not None:
			plain = self.buffer+plain
			self.buffer = None
		if (not self.seeded):
			ba = self.spBox.getSeed()
			returnvalue.extend(ba)
			self.seeded = True
		while len(plain) >= 256:
			ba = bytearray()
			for i in range(256):
				ba.append(plain.pop(0))
			encoded = self.spBox.encode(ba)
			returnvalue.extend(encoded)
		if len(plain) > 0:
			self.buffer = plain
		return returnvalue
	def close(self):
		while len(self.buffer) < 256:
			self.buffer.append(randint(0, 255))
		return self.encode(bytearray())

class Decoder:
	def __init__(self, pw: str, seed: bytearray=None):
		password = []
		for c in pw:
			password.append(ord(c))
		index = 0
		while len(password) < 4096:
			password += ord(pw[index%len(pw)])
			index += 1
		self.spBox = SPBox(password, seed)
		self.buffer = None
		self.seeded = False
	def decode(self, encoded: bytearray):
		returnvalue = bytearray
		if self.buffer is not None:
			encoded = self.buffer+encoded
			self.buffer = None
		while len(encoded) >= 256:
			ba = bytearray()
			for i in range(256):
				ba.append(encoded.pop(0))
			if (self.seeded):
				decoded = self.spBox.decode(ba)
				returnvalue.extend(decoded)
			else:
				self.spBox.setSeed(ba)
				self.seeded = True
		if len(encoded) > 0:
			self.buffer = encoded
		return returnvalue
	def close(self):
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

	| **Post:**
	|	len(self.encodeMap) == 256
	|	self.encodeMap[i] >= 0
	|	self.encodeMap[i] < 256
	|	len(self.decodeMap) == 256
	|	self.decodeMap[i] >= 0
	|	self.decodeMap[i] < 256
	"""

	def __init__(self, pw: bytearray):
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

	| **Post:**
	|	len(self.encodeMap) == 2048
	|	self.encodeMap[i] >= 0
	|	self.encodeMap[i] < 2048
	|	len(self.decodeMap) == 2048
	|	self.decodeMap[i] >= 0
	|	self.decodeMap[i] < 2048
	"""

	def __init__(self, pw: bytearray):
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

	def encode(self, plain: bytearray, seed: int) -> bytearray:
		"""
		Encodes a block of plain numbers.

		Parameters:
			plain: block of plain numbers
			seed: seed

		Returns:
			block of encoded numbers

		| **Pre:**
		|	len(plain) == 256
		|	seed >= 0
		|	seed < 256

		| **Post:**
		|	len(return) == 256
		|	return[i] >= 0
		|	return[i] < 256
		"""
		encoded = bytearray(256)
		for i in range(256):
			indexVar = i*8+seed
			for b in range(8):
				if ((plain[i]) & (1<<b)):
					index = self.encodeMap[(b+indexVar)%2048]
					index8 = int(index/8)
					encoded[index8] = encoded[index8]+(1<<(index%8))
		return encoded

	def decode(self, encoded: bytearray, seed: int) -> List[int]:
		"""
		Decodes a block of encoded numbers.

		Parameters:
			encoded: block of encoded numbers
			seed: seed

		Returns:
			block of decoded numbers

		| **Pre:**
		|	len(encoded) == 256
		|	seed >= 0
		|	seed < 256

		| **Post:**
		|	len(return) == 256
		|	return[i] >= 0
		|	return[i] < 256
		"""
		decoded = bytearray(256)
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
	|	len(seed) == 256
	|	seed[i] >= 1

	| **Post:**
	|	len(self.sBoxes) == 8
	|	len(self.seed) == 256
	|	self.seed[i] >= 1
	"""

	def __init__(self, pw: bytearray, seed: bytearray = None):
		self.sBoxes: List[SBox] = [None]*8
		if (seed is None):
			seed = bytearray(256)
			for i in range(256):
				seed[i] = randint(1, 255)
		self.seed: bytearray = seed
		for s in range(8):
			spw = bytearray(256)
			for i in range(256):
				spw[i] = pw[s*256+i]
			self.sBoxes[s] = SBox(spw)
		ppw = bytearray(2048)
		for i in range(2048):
			ppw[i] = pw[8*256+i]
		self.pBox: PBox = PBox(ppw)

	def encodeRound(self, plain: bytearray, round: int, pSeed: int) -> bytearray:
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
		|	round >= 0
		|	round < 8
		|	pSeed >= 0
		|	pSeed < 256

		| **Post:**
		|	len(return) == 256
		"""
		encoded = bytearray(256)
		for i in range(256):
			seedAtI = self.seed[i]
			encoded[i] = plain[i] ^ self.sBoxes[round].encodeMap[i] ^ seedAtI
			for j in range(8):
				if ((seedAtI & (1<<j)) != 0):
					encoded[i] = self.sBoxes[j].encodeMap[
						encoded[i]]  # replacement for SBox.encode() to improve performance
		encoded = self.pBox.encode(encoded, pSeed)
		return encoded

	def decodeRound(self, encoded: bytearray, round: int, pSeed: int) -> bytearray:
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
		|	round >= 0
		|	round < 8
		|	pSeed >= 0
		|	pSeed < 256

		| **Post:**
		|	len(return) == 256
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

	def encode(self, plain: bytearray) -> bytearray:
		"""
		Encodes a block of plain numbers.

		Parameters:
			plain: block of plain numbers

		Returns:
			block of encoded numbers

		| **Pre:**
		|	len(plain) == 256

		| **Post:**
		|	len(return) == 256

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

	def decode(self, encoded: bytearray) -> bytearray:
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

	def getSeed(self) -> bytearray:
		"""
		Gets the seed.

		Returns:
			block of seed numbers

		| **Post:**
		|	len(return) == 256
		|	return[i] >= 1
		"""
		seed = bytearray(256)
		for i in range(256):
			seed[i] = self.seed[i]
		return seed

	def setSeed(self, seed: bytearray):
		"""
		Sets the seed.

		Parameters:
			seed: block of seed numbers

		| **Pre:**
		|	len(seed) == 256
		|	seed[i] >= 1

		| **Modifies:**
		|	self.seed[i]
		"""
		for i in range(256):
			self.seed[i] = seed[i]

# TODO change general parameter policy: all parameters may be edited by functions, no deepcopy needed
#TODO change to bytearray

class SBoxUnitTest(unittest.TestCase):
	def setUp(self):
		self.pw = bytearray()
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
		self.pw = bytearray()
		for i in range(2048):
			self.pw.append(randint(0, 255))
		self.pBox = PBox(self.pw)

	def tearDown(self):
		self.pw = None
		self.pBox = None

	def test_simple(self):
		plain = bytearray()
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
		self.pw = bytearray()
		for i in range(4096):
			self.pw.append(randint(0, 255))
		self.spBox = SPBox(self.pw)

	def tearDown(self):
		self.pw = None
		self.spBox = None

	def test_simple(self):
		plain = bytearray()
		for i in range(256):
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
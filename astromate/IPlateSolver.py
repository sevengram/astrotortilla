"IPlateSolver - Plate Solver interface"

from units import Coordinate, Separation
from Configurations import Configurable

class Solution(object):
	"Plate solver solution"
	def __init__(self, center, rotation, parity, hFOV, vFOV, wcsInfo=None):
		if not isinstance(center, Coordinate):
			raise TypeError("Invalid arguments, expected Coordinate")
		self.__center = center
		self.__rotation = float(rotation)
		self.__parity = parity
		self.__vFOV = float(vFOV)
		self.__hFOV = float(hFOV)
		if wcsInfo: self.__wcsInfo = wcsInfo
		else: self.__wcsInfo = {}

	def __repr__(self):
		return "Solution(%s, %f, %d, %f, %f)"%(self.__center, self.__rotation, self.__parity, self.__hFOV, self.__vFOV)

	@property
	def center(self):
		return self.__center

	@property
	def rotation(self):
		return self.__rotation

	@property
	def parity(self):
		return self.__parity

	@property
	def fieldOfView(self):
		return self.__hFOV, self.__vFOV

	@property
	def wcsInfo(self):
		return self.__wcsInfo

class IPlateSolver(Configurable):
	"""Plate solver interface
Properties:
bool hasSolution ro
Solution solution ro
int timeout rw

Functions:
bool solve(imagePath, target=None, minFOV=0.1, maxFOV=180.0)
reset()
"""
	@property
	def hasSolution():
		"bool - is a solution available"
		return False

	@property
	def solution(self):
		"Get current solution or None if not available"
		return None

	@property
	def timeout(self):
		return 0

	@timeout.setter
	def timeout(self, value):
		pass
	
	def solve(self, imagePath, target=None, targetRadius=3, minFOV=0.1, maxFOV=180.0, callback=None):
		"Do plate solving for image, return True on success"
		return False

	def reset(self):
		"Reset current state"
		pass

	def abort(self):
		"Abort on-going solver is possible"
		pass

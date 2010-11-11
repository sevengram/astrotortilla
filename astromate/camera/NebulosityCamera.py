"""NebulosityCamera
- simple camera interface to Nebulosity 2
"""

from ..ICamera import ICamera
from .. import CameraState
import tempfile, shutil
import os.path, os
import socket, glob, time

CAMERAS = (
		"No Camera",
		"Simulator",
		"Starlight Xpress USB",
		"ASCOM Camera",
		)

PROPERTYLIST = {
		"port":("Nebulosity ListenPort", int, "", "", 4301),
		}

class NebulosityCamera(ICamera):
	"""NebulosityCamera()
	Create NebulosityCamera and connect to Nebulosity 2.3.3 or
	newer. Use a Nebulosity2 script with the line "ListenPort 4301"
	to listen to port 4301.
	Default "port" property value is 4301.
	"""
	def __init__(self):
		super(NebulosityCamera, self).__init__()
		self.__camera = None
		self.__sock = None
		self.__bin = 1
		self.__basename = "Capture"
		self.propertyList = PROPERTYLIST
		self.__autoDisco = True

	def __del__(self):
		if self.__sock:
			self.__sock.send("ListenPort 0\n".encode())
			self.__sock.recv(1)
			self.__sock.close()
			del self.__sock
		try:
			map(os.remove, glob.glob(os.path.join(self.workingDirectory, self.__basename+"*.fit")))
		except:
			pass
		super(NebulosityCamera, self).__del__()
	
	def __cmd(self, cmd):
		if not self.__sock:
			try:
				self.connected = True
			except:
				raise IOError("Not connected")
		self.__sock.send(cmd.encode())
		self.__sock.send("\n".encode())

	@property
	def imageTypes(self):
		"List of image types supported by the camera"
		return ["fit"]

	@property
	def cameraList(self):
		"List of cameras supported if one must be pre-selected"
		return CAMERAS

	@property
	def camera(self):
		"Current camera if multiple options"
		return self.__camera

	@camera.setter
	def camera(self, value):
		"Set current camera value or None for no change"
		if value in CAMERAS or value is None:
			self.__camera = value
			if self.__camera:
				self.__cmd("ConnectName %s"%self.__camera)
		else:
			raise NameError("'%s' is not a known camera"%str(value))

	@property
	def connected(self):
		return self.__sock != None

	@connected.setter
	def connected(self, value):
		if value == True:
			if self.__sock:
				return
			try:
				self.__sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				self.__sock.connect(("127.0.0.1", self.getProperty("port")))
				if self.__camera:
					self.__cmd("ConnectName %s"%self.__camera)
			except:
				self.__sock = None
				raise IOError("Connection failed")
		else:
			if self.__sock == None:
				return
			self.__cmd("ListenPort 0")
			# Wait for Nebulosity to close the socket first
			self.__sock.recv(1)
			self.__sock.close()
			del self.__sock
			self.__sock = None
	
	@property
	def canAutoConnect(self):
		return True

	@property
	def disconnectAfterCapture(self):
		return self.__autoDisco

	@disconnectAfterCapture.setter
	def disconnectAfterCapture(self, value):
		self.__autoDisco = value == True

	@property
	def binning(self):
		"Current binning setting"
		return self.__bin

	@binning.setter
	def binning(self, bin):
		"Set bin value, 1<= `bin` <= `maxBin`"
		if (1 <= bin <= maxBin):
			raise ValueError("bin value must be 1 <= value < maxBin")
		self.__bin = int(bin)
		self.__cmd("SetBinning %d"%(self.__bin-1))

	@property
	def maxBin(self):
		"Maximum supported binning level"
		return 4


	@property
	def cameraState(self):
		"Current camera state, see ASCOM cameraState parameter"
		return CameraState.Idle

	@property
	def errorMessage(self):
		return None


	@property
	def cameraXSize(self):
		"Image width, 0 if not known"
		return 0

	@property
	def cameraYSize(self):
		"Image width, 0 if not known"
		return 0

	@property
	def imageReady(self):
		"Returns True if a captured image is available"
		return len(glob.glob(os.path.join(self.workingDirectory, self.__basename+"*.fit"))) > 0
	
	def capture(self, duration):
		"Starts image exposure, no returned value"
# clear temp directory first
		try:
			map(os.remove, glob.glob(os.path.join(self.workingDirectory, self.__basename+"*.fit")))
		except Exception as detail:
			raise IOError("Failed to clear cache: %s"%detail)

		if not self.connected:
			self.connected = True

		self.__cmd("SetDuration %d"%(int(duration*1000)))
		self.__cmd("SetDirectory %s"%self.workingDirectory)
		self.__cmd("SetName %s"%(self.__basename))
		self.__cmd("Capture 1")
		if self.__autoDisco:
			self.connected = False


	def getImage(self):
		"Returns None or path to image"
		if self.imageReady:
			return glob.glob(os.path.join(self.workingDirectory, self.__basename+"*.fit"))[-1]
		else:
			return None

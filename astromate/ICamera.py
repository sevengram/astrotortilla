"""ICamera
- simple camera interface
"""

import tempfile, shutil
import os.path
import CameraState
from Configurations import Configurable

class ICamera(Configurable):
	def __init__(self):
		super(ICamera, self).__init__()
		self.__wd = tempfile.mkdtemp(prefix="cam")
	
	def __del__(self):
		try:
			shutil.rmtree(self.__wd)
		except:
			pass

	@property
	def imageTypes(self):
		"List of image types supported by the camera"
		return []

	@property
	def needsCameraName(self):
		"True if cannot capture until a camera is chosen from list"
		return False

	@property
	def cameraList(self):
		"List of cameras supported if one must be pre-selected"
		return []

	@property
	def camera(self):
		"Current camera if multiple options"
		return None

	@camera.setter
	def camera(self, value):
		"Set current camera value or None for no change"
		return

	@property
	def hasSetupDialog(self):
		"True if calling setup() function brings up a separate dialog"
		return False

	def setup(self):
		"Placeholder for Dialog invocation"
		pass

	@property
	def connected(self):
		"Is camera connected?"
		return False

	@connected.setter
	def connected(self, value):
		"Connect/Disconnect"
		return

	@property
	def canAutoConnect(self):
		"Can the camera automatically connect before capture"
		return False

	@property
	def disconnectAfterCapture(self):
		"Does the camera disconnect after each capture"
		return False

	@property
	def binning(self):
		"Current binning setting"
		return 1

	@binning.setter
	def binning(self, bin):
		return

	@property
	def maxBin(self):
		return 1


	@property
	def cameraState(self):
		"Current camera state, see ASCOM cameraState parameter"
		return CameraState.Error

	@property
	def errorMessage(self):
		"Last error message from camera"
		return "Camera not implemented"

	@property
	def cameraXSize(self):
		return 0

	@property
	def cameraYSize(self):
		return 0

	@property
	def imageReady(self):
		return False
	
	@property
	def workingDirectory(self):
		return self.__wd
	
	@workingDirectory.setter
	def workingDirectory(self, value):
		"Changes current WD, old WD is not deleted."
		if os.path.isdir(value):
			self.__wd = value
		else:
			raise ValueError("value is not a path to a directory")

	def capture(self, duration):
		"Starts image exposure, no returned value"
		return

	def getImage(self):
		"Returns None or path to image"
		return None

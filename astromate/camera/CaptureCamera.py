"""CaptureCamera
- simple camera interface to screen capture based imaging
"""

from ..ICamera import ICamera
from .. import CameraState
import tempfile, shutil
import os.path, os
import glob, time, re
import win32ui, win32api, win32con
try:
	import winxpgui as win32gui
except:
	import win32gui
import Image


"""dict of properties
Each property is structured in a tuple:
handle: (name, validation-func, help, value help, default)
	handle = string, internal name of property
	name = string, human understandable name of property
	validation-func = function(param) or None, new value is accepted is function returns without exceptions
	help = tool-tip for the value
	value help = tool-tip for the value entry
	default = default value (not necessarily current)"""

PROPERTYLIST = {
	"leftmargin":("Left margin", int, "", "", 3),
	"rightmargin":("Right margin", int, "", "", 48),
	"topmargin":("Top margin", int, "", "", 49),
	"bottommargin":("Bottom margin", int, "", "", 70),
	"classname":("Window class", re.compile, "Regex match filter", "", ".*"),
	"windowtitle":("Window title", re.compile, "Regex match filter", "", "^PHD Guiding.*"),
		}

def _hwndCallback(hwnd, extra):
	extra.append((hwnd,
		win32gui.GetWindowText(hwnd),
		win32gui.GetClassName(hwnd)
		))

class CaptureCamera(ICamera):
	"""CaptureCamera()
	Create CaptureCamera 
	"""
	def __init__(self):
		super(CaptureCamera, self).__init__()
		self.__basename = "Capture"
		self.__windowList = []
		self.__bin = 1
		self.__camera = None
		self.__cameraName = None
		self.propertyList = PROPERTYLIST
	
	def __del__(self):
		super(CaptureCamera, self).__del__()
	
	@property
	def imageTypes(self):
		"List of image types supported by the camera"
		return ["jpg"]

	@property
	def cameraList(self):
		"List of cameras supported if one must be pre-selected"
		hwndList = []
		win32gui.EnumWindows(_hwndCallback, hwndList)
		winTitle = re.compile(self.getProperty("windowtitle"))
		className = re.compile(self.getProperty("classname"))
		self.__windowList = [elem for elem in hwndList if className.match(elem[2]) and winTitle.match(elem[1])]
		titles = [elem[1] for elem in self.__windowList]
		return titles

	@property
	def needsCameraName(self):
		return True

	@property
	def camera(self):
		"Current camera if multiple options"
		if self.__cameraName:
			return self.__cameraName
		else:
			return None

	@camera.setter
	def camera(self, value):
		"Set current camera value or None for no change"
		if value is None:
			self.__camera = None
			self.__cameraName = None
		elif value in self.cameraList:
			self.__camera = filter(lambda x, title=value: x[1]==title, self.__windowList)[0]
			self.__cameraName = value
		else:
			raise NameError("'%s' is not a known window"%str(value))

	@property
	def connected(self):
		"TODO: Returns true if selected window is visible"
		return True

	@connected.setter
	def connected(self, value):
		return

	@property
	def binning(self):
		"Current binning setting"
		return self.__bin

	@binning.setter
	def binning(self, bin):
		"Set bin value, 1<= `bin` <= `maxBin`"
		if (1 <= bin <= self.maxBin):
			raise ValueError("bin value must be 1 <= value < maxBin")
		self.__bin = int(bin)

	@property
	def maxBin(self):
		"Maximum supported binning level"
		return 1


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
		return len(glob.glob(os.path.join(self.workingDirectory, self.__basename+".jpg"))) > 0
	
	def capture(self, duration):
		"Starts image exposure, waits `duration` seconds before window capture, no returned value"
# clear temp directory first
		try:
			map(os.remove, glob.glob(os.path.join(self.workingDirectory, self.__basename+".jpg")))
		except Exception as detail:
			raise IOError("Failed to clear cache: %s"%detail)

		if not self.connected:
			raise ValueError("Not connected")

		hwnd = self.__camera[0]
		win32gui.ShowWindow(hwnd,win32con.SW_RESTORE)
		win32gui.SetForegroundWindow(hwnd)
		time.sleep(duration)
		l,t,r,b=win32gui.GetWindowRect(hwnd)
		lm = int(self.getProperty("leftmargin"))
		rm = int(self.getProperty("rightmargin"))
		tm = int(self.getProperty("topmargin"))
		bm = int(self.getProperty("bottommargin"))

		h=b-t-(tm+bm)
		w=r-l-(rm+lm)

		hwndDC = win32gui.GetWindowDC(hwnd)
		mfcDC=win32ui.CreateDCFromHandle(hwndDC)
		saveDC=mfcDC.CreateCompatibleDC()
		saveBitMap = win32ui.CreateBitmap()
		saveBitMap.CreateCompatibleBitmap(mfcDC, w, h)
		saveDC.SelectObject(saveBitMap)
		saveDC.BitBlt((0,0),(w, h) , mfcDC, (lm,tm), win32con.SRCCOPY)
		jpgname = os.path.join(self.workingDirectory, self.__basename+".jpg")
		bmpstr = saveBitMap.GetBitmapBits(True)
		bmpinfo = saveBitMap.GetInfo()
 
		im = Image.frombuffer('RGB', (bmpinfo['bmWidth'], bmpinfo['bmHeight']), bmpstr, 'raw', 'BGRX', 0, 1)
		im.save(jpgname, format = 'jpeg', quality = 85)
		saveDC.DeleteDC()
		win32gui.DeleteObject(saveBitMap.GetHandle())


		return

	def getImage(self):
		"Returns None or path to image"
		if self.imageReady:
			return glob.glob(os.path.join(self.workingDirectory, self.__basename+".jpg"))[-1]
		else:
			return None

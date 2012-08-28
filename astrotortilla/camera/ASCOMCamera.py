# vim:st=4 sts=4 sw=4 et si
"ASCOM camera interface"

import logging
logger = logging.getLogger("astrotortilla.ASCOMCamera")

from ..ICamera import ICamera
from .. import CameraState
from win32com.client import Dispatch
from array import array
import Image, os, os.path

import gettext
t = gettext.translation('astrotortilla', 'locale', fallback=True)
_ = t.gettext


# Property dict structure:
# key: (readable name, validation function, name tooltip, value tooltip, default value)
# The values can be set as strings by the using application.
PROPERTYLIST = {
        "lastCamera":(_("Default camera"), str, "", "", "")
        }
class ASCOMCamera(ICamera):
    """ASCOMCamera()
    """
    def __init__(self):
        super(ASCOMCamera, self).__init__()
        self.propertyList = PROPERTYLIST
        self.__initChooser()
        self.__bin = 1
        self.__camname = None
        self.__cam = None
        self.__camState = CameraState.Idle
        self.propertyList = PROPERTYLIST

    def __initChooser(self):
        self.__chooser = None
        try:
            self.__chooser = Dispatch("DriverHelper.Chooser")
        except: pass
        try:
            self.__chooser = Dispatch("Utilities.Chooser")
        except: pass
        try:
            self.__chooser = Dispatch("ASCOM.Utilities.Chooser")
        except: pass

        if self.__chooser:
            self.__chooser.DeviceType = "Camera"

    def __del__(self):
        del self.__chooser
        del self.__cam
        super(ASCOMCamera, self).__del__()

    @classmethod
    def getName(cls):
        return "ASCOM Camera"

    @property
    def imageTypes(self):
        "List of image types supported by the camera"
        return ["jpg"]

    @property
    def hasSetupDialog(self):
        return True

    def setup(self):
        if self.__cam:
            try:
                self.__cam.SetupDialog()
            except:
                logger.info("Could not show Setup Dialog")
                pass
    
    def connect(self):
        if self.__cam:
            if self.__cam.Connected:
                return
            else:
                self.__cam.Connected = True
                return
        if not self.__camname:
            self.__initChooser()
            if not self.__chooser:
                raise Exception("Failed to initialize ASCOM device chooser")
            self.__camname = self.__chooser.Choose(self.getProperty("lastCamera"))
            if not self.__camname: # End-user cancel
                self.__camname = None
                return
        self.setProperty("lastCamera", self.__camname)
        self.__cam = Dispatch(self.__camname)
        if not self.__cam:
            raise Exception("Dispatching %s failed"%self.__camname)
        self.__cam.Connected=True


    @property
    def binning(self):
        "Current binning setting"
        return self.__bin

    @binning.setter
    def binning(self, bin):
        "Set bin value, 1<= `bin` <= `maxBin`"
        if not (1 <= bin <= self.maxBin):
            raise ValueError("bin value must be 1 <= value < maxBin")
        self.__bin = int(bin)

    @property
    def maxBin(self):
        "Maximum supported binning level"
        if self.__cam:
            return self.__cam.MaxBinX
        else:
            return 1

    @property
    def connected(self):
        if not self.__cam:
            return False
        return self.__cam.Connected

    @connected.setter
    def connected(self, value):
        if value == self.connected:
            return
        self.connect()
        if not self.__cam:
            return
        self.__cam.Connected = value

    @property
    def cameraState(self):
        "Current camera state, see ASCOM cameraState parameter"
        if self.__cam:
            return self.__cam.CameraState
        return self.__camState

    @property
    def errorMessage(self):
        "Last error message from camera"
        if not self.connected:
            return _("Not connected")
        return None
    
    def capture(self, duration):
        self.__camState = CameraState.Exposing
        try:
            self.connect()
            self.__cam.BinX = self.__bin
            self.__cam.BinY = self.__bin
            self.__cam.StartExposure(duration, True)
        except:
            self.__camState = CameraState.Error

    @property
    def imageReady(self):
        if not self.__cam:
            return False
        return self.__cam.ImageReady

    def getImage(self):
        self.connect()
        if not self.__cam.ImageReady:
            return None
        self.__camState = CameraState.Idle
        imgName = os.path.join(self.workingDirectory, "ASCOM.png")
        tup = self.__cam.ImageArray
# HACK the column major data to be correct
        iwidth = len(tup)
        iheight = len(tup[0])
        if self.__cam.MaxADU < 256:
            data = array("B")
        else:
            data = array("L")
        for y in xrange(iheight):
            for x in xrange(iwidth):
                data.append(tup[x][y])
        if self.__cam.MaxADU < 256:
            mode = "L"
        else:
            mode = "I"
        img = Image.new(mode, (iwidth, iheight), 0)
        img.fromstring(data.tostring())
        img.save(imgName,format="PNG")
        return imgName

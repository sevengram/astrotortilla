# vim:st=4 sts=4 sw=4 et si
"Maxim DL Camera interface"

from ..ICamera import ICamera
from .. import CameraState
from win32com.client import Dispatch
import os, os.path

import gettext
t = gettext.translation('astrotortilla', 'locale', fallback=True)
_ = t.gettext


# Property dict structure:
# key: (readable name, validation function, name tooltip, value tooltip, default value)
# The values can be set as strings by the using application.
PROPERTYLIST = {
        "filter":(_("Filter"), int, _("Filter index for plate solve capture"), _("-1 for none"), "0"),
    }

class MaximDLCamera(ICamera):
    def __init__(self):
        super(MaximDLCamera, self).__init__()
        self.__bin = 1
        #self.__app = None
        self.__cam = None
        self.__camState = CameraState.Idle
        self.propertyList = PROPERTYLIST
    
    def __del__(self):
        del self.__cam
        super(MaximDLCamera, self).__del__()
    
    @property
    def imageTypes(self):
        return ["jpg", "fit"]

    @property
    def hasSetupDialog(self):
        return False

    def connect(self):
        if self.__cam:
            if self.__cam.LinkEnabled:
                return
            else:
                self.__cam.LinkEnabled = True
                return
        self.__cam = Dispatch("Maxim.CCDCamera")
        if not self.__cam:
            raise Exception(_("Dispatching Maxim.CCDCamera failed"))
        self.__cam.LinkEnabled = True
        self.__cam.DisableAutoShutdown = True
        

    @property
    def binning(self):
        return self.__bin

    @binning.setter
    def binning(self, bin):
        "Set bin value, 1 <= `bin` <= `maxBin`"
        if not (1 <= bin <= self.maxBin):
            raise ValueError("bin value must be 1..maxBin")
        self.__bin = int(bin)

    @property
    def maxBin(self):
        "Maximum supported binning level"
        if self.__cam:
            return self.__cam.MaxBinX
        else:
            return 64

    @property
    def connected(self):
        if not self.__cam:
            return False
        return self.__cam.LinkEnabled

    @connected.setter
    def connected(self, value):
        if value == self.connected:
            return
        self.connect()
        if not self.__cam:
            return
        self.__cam.LinkEnabled = value

    @property
    def cameraState(self):
        "Current camera state, see ASCOM cameraState parameter"
        if self.__cam:
            state = self.__cam.CameraStatus
            if state == 2: return CameraState.Idle
            if state == 7 or state == 8 or state == 15 or state ==20: return CameraState.Waiting
            if state == 3: return CameraState.Exposing
            if state == 4: return CameraState.Reading
            if state == 5: return CameraState.Downloading
            if state == 1: return CameraState.Error
        return self.__camState # Idle?

    @property 
    def errorMessage(self):
        "Last error message from camera"
        if not self.connected:
            return "Not connected"
        return None

    def capture(self, duration):
        self.__camState = CameraState.Exposing
        try:
            self.connect()
            self.__cam.BinX = self.__bin
            self.__cam.BinY = self.__bin
            if self.getProperty("filter") != "-1":
                self.__cam.Expose(duration, 1, int(self.getProperty("filter")))
            else:
                self.__cam.Expose(duration, 1) # 1 for lightframe
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
        #imgName = os.path.join(self.workingDirectory, "Maxim.jpg")
        imgName = os.path.join(self.workingDirectory, "Maxim.fit")
        doc = self.__cam.Document
        #doc.SaveFile(imgName, 6, True) # jpg, auto stretch
        doc.SaveFile(imgName, 3, True, 1) # fits, auto stretch
        return imgName


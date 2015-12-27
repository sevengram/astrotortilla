"""
FileOpenCamera - simple camera interface to read a file from disc
"""

import os
import wx
import gettext

from ..ICamera import ICamera
from .. import CameraState

t = gettext.translation('astrotortilla', 'locale', fallback=True)
_ = t.gettext

PROPERTYLIST = {
    "directory": (_("Directory"), str, "", "", "")
}


class FileOpenCamera(ICamera):
    """
    FileOpenCamera()
    Create FileOpenCamera 
    """

    def __init__(self):
        super(FileOpenCamera, self).__init__()
        self.__openedFile = None
        self.__bin = 1
        self.__selected = False
        if PROPERTYLIST:
            self.propertyList = PROPERTYLIST

    def __del__(self):
        super(FileOpenCamera, self).__del__()

    @classmethod
    def getName(cls):
        return _("File Open dialog")

    @property
    def imageTypes(self):
        """List of image types supported by the camera"""
        return ["fits", "fit", "jpg", "tiff", "tif", "pnm"]

    @property
    def cameraList(self):
        return None

    @property
    def needsCameraName(self):
        return False

    @property
    def camera(self):
        """Current camera if multiple options"""
        return None

    @property
    def hasSetupDialog(self):
        return True

    def setup(self):
        """No settings available at the moment"""
        return

    @property
    def connected(self):
        """Nothing to connect to"""
        return True

    @connected.setter
    def connected(self, value):
        return

    @property
    def binning(self):
        """Current binning setting"""
        return self.__bin

    @binning.setter
    def binning(self, _bin):
        """Set bin value, 1 <= bin <= maxBin"""
        if not (1 <= _bin <= self.maxBin):
            raise ValueError("bin value must be 1 <= value < maxBin")
        self.__bin = int(_bin)

    @property
    def maxBin(self):
        """Maximum supported binning level"""
        return 1

    @property
    def cameraState(self):
        """Current camera state, see ASCOM cameraState parameter"""
        if self.__selected:
            if self.__openedFile:
                return CameraState.Idle
            else:
                return CameraState.Error
        else:
            return CameraState.Idle

    @property
    def errorMessage(self):
        return None

    @property
    def cameraXSize(self):
        """Image width, 0 if not known"""
        return 0

    @property
    def cameraYSize(self):
        """Image width, 0 if not known"""
        return 0

    @property
    def imageReady(self):
        """Returns True if a captured image is available"""
        return self.__selected

    def capture(self, duration):
        """Open file open dialog"""
        self.__selected = False
        fileName = wx.FileSelector(
            message=_("Choose file to solve"),
            default_path=os.path.dirname(self.__openedFile or self.getProperty("directory")),
            flags=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST,
            wildcard=_("Image files") + " (*.fit; *.fits; *.fts; *.jpg; *.tiff; *.tif; *.pnm)|*.fit; *.fits; *.fts; *.jpg; *.tiff; *.tif; *.pnm"
        )
        self.__selected = True
        if not fileName:
            self.__openedFile = None
        else:
            self.__openedFile = fileName
        self.setProperty("directory", os.path.dirname(fileName))
        return

    def getImage(self):
        """Returns None or path to image"""
        return self.__openedFile

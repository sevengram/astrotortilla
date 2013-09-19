# vim:st=4 sts=4 sw=4 et si
"""ByEosCamera
- simple camera interface to BackyardEOS
"""

import logging
logger = logging.getLogger("astrotortilla.ByEosCamera")

from ..ICamera import ICamera
from .. import CameraState
import tempfile, shutil
import os.path, os, string
import win32ui, win32api, win32con
try:
    import winxpgui as win32gui
except:
    import win32gui
import socket, glob, time
from pywinauto import Application
from pywinauto.timings import WaitUntil
import threading
import gettext
t = gettext.translation('astrotortilla', 'locale', fallback=True)
_ = t.gettext


def str2bool(string):
    s = str(string).lower()+" "
    return s[0] in ("y", "t", "1")


# Property dict structure:
# key: (readable name, validation function, name tooltip, value tooltip, default value)
# The values can be set as strings by the using application.

PROPERTYLIST = {
        "hostname":(_("BackyardEOS address"), str, _("Hostname or IP address"), "", "127.0.0.1"),
        "port":(_("Port number"), int, _("BackyardEOS server port"), "", "1499"),
        "ISO":(_("ISO value"), int, _("ISO value for AstroTortilla images"), "", "800"),
        "timeout":(_("Messaging timeout"), int, _("Communication timeout in seconds"), "", "10"),
        }

STATUS={
    '' : CameraState.Error,
    'idle' : CameraState.Idle,
    'error' : CameraState.Error,
    'busy' : CameraState.Exposing
    }

class ByEosCamera(ICamera):
#class ByEosCamera: # Use above line when supported
    def __init__(self):
        super(ByEosCamera, self).__init__()
        self.__bin = 1
        self.propertyList = PROPERTYLIST
        self.__state = CameraState.Idle
        self.__buffersize = 512
        self.__latestImage = None
        self.__lastError = ""

    def __connect(self):
        s = None
        try:
            s = socket.create_connection((self.getProperty("hostname"), int(self.getProperty("port"))), timeout=self.__timeout)
        except:
            self.__lastError = "Failed to connect to BackyardEOS"
            logger.error("Failed to connect to BackyardEOS")
        return s

    @property
    def __timeout(self):
        return int(self.getProperty("timeout"))

    def __command(self, command):
        conn = self.__connect()
        if not conn:
            return ""
        response = ""
        try:
            conn.send(command)
            time.sleep(0.1)
            if command[:3].lower() == "get":
                response = conn.recv(self.__buffersize)
            else:
                response = None
        except socket.timeout:
            pass # TODO: handle timeouts properly
        except Exception:
            import traceback
            logger.error(traceback.format_exc())
            logger.error("BackyardEOS connection lost during command")
        return response

    def __del__(self):
        super(ByEosCamera, self).__del__()
    
    @classmethod
    def getName(cls):
        return "BackyardEOS"

    @property
    def imageTypes(self):
        "List of image types supported by the camera"
        return ["jpg"]

    @property
    def connected(self):
        return True

    @connected.setter
    def connected(self, value):
        return

    @property
    def canAutoConnect(self):
        "@return True, ByEosCamera can connect automatically for capturing."
        return True

    @property
    def disconnectAfterCapture(self):
        "@return True if BackyardEOS connection is closed after capture."
        return True

    @disconnectAfterCapture.setter
    def disconnectAfterCapture(self, value):
        "If value == True, connection to BackyardEOS is closed after capture."
        return

    @property
    def binning(self):
        "Current binning setting"
        return self.__bin

    @binning.setter
    def binning(self, bin):
        "Set bin value, 1<= `bin` <= `maxBin`"
        if not (1 <= bin <= self.maxBin):
            raise ValueError("bin value must be 1 <= value <= maxBin")
        self.__bin = int(bin)

    @property
    def maxBin(self):
        "Maximum supported binning level"
        return 4

    @property
    def cameraState(self):
        "Current camera state, see ASCOM cameraState parameter"
        status = CameraState.Error
        rsp = ""
        try:
            rsp = self.__command("getstatus")
            status = STATUS[rsp]
        except Exception:
            import traceback
            logger.error(traceback.format_exc())
            logger.error("BackyardEOS response: '%s'"%rsp)
        return status

    @property
    def errorMessage(self):
        rsp = _("Could not connect to BackyardEOS")
        try:
            rsp= self.__command("getlasterror").strip()
            if not rsp:
                rsp = self.__lastError
        except:
            pass
        self.__lastError = rsp
        return self.__lastError


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
        "@return True if a captured image is available"
        # maybe not the best way?
        rsp = self.__command("getispictureready")
        return rsp.lower().strip() == "true"
    
    def capture(self, duration):
        "Starts image exposure, no returned value"
        # clear temp directory first
        if self.cameraState != CameraState.Idle:
            raise Exception(self.errorMessage)
        
        self.__state = CameraState.Exposing
        if self.__latestImage:
            try:
                os.remove(self.__latestImage)
            except Exception as detail:
                raise IOError("Failed to clear cache: %s"%detail)
        self.__latestImage = None
        
        try:
            response = self.__command("takepicture duration:%f iso:%s bin:%d" %(duration, self.getProperty("ISO"), self.__bin))
        except:
            import traceback
            logger.error(traceback.format_exc())
            self.__state = CameraState.Error
        self.__state = CameraState.Idle


    def getImage(self):
        "@return None or path to image"
        if self.__latestImage:
            return self.__latestImage
        
        if self.imageReady:
            self.__state = CameraState.Idle
            reply = self.__command("getpicturepath")
            newPath = os.path.join(self.workingDirectory, os.path.basename(reply))
            shutil.copyfile(reply, newPath)
            self.__latestImage = newPath
            return newPath
        else:
            return None

    def reset(self):
        status = self.cameraState
        if status == CameraState.Error:
            logger.error("Resetting error: %s"% self.errorMessage)
        elif status == CameraState.Exposing:
            self.__command("abort")


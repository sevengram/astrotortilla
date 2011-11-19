# vim:st=4 sts=4 sw=4 et si
"""NebulosityCamera
- simple camera interface to Nebulosity 2
"""

from ..ICamera import ICamera
from .. import CameraState
import tempfile, shutil
import os.path, os
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


CAMERAS = (
        "No Camera",
        "Simulator",
        "Apogee",
        "Artemis 285 / Atik 16HR",
        "Artemis 285C / Atik 16HRC",
        "Artemis 429 / Atik 16",
        "Artemis 429C / Atik 16C",
        "Atik 16C",
        "Atik 16IC Color",
        "Atik 3xx, 4000, 11000",
        "Canon DIGICII/III/4 DSLR",
        "CCD Labs Q285M/QHY2Pro",
        "FLI",
        "Fishcamp Starfish",
        "Meade DSI",
        "Moravian G2/G3",
        "Opticstar DS-335C",
        "Opticstar DS-335C ICE",
        "Opticstar DS-336C XL",
        "Opticstar DS-615C XL",
        "Opticstar PL-130M",
        "Opticstar PL-130C",
        "Opticstar DS-142M ICE",
        "Opticstar DS-142C ICE",
        "Opticstar DS-145M ICE",
        "Opticstar DS-145C ICE",
        "Orion StarShoot",
        "QHY2 TVDE",
        "QHY8 Pro",
        "QHY8",
        "QHY9",
        "QSI 500",
        "SAC-10",
        "SAC7/SC webcam LXUSB",
        "SAC7/SC webcam Parallel",
        "SBIG",
        "Starlight Xpress USB",
        "ASCOM Camera",
        "ASCOMLate Camera",
        )

def str2bool(string):
    s = str(string).lower()+" "
    return s[0] in ("y", "t", "1")

# Property dict structure:
# key: (readable name, validation function, name tooltip, value tooltip, default value)
# The values can be set as strings by the using application.
PROPERTYLIST = {
        "path":(_("Nebulosity Path"), os.path.isdir, "", "", "C:\\Program Files\\Nebulosity2\\"),
        "setCamera":(_("Set camera"), str2bool, _("Set camera model on capture"), _("True or False"), "False"),
        "setExtFilterWheel":(_("Set ext filter"), int, _("Set ext filter before solving"), _("Filter index or -1"), "-1"),
        "setFilterWheel":(_("Set filter"), int, _("Set filter before solving"), _("Filter index or -1"), "-1"),
        "resetPath":(_("Reset directory to"), str, _("After capture directory"), _("%(date)s = current date, %(night)s = current date at dusk"), ""),
        }

class NebulosityCamera(ICamera):
    def __init__(self):
        super(NebulosityCamera, self).__init__()
        self.__camera = None
        self.__sock = None
        self.__bin = 1
        self.__basename = "Capture"
        self.propertyList = PROPERTYLIST
        self.__state = CameraState.Idle

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
        "Execute script commands in Nebulosity"
        if type(cmd)==str:
            cmd += "\n"
        elif type(cmd) in (list, tuple):
            cmd = "\n".join(cmd)
            cmd += "\n"
        self.__nebulositySendSript(cmd)

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
        else:
            raise NameError("'%s' is not a known camera"%str(value))

    @property
    def connected(self):
        "@return True, Nebulosity is autoconnected"
        return True

    @connected.setter
    def connected(self, value):
        "Do nothing, autoconnected"
        return
    
    @property
    def canAutoConnect(self):
        "@return True, NebulosityCamera can connect automatically for capturing."
        return True

    @property
    def disconnectAfterCapture(self):
        "@return True if Nebulosity connection is closed after capture."
        return True

    @disconnectAfterCapture.setter
    def disconnectAfterCapture(self, value):
        "If value == True, connection to Nebulosity is closed after capture."
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
        return self.__state

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
        "@return True if a captured image is available"
        rv = len(glob.glob(os.path.join(self.workingDirectory, self.__basename+"*.fit"))) > 0
        if rv:
            self.__state = CameraState.Idle
        return rv
    
    def capture(self, duration):
        "Starts image exposure, no returned value"
        # clear temp directory first
        self.__state = CameraState.Exposing
        try:
            map(os.remove, glob.glob(os.path.join(self.workingDirectory, self.__basename+"*.fit")))
        except Exception as detail:
            raise IOError("Failed to clear cache: %s"%detail)


        cmd = [
            "SetDuration %d"%(int(duration*1000)),
            "SetDirectory %s"%self.workingDirectory,
            "SetBinning %d"%(self.__bin-1)]

        if str2bool(self.getProperty("setCamera")) and self.__camera:
            cmd.insert(0, "ConnectName %s"%(self.__camera))

        if self.getProperty("setExtFilterWheel") != "-1":
            cmd.append("SetExtFilter %s"%self.getProperty("setExtFilterWheel"))

        if self.getProperty("setFilterWheel") != "-1":
            cmd.append("SetFilter %s"%self.getProperty("setFilterWheel"))


        cmd.append( "CaptureSingle %s"%(self.__basename))

        if self.getProperty("resetPath") != "":
            pathDict={
                "date":time.strftime("%Y-%m-%d"),
                "night":time.strftime("%Y-%m-%d", time.gmtime(time.time()-86400/2))
                }
            resetPath = "%s"%(self.getProperty("resetPath")%pathDict)
            try:
                if not os.path.exists(resetPath):
                    os.mkdir(resetPath)
            except:
                pass
            cmd.append("SetDirectory %s"%resetPath)

        self.__cmd(cmd)
        self.__state = CameraState.Idle


    def getImage(self):
        "@return None or path to image"
        if self.imageReady:
            self.__state = CameraState.Idle
            return glob.glob(os.path.join(self.workingDirectory, self.__basename+"*.fit"))[-1]
        else:
            return None

    def __nebulositySendSript(self, script):
        """Get handle to nebulosity window
        Send <ctrl-R>
        get handle to the script loading dialog
        Create script file with contents from str script
        send path to script file to loading dialog
        Send <enter> to dialog
        Throws an exception if anything fails.
        """
        app = Application()
        nebu_path = os.path.join(self.getProperty("path"), "nebulosity.exe")
        print nebu_path
        try:
            app.connect_(path=nebu_path)
        except:
            app.start_(nebu_path)
        # Create script file
        fname = os.path.join(self.getProperty("path"), "capture.neb")
        f = file(fname, "w")
        f.write(script)
        f.close()
        fname = fname.replace("~", "{~}")
        app.Nebulosity.Wait("visible")
        app.Nebulosity.SetFocus()
        app.Nebulosity.TypeKeys("^r")
        try:
            WaitUntil(10.5, 0.5, app.LoadScript.Exists, True)
        except:
            raise _("Nebulosity not responding to script loading")
        dlg = app.LoadScript.Wait("visible")
        dlg.SetFocus()
        dlg.TypeKeys(fname+"{ENTER}", pause=0.001, with_spaces=True)


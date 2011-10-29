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
from astromate.automation import SendKeys
import threading
import gettext
t = gettext.translation('nebulositycamera', 'locale', fallback=True)
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
        "port":(_("Nebulosity ListenPort"), int, "", _("0 for script connection"), 0),
        "path":(_("Nebulosity Path"), os.path.isdir, "", "", "C:\\Program Files\\Nebulosity2\\"),
        "mapColon":(_("Colon escape"), str, "", "", "+."),
        "mapBackslash":(_("Backslash escape"), str, "", "", "^%\\"),
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
        self.__autoDisco = True
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
        if int(self.getProperty("port"))>0: # socket communications
            if not self.__sock:
                try:
                    self.connected = True
                except:
                    raise IOError("Not connected")
            self.__sock.send(cmd.encode())
        else: # direct script communication
            self.__nebulositySendSript(cmd)

    def __asyncDisconnect(self):
        "Disconnect asynchronously without blocking"
        def disconnector(obj):
            obj.connected=False
            obj.__state = CameraState.Idle

        worker = threading.Thread(target=disconnector, args=(self,))
        worker.start()
        #self.connected=False
        #self.__state = CameraState.Idle

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
        "@return True when connection to Nebulosity exists"
        return int(self.getProperty("port")) <= 0 or self.__sock != None

    @connected.setter
    def connected(self, value):
        "Connect to Nebulosity when value == True, disconnect when value == False"
        if int(self.getProperty("port")) <=0:
            return

        if value == True:
            if self.__sock:
                return
            try:
                # set Nebulosity to script listening mode
                self.__nebulosityScriptMode()
                # connect to server socket, retry for 20s
                now = startTime = time.time()
                while not self.__sock:
                    try:
                        self.__sock = socket.create_connection(("127.0.0.1", int(self.getProperty("port"))), 1)
                    except (Exception, socket.error) as error:
                        now = time.time()
                        if now - startTime > 20: # re-raise error after 20s
                            raise error
                        time.sleep(0.5)
                        del self.__sock
                        self.__sock = None
            except:
                self.__sock = None
                raise IOError("Connection failed")
        else:
            if self.__sock == None:
                return
            try:
                self.__cmd("ListenPort 0")
                # Wait for Nebulosity to close the socket first
                self.__sock.recv(1)
                self.__sock.close()
            except:
                pass
            del self.__sock
            self.__sock = None
    
    @property
    def canAutoConnect(self):
        "@return True, NebulosityCamera can connect automatically for capturing."
        return True

    @property
    def disconnectAfterCapture(self):
        "@return True if Nebulosity connection is closed after capture."
        return self.__autoDisco

    @disconnectAfterCapture.setter
    def disconnectAfterCapture(self, value):
        "If value == True, connection to Nebulosity is closed after capture."
        self.__autoDisco = value == True

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

        if not self.connected:
            self.connected = True

        cmd = [
            "SetDuration %d"%(int(duration*1000)),
            "SetDirectory %s"%self.workingDirectory,
#            "SetName %s"%(self.__basename),
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
        
        if self.__autoDisco:
            self.__asyncDisconnect()


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
        def _hwndCallback(hwnd, extra):
            extra.append((hwnd,
                win32gui.GetWindowText(hwnd),
                win32gui.GetClassName(hwnd)
                ))

        hwndList = []
        win32gui.EnumWindows(_hwndCallback, hwndList)
        windows = [window for window in hwndList if window[1].startswith("Nebulosity v2.4.")]
        if not windows:
            raise Exception(_("Nebulosity window not found"))
        hwnd = windows[0][0]
        win32gui.ShowWindow(hwnd,win32con.SW_RESTORE)
        win32gui.SetForegroundWindow(hwnd)
        time.sleep(0.2) # give time for Nebulosity to get focus
        SendKeys("^r")
        # Create script file
        fname = os.path.join(self.getProperty("path"), "capture.neb")
        f = file(fname, "w")
        f.write(script)
        f.close()
        scriptWin = None
        start = time.time()
        while not scriptWin and time.time()-start < 5:
            hwndList = []
            win32gui.EnumWindows(_hwndCallback, hwndList)
            scriptWin = [window for window in hwndList if window[1] == "Load script"]
        if not scriptWin:
            raise _("Script loading failed")
        win32gui.SetForegroundWindow(scriptWin[0][0])
        time.sleep(0.1)
        fname = fname.replace(":", self.getProperty("mapColon"))
        fname = fname.replace("\\", self.getProperty("mapBackslash"))
        SendKeys(fname, pause=0.001, with_spaces=True)
        SendKeys("{ENTER}")


    def __nebulosityScriptMode(self):
        self.__nebulositySendSript("ListenPort %d\n"%int(self.getProperty("port")))

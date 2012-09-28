# vim:st=4 sts=4 sw=4 et si
"Astro Photography Tool Camera interface"

import logging
logger = logging.getLogger("astrotortilla.APTCamera")


from ..ICamera import ICamera
from .. import CameraState
import os, os.path
import shutil
import socket
import time
from select import select

import gettext
t = gettext.translation('astrotortilla', 'locale', fallback=True)
_ = t.gettext
#
"""APT commands Nov2011
Command "S" (status) returns:
        NCC - no camera connection
        IDL - APT can accept commands
        BUS - APT is busy
        CAP - APT is capturing image in result of "C" command
        E01 - unknown status
        E02 - the camera has to be set in B/M dial mode. The status will be
              set to IDL after the E02 is read with "S" command from AT. This case happens
              when "C" command is sent, but exposure can't start

Command "C" (capture) - format C1XXX. Returns:
        E01 - Bad exposure duration parameter
        E02 - Bad state - APT can't start the exposure because is busy or
              there is no connection to camera
        E03 - Can't start exposure
        ROK - the command is accepted. Wait a second or two and check the
              status to see if you will get E02, if the status is CAP or IDL everything is
              fine

Command "G" (get) returns
        A string with the filename. The socket will provide the length of
        the string

Command "R" (remove). This deletes the last captured for AT image. Returns:
        E01 - the file can't be deleted - most likely doesn't exist
        ROK - the file is deleted

If a command gets a result "USC" this means "Unsupported command".
"""
#
#
#
PROPERTYLIST = {
        "port":(_("Port"), int, _("Astro Photography Tool TCP port"), _("default 21701"), "21701"),
        "hostname":(_("Hostname"), str, _("Hostname or IP address"), "", "localhost"),
        }

class APTCamera(ICamera):
    """
    State transitions:
    __exposing == exposure issued, not completed yet
    __waitingDON == exposure issued, current socket connection has not yet acknowledged completion
    __latestImage== name of the image file after latest successfull exposure or None
    """
    status = {
        "":CameraState.Error,
        "IDL": CameraState.Idle,
        "CAP": CameraState.Exposing,
        "BUS": CameraState.Busy,
        "E01": CameraState.Error,
        "E02": CameraState.Error,
        "NCC": CameraState.Error,
        }
    def __init__(self):
        super(APTCamera, self).__init__()
        self.__socket = None
        self.__connected = False
        self.__buffersize = 512
        self.__latestImage = None
        self.__exposing = True # internal state keeping flag
        self.__waitingDON = False # out-of-state transition flag
        self.propertyList = PROPERTYLIST

    def __del__(self):
        if self.__socket:
            self.__socket.close()
            self.__socket = None
        super(APTCamera, self).__del__()

    @classmethod
    def getName(cls):
        return "Astro Photography Tool"

    @property
    def imageTypes(self):
        return ["jpg"]

    def aptCmd(self, command, timeout=0):
        self.connected = True
        if not self.connected:
            return ""
        if timeout > 0:
            n=self.__socket.gettimeout()
            self.__socket.settimeout(timeout)
            timeout=n
        response = ""
        try:
            self.__socket.send(command)
            time.sleep(0.1) # A small pause for scheduling and APT processing
            response = self.__socket.recv(self.__buffersize)
        except socket.timeout:
            pass # TODO: deal with timeouts properly
        except Exception:
            import traceback
            logger.error(traceback.format_exc())
            logger.error("APT connection lost during command")
        finally:
            if timeout > 0:
                self.__socket.settimeout(timeout)
        return response

    def connect(self):
        if not self.__socket:
            try:
                self.__socket = socket.create_connection((self.getProperty("hostname"), int(self.getProperty("port"))), timeout=10)
            except: # incorrect socket or APT not running
                #import traceback
                #logger.error(traceback.format_exc())
                self.__socket = None

    @property
    def connected(self):
        return bool(self.__socket)

    @connected.setter
    def connected(self, value):
        if value and not self.__socket:
            self.connect()

        if not value and self.connected:
            try:
                self.__socket.close()
            except: pass
            self.__socket = None

    @property
    def cameraState(self):
        "Current camera state, see ASCOM cameraState parameter"
        if self.__waitingDON: # Capturing started, not done yet
            return CameraState.Exposing
        return APTCamera.status[self.aptCmd("S")]

    @property
    def imageReady(self):
        if self.__latestImage != None:
            return True
        if self.__waitingDON:
            r,s,x = select([self.__socket], [],[],.02)
            if not r:
                return False
            try:
                don=self.__socket.recv(3)
                if don == "DON":
                    self.__waitingDON = False
                    self.__exposing = CameraState.Idle
                    self.__getImage()
                    logger.debug("Image ready")
                    return True
            except socket.timeout:
                logger.debug("Communication timeout")
                return False
            except:
                import traceback
                logger.error(traceback.format_exc())
                self.connected = False
                self.__waitingDON = False
                self.__connected= True
        # Fall thru on connection failure, reconnect and wait for idle status
        if self.cameraState == CameraState.Idle and self.__exposing == CameraState.Exposing:
            self.__exposing = False
            self.__waitingDON = False
            logger.debug("Recovering connection, APT is idle")
            self.__getImage()
            return True
        else:
            logger.debug("Recovering connection, APT is busy")
            return False

    def capture(self, duration):
        if not self.cameraState == CameraState.Idle:
            raise Exception("APT: Camera not idle") 
        if duration < 1:
            exposureTime = 1
        elif duration > 999:
            exposureTime = 999
        else:
            exposureTime = duration

        self.__latestImage = None
        try:
            reply = self.aptCmd("C1%03i" % exposureTime)
            if "ROK" not in reply:
                raise Exception("APT: Unexpected response: %s"%reply)
            self.__waitingDON = True
            self.__exposing = True
        except Exception:
            raise 

    def getImage(self):
        return self.__latestImage

    def __getImage(self):
        self.__exposing = False
        reply = self.aptCmd("G")
        newPath = os.path.join(self.workingDirectory, os.path.basename(reply))
        shutil.copyfile(reply, newPath)
        self.aptCmd("R")
        self.__latestImage = newPath
        self.connected = False # close connection to avoid APT issued disconnect problems.
        logger.debug(newPath)

    def reset(self):
        self.__exposing = False
        self.__waitingDON = False
        self.connected = False

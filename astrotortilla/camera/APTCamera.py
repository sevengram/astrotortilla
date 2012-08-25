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

import gettext
t = gettext.translation('astrotortilla', 'locale', fallback=True)
_ = t.gettext

PROPERTYLIST = {
        "port":(_("Port"), int, _("Astro Photography Tool TCP port"), _("default 21701"), "21701"),
        "hostname":(_("Hostname"), str, _("Hostname or IP address"), "", "localhost"),
        }

class APTCamera(ICamera):
    def __init__(self):
        super(APTCamera, self).__init__()
        self.__socket = None
        self.__buffersize = 512
        self.__camState = CameraState.Idle
        self.__latestImage = None

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

    def aptCmd(self, command):
        self.connected = true
        response = ""
        try:
            self.__socket.send(command)
            response = self.__socket.recv(self.__buffersize)
        except:
            logger.error("APT connection lost during command")
        self.connected = false
        return response

    def connect(self):
        if not self.__socket:
            try:
                self.__socket = socket.create_connection((self.getProperty("hostname"), int(self.getProperty("port"))), timeout=10)
            except:
                self.__socket = None

    @property
    def connected(self):
        return bool(self.__socket)

    @connected.setter
    def connected(self, value):
        if value == self.connected:
            return
        if value:
            self.connect()
        else:
            self.__socket.close()
            self.__socket = None

    @property
    def cameraState(self):
        "Current camera state, see ASCOM cameraState parameter"
        return self.__camState

    @property
    def imageReady(self):
        reply = self.aptCmd("S")
        if "IDL" in reply or "DON" in reply and self.__latestImage:
            self.__camState = CameraState.Idle
            return True
        else:
            return False

    def capture(self, duration):
        self.__camState = CameraState.Exposing
        if duration < 1:
            exposureTime = 1
        elif duration > 999:
            exposureTime = 999
        else:
            exposureTime = duration

        try:
            reply = self.aptCmd("S")
            if "IDL" not in reply:
                raise Exception("APT: Not idle!")
            reply = self.aptCmd("C1%03i" % exposureTime)
            if "ROK" not in reply:
                raise Exception("APT: No ROK in reply!")
        except Exception:
            self.__camState = CameraState.Error
            raise

    def getImage(self):
        if self.__camState == CameraState.Error:
            return None
        self.connect()
        if not self.connected or not self.imageReady:
            return None
        self.__camState = CameraState.Idle
        reply = self.aptCmd("G")
        if reply == "ROK":
            return None
        newPath = os.path.join(self.workingDirectory, "APT.jpg")
        shutil.copyfile(reply, newPath)
        self.aptCmd("R")
        self.__latestImage = newPath
        return newPath

# vim:st=4 sts=4 sw=4 et si
"Astro Photography Tool Camera interface"

from ..ICamera import ICamera
from .. import CameraState
import os, os.path
import shutil
import socket
import time

import gettext
t = gettext.translation('astrotortilla', 'locale', fallback=True)
_ = t.gettext

class APTCamera(ICamera):
    def __init__(self):
        super(APTCamera, self).__init__()
        self.__port = 21701
        self.__socket = None
        self.__buffersize = 512
        self.__camState = CameraState.Idle
        self.__latestImage = None

    def __del__(self):
        if self.__socket:
            self.__socket.close()
            self.__socket = None
        super(APTCamera, self).__del__()

    @property
    def imageTypes(self):
        return ["jpg"]

    def connect(self):
        if not self.__socket:
            try:
                self.__socket = socket.create_connection(('localhost', self.__port), timeout=3)
            except:
                self.__socket = None

    @property
    def connected(self):
        return bool(self.__socket)

    @connected.setter
    def connected(self, value):
        if value == self.connected:
            return
        self.connect()

    @property
    def cameraState(self):
        "Current camera state, see ASCOM cameraState parameter"
        return self.__camState

    @property
    def imageReady(self):
        if not self.connected:
            return False
        self.__socket.send("S")
        reply = self.__socket.recv(self.__buffersize)
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
            self.connect()
            if not self.connected:
                raise Exception("APT: Not connected!")
            self.__socket.send("S")
            if self.__socket.recv(self.__buffersize) != "IDL":
                raise Exception("APT: Not idle!")
            self.__socket.send("C1%03i" % exposureTime)
            reply = self.__socket.recv(self.__buffersize)
            if "ROK" not in reply:
                raise Exception("APT: No ROK in reply!")
        except Exception:
            if self.connected:
                self.__socket.close()
            self.__socket = None
            self.__camState = CameraState.Error
            raise

    def getImage(self):
        if self.__camState == CameraState.Error:
            return None
        self.connect()
        if not self.connected or not self.imageReady:
            return None
        self.__camState = CameraState.Idle
        self.__socket.send("G")
        reply = self.__socket.recv(self.__buffersize)
        if reply == "ROK":
            return None
        newPath = os.path.join(self.workingDirectory, "APT.jpg")
        shutil.copyfile(reply, newPath)
        self.__socket.send("R")
        self.__socket.recv(self.__buffersize)
        self.__latestImage = newPath
        return newPath

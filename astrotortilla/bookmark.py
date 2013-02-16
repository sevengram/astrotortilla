"AstroTortilla bookmark class"
# vim: set fileencoding=UTF-8 encoding=UTF-8
# -*- coding: UTF-8 -*-

from libs.appdirs.appdirs import AppDirs
from units import deg2hms, deg2dms
import logging, base64
logger = logging.getLogger("astrotortilla.Bookmark")
logger.setLevel(logging.DEBUG)
logFormatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')


import gettext, sys
from astrotortilla.units import Coordinate, deg2dms, deg2hms, dms2deg, hms2deg, deg2str

t = gettext.translation('astrotortilla', 'locale', fallback=True)
_ = t.gettext

class Bookmark(object):
    "Named bookmark holder"
    def __init__(self, name, position, angle):
        if not (type(name) in (str, unicode) and issubclass(type(position), Coordinate) and type(angle) in (float, int)):
            raise TypeError("Invalid parameter types")
        if type(name) == str:
            trying=["utf8", "latin1"]
            while trying:
                try:
                    name = name.decode(trying.pop())
                except:pass
        self.__name = unicode(name).strip() or u"%s/%s"%(deg2hms(position.RA), deg2dms(position.dec))
        self.__position = position
        self.__angle = angle

    @property
    def name(self):
        return self.__name

    @property
    def position(self):
        return self.__position

    @property
    def camera_angle(self):
        return self.__angle

    def to_string(self):
        "Short string representation"
        name = "(b64|utf8)" + base64.b64encode(self.__name.encode("utf8"))
        return u"%s,%s,%.1f,%s"%(deg2hms(self.__position.RA), deg2dms(self.__position.dec,":"), self.__angle, name)

    @classmethod
    def from_string(cls, bookmark):
        "construct bookmark from serialized string representation"
        ra, dec, angle, name = bookmark.split(",",4)
        position = Coordinate(ra.strip(), dec.strip())
        angle = float(angle.strip())
        name = name.strip()
        try:
            if name[:4] == "(b64":
                enc,name = name[5:].split(")", 1)
                name = base64.b64decode(name).decode(enc or "utf8")
        except: pass
        return Bookmark(name, position, angle)

    @property
    def position_label(self):
        return "%s/%s/%s"%(deg2hms(self.position.RA), deg2dms(self.position.dec),deg2str(self.camera_angle))

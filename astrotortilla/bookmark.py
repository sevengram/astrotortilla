"AstroTortilla bookmark class"
# vim: set fileencoding=UTF-8 encoding=UTF-8
# -*- coding: UTF-8 -*-

from libs.appdirs.appdirs import AppDirs
import logging
logger = logging.getLogger("astrotortilla.Bookmark")
logger.setLevel(logging.DEBUG)
logFormatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')


import gettext, sys
from astrotortilla.units import Coordinate, deg2dms, deg2hms, dms2deg, hms2deg

t = gettext.translation('astrotortilla', 'locale', fallback=True)
_ = t.gettext

class Bookmark(object):
    "Named bookmark holder"
    def __init__(self, name, position, angle):	    
        if not (type(name) in (str, unicode) and issubclass(type(position), Coordinate) and type(angle) in (float, int)):
            raise TypeError("Invalid parameter types")
        self.__name = name
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
        return u"%s,%s,%.1f,%s"%(deg2hms(self.__position.RA), deg2dms(self.__position.dec,":"), self.__angle, self.__name)

    @classmethod
    def from_string(cls, bookmark):
        "construct bookmark from serialized string representation"
        ra, dec, angle, name = bookmark.split(",",4)
        position = Coordinate(ra.strip(), dec.strip())
        angle = float(angle.strip())
        return Bookmark(name.strip(), position, angle)

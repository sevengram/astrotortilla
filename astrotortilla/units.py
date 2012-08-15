"AstroMate units"
# vim: set fileencoding=UTF-8 encoding=UTF-8:
# -*- coding: UTF-8 -*-

import gettext

from math import pi, sin, cos, asin, sqrt, radians, degrees, atan2

class Coordinate(object):
    "Equatorial coordinate-pair RA and dec"
    def __init__(self, RA, Dec):
        if type(RA) in (str,unicode) or type(RA) == tuple:
            if isFloat(RA):
                self.__ra = float(RA) # float degrees in string format?
            else:
                self.__ra = hms2deg(RA)
        elif type(RA) == float or type(RA) == int:
            self.__ra = float(RA)
        else:
            raise TypeError("Invalid type for RA")
        
        if type(Dec) in (str,unicode) or type(Dec) == tuple:
            if isFloat(Dec):
                self.__dec = float(Dec) # float degrees in string format?
            else:
                self.__dec = dms2deg(Dec)
        elif type(Dec) == float or type(Dec) == int:
            self.__dec = float(Dec)
        else:
            raise TypeError("Invalid type for Dec")
        self.__ra %= 360
        while self.__ra < 0:
            self.__ra += 360
        if self.__dec > 90: self.__dec = 90.0
        if self.__dec < -90: self.__dec = -90

    @property
    def RA(self):
        "Right ascension in degrees"
        return self.__ra

    @property
    def dec(self):
        "Declination in degrees"
        return self.__dec

    def __repr__(self):
        return "Coordinate(%f, %f)"%(self.__ra, self.__dec)

    def __sub__(self, other):
        if isinstance(other, Coordinate):
            sep = Separation(other, self)
            return Separation(sep.degrees, (180+sep.bearing)%360)
        #if isinstance(other, Separation):
        #   s2 = Separation(other.degrees, (180+other.bearing)%360)
        #   return s2 + self
        raise TypeError("Cannot subtract %s from Coordinate"%repr(type(other)))
    
    def __add__(self, other):
        if not isinstance(other, Separation):
            raise TypeError("Cannot add %s to Coordinate"%repr(type(other)))
        return other + self

class Separation(object):
    "Separation of two celestial coordinates"
    def __init__(self, coord1, coord2):
        """Separation(Coordinate c1, Coordinate c2)
        Separation(float separation, float bearing)
        """
        if not  ( ( type(coord1) == type(coord2) == float ) or
            ( isinstance(coord1, Coordinate) and isinstance(coord2, Coordinate) ) ):
            raise TypeError("Invalid parameters")

        if type(coord1) == float:
            self.__sep = coord1
            self.__bear = coord2
        else:
            dRA = coord1.RA - coord2.RA
            dDec = coord1.dec - coord2.dec
            # Sinnott's formula for angular separation 
            C = sin(radians(dDec)/2)**2 + cos(radians(coord1.dec))*cos(radians(coord2.dec)) * sin(radians(dRA)/2)**2
            self.__sep = degrees( 2 * asin( sqrt (abs(C)) ) )
            # initial bearing
            y = sin(radians(dRA)) * cos(radians(coord2.dec))
            x = cos(radians(coord1.dec))*sin(radians(coord2.dec)) - sin(radians(coord1.dec))*cos(radians(coord2.dec))*cos(radians(dRA))
            self.__bear = degrees(atan2(y, x))
            
    
    @property
    def bearing(self):
        "Bearing of separation in degrees"
        return self.__bear

    @property
    def degrees(self):
        "Angular separation in degrees"
        return self.__sep

    @property
    def arcminutes(self):
        "Angular separation in arcminutes"
        return self.__sep * 60.

    @property
    def arcseconds(self):
        "Angular separation in arcseconds"
        return self.__sep * 3600.

    def __repr__(self):
        return "Separation(%f, %f)"%(self.__sep, self.__bear)

    def __add__(self, other):
        if not isinstance(other, Coordinate):
            raise TypeError("Invalid parameter type %s"%repr(type(other)))
        destDec = asin( sin(radians(other.dec))*cos(radians(self.__sep)) + cos(radians(other.dec))*sin(radians(self.__sep))*cos(radians(self.__bear)) );

        destRA = radians(other.RA) + atan2( sin(radians(self.__bear))*sin(radians(self.__sep))*cos(radians(other.dec)), cos(radians(self.__sep))-sin(radians(other.dec))*sin(destDec));
        
        return Coordinate(degrees(destRA), degrees(destDec))

def hms2deg(hms):
    "Convert from HHhMMmSS.SSs,HH:MM:SS.SS or tuple of floats to arc seconds"
    if type(hms) in (str, unicode):
        if ":" in hms:
            hms = map(float, hms.split(":")[:3])
        elif "h" in hms:
            h, rest = hms.split("h",1)
            m, rest = rest.split("m", 1)
            s, rest = rest.split("s", 1)
            if rest:
                s = float(s) + float("0."+rest)
            hms = map(float, (h, m, s))
        else:
            raise TypeError("Invalid HMS string format")
    elif type(hms) == tuple and len(hms) == 3:
        hms = map(float, hms)
    else:
        raise TypeError("Invalid HMS type")
    
    h,m,s = hms
    return (h + m/60. + s/3600.)*360./24

def dms2deg(dms):
    "Convert from HH:MM:SS.SS or tuple of floats to arc seconds"
    _dms = [0,0,0]
    sign = 1
    if type(dms) in ( str, unicode ):
        if dms[0] == "-":
            sign = -1
            dms = dms[1:]
        if ":" in dms:
            _dms = map(float, dms.split(":")[:3])
        elif "d" in dms:
            d, rest = dms.split("d",1)
            m, rest = rest.split("m", 1)
            s, rest = rest.split("s", 1)
            if rest:
                s = float(s) + float("0."+rest)
            _dms = map(float, (d, m, s))
        elif u"\xb0" in unicode(dms):
            d, rest = unicode(dms).split(u"\xb0",1)
            m, rest = rest.split("'", 1)
            s, rest = rest.split("\"", 1)
            if rest:
                s = float(s) + float("0."+rest)
            _dms = map(float, (d, m, s))
        elif "\xf8" in dms: # degree -char in Windows
            d, rest = dms.split("\xf8",1)
            m, rest = rest.split("'", 1)
            s, rest = rest.split("\"", 1)
            if rest:
                s = float(s) + float("0."+rest)
            _dms = map(float, (d, m, s))
        else:
            raise TypeError("Invalid DMS string format")
    elif type(dms) == tuple and len(dms) == 3:
        if dms[0] < 0:
            sign = -1
            dms = (abs(dms[0]), dms[1], dms[2])
        _dms = map(float, dms)
    else:
        raise TypeError("Invalid DMS type")
    
    d,m,s = _dms
    return sign * (d + m/60. + s/3600. )

def deg2hms(deg, separator=None):
    while deg < 0:
        deg += 360
    hrs = deg*24./360
    hours = int(hrs)
    mfrac = hrs-hours
    amin = int(mfrac*60)
    asec = (mfrac*60 - amin)*60
    if separator and type(separator) is str:
        return separator.join(("%02d"%hours,"%02d"%amin,"%05.2f"%asec))
    return "%02dh%02dm%05.2fs"%(hours,amin,asec)

def deg2dms(deg, separator=None):
    negative = deg<0
    deg = abs(deg)
    degs = int(deg)
    mfrac = deg-degs
    amin = int(mfrac*60)
    asec = (mfrac*60 - amin)*60
    sign = u""
    if negative:
        sign = u"-"
    if separator and type(separator) is str:
        return sign + separator.join(("%02d"%degs,"%02d"%amin,"%05.2f"%asec))
    return u"%s%02d\xb0%02d'%05.2f\""%(sign,degs,amin,asec)

def deg2str(deg, prec=2):
    "return a string with wanted precision in highest non-zero unit"
    if abs(deg) > 1:
        return u"%.*f\xb0"%(prec, deg)
    amin = deg*60
    if abs(amin) > 1:
        return u"%.*f'"%(prec, amin)
    asec = deg*3600
    return u"%.*f\""%(prec, asec)

def isFloat(value):
    try:
        float(value)
        return True
    except:
        pass
    return False

def alignment(angle1, angle2):
    "return angle of alignment between angle1 and angle2 in range (-90..90]"
    # 180 rotation is considered 0 degree shift
    #normalize to 0..360
    if angle1<0: angle1 += (1 + int(-angle1)/360 ) * 360
    if angle2<0: angle2 += (1 + int(-angle2)/360 ) * 360

    
    # use angle1 as origin, modulo 180 each for match image framing matching
    delta = angle2%180 - angle1%180
    return delta if -90 < delta <= 90 else delta%180
    

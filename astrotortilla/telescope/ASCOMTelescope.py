"""ASCOMTelescope
Interface for ASCOM telescope
"""

import time
from ..ITelescope import ITelescope
from ..units import Coordinate, deg2str
from win32com.client import Dispatch

TRACE = 0 # 1 to enable function tracing

import logging
logger = logging.getLogger("astrotortilla.ASCOMTelescope")

PROPERTYLIST = {
        "lastselection":("", str, "", "", ""),
        "propertyAgeLimit":("", float, "", "", "1.0"),
        "slewSettleTime":("", float, "", "", "0.0"),
        "syncMaxWait":("", float, "", "", "2.0"),
        "syncAccuracy":("", float, "", "", "1.0")
        }

class ASCOMTelescope(ITelescope):
    def __init__(self):
        super(ASCOMTelescope, self).__init__()
        if TRACE: logger.debug(">init")
        self.__chooser = None
        try:
            self.__chooser = Dispatch("DriverHelper.Chooser")
        except: pass
        try:
            self.__chooser = Dispatch("Utilities.Chooser")
        except: pass
        try:
            self.__chooser = Dispatch("ASCOM.Utilities.Chooser")
        except: pass
        if not self.__chooser:
            raise Exception("Failed to initialize ASCOM device chooser")
        self.__chooser.DeviceType = "Telescope"
        self.propertyList = PROPERTYLIST
        self.__scopeName = None
        self.__scope = None
        self.__position = None
        self.__positionTime = 0
        self.__target = None
        self.__targetTime = 0
        self.__parked = None
        self.__parkedTime = 0
        self.__slewing = None
        self.__slewingTime = 0
        self.__slewingStopTime = 0
        self.__tracking = None
        self.__trackingTime = 0
        self.__scopeIFVersion = 0
        self.__errorCounter = 0
        if TRACE: logger.debug("<init")

    def __invalidateCache(self):
        self.__positionTime = 0
        self.__targetTime = 0
        self.__parkedTime = 0
        self.__slewingTime = 0
        self.__trackingTime = 0
        self._operation_ok = True
    
    def __del__(self):
        del self.__chooser
        del self.__scope
        super(ASCOMTelescope, self).__del__()

    @property
    def _operation_ok(self):
        return self.__errorCounter == 0

    @_operation_ok.setter
    def _operation_ok(self, value):
        if not value:
            self.__errorCounter += 1
        else:
            self.__errorCounter = 0
        if self.__errorCounter > 10:
            logger.error("10 errors in a row, disconnecting.")
            self.connected = False

    @classmethod
    def getName(cls):
        return "ASCOM Telescope"

    @property
    def _maxAge(self):
        return float(self.getProperty("propertyAgeLimit"))

    @property
    def connected(self):
        "Is the telescope connected"
        if TRACE: logger.debug("<>connected")
        rval = False
        if not self.__scope:
            return rval
        try:
            rval= self.__scope.Connected
            self._operation_ok = True
        except:
            logger.error("ASCOM Error trying to retrieve connection status")
            self.__scope = None
            self._operation_ok = False
        return rval

    def _connect(self):
        "Connect the scope"
        if TRACE: logger.debug(">connect")
        if self.__scope:
            if not self.__scope.Connected:
                self.__scope.Connected = True
            if TRACE: logger.debug("<connect")
            self.__invalidateCache()
            return
        if not self.__scopeName:
            self.__scopeName = self.__chooser.Choose(self.getProperty("lastselection"))
            if not self.__scopeName: # Canceled
                self.__invalidateCache()
                return
        self.__scope = Dispatch(self.__scopeName)
        self.setProperty("lastselection", self.__scopeName)
        self.__scope.Connected = True
        self.__scopeIFVersion = 1
        try:
            self.__scopeIFVersion = self.__scope.InterfaceVersion
        except:
            pass
        if TRACE: logger.debug("<connect")
        self.__invalidateCache()

    @connected.setter
    def connected(self, value):
        "Connect or disconnect telescope"
        if TRACE: logger.debug(">connect set")
        if value == self.connected:
            if TRACE: logger.debug("<connect set")
            return
        if value:
            self._connect()
        if self.__scope:
            self.__scope.Connected = value
        if TRACE: logger.debug("<connect set")
        self.__invalidateCache()

    @property
    def position(self):
        "Current assumed position or None if not known"
        if TRACE: logger.debug(">position")
        if not self.connected:
            if TRACE: logger.debug("<position")
            return None
        now = time.time()
        if now - self.__positionTime > self._maxAge:
            try:
                # convert RA from hours to degrees
                logger.debug("request position")
                RA = self.__scope.RightAscension*360./24
                dec = self.__scope.Declination
                self.__position = Coordinate(RA, dec)
                self.__positionTime = now
                self._operation_ok = True
            except:
                logger.error("ASCOM Error: Getting RA/DEC failed")
                self._operation_ok = False
        if TRACE: logger.debug("<position")
        return self.__position


    @property
    def target(self):
        "Target coordinates or None if not known"
        if not self.connected:
            return None
        # convert RA from hours to degrees
        if TRACE: logger.debug(">target")
        now = time.time()
        if now - self.__targetTime > self._maxAge:
            logger.debug("request target")
            try:
                self.__targetTime = now
                RA = self.__scope.TargetRightAscension*360./24
                dec = self.__scope.TargetDeclination
                self.__target = Coordinate(RA, dec)
            except:
                self.__target = None
        if TRACE: logger.debug("<target")
        return self.__target
    
    @target.setter
    def target(self, coord):
        "Set target coordinates"
        if TRACE: logger.debug(">target set")
        try:
            RA = coord.RA*24./360
            dec = coord.dec
            self.__scope.TargetRightAscension = RA
            self.__scope.TargetDeclination = dec
        except:
            logger.warning("target set failed")
        self.__invalidateCache()
        if TRACE: logger.debug("<target set")

    @position.setter
    def position(self, coord):
        "Synchronize current position to parameter `coord`"
        if not isinstance(coord, Coordinate):
            raise TypeError("Parameter not a Coordinate")
        if TRACE: logger.debug(">position set")
        if not self.connected:
            logger.debug("not connected")
            if TRACE: logger.debug("<position set")
            return
        # convert degrees to hours
        logger.info("Syncing to %s"%(str(coord)))
        RA = coord.RA*24./360.
        dec = coord.dec
        separation = self.position - coord
        logger.info("Sync separation is %s"%deg2str(separation.degrees))
        self.__scope.SyncToCoordinates(RA, dec)
        sync_time = now = time.time()
        while (now - sync_time) < float(self.getProperty("syncMaxWait")):
            self.__invalidateCache()
            separation = self.position - coord
            if separation.arcminutes < float(self.getProperty("syncAccuracy")):
                break
            time.sleep(float(self.getProperty("syncAccuracy"))/10.0)
        if TRACE: logger.debug("<position set")

    @property
    def slewing(self):
        "Is the telescope currently slewing"
        if TRACE: logger.debug(">slewing")
        if not self.connected:
            if TRACE: logger.debug("<slewing")
            return False
        now = time.time()
        if now - self.__slewingTime > self._maxAge:
            logger.debug("request slewing attribute")
            try:
                wasSlewing = self.__slewing
                isSlewing = self.__scope.Slewing
                self.__slewingTime = now
                if wasSlewing and not isSlewing:
                    if self.__slewingStopTime == 0:
                        self.__slewingStopTime = now
                    if self.__slewingTime >= self.__slewingStopTime + float(self.getProperty("slewSettleTime")):
                        self.__slewing = isSlewing
                        self.__slewingStopTime = 0
                else:
                    self.__slewing = isSlewing
                self._operation_ok = False
            except:
                logger.error("ASCOM error reading slewing status")
                self._operation_ok = False
        if TRACE: logger.debug("<slewing")
        return self.__slewing

    @property
    def tracking(self):
        "Is the telescope tracking"
        if TRACE: logger.debug(">tracking")
        if not self.connected:
            if TRACE: logger.debug("<tracking")
            return False

        now = time.time()
        if now - self.__trackingTime > self._maxAge:
            try:
                logger.debug("request tracking status")
                self.__tracking = self.__scope.Tracking
                self.__trackingTime = now
                self._operation_ok = True
            except:
                self._operation_ok = False
                logger.error("ASCOM error reading tracking status")
        if TRACE: logger.debug("<tracking")
        return self.__tracking

    @tracking.setter
    def tracking(self, value):
        "Set the telescope tracking to 'value'"
        if not self.connected:
            return
        if TRACE: self.debug(">tracking set")
        self.__scope.Tracking = value
        self.__invalidateCache()
        if TRACE: self.debug("<tracking set")


    @property
    def canSetRARate(self):
        "Can the RA rate be set?"
        if not self.connected:
            return False
        else:
            return self.__scope.canSetRightAscensionRate

    @property
    def RightAscensionRate(self):
        "Right Ascensions rate in sec/sidereal sec"
        if not self.connected:
            return 0
        else:
            return self.__scope.RightAscensionRate

    @RightAscensionRate.setter
    def RightAscensionRate(self, value):
        "Set Right Ascensions rate to 'value' in sec/sidereal sec"
        if not self.connected:
            return
        else:
            self.__scope.RightAscensionRate = float(value)
    

    @property
    def pierSide(self):
        "Which side of pier is the scope, 0=looking west, 1=looking east"
        if not self.connected:
            return 0
        if self.__scopeIFVersion < 2:
            return 0
        return self.__scope.SideOfPier

    @property
    def parked(self):
        "Is telescope parked"
        if TRACE: logger.debug(">parked")
        if not self.connected:
            if TRACE: logger.debug("<parked")
            return True
        if self.__scopeIFVersion < 2:
            return False # v1 ASCOM cannot park/unpark
        now = time.time()
        try:
            if now - self.__parkedTime > self._maxAge:
                logger.debug("request parked status")
                self.__parked = self.__scope.AtPark
                self.__parkedTime = now
        except: # Getting parked status fails, assume V1 driver
            self.__scopeIFVersion = 1
        if TRACE: logger.debug("<parked")
        return self.__parked

    @parked.setter
    def parked(self, state):
        "Park and Unpark scope"
        if not self.connected:
            return
        return # v1 ASCOM cannot park/unpark
        if TRACE: logger.debug(">park")
        if state:
            self.__scope.Park()
        else:
            self.__scope.Unpark()
        self.__invalidateCache()
        if TRACE: logger.debug("<park")

    def slewTo(self, coord):
        "Slew telescope to coord"
        if not isinstance(coord, Coordinate):
            raise TypeError("Parameter not a Coordinate")
        if not self.connected:
            return
        self.target = coord
        RA = coord.RA*24./360
        dec = coord.dec
        self.__scope.SlewToCoordinates(RA, dec)
        self.__invalidateCache()
        

    def slewToAsync(self, coord):
        "Slew telescope to coord, return as soon as possible"
        if not isinstance(coord, Coordinate):
            raise TypeError("Parameter not a Coordinate")
        if not self.connected:
            return
        self.target = coord
        RA = coord.RA*24./360
        dec = coord.dec
        if self.__scope.CanSlewAsync:
            self.__scope.SlewToCoordinatesAsync(RA, dec)
        else:
            self.__scope.SlewToCoordinates(RA, dec)
        self.__invalidateCache()

    def destinationPierSide(self, coord):
        "Is the `coord` on looking west (0) or looking east (1) pier side"
        if not isinstance(coord, Coordinate):
            raise TypeError("Parameter not a Coordinate")
        if not self.connected:
            return 0
        RA = coord.RA*24./360
        dec = coord.dec
        rv = self.__scope.DestinationSideOfPier(RA, dec)
        if type(rv) == tuple:
            return rv[0]
        else:
            return rv

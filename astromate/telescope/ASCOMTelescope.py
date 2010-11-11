"""ASCOMTelescope
Interface for ASCOM telescope
"""

from ..ITelescope import ITelescope
from ..units import Coordinate
from win32com.client import Dispatch

class ASCOMTelescope(ITelescope):
	def __init__(self):
		super(ASCOMTelescope, self).__init__()
		self.__chooser = Dispatch("DriverHelper.Chooser")
		self.__chooser.DeviceType = "Telescope"
		self.__scopeName = None
		self.__scope = None
	
	def __del__(self):
		super(ASCOMTelescope, self).__del__()

	@property
	def connected(self):
		"Is the telescope connected"
		if not self.__scope:
			return False
		return self.__scope.Connected

	def _connect(self):
		"Connect the scope"
		if self.__scope:
			if not self.__scope.Connected:
				self.__scope.Connected = True
			return
		if not self.__scopeName:
			self.__scopeName = self.__chooser.Choose()
			if not self.__scopeName: # Canceled
				return
		self.__scope = Dispatch(self.__scopeName)
		self.__scope.Connected = True

	@connected.setter
	def connected(self, value):
		"Connect or disconnect telescope"
		if value == self.connected:
			return
		if value:
			self._connect()
		self.__scope.Connected = value

	@property
	def position(self):
		"Current assumed position or None if not known"
		if not self.connected:
			return None
		# convert RA from hours to degrees
		RA = self.__scope.RightAscension*360./24
		dec = self.__scope.Declination
		return Coordinate(RA, dec)

	@property
	def target(self):
		"Target coordinates or None if not known:"
		if not self.connected:
			return None
		# convert RA from hours to degrees
		try:
			RA = self.__scope.TargetRightAscension*360./24
			dec = self.__scope.TargetDeclination
			return Coordinate(RA, dec)
		except:
			return None

	@position.setter
	def position(self, coord):
		"Synchronize current position to parameter `coord`"
		if not isinstance(coord, Coordinate):
			raise TypeError("Parameter not a Coordinate")
		if not self.connected:
			return
		# convert degrees to hours
		RA = coord.RA*24./360
		dec = coord.dec
		self.__scope.SyncToCoordinates(RA, dec)


	@property
	def slewing(self):
		"Is the telescope currently slewing"
		if not self.connected:
			return False
		return self.__scope.Slewing

	@property
	def tracking(self):
		"Is the telescope tracking"
		if not self.connected:
			return False
		return self.__scope.Tracking

	@property
	def pierSide(self):
		"Which side of pier is the scope, 0=looking west, 1=looking east"
		if not self.connected:
			return 0
		return self.__scope.SideOfPier

	@property
	def parked(self):
		"Is telescope parked"
		if not self.connected:
			return True
		return self.__scope.AtPark

	@parked.setter
	def parked(self, state):
		"Park and Unpark scope"
		if not self.connected:
			return
		if state:
			self.__scope.Park()
		else:
			self.__scope.Unpark()

	def slewTo(self, coord):
		"Slew telescope to coord"
		if not isinstance(coord, Coordinate):
			raise TypeError("Parameter not a Coordinate")
		if not self.connected:
			return
		RA = coord.RA*24./360
		dec = coord.dec
		self.__scope.SlewToCoordinates(RA, dec)
		

	def slewToAsync(self, coord):
		"Slew telescope to coord, return as soon as possible"
		if not isinstance(coord, Coordinate):
			raise TypeError("Parameter not a Coordinate")
		if not self.connected:
			return
		RA = coord.RA*24./360
		dec = coord.dec
		if self.__scope.CanSlewAsync:
			self.__scope.SlewToCoordinatesAsync(RA, dec)
		else:
			self.__scope.SlewToCoordinates(RA, dec)

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

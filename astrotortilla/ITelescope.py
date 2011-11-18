"""ITelescope
Interface for simple telescope tasks
"""

from Configurations import Configurable
from units import Coordinate, Separation

class ITelescope(Configurable):
	def __init__(self):
		super(ITelescope, self).__init__()
	
	def __del__(self):
		super(ITelescope, self).__del__()

	@property
	def connected(self):
		"Is the telescope connected"
		return False

	@connected.setter
	def connected(self, value):
		"Connect or disconnect telescope"
		pass

	@property
	def position(self):
		"Current assumed position or None if not known"
		return None

	@position.setter
	def position(self, coord):
		"Synchronize current position to parameter `coord`"
		pass

	@property
	def target(self):
		"Target coordinates or None if not known:"
		return None

	@property
	def slewing(self):
		"Is the telescope currently slewing"
		return False

	@property
	def tracking(self):
		"Is the telescope tracking"
		return False

	@tracking.setter
	def tracking(self, value):
		"Set the telescope tracking to 'value'"
		pass

	@property
	def canSetRARate(self):
		"Can the RA rate be set?"
		return False

	@property
	def RightAscensionRate(self):
		"Right Ascensions rate in sec/sidereal sec"
		return 0

	@RightAscensionRate.setter
	def RightAscensionRate(self, value):
		"Set Right Ascensions rate to 'value' in sec/sidereal sec"
		pass
	
	@property
	def pierSide(self):
		"Which side of pier is the scope, 0=looking west, 1=looking east"
		return 0

	@property
	def parked(self):
		"Is telescope parked"
		return True

	@parked.setter
	def parked(self, state):
		"Park and Unpark scope"
		pass

	def slewTo(self, coord):
		"Slew telescope to coord"
		pass

	def slewToAsync(self, coord):
		"Slew telescope to coord, return as soon as possible"
		pass

	def destinationPierSide(self, coord):
		"Is the `coord` on looking west (0) or looking east (1) pier side"
		return 0

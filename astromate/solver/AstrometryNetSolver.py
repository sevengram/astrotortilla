from ..IPlateSolver import IPlateSolver, Solution
from ..units import Coordinate
import subprocess, os, os.path, time, tempfile, shutil, threading
# vim: set fileencoding=UTF-8 :
# -*- coding: UTF-8 -*-

#TODO: use property list properties for solving instead of current hack

PROPERTYLIST = {
		"downscale":("Downscaling", int, "Image downscaling factor" ,"", 2),
		"configfile":("Backend config", str, "Cygwin path to backend config file", "", "/usr/local/astrometry/etc/backend.cfg"),
		"searchradius":("Search radius", float, "Radius of search area in degrees", "0..180", 180),
		"scale_low":("Scale minimum", float, "Image scale lower bound", "", 0),
		"scale_max":("Scale maximum", float, "Image scale upper bound", "", 179),
		"scale_units":("Scale units", str, "View scale size units", "arcminwidth, degwidth, arcsecperpix", "degwidth"),
		"scale_xrefine":("Scale refinement", float, "Image scale refinement factor", "0 to turn off", 0.1),
		"xtra":("Custom options", str, "Additional custom options", "", ""),
		}

def ThreadedReader(pipe, outputList, terminator):
	while not terminator.is_set():
		line = pipe.readline()
		outputList.insert(0, line)

class AstrometryNetSolver(IPlateSolver):
	"PlateSolver using astrometry.net solver"
	def __init__(self, workDirectory=None, cygShell='C:\\cygwin\\bin\\bash --login -c "%s"'):
		super(AstrometryNetSolver, self).__init__()
		self.propertyList = PROPERTYLIST
		self.__found = False
		self.__solution = None
		self.__timeout = 300
		self.__cygShell = cygShell
		self.__wd = workDirectory
		self.__counter = 0
		self.__wdCreated = False
		self.__callback = None
		self.__abort = False
		if not workDirectory:
			self.__wd = tempfile.mkdtemp(prefix="solver")
			self.__wdCreated = True
		if not os.path.exists(self.__wd):
			os.mkdir(self.__wd)
			self.__wdCreated = True
		if not os.path.isdir(self.__wd):
			raise "Work directory exists and is not a directory"
	
	def __del__(self):
		try:
			if self.__wdCreated:
				shutil.rmtree(self.__wd)
		except:
			pass

	def __execute(self, command):
		if 0: print ("Executing: %s"%command)
		if self.__callback:
			stderrPipe = subprocess.STDOUT
		else:
			stderrPipe = subprocess.PIPE
		shell = subprocess.Popen(self.__cygShell%command, shell=False, bufsize=1,
				stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=stderrPipe)
		if self.__callback:
			# Loop until child exits
			stdoutList = []
			terminator = threading.Event()
			reader = threading.Thread(target=ThreadedReader, args=(shell.stdout, stdoutList, terminator))
			reader.start()
			while shell.poll() == None:
				if stdoutList:
					self.__callback(stdoutList.pop())
				if self.__abort:
					terminator.set()
					shell.kill()
					reader.join()
					return [None, None]
				time.sleep(0.1)
			# Pipe whatever is left after child exit
			terminator.set()
			reader.join()
			map(self.__callback, stdoutList)
		else:
			return shell.communicate()


	@property
	def hasSolution(self):
		return self.__found

	@property
	def solution(self):
		return self.__solution

	@property
	def timeout(self):
		return self.__timeout

	@timeout.setter
	def timeout(self, value):
		self.__timeout = value

	def solve(self, imagePath, target=None, targetRadius=None, minFov=None, maxFov=None, callback = None):
		self.__callback = callback
		workDir = os.path.join(self.__wd, str(self.__counter)).replace("\\", "/")
		imageBase = os.path.splitext(os.path.basename(imagePath))[0].replace("\\", "/")
		resultRoot = os.path.join(workDir, imageBase).replace("\\", "/")
		imagePath = imagePath.replace("\\", "/")
		options=[]
		if target:
			if targetRadius:
				t_radius = targetRadius
			else:
				t_radius = self.getProperty("searchradius")
			options.append("-3 %f -4 %f -5 %f"%(target.RA, target.dec, t_radius))
		options.append("-b `cygpath %s`"%(self.getProperty("configfile").replace("\\", "/")))
		options.append("%s"%(self.getProperty("xtra")))
		options.append("-L %s"%(minFov or self.getProperty("scale_low")))
		options.append("-H %s"%(maxFov or self.getProperty("scale_max")))
		options.append("-u %s"%(self.getProperty("scale_units")))
		r=self.__execute('solve-field -z %d %s --no-plot -D `cygpath %s` `cygpath %s`'%(int(self.getProperty("downscale")), " ".join(options), workDir, imagePath))
		self.__callback = None
		if r and len(r)>1 and r[1]: print(r[1])
		wcsInfo=[]

		if os.path.exists(resultRoot+".solved") and\
				open(resultRoot+".solved", "rb").read()==b'\x01':
			output, errors = self.__execute('wcsinfo `cygpath %s`/%s.wcs'%(workDir, imageBase))
			if errors: print(errors)
			self.__wcsInfo = dict(
					[(e[0], self.__parseValue(e[1])) for e in
						[x.split(None,1) for x in output.decode().split("\n") if x.strip()]
					]
					)
			center = Coordinate(self.__wcsInfo["ra_center"], self.__wcsInfo["dec_center"])
			hFOV = float(self.__wcsInfo["fieldw"])
			vFOV = float(self.__wcsInfo["fieldh"])
			vunits = self.__wcsInfo["fieldunits"]
			if vunits == "degrees":
				pass
			elif vunits == "arcminutes":
				hFOV /= 60.
				vFOV /= 60.
			elif vunits == "arcseconds":
				hFOV /= 3600. 
				vFOV /= 3600. 
			self.__solution = Solution(center,
							self.__wcsInfo["orientation_center"],
							self.__wcsInfo["parity"],
							hFOV, vFOV,
							wcsInfo = self.__wcsInfo
						)
			self.__found = True
			if self.getProperty("scale_xrefine") > 0:
				refinement = float(self.getProperty("scale_xrefine")) + 1
				scaleUnits = self.getProperty("scale_units")
				if scaleUnits == "degwidth":
					self.setProperty("scale_low", hFOV/refinement)
					self.setProperty("scale_max", hFOV*refinement)
				elif scaleUnits == "arcminwidth":
					self.setProperty("scale_low", hFOV*60/refinement)
					self.setProperty("scale_max", hFOV*60*refinement)
				elif scaleUnits == "arcsecperpix":
					aspp=float(self.__wcs["pixscale"])
					self.setProperty("scale_low", aspp/refinement)
					self.setProperty("scale_max", aspp*refinement)

		else:
			self.__found = False
			del self.__solution 
			self.__solution = None

		shutil.rmtree(workDir)
		self.__counter += 1
		self.__abort = False
		return self.__solution

	def __parseValue(self, value):
		try:
			v=float(value)
		except:
			v=value
		return v

	def reset(self):
		self.__found = False
		self.__solution = None
		self.__abort = False
	
	def abort(self):
		self.__abort = True

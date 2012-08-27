import logging
logger = logging.getLogger("astrotortilla.AstrometryNetSolver")

from ..IPlateSolver import IPlateSolver, Solution
from ..units import Coordinate
import subprocess, os, os.path, time, tempfile, shutil, threading
import win32process
import win32con
from win32com.client import Dispatch
import gettext
t = gettext.translation('astrotortilla', 'locale', fallback=True)
_ = t.gettext

# vim: set fileencoding=UTF-8 : ts=4 sts=4 sw=4 et si
# -*- coding: UTF-8 -*-

DEBUG = 0 # 1 to enable some debug prints

PROPERTYLIST = {
        "downscale":(_("Downscaling"), int, _("Image downscaling factor") ,"", 0),
        "configfile":(_("Backend config"), str, _("Cygwin path to backend config file"), "", "/etc/astrometry/backend.cfg"),
        "searchradius":(_("Search radius"), float, _("Radius of search area in degrees"), "0..180", 180),
        "scale_low":(_("Scale minimum"), float, _("Image scale lower bound"), "", 0),
        "scale_max":(_("Scale maximum"), float, _("Image scale upper bound"), "", 179),
        "scale_units":(_("Scale units"), str, _("View scale size units"), _("arcminwidth, degwidth, arcsecperpix"), "degwidth"),
        "scale_xrefine":(_("Scale refinement"), float, _("Image scale refinement factor"), _("0 to turn off"), 0),
        "xtra":(_("Custom options"), str, _("Additional custom options"), "", "--sigma 1 --no-plot -N none"),
        "shell":(_("Cygwin shell"), str, _("Shell command for Cygwin execution"), "", 'C:\\cygwin\\bin\\bash --login -c "%s"'),
        "year_epoch":(_("JNow or J2000"), str, _("JNOW or J2000"), "", "JNOW"),
        }

def ThreadedReader(pipe, outputList, terminator):
    "Reader function to get output from subprocess asynchronously to main-thread"
    while not terminator.is_set():
        line = pipe.readline()
        outputList.insert(0, line)

class AstrometryNetSolver(IPlateSolver):
    "PlateSolver using astrometry.net solver"
    def __init__(self, workDirectory=None):
        super(AstrometryNetSolver, self).__init__()
        self.propertyList = PROPERTYLIST
        self.__found = False        # have a solution?
        self.__solution = None      # current solution
        self.__timeout = 300        # timeout for finding a solution
        self.__wd = workDirectory   # temporary working directory
        self.__counter = 0      # internal solution counter
        self.__wdCreated = None    # book-keeping on temp-dir clean-up responsibility
        self.__callback = None      # status update callback reference
        self.__abort = False        # has abort been requested?
        if not workDirectory:
            self.__wd = tempfile.mkdtemp(prefix="solver")
            self.__wdCreated = self.__wd
        if not os.path.exists(self.__wd):
            os.makedirs(self.__wd)
        if not os.path.isdir(self.__wd):
            raise "Work directory exists and is not a directory"
        try:
            self.__transform = Dispatch("ASCOM.Astrometry.Transform.Transform")
        except:
            logger.error("Failed to initialize ASCOM astrometric transformer, no epoch conversion available")
            self.__transform = None
    
    def __del__(self):
        del self.__transform
        try:
            if self.__wdCreated:
                shutil.rmtree(self.__wdCreated)
        except:
            pass

    @classmethod
    def getName(cls):
        return _("Local astrometry.net")

    def __execute(self, command):
        "Execute a command in cygwin shell"
        logger.debug("Executing: %s"%command)
        if self.__callback:
            stderrPipe = subprocess.STDOUT
        else:
            stderrPipe = subprocess.PIPE
        cygShell = self.getProperty("shell")

        si = subprocess.STARTUPINFO()
        si.dwFlags |= win32process.STARTF_USESHOWWINDOW
        si.wShowWindow = win32con.SW_HIDE
        shell = subprocess.Popen(cygShell%command, shell=False, bufsize=1,
                stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                stderr=stderrPipe, startupinfo=si)

        if self.__callback:
            # Loop until child exits
            stdoutList = []
            terminator = threading.Event()
            reader = threading.Thread(target=ThreadedReader, args=(shell.stdout, stdoutList, terminator))
            reader.start()
            while shell.poll() == None:
                if stdoutList:
                    self.__callback(stdoutList.pop())
                else:
                    self.__callback(None)
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
        else: # return (stdout, stderr) if no callback is defined.
            return shell.communicate()


    @property
    def hasSolution(self):
        "@return True if a solution was found"
        return self.__found

    @property
    def solution(self):
        "@return current solution object or None"
        return self.__solution

    @property
    def timeout(self):
        "@return int, current time-out value"
        return self.__timeout

    @timeout.setter
    def timeout(self, value):
        "@param value int, time-out for finding the solution"
        self.__timeout = int(value)

    def solve(self, imagePath, target=None, targetRadius=None, minFov=None, maxFov=None, callback = None):
        """Do plate solving for image, return True on success
        @param imagePath string, path to image to be solved
        @param target Coordinate(), optional guess at image center
        @param targetRadius float, target coordinate guess accuracy
        @param minFOV float, optional minimum field width in degrees
        @param maxFOV float, optional maximum field width in degrees
        @param callback function, optional function called periodically
        @return Solution() or None

        The callback function must be callable with a string argument and with explicit None.
        """
        self.__callback = callback
        self.__found = False
        # construct command line
        workDir = os.path.join(self.__wd, str(self.__counter)).replace("\\", "/")
        imageBase = os.path.splitext(os.path.basename(imagePath))[0].replace("\\", "/")
        resultRoot = os.path.join(workDir, imageBase).replace("\\", "/")
        imagePath = imagePath.replace("\\", "/")
        options=[]
        if target:
            if targetRadius:
                t_radius = float(targetRadius)
            else:
                t_radius = float(self.getProperty("searchradius"))
            options.append("-3 %f -4 %f -5 %f"%(target.RA, target.dec, t_radius))
        options.append("-b %s"%(self.getProperty("configfile").replace("\\", "/")))
        options.append("%s"%(self.getProperty("xtra")))
        options.append("-L %s"%(minFov or self.getProperty("scale_low")))
        options.append("-H %s"%(maxFov or self.getProperty("scale_max")))
        options.append("-u %s"%(self.getProperty("scale_units")))
        try:

            int(self.getProperty("downscale"))
            if int(self.getProperty("downscale")) > 1:
                options.append("-z %d"%int(self.getProperty("downscale")))
        except:
            pass


        r=self.__execute('solve-field %s -D \\"`cygpath -a \\"%s\\"`\\" \\"`cygpath -a \\"%s\\"`\\"'%(" ".join(options), workDir, imagePath))

        if r and len(r)>1 and r[1]: map(logger.info, r[1])
        wcsInfo=[]

        # solution resolution exists and a solution was found?
        if os.path.exists(resultRoot+".solved") and\
                open(resultRoot+".solved", "rb").read()==b'\x01':
            # inform a waiting user
            if self.__callback: self.__callback(_("Parsing results..."))
            self.__callback = None # clear callback, we want to capture output from the next

            output, errors = self.__execute('wcsinfo \\"`cygpath -a \\"%s\\"`/%s.wcs\\"'%(workDir, imageBase))
            if errors:
                if callback:
                    map(callback, errors)
                else:
                    map(logger.error, errors)

            # build a WCS info dict, make all numbers to floats
            self.__wcsInfo = dict(
                    [(e[0], self.__parseValue(e[1])) for e in
                        [x.split(None,1) for x in output.decode().split("\n") if x.strip()]
                    ]
                    )
            # construct solution center Coordinate
            ra, dec = self.__wcsInfo["ra_center"], self.__wcsInfo["dec_center"]
            center = Coordinate(ra, dec)
            if self.__transform and self.getProperty("year_epoch").lower() == "jnow":
                self.__transform.SetJ2000(center.RAhour, center.dec)
                center  = Coordinate(self.__transform.RAApparent/24.*360, self.__transform.DECApparent)
                

            # field of view in degrees
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

            # construct a Solution
            self.__solution = Solution(center,
                            self.__wcsInfo["orientation_center"],
                            self.__wcsInfo["parity"],
                            hFOV, vFOV,
                            wcsInfo = self.__wcsInfo
                        )
            self.__found = True

            # see if the property for image width should be refined based on solution
            if float(self.getProperty("scale_xrefine")) > 0:
                refinement = float(self.getProperty("scale_xrefine")) + 1
                scaleUnits = self.getProperty("scale_units")
                if scaleUnits == "degwidth":
                    self.setProperty("scale_low", hFOV/refinement)
                    self.setProperty("scale_max", hFOV*refinement)
                elif scaleUnits == "arcminwidth":
                    self.setProperty("scale_low", hFOV*60/refinement)
                    self.setProperty("scale_max", hFOV*60*refinement)
                elif scaleUnits == "arcsecperpix":
                    aspp=float(self.__wcsInfo["pixscale"])
                    self.setProperty("scale_low", aspp/refinement)
                    self.setProperty("scale_max", aspp*refinement)

        else:
            # No solution was found
            self.__found = False
            del self.__solution 
            self.__solution = None

        # Clean up and return
        try:
            if self.__wdCreated:
                shutil.rmtree(workDir)
        except:
            pass
        self.__counter += 1
        self.__abort = False
        return self.__solution

    def __parseValue(self, value):
        """Try to parse a value to float
        @param value anything
        @return float(value) or value
        """
        try:
            v=float(value)
        except:
            v=value
        return v

    def reset(self):
        "Reset solver state."
        self.__found = False
        self.__solution = None
        self.__abort = False
    
    def abort(self):
        "Abort current solver"
        self.__abort = True

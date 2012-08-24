"AstroTortilla main engine classes"
# vim: set fileencoding=UTF-8 encoding=UTF-8
# -*- coding: UTF-8 -*-

from libs.appdirs.appdirs import AppDirs
appdirs = AppDirs("AstroTortilla", "astrotortilla.sf.net")
import logging
logger = logging.getLogger("astrotortilla")
logger.setLevel(logging.DEBUG)
logFormatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')


import gettext, sys, codecs
import camera, solver, telescope
from IPlateSolver import IPlateSolver
from ICamera import ICamera
from ITelescope import ITelescope
from inspect import isclass, getmembers
import ConfigParser
import os, os.path
from time import time, sleep

from astrotortilla import CameraState
from astrotortilla.bookmark import Bookmark
from astrotortilla.units import Coordinate, Separation, deg2dms, deg2hms

from win32api import LoadResource
from StringIO import StringIO

t = gettext.translation('astrotortilla', 'locale', fallback=True)
_ = t.gettext

CFGFILE = os.path.join(appdirs.user_data_dir, "astrotortilla.cfg")
CFGDEFAULTS = {
        "Session":
            {
                "iterlimitcount":"5",
                "iterlimitarcmin":"1.0",
                "exposure":"5",
                "solver":"",
                "syncmode":"0",
            },
        "Bookmarks": {"count":"0"},
        "AstroTortilla": 
            {
                "settings_path":"", 
                "log_file":"",
                "log_level":"ERROR",
            }
        }

logLevels={
        "FATAL":logging.FATAL,
        "CRITICAL":logging.CRITICAL,
        "ERROR":logging.ERROR,
        "WARNING":logging.WARNING,
        "INFO":logging.INFO,
        "DEBUG":logging.DEBUG,
        }
class Status(object):
    Idle = 0
    Slewing = 1
    Capturing = 2
    Solving = 3
    Error = -1

class TortillaEngine(object):
    def __init__(self):
        ch = logging.StreamHandler()
        ch.setLevel(logging.ERROR)
        ch.setFormatter(logFormatter)
        logger.addHandler(ch)

        self.__workDirectory = None

        self.__telescopes = self._list_subclasses(ITelescope, telescope)
        self.__telescope = None
        self.__telescopeName = _(u'Not selected')

        self.__solvers = self._list_subclasses(IPlateSolver, solver)
        self.__solver = None
        self.__solverName = _(u'Not selected')

        self.__cameras = self._list_subclasses(ICamera, camera)
        self.__camera = None
        self.__cameraName = _(u'Not selected')

        self.__bookmarks = []
        
        self.__status = [Status.Idle]
        self.__abortAction = False   # did user want to abort current action?
        if sys.version_info[0] >= 2 and sys.version_info[1] >= 7:
            self.config = ConfigParser.SafeConfigParser(allow_no_value = True)
        else:
            self.config = ConfigParser.SafeConfigParser()
        for section in CFGDEFAULTS:
            self.config.add_section(section)
            for k,v in CFGDEFAULTS[section].items():
                self.config.set(section, k, v)
        self.__progressCB = []
        self.__statusCB = []
        self.loadConfig(CFGFILE)

        logFile = self.config.get("AstroTortilla", "log_file").strip()
        if logFile:
            if not os.path.isabs(logFile):
                logFile = os.path.join(appdirs.user_log_dir, logFile)
                try:
                    os.makedirs(os.path.dirname(logFile))
                except: pass
            logHandler = logging.FileHandler(logFile)
            logHandler.setLevel(logLevels[self.config.get("AstroTortilla", "log_level")])
            logHandler.setFormatter(logFormatter)
            logger.addHandler(logHandler)
            logger.info("Log started")
        self.solution = None
        self.lastCorrection = None

    @property
    def logger(self):
        return logger

    @property
    def version(self):
        version = ""
        try:
            version = LoadResource(0, u'VERSION', 1)
        except:
            pass
        if not version.strip():
            version = "unversioned"
        return version

    def loadConfig(self, fileName=None):
        if fileName:
            try:
                with codecs.open(fileName, mode="rb", encoding="UTF-8") as conffile:
                    self.config.readfp(conffile)
                self.config.set("AstroTortilla", "settings_path", os.path.abspath(os.path.dirname(fileName)))
                self.__configure(self.__telescope, "Telescope-%s"%self.__telescopeName)
                self.__loadCameraConfig()
                self.__configure(self.__solver, "Solver-%s"%self.__solverName)
            except:
                pass # No config file necessarily exists on first start
        default_path=None
        try:
            default_path = self.config.get("AstroTortilla", "settings_path")
        except:
            if not self.config.has_section("AstroTortilla"):
                self.config.add_section("AstroTortilla")
        if not (default_path and os.access(default_path, os.W_OK)):
            data_dir = appdirs.user_data_dir
            os.makedirs(data_dir)
            self.config.set("AstroTortilla", "settings_path", data_dir)
        if self.config.has_option("Session", "solver"):
            self.selectSolver(self.config.get("Session", "solver"))
        if self.config.has_option("Session", "camera"):
            self.selectCamera(self.config.get("Session", "camera"))
        if self.config.has_section("Bookmarks"):
            bmlist = []
            bm_count = self.config.getint("Bookmarks", "count")
            for i in xrange(bm_count):
                try:
                    bm = Bookmark.from_string(self.config.get("Bookmarks", "bm-%d"%i))
                    bmlist.append(bm)
                except:
                    pass
            self.__bookmarks = bmlist
        self.__workDirectory = self.config.get("AstroTortilla", "work_directory") if self.config.has_option("AstroTortilla", "work_directory") else None

    def __loadCameraConfig(self):
        "Assign camera specific configuration to current camera"
        if not self.__camera or not self.__cameraName:
            return
        self.__configure(self.__camera, "Camera-%s"%self.__cameraName)
        if self.config.has_option("Camera-%s"%self.__cameraName, "binning"):
            self.__camera.binning = self.config.getint("Camera-%s"%self.__cameraName, "binning")
        if self.config.has_option("Camera-%s"%self.__cameraName, "camera"):
            self.__camera.camera = self.config.get("Camera-%s"%self.__cameraName, "camera")
    
    def __saveCameraConfig(self):
        "Save current camera properties and other settings"
        if self.__camera and self.__cameraName:
            self.__saveObjConfig(self.__camera, "Camera-%s"%self.__cameraName)
            self.config.set("Camera-%s"%self.__cameraName, "binning", str(self.__camera.binning))
            if self.__camera.camera:
                self.config.set("Camera-%s"%self.__cameraName, "camera", str(self.__camera.camera))

    def listCameras(self):
        return self.__cameras.items()

    def selectCamera(self, camName):
        self.deselectCamera()
        if camName in self.__cameras:
            self.__camera = self.__cameras[camName]()
            self.__camera.workingDirectory = self.__workDirectory
            self.__cameraName = camName
            self.__loadCameraConfig()
        self.config.set("Session", "camera", camName)

    def deselectCamera(self):
        if self.__camera:
            self.__saveCameraConfig()
            del self.__camera

        self.__camera = None
        self.__cameraName = None

    def getCamera(self):
        return self.__camera

    def getCameraName(self):
        return self.__cameraName

    def listSolvers(self):
        return self.__solvers.items()

    def selectSolver(self, solverName):
        self.deselectSolver()
        if solverName in self.__solvers:
            self.__solver = self.__solvers[solverName](self.__workDirectory)
            self.__solverName = solverName
            self.__configure(self.__solver, "Solver-%s"%self.__solverName)
        self.config.set("Session", "solver", solverName)

    def deselectSolver(self):
        if self.__solver:
            self.__saveObjConfig(self.__solver, "Solver-%s"%self.__solverName)
            del self.__solver
        self.__solver = None
        self.__solverName = None

    def getSolver(self):
        return self.__solver

    def getSolverName(self):
        return self.__solverName


    def listTelescopes(self):
        return self.__telescopes.items()

    def selectTelescope(self, telescopeName):
        self.deselectTelescope()
        if telescopeName in self.__telescopes:
            self.__telescope = self.__telescopes[telescopeName]()
            self.__telescopeName = telescopeName
            self.__configure(self.__telescope, "Telescope-%s"%self.__telescopeName)
            self.__telescope.connected = True

    def deselectTelescope(self):
        if self.__telescope:
            self.__saveObjConfig(self.__telescope, "Telescope-%s"%self.__telescopeName)
            del self.__telescope
        self.__telescope = None
        self.__telescopeName = None

    def getTelescope(self):
        return self.__telescope

    def setExposure(self, value):
        self.config.set("Session", "exposure", str(float(value)))

    def getExposure(self):
        return self.config.getfloat("Session", "exposure")

    def subscribeStatus(self, callback):
        "Add @callback as a status callback function"
        if not callable(callback):
            raise ValueError("Parameter for callback must be a callable function accepting a single string value.")
        if callback not in self.__statusCB:
            self.__statusCB.append(callback)

    def subscribeProgress(self, callback):
        """Add @callback as a progress callback function accepting a float 0.0 .. 100.0
        activity (or None for undefined activity) and an optional status string"""
        if not callable(callback):
            raise ValueError("Parameter for callback must be a callable function accepting a float and string.")
        if callback not in self.__progressCB:
            self.__progressCB.append(callback)

    def _list_subclasses(self, baseClass, moduleRef):
        """return list of (className, classRef) for sub-classes of baseClass
        found in moduleRef"""
        rval = {}
        for module in moduleRef.__all__:
            fqmn = moduleRef.__name__+"."+module
            mod_ = __import__(fqmn, globals(), locals())
            subclasses = getmembers(sys.modules[fqmn], lambda m: isclass(m) and issubclass(m, baseClass) and m is not baseClass)
            for className, classRef in subclasses:
                rval[className] = classRef
        return rval
        
    
    def setStatus(self, status):
        if type(status) not in (str, unicode): return
        failed = []
        for callback in self.__statusCB:
            try:
                callback(status)
            except:
                failed.append(callback)
        if status.strip():
            logger.info(status)
        [self.__callback.remove(cb) for cb in failed]

    def setProgress(self, progress, status=None):
        if progress and type(progress) not in (int, float): return
        if status != None and type(status) not in (str, unicode): return
        failed = []
        for callback in self.__progressCB:
            try:
                callback(progress, status)
            except:
                failed.append(callback)
        [self.__callback.remove(cb) for cb in failed]

    def __configure(self, obj, name):
        "Configure `obj` from config if `name` is found as a section"
        if obj and self.config.has_section(name):
            for k,v in self.config.items(name):
                try:
                    obj.setProperty(k,v)
                except:
                    pass
                    
    def __saveObjConfig(self, obj, name):
        "Save `obj` properties as section `name` in config structure"
        if not self.config.has_section(name):
            self.config.add_section(name)
                
        defaultConfig = obj.configuration
        for k,v in defaultConfig.items():
            self.config.set(name, k, unicode(v).replace("%", "%%"))

    def saveConfig(self, filename=CFGFILE):
        try:
            self.config.set("AstroTortilla", "settings_path", os.path.abspath(os.path.dirname(filename)))
            if self.__telescope and self.__telescopeName:
                self.__saveObjConfig(self.__telescope, "Telescope-%s"%self.__telescopeName)
            if self.__camera and self.__cameraName:
                self.__saveCameraConfig()
            if self.__solver and self.__solverName:
                self.__saveObjConfig(self.__solver, "Solver-%s"%self.__solverName)
            if self.__bookmarks:
                self.config.remove_section("Bookmarks") ## clear old bookmarks from settings
                self.config.add_section("Bookmarks")
                bmi = 0
                for bookmark in self.__bookmarks:
                    self.config.set("Bookmarks", "bm-%d"%(bmi), bookmark.to_string().replace("%", "%%"))
                    bmi += 1
                self.config.set("Bookmarks", "count", "%d"%bmi)
            if not os.path.exists(os.path.dirname(filename)):
                os.makedirs(os.path.dirname(filename))
            with codecs.open(filename, mode="wb", encoding="UTF-8") as conffile:
                self.config.write(conffile)
        except:
            import traceback
            logger.error(traceback.format_exc())

    def addBookmark(self, bookmark):
        if type(bookmark) != Bookmark:
            return
        self.__bookmarks.append(bookmark)

    @property
    def bookmarks(self):
        return self.__bookmarks

    @property
    def isReady(self):
        rv = True
        if not self.__camera or\
           not self.__solver or\
           not self.__telescope or\
           (self.__telescope != None and self.__telescope.slewing):
            rv = False
        if not self.__telescope.tracking:
            rv = False
        return rv

    @property    
    def isBusy(self):
        return len(self.__status)>1

    def abort(self):
        "Try to abort current action"
        if self.__solver:
            self.__solver.abort()
        self.__abortAction=True

    def clearStatus(self):
        "Clear current errors and aborted status"
        self.__abortAction = False
        self.__status = self.__status[:1]

    def solveImage(self, imgFile, blind=False):
        "Return Solution object for a given image"
        if not self.__solver:
            self.setStatus(_("ERROR: No solver selected."))
            return None
        self.solution = None
        self.__status.append(Status.Solving)
        self.setStatus(_("Solving..."))
        startTime = time()
        # solve based on current location if telescope is tracking, otherwise pure blind solve
        try:
            if not blind and self.__telescope and self.__telescope.tracking:
                self.solution = self.__solver.solve(imgFile, target=self.__telescope.position, targetRadius=None, callback=self.setStatus)
            else:
                self.solution = self.__solver.solve(imgFile, callback=self.setStatus)
            self.__status.pop()
        except Exception, detail: # Silent errors
            import traceback
            logger.error(traceback.format_exc())
        if self.solution:
            self.setStatus(_("Solved in %.1fs")%(time()-startTime))
        else:
            self.setStatus(_("No solution in %.1fs")%(time()-startTime))
        return self.solution


    def solveCamera(self, exposure=None):
        "Return Solution object for current camera view"
        if not self.__camera:
            self.setStatus(_("ERROR: No camera connected."))
            return None
        self.__status.append(Status.Capturing)

        img = None
        try:
            self.setStatus(_("Connecting to camera..."))
            if not self.__camera.canAutoConnect and not self.__camera.connected:
                self.__camera.connected = True
            if self.__camera.needsCameraName and not self.__camera.camera:
                self.__camera.camera = self.__camera.cameraList[0]
            exposure = exposure or self.getExposure()
            if not self.__camera.connected:
                self.setStatus(_("ERROR: No camera connected."))
                self.__status.pop()
                return None
            self.setStatus(_("Exposing: %.2f seconds")%exposure)
            self.__camera.capture(exposure)
            tEnd = time() + exposure
            while not self.__camera.imageReady and self.__camera.cameraState not in (CameraState.Error, ):
                sleep(0.1)
                tLeft = tEnd - time()
                if tLeft >= 0:
                    self.setStatus(_("Exposing: %.2f seconds")%tLeft)
                    self.setProgress((1. - tLeft/exposure)*100)
                else:
                    self.setStatus(_("Waiting for camera"))
                if self.__abortAction: break;
            self.setProgress(-1)
            if self.__camera.cameraState == CameraState.Error:
                self.__abortAction = True
            if self.__camera.imageReady and not self.__abortAction:
                self.setStatus(_("Reading image from camera"))
                img = self.__camera.getImage()
            elif self.__abortAction:
                self.setStatus(_("Aborted."))
            else:
                self.setStatus(_("Camera did not produce an image to solve"))
        except Exception, detail:
            self.setStatus(_("An error occurred."))
            import traceback
            logger.error(traceback.format_exc())
        self.setStatus(_(""))
        solution = None
        if img:
            solution = self.solveImage(img)

        self.__status.pop()
        self.__abortAction = False
        return solution

    def gotoImage(self, imageFile, limit=0, threshold=0.0):
        "Goto solved image"
        if not self.__telescope:
            self.setStatus(_("ERROR: No telescope connected."))
            return None
        newTarget = self.solveImage(imageFile, blind=True)
        if newTarget:
            self.__telescope.slewToAsync(newTarget.center)
            return self.gotoCurrentTarget(limit, threshold)
        return None

    def gotoPosition(self, coords, limit=0, threshold=0.0):
        "Goto a defined coordinate position"
        if not self.__telescope:
            self.setStatus(_("ERROR: No telescope connected."))
            return None
        self.__telescope.slewToAsync(coords)
        return self.gotoCurrentTarget(limit, threshold)

    def gotoCurrentTarget(self, limit=0, threshold=0.0):
        "Correct slew to telescope target, retry until within 'threshold' arc minutes, no more than 'limit' times"
        if not self.__telescope:
            self.setStatus(_("ERROR: No telescope connected."))
            return None
        self.__status.append(Status.Slewing)
        self.setStatus(_("Waiting for scope to stop"))
        startPosition = self.__telescope.position
        while self.__telescope.slewing:
            sleep(0.2)
            try:
                targetPos = self.__telescope.target
                startDistance = startPosition - targetPos
                distance = self.__telescope.position - targetPos
                self.setProgress((1. - distance.arcminutes/startDistance.arcminutes)*100)
            except:
                pass
        self.setProgress(-1)
        targetPos = self.__telescope.position
        currentSolution=self.solveCamera()
        if not currentSolution:
            self.__status.pop()
            self.lastCorrection = None
            return None

        limit = limit or self.config.getint("Session", "iterlimitcount")
        threshold = threshold or self.config.getfloat("Session", "iterlimitarcmin")

        pointError = targetPos - currentSolution.center
        self.lastCorrection = pointError

        retries = 0
        while (retries < limit) and (pointError.arcminutes > threshold):
            self.setStatus(_("Re-centering..."))
            self.__telescope.position = currentSolution.center
            sync_delta = self.__telescope.position - currentSolution.center
            if sync_delta.arcminutes > threshold:
                raise Exception("ASCOM Telescope sync error")
            self.__telescope.slewToAsync(targetPos)
            while self.__telescope.slewing:
                sleep(0.1)
                distance = self.__telescope.position - targetPos
                self.setProgress((1. - distance.arcminutes/pointError.arcminutes)*100)
            self.setProgress(-1)
            currentSolution=self.solveCamera()
            if not currentSolution:
                self.__status.pop()
                return None

            pointError = targetPos - currentSolution.center
            self.lastCorrection = pointError
            retries += 1
        self.__status.pop()
        return pointError

def testEngine():
    t = TortillaEngine()
    import sys
    t.subscribeStatus(sys.stderr.write)
    t.selectSolver(t.listSolvers()[-1][0])
    t.selectCamera(t.listCameras()[0][0])
    t.selectTelescope(t.listTelescopes()[0][0])
    t.getCamera().connected=True
    t.getSolver().setProperty("scale_low", 90)
    t.getSolver().setProperty("scale_max", 120)
    t.getSolver().setProperty("scale_units", "arcminwidth")
    t.getSolver().setProperty("downscale", 0)
    t.getSolver().setProperty("xtra", "--sigma=150")
    t.getCamera().binning=2
    return t.gotoImage("D:/Astro/2011-10-21/Veil_0000_001Ha.fit")

if __name__ == "__main__":
    testEngine()

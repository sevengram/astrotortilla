"""
AstroTortilla main engine classes
"""

import logging
import gettext
import sys
import codecs
import ConfigParser
import os
import os.path
import time
from inspect import isclass, getmembers

from libs.appdirs.appdirs import AppDirs
from win32api import LoadResource
import camera
import solver
import telescope
from IPlateSolver import IPlateSolver
from ICamera import ICamera
from ITelescope import ITelescope
from astrotortilla import CameraState
from astrotortilla.bookmark import Bookmark

appdirs = AppDirs("AstroTortilla", "astrotortilla.sf.net")
logger = logging.getLogger("astrotortilla")
logger.setLevel(logging.DEBUG)
logFormatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

t = gettext.translation('astrotortilla', 'locale', fallback=True)
_ = t.gettext

CFGFILE = os.path.join(appdirs.user_data_dir, "astrotortilla.cfg")
CFGDEFAULTS = {
    "Session":
        {
            "iterlimitcount": "5",
            "iterlimitarcmin": "1.0",
            "exposure": "5",
            "solver": "",
            "syncmode": "0",
        },
    "Bookmarks": {"count": "0"},
    "AstroTortilla":
        {
            "settings_path": "",
            "log_file": "",
            "log_level": "ERROR",
        }
}

logLevels = {
    "FATAL": logging.FATAL,
    "CRITICAL": logging.CRITICAL,
    "ERROR": logging.ERROR,
    "WARNING": logging.WARNING,
    "INFO": logging.INFO,
    "DEBUG": logging.DEBUG,
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
        self.__telescopeName = _('Not selected')

        self.__solvers = self._list_subclasses(IPlateSolver, solver)
        self.__solver = None
        self.__solverName = _('Not selected')

        self.__cameras = self._list_subclasses(ICamera, camera)
        self.__camera = None
        self.__cameraName = _('Not selected')

        self.__bookmarks = []

        self.__status = [Status.Idle]
        self.__abortAction = False  # did user want to abort current action?
        if sys.version_info[0] >= 2 and sys.version_info[1] >= 7:
            self.config = ConfigParser.SafeConfigParser(allow_no_value=True)
        else:
            self.config = ConfigParser.SafeConfigParser()
        for section in CFGDEFAULTS:
            self.config.add_section(section)
            for k, v in CFGDEFAULTS[section].items():
                self.config.set(section, k, v)
        self.__progressCB = []
        self.__statusCB = []
        self.loadConfig(CFGFILE)

        self.solution = None
        self.lastCorrection = None

    @property
    def logger(self):
        return logger

    @property
    def version(self):
        version = ""
        try:
            version = LoadResource(0, 'VERSION', 1).rstrip("0.")
            tag = self.version_tag
            if tag.strip():
                version += " " + tag
        except:
            pass
        if not version.strip():
            version = "unversioned"
        return version

    @property
    def version_tag(self):
        tag = ""
        try:
            tag = LoadResource(0, 'VERSIONTAG', 2)
        except:
            pass
        return tag

    def loadConfig(self, fileName=None):
        if fileName:
            try:
                with codecs.open(fileName, mode="rb", encoding="UTF-8") as conffile:
                    self.config.readfp(conffile)
                self.config.set("AstroTortilla", "settings_path", os.path.abspath(os.path.dirname(fileName)))
                self.__configure(self.__telescope, "Telescope-%s" % self.__telescopeName)
                self.__loadCameraConfig()
                self.__configure(self.__solver, "Solver-%s" % self.__solverName)
            except:
                pass  # No config file necessarily exists on first start

        # Create log-file if not defined yet
        logFile = None
        try:
            logFile = self.config.get("AstroTortilla", "log_file").strip()
        except:
            logger.warning("The log_file parameter value in config file is invalid.")
        if logFile:
            if not os.path.isabs(logFile):
                logFile = os.path.join(appdirs.user_log_dir, logFile)
            try:
                os.makedirs(os.path.dirname(logFile))
            except:
                pass
            exists = False
            for file_handler in filter(lambda h: isinstance(h, logging.FileHandler), tuple(logger.handlers)):
                if os.path.normpath(file_handler.baseFilename).lower() == os.path.normpath(logFile).lower():
                    exists = True
                    continue
                logger.removeHandler(file_handler)

            if not exists:
                logger.info("Starting logfile %s" % logFile)
                logHandler = logging.FileHandler(logFile)
                logHandler.setLevel(logLevels[self.config.get("AstroTortilla", "log_level")])
                logHandler.setFormatter(logFormatter)
                logger.addHandler(logHandler)
                logger.info("Log started")

        default_path = None
        try:
            default_path = self.config.get("AstroTortilla", "settings_path")
        except:
            if not self.config.has_section("AstroTortilla"):
                self.config.add_section("AstroTortilla")
        if not (default_path and os.access(default_path, os.W_OK)):
            data_dir = appdirs.user_data_dir
            try:
                os.makedirs(data_dir)  # fails if exists
            except:
                pass
            self.config.set("AstroTortilla", "settings_path", data_dir)
        if self.config.has_section("Bookmarks"):
            bmlist = []
            bm_count = self.config.getint("Bookmarks", "count")
            for i in xrange(bm_count):
                try:
                    bm = Bookmark.from_string(self.config.get("Bookmarks", "bm-%d" % i))
                    bmlist.append(bm)
                except:
                    pass
            self.__bookmarks = bmlist
        self.__workDirectory = self.config.get("AstroTortilla", "work_directory") if self.config.has_option(
            "AstroTortilla", "work_directory") else None
        if self.__workDirectory:
            try:
                logger.debug("work_directory set as %s" % self.__workDirectory)
                if not os.path.exists(self.__workDirectory):
                    os.makedirs(self.__workDirectory)
                if not os.path.isdir(self.__workDirectory):
                    logger.error("work_directory not set to a directory, using system temporary directory")
                    self.__workDirectory = None
                logger.debug("Testing if work_directory is writable")
                import tempfile
                tfn = tempfile.mktemp(dir=self.__workDirectory)
                logger.debug("Creating test-file %s" % tfn)
                tf = file(tfn, "w")
                tf.close()
                del tf
                os.remove(tfn)
                logger.debug("work_directory setting OK")
            except:
                logger.error("work_directory not accessible, using system temporary directory")
                self.__workDirectory = None
        if self.config.has_option("Session", "solver"):
            self.selectSolver(self.config.get("Session", "solver"))
        if self.config.has_option("Session", "camera"):
            self.selectCamera(self.config.get("Session", "camera"))

    def __loadCameraConfig(self):
        """Assign camera specific configuration to current camera"""
        if not self.__camera or not self.__cameraName:
            return
        self.__configure(self.__camera, "Camera-%s" % self.__cameraName)
        if self.config.has_option("Camera-%s" % self.__cameraName, "binning"):
            self.__camera.binning = self.config.getint("Camera-%s" % self.__cameraName, "binning")
        if self.config.has_option("Camera-%s" % self.__cameraName, "camera"):
            try:
                self.__camera.camera = self.config.get("Camera-%s" % self.__cameraName, "camera")
            except:
                pass

    def __saveCameraConfig(self):
        """Save current camera properties and other settings"""
        if self.__camera and self.__cameraName:
            self.__saveObjConfig(self.__camera, "Camera-%s" % self.__cameraName)
            self.config.set("Camera-%s" % self.__cameraName, "binning", str(self.__camera.binning))
            if self.__camera.camera:
                self.config.set("Camera-%s" % self.__cameraName, "camera", str(self.__camera.camera))

    def listCameras(self):
        return self.__cameras.items()

    def selectCamera(self, camName):
        self.deselectCamera()
        if camName in self.__cameras:
            self.__camera = self.__cameras[camName]()
            try:
                if self.__workDirectory is not None:
                    self.__camera.workingDirectory = self.__workDirectory
            except:
                import traceback
                logger.error(
                    "Setting working to '%s' directory failed: %s" % (self.__workDirectory, traceback.format_exc()))
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
            self.__configure(self.__solver, "Solver-%s" % self.__solverName)
        self.config.set("Session", "solver", solverName)

    def deselectSolver(self):
        if self.__solver:
            self.__saveObjConfig(self.__solver, "Solver-%s" % self.__solverName)
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
            self.__configure(self.__telescope, "Telescope-%s" % self.__telescopeName)
            self.__telescope.connected = True

    def deselectTelescope(self):
        if self.__telescope:
            self.__saveObjConfig(self.__telescope, "Telescope-%s" % self.__telescopeName)
            del self.__telescope
        self.__telescope = None
        self.__telescopeName = None

    def getTelescope(self):
        return self.__telescope

    def setAccuracy(self, value):
        self.config.set("Session", "iterlimitarcmin", str(float(value)))

    def getAccuracy(self):
        return self.config.getfloat("Session", "iterlimitarcmin")

    def setExposure(self, value):
        self.config.set("Session", "exposure", str(float(value)))

    def getExposure(self):
        return self.config.getfloat("Session", "exposure")

    def subscribeStatus(self, callback):
        """Add @callback as a status callback function"""
        if not callable(callback):
            raise ValueError("Parameter for callback must be a callable function accepting a single string value.")
        if callback not in self.__statusCB:
            self.__statusCB.append(callback)

    def subscribeProgress(self, callback):
        """
        Add @callback as a progress callback function accepting a float 0.0 .. 100.0
        activity (or None for undefined activity) and an optional status string
        """
        if not callable(callback):
            raise ValueError("Parameter for callback must be a callable function accepting a float and string.")
        if callback not in self.__progressCB:
            self.__progressCB.append(callback)

    def _list_subclasses(self, baseClass, moduleRef):
        """
        return list of (className, classRef) for sub-classes of baseClass
        found in moduleRef
        """
        rval = {}
        for module in moduleRef.__all__:
            fqmn = moduleRef.__name__ + "." + module
            mod_ = __import__(fqmn, globals(), locals())
            subclasses = getmembers(sys.modules[fqmn],
                                    lambda m: isclass(m) and issubclass(m, baseClass) and m is not baseClass)
            for className, classRef in subclasses:
                rval[className] = classRef
        return rval

    def setStatus(self, status):
        failed = []
        for callback in self.__statusCB:
            try:
                callback(status)
            except:
                if type(status) in (str, unicode):
                    failed.append(callback)
        if status and status.strip():
            logger.info(status)
        [self.__statusCB.remove(cb) for cb in failed]

    def setProgress(self, progress, status=None):
        if progress and type(progress) not in (int, float):
            return
        if status is not None and type(status) not in (str, unicode):
            return
        failed = []
        for callback in self.__progressCB:
            try:
                callback(progress, status)
            except:
                failed.append(callback)
        [self.__statusCB.remove(cb) for cb in failed]

    def __configure(self, obj, name):
        """Configure obj from config if name is found as a section"""
        if obj and self.config.has_section(name):
            for k, v in self.config.items(name):
                try:
                    obj.setProperty(k, v)
                except:
                    logger.info("Failed to set '%s' to '%s' for '%s'" % (k, v, name))

    def __saveObjConfig(self, obj, name):
        """Save obj properties as section name in config structure"""
        if not self.config.has_section(name):
            self.config.add_section(name)
        defaultConfig = obj.configuration
        for k, v in defaultConfig.items():
            self.config.set(name, k, unicode(v).replace("%", "%%"))

    def saveConfig(self, filename=CFGFILE):
        try:
            self.config.set("AstroTortilla", "settings_path", os.path.abspath(os.path.dirname(filename)))
            if self.__telescope and self.__telescopeName:
                self.__saveObjConfig(self.__telescope, "Telescope-%s" % self.__telescopeName)
            if self.__camera and self.__cameraName:
                self.__saveCameraConfig()
            if self.__solver and self.__solverName:
                self.__saveObjConfig(self.__solver, "Solver-%s" % self.__solverName)
            if self.__bookmarks:
                self.config.remove_section("Bookmarks")  # clear old bookmarks from settings
                self.config.add_section("Bookmarks")
                bmi = 0
                for bookmark in self.__bookmarks:
                    self.config.set("Bookmarks", "bm-%d" % bmi, bookmark.to_string().replace("%", "%%"))
                    bmi += 1
                self.config.set("Bookmarks", "count", "%d" % bmi)
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

    def replaceBookmarks(self, bookmarks):
        self.__bookmarks = bookmarks

    @property
    def bookmarks(self):
        return self.__bookmarks

    @property
    def isReady(self):
        rv = True
        if not self.__camera or \
                not self.__solver or \
                not self.__telescope or \
                (self.__telescope is not None and self.__telescope.slewing):
            rv = False
        if not self.__telescope.tracking:
            rv = False
        return rv

    @property
    def isBusy(self):
        return len(self.__status) > 1

    def abort(self):
        """Try to abort current action"""
        if self.__solver:
            self.__solver.abort()
        if self.__camera:
            self.__camera.reset()
        self.__abortAction = True

    def clearStatus(self):
        """Clear current errors and aborted status"""
        self.__abortAction = False
        self.__status = self.__status[:1]

    def solveImage(self, imgFile, blind=False):
        """Return Solution object for a given image"""
        if not self.__solver:
            self.setStatus(_("ERROR: No solver selected."))
            return None
        self.solution = None
        self.__status.append(Status.Solving)
        self.setStatus(_("Solving..."))
        startTime = time.time()
        # solve based on current location if telescope is tracking, otherwise pure blind solve
        try:
            if not blind and self.__telescope and self.__telescope.tracking:
                self.solution = self.__solver.solve(imgFile, target=self.__telescope.position, targetRadius=None,
                                                    callback=self.setStatus)
            else:
                self.solution = self.__solver.solve(imgFile, callback=self.setStatus)
            self.__status.pop()
        except:  # Silent errors
            import traceback
            logger.error(traceback.format_exc())
        if self.solution:
            self.setStatus(_("Solved in %.1fs") % (time.time() - startTime))
        else:
            self.setStatus(_("No solution in %.1fs") % (time.time() - startTime))
        return self.solution

    def solveCamera(self, exposure=None):
        """Return Solution object for current camera view"""
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
                if self.__camera.cameraList:
                    self.__camera.camera = self.__camera.cameraList[0]
                else:
                    raise Exception(_("No window matches search pattern"))
            exposure = exposure or self.getExposure()
            if not self.__camera.connected:
                self.setStatus(_("ERROR: No camera connected."))
                self.__status.pop()
                return None
            self.setStatus(_("Exposing: %.2f seconds") % exposure)
            self.__camera.capture(exposure)
            tEnd = time.time() + exposure
            tLast = exposure
            while not self.__camera.imageReady and self.__camera.cameraState not in (CameraState.Error,):
                time.sleep(0.02)
                tLeft = tEnd - time.time()
                if tLeft >= 0:
                    self.setProgress((1. - tLeft / exposure) * 100)
                if int(tLeft * 2) != tLast:
                    tLast = int(tLeft * 2)
                    if tLeft >= 0:
                        self.setStatus(_("Exposing: %.1f seconds") % tLeft)
                    else:
                        self.setStatus(_("Waiting for camera"))
                else:
                    self.setStatus("")
                if self.__abortAction:
                    break
            self.setProgress(-1)
            cameraError = False
            if self.__camera.cameraState == CameraState.Error:
                logger.debug("Camera in error state")
                cameraError = True
            if self.__camera.imageReady and not self.__abortAction:
                self.setStatus(_("Reading image from camera"))
                img = self.__camera.getImage()
            elif cameraError:
                detail = _("Unknown error")
                try:
                    detail = self.__camera.errorMessage
                except:
                    pass
                self.setStatus(_("Camera error: ") + detail)
                self.__camera.reset()
            elif self.__abortAction:
                self.setStatus(_("Aborted."))
            else:
                self.setStatus(_("Camera did not produce an image to solve"))
        except Exception as detail:
            self.setStatus(_("Camera error: ") + str(detail.message))
            self.setProgress(-1)
            import traceback
            logger.error(detail.message)
            logger.error(traceback.format_exc())
        self.setStatus("")
        solution = None
        if img:
            solution = self.solveImage(img)

        self.__status.pop()
        self.__abortAction = False
        return solution

    def gotoImage(self, imageFile, limit=0, threshold=0.0):
        """Goto solved image"""
        if not self.__telescope:
            self.setStatus(_("ERROR: No telescope connected."))
            return None
        newTarget = self.solveImage(imageFile, blind=True)
        if newTarget:
            self.__telescope.slewToAsync(newTarget.center)
            return self.gotoCurrentTarget(limit, threshold)
        return None

    def gotoPosition(self, coords, limit=0, threshold=0.0):
        """Goto a defined coordinate position"""
        if not self.__telescope:
            self.setStatus(_("ERROR: No telescope connected."))
            return None
        self.__telescope.slewToAsync(coords)
        return self.gotoCurrentTarget(limit, threshold)

    def gotoCurrentTarget(self, limit=0, threshold=0.0):
        """Correct slew to telescope target, retry until within 'threshold' arc minutes, no more than 'limit' times"""
        if not self.__telescope:
            self.setStatus(_("ERROR: No telescope connected."))
            return None
        self.__status.append(Status.Slewing)
        self.setStatus(_("Waiting for scope to stop"))
        startPosition = self.__telescope.position
        while self.__telescope.slewing:
            time.sleep(0.2)
            try:
                targetPos = self.__telescope.target
                startDistance = startPosition - targetPos
                distance = self.__telescope.position - targetPos
                self.setProgress((1. - distance.arcminutes / startDistance.arcminutes) * 100)
            except:
                pass
        self.setProgress(-1)
        if not self.__telescope:
            self.lastCorrection = None
            self.__status.pop()
            self.setStatus(_("ERROR: Telescope connection lost"))
            return None
        targetPos = self.__telescope.position
        currentSolution = self.solveCamera()
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
                time.sleep(0.1)
                distance = self.__telescope.position - targetPos
                self.setProgress((1. - distance.arcminutes / pointError.arcminutes) * 100)
            self.setProgress(-1)
            currentSolution = self.solveCamera()
            if not currentSolution:
                self.__status.pop()
                return None

            pointError = targetPos - currentSolution.center
            self.lastCorrection = pointError
            retries += 1
        self.__status.pop()
        return pointError

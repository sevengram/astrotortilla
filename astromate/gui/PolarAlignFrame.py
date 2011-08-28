#Boa:Frame:PolarAlignFrame

import wx
import gettext
from math import cos, radians, fabs
from time import time, sleep
from astromate import CameraState
from astromate.units import Coordinate
t = gettext.translation('mainframe', 'locale', fallback=True)
_ = t.gettext

def create(parent):
    return PolarAlignFrame(parent)

def enable(ctrl):
    try:
        if not ctrl.IsEnabled():
            ctrl.Enable()
    except:
        pass
    
def disable(ctrl):
    try:
        if ctr.IsEnabled():
            ctrl.Disable()
    except:
        pass

[wxID_POLARALIGNFRAME, wxID_POLARALIGNFRAMEALIGNFRAME, 
 wxID_POLARALIGNFRAMEALTITUDEERRORLABEL, 
 wxID_POLARALIGNFRAMEALTITUDEERRORRESULT, 
 wxID_POLARALIGNFRAMEALTITUDEHELPTEXT, 
 wxID_POLARALIGNFRAMEALTITUDEMEASUREBUTTON, 
 wxID_POLARALIGNFRAMEALTITUDESIDECHOICE, 
 wxID_POLARALIGNFRAMEALTITUDESIDESTATICTEXT, 
 wxID_POLARALIGNFRAMEALTITUDESTATICBOX, wxID_POLARALIGNFRAMEAZIMUTHERRORLABEL, 
 wxID_POLARALIGNFRAMEAZIMUTHERRORRESULT, wxID_POLARALIGNFRAMEAZIMUTHHELPTEXT, 
 wxID_POLARALIGNFRAMEAZIMUTHMEASUREBUTTON, 
 wxID_POLARALIGNFRAMEAZIMUTHSTATICBOX, wxID_POLARALIGNFRAMEHEMISPHERECHOICE, 
 wxID_POLARALIGNFRAMEHEMISPHERESTATICTEXT, wxID_POLARALIGNFRAMESTATUSBAR, 
] = [wx.NewId() for _init_ctrls in range(17)]

class PolarAlignFrame(wx.Frame):
    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wx.Frame.__init__(self, id=wxID_POLARALIGNFRAME,
              name=u'PolarAlignFrame', parent=prnt, pos=wx.Point(685, 201),
              size=wx.Size(310, 384),
              style=wx.CAPTION | wx.SYSTEM_MENU | wx.CLOSE_BOX | wx.MAXIMIZE_BOX | wx.MINIMIZE_BOX,
              title=u'Polar Alignment')
        self.SetClientSize(wx.Size(302, 357))
        self.SetMaxSize(wx.Size(-1, -1))
        self.SetMinSize(wx.Size(-1, -1))

        self.AlignFrame = wx.Panel(id=wxID_POLARALIGNFRAMEALIGNFRAME,
              name=u'AlignFrame', parent=self, pos=wx.Point(0, 0),
              size=wx.Size(302, 337), style=wx.TAB_TRAVERSAL)
        self.AlignFrame.SetToolTipString(u'')

        self.HemisphereStaticText = wx.StaticText(id=wxID_POLARALIGNFRAMEHEMISPHERESTATICTEXT,
              label=u'Observer Hemisphere:', name=u'HemisphereStaticText',
              parent=self.AlignFrame, pos=wx.Point(16, 11), size=wx.Size(109,
              16), style=0)
        self.HemisphereStaticText.SetToolTipString(u'')

        self.HemisphereChoice = wx.Choice(choices=["North", "South"],
              id=wxID_POLARALIGNFRAMEHEMISPHERECHOICE, name=u'HemisphereChoice',
              parent=self.AlignFrame, pos=wx.Point(128, 8), size=wx.Size(130,
              21), style=0)
        self.HemisphereChoice.SetSelection(0)
        self.HemisphereChoice.Bind(wx.EVT_CHOICE, self.OnHemisphereChoiceChoice,
              id=wxID_POLARALIGNFRAMEHEMISPHERECHOICE)

        self.AltitudeStaticBox = wx.StaticBox(id=wxID_POLARALIGNFRAMEALTITUDESTATICBOX,
              label=u'Mount altitude', name=u'AltitudeStaticBox',
              parent=self.AlignFrame, pos=wx.Point(8, 40), size=wx.Size(288,
              160), style=0)

        self.AzimuthStaticBox = wx.StaticBox(id=wxID_POLARALIGNFRAMEAZIMUTHSTATICBOX,
              label=u'Mount azimuth', name=u'AzimuthStaticBox',
              parent=self.AlignFrame, pos=wx.Point(8, 208), size=wx.Size(288,
              128), style=0)

        self.AltitudeSideChoice = wx.Choice(choices=["East", "West"],
              id=wxID_POLARALIGNFRAMEALTITUDESIDECHOICE,
              name=u'AltitudeSideChoice', parent=self.AlignFrame,
              pos=wx.Point(128, 96), size=wx.Size(130, 21), style=0)
        self.AltitudeSideChoice.SetSelection(0)
        self.AltitudeSideChoice.SetToolTipString(u'')
        self.AltitudeSideChoice.Bind(wx.EVT_CHOICE, self.OnAltitudeSideChoice,
              id=wxID_POLARALIGNFRAMEALTITUDESIDECHOICE)

        self.AltitudeSideStaticText = wx.StaticText(id=wxID_POLARALIGNFRAMEALTITUDESIDESTATICTEXT,
              label=u'Measurement side:', name=u'AltitudeSideStaticText',
              parent=self.AlignFrame, pos=wx.Point(24, 99), size=wx.Size(92,
              13), style=0)

        self.AltitudeMeasureButton = wx.Button(id=wxID_POLARALIGNFRAMEALTITUDEMEASUREBUTTON,
              label=u'Measure altitude error', name=u'AltitudeMeasureButton',
              parent=self.AlignFrame, pos=wx.Point(64, 168), size=wx.Size(184,
              23), style=0)
        self.AltitudeMeasureButton.Bind(wx.EVT_BUTTON,
              self.OnAltitudeMeasureButtonButton,
              id=wxID_POLARALIGNFRAMEALTITUDEMEASUREBUTTON)

        self.StatusBar = wx.StatusBar(id=wxID_POLARALIGNFRAMESTATUSBAR,
              name=u'StatusBar', parent=self, style=0)
        self.StatusBar.SetToolTipString(u'')
        self.SetStatusBar(self.StatusBar)

        self.AzimuthMeasureButton = wx.Button(id=wxID_POLARALIGNFRAMEAZIMUTHMEASUREBUTTON,
              label=u'Measure azimuth error', name=u'AzimuthMeasureButton',
              parent=self.AlignFrame, pos=wx.Point(88, 304), size=wx.Size(144,
              23), style=0)
        self.AzimuthMeasureButton.Bind(wx.EVT_BUTTON,
              self.OnAzimuthMeasureButtonButton,
              id=wxID_POLARALIGNFRAMEAZIMUTHMEASUREBUTTON)

        self.AzimuthHelpText = wx.StaticText(id=wxID_POLARALIGNFRAMEAZIMUTHHELPTEXT,
              label=u'Point the telescope to the meridian before measuring!',
              name=u'AzimuthHelpText', parent=self.AlignFrame, pos=wx.Point(20,
              232), size=wx.Size(259, 13), style=0)
        self.AzimuthHelpText.SetToolTipString(u'')

        self.AltitudeHelpText = wx.StaticText(id=wxID_POLARALIGNFRAMEALTITUDEHELPTEXT,
              label=u'Point the telescope to the east or west before\nmeasuring!',
              name=u'AltitudeHelpText', parent=self.AlignFrame, pos=wx.Point(32,
              64), size=wx.Size(223, 26), style=0)

        self.AltitudeErrorLabel = wx.StaticText(id=wxID_POLARALIGNFRAMEALTITUDEERRORLABEL,
              label=u'Measured altitude error:', name=u'AltitudeErrorLabel',
              parent=self.AlignFrame, pos=wx.Point(32, 136), size=wx.Size(138,
              13), style=0)
        self.AltitudeErrorLabel.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.BOLD,
              False, u'Tahoma'))

        self.AltitudeErrorResult = wx.StaticText(id=wxID_POLARALIGNFRAMEALTITUDEERRORRESULT,
              label=u'N/A', name=u'AltitudeErrorResult', parent=self.AlignFrame,
              pos=wx.Point(184, 136), size=wx.Size(22, 13), style=0)
        self.AltitudeErrorResult.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL,
              wx.BOLD, False, u'Tahoma'))

        self.AzimuthErrorLabel = wx.StaticText(id=wxID_POLARALIGNFRAMEAZIMUTHERRORLABEL,
              label=u'Measured azimuth error:', name=u'AzimuthErrorLabel',
              parent=self.AlignFrame, pos=wx.Point(32, 264), size=wx.Size(140,
              13), style=0)
        self.AzimuthErrorLabel.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.BOLD,
              False, u'Tahoma'))

        self.AzimuthErrorResult = wx.StaticText(id=wxID_POLARALIGNFRAMEAZIMUTHERRORRESULT,
              label=u'N/A', name=u'AzimuthErrorResult', parent=self.AlignFrame,
              pos=wx.Point(184, 264), size=wx.Size(22, 13), style=0)
        self.AzimuthErrorResult.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.BOLD,
              False, u'Tahoma'))

    def __init__(self, parent):
        self._init_ctrls(parent)
        # 0 for north/east, 1 for south/west
        self._parent = parent
        self._camera = self._parent.camera
        self._telescope = self._parent.telescope
        self._solver = self._parent.solver
        self._hemisphere = self.HemisphereChoice.GetSelection()
        self._altitudeSide = self.AltitudeSideChoice.GetSelection()
        self.__solving = False
        self.__abortSolve = False
        

    def OnHemisphereChoiceChoice(self, event):
        self._hemisphere = self.HemisphereChoice.GetSelection()

    def OnAltitudeSideChoice(self, event):
        self._altitudeSide = self.AltitudeSideChoice.GetSelection()
    
    def __captureSolve(self):
        "Captures an image and returns the platesolve solution"
        disable(self._parent.btnGO) # Disable the main window button
        if self._telescope:
            self.SetStatusText(_("Waiting for scope to stop"))
            while self._telescope.slewing:
                sleep(0.2)
        else:
            self.SetStatusText(_("Telescope not connected"))
            enable(self._parent.btnGO)
            return None
        self.__solving = True
        self.AltitudeMeasureButton.SetLabel(_("Abort solver"))
        solution = None
        try:
            try:
                self.SetStatusText(_("Connecting to camera..."))
                if not self._camera.canAutoConnect and not self._camera.connected:
                    self._camera.connected = True
                if self._camera.needsCameraName and not self._camera.camera:
                    self._camera.camera = self._camera.cameraList[0]
                exposureTime = self._parent.numCtrlExposure.GetValue()
                self.SetStatusText(_("Exposing %.2f seconds")%exposureTime)
                self._camera.capture(exposureTime) # Start exposing
                tEnd = time() + exposureTime
                while not self._camera.imageReady and self._camera.cameraState not in (CameraState.Error, ):
                    sleep(0.1)
                    tLeft = tEnd - time()
                    if tLeft >= 0:
                        self.SetStatusText(_("Exposing: %.2f seconds"%tLeft))
                    else:
                        self.SetStatusText(_("Waiting for camera"))
                    wx.SafeYield()
                    if self.__abortSolve:
                        break;
                if self._camera.imageReady and not self.__abortSolve:
                    self.SetStatusText(_("Reading image from camera"))
                    img = self._camera.getImage()
                    self.SetStatusText(_("Solving..."))
                    # If tracking, use current position as a starting point,
                    # else blind solve
                    if self._telescope and self._telescope.tracking:
                        solution = self._solver.solve(img,
                            target=self._telescope.position, targetRadius = None,
                            callback=self.__statusUpdater)
                    else:
                        solution = self._solver.solve(img, callback=self.__statusUpdater)
                elif self.__abortSolve:
                    self.SetStatusText(_("Aborted."))
                else:
                    self.SetStatusText(_("Camera did not produce an image to solve."))
                if solution:
                    self._parent.solution = solution
            except Exception, detail:
                import traceback
                diag = wx.MessageDialog(parent=self,
                    message=traceback.format_exc(),
                    caption=_("Camera error"),
                    style = wx.OK)
                try:
                    diag.ShowModal()
                except:
                    diag.Destroy()
        finally:
            self._parent._updateCamera()
            self.AltitudeMeasureButton.SetLabel(_("Measure altitude error"))
            enable(self._parent.btnGO)
            self.__solving = False
            self.__abortSolve = False
            if solution:
                self.SetStatusText(_("Solution found."))
                return solution
            else:
                self.SetStatusText(_("Solution not found."))
                return None

    def __poleError(self):
        "Calculate pole error by platesolving"
        solution = None
        if not self._telescope.tracking:
            self._telescope.tracking = True
        if self.__solving:
            self._solver.abort()
            self.__abortSolve = True
        else:
            # Take first exposure
            solution = self.__captureSolve()
        if not solution:
            return
        movement = 0.5 # Amount of degrees to slew
        firstSolve = solution.center # Center of the first platesolve
        startPos = self._telescope.position
        self.SetStatusText(_("Slewing..."))
        targetPos = Coordinate(startPos.RA - movement, startPos.dec)
        self._telescope.slewTo(targetPos) # Slew to the west
        solution = self.__captureSolve()
        if not solution:
            return
        secondSolve = solution.center # Center of the second platesolve
        decSeparation = firstSolve.dec - secondSolve.dec
        self.SetStatusText(_("Slewing..."))
        self._telescope.slewTo(startPos) # Slew back to starting position
        self.SetStatusText(_("Done!"))
        # Calculate pole error
        poleError = 3.81*3600.0*decSeparation/(4*movement*cos(radians(startPos.dec)))
        # Convert pole error from arcminutes to degrees
        poleError = poleError/60.0
        return poleError
            
    def OnAltitudeMeasureButtonButton(self, event):
        "Determine altitude error direction and size"
        poleError = self.__poleError()
        if poleError == None:
            self.SetStatusText(_("An error occurred!"))
            return
        direction = ""
        if self._hemisphere == 0:
            # Northern hemisphere
            if self._altitudeSide == 0:
                # East side
                if poleError < 0:
                    direction = "too low"
                elif poleError > 0:
                    direction = "too high"
            else:
                # West side
                if poleError < 0:
                    direction = "too high"
                elif poleError > 0:
                    direction = "too low"
        else:
            # Southern hemisphere
            if self._altitudeSide == 0:
                # East side
                if poleError < 0:
                    direction = "too high"
                elif poleError > 0:
                    direction = "too low"
            else:
                # West side
                if poleError < 0:
                    direction = "too low"
                elif poleError > 0:
                    direction = "too high"
        self.AltitudeErrorResult.SetLabel(_("%.2f degrees\n%s"%(fabs(poleError), direction)))

    def OnAzimuthMeasureButtonButton(self, event):
        "Determine azimuth error direction and size"
        poleError = self.__poleError()
        if poleError == None:
            self.SetStatusText(_("An error occurred!"))
            return        
        direction = ""
        if self._hemisphere == 0:
            # Northern hemisphere
            if poleError < 0:
                direction = "too east"
            elif poleError > 0:
                direction = "too west"
        else:
            # Southern hemisphere
            if poleError < 0:
                direction = "too west"
            elif poleError > 0:
                direction = "too east"
        self.AzimuthErrorResult.SetLabel(_("%.2f degrees\n%s"%(fabs(poleError), direction)))
        
    def __statusUpdater(self, status=None):
        "Update status bar and process UI events safely"
        if status:
            self.SetStatusText(status)
        wx.SafeYield(self)

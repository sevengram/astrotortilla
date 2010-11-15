#Boa:Frame:mainFrame

import wx
import wx.grid
import wx.lib.masked.numctrl
import DlgHelpAbout
import DlgCameraSetup
import gettext
import ConfigParser
import os, os.path
from time import time, sleep
from astromate import CameraState
from astromate.units import Coordinate, Separation, deg2dms, deg2hms
t = gettext.translation('mainframe', 'locale', fallback=True)
_ = t.gettext

def create(parent):
    return mainFrame(parent)

[wxID_MAINFRAME, wxID_MAINFRAMEBTNGO, wxID_MAINFRAMEBTNSCOPEPARK, 
 wxID_MAINFRAMECAMSETUP, wxID_MAINFRAMECHKREPEAT, wxID_MAINFRAMECHKSLEWTARGET, 
 wxID_MAINFRAMECHKSYNC, wxID_MAINFRAMECHOICECAM, wxID_MAINFRAMECHOICESCOPE, 
 wxID_MAINFRAMECHOICESOLVER, wxID_MAINFRAMECONFIGGRID, 
 wxID_MAINFRAMELBLACTIONS, wxID_MAINFRAMELBLARCMIN, wxID_MAINFRAMELBLCAMDEC, 
 wxID_MAINFRAMELBLCAMRA, wxID_MAINFRAMELBLCAMSTATUS, wxID_MAINFRAMELBLDEC, 
 wxID_MAINFRAMELBLEXPOSURE, wxID_MAINFRAMELBLFIELD, wxID_MAINFRAMELBLMIRROR, 
 wxID_MAINFRAMELBLRA, wxID_MAINFRAMELBLROTATION, 
 wxID_MAINFRAMELBLSCOPECURRENT, wxID_MAINFRAMELBLSCOPETARGET, 
 wxID_MAINFRAMELBLSECONDS, wxID_MAINFRAMEMAINCAMERA, 
 wxID_MAINFRAMENUMCTRLACCURACY, wxID_MAINFRAMENUMCTRLEXPOSURE, 
 wxID_MAINFRAMESTATICBOX1, wxID_MAINFRAMESTATICBOX2, wxID_MAINFRAMESTATUSBAR1, 
 wxID_MAINFRAMETELESCOPE, wxID_MAINFRAMETXTCAM, wxID_MAINFRAMETXTCAMDEC, 
 wxID_MAINFRAMETXTCAMRA, wxID_MAINFRAMETXTCAMSTATUS, wxID_MAINFRAMETXTDEC, 
 wxID_MAINFRAMETXTFIELD, wxID_MAINFRAMETXTRA, wxID_MAINFRAMETXTROTATION, 
 wxID_MAINFRAMETXTSCOPESLEWING, wxID_MAINFRAMETXTSCOPETARGETDEC, 
 wxID_MAINFRAMETXTSCOPETARGETRA, wxID_MAINFRAMETXTSCOPETRACKING, 
] = [wx.NewId() for _init_ctrls in range(44)]

CFGFILE = "astrotortilla.cfg" 

def hide(ctrl):
    """Hide a control if it's not hidden yet. 
    Fails silently if IsShown and Hide are not implemented for control"""
    try:
        if ctrl.IsShown():
            ctrl.Hide()
    except:
        pass

def show(ctrl):
    """Show a control if it's hidden.
    Fails silently if IsShown and Show are not implemented for control"""
    try:
        if not ctrl.IsShown():
            ctrl.Show()
    except:
        pass

def enable(ctrl):
    """Enables a control if it is disabled."""
    try:
        if not ctrl.IsEnabled():
            ctrl.Enable()
    except:
        pass

def disable(ctrl):
    """Disables a control if it is enabled."""
    try:
        if ctrl.IsEnabled():
            ctrl.Disable()
    except:
        pass


[wxID_MAINFRAMEMENUFILEFILEEXIT, wxID_MAINFRAMEMENUFILEITEMS1, 
 wxID_MAINFRAMEMENUFILEITEMS2, 
] = [wx.NewId() for _init_coll_menuFile_Items in range(3)]

[wxID_MAINFRAMEMENUHELPHELPABOUT] = [wx.NewId() for _init_coll_menuHelp_Items in range(1)]

[wxID_MAINFRAMESCOPEPOLLTIMER] = [wx.NewId() for _init_utils in range(1)]

class mainFrame(wx.Frame):
    def _init_coll_menuBar1_Menus(self, parent):
        # generated method, don't edit

        parent.Append(menu=self.menuFile, title=_('File'))
        parent.Append(menu=self.menuHelp, title=_('Help'))

    def _init_coll_menuHelp_Items(self, parent):
        # generated method, don't edit

        parent.Append(help=_('Information about the application.'),
              id=wxID_MAINFRAMEMENUHELPHELPABOUT, kind=wx.ITEM_NORMAL,
              text=_('About'))
        self.Bind(wx.EVT_MENU, self.OnMenuHelpHelpaboutMenu,
              id=wxID_MAINFRAMEMENUHELPHELPABOUT)

    def _init_coll_menuFile_Items(self, parent):
        # generated method, don't edit

        parent.Append(help='', id=wxID_MAINFRAMEMENUFILEITEMS1,
              kind=wx.ITEM_NORMAL, text=_('Load settings...'))
        parent.Append(help='', id=wxID_MAINFRAMEMENUFILEITEMS2,
              kind=wx.ITEM_NORMAL, text=_('Save settings...'))
        parent.AppendSeparator()
        parent.Append(help=_('Exit the application'),
              id=wxID_MAINFRAMEMENUFILEFILEEXIT, kind=wx.ITEM_NORMAL,
              text=_('Exit'))
        self.Bind(wx.EVT_MENU, self.OnMenuFileFileexitMenu,
              id=wxID_MAINFRAMEMENUFILEFILEEXIT)
        self.Bind(wx.EVT_MENU, self.OnMenuFileLoadSettingsMenu,
              id=wxID_MAINFRAMEMENUFILEITEMS1)
        self.Bind(wx.EVT_MENU, self.OnMenuFileSaveSettingsMenu,
              id=wxID_MAINFRAMEMENUFILEITEMS2)

    def _init_coll_statusBar1_Fields(self, parent):
        # generated method, don't edit
        parent.SetFieldsCount(1)

        parent.SetStatusText(number=0, text='status')

        parent.SetStatusWidths([-1])

    def _init_utils(self):
        # generated method, don't edit
        self.menuFile = wx.Menu(title=_(''))

        self.menuHelp = wx.Menu(title=_(''))

        self.menuBar1 = wx.MenuBar()

        self.scopePollTimer = wx.Timer(id=wxID_MAINFRAMESCOPEPOLLTIMER,
              owner=self)
        self.Bind(wx.EVT_TIMER, self.OnScopePollTimer,
              id=wxID_MAINFRAMESCOPEPOLLTIMER)

        self._init_coll_menuFile_Items(self.menuFile)
        self._init_coll_menuHelp_Items(self.menuHelp)
        self._init_coll_menuBar1_Menus(self.menuBar1)

    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wx.Frame.__init__(self, id=wxID_MAINFRAME, name='mainFrame',
              parent=prnt, pos=wx.Point(481, 126), size=wx.Size(410, 380),
              style=wx.DEFAULT_FRAME_STYLE, title='AstroTortilla')
        self._init_utils()
        self.SetClientSize(wx.Size(402, 346))
        self.SetMenuBar(self.menuBar1)
        self.SetThemeEnabled(True)
        self.SetToolTipString('')
        self.SetMaxSize(wx.Size(410, 380))
        self.SetMinSize(wx.Size(410, 380))

        self.statusBar1 = wx.StatusBar(id=wxID_MAINFRAMESTATUSBAR1,
              name='statusBar1', parent=self, style=0)
        self.statusBar1.SetLabel('')
        self.statusBar1.SetStatusText('')
        self._init_coll_statusBar1_Fields(self.statusBar1)
        self.SetStatusBar(self.statusBar1)

        self.Telescope = wx.StaticBox(id=wxID_MAINFRAMETELESCOPE,
              label=_('Telescope'), name='Telescope', parent=self,
              pos=wx.Point(8, 0), size=wx.Size(384, 80), style=0)
        self.Telescope.SetToolTipString(_(''))
        self.Telescope.SetHelpText('')
        self.Telescope.SetWindowVariant(wx.WINDOW_VARIANT_NORMAL)
        self.Telescope.SetThemeEnabled(False)

        self.mainCamera = wx.StaticBox(id=wxID_MAINFRAMEMAINCAMERA,
              label=_('Camera'), name='mainCamera', parent=self, pos=wx.Point(8,
              80), size=wx.Size(384, 88), style=0)
        self.mainCamera.SetToolTipString('')

        self.staticBox1 = wx.StaticBox(id=wxID_MAINFRAMESTATICBOX1,
              label=_('Actions'), name='staticBox1', parent=self,
              pos=wx.Point(256, 168), size=wx.Size(136, 134), style=0)
        self.staticBox1.SetToolTipString('')

        self.camSetup = wx.Button(id=wxID_MAINFRAMECAMSETUP, label=_('Setup'),
              name='camSetup', parent=self, pos=wx.Point(16, 128),
              size=wx.Size(96, 23), style=0)
        self.camSetup.SetToolTipString(_('Setup camera'))
        self.camSetup.Bind(wx.EVT_BUTTON, self.OnCamSetupButton,
              id=wxID_MAINFRAMECAMSETUP)

        self.lblRA = wx.StaticText(id=wxID_MAINFRAMELBLRA, label=_('RA:'),
              name='lblRA', parent=self, pos=wx.Point(184, 24), size=wx.Size(16,
              16), style=0)
        self.lblRA.SetToolTipString('')

        self.lblDec = wx.StaticText(id=wxID_MAINFRAMELBLDEC, label=_('Dec:'),
              name='lblDec', parent=self, pos=wx.Point(176, 40),
              size=wx.Size(24, 16), style=0)
        self.lblDec.SetToolTipString('')

        self.txtRA = wx.StaticText(id=wxID_MAINFRAMETXTRA, label='00h00m00.00s',
              name='txtRA', parent=self, pos=wx.Point(208, 24), size=wx.Size(71,
              13), style=0)
        self.txtRA.SetToolTipString(_('Right ascension'))

        self.txtDec = wx.StaticText(id=wxID_MAINFRAMETXTDEC, label='0',
              name='txtDec', parent=self, pos=wx.Point(208, 40),
              size=wx.Size(71, 13), style=0)
        self.txtDec.SetToolTipString(_('Declination'))

        self.txtCam = wx.StaticText(id=wxID_MAINFRAMETXTCAM,
              label=_('No camera'), name='txtCam', parent=self,
              pos=wx.Point(120, 96), size=wx.Size(51, 13), style=0)
        self.txtCam.SetToolTipString('')

        self.btnScopePark = wx.Button(id=wxID_MAINFRAMEBTNSCOPEPARK,
              label=_('Unpark'), name='btnScopePark', parent=self,
              pos=wx.Point(16, 48), size=wx.Size(96, 23), style=0)
        self.btnScopePark.SetToolTipString(_('(Un)park'))
        self.btnScopePark.Bind(wx.EVT_BUTTON, self.OnBtnScopeParkButton,
              id=wxID_MAINFRAMEBTNSCOPEPARK)

        self.lblField = wx.StaticText(id=wxID_MAINFRAMELBLFIELD,
              label=_('Field size:'), name='lblField', parent=self,
              pos=wx.Point(240, 128), size=wx.Size(48, 13), style=0)
        self.lblField.SetToolTipString('')

        self.txtField = wx.StaticText(id=wxID_MAINFRAMETXTFIELD, label='-',
              name='txtField', parent=self, pos=wx.Point(296, 128),
              size=wx.Size(4, 13), style=0)

        self.lblRotation = wx.StaticText(id=wxID_MAINFRAMELBLROTATION,
              label=_('Rotation:'), name='lblRotation', parent=self,
              pos=wx.Point(240, 144), size=wx.Size(45, 13), style=0)
        self.lblRotation.SetToolTipString('')

        self.txtRotation = wx.StaticText(id=wxID_MAINFRAMETXTROTATION,
              label='-', name='txtRotation', parent=self, pos=wx.Point(296,
              144), size=wx.Size(4, 13), style=0)

        self.lblMirror = wx.StaticText(id=wxID_MAINFRAMELBLMIRROR,
              label=_('Normal'), name='lblMirror', parent=self,
              pos=wx.Point(344, 144), size=wx.Size(33, 13), style=0)
        self.lblMirror.SetToolTipString('')

        self.lblActions = wx.StaticText(id=wxID_MAINFRAMELBLACTIONS,
              label=_('After solve:'), name='lblActions', parent=self,
              pos=wx.Point(264, 184), size=wx.Size(57, 13), style=0)
        self.lblActions.SetToolTipString('')

        self.numCtrlAccuracy = wx.lib.masked.numctrl.NumCtrl(id=wxID_MAINFRAMENUMCTRLACCURACY,
              name='numCtrlAccuracy', parent=self, pos=wx.Point(280, 248),
              size=wx.Size(43, 22), style=0, value=1)
        self.numCtrlAccuracy.SetFractionWidth(1)
        self.numCtrlAccuracy.SetIntegerWidth(2)
        self.numCtrlAccuracy.SetBackgroundColour(wx.Colour(255, 255, 255))
        self.numCtrlAccuracy.SetLimited(True)
        self.numCtrlAccuracy.SetMin(0.0)
        self.numCtrlAccuracy.SetMax(60)
        self.numCtrlAccuracy.SetLimitOnFieldChange(True)
        self.numCtrlAccuracy.SetValue(1.0)

        self.lblArcmin = wx.StaticText(id=wxID_MAINFRAMELBLARCMIN,
              label=_('arcmin'), name='lblArcmin', parent=self,
              pos=wx.Point(328, 248), size=wx.Size(56, 13), style=0)

        self.lblCamRA = wx.StaticText(id=wxID_MAINFRAMELBLCAMRA, label=_('RA:'),
              name='lblCamRA', parent=self, pos=wx.Point(120, 112),
              size=wx.Size(18, 13), style=0)

        self.txtCamRA = wx.StaticText(id=wxID_MAINFRAMETXTCAMRA,
              label='00h00m00.00s', name='txtCamRA', parent=self,
              pos=wx.Point(160, 112), size=wx.Size(71, 13), style=0)

        self.lblCamDec = wx.StaticText(id=wxID_MAINFRAMELBLCAMDEC,
              label=_('Dec:'), name='lblCamDec', parent=self, pos=wx.Point(120,
              128), size=wx.Size(22, 13), style=0)

        self.txtCamDec = wx.StaticText(id=wxID_MAINFRAMETXTCAMDEC, label='0',
              name='txtCamDec', parent=self, pos=wx.Point(160, 128),
              size=wx.Size(71, 13), style=0)

        self.lblCamStatus = wx.StaticText(id=wxID_MAINFRAMELBLCAMSTATUS,
              label=_('Status:'), name='lblCamStatus', parent=self,
              pos=wx.Point(120, 144), size=wx.Size(35, 13), style=0)

        self.txtCamStatus = wx.StaticText(id=wxID_MAINFRAMETXTCAMSTATUS,
              label=_('Not connected'), name='txtCamStatus', parent=self,
              pos=wx.Point(160, 144), size=wx.Size(70, 13), style=0)

        self.txtScopeSlewing = wx.StaticText(id=wxID_MAINFRAMETXTSCOPESLEWING,
              label=_('Slewing'), name='txtScopeSlewing', parent=self,
              pos=wx.Point(208, 56), size=wx.Size(43, 13), style=0)
        self.txtScopeSlewing.SetForegroundColour(wx.Colour(255, 0, 0))
        self.txtScopeSlewing.Enable(True)
        self.txtScopeSlewing.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.BOLD,
              False, 'Tahoma'))

        self.txtScopeTracking = wx.StaticText(id=wxID_MAINFRAMETXTSCOPETRACKING,
              label=_('Tracking'), name='txtScopeTracking', parent=self,
              pos=wx.Point(304, 56), size=wx.Size(40, 13), style=0)
        self.txtScopeTracking.SetForegroundColour(wx.Colour(0, 255, 0))

        self.lblExposure = wx.StaticText(id=wxID_MAINFRAMELBLEXPOSURE,
              label=_('Exposure:'), name='lblExposure', parent=self,
              pos=wx.Point(240, 112), size=wx.Size(49, 13), style=0)
        self.lblExposure.SetToolTipString('')

        self.lblSeconds = wx.StaticText(id=wxID_MAINFRAMELBLSECONDS, label='s',
              name='lblSeconds', parent=self, pos=wx.Point(352, 112),
              size=wx.Size(5, 13), style=0)
        self.lblSeconds.SetToolTipString('')

        self.numCtrlExposure = wx.lib.masked.numctrl.NumCtrl(id=wxID_MAINFRAMENUMCTRLEXPOSURE,
              name='numCtrlExposure', parent=self, pos=wx.Point(296, 104),
              size=wx.Size(50, 22), style=0, value=1.0)
        self.numCtrlExposure.SetBounds((0.0, 180))
        self.numCtrlExposure.SetFractionWidth(1)
        self.numCtrlExposure.SetIntegerWidth(3)
        self.numCtrlExposure.SetToolTipString(_('Exposure time in seconds'))
        self.numCtrlExposure.SetBackgroundColour(wx.Colour(255, 255, 255))
        self.numCtrlExposure.SetMin(0.0)
        self.numCtrlExposure.SetMax(180)
        self.numCtrlExposure.SetLimited(True)
        self.numCtrlExposure.SetLimitOnFieldChange(True)
        self.numCtrlExposure.SetValue(5.0)

        self.lblScopeCurrent = wx.StaticText(id=wxID_MAINFRAMELBLSCOPECURRENT,
              label=_('Current:'), name='lblScopeCurrent', parent=self,
              pos=wx.Point(208, 8), size=wx.Size(46, 13), style=0)
        self.lblScopeCurrent.SetToolTipString('')
        self.lblScopeCurrent.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.BOLD,
              False, 'Tahoma'))

        self.lblScopeTarget = wx.StaticText(id=wxID_MAINFRAMELBLSCOPETARGET,
              label=_('Target:'), name='lblScopeTarget', parent=self,
              pos=wx.Point(304, 8), size=wx.Size(41, 13), style=0)
        self.lblScopeTarget.SetFont(wx.Font(8, wx.SWISS, wx.NORMAL, wx.BOLD,
              False, 'Tahoma'))
        self.lblScopeTarget.SetToolTipString('')

        self.txtScopeTargetRA = wx.StaticText(id=wxID_MAINFRAMETXTSCOPETARGETRA,
              label='00h00m00.00s', name='txtScopeTargetRA', parent=self,
              pos=wx.Point(304, 24), size=wx.Size(71, 13), style=0)
        self.txtScopeTargetRA.SetToolTipString('')

        self.txtScopeTargetDec = wx.StaticText(id=wxID_MAINFRAMETXTSCOPETARGETDEC,
              label='0', name='txtScopeTargetDec', parent=self,
              pos=wx.Point(304, 40), size=wx.Size(71, 13), style=0)

        self.chkSync = wx.CheckBox(id=wxID_MAINFRAMECHKSYNC, label='Sync scope',
              name='chkSync', parent=self, pos=wx.Point(264, 200),
              size=wx.Size(120, 13), style=0)
        self.chkSync.SetValue(False)
        self.chkSync.Bind(wx.EVT_CHECKBOX, self.OnChkSyncCheckbox,
              id=wxID_MAINFRAMECHKSYNC)

        self.chkSlewTarget = wx.CheckBox(id=wxID_MAINFRAMECHKSLEWTARGET,
              label='Re-slew to target', name='chkSlewTarget', parent=self,
              pos=wx.Point(264, 216), size=wx.Size(120, 13), style=0)
        self.chkSlewTarget.SetValue(False)
        self.chkSlewTarget.Bind(wx.EVT_CHECKBOX, self.OnChkSlewTargetCheckbox,
              id=wxID_MAINFRAMECHKSLEWTARGET)

        self.chkRepeat = wx.CheckBox(id=wxID_MAINFRAMECHKREPEAT,
              label=_('Repeat until within'), name='chkRepeat', parent=self,
              pos=wx.Point(264, 232), size=wx.Size(120, 13), style=0)
        self.chkRepeat.SetValue(False)
        self.chkRepeat.Bind(wx.EVT_CHECKBOX, self.OnChkRepeatCheckbox,
              id=wxID_MAINFRAMECHKREPEAT)

        self.btnGO = wx.Button(id=wxID_MAINFRAMEBTNGO,
              label=_('Capture and Solve'), name='btnGO', parent=self,
              pos=wx.Point(264, 272), size=wx.Size(120, 23), style=0)
        self.btnGO.SetToolTipString('')
        self.btnGO.Bind(wx.EVT_BUTTON, self.OnBtnGOButton,
              id=wxID_MAINFRAMEBTNGO)

        self.staticBox2 = wx.StaticBox(id=wxID_MAINFRAMESTATICBOX2,
              label=_('Solver'), name='staticBox2', parent=self, pos=wx.Point(8,
              168), size=wx.Size(240, 134), style=0)
        self.staticBox2.SetToolTipString('')

        self.choiceSolver = wx.Choice(choices=[], id=wxID_MAINFRAMECHOICESOLVER,
              name='choiceSolver', parent=self, pos=wx.Point(16, 184),
              size=wx.Size(130, 21), style=0)
        self.choiceSolver.Bind(wx.EVT_CHOICE, self.OnChoiceSolverChoice,
              id=wxID_MAINFRAMECHOICESOLVER)

        self.configGrid = wx.grid.Grid(id=wxID_MAINFRAMECONFIGGRID,
              name='configGrid', parent=self, pos=wx.Point(16, 208),
              size=wx.Size(216, 88), style=0)
        self.configGrid.SetAutoLayout(True)
        self.configGrid.SetToolTipString(_('Solver configuration'))
        self.configGrid.SetColLabelSize(0)
        self.configGrid.SetRowLabelSize(100)
        self.configGrid.SetDefaultColSize(100)
        self.configGrid.Bind(wx.EVT_MOTION, self.OnConfigGridMotion)
        self.configGrid.Bind(wx.grid.EVT_GRID_CELL_CHANGE,
              self.OnConfigGridGridCellChange)

        self.choiceScope = wx.Choice(choices=[], id=wxID_MAINFRAMECHOICESCOPE,
              name='choiceScope', parent=self, pos=wx.Point(16, 16),
              size=wx.Size(130, 21), style=0)
        self.choiceScope.Bind(wx.EVT_CHOICE, self.OnChoiceScopeChoice,
              id=wxID_MAINFRAMECHOICESCOPE)

        self.choiceCam = wx.Choice(choices=[], id=wxID_MAINFRAMECHOICECAM,
              name='choiceCam', parent=self, pos=wx.Point(16, 104),
              size=wx.Size(96, 21), style=0)
        self.choiceCam.Bind(wx.EVT_CHOICE, self.OnChoiceCamChoice,
              id=wxID_MAINFRAMECHOICECAM)

    def __init__(self, parent):
        self._init_ctrls(parent)
        self.configGrid.CreateGrid(1,2)
        self.telescope = None
        self.telescopeName = None
        self.camera = None
        self.cameraName = None
        self.solver = None
        self.solverName = None
        self.solution = None
        self.lastSolution = 0
        self.config = ConfigParser.SafeConfigParser() # Python 2.7: allow_no_value = True)
        self.config.read(CFGFILE)
        try:
            default_path = self.config.get("AstroTortilla", "settings_path")
        except:
            if not self.config.has_section("AstroTortilla"):
                self.config.add_section("AstroTortilla")
            self.config.set("AstroTortilla", "settings_path", os.getcwdu())
        self.prev_rowcol = [None, None]
        self.txtDec.SetLabel(deg2dms(0))
        self.txtScopeTargetDec.SetLabel(deg2dms(0))
        self.txtCamDec.SetLabel(deg2dms(0))
        self.__solving = False
        self.__abortSolve = False
        self.Bind(wx.EVT_CLOSE, self.OnClose)
    
    def OnClose(self, event):
        try:
            if self.telescope and self.telescopeName:
                self.__saveObjConfig(self.telescope, self.telescopeName)
            if self.camera and self.cameraName:
                self.__saveObjConfig(self.camera, self.cameraName)
            if self.solver and self.solverName:
                self.__saveObjConfig(self.solver, self.solverName)
            self.config.write(file(CFGFILE, "w"))
        except:
            import traceback
            traceback.print_exc() 
        event.Skip()


    def __configure(self, obj, name):
            if obj and self.config.has_section(name):
                for k,v in self.config.items(name):
                    obj.setProperty(k,v)
                    
    def __saveObjConfig(self, obj, name):
            if not self.config.has_section(name):
                self.config.add_section(name)
                
            defaultConfig = obj.configuration
            for k,v in defaultConfig.items():
                self.config.set(name, k, unicode(v))
                
    def OnMenuFileFileexitMenu(self, event):
        self.Close()

    def OnMenuHelpHelpaboutMenu(self, event):
        dlg = DlgHelpAbout.DlgHelpAbout(self)
        try:
            dlg.ShowModal()
        except:
            dlg.Destroy()

    def OnConfigGridGridEditorCreated(self, event):
        event.Skip()

    def OnChoiceSolverChoice(self, event):
        self._selectSolver(event.GetEventObject().GetSelection())

    def _selectSolver(self, n):
        if self.solver:
            self.__saveObjConfig(self.solver, self.solverName)
            del self.solver
            self.configGrid.Hide()
        self.solver = None
        self.solverName = None
        solver = self.choiceSolver.GetClientData(n)
        if solver:
            self.solver = solver()
            # update config data structure                    
            self.solver = self.choiceSolver.GetClientData(n)()
            self.solverName = "Solver-%s"%(self.choiceSolver.GetStringSelection())
            self._updateSolverGrid()
            
    def _updateSolverGrid(self):
            solverProps = self.solver.propertyList
            self.__configure(self.solver, self.solverName)
            self.configGrid.ClearGrid()
            solverConfig = self.solver.configuration
            cfgSize = len(solverConfig)
            gridSize = self.configGrid.GetNumberRows()
            if gridSize > cfgSize:
                self.configGrid.DeleteRows(0, gridSize - cfgSize)
            elif gridSize < cfgSize:
                self.configGrid.AppendRows(cfgSize - gridSize)
            self.configGrid.SetRowLabelSize(0)
            self.configGrid.DisableDragGridSize()
            self.configGrid.SetColSize(1, 200)

            i = 0
            keyList = solverConfig.keys()
            keyList.sort()
            for key in keyList:
                self.configGrid.SetCellValue(i, 0, solverProps[key][0])
                self.configGrid.SetReadOnly(i, 0, True)
                self.configGrid.SetCellValue(i, 1, str(solverConfig[key]))
                self.configGrid.SetRowLabelValue(i, key)
                i += 1
            wx.EVT_MOTION(self.configGrid.GetGridWindow(), self.OnConfigGridMotion)
            self.configGrid.ForceRefresh()
            self.configGrid.Show()
        
    def OnConfigGridMotion(self, evt):
        # evt.GetRow() and evt.GetCol() would be nice to have here,
        # but as this is a mouse event, not a grid event, they are not
        # available and we need to compute them by hand.
        grid = self.configGrid
        x, y = grid.CalcUnscrolledPosition(evt.GetPosition())
        row = grid.YToRow(y)
        col = grid.XToCol(x)
        if (row,col) != self.prev_rowcol and row >= 0 and col >= 0:
            self.prev_rowcol[:] = [row,col]
            hinttext = self.solver.propertyList[grid.GetRowLabelValue(row)][col+2]
            if hinttext is None:
                hinttext = ''
            grid.GetGridWindow().SetToolTipString(hinttext)
        evt.Skip()


    def OnChoiceScopeChoice(self, event):
        n = event.GetEventObject().GetSelection()
        if self.telescope:
            self.__saveObjConf(self.telescope, self.telescopeName)
        if n == 0:
            del self.telescope
            self.telescope = None
            self.telescopeName = None
        else:
            self.telescope = self.choiceScope.GetClientData(n)()
            self.telescopeName = "Telescope-%s"%(self.choiceScope.GetStringSelection())
            if self.telescope:
                self.telescope.connected = True
                self.scopePollTimer.Start(300)


    def OnChoiceCamChoice(self, event):
        n = event.GetEventObject().GetSelection()
        if self.camera:
            self.__saveObjConfig(self.camera, self.cameraName)
        if n == 0 or self.choiceCam.GetClientData(n) is not type(self.camera):
            if self.camera and self.camera.connected:
                self.camera.connected = False
            del self.camera
            self.camera = None
            self.cameraName = None
        if n == 0: 
            self.camSetup.Disable()
            self.txtCam.SetLabel(_("No camera"))
            self._updateCamera()
            return
        self.camera = self.choiceCam.GetClientData(n)()
        self.cameraName = "Camera-%s"%(self.choiceCam.GetStringSelection)
        self.camSetup.Enable()
        self._updateCamera()

    def _updateCamera(self):
        if not self.camera:
            self.txtCamStatus.SetLabel(_("Not connected"))
            self.btnGO.Disable()
        else:
            self.btnGO.Enable()
            self.txtCamStatus.SetLabel(CameraState.State[self.camera.cameraState])
        if not self.solution:
            if self.camera:
                self.txtCam.SetLabel(_("No solution"))
        else:
            self.txtCamRA.SetLabel(deg2hms(self.solution.center.RA))
            self.txtCamDec.SetLabel(deg2dms(self.solution.center.dec))
            hFov, vFov = self.solution.fieldOfView
            fovUnit = _(u"\xb0")
            if hFov < 1.0 or vFov < 1.0:
                hFov *= 60.
                vFov *= 60.
                fovUnit = _("'")
            self.txtField.SetLabel("%01.2f%s x %01.2f%s"%(hFov, fovUnit, vFov, fovUnit))
            if int(self.solution.parity) == 1:
                self.lblMirror.SetLabel(_("Flipped"))
            else:
                self.lblMirror.SetLabel(_("Normal"))
            self.txtRotation.SetLabel("%.2f"%(self.solution.rotation))
            if self.lastSolution:
                if self.telescope:
                    separation = self.telescope.position - self.solution.center
                    separationString = ""
                    if separation.degrees > 1:
                        separationString = u"%.2fxb0"%(separation.degrees)
                    elif separation.arcminutes>1:
                        separationString = u"%.2f'"%(separation.arcminutes)
                    else:
                        separationString = u"%.2f\""%(separation.arcseconds)
                    self.txtCam.SetLabel(_("Distance: %s (%ds old)"%(separationString, time() - self.lastSolution)))
                else:
                    self.txtCam.SetLabel(_("Age: %ds"%(time() - self.lastSolution)))
        

    def OnConfigGridMouseEvents(self, event):
        event.Skip()

    def OnCamSetupButton(self, event):
        if not self.camera:
            event.Skip()
            return
        if self.camera.hasSetupDialog:
            if not self.camera.connected: 
                try:
                    self.camera.connected = True
                except Exception, detail:
                    import traceback
                    diag = wx.MessageDialog(parent=self, 
                        message=traceback.format_exc(), 
                        caption=_("Camera error"),
                        style = wx.OK
                        )
                    try:
                        diag.ShowModal()
                    except:
                        diag.Destroy()
                    return
            self.camera.setup()
            return
        dlg = DlgCameraSetup.DlgCameraSetup(self)
        try:
            dlg.ShowModal()
        except:
            dlg.Destroy()
        

    def OnBtnScopeParkButton(self, event):
        if self.telescope == None:
            return
        self.telescope.parked = not self.telescope.parked

    def OnChkSlewTargetCheckbox(self, event):
        state = event.GetEventObject().IsChecked()
        if state:
            self.chkSync.SetValue(True)
        else:
            self.chkRepeat.SetValue(False)

    def OnChkRepeatCheckbox(self, event):
        state = event.GetEventObject().IsChecked()
        if state:
            self.chkSlewTarget.SetValue(True)
            self.chkSync.SetValue(True)

    def OnBtnGOButton(self, event):
        if not self.camera or not self.solver:
            event.Skip()
            return
        if self.__solving:
            self.solver.abort()
            self.__abortSolve = True
            self.btnGO.SetLabel(_("Aborting..."))
            return
        self.__solving = True
        self.btnGO.SetLabel(_("Abort solver"))
        try:
            while True:
                distance = self.__captureSolve()
                if not self.chkRepeat.IsChecked():
                    break
                if distance <= self.numCtrlAccuracy.GetValue():
                    break
        finally:
            for row in range(self.configGrid.GetNumberRows()):
                key = self.configGrid.GetRowLabelValue(row)
                self.configGrid.SetCellValue(row,1,str(self.solver.getProperty(key)))
                
            self.__solving = False
            self.__abortSolve = False
            self.btnGO.SetLabel(_("Capture and Solve"))
                

    def __captureSolve(self):
        pointError = -1
        targetPos = None
        if self.telescope:
            self.SetStatusText(_("Waiting for scope to stop"))
            while self.telescope.slewing:
                sleep(0.2)
            targetPos = self.telescope.position
        self.solution = 0
        try:
            self.solution = None
            try:
                self.SetStatusText(_("Connecting to camera..."))
                if not self.camera.canAutoConnect and not self.camera.connected:
                    self.camera.connected = True
                if self.camera.needsCameraName:
                    self.camera.camera = self.camera.cameraList[0]
                self.SetStatusText(_("Exposing: %.2f seconds")%self.numCtrlExposure.GetValue())
                self.camera.capture(self.numCtrlExposure.GetValue())
                tEnd = time() + self.numCtrlExposure.GetValue()
                while not self.camera.imageReady and self.camera.cameraState not in (CameraState.Error, CameraState.Idle):
                    sleep(0.1)
                    tLeft = tEnd - time()
                    if tLeft >= 0:
                        self.SetStatusText(_("Exposing: %.2f seconds")%tLeft)
                    else:
                        self.SetStatusText(_("Waiting for camera"))
                    wx.SafeYield()
                    if self.__abortSolve: break;
                if self.camera.imageReady and not self.__abortSolve:
                    self.SetStatusText(_("Reading image from camera"))
                    img = self.camera.getImage()
                    self.SetStatusText(_("Solving..."))
                    if self.telescope and self.telescope.tracking:
                        self.solution = self.solver.solve(img, target=self.telescope.position, targetRadius=None, callback=self.__statusUpdater)
                    else:
                        self.solution = self.solver.solve(img, callback=self.__statusUpdater)
                elif self.__abortSolve:
                    pass
                else:
                    self.SetStatusText(_("Camera did not produce an image to solve"))
            except Exception, detail:
                import traceback
                diag = wx.MessageDialog(parent=self, 
                    message=traceback.format_exc(), 
                    caption=_("Camera error"),
                    style = wx.OK
                    )
                try:
                    diag.ShowModal()
                except:
                    diag.Destroy()
                
            if self.solution:
                self.lastSolution = time()
        finally:
            self._updateCamera()
            if self.solution:
                self.SetStatusText(_("Solution found."))
                
                if targetPos:
                    pointError = self.solution.center - targetPos
                    self.SetStatusText(_("Separation: %s")%deg2dms(pointError.degrees))
                if self.telescope and self.telescope.tracking:
                    if self.chkSync.IsChecked():
                        self.telescope.position = self.solution.center
                    if self.chkSlewTarget.IsChecked():
                        self.telescope.slewToAsync(targetPos)
            else:
                self.SetStatusText(_("Solution not found."))
        return pointError

    def __statusUpdater(self, status):
        self.SetStatusText(status)
        wx.SafeYield(self)

    def OnScopePollTimer(self, event):
        if not self.telescope:
            self.scopePollTimer.Stop()
            map(hide, (self.txtScopeTracking, self.txtScopeSlewing))
            self.txtScopeTracking.Update()
            self.txtScopeSlewing.Update()
            map(disable, (
                self.btnScopePark,
                self.chkSync,
                self.chkSlewTarget,
                self.chkRepeat
                ))
            return
        if self.telescope.parked:
                enable(self.btnScopePark)
        else:
                disable(self.btnScopePark)
        if self.telescope.tracking:
            show(self.txtScopeTracking)
            map(enable, (
                self.chkSync,
                self.chkSlewTarget,
                self.chkRepeat
                ))
        else:
            hide(self.txtScopeTracking)
            map(disable, (
                self.chkSync,
                self.chkSlewTarget,
                self.chkRepeat
                ))
        if self.telescope.slewing:
            show(self.txtScopeSlewing)
            disable(self.btnGO)
        else:
            hide(self.txtScopeSlewing)
            enable(self.btnGO)
        curPos = self.telescope.position
        targetPos = self.telescope.target
        self.txtRA.SetLabel(deg2hms(curPos.RA))
        self.txtDec.SetLabel(deg2dms(curPos.dec))
        if not targetPos: targetPos = curPos
        self.txtScopeTargetRA.SetLabel(deg2hms(targetPos.RA))
        self.txtScopeTargetDec.SetLabel(deg2dms(targetPos.dec))
        if self.lastSolution:
                separation = self.telescope.position - self.solution.center
                separationString = ""
                if separation.degrees > 1:
                    separationString = u"%.2fxb0"%(separation.degrees)
                elif separation.arcminutes>1:
                    separationString = u"%.2f'"%(separation.arcminutes)
                else:
                    separationString = u"%.2f\""%(separation.arcseconds)
                self.txtCam.SetLabel(_("Distance: %s (%ds old)"%(separationString, time() - self.lastSolution)))
        self.txtScopeTracking.Update()
        self.txtScopeSlewing.Update()

    def OnChkSyncCheckbox(self, event):
        state = event.GetEventObject().IsChecked()
        if not state:
            self.chkSlewTarget.SetValue(False)
            self.chkRepeat.SetValue(False)

    def OnConfigGridGridCellChange(self, event):
        col, row =event.GetCol(), event.GetRow()
        key = self.configGrid.GetRowLabelValue(row)
        validator = self.solver.propertyList[key][1]
        data = self.configGrid.GetCellValue(row,col)
        try:
            validator(data) # test validity
            self.solver.setProperty(key, data)
        except:
            self.SetStatusText("Invalid data")
            self.configGrid.SetCellValue(row,col,str(self.solver.getProperty(key)))

    def OnMenuFileLoadSettingsMenu(self, event):
        fileName = wx.FileSelector(
				message=_("Load settings"),
				default_path = self.config.get("AstroTortilla", "settings_path"),
				flags = wx.FD_OPEN|wx.FD_FILE_MUST_EXIST,
				wildcard="Config file(*.cfg)|*.cfg",
				)

        if fileName:
            self.config.read(fileName)
            self.config.set("AstroTortilla", "settings_path", os.path.dirname(fileName))
            self.__configure(self.telescope, "Telescope-%s"%self.telescopeName)
            self.__configure(self.camera, "Telescope-%s"%self.cameraName)
            self.__configure(self.solver, "Telescope-%s"%self.solverName)
            self._updateSolverGrid()
            


    def OnMenuFileSaveSettingsMenu(self, event):
        fileName = wx.FileSelector(
				message=_("Save settings"),
				default_path = self.config.get("AstroTortilla", "settings_path"),
				flags = wx.FD_SAVE,
				wildcard="Config file(*.cfg)|*.cfg",
				)
        if not fileName:
            return
        try:
            self.config.set("AstroTortilla", "settings_path", os.path.dirname(fileName))
            if self.telescope and self.telescopeName:
                self.__saveObjConfig(self.telescope, self.telescopeName)
            if self.camera and self.cameraName:
                self.__saveObjConfig(self.camera, self.cameraName)
            if self.solver and self.solverName:
                self.__saveObjConfig(self.solver, self.solverName)
            self.config.write(file(fileName, "w"))
        except:
            import traceback
            traceback.print_exc() 
            
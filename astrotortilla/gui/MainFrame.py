# -*- coding: UTF-8 -*-

import win32gui
import wx
import wx.grid
import wx.lib.masked.numctrl
import gettext
import logging
from time import time, sleep
from wx.lib.anchors import LayoutAnchors

import DlgHelpAbout
import DlgCameraSetup
import DlgTelescopeSetup
import BookmarkEditor
import LogFrame
from astrotortilla import CameraState
from astrotortilla.bookmark import Bookmark
from astrotortilla.engine import TortillaEngine
from astrotortilla.units import deg2dms, deg2hms, deg2str

logger = logging.getLogger("astrotortilla.Main")

t = gettext.translation('astrotortilla', 'locale', fallback=True)
_ = t.gettext

DEBUG = 0  # 1 to enable some debug prints


def create(parent):
    return mainFrame(parent)


[wxID_MAINFRAME, wxID_MAINFRAMEBTNGO, wxID_MAINFRAMEBTNSCOPESETUP,
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
 wxID_MAINFRAMEPROGRESS, wxID_MAINFRAMESTATICBOX1,
 wxID_MAINFRAMESTATICBOXSOLVER, wxID_MAINFRAMESTATUSBAR1,
 wxID_MAINFRAMETELESCOPE, wxID_MAINFRAMETXTCAM, wxID_MAINFRAMETXTCAMDEC,
 wxID_MAINFRAMETXTCAMRA, wxID_MAINFRAMETXTCAMSTATUS, wxID_MAINFRAMETXTDEC,
 wxID_MAINFRAMETXTFIELD, wxID_MAINFRAMETXTRA, wxID_MAINFRAMETXTROTATION,
 wxID_MAINFRAMETXTSCOPESLEWING, wxID_MAINFRAMETXTSCOPETARGETDEC,
 wxID_MAINFRAMETXTSCOPETARGETRA, wxID_MAINFRAMETXTSCOPETRACKING,
 ] = [wx.NewId() for _init_ctrls in range(45)]

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

[wxID_MAINFRAMEMENUTOOLSDRIFTSHOT, wxID_MAINFRAMEMENUTOOLSITEMS2,
 wxID_MAINFRAMEMENUTOOLSLOGWINDOW,
 ] = [wx.NewId() for _init_coll_menuTools_Items in range(3)]

[wxID_MAINFRAMEMENUBOOKMARKSADDIMAGEBM,
 wxID_MAINFRAMEMENUBOOKMARKSADDSOLUTIONBM,
 wxID_MAINFRAMEMENUBOOKMARKSEDITBOOKMARKS,
 ] = [wx.NewId() for _init_coll_menuBookmarks_Items in range(3)]

[wxID_MAINFRAMEMENUHELPHELPABOUT] = [wx.NewId() for _init_coll_menuHelp_Items in range(1)]

[wxID_MAINFRAMESCOPEPOLLTIMER] = [wx.NewId() for _init_utils in range(1)]


class mainFrame(wx.Frame):
    def _init_coll_menuBookmarks_Items(self, parent):
        # generated method, don't edit

        parent.Append(help='', id=wxID_MAINFRAMEMENUBOOKMARKSADDSOLUTIONBM,
                      kind=wx.ITEM_NORMAL, text=_(u'Add current solution'))
        parent.Append(help='', id=wxID_MAINFRAMEMENUBOOKMARKSADDIMAGEBM,
                      kind=wx.ITEM_NORMAL, text=_(u'Add from solved image'))
        parent.Append(help='', id=wxID_MAINFRAMEMENUBOOKMARKSEDITBOOKMARKS,
                      kind=wx.ITEM_NORMAL, text=_(u'Edit bookmarks'))
        parent.AppendSeparator()
        self.Bind(wx.EVT_MENU, self.OnMenuBookmarksAddsolutionbmMenu,
                  id=wxID_MAINFRAMEMENUBOOKMARKSADDSOLUTIONBM)
        self.Bind(wx.EVT_MENU, self.OnMenuBookmarksAddimagebmMenu,
                  id=wxID_MAINFRAMEMENUBOOKMARKSADDIMAGEBM)
        self.Bind(wx.EVT_MENU, self.OnMenuBookmarksEditbookmarksMenu,
                  id=wxID_MAINFRAMEMENUBOOKMARKSEDITBOOKMARKS)

    def _init_coll_menuBar1_Menus(self, parent):
        # generated method, don't edit

        parent.Append(menu=self.menuFile, title=_('File'))
        parent.Append(menu=self.menuBookmarks, title=_('Bookmarks'))
        parent.Append(menu=self.menuTools, title=_('Tools'))
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

    def _init_coll_menuTools_Items(self, parent):
        # generated method, don't edit

        parent.Append(help='', id=wxID_MAINFRAMEMENUTOOLSITEMS2,
                      kind=wx.ITEM_NORMAL, text=_('Goto Image'))
        parent.Append(help='', id=wxID_MAINFRAMEMENUTOOLSDRIFTSHOT,
                      kind=wx.ITEM_NORMAL, text=_('Drift shot'))
        parent.Append(help='', id=wxID_MAINFRAMEMENUTOOLSLOGWINDOW,
                      kind=wx.ITEM_NORMAL, text=_('Log viewer'))
        self.Bind(wx.EVT_MENU, self.OnMenuToolsDriftshotMenu,
                  id=wxID_MAINFRAMEMENUTOOLSDRIFTSHOT)
        self.Bind(wx.EVT_MENU, self.OnMenuToolsGotoImage,
                  id=wxID_MAINFRAMEMENUTOOLSITEMS2)
        self.Bind(wx.EVT_MENU, self.OnMenuToolsLogwindowMenu,
                  id=wxID_MAINFRAMEMENUTOOLSLOGWINDOW)

    def _init_coll_statusBar1_Fields(self, parent):
        # generated method, don't edit
        parent.SetFieldsCount(1)

        parent.SetStatusText(number=0, text='status')

        parent.SetStatusWidths([-1])

    def _init_utils(self):
        # generated method, don't edit
        self.menuFile = wx.Menu(title='')

        self.menuHelp = wx.Menu(title='')

        self.menuBar1 = wx.MenuBar()

        self.scopePollTimer = wx.Timer(id=wxID_MAINFRAMESCOPEPOLLTIMER,
                                       owner=self)
        self.Bind(wx.EVT_TIMER, self.OnScopePollTimer,
                  id=wxID_MAINFRAMESCOPEPOLLTIMER)

        self.menuTools = wx.Menu(title='')

        self.menuBookmarks = wx.Menu(title='')

        self._init_coll_menuFile_Items(self.menuFile)
        self._init_coll_menuHelp_Items(self.menuHelp)
        self._init_coll_menuBar1_Menus(self.menuBar1)
        self._init_coll_menuTools_Items(self.menuTools)
        self._init_coll_menuBookmarks_Items(self.menuBookmarks)

    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wx.Frame.__init__(self, id=wxID_MAINFRAME, name='mainFrame',
                          parent=prnt, pos=wx.Point(892, 147), size=wx.Size(410, 384),
                          style=wx.DEFAULT_FRAME_STYLE, title='AstroTortilla')
        self._init_utils()
        self.SetMenuBar(self.menuBar1)
        self.SetThemeEnabled(True)
        self.SetToolTipString('')
        self.SetMinSize(wx.Size(410, 384))
        self.SetAutoLayout(True)
        self.SetClientSize(wx.Size(394, 346))
        self.Bind(wx.EVT_MOVE, self.OnMainFrameMove)
        self.Bind(wx.EVT_SIZE, self.OnMainFrameSize)
        self.Bind(wx.EVT_ACTIVATE, self.OnMainFrameActivate)

        self.statusBar1 = wx.StatusBar(id=wxID_MAINFRAMESTATUSBAR1,
                                       name='statusBar1', parent=self, style=0)
        self.statusBar1.SetLabel('')
        self.statusBar1.SetStatusText('')
        self._init_coll_statusBar1_Fields(self.statusBar1)
        self.SetStatusBar(self.statusBar1)

        self.progress = wx.Gauge(id=wxID_MAINFRAMEPROGRESS, name='progress',
                                 parent=self.statusBar1, pos=wx.Point(300, 1), range=100,
                                 size=wx.Size(100, 22), style=wx.GA_HORIZONTAL)
        self.progress.SetToolTipString('')

        self.Telescope = wx.StaticBox(id=wxID_MAINFRAMETELESCOPE,
                                      label=_('Telescope'), name='Telescope', parent=self,
                                      pos=wx.Point(8, 0), size=wx.Size(384, 80), style=0)
        self.Telescope.SetToolTipString(_(''))
        self.Telescope.SetHelpText('')
        self.Telescope.SetWindowVariant(wx.WINDOW_VARIANT_NORMAL)
        self.Telescope.SetThemeEnabled(False)
        self.Telescope.SetConstraints(LayoutAnchors(self.Telescope, True, True,
                                                    True, False))

        self.mainCamera = wx.StaticBox(id=wxID_MAINFRAMEMAINCAMERA,
                                       label=_('Camera'), name='mainCamera', parent=self, pos=wx.Point(8,
                                                                                                       80),
                                       size=wx.Size(384, 88), style=0)
        self.mainCamera.SetToolTipString('')
        self.mainCamera.SetConstraints(LayoutAnchors(self.mainCamera, True,
                                                     True, True, False))

        self.staticBox1 = wx.StaticBox(id=wxID_MAINFRAMESTATICBOX1,
                                       label=_('Actions'), name='staticBox1', parent=self,
                                       pos=wx.Point(256, 168), size=wx.Size(136, 134), style=0)
        self.staticBox1.SetToolTipString('')
        self.staticBox1.SetConstraints(LayoutAnchors(self.staticBox1, False,
                                                     True, True, False))

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

        self.btnScopeSetup = wx.Button(id=wxID_MAINFRAMEBTNSCOPESETUP,
                                       label=_(u'Setup'), name=u'btnScopeSetup', parent=self,
                                       pos=wx.Point(16, 48), size=wx.Size(96, 23), style=0)
        self.btnScopeSetup.SetToolTipString(_(u'Telescope driver workarounds'))
        self.btnScopeSetup.Bind(wx.EVT_BUTTON, self.OnBtnScopeSetupButton,
                                id=wxID_MAINFRAMEBTNSCOPESETUP)

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
                                                                                                  144),
                                         size=wx.Size(4, 13), style=0)

        self.lblMirror = wx.StaticText(id=wxID_MAINFRAMELBLMIRROR,
                                       label=_('Normal'), name='lblMirror', parent=self,
                                       pos=wx.Point(344, 144), size=wx.Size(33, 13), style=0)
        self.lblMirror.SetToolTipString('')
        self.lblMirror.SetConstraints(LayoutAnchors(self.lblMirror, True, True,
                                                    True, False))

        self.lblActions = wx.StaticText(id=wxID_MAINFRAMELBLACTIONS,
                                        label=_('After solve:'), name='lblActions', parent=self,
                                        pos=wx.Point(264, 184), size=wx.Size(120, 13), style=0)
        self.lblActions.SetToolTipString('')
        self.lblActions.SetConstraints(LayoutAnchors(self.lblActions, False,
                                                     True, True, False))

        self.numCtrlAccuracy = wx.lib.masked.numctrl.NumCtrl(id=wxID_MAINFRAMENUMCTRLACCURACY,
                                                             name='numCtrlAccuracy', parent=self,
                                                             pos=wx.Point(280, 248),
                                                             size=wx.Size(43, 22), style=0, value=1)
        self.numCtrlAccuracy.SetFractionWidth(1)
        self.numCtrlAccuracy.SetIntegerWidth(2)
        self.numCtrlAccuracy.SetBackgroundColour(wx.Colour(255, 255, 255))
        self.numCtrlAccuracy.SetLimited(True)
        self.numCtrlAccuracy.SetMin(0.0)
        self.numCtrlAccuracy.SetMax(60)
        self.numCtrlAccuracy.SetLimitOnFieldChange(True)
        self.numCtrlAccuracy.SetValue(1.0)
        self.numCtrlAccuracy.SetConstraints(LayoutAnchors(self.numCtrlAccuracy,
                                                          False, True, True, False))
        self.numCtrlAccuracy.Bind(wx.EVT_TEXT, self.__accuracyChanged)

        self.lblArcmin = wx.StaticText(id=wxID_MAINFRAMELBLARCMIN,
                                       label=_('arcmin'), name='lblArcmin', parent=self,
                                       pos=wx.Point(328, 248), size=wx.Size(56, 13), style=0)
        self.lblArcmin.SetConstraints(LayoutAnchors(self.lblArcmin, False, True,
                                                    True, False))

        self.lblCamRA = wx.StaticText(id=wxID_MAINFRAMELBLCAMRA, label=_('RA:'),
                                      name='lblCamRA', parent=self, pos=wx.Point(120, 112),
                                      size=wx.Size(18, 13), style=0)

        self.txtCamRA = wx.StaticText(id=wxID_MAINFRAMETXTCAMRA,
                                      label='00h00m00.00s', name='txtCamRA', parent=self,
                                      pos=wx.Point(160, 112), size=wx.Size(71, 13), style=0)

        self.lblCamDec = wx.StaticText(id=wxID_MAINFRAMELBLCAMDEC,
                                       label=_('Dec:'), name='lblCamDec', parent=self, pos=wx.Point(120,
                                                                                                    128),
                                       size=wx.Size(22, 13), style=0)

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
                                                             name='numCtrlExposure', parent=self,
                                                             pos=wx.Point(296, 104),
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
        self.numCtrlExposure.Bind(wx.EVT_TEXT, self.__exposureChanged)

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

        self.chkSync = wx.CheckBox(id=wxID_MAINFRAMECHKSYNC,
                                   label=_('Sync scope'), name='chkSync', parent=self,
                                   pos=wx.Point(264, 200), size=wx.Size(120, 13), style=0)
        self.chkSync.SetValue(True)
        self.chkSync.SetConstraints(LayoutAnchors(self.chkSync, False, True,
                                                  True, False))
        self.chkSync.Bind(wx.EVT_CHECKBOX, self.OnChkSyncCheckbox,
                          id=wxID_MAINFRAMECHKSYNC)

        self.chkRepeat = wx.CheckBox(id=wxID_MAINFRAMECHKREPEAT,
                                     label=_('Repeat until within'), name='chkRepeat', parent=self,
                                     pos=wx.Point(264, 232), size=wx.Size(120, 13), style=0)
        self.chkRepeat.SetValue(False)
        self.chkRepeat.SetConstraints(LayoutAnchors(self.chkRepeat, False, True,
                                                    True, False))
        self.chkRepeat.Bind(wx.EVT_CHECKBOX, self.OnChkRepeatCheckbox,
                            id=wxID_MAINFRAMECHKREPEAT)

        self.btnGO = wx.Button(id=wxID_MAINFRAMEBTNGO,
                               label=_('Capture and Solve'), name='btnGO', parent=self,
                               pos=wx.Point(264, 272), size=wx.Size(120, 23), style=0)
        self.btnGO.SetToolTipString('')
        self.btnGO.SetConstraints(LayoutAnchors(self.btnGO, False, True, True,
                                                False))
        self.btnGO.Bind(wx.EVT_BUTTON, self.OnBtnGOButton,
                        id=wxID_MAINFRAMEBTNGO)

        self.staticBoxSolver = wx.StaticBox(id=wxID_MAINFRAMESTATICBOXSOLVER,
                                            label=_('Solver'), name=u'staticBoxSolver', parent=self,
                                            pos=wx.Point(8, 168), size=wx.Size(240, 154), style=0)
        self.staticBoxSolver.SetToolTipString('')
        self.staticBoxSolver.SetAutoLayout(True)
        self.staticBoxSolver.SetConstraints(LayoutAnchors(self.staticBoxSolver,
                                                          True, True, True, True))
        self.staticBoxSolver.SetMinSize(wx.Size(249, 134))

        self.choiceSolver = wx.Choice(choices=[], id=wxID_MAINFRAMECHOICESOLVER,
                                      name='choiceSolver', parent=self, pos=wx.Point(16, 184),
                                      size=wx.Size(130, 21), style=0)
        self.choiceSolver.SetConstraints(LayoutAnchors(self.choiceSolver, True,
                                                       True, False, False))
        self.choiceSolver.Bind(wx.EVT_CHOICE, self.OnChoiceSolverChoice,
                               id=wxID_MAINFRAMECHOICESOLVER)

        self.configGrid = wx.grid.Grid(id=wxID_MAINFRAMECONFIGGRID,
                                       name='configGrid', parent=self, pos=wx.Point(16, 208),
                                       size=wx.Size(220, 110), style=0)
        self.configGrid.SetAutoLayout(True)
        self.configGrid.SetToolTipString(_('Solver configuration'))
        self.configGrid.SetColLabelSize(0)
        self.configGrid.SetRowLabelSize(100)
        self.configGrid.SetDefaultColSize(100)
        self.configGrid.SetConstraints(LayoutAnchors(self.configGrid, True,
                                                     True, True, True))
        self.configGrid.SetHelpText(u'')
        self.configGrid.SetLabel(u'configGrid')
        self.configGrid.SetMinSize(wx.Size(220, 94))
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

        self.chkSlewTarget = wx.CheckBox(id=wxID_MAINFRAMECHKSLEWTARGET,
                                         label=_('Re-slew to target'), name='chkSlewTarget', parent=self,
                                         pos=wx.Point(264, 216), size=wx.Size(120, 13), style=0)
        self.chkSlewTarget.SetValue(True)
        self.chkSlewTarget.SetConstraints(LayoutAnchors(self.chkSlewTarget,
                                                        False, True, True, False))
        self.chkSlewTarget.Bind(wx.EVT_CHECKBOX, self.OnChkSlewTargetCheckbox,
                                id=wxID_MAINFRAMECHKSLEWTARGET)

    def __exposureChanged(self, event_args):
        self.engine.setExposure(self.numCtrlExposure.GetValue())

    def __accuracyChanged(self, event_args):
        self.engine.setAccuracy(self.numCtrlAccuracy.GetValue())

    def __init__(self, parent):
        self.__logFrame = None
        self._init_ctrls(parent)
        self.engine = TortillaEngine()
        if not self.engine.version_tag.startswith("NoIcon"):
            try:
                import win32api
                exeName = win32api.GetModuleFileName(win32api.GetModuleHandle(None))
                icon = wx.Icon(exeName, wx.BITMAP_TYPE_ICO)
                self.SetIcon(icon)
            except:
                pass

        self.SetTitle('AstroTortilla %s' % (self.engine.version))

        self.progress.Hide()
        self.configGrid.CreateGrid(1, 2)
        self.engine.subscribeStatus(self.__statusUpdater)
        self.engine.subscribeProgress(self.__progressUpdater)
        self.prev_rowcol = [None, None]  # helper for solver config matrix tooltip
        # set default null values everywhere
        self.txtDec.SetLabel(deg2dms(0))
        self.txtScopeTargetDec.SetLabel(deg2dms(0))
        self.txtCamDec.SetLabel(deg2dms(0))

        # Bind self.OnClose to window closing event
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.numCtrlExposure.SetValue(self.engine.getExposure() or 5.0)  # set default exposure value
        self.numCtrlAccuracy.SetValue(self.engine.getAccuracy() or 1.0)  # set default accuracy value
        self.bookmarkMenuStart = self.menuBookmarks.GetMenuItemCount()
        self.bookmarkMenuItems = []
        self.bookmarkMap = {}
        disable(self.btnScopeSetup)
        self.updateBookmarkMenu()
        self._updateCamera()
        # Old compatibility mode
        x = y = w = h = -32000
        try:
            x = self.engine.config.getint("Session", "GuiX")
            y = self.engine.config.getint("Session", "GuiY")
            w = self.engine.config.getint("Session", "GuiW")
            h = self.engine.config.getint("Session", "GuiH")
        except:
            pass
        # -32000 for minimized state? check SetWindowPlacement/Get...
        if x > -32000:
            self.SetPosition((x, y))
        if h > 0:
            self.SetSize((w, h))
        # New window placement method
        try:
            placement = self.engine.config.get("Session", "MainPlacement")
            import ast
            win32gui.SetWindowPlacement(self.GetHandle(), ast.literal_eval(placement))
        except:
            pass

    def OnClose(self, event):
        "Save settings on exit"
        placement = win32gui.GetWindowPlacement(self.GetHandle())
        self.engine.config.set("Session", "MainPlacement", str(placement))
        # remove old options from config
        for oldPosition in ("GuiX", "GuiY", "GuiH", "GuiW", "LogWindowX", "LogWindowY", "LogWindowH", "LogWindowW"):
            try:
                self.engine.config.remove_option("Session", oldPosition)
            except:
                pass
        try:
            self.engine.saveConfig()
        except:
            pass
        # saving settings on exit failed, but nowhere to show the error anymore
        event.Skip()

    def OnMenuFileFileexitMenu(self, event):
        self.Close()

    def OnMenuHelpHelpaboutMenu(self, event):
        dlg = DlgHelpAbout.DlgHelpAbout(self)
        try:
            dlg.ShowModal()
        except:
            pass
        finally:
            dlg.Destroy()

    def OnConfigGridGridEditorCreated(self, event):
        event.Skip()

    def OnChoiceSolverChoice(self, event):
        self.engine.selectSolver(event.GetClientData())
        if self.engine.getSolver():
            self._updateSolverGrid()

    def _updateSolverGrid(self):
        "Update solver configuration grid"
        if not self.engine.getSolver():
            return
        solverProps = self.engine.getSolver().propertyList
        self.configGrid.ClearGrid()
        solverConfig = self.engine.getSolver().configuration
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
        self.configGrid.SetColMinimalAcceptableWidth(80)
        self.configGrid.AutoSize()
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
        if (row, col) != self.prev_rowcol and row >= 0 and col >= 0:
            self.prev_rowcol[:] = [row, col]
            hinttext = self.engine.getSolver().propertyList[grid.GetRowLabelValue(row)][col + 2]
            if hinttext is None:
                hinttext = ''
            grid.GetGridWindow().SetToolTipString(hinttext)
        evt.Skip()

    def OnChoiceScopeChoice(self, event):
        n = event.GetEventObject().GetSelection()
        if n == 0:
            self.engine.deselectTelescope()
            disable(self.btnScopeSetup)
        else:
            self.engine.selectTelescope(event.GetClientData())
            enable(self.btnScopeSetup)
            if self.engine.getTelescope():
                self.scopePollTimer.Start(300)

    def OnChoiceCamChoice(self, event):
        n = event.GetEventObject().GetSelection()
        if n == 0 or self.choiceCam.GetClientData(n) is not type(self.engine.getCamera()):
            self.engine.deselectCamera()
        if n == 0:
            self.txtCam.SetLabel(_("No camera"))
            self._updateCamera()
            return
        self.engine.selectCamera(event.GetClientData())
        self._updateCamera()
        logger.debug("Camera set to %s" % self.choiceCam.GetStringSelection())

    def _updateCamera(self):
        "Update camera status display"
        if not self.engine.getCamera():
            self.txtCamStatus.SetLabel(_("Not connected"))
            self.btnGO.Disable()
        else:
            self.camSetup.Enable()
            self.btnGO.Enable()
            self.txtCamStatus.SetLabel(CameraState.State[self.engine.getCamera().cameraState])
            n = self.choiceCam.GetSelection()
            if n < 0 or self.choiceCam.GetClientData(n) != self.engine.getCamera():
                self.choiceCam.SetSelection(self.choiceCam.FindString(self.engine.getCamera().getName()))

        if not self.engine.solution:
            if self.engine.getCamera():
                self.txtCam.SetLabel(_("Previous solution"))
        else:
            self.txtCamRA.SetLabel(deg2hms(self.engine.solution.center.RA))
            self.txtCamDec.SetLabel(deg2dms(self.engine.solution.center.dec))
            hFov, vFov = self.engine.solution.fieldOfView
            fovUnit = u"\xb0"
            if hFov < 1.0 or vFov < 1.0:
                hFov *= 60.
                vFov *= 60.
                fovUnit = "'"
            self.txtField.SetLabel("%01.2f%s x %01.2f%s" % (hFov, fovUnit, vFov, fovUnit))
            if int(self.engine.solution.parity) == 1:
                self.lblMirror.SetLabel(_("Flipped"))
            else:
                self.lblMirror.SetLabel(_("Normal"))
            self.txtRotation.SetLabel("%.2f" % (self.engine.solution.rotation))
            if self.engine.lastCorrection:
                separation = self.engine.lastCorrection
                separationString = deg2str(separation.degrees)
                self.txtCam.SetLabel(_("Last error: %s") % (separationString))

    def OnConfigGridMouseEvents(self, event):
        event.Skip()

    def OnCamSetupButton(self, event):
        if not self.engine.getCamera():
            event.Skip()
            return
        if self.engine.getCamera().hasSetupDialog:
            if not self.engine.getCamera().connected:
                try:
                    self.engine.getCamera().connected = True
                except Exception, detail:
                    import traceback
                    logger.error("Camera error: %s" % traceback.format_exc())
                    self.showTracebackDialog(traceback.format_exc(), _("Camera error"))
                    return
            self.engine.getCamera().setup()
            return
        dlg = DlgCameraSetup.DlgCameraSetup(self)
        try:
            dlg.ShowModal()
        except:
            pass
        finally:
            dlg.Destroy()

    def OnBtnScopeSetupButton(self, event):
        if self.engine.getTelescope() == None:
            return
        dlg = DlgTelescopeSetup.DlgTelescopeSetup(self)
        try:
            dlg.ShowModal()
        except:
            pass
        finally:
            dlg.Destroy()

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

    def showTracebackDialog(self, traceback, header):
        diag = wx.MessageDialog(parent=self,
                                message=traceback.format_exc(),
                                caption=header,
                                style=wx.OK
                                )
        try:
            diag.ShowModal()
        except:
            pass
        finally:
            diag.Destroy()

    def OnBtnGOButton(self, event):
        if not self.engine.getCamera() or not self.engine.getSolver():
            event.Skip()
            return
        if self.engine.isBusy:
            self.engine.abort()
            self.btnGO.SetLabel(_("Aborting..."))
            return
        self.btnGO.SetLabel(_("Abort solver"))
        try:
            arcminLimit = self.numCtrlAccuracy.GetValue()
            exposeTime = self.numCtrlExposure.GetValue()
            self.engine.setExposure(exposeTime)
            if self.chkSlewTarget.IsChecked():
                if self.chkRepeat.IsChecked():
                    limit = 0
                else:
                    limit = 1
                self.engine.gotoCurrentTarget(limit=limit, threshold=arcminLimit)
            else:
                self.engine.solveCamera()
                if self.chkSync.IsChecked() and self.engine.solution:
                    self.engine.getTelescope().position = self.engine.solution.center
                    sync_error = self.engine.getTelescope().position - self.engine.solution.center
                    if sync_error.arcminutes > arcminLimit:
                        raise Exception(_("ASCOM Telescope sync error"))
        except Exception as e:
            import traceback
            logger.error("Sync failed: %s" % traceback.format_exc())
            self.showTracebackDialog(traceback.format_exc(), _("Telescope communication error"))

        finally:
            self._updateCamera()
            # update solver configuration grid from solver properties
            for row in range(self.configGrid.GetNumberRows()):
                key = self.configGrid.GetRowLabelValue(row)
                self.configGrid.SetCellValue(row, 1, str(self.engine.getSolver().getProperty(key)))

            self.engine.clearStatus()
            self.btnGO.SetLabel(_("Capture and Solve"))

    def __statusUpdater(self, status=None):
        "Update status bar and process UI events safely"
        if status:
            if DEBUG: print status
            self.SetStatusText(status)
        wx.SafeYield(self, True)
        wx.GetApp().Yield(True)

    def OnScopePollTimer(self, event):
        if not self.engine.getTelescope():
            self.choiceScope.SetSelection(0)
            self.scopePollTimer.Stop()
            map(hide, (self.txtScopeTracking, self.txtScopeSlewing))
            self.txtScopeTracking.Update()
            self.txtScopeSlewing.Update()
            map(disable, (
                self.chkSync,
                self.chkSlewTarget,
                self.chkRepeat
            ))
            return
        if not self.engine.getTelescope().connected:
            self.engine.deselectTelescope()
            return

        if self.engine.getTelescope().tracking:
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
        if self.engine.getTelescope().slewing:
            show(self.txtScopeSlewing)
            disable(self.btnGO)
        else:
            hide(self.txtScopeSlewing)
            enable(self.btnGO)
        self.txtScopeTracking.Update()
        self.txtScopeSlewing.Update()
        if self.engine.getTelescope() and self.engine.getTelescope().position:
            curPos = self.engine.getTelescope().position
            targetPos = self.engine.getTelescope().target
            self.txtRA.SetLabel(deg2hms(curPos.RA))
            self.txtDec.SetLabel(deg2dms(curPos.dec))

            # if no targetPosition, assume current position is target
            if not targetPos:
                targetPos = curPos

            self.txtScopeTargetRA.SetLabel(deg2hms(targetPos.RA))
            self.txtScopeTargetDec.SetLabel(deg2dms(targetPos.dec))

            # Show goto-error on the last solution
            if self.engine.lastCorrection:
                separation = self.engine.lastCorrection
                separationString = deg2str(separation.degrees)
                self.txtCam.SetLabel(_("Last error: %s") % (separationString))

    def OnChkSyncCheckbox(self, event):
        state = event.GetEventObject().IsChecked()
        if not state:
            self.chkSlewTarget.SetValue(False)
            self.chkRepeat.SetValue(False)

    def OnConfigGridGridCellChange(self, event):
        col, row = event.GetCol(), event.GetRow()
        key = self.configGrid.GetRowLabelValue(row)
        validator = self.engine.getSolver().propertyList[key][1]
        data = self.configGrid.GetCellValue(row, col)
        try:
            validator(data)  # test validity
            self.engine.getSolver().setProperty(key, data)
        except:
            self.SetStatusText(_("Invalid data"))
            self.configGrid.SetCellValue(row, col, str(self.engine.getSolver().getProperty(key)))

    def OnMenuFileLoadSettingsMenu(self, event):
        fileName = wx.FileSelector(
            message=_("Load settings"),
            default_path=self.engine.config.get("AstroTortilla", "settings_path"),
            flags=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST,
            wildcard=_("Config files") + " (*.cfg)|*.cfg",
        )

        if fileName:
            self.engine.loadConfig(fileName)
            self._updateSolverGrid()

    def OnMenuFileSaveSettingsMenu(self, event):
        fileName = wx.FileSelector(
            message=_("Save settings"),
            default_path=self.engine.config.get("AstroTortilla", "settings_path"),
            flags=wx.FD_SAVE,
            wildcard=_("Config files") + " (*.cfg)|*.cfg",
        )
        if not fileName:
            return
        try:
            if (fileName[-4:]).lower() != ".cfg":
                fileName += ".cfg"
            self.engine.saveConfig(fileName)
        except:
            import traceback
            logger.error("Saving settings failed: %s" % traceback.format_exc())
            self.showTracebackDialog(traceback.format_exc(), _("Error saving settings"))

    def OnMenuToolsDriftshotMenu(self, event):
        if not self.engine.isReady:
            event.Skip()
            return
        disable(self.btnGO)
        self.SetStatusText(_("Connecting to camera..."))
        if self.engine.getCamera().canAutoConnect:
            autoDisco = self.engine.getCamera().disconnectAfterCapture
            self.engine.getCamera().disconnectAfterCapture = False
        self.engine.getCamera().connected = True
        if self.engine.getCamera().needsCameraName and not self.engine.getCamera().camera:
            self.engine.getCamera().camera = self.engine.getCamera().cameraList[0]
        exposeTime = self.numCtrlExposure.GetValue()
        if exposeTime < 30.0:
            exposeTime = 30.0
        self.SetStatusText(_("Drifting: %.2f seconds") % exposeTime)
        self.engine.getCamera().capture(exposeTime)
        self.engine.getTelescope().tracking = True
        if exposeTime < 60:
            stillTime = 5
        else:
            stillTime = 10
        rateQueue = [(-14.0, exposeTime - stillTime), (14.0, (exposeTime - stillTime) / 2.)]
        tEnd = time() + exposeTime
        tLeft = tEnd - time()
        while tLeft > 0:
            if rateQueue and tLeft < rateQueue[0][1]:
                self.engine.getTelescope().RightAscensionRate = rateQueue[0][0]
                del rateQueue[0]
            sleep(0.1)
            tLeft = tEnd - time()
            if tLeft >= 0:
                self.SetStatusText(_("Drifting: %.2f seconds") % tLeft)
            wx.SafeYield(self, True)
            wx.GetApp().Yield(True)
        self.engine.getTelescope().RightAscensionRate = 0.0
        self.engine.getTelescope().tracking = True
        if self.engine.getCamera().canAutoConnect:
            self.engine.getCamera().disconnectAfterCapture = autoDisco
        self.SetStatusText(_("Waiting for camera"))
        if self.engine.getCamera().disconnectAfterCapture:
            while not self.engine.getCamera().imageReady and self.engine.getCamera().cameraState not in (
                    CameraState.Error,):
                sleep(0.2)
            self.engine.getCamera().connected = False
        enable(self.btnGO)
        self.SetStatusText(_("Drifting done."))

    def __progressUpdater(self, pct, readable=None):
        if pct < 0:
            hide(self.progress)
        else:
            show(self.progress)
            self.progress.SetValue(pct)
        wx.SafeYield(self, True)
        wx.GetApp().Yield(True)

    def OnMenuToolsGotoImage(self, event):
        if not self.engine.config.has_option("AstroTortilla", "last_gotoimage"):
            self.engine.config.set("AstroTortilla", "last_gotoimage", "")

        fileName = wx.FileSelector(
            message=_("Goto Image"),
            default_path=self.engine.config.get("AstroTortilla", "last_gotoimage"),
            flags=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST,
            wildcard=_(
                "Image files") + " (*.fit; *.fits; *.fts; *.jpg; *.tiff; *.tif; *.pnm)|*.fit; *.fits; *.fts; *.jpg; *.tiff; *.tif; *.pnm",
        )

        if fileName:
            self.engine.config.set("AstroTortilla", "last_gotoimage", fileName)
            self.btnGO.SetLabel(_("Abort solver"))
            try:
                self.engine.gotoImage(fileName)
            except:
                import traceback
                logger.error("Solver error occurred: %s" % traceback.format_exc())
                self.showTracebackDialog(traceback.format_exc(), _("Solver error"))
            self.btnGO.SetLabel(_("Capture and Solve"))
            self._updateCamera()

    def OnMenuToolsLogwindowMenu(self, event):
        if not self.__logFrame or not self.__logFrame.IsShown():
            self.__logFrame = LogFrame.create(self)
        self.__logFrame.Show()
        self.__logFrame.Iconize(False)
        self.__logFrame.Raise()

    def OnMenuBookmarksAddsolutionbmMenu(self, event):
        if not self.engine.solution:
            self.SetStatusText(_("No current solution"))
            return
        self.SetStatusText(_("Creating bookmark from current solution"))
        self.CreateBookmark(self.engine.solution)

    def CreateBookmark(self, solution):
        dlg = wx.TextEntryDialog(self, message=_("Enter a name for the bookmark"), caption=_("Bookmark name"))
        try:
            dlg.ShowModal()
            bmName = dlg.GetValue()
            bm = Bookmark(bmName, solution.center, solution.rotation)
            self.engine.addBookmark(bm)
            self.updateBookmarkMenu()
            self.SetStatusText(_("Done"))
        except:
            pass
        finally:
            dlg.Destroy()

    def OnMenuBookmarksAddimagebmMenu(self, event):
        self.SetStatusText(_("Creating bookmark from image"))
        if not self.engine.config.has_option("AstroTortilla", "last_gotoimage"):
            self.engine.config.set("AstroTortilla", "last_gotoimage", "")
        fileName = wx.FileSelector(
            message=_("Goto Image"),
            default_path=self.engine.config.get("AstroTortilla", "last_gotoimage"),
            flags=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST,
            wildcard=_(
                "Image files") + " (*.fit; *.fits; *.fts; *.jpg; *.tiff; *.tif; *.pnm)|*.fit; *.fits; *.fts; *.jpg; *.tiff; *.tif; *.pnm",
        )

        if fileName:
            self.btnGO.SetLabel(_("Abort solver"))
            target = None
            try:
                target = self.engine.solveImage(fileName)
            except:
                import traceback
                logger.error("Solver error occurred: %" % traceback.format_exc())
                self.showTracebackDialog(traceback.format_exc(), _("Solver error"))
            self.btnGO.SetLabel(_("Capture and Solve"))
            if target:
                self.CreateBookmark(target)

    def OnMenuBookmarksBookmarklistMenu(self, event):
        event.skip()

    def updateBookmarkMenu(self):
        # Clear old bookmarks from menu
        while self.menuBookmarks.GetMenuItemCount() > self.bookmarkMenuStart:
            bm = self.bookmarkMenuItems.pop()
            self.Unbind(wx.EVT_MENU, id=bm, handler=self.OnMenuBookmarksBookmarklistEntry)
            self.menuBookmarks.DeleteItem(self.menuBookmarks.FindItemByPosition(self.bookmarkMenuStart))
        self.bookmarkMap = {}
        # add bookmarks from engine to menu
        for bookmark in self.engine.bookmarks:
            i = wx.NewId()
            self.menuBookmarks.Append(help='', id=i,
                                      kind=wx.ITEM_NORMAL, text=bookmark.name)
            self.Bind(wx.EVT_MENU, self.OnMenuBookmarksBookmarklistEntry,
                      id=i)
            self.bookmarkMenuItems.append(i)
            self.bookmarkMap[i] = bookmark

    def OnMenuBookmarksBookmarklistEntry(self, event):
        bm = self.bookmarkMap[event.GetId()]
        self.engine.gotoPosition(bm.position)

    def OnMenuBookmarksEditbookmarksMenu(self, event):
        editor = BookmarkEditor.create(self)
        try:
            editor.ShowModal()
        except:
            pass
        finally:
            editor.Destroy()
        self.updateBookmarkMenu()

    def OnMainFrameMove(self, event):
        event.Skip()

    def OnMainFrameSize(self, event):
        event.Skip()

    def OnMainFrameActivate(self, event):
        event.Skip()

    def LogWindowClosed(self):
        self.__logFrame = None


if __name__ == '__main__':
    app = wx.PySimpleApp()
    frame = create(None)
    frame.Show()

    app.MainLoop()

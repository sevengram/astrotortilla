import wx
import gettext
import wx.grid
from wx.lib.anchors import LayoutAnchors

t = gettext.translation('astrotortilla', 'locale', fallback=True)
_ = t.gettext


def create(parent):
    return DlgCameraSetup(parent)


[wxID_DLGCAMERASETUP, wxID_DLGCAMERASETUPBTNCLOSE,
 wxID_DLGCAMERASETUPBTNREFRESH, wxID_DLGCAMERASETUPCHCAMNAME,
 wxID_DLGCAMERASETUPGRIDCAMERACONF, wxID_DLGCAMERASETUPLBLBINNING,
 wxID_DLGCAMERASETUPLBLCAMERANAME, wxID_DLGCAMERASETUPLBLCAMLIST,
 wxID_DLGCAMERASETUPSPINBINNING,
 ] = [wx.NewId() for _init_ctrls in range(9)]


class DlgCameraSetup(wx.Dialog):
    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wx.Dialog.__init__(self, id=wxID_DLGCAMERASETUP, name='', parent=prnt,
                           pos=wx.Point(510, 122), size=wx.Size(312, 346),
                           style=wx.DEFAULT_DIALOG_STYLE, title=_('Camera Setup'))
        self.SetClientSize(wx.Size(296, 308))

        self.gridCameraConf = wx.grid.Grid(id=wxID_DLGCAMERASETUPGRIDCAMERACONF,
                                           name='gridCameraConf', parent=self, pos=wx.Point(8, 32),
                                           size=wx.Size(240, 160), style=0)
        self.gridCameraConf.SetColLabelSize(0)
        self.gridCameraConf.SetLabel('')
        self.gridCameraConf.SetHelpText('')
        self.gridCameraConf.SetToolTipString("''")
        self.gridCameraConf.Bind(wx.EVT_MOTION, self.OnGridCameraConfMotion)
        self.gridCameraConf.Bind(wx.grid.EVT_GRID_CELL_CHANGE,
                                 self.OnGridCameraConfGridCellChange)
        self.gridCameraConf.SetConstraints(LayoutAnchors(self.gridCameraConf, True, True,
                                                         True, True))

        self.btnClose = wx.Button(id=wxID_DLGCAMERASETUPBTNCLOSE,
                                  label=_('Close'), name='btnClose', parent=self, pos=wx.Point(216,
                                                                                               280),
                                  size=wx.Size(75, 23), style=0)
        self.btnClose.Bind(wx.EVT_BUTTON, self.OnBtnCloseButton,
                           id=wxID_DLGCAMERASETUPBTNCLOSE)

        self.lblCameraName = wx.StaticText(id=wxID_DLGCAMERASETUPLBLCAMERANAME,
                                           label=_('Camera Setup'), name='lblCameraName', parent=self,
                                           pos=wx.Point(16, 8), size=wx.Size(224, 13), style=0)

        self.chCamName = wx.Choice(choices=[], id=wxID_DLGCAMERASETUPCHCAMNAME,
                                   name='chCamName', parent=self, pos=wx.Point(64, 200),
                                   size=wx.Size(146, 21), style=0)
        self.chCamName.SetToolTipString(_('Camera interface selection'))
        self.chCamName.Bind(wx.EVT_CHOICE, self.OnCamChoiceChoice,
                            id=wxID_DLGCAMERASETUPCHCAMNAME)

        self.lblCamList = wx.StaticText(id=wxID_DLGCAMERASETUPLBLCAMLIST,
                                        label=_('Camera:'), name='lblCamList', parent=self,
                                        pos=wx.Point(16, 200), size=wx.Size(41, 13), style=0)

        self.btnRefresh = wx.Button(id=wxID_DLGCAMERASETUPBTNREFRESH,
                                    label=_('Refresh list'), name='btnRefresh', parent=self,
                                    pos=wx.Point(216, 200), size=wx.Size(75, 23), style=0)
        self.btnRefresh.SetToolTipString(_('Refresh camera selection list'))
        self.btnRefresh.Bind(wx.EVT_BUTTON, self.OnBtnRefreshButton,
                             id=wxID_DLGCAMERASETUPBTNREFRESH)

        self.lblBinning = wx.StaticText(id=wxID_DLGCAMERASETUPLBLBINNING,
                                        label=_('Binning:'), name='lblBinning', parent=self,
                                        pos=wx.Point(16, 240), size=wx.Size(38, 13), style=0)

        self.spinBinning = wx.SpinCtrl(id=wxID_DLGCAMERASETUPSPINBINNING,
                                       initial=0, max=100, min=0, name='spinBinning', parent=self,
                                       pos=wx.Point(64, 232), size=wx.Size(48, 21),
                                       style=wx.SP_ARROW_KEYS)
        self.spinBinning.SetToolTipString(_('Camera binning'))

    def __init__(self, parent):
        self._init_ctrls(parent)
        self.__parent = parent
        self.camera = parent.engine.getCamera()
        if not self.camera:
            self.Destroy()
        self.gridCameraConf.ClearGrid()
        camConfig = self.camera.configuration
        self.camProps = self.camera.propertyList
        self.gridCameraConf.CreateGrid(len(camConfig), 2)
        self.gridCameraConf.SetRowLabelSize(0)
        self.gridCameraConf.DisableDragGridSize()
        self.gridCameraConf.SetColSize(1, 200)
        i = 0
        keyList = camConfig.keys()
        keyList.sort()
        for key in keyList:
            self.gridCameraConf.SetCellValue(i, 0, self.camProps[key][0])
            self.gridCameraConf.SetReadOnly(i, 0, True)
            self.gridCameraConf.SetCellValue(i, 1, str(camConfig[key]))
            self.gridCameraConf.SetRowLabelValue(i, key)
            i += 1
        wx.EVT_MOTION(self.gridCameraConf.GetGridWindow(), self.OnGridCameraConfMotion)
        self.gridCameraConf.AutoSizeColumn(0)
        self.gridCameraConf.ForceRefresh()
        self.gridCameraConf.AutoSizeColumn(0)
        self.gridCameraConf.SetColMinimalWidth(1, self.gridCameraConf.GetSize()[0] - self.gridCameraConf.GetColSize(0))
        self.gridCameraConf.AutoSizeColumns(False)
        self.gridCameraConf.Show()
        self.spinBinning.SetRange(1, self.camera.maxBin)
        self.spinBinning.SetValue(self.camera.binning)
        self.Layout()
        self.prev_rowcol = [None, None]
        self.__updateCamList()

    def __updateCamList(self):
        self.chCamName.Clear()
        camlist = self.camera.cameraList
        curCam = self.camera.camera
        map(self.chCamName.Append, camlist)
        if curCam in camlist:
            self.chCamName.SetStringSelection(curCam)
        if not camlist:
            self.lblCamList.Hide()
            self.chCamName.Disable()
            self.btnRefresh.Disable()
            self.chCamName.Hide()
            self.btnRefresh.Hide()
        else:
            self.lblCamList.Show()
            self.chCamName.Enable()
            self.chCamName.Show()
            self.btnRefresh.Enable()
            self.btnRefresh.Show()

    def OnGridCameraConfMotion(self, evt):
        # evt.GetRow() and evt.GetCol() would be nice to have here,
        # but as this is a mouse event, not a grid event, they are not
        # available and we need to compute them by hand.
        grid = self.gridCameraConf
        x, y = grid.CalcUnscrolledPosition(evt.GetPosition())
        row = grid.YToRow(y)
        col = grid.XToCol(x)
        if (row, col) != self.prev_rowcol and row >= 0 and col >= 0:
            self.prev_rowcol[:] = [row, col]
            hinttext = self.camProps[grid.GetRowLabelValue(row)][col + 2]
            if hinttext is None:
                hinttext = ''
            grid.GetGridWindow().SetToolTipString(hinttext)
        evt.Skip()

    def OnGridCameraConfGridCellChange(self, event):
        col, row = event.GetCol(), event.GetRow()
        key = self.gridCameraConf.GetRowLabelValue(row)
        rowdata = self.camProps[key]
        data = self.gridCameraConf.GetCellValue(row, col)
        if data == self.camera.getProperty(key):
            return
        try:
            rowdata[1](data)  # test validity
            self.camera.setProperty(key, data)
            self.gridCameraConf.SetColMinimalWidth(1,
                                                   self.gridCameraConf.GetSize()[0] - self.gridCameraConf.GetColSize(0))
            self.gridCameraConf.AutoSizeColumns(False)
            self.Layout()
            self.__updateCamList()
        except:
            self.gridCameraConf.SetCellValue(row, col, str(self.camera.getProperty(key)))

    def OnCamChoiceChoice(self, event):
        self.camera.camera = self.chCamName.GetStringSelection()

    def OnBtnRefreshButton(self, event):
        self.__updateCamList()

    def OnBtnCloseButton(self, event):
        try:
            self.camera.binning = self.spinBinning.GetValue()
        except:
            pass
        self.Destroy()

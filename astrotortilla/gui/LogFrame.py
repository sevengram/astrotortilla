import wx
import wx.grid
import logging
import gettext
import win32gui
from wx.lib.anchors import LayoutAnchors

logger = logging.getLogger("astrotortilla.LogFrame")

t = gettext.translation('astrotortilla', 'locale', fallback=True)
_ = t.gettext

logFrame = None


def create(parent):
    global logFrame
    if not logFrame:
        logFrame = LogWindow(parent)
    return logFrame


[wxID_LOGWINDOW, wxID_LOGWINDOWBTNCLEAR, wxID_LOGWINDOWBTNCOPY,
 wxID_LOGWINDOWCHOICELOGLEVEL, wxID_LOGWINDOWLOGGRID,
 wxID_LOGWINDOWSTATICTEXTLOGLEVEL,
 ] = [wx.NewId() for _init_ctrls in range(6)]


class LogWindowHandler(logging.Handler):
    def __init__(self, logGrid):
        logging.Handler.__init__(self)
        self.grid = logGrid
        self.grid.ClearGrid()
        self.grid.AutoSizeColumn(0)

    def emit(self, record):
        try:
            self.grid.AppendRows(1, False)
            self.grid.SetCellValue(self.grid.GetNumberRows() - 1, 0, self.format(record))
            self.grid.MakeCellVisible(self.grid.GetNumberRows() - 1, 0)
            self.grid.AutoSizeColumn(0)
            wx.SafeYield(self)
        except:
            pass  # do nothing to avoid an eternal recursion


class LogWindow(wx.Frame):
    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wx.Frame.__init__(self, id=wxID_LOGWINDOW, name='', parent=prnt,
                          pos=wx.Point(525, 152), size=wx.Size(416, 391),
                          style=wx.DEFAULT_FRAME_STYLE, title='LogWindow')
        self.SetClientSize(wx.Size(400, 353))
        self.SetMinSize(wx.Size(300, 120))
        self.Show(False)
        self.SetToolTipString('LogWindow')
        self.Bind(wx.EVT_CLOSE, self.OnLogWindowClose)
        self.Bind(wx.EVT_SIZE, self.OnLogWindowSize)
        self.Bind(wx.EVT_ACTIVATE, self.OnLogWindowActivate)
        self.Bind(wx.EVT_MOVE, self.OnLogWindowMove)

        self.staticTextLogLevel = wx.StaticText(id=wxID_LOGWINDOWSTATICTEXTLOGLEVEL,
                                                label=_('Log level'), name='staticTextLogLevel', parent=self,
                                                pos=wx.Point(0, 0), size=wx.Size(42, 13), style=0)
        self.staticTextLogLevel.SetToolTipString('')

        self.choiceLogLevel = wx.Choice(choices=[],
                                        id=wxID_LOGWINDOWCHOICELOGLEVEL, name='choiceLogLevel',
                                        parent=self, pos=wx.Point(48, 0), size=wx.Size(130, 21), style=0)
        self.choiceLogLevel.SetToolTipString(_('Active log level'))
        self.choiceLogLevel.Bind(wx.EVT_CHOICE, self.OnChoiceLogLevelChoice,
                                 id=wxID_LOGWINDOWCHOICELOGLEVEL)

        self.logGrid = wx.grid.Grid(id=wxID_LOGWINDOWLOGGRID, name='logGrid',
                                    parent=self, pos=wx.Point(0, 32), size=wx.Size(400, 320),
                                    style=0)
        self.logGrid.SetRowLabelSize(0)
        self.logGrid.SetToolTipString('')
        self.logGrid.EnableEditing(False)
        self.logGrid.SetLabel('')
        self.logGrid.SetColLabelSize(0)
        self.logGrid.SetDefaultColSize(-1)
        self.logGrid.SetAutoLayout(True)
        self.logGrid.SetConstraints(LayoutAnchors(self.logGrid, True, True,
                                                  True, True))

        self.btnClear = wx.Button(id=wxID_LOGWINDOWBTNCLEAR, label=_('Clear'),
                                  name='btnClear', parent=self, pos=wx.Point(304, 0),
                                  size=wx.Size(88, 23), style=0)
        self.btnClear.SetToolTipString(_('Clear the log'))
        self.btnClear.Bind(wx.EVT_BUTTON, self.OnBtnClearButton,
                           id=wxID_LOGWINDOWBTNCLEAR)

        self.btnCopy = wx.Button(id=wxID_LOGWINDOWBTNCOPY, label=_('Copy'),
                                 name='btnCopy', parent=self, pos=wx.Point(192, 0),
                                 size=wx.Size(80, 23), style=0)
        self.btnCopy.SetToolTipString(_('Copy selection or all to clip board'))
        self.btnCopy.Bind(wx.EVT_BUTTON, self.OnBtnCopyButton,
                          id=wxID_LOGWINDOWBTNCOPY)

    def __init__(self, parent):
        self._init_ctrls(parent)
        self._parent = parent
        for name, level in (("Critial", logging.CRITICAL),
                            ("Error", logging.ERROR),
                            ("Warning", logging.WARNING),
                            ("Info", logging.INFO),
                            ("Debug", logging.DEBUG),
                            ):
            self.choiceLogLevel.Append(name, level)
        self.logGrid.CreateGrid(0, 1)
        self.logGrid.EnableDragRowSize(False)
        self.choiceLogLevel.SetStringSelection("Info")
        logFormatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.handler = LogWindowHandler(self.logGrid)
        self.handler.setLevel(logging.INFO)
        self.handler.setFormatter(logFormatter)
        self._parent.engine.logger.addHandler(self.handler)
        # Compatibility with old configs
        x = y = w = h = -32000
        try:
            x = self._parent.engine.config.getint("Session", "LogWindowX")
            y = self._parent.engine.config.getint("Session", "LogWindowY")
            w = self._parent.engine.config.getint("Session", "LogWindowW")
            h = self._parent.engine.config.getint("Session", "LogWindowH")
        except:
            pass
        if x > -32000:
            self.SetPosition((x, y))
        if h > 0:
            self.SetSize((w, h))
        # New window placement method
        try:
            placement = self._parent.engine.config.get("Session", "LogPlacement")
            import ast
            win32gui.SetWindowPlacement(self.GetHandle(), ast.literal_eval(placement))
        except:
            pass

    def Show(self, visible=True):
        wx.Frame.Show(self, visible)
        if visible and not self.IsShownOnScreen():
            self.Center()

    def OnCloseButton(self, event):
        self.Close()

    def OnChoiceLogLevelChoice(self, event):
        try:
            self.handler.setLevel(event.GetClientData())
        except Exception, exc:  # except Exception as exc
            logger.exception(exc)
        logger.info("Log level changed to '%s'" % self.choiceLogLevel.GetStringSelection())

    def OnLogWindowClose(self, event):
        placement = win32gui.GetWindowPlacement(self.GetHandle())
        self._parent.engine.config.set("Session", "LogPlacement", str(placement))
        global logFrame
        logFrame = None
        self._parent.engine.logger.removeHandler(self.handler)
        self._parent.LogWindowClosed()
        event.Skip()

    def OnLogWindowSize(self, event):
        cwidth, cheight = self.GetClientSizeTuple()
        if cwidth < 300:
            self.SetClientSize(wx.Size(300, cheight))
            cwidth = 300
        if cheight < 120:
            self.SetClientSize(wx.Size(cwidth, 120))
            cheight = 120
        gx, gy = self.logGrid.GetPositionTuple()
        self.logGrid.SetSizeWH(cwidth - gx, cheight - gy)
        event.Skip()

    def OnBtnClearButton(self, event):
        self.logGrid.ClearGrid()
        self.logGrid.DeleteRows(0, self.logGrid.GetNumberRows(), True)
        self.logGrid.AutoSizeColumn(0)
        event.Skip()

    def OnBtnCopyButton(self, event):
        top_left = self.logGrid.GetSelectionBlockTopLeft()
        if top_left:
            bottom_right = self.logGrid.GetSelectionBlockBottomRight()
            selected = xrange(top_left[0][0], bottom_right[0][0] + 1)
        else:
            selected = [c[0] for c in self.logGrid.GetSelectedCells()]
        if not selected:
            selected = xrange(0, self.logGrid.GetNumberRows())
        logdata = []
        for row in selected:
            logdata.append(self.logGrid.GetCellValue(row, 0))
        clipBoard = wx.TextDataObject()
        clipBoard.SetText("\r\n".join(logdata))
        if wx.TheClipboard.Open():
            wx.TheClipboard.SetData(clipBoard)
            wx.TheClipboard.Close()
        event.Skip()

    def OnLogWindowActivate(self, event):
        event.Skip()

    def OnLogWindowMove(self, event):
        event.Skip()

#Boa:Frame:LogWindow

import wx
import wx.grid
import logging
logger = logging.getLogger("astrotortilla.LogFrame")


import gettext
t = gettext.translation('astrotortilla', 'locale', fallback=True)
_ = t.gettext


logFrame = None
def create(parent):
    global logFrame
    if not logFrame:
        logFrame = LogWindow(parent)
    return logFrame

[wxID_LOGWINDOW, wxID_LOGWINDOWCHOICELOGLEVEL, wxID_LOGWINDOWCLOSE, 
 wxID_LOGWINDOWLOGGRID, wxID_LOGWINDOWSTATICTEXTLOGLEVEL, 
] = [wx.NewId() for _init_ctrls in range(5)]

class LogWindowHandler(logging.Handler):
    def __init__(self, logGrid, **kwargs):
        logging.Handler.__init__(self)
        self.grid = logGrid
        self.grid.ClearGrid()
        self.grid.AutoSizeColumn(0)

        
    def emit(self, record):
        try:
            self.grid.AppendRows(1, False)
            self.grid.SetCellValue(self.grid.GetNumberRows()-1, 0, self.format(record))
            self.grid.MakeCellVisible(self.grid.GetNumberRows()-1, 0)
            self.grid.AutoSizeColumn(0)
            wx.SafeYield(self)
        except:
            pass # do nothing to avoid an eternal recursion
        

class LogWindow(wx.Frame):
    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wx.Frame.__init__(self, id=wxID_LOGWINDOW, name='', parent=prnt,
              pos=wx.Point(490, 117), size=wx.Size(408, 387),
              style=wx.DEFAULT_FRAME_STYLE, title='LogWindow')
        self.SetClientSize(wx.Size(400, 353))
        self.SetMinSize(wx.Size(300, 120))
        self.Show(False)
        self.SetToolTipString('LogWindow')
        self.Bind(wx.EVT_CLOSE, self.OnLogWindowClose)
        self.Bind(wx.EVT_SIZE, self.OnLogWindowSize)

        self.close = wx.Button(id=wxID_LOGWINDOWCLOSE, label=_('Close'),
              name='close', parent=self, pos=wx.Point(192, 0), size=wx.Size(75,
              23), style=0)
        self.close.Bind(wx.EVT_BUTTON, self.OnCloseButton,
              id=wxID_LOGWINDOWCLOSE)

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
        self.logGrid.CreateGrid(0,1)
        self.choiceLogLevel.SetStringSelection("Info")
        logFormatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.handler = LogWindowHandler(self.logGrid)
        self.handler.setLevel(logging.INFO)
        self.handler.setFormatter(logFormatter)
        self._parent.engine.logger.addHandler(self.handler)
        
        
    def OnCloseButton(self, event):
        self.Close()

    def OnChoiceLogLevelChoice(self, event):
        try:
            self.handler.setLevel(event.GetClientData())
        except Exception, exc: # except Exception as exc
            logger.exception(exc)
        logger.info("Log level changed to '%s'"%self.choiceLogLevel.GetStringSelection())

    def OnLogWindowClose(self, event):
        global logFrame
        logFrame = None
        self._parent.engine.logger.removeHandler(self.handler)        
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
        self.logGrid.SetSizeWH(cwidth-gx, cheight-gy)
        event.Skip()

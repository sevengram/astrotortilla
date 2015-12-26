import gettext
import wx
import wx.lib.intctrl

t = gettext.translation('astrotortilla', 'locale', fallback=True)
_ = t.gettext


def create(parent):
    return DlgTelescopeSetup(parent)


[wxID_DLGTELESCOPESETUP, wxID_DLGTELESCOPESETUPBTNCANCEL,
 wxID_DLGTELESCOPESETUPBTNOK, wxID_DLGTELESCOPESETUPINTPROPERTYAGE,
 wxID_DLGTELESCOPESETUPINTSLEWSETTLE,
 wxID_DLGTELESCOPESETUPLBLSCOPEPOLLPERIOD,
 wxID_DLGTELESCOPESETUPLBLSLEWSETTLETIME,
 wxID_DLGTELESCOPESETUPSLEW_SETTLE_UNIT, wxID_DLGTELESCOPESETUPSTATICTEXT2,
 ] = [wx.NewId() for _init_ctrls in range(9)]


class DlgTelescopeSetup(wx.Dialog):
    def _init_coll_gridBagSizer1_Items(self, parent):
        # generated method, don't edit

        parent.AddWindow(self.btnOK, (2, 1), border=0, flag=0, span=(1, 2))
        parent.AddWindow(self.lblSlewSettleTime, (0, 0), border=0, flag=0,
                         span=(1, 1))
        parent.AddWindow(self.intSlewSettle, (0, 1), border=0, flag=0, span=(1,
                                                                             1))
        parent.AddWindow(self.slew_settle_unit, (0, 2), border=0, flag=0,
                         span=(1, 1))
        parent.AddWindow(self.lblScopePollPeriod, (1, 0), border=0, flag=0,
                         span=(1, 1))
        parent.AddWindow(self.intPropertyAge, (1, 1), border=0, flag=0, span=(1,
                                                                              1))
        parent.AddWindow(self.staticText2, (1, 2), border=0, flag=0, span=(1, 1))
        parent.AddWindow(self.btnCancel, (2, 0), border=0, flag=0, span=(1, 1))

    def _init_sizers(self):
        # generated method, don't edit
        self.gridBagSizer1 = wx.GridBagSizer(hgap=0, vgap=0)
        self.gridBagSizer1.SetCols(3)
        self.gridBagSizer1.SetRows(3)

        self._init_coll_gridBagSizer1_Items(self.gridBagSizer1)

        self.SetSizer(self.gridBagSizer1)

    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wx.Dialog.__init__(self, id=wxID_DLGTELESCOPESETUP, name='',
                           parent=prnt, pos=wx.Point(814, 390), size=wx.Size(260, 111),
                           style=wx.DEFAULT_DIALOG_STYLE, title=_('Telescope quirks setup'))
        self.SetClientSize(wx.Size(244, 73))

        self.btnOK = wx.Button(id=wxID_DLGTELESCOPESETUPBTNOK, label=_(u'OK'),
                               name=u'btnOK', parent=self, pos=wx.Point(155, 42),
                               size=wx.Size(75, 23), style=0)
        self.btnOK.Bind(wx.EVT_BUTTON, self.OnBtnOKButton,
                        id=wxID_DLGTELESCOPESETUPBTNOK)

        self.lblSlewSettleTime = wx.StaticText(id=wxID_DLGTELESCOPESETUPLBLSLEWSETTLETIME,
                                               label=_(u'Slew settle extra wait'), name=u'lblSlewSettleTime',
                                               parent=self, pos=wx.Point(0, 0), size=wx.Size(155, 13), style=0)

        self.intSlewSettle = wx.lib.intctrl.IntCtrl(allow_long=False,
                                                    allow_none=False, default_color=wx.BLACK,
                                                    id=wxID_DLGTELESCOPESETUPINTSLEWSETTLE, limited=True, max=99,
                                                    min=0, name=u'intSlewSettle', oob_color=wx.RED, parent=self,
                                                    pos=wx.Point(155, 0), size=wx.Size(30, 21), style=0, value=0)
        self.intSlewSettle.SetMaxLength(2)
        self.intSlewSettle.SetInsertionPoint(0)

        self.slew_settle_unit = wx.StaticText(id=wxID_DLGTELESCOPESETUPSLEW_SETTLE_UNIT,
                                              label=u's', name=u'slew_settle_unit', parent=self,
                                              pos=wx.Point(185, 0), size=wx.Size(6, 13), style=0)

        self.lblScopePollPeriod = wx.StaticText(id=wxID_DLGTELESCOPESETUPLBLSCOPEPOLLPERIOD,
                                                label=_(u'Telescope property caching'),
                                                name=u'lblScopePollPeriod', parent=self, pos=wx.Point(0, 21),
                                                size=wx.Size(155, 21), style=0)

        self.intPropertyAge = wx.lib.intctrl.IntCtrl(allow_long=False,
                                                     allow_none=False, default_color=wx.BLACK,
                                                     id=wxID_DLGTELESCOPESETUPINTPROPERTYAGE, limited=False, max=10,
                                                     min=0, name=u'intPropertyAge', oob_color=wx.RED, parent=self,
                                                     pos=wx.Point(155, 21), size=wx.Size(30, 21), style=0, value=0)

        self.staticText2 = wx.StaticText(id=wxID_DLGTELESCOPESETUPSTATICTEXT2,
                                         label=u's', name='staticText2', parent=self, pos=wx.Point(185,
                                                                                                   21),
                                         size=wx.Size(55, 13), style=0)

        self.btnCancel = wx.Button(id=wxID_DLGTELESCOPESETUPBTNCANCEL,
                                   label=_(u'Cancel'), name=u'btnCancel', parent=self,
                                   pos=wx.Point(0, 42), size=wx.Size(75, 23), style=0)
        self.btnCancel.Bind(wx.EVT_BUTTON, self.OnBtnCancelButton,
                            id=wxID_DLGTELESCOPESETUPBTNCANCEL)

        self._init_sizers()

    def __init__(self, parent):
        self._init_ctrls(parent)
        self.__parent = parent
        scope = self.__parent.engine.getTelescope()
        if scope:
            self.intSlewSettle.SetValue(int(float(scope.getProperty("slewSettleTime"))))
            self.intPropertyAge.SetValue(int(float(scope.getProperty("propertyAgeLimit"))))

    def OnBtnOKButton(self, event):
        scope = self.__parent.engine.getTelescope()
        if scope:
            scope.setProperty("slewSettleTime", str(self.intSlewSettle.GetValue()))
            scope.setProperty("propertyAgeLimit", str(self.intPropertyAge.GetValue()))
        self.Close()

    def OnBtnCancelButton(self, event):
        self.Close()

#Boa:Dialog:DlgHelpAbout

import wx
import wx.richtext
import gettext
t = gettext.translation('helpabout', 'locale', fallback=True)
_ = t.gettext


def create(parent):
    return DlgHelpAbout(parent)

[wxID_DLGHELPABOUT, wxID_DLGHELPABOUTCLOSE, wxID_DLGHELPABOUTRICHTEXTCTRL1, 
 wxID_DLGHELPABOUTSTATICTEXT1, 
] = [wx.NewId() for _init_ctrls in range(4)]

class DlgHelpAbout(wx.Dialog):
    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wx.Dialog.__init__(self, id=wxID_DLGHELPABOUT, name='', parent=prnt,
              pos=wx.Point(568, 131), size=wx.Size(292, 315),
              style=wx.DEFAULT_DIALOG_STYLE, title='Help About')
        self.SetClientSize(wx.Size(284, 281))

        self.close = wx.Button(id=wxID_DLGHELPABOUTCLOSE, label='Close',
              name='close', parent=self, pos=wx.Point(104, 240),
              size=wx.Size(75, 23), style=0)
        self.close.Center(wx.HORIZONTAL)
        self.close.SetToolTipString('Close')
        self.close.SetHelpText('Close')
        self.close.Bind(wx.EVT_BUTTON, self.OnCloseButton,
              id=wxID_DLGHELPABOUTCLOSE)

        self.staticText1 = wx.StaticText(id=wxID_DLGHELPABOUTSTATICTEXT1,
              label='AstroTorilla v0.1', name='staticText1', parent=self,
              pos=wx.Point(16, 16), size=wx.Size(79, 13), style=0)

        self.richTextCtrl1 = wx.richtext.RichTextCtrl(id=wxID_DLGHELPABOUTRICHTEXTCTRL1,
              parent=self, pos=wx.Point(16, 32), size=wx.Size(248, 200),
              style=wx.richtext.RE_MULTILINE,
              value='AstroTortilla is aimed for automating telescope GoTo corrections using plate-solving. It uses the astromate wrapper library for telescope control, image capture and plate-solving. See the files README and LICENSE for details.\n\nAstroTortilla and astromate library are licensed under the GNU General Public License v2.\n\nAstroTortilla and astromate library use:\n * Python\n * PyWX\n * win32all for Python\n * Python Imaging Library (PIL)\n * Astrometry.net astrometrical plate-solving SW\n * CygWin (for executing Astrometry.net)\n\nCopyright 2010-2011 Antti Kuntsi <mickut@gmail.com>')
        self.richTextCtrl1.SetLabel('text')

    def __init__(self, parent):
        self._init_ctrls(parent)

    def OnCloseButton(self, event):
        self.Close()

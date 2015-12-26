import wx
import logging
import gettext
import wx.grid
from wx.lib.anchors import LayoutAnchors

from astrotortilla.units import deg2hms, deg2dms, Coordinate
from astrotortilla.bookmark import Bookmark

logger = logging.getLogger("astrotortilla.BookmarkEditor")

t = gettext.translation('astrotortilla', 'locale', fallback=True)
_ = t.gettext


def create(parent):
    return BookmarkEditor(parent)


[wxID_BOOKMARKEDITOR, wxID_BOOKMARKEDITORBTNCANCEL, wxID_BOOKMARKEDITORBTNOK,
 wxID_BOOKMARKEDITORGRID1,
 ] = [wx.NewId() for _init_ctrls in range(4)]


class BookmarkEditor(wx.Dialog):
    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wx.Dialog.__init__(self, id=wxID_BOOKMARKEDITOR, name='BookmarkEditor',
                           parent=prnt, pos=wx.Point(577, 332), size=wx.Size(316, 158),
                           style=wx.DEFAULT_FRAME_STYLE, title=_('Edit bookmarks'))
        self.SetClientSize(wx.Size(300, 120))
        self.SetAutoLayout(True)
        self.SetThemeEnabled(False)
        self.SetToolTipString('')
        self.SetMinSize(wx.Size(300, 120))
        self.Show(False)
        self.Bind(wx.EVT_SIZE, self.OnBookmarkEditorWindowSize)
        self.Bind(wx.EVT_CLOSE, self.OnBookmarkEditorClose)

        self.btnOK = wx.Button(id=wxID_BOOKMARKEDITORBTNOK, label=_('OK'),
                               name='btnOK', parent=self, pos=wx.Point(223, 93),
                               size=wx.Size(75, 23), style=0)
        self.btnOK.SetConstraints(LayoutAnchors(self.btnOK, False, False, True,
                                                True))
        self.btnOK.SetToolTipString('Close')
        self.btnOK.Bind(wx.EVT_BUTTON, self.OnBtnOKButton,
                        id=wxID_BOOKMARKEDITORBTNOK)

        self.grid1 = wx.grid.Grid(id=wxID_BOOKMARKEDITORGRID1, name='grid1',
                                  parent=self, pos=wx.Point(0, 0), size=wx.Size(300, 88), style=0)
        self.grid1.SetAutoLayout(True)
        self.grid1.SetRowLabelSize(200)
        self.grid1.SetConstraints(LayoutAnchors(self.grid1, True, True, True,
                                                True))

        self.btnCancel = wx.Button(id=wxID_BOOKMARKEDITORBTNCANCEL,
                                   label=_('Cancel'), name='btnCancel', parent=self,
                                   pos=wx.Point(135, 93), size=wx.Size(75, 23), style=0)
        self.btnCancel.SetConstraints(LayoutAnchors(self.btnCancel, False,
                                                    False, True, True))
        self.btnCancel.Bind(wx.EVT_BUTTON, self.OnBtnCancelButton,
                            id=wxID_BOOKMARKEDITORBTNCANCEL)

    def __init__(self, parent):
        self._init_ctrls(parent)
        self.parent = parent
        self.__currentBM = -1
        self.grid1.CreateGrid(0, 4)
        self.grid1.SetAutoLayout(True)
        self.grid1.EnableDragGridSize()
        self.grid1.EnableDragColMove()
        self.grid1.SetColLabelValue(0, _("RA"))
        self.grid1.SetColLabelValue(1, _("Declination"))
        self.grid1.SetColLabelValue(2, _("Rotation"))
        self.grid1.SetColLabelValue(3, _("Bookmark name"))
        self.grid1.SetRowLabelSize(32)
        for bookmark in self.parent.engine.bookmarks:
            self.grid1.AppendRows(1, False)
            row = self.grid1.GetNumberRows() - 1
            self.grid1.SetRowLabelValue(row, "%d" % (row + 1))
            self.grid1.SetCellValue(row, 0, deg2hms(bookmark.position.RA))
            self.grid1.SetCellValue(row, 1, deg2dms(bookmark.position.dec))
            self.grid1.SetCellValue(row, 2, "%.2f" % bookmark.camera_angle)
            self.grid1.SetCellValue(row, 3, bookmark.name)
        self.grid1.AutoSizeColumns(True)
        self.grid1.AutoSizeRows(True)
        self.grid1.AutoSize()
        self.grid1.Bind(wx.grid.EVT_GRID_CELL_RIGHT_CLICK,
                        self.showPopupMenu)
        x = y = w = h = -1
        try:
            x = self.parent.engine.config.getint("Session", "BmEditorWindowX")
            y = self.parent.engine.config.getint("Session", "BmEditorWindowY")
            w = self.parent.engine.config.getint("Session", "BmEditorWindowW")
            h = self.parent.engine.config.getint("Session", "BmEditorWindowH")
        except:
            pass
        if h != -1:
            self.SetPosition((x, y))
            self.SetSize((w, h))

    def OnBtnOKButton(self, event):
        newBookmarks = []
        errors = []
        for row in xrange(self.grid1.GetNumberRows()):
            try:
                ra = self.grid1.GetCellValue(row, 0)
                dec = self.grid1.GetCellValue(row, 1)
                position = Coordinate(ra, dec)
                angle = float(self.grid1.GetCellValue(row, 2))
                name = self.grid1.GetCellValue(row, 3)
                bm = Bookmark(name, position, angle)
                newBookmarks.append(bm)
            except:
                errors.append("%d" % (row + 1))
        if not errors:
            self.parent.engine.replaceBookmarks(newBookmarks)
            self.Close()
        else:
            diag = wx.MessageDialog(parent=self,
                                    message=_("Invalid values on row(s):") + " " + ", ".join(errors),
                                    caption=_("Bookmark coordinate error"),
                                    style=wx.OK
                                    )
            try:
                diag.ShowModal()
            except:
                pass
            finally:
                diag.Destroy()
        event.Skip()

    def OnBookmarkEditorWindowSize(self, event):
        cwidth, cheight = self.GetClientSizeTuple()
        self.SetClientSize(wx.Size(max(cwidth, 300), max(cheight, 120)))
        event.Skip()

    def OnBtnCancelButton(self, event):
        self.Close()
        event.Skip()

    def showPopupMenu(self, event):
        """
        Create and display a popup menu on right-click event
        """
        if not hasattr(self, "popupID1"):
            self.popupID1 = wx.NewId()
            self.popupID2 = wx.NewId()
            # self.popupID3 = wx.NewId()
            # Bind event handlers only once
            self.Bind(wx.EVT_MENU, self.OnCtxMenuDeleteBookmark,
                      id=self.popupID1)
            self.Bind(wx.EVT_MENU, self.OnCtxMenuInsertBookmark,
                      id=self.popupID2)

        # make a menu
        self.__currentBM = event.GetRow()
        menu = wx.Menu()
        # Show how to put an icon in the menu
        item = wx.MenuItem(menu, self.popupID1, _("Delete bookmark"))
        menu.AppendItem(item)
        item = wx.MenuItem(menu, self.popupID2, _("New bookmark"))

        menu.AppendItem(item)
        # menu.Append(self.popupID3, "Three")

        # Popup the menu. If an item is selected then its handler will be called before PopupMenu returns.
        self.PopupMenu(menu)
        menu.Destroy()

    def OnCtxMenuDeleteBookmark(self, event):
        try:
            self.grid1.DeleteRows(self.__currentBM)
            self.grid1.ForceRefresh()
        except:
            pass
        for row in xrange(self.grid1.GetNumberRows()):
            self.grid1.SetRowLabelValue(row, "%d" % (row + 1))
        self.grid1.ForceRefresh()
        event.Skip()

    def OnCtxMenuInsertBookmark(self, event):
        self.grid1.InsertRows(self.__currentBM + 1)
        self.grid1.ForceRefresh()
        for row in xrange(self.grid1.GetNumberRows()):
            self.grid1.SetRowLabelValue(row, "%d" % (row + 1))
        self.grid1.ForceRefresh()
        event.Skip()

    def OnBookmarkEditorClose(self, event):
        try:
            x, y = self.GetPosition()
            w, h = self.GetSize()
            self.parent.engine.config.set("Session", "BmEditorWindowX", str(x))
            self.parent.engine.config.set("Session", "BmEditorWindowY", str(y))
            self.parent.engine.config.set("Session", "BmEditorWindowW", str(w))
            self.parent.engine.config.set("Session", "BmEditorWindowH", str(h))
        except:
            pass
        event.Skip()

#!/usr/bin/env python

import wx
import logging
import astrotortilla.gui.MainFrame as MainFrame

logger = logging.getLogger("astrotortilla.main")

modules = {u'BookmarkEditor': [0, '', u'astrotortilla/gui/BookmarkEditor.py'],
           u'DlgCameraSetup': [0, '', u'astrotortilla/gui/DlgCameraSetup.py'],
           u'DlgHelpAbout': [0, '', u'astrotortilla/gui/DlgHelpAbout.py'],
           u'DlgTelescopeSetup': [0, '', u'astrotortilla/gui/DlgTelescopeSetup.py'],
           u'LogFrame': [0, u'Log window', u'astrotortilla/gui/LogFrame.py'],
           u'MainFrame': [1, u'Main frame of Application', u'astrotortilla/gui/MainFrame.py']}


class BoaApp(wx.App):
    def OnInit(self):
        self.main = MainFrame.create(None)
        self.main.choiceSolver.Clear()
        self.__populateChoiceList(self.main.choiceSolver, self.main.engine.listSolvers())
        if len(self.main.engine.listSolvers()) == 1:
            self.main.engine.selectSolver(self.main.engine.listSolvers()[0][0])
            self.main.choiceSolver.SetSelection(0)
            self.main.choiceSolver.Disable()
            self.main._updateSolverGrid()
        else:
            self.main.configGrid.Show(False)
        self.main.choiceCam.Clear()
        self.main.choiceCam.Append("Disconnected")
        self.main.choiceCam.SetSelection(0)
        self.__populateChoiceList(self.main.choiceCam, self.main.engine.listCameras())

        self.main.choiceScope.Clear()
        self.main.choiceScope.Append("Disconnected")
        self.main.choiceScope.SetSelection(0)
        self.__populateChoiceList(self.main.choiceScope, self.main.engine.listTelescopes())

        self.main.scopePollTimer.Start(1, False)
        self.main.chkSync.SetValue(False)
        self.main.chkSlewTarget.SetValue(False)
        self.main.chkRepeat.SetValue(False)
        self.main._updateCamera()
        self.main.Show()
        self.SetTopWindow(self.main)
        # update GUI on engine status
        if self.main.engine.getCamera():
            self.main.choiceCam.SetStringSelection(self.main.engine.getCameraName())
            self.main._updateCamera()
        if self.main.engine.getSolver():
            self.main.choiceSolver.SetStringSelection(self.main.engine.getSolverName())
            self.main._updateSolverGrid()
        return True

    def __populateChoiceList(self, choiceList, choices):
        for className, classRef in choices:
            choiceList.Append(classRef.getName(), className)


if __name__ == '__main__':
    application = BoaApp(redirect=0)
    application.MainLoop()
    del application
    wx.Exit()

#!/usr/bin/env python

import wx
import logging
import astrotortilla.gui.MainFrame as MainFrame

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

modules = {'DlgCameraSetup': [0, '', 'astrotortilla/gui/DlgCameraSetup.py'],
           'DlgHelpAbout': [0, '', 'astrotortilla/gui/DlgHelpAbout.py'],
           'DlgTelescopeSetup': [0, '', 'astrotortilla/gui/DlgTelescopeSetup.py'],
           'MainFrame': [1, 'Main frame of Application', 'astrotortilla/gui/MainFrame.py']}


class BoaApp(wx.App):
    def OnInit(self):
        self.main = MainFrame.create(None)
        self.main.choiceSolver.Clear()
        self.__populateChoiceList(self.main.choiceSolver, self.main.engine.listSolvers())

        self.main.engine.selectSolver(self.main.engine.listSolvers()[0][0])
        self.main.choiceSolver.SetSelection(0)
        self.main.updateSolverGrid()

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
        self.main.updateCamera()
        self.main.Show()
        self.SetTopWindow(self.main)

        # update GUI on engine status
        if self.main.engine.getCamera():
            self.main.choiceCam.SetStringSelection(self.main.engine.getCameraName())
            self.main.updateCamera()
        if self.main.engine.getSolver():
            self.main.choiceSolver.SetStringSelection(self.main.engine.getSolverName())
            self.main.updateSolverGrid()
        return True

    def __populateChoiceList(self, choiceList, choices):
        for className, classRef in choices:
            choiceList.Append(classRef.getName(), className)


if __name__ == '__main__':
    application = BoaApp(redirect=0)
    application.MainLoop()
    del application
    wx.Exit()

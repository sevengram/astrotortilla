#!/usr/bin/env python
#Boa:App:BoaApp

import wx

import astromate.gui.MainFrame as MainFrame
import astromate.camera, astromate.solver, astromate.telescope
from astromate.IPlateSolver import IPlateSolver
from astromate.ICamera import ICamera
from astromate.ITelescope import ITelescope
from inspect import isclass, getmembers
import sys

modules ={u'DlgCameraSetup': [0, '', u'astromate/gui/DlgCameraSetup.py'],
 'DlgHelpAbout': [0, '', u'astromate/gui/DlgHelpAbout.py'],
 'MainFrame': [1, 'Main frame of Application', u'astromate/gui/MainFrame.py'],
 u'PolarAlignFrame': [0,
                      u'Polar alignment frame',
                      u'astromate/gui/PolarAlignFrame.py']}

class BoaApp(wx.App):
    def OnInit(self):
        self.main = MainFrame.create(None)
        self.main.choiceSolver.Clear()
        #self.__populateChoiceList(self.main.choiceSolver, astromate.solver, IPlateSolver)
        self.__populateChoiceList(self.main.choiceSolver, self.main.engine.listSolvers())
        #if len(astromate.solver.__all__) == 1:
        if len(self.main.engine.listSolvers()) == 1:
            self.main.engine.selectSolver(self.main.engine.listSolvers()[0])
            self.main.choiceSolver.SetSelection(0)
            self.main.choiceSolver.Disable()
            self.main._updateSolverGrid()
        else:
            self.main.configGrid.Show(False)
        self.main.choiceCam.Clear()
        self.main.choiceCam.Append("Disconnected")
        self.main.choiceCam.SetSelection(0)
        #self.__populateChoiceList(self.main.choiceCam, astromate.camera, ICamera)
        self.__populateChoiceList(self.main.choiceCam, self.main.engine.listCameras())
        
        self.main.choiceScope.Clear()
        self.main.choiceScope.Append("Disconnected")
        self.main.choiceScope.SetSelection(0)
        #self.__populateChoiceList(self.main.choiceScope, astromate.telescope, ITelescope)
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
        for className in choices:
            choiceList.Append(className, className)

    #def __populateChoiceList(self, choiceList, moduleRef, baseClass):
    #    for module in moduleRef.__all__:
    #        fqmn = moduleRef.__name__+"."+module
    #        mod_ = __import__(fqmn, globals(), locals())
    #        solvers = getmembers(sys.modules[fqmn], lambda m: isclass(m) and issubclass(m, baseClass) and m is not baseClass)
    #        for className, classRef in solvers:
    #            choiceList.Append(className, classRef)

def main():
    application = BoaApp(0)
    application.MainLoop()

if __name__ == '__main__':
    main()

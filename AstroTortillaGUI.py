#!/usr/bin/env python
#Boa:App:BoaApp

import wx

import astrotortilla.engine
import astrotortilla.gui.MainFrame as MainFrame
import astrotortilla.camera, astrotortilla.solver, astrotortilla.telescope
from astrotortilla.IPlateSolver import IPlateSolver
from astrotortilla.ICamera import ICamera
from astrotortilla.ITelescope import ITelescope
from inspect import isclass, getmembers
import sys

import logging
logger = logging.getLogger("astrotortilla.main")

modules ={u'DlgCameraSetup': [0, '', u'astrotortilla/gui/DlgCameraSetup.py'],
 'DlgHelpAbout': [0, '', u'astrotortilla/gui/DlgHelpAbout.py'],
 u'LogFrame': [0, 'Log window', u'astrotortilla/gui/LogFrame.py'],
 'MainFrame': [1,
               'Main frame of Application',
               u'astrotortilla/gui/MainFrame.py'],
 u'PolarAlignFrame': [0,
                      u'Polar alignment frame',
                      u'astrotortilla/gui/PolarAlignFrame.py']}

class BoaApp(wx.App):
    def OnInit(self):
        self.main = MainFrame.create(None)
        self.main.choiceSolver.Clear()
        #self.__populateChoiceList(self.main.choiceSolver, astrotortilla.solver, IPlateSolver)
        self.__populateChoiceList(self.main.choiceSolver, self.main.engine.listSolvers())
        #if len(astrotortilla.solver.__all__) == 1:
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
        #self.__populateChoiceList(self.main.choiceCam, astrotortilla.camera, ICamera)
        self.__populateChoiceList(self.main.choiceCam, self.main.engine.listCameras())
        
        self.main.choiceScope.Clear()
        self.main.choiceScope.Append("Disconnected")
        self.main.choiceScope.SetSelection(0)
        #self.__populateChoiceList(self.main.choiceScope, astrotortilla.telescope, ITelescope)
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
    logger.info("Closed")

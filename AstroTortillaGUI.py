#!/usr/bin/env python
#Boa:App:BoaApp

import sys

import wx

import astrotortilla.engine
import astrotortilla.gui.MainFrame as MainFrame
import astrotortilla.camera, astrotortilla.solver, astrotortilla.telescope
from astrotortilla.IPlateSolver import IPlateSolver
from astrotortilla.ICamera import ICamera
from astrotortilla.ITelescope import ITelescope
from inspect import isclass, getmembers

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
            self.main.engine.selectSolver(self.main.engine.listSolvers()[0][0])
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
        for className, classRef in choices:
            choiceList.Append(classRef.getName(), className)

    #def __populateChoiceList(self, choiceList, moduleRef, baseClass):
    #    for module in moduleRef.__all__:
    #        fqmn = moduleRef.__name__+"."+module
    #        mod_ = __import__(fqmn, globals(), locals())
    #        solvers = getmembers(sys.modules[fqmn], lambda m: isclass(m) and issubclass(m, baseClass) and m is not baseClass)
    #        for className, classRef in solvers:
    #            choiceList.Append(className, classRef)

def main():
    application = BoaApp(redirect=0)
    application.MainLoop()
    del application
    wx.Exit()

if __name__ == '__main__':
    import threading
    main()
    ## wx+win32ui causes the python interpreter not to exit on win7, so kill
    ## the current process.
##Maybe cured with forcibly GC'ing the wx.App and exiting wx
    #import platform
    #if '7' in platform.win32_ver()[:1]:
    #    import os, signal
    #    os.kill(os.getpid(), signal.SIGTERM)

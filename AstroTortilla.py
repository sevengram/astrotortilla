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
 'MainFrame': [1, 'Main frame of Application', u'astromate/gui/MainFrame.py']}

class BoaApp(wx.App):
    def OnInit(self):
        self.main = MainFrame.create(None)
        self.main.choiceSolver.Clear()
        self.__populateChoiceList(self.main.choiceSolver, astromate.solver, IPlateSolver)
        if len(astromate.solver.__all__) == 1:
            self.main.choiceSolver.SetSelection(0)
            self.main.choiceSolver.Disable()
            self.main._selectSolver(0)
        else:
            self.main.configGrid.Show(False)
        self.main.choiceCam.Clear()
        self.main.choiceCam.Append("Disconnected")
        self.main.choiceCam.SetSelection(0)
        self.__populateChoiceList(self.main.choiceCam, astromate.camera, ICamera)
        
        self.main.choiceScope.Clear()
        self.main.choiceScope.Append("Disconnected")
        self.main.choiceScope.SetSelection(0)
        self.__populateChoiceList(self.main.choiceScope, astromate.telescope, ITelescope)
        
        self.main.scopePollTimer.Start(1, False)
        self.main.chkSync.SetValue(False)
        self.main.chkSlewTarget.SetValue(False)
        self.main.chkRepeat.SetValue(False)
        self.main._updateCamera()
        self.main.Show()
        self.SetTopWindow(self.main)
        return True

    def __populateChoiceList(self, choiceList, moduleRef, baseClass):
        for module in moduleRef.__all__:
            fqmn = moduleRef.__name__+"."+module
            mod_ = __import__(fqmn, globals(), locals(), "", -1)
            solvers = getmembers(sys.modules[fqmn], lambda m: isclass(m) and issubclass(m, baseClass) and m is not baseClass)
            for className, classRef in solvers:
                choiceList.Append(className, classRef)

def main():
    application = BoaApp(0)
    application.MainLoop()

if __name__ == '__main__':
    main()

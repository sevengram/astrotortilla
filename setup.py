#!/usr/bin/python
"""Setup AstroTortilla for py2exe and distutils"""

from distutils.core import setup
import py2exe
from glob import glob
import os.path
import platform, sys

VERSION = "0.4.3.0"
VERSIONTAG = ""

data_files = []

gdidll = os.path.join(sys.prefix, r"lib\site-packages\wx-2.8-msw-unicode\wx\gdiplus.dll")
if os.path.exists(gdidll):
    data_files.append( ("", [gdidll]) )
data_files.append( (r"locale/fi/LC_MESSAGES", glob(r"locale/fi/LC_MESSAGES/*.mo")) )
data_files.append( ("docs", glob("docs/*.pdf")) )

other_resources = [(u"VERSION", 1, VERSION)]
if VERSIONTAG:
	other_resources.append((u"VERSIONTAG", 2, VERSIONTAG))


setup(
        name = "AstroTortilla",
        windows = [
            {
                "script":"AstroTortillaGUI.py",
                "other_resources":other_resources,
                "icon_resources":[(0, "astrotortilla.ico"), (1, "astrotortilla-16c.ico"), (42, "astrotortilla-16.ico")],
                "dest_base":"AstroTortilla",
            }
        ],
        version = VERSION,
        packages = ["astrotortilla",
                    "astrotortilla.gui", 
                    "astrotortilla.camera",
                    "astrotortilla.solver", 
                    "astrotortilla.telescope",
                    "libs",
                    "libs.appdirs"
        ],
        options = { 
                "py2exe":
                {
                    "dll_excludes":["MSVCP90.dll", "MFC90.dll"],
                    "includes" : [
                        "astrotortilla.camera.*",
                        "astrotortilla.solver.*",
                        "astrotortilla.telescope.*",
                        "libs.appdirs.*"
                    ],
                    "excludes":[
                        '_ssl', 'doctest', 'unittest', 'calendar', 'email'
                    ],
                    "packages":[
                        "encodings", "pywinauto",
                        "pywinauto.controls", "pywinauto.tests"
                    ],
                    "bundle_files": 3,
                    "optimize":2,
                }
        },
        data_files = data_files,
    )

# Make a copy of readme as readme.txt for installer
file("README.txt", "w").write(file("README").read())
if not os.path.exists("setup.exe"):
    import urllib
    print "Fetching Cygwin setup.exe"
    urllib.urlretrieve("http://cygwin.com/setup.exe", "setup.exe")

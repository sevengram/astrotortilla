@echo off
rem build with py2exe
rem
setlocal

if exist "C:\python27-32bit\python.exe" (
	set PYTHON="C:\python27-32bit\python.exe"
	set PYTHONPATH="C:\python27-32bit"
)

if exist "C:\program files\Inno Setup 5\iscc.exe" (
	set INNOSETUP="C:\program files\Inno Setup 5\iscc.exe"
)
if exist "C:\Program Files (x86)\Inno Setup 5\iscc.exe" (
	set INNOSETUP="c:\Program Files (x86)\Inno Setup 5\iscc.exe"
)

if x%PYTHON% == x (
echo Python not found.
GOTO END
)
if x%INNOSETUP% == x (
echo InnoSetup compiler not found.
GOTO END
)

echo #define VCRedist "vcredist_x86.exe" > current_build.iss
echo #define Platform "x86" >> current_build.iss

echo *** rebuilding localization files ***
pushd locale\fi\LC_MESSAGES
%PYTHON% %PYTHONPATH%\Tools\i18n\msgfmt.py AstroTortilla.po
popd

rmdir /q /s build dist
%PYTHON% setup.py -q py2exe
echo *** building setup executable ***
%INNOSETUP% /q setup.iss
FOR /F "delims=" %%I IN ('DIR output /B /O:-D') DO echo "*** output\%%I ***"  & GOTO :END

:END
endlocal

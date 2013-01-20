@echo off
rem build with py2exe
rem
setlocal

if exist "\python27\python.exe" (
	set PYTHON="\python27\python.exe"
	set PYTHONPATH="\python27"
)

if exist "\program files\Inno Setup 5\iscc.exe" (
	set INNOSETUP="\program files\Inno Setup 5\iscc.exe"
)
if exist "\Program Files (x86)\Inno Setup 5\iscc.exe" (
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

echo #define VCRedist "vcredist_x64.exe" > current_build.iss
echo #define Platform "x64" >> current_build.iss

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

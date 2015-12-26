rem Generates the i18n .pot message file
rem Use poedit to update the existing translation from the
rem locale/astrotortilla.pot file

if exist "D:\Program Files\python27\python.exe" (
    set PYTHON="D:\Program Files\python27\python.exe"
    set PYTHONPATH="D:\Program Files\python27"
)

%PYTHONPATH%\Tools\i18n\pygettext.py -a -p locale -d astrotortilla AstroTortillaGUI.py astrotortilla libs

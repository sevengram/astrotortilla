rem Generates the i18n .pot message file
rem Use poedit to update the existing translation from the
rem locale/astrotortilla.pot file
\Python27\Tools\i18n\pygettext.py -a -p locale -d astrotortilla AstroTortillaGUI.py astrotortilla libs

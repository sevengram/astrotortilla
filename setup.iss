; Script generated by the Inno Setup Script Wizard.
; SEE THE DOCUMENTATION FOR DETAILS ON CREATING INNO SETUP SCRIPT FILES!

#define AstroTortilla "AstroTortilla"
#define TortillaVersion GetFileVersion(AddBackslash(SourcePath) + "Dist\\AstroTortilla.exe")
#ifexist "vcredist_x64.exe"
#define VCRedist "vcredist_x64.exe"
#define Platform "amd64"
#else
#define VCRedist "vcredist_x86.exe"
#define Platform "x86"
#endif

[Setup]
; NOTE: The value of AppId uniquely identifies this application.
; Do not use the same AppId value in installers for other applications.
; (To generate a new GUID, click Tools | Generate GUID inside the IDE.)
AppId={{B42B2870-EC8A-4D2D-90E6-9075D4DB5960}
AppName={#AstroTortilla}
AppVersion={#TortillaVersion}
AppVerName={#AstroTortilla} version {#TortillaVersion}
AppPublisherURL=http://astrotortilla.sf.net
AppSupportURL=http://astrotortilla.sf.net
AppUpdatesURL=http://astrotortilla.sf.net
DefaultDirName={pf}\{#AstroTortilla}
DefaultGroupName={#AstroTortilla}
AllowNoIcons=yes
LicenseFile=LICENSE
Compression=lzma
SolidCompression=yes
OutputBaseFilename={#AstroTortilla}-{#TortillaVersion}-{#Platform}

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "finnish"; MessagesFile: "compiler:Languages\Finnish.isl"

[CustomMessages]
Install2=Install %1 and %2
finnish.Install2=Asenna %1 ja %2
Installer=%1 setup
finnish.Installer=%1 asetukset
FullInstallation=Install {#AstroTortilla}, Cygwin and astrometry.net
finnish.FullInstallation=Asenna {#AstroTortilla}, Cygwin ja astrometry.net
NoCygwin=Install {#AstroTortilla} only
finnish.NoCygwin=Asenna vain {#AstroTortilla}
And=%1 and %2
finnish.And=%1 ja %2

[Types]
Name: "full"; Description: "{cm:FullInstallation}"
Name: "nocygwin"; Description: "{cm:NoCygwin}"

[Components]
Name: "AstroTortilla"; Types: full nocygwin; Description: "AstroTortilla"      
Name: "cygwin"; Types: full; Description: "{cm:And,Cygwin,astrometry.net}"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 0,6.1

[Files]
Source: "dist\AstroTortilla.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\*"; DestDir: "{app}";
Source: "dist\docs\*"; DestDir: "{app}\docs";
Source: "dist\locale\*"; DestDir: "{app}\locale"; Flags: recursesubdirs
Source: "LICENSE"; DestDir: "{app}";
Source: "AstrometryNetPackages.txt"; DestDir: "{app}";
Source: "README.txt"; DestDir: "{app}"; Flags: isreadme
; NOTE: Don't use "Flags: ignoreversion" on any shared system files
Source: {#VCRedist}; DestDir: {tmp}; Flags: ignoreversion
Source: "setup.exe"; DestDir: "{app}";

[Icons]
Name: "{group}\AstroTortilla"; Filename: "{app}\AstroTortilla.exe"
Name: "{group}\Getting started (English)"; Filename: "{app}\docs\Getting_Started_with_AstroTortilla.pdf"
Name: "{group}\User guide (English)"; Filename: "{app}\docs\AstroTortilla_user_guide.pdf"
Name: "{group}\Pikaopas (Finnish)"; Filename: "{app}\docs\AstroTortilla_pikaopas.pdf"
Name: "{group}\K�ytt�ohje (Finnish)"; Filename: "{app}\docs\AstroTortilla_kayttoohje.pdf"
Name: "{group}\{cm:UninstallProgram,AstroTortilla}"; Filename: "{uninstallexe}"
Name: "{group}\{cm:Installer,Cygwin}"; Filename: "{app}\setup.exe"; Parameters: "-P astrometry.net -K http://sourceforge.net/projects/astrotortilla/files/cygwin-custom/tortilla.gpg -s http://sourceforge.net/projects/astrotortilla/files/cygwin-custom"
Name: "{commondesktop}\AstroTortilla"; Filename: "{app}\AstroTortilla.exe"; Tasks: desktopicon
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\AstroTortilla"; Filename: "{app}\AstroTortilla.exe"; Tasks: quicklaunchicon

[Run]
Filename: "{tmp}\{#VCRedist}"; WorkingDir: {tmp}; Flags: skipifdoesntexist; StatusMsg: "Checking for and installing ""Microsoft Visual C++ Redistributable Package"" if needed, This can take several minutes..."
Filename: "{app}\setup.exe"; Components: cygwin;Parameters: "-P astrometry.net -K http://sourceforge.net/projects/astrotortilla/files/cygwin-custom/tortilla.gpg -s http://sourceforge.net/projects/astrotortilla/files/cygwin-custom"; Description: "{cm:Install2,Cygwin,astrometry.net}";
Filename: "{app}\AstroTortilla.exe"; Description: "{cm:LaunchProgram,AstroTortilla}"; Flags: nowait postinstall skipifsilent


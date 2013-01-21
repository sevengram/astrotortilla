; Script generated by the Inno Setup Script Wizard.
; SEE THE DOCUMENTATION FOR DETAILS ON CREATING INNO SETUP SCRIPT FILES!

#define AstroTortilla "AstroTortilla"
#define TortillaVersion GetFileVersion(AddBackslash(SourcePath) + "Dist\\AstroTortilla.exe")
; Auto-select based on which build was made (using buildXX.bat)
#include "current_build.iss"
; InnoTools Downloader 0.3.5 from
; http://www.sherlocksoftware.org/page.php?id=51
#include "it_download.iss"

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
AlwaysShowComponentsList=yes


[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "finnish"; MessagesFile: "compiler:Languages\Finnish.isl"

[CustomMessages]
Install2=Install %1 and %2
finnish.Install2=Asenna %1 ja %2
Installer=%1 setup
finnish.Installer=%1 asetukset
FullInstallation=Install {#AstroTortilla}, Cygwin, astrometry.net and indexes
finnish.FullInstallation=Asenna {#AstroTortilla}, Cygwin, astrometry.net ja indeksit
NoCygwin=Install {#AstroTortilla} only
finnish.NoCygwin=Asenna vain {#AstroTortilla}
NoIndexes=Install {#AstroTortilla}, Cygwin and astrometry.net without indexes
finnish.NoIndexes=Asenna {#AstroTortilla}, Cygwin ja astrometry.net ilman indeksej�
AstrometricIndexes=Astrometric index files
finnish.AstrometricIndexes=Astrometriset tietokannat
And=%1 and %2
finnish.And=%1 ja %2
CygPageTitle=Cygwin location
CygPageSubtitle=Select a directory where Cygwin and astrometry.net are to be installed
CygRootTip=Cygwin root folder
CygLocalDirectoryTip=Local Cygwin package cache (not within Cygwin root)
finnish.CygPageTitle=Cygwin asennus
finnish.CygPageSubtitle=Valitse Cygwin ja astrometry.net -asennuksen juurihakemisto
finnish.CygRootTip=Juurihakemisto
finnish.CygLocalDirectoryTip=Paikallinen Cygwin pakettihakemisto (ei Cygwin juuren alla)
IndexMirrorSelectionHelp=Select the upper and lower level for index files to download. Choose the levels based on the field of view of your setup. You can always come back to this selection later for fetching more index files. Read the User Guide for detailed instructions.
IndexOnlineSolver=Online plate-solver
IndexSelectTitle=Astrometric Index selection
IndexSelectSubtitle=Select which astrometric indexes you would like to download.
LblSelectMirror=Download indexes from
LblMirrorInternational=international server
LblMirrorFinland=from server in Finland
LblWideFov=Widest level (choose a size corresponding to your widest FOV)
LblNarrowFov=Narrowest level (choose a size corresponding to ca. 20% of your narrowest FOV)
finnish.IndexMirrorSelectionHelp=Valitse ladattavien indeksien yl�- ja alaraja laitteistosi n�k�kent�n perusteella. Voit palata asennusohjelmaan my�hemmin halutessasi ladata lis�� indeksej�. Tarkemmat ohjeet l�ytyv�t AstroTortillan k�ytt�ohjeesta.
finnish.IndexOnlineSolver=Online-ratkoja
finnish.IndexSelectTitle=Astrometristen indeksien valinta
finnish.IndexSelectSubtitle=Valitse ladattavat astrometriset indeksit.
finnish.LblSelectMirror=Lataa indeksit
finnish.LblMirrorInternational=Kansainv�liselt� palvelimelta
finnish.LblMirrorFinland=Suomen palvelimelta
finnish.LblWideFov=Laajin taso (valitse laajinta kuva-alaasi vastaava koko)
finnish.LblNarrowFov=Kapein taso (valitse n. 20%:a kapeimmasta kuva-alastasi vastaava koko)
ErrorIndexOrder=Please ensure the narrowest level is not wider than widest level.
finnish.ErrorIndexOrder=Tarkista ettei kapein taso laajinta tasoa laajempi.
UncompressTitle=Uncompressing index files
UncompressDescription=Setup is now uncompressing the downloaded astrometric index files...
finnish.UncompressTitle=Puretaan indeksej�
finnish.UncompressDescription=Puretaan ladattuja astrometrisi� indeksitiedostoja...
IndexesOnly=Install additional astrometric index files
CygwinAndIndexes=Update Cygwin, astrometry.net and install index files
finnish.IndexesOnly=Lis�� uusia astrometrisi� indeksej�
finnish.CygwinAndIndexes=P�ivit� Cygwin, astrometry.net ja asenna indeksej�

[Types]
Name: "full"; Description: "{cm:FullInstallation}"
Name: "noindexes"; Description: "{cm:NoIndexes}"
Name: "nocygwin"; Description: "{cm:NoCygwin}"
Name: "indexonly"; Description: "{cm:IndexesOnly}"
Name: "cygwinindex"; Description: "{cm:CygwinAndIndexes}"

[Components]
Name: "AstroTortilla"; Types: full nocygwin noindexes; Description: "AstroTortilla"; Flags: checkablealone
Name: "cygwin"; Types: full noindexes cygwinindex; Description: "{cm:And,Cygwin,astrometry.net}"; Flags: checkablealone
Name: "indexfiles"; Types: full indexonly cygwinindex; Description: "{cm:AstrometricIndexes}"; Flags: checkablealone

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
Source: {#VCRedist}; DestDir: {tmp}; Flags: ignoreversion deleteafterinstall
Source: "setup.exe"; DestDir: "{app}";


[Icons]
Name: "{group}\AstroTortilla"; Filename: "{app}\AstroTortilla.exe"
Name: "{group}\Getting started (English)"; Filename: "{app}\docs\Getting_Started_with_AstroTortilla.pdf"
Name: "{group}\User guide (English)"; Filename: "{app}\docs\AstroTortilla_user_guide.pdf"
Name: "{group}\Pikaopas (Finnish)"; Filename: "{app}\docs\AstroTortilla_pikaopas.pdf"
Name: "{group}\K�ytt�ohje (Finnish)"; Filename: "{app}\docs\AstroTortilla_kayttoohje.pdf"
Name: "{group}\{cm:UninstallProgram,AstroTortilla}"; Filename: "{uninstallexe}"
Name: "{group}\{cm:Installer,Cygwin}"; Filename: "{app}\setup.exe"; Parameters: "-P astrometry.net -K http://astrotortilla.comsix.fi/tortilla.gpg -s http://astrotortilla.comsix.fi  -R {code:CygwinRootDir|C:\cygwin\} -l {code:CygwinCacheDir|C:\temp\cygcache\}"
Name: "{commondesktop}\AstroTortilla"; Filename: "{app}\AstroTortilla.exe"; Tasks: desktopicon
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\AstroTortilla"; Filename: "{app}\AstroTortilla.exe"; Tasks: quicklaunchicon

[Run]
Filename: "{tmp}\{#VCRedist}"; WorkingDir: {tmp}; Flags: skipifdoesntexist; Check: VCRedistNeedsInstall; StatusMsg: "Checking for and installing ""Microsoft Visual C++ Redistributable Package"" if needed, This can take several minutes..."
Filename: "{app}\setup.exe"; Components: cygwin;Parameters: "-P astrometry.net -K http://astrotortilla.comsix.fi/tortilla.gpg -s http://astrotortilla.comsix.fi -O -q -R {code:CygwinRootDir|C:\cygwin\} -l {code:CygwinCacheDir|C:\temp\cygcache\}"; Description: "{cm:Install2,Cygwin,astrometry.net}"; AfterInstall: RebaseAndUncompress
Filename: "{app}\AstroTortilla.exe"; Description: "{cm:LaunchProgram,AstroTortilla}"; Flags: nowait postinstall skipifsilent

[INI]
Filename: "{localappdata}\astrotortilla.sf.net\AstroTortilla\AstroTortilla.cfg"; Section: "Solver-AstrometryNetSolver"; Key: "shell"; String: "{code:CygwinShell|C:\cygwin\}"

[Code]
#IFDEF UNICODE
  #DEFINE AW "W"
#ELSE
  #DEFINE AW "A"
#ENDIF

var
  CygDirPage: TInputDirWizardPage;
  CygDirPageId : Integer;
  IdxPage: TWizardPage;
  IdxPageId, IntlServerRadioBtn: Integer;
  ServerSelection : TNewCheckListBox; // Index downloading server selector
  NarrowFovCombo,WideFovCombo : TNewComboBox; // Index limits
  
type
  INSTALLSTATE = Longint;
const
  INSTALLSTATE_INVALIDARG = -2;  // An invalid parameter was passed to the function.
  INSTALLSTATE_UNKNOWN = -1;     // The product is neither advertised or installed.
  INSTALLSTATE_ADVERTISED = 1;   // The product is advertised but not installed.
  INSTALLSTATE_ABSENT = 2;       // The product is installed for a different user.
  INSTALLSTATE_DEFAULT = 5;      // The product is installed for the current user.

  VC_2005_REDIST_X86 = '{A49F249F-0C91-497F-86DF-B2585E8E76B7}';
  VC_2005_REDIST_X64 = '{6E8E85E8-CE4B-4FF5-91F7-04999C9FAE6A}';
  VC_2005_REDIST_IA64 = '{03ED71EA-F531-4927-AABD-1C31BCE8E187}';
  VC_2005_SP1_REDIST_X86 = '{7299052B-02A4-4627-81F2-1818DA5D550D}';
  VC_2005_SP1_REDIST_X64 = '{071C9B48-7C32-4621-A0AC-3F809523288F}';
  VC_2005_SP1_REDIST_IA64 = '{0F8FB34E-675E-42ED-850B-29D98C2ECE08}';
  VC_2005_SP1_ATL_SEC_UPD_REDIST_X86 = '{837B34E3-7C30-493C-8F6A-2B0F04E2912C}';
  VC_2005_SP1_ATL_SEC_UPD_REDIST_X64 = '{6CE5BAE9-D3CA-4B99-891A-1DC6C118A5FC}';
  VC_2005_SP1_ATL_SEC_UPD_REDIST_IA64 = '{85025851-A784-46D8-950D-05CB3CA43A13}';

  VC_2008_REDIST_X86 = '{FF66E9F6-83E7-3A3E-AF14-8DE9A809A6A4}';
  VC_2008_REDIST_X64 = '{350AA351-21FA-3270-8B7A-835434E766AD}';
  VC_2008_REDIST_IA64 = '{2B547B43-DB50-3139-9EBE-37D419E0F5FA}';
  VC_2008_SP1_REDIST_X86 = '{9A25302D-30C0-39D9-BD6F-21E6EC160475}';
  VC_2008_SP1_REDIST_X64 = '{8220EEFE-38CD-377E-8595-13398D740ACE}';
  VC_2008_SP1_REDIST_IA64 = '{5827ECE1-AEB0-328E-B813-6FC68622C1F9}';
  VC_2008_SP1_ATL_SEC_UPD_REDIST_X86 = '{1F1C2DFC-2D24-3E06-BCB8-725134ADF989}';
  VC_2008_SP1_ATL_SEC_UPD_REDIST_X64 = '{4B6C7001-C7D6-3710-913E-5BC23FCE91E6}';
  VC_2008_SP1_ATL_SEC_UPD_REDIST_IA64 = '{977AD349-C2A8-39DD-9273-285C08987C7B}';
  VC_2008_SP1_MFC_SEC_UPD_REDIST_X86 = '{9BE518E6-ECC6-35A9-88E4-87755C07200F}';
  VC_2008_SP1_MFC_SEC_UPD_REDIST_X64 = '{5FCE6D76-F5DC-37AB-B2B8-22AB8CEDB1D4}';
  VC_2008_SP1_MFC_SEC_UPD_REDIST_IA64 = '{515643D1-4E9E-342F-A75A-D1F16448DC04}';

  VC_2010_REDIST_X86 = '{196BB40D-1578-3D01-B289-BEFC77A11A1E}';
  VC_2010_REDIST_X64 = '{DA5E371C-6333-3D8A-93A4-6FD5B20BCC6E}';
  VC_2010_REDIST_IA64 = '{C1A35166-4301-38E9-BA67-02823AD72A1B}';
  VC_2010_SP1_REDIST_X86 = '{F0C3E5D1-1ADE-321E-8167-68EF0DE699A5}';
  VC_2010_SP1_REDIST_X64 = '{1D8E6291-B0D5-35EC-8441-6616F567A0F7}';
  VC_2010_SP1_REDIST_IA64 = '{88C73C1C-2DE5-3B01-AFB8-B46EF4AB41CD}';

function MsiQueryProductState(szProduct: string): INSTALLSTATE; 
  external 'MsiQueryProductState{#AW}@msi.dll stdcall';

function VCVersionInstalled(const ProductID: string): Boolean;
begin
  Result := MsiQueryProductState(ProductID) = INSTALLSTATE_DEFAULT;
end;

function VCRedistNeedsInstall: Boolean;
begin
  // here the Result must be True when you need to install your VCRedist
  // or False when you don't need to, so now it's upon you how you build
  // this statement, the following won't install your VC redist only when
  // the Visual C++ 2010 Redist (x86) and Visual C++ 2010 SP1 Redist(x86)
  // are installed for the current user
  if Is64BitInstallMode then
  begin
    Result := not (VCVersionInstalled(VC_2008_REDIST_X64));
  end
  else
  begin
    Result := not (VCVersionInstalled(VC_2008_REDIST_X86));
  end;
end;
procedure URLLabelOnClick(Sender: TObject);
var
  ErrorCode: Integer;
begin
  ShellExecAsOriginalUser('open', 'http://nova.astrometry.net/', '', '', SW_SHOWNORMAL, ewNoWait, ErrorCode);
end;

function PlaceBelow(const element:TControl; const pad:Integer):Integer;
begin
  Result := element.Top + element.ClientHeight + ScaleY(pad);
end;

function CreateIndexWizardPage(FollowsPage:integer) : TWizardPage;
var
  Page : TWizardPage;
  descMirror, URLLabel : TNewStaticText;
  LblWideFov, LblNarrowFov : TLabel;
  IndexList : TStringList;
begin
  // Setup index file selection form
  Page := CreateCustomPage(FollowsPage, CustomMessage('IndexSelectTitle'), CustomMessage('IndexSelectSubtitle'));
  descMirror := TNewStaticText.Create(Page);
  with descMirror do
  begin
    Parent := Page.Surface;                             
    Width := Page.SurfaceWidth;
    AutoSize := False;
    WordWrap := True;
    Caption := CustomMessage('IndexMirrorSelectionHelp');
  end;
  descMirror.AdjustHeight();
  ServerSelection := TNewCheckListBox.Create(Page);
  with ServerSelection do
  begin
    Top := PlaceBelow(descMirror, 0);
    Parent := Page.Surface;
    Width := Page.SurfaceWidth;
    Height := ScaleY(MinItemHeight*3);
    BorderStyle := bsNone;
    ParentColor := True;
    WantTabs := True;
    ShowLines := False;
    AddGroup(CustomMessage('LblSelectMirror'), '', 0, nil);
    IntlServerRadioBtn := AddRadioButton(CustomMessage('LblMirrorInternational'), '', 0, True, True, nil);
    AddRadioButton(CustomMessage('LblMirrorFinland'), '', 0, False, True, nil);
  end;
  IndexList := TStringList.Create();
  
  IndexList.Add('index 4000, 11GB, 2 to 2.8 arcmin');
  IndexList.Add('index 4001, 7GB, 2.8 to 4 arcmin');
  IndexList.Add('index 4002, 3.8GB, 4 to 5.6 arcmin');
  IndexList.Add('index 4003, 2GB, 5.6 to 8 arcmin');
  IndexList.Add('index 4004, 960MB, 8 to 11 arcmin');
  IndexList.Add('index 4005, 470MB, 11 to 16 arcmin');
  IndexList.Add('index 4006, 230MB, 16 to 22 arcmin');
  IndexList.Add('index 4007, 115MB, 22 to 30 arcmin');
  IndexList.Add('index 4008, 62MB, 0.5 to 0.7 deg (30 to 42 arcmin)');
  IndexList.Add('index 4009, 31MB, 0.7 to 1 deg (42 to 60 arcmin)');
  IndexList.Add('index 4010, 15MB, 1 to 1.42 deg (60 to 85 arcmin)');
  IndexList.Add('index 4011, 5.6MB, 1.42 to 2 deg (85 to 120 arcmin)');
  IndexList.Add('index 4012, 2.8MB, 2 to 2.83 deg (120 to 170 arcmin)');
  IndexList.Add('index 4013, 1.4MB, 2.83 to 4 deg (170 to 240 arcmin)');
  IndexList.Add('index 4014, 735KB, 4 to 5.67 deg');
  IndexList.Add('index 4015, 375KB, 5.67 to 8 deg');
  IndexList.Add('index 4016, 185KB, 8 to 11.3 deg');
  IndexList.Add('index 4017, 96KB, 11.3 to 16.7 deg');
  IndexList.Add('index 4018, 63KB, 16.7 to 23.3 deg');
  IndexList.Add('index 4019, 38KB, 23.3 to 33.3 deg');

  LblNarrowFov := TLabel.Create(Page);
  with LblNarrowFov do
  begin
    Parent := Page.Surface;
    Top := PlaceBelow(ServerSelection, 8);
    Caption := CustomMessage('LblNarrowFov')
  end;

  NarrowFovCombo := TNewComboBox.Create(Page);
  with NarrowFovCombo do
  begin
    Parent := Page.Surface;
    Top := PlaceBelow(LblNarrowFov, 0);
    Style := csDropDown;
    Items := IndexList;
    Left := ScaleX(16);
    Width := Page.SurfaceWidth - ScaleX(16);
    ItemIndex := 14;
  end;

  LblWideFov := TLabel.Create(Page);
  with LblWideFov do
  begin
    Parent := Page.Surface;
    Top := PlaceBelow(NarrowFovCombo, 8);
    Caption := CustomMessage('LblWideFov')
  end;

  WideFovCombo := TNewComboBox.Create(Page);
  with WideFovCombo do
  begin
    Parent := Page.Surface;
    Top := PlaceBelow(LblWideFov, 0);
    Style := csDropDown;
    Items := IndexList;
    Left := ScaleX(16);
    Width := Page.SurfaceWidth - ScaleX(16);
    ItemIndex := 19;
  end;

  URLLabel := TNewStaticText.Create(Page);
  with URLLabel do
  begin
    Parent := Page.Surface;
    Caption := CustomMessage('IndexOnlineSolver') + ' http://nova.astrometry.net/';
    Top := PlaceBelow(WideFovCombo, 32);
    Cursor := crHand;
    OnClick := @URLLabelOnClick;
    { Alter Font *after* setting Parent so the correct defaults are inherited first }
    Font.Style := URLLabel.Font.Style + [fsUnderline];
    Font.Color := clBlue;
  end;

  Result := Page;
end;

procedure InitializeWizard;
begin
  // Setup Cygwin root directory query page
  CygDirPage := CreateInputDirPage(wpSelectComponents,
    CustomMessage('CygPageTitle'),
    CustomMessage('CygPageSubtitle'),
    '',
    False,
    '');
  CygDirPage.Add(CustomMessage('CygRootTip'));
  CygDirPage.Values[0] := 'C:\cygwin\';
  CygDirPage.Add(CustomMessage('CygLocalDirectoryTip'));
  CygDirPage.Values[1] := 'C:\temp\cygcache\';
  CygDirPageId := CygDirPage.ID;

  IdxPage := CreateIndexWizardPage(CygDirPageId);
  IdxPageId := IdxPage.ID;


  // Setup index file downloader
  ITD_Init();
  ITD_DownloadAfter(wpReady);
  ITD_SetOption('UI_DetailedMode', '1');
  ITD_SetOption('UI_AllowContinue', '1');

end;

function ShouldSkipPage(PageID: Integer): Boolean;
begin
  Result := false;
  if PageID = CygDirPageId then
    Result := not IsComponentSelected('cygwin');
  if PageID = IdxPageId then
    Result := not IsComponentSelected('indexfiles');
end;

function CygwinCacheDir(Param:string):string;
var
  cygCache : String;
begin
  cygCache := CygDirPage.Values[1];
  if cygCache = '' then
    cygCache := Param;
   Result := AddBackslash(cygCache);

end;

function CygwinRootDir(Param: string):string;
var
  cygPath : String;
begin
  cygPath := CygDirPage.Values[0];
  if cygPath = '' then
    cygPath := Param;
   Result := AddBackslash(cygPath);
end;

function CygwinShell(Param: string):string;
begin
  Result := AddBackslash(CygwinRootDir(Param)) + 'bin\bash.exe --login -c "%%s"';
end;

procedure AddIndexToDownload(Index:Integer; UseIntlServer:Boolean);
var
  indexCount, i : Integer;
  uriBase, targetDir, targetFile : String;

begin
  case Index of
    5..7:
    indexCount := 11;
    0..4:
    indexCount := 47;
  else
    indexCount := 0;
  end;
  if UseIntlServer then
    uriBase := 'http://broiler.astrometry.net/~dstn/4000/'
  else
    uriBase := 'http://astrotortilla.comsix.fi/indices/';
  targetDir := AddBackslash(CygwinRootDir('C:\cygwin\')) + 'usr\share\astrometry\data\';
  if indexCount = 0 then
    begin
    targetFile := Format('index-40%.2d.fits', [Index]);
    if not (FileExists(targetDir + targetFile) or FileExists(targetDir + targetFile + '.bz2')) then
      begin
      Log(targetFile);
      ITD_AddFile(uriBase + targetFile + '.bz2', targetDir + targetFile + '.bz2');
      end;
    end
  else
    begin
      for i := 0 to indexCount do
        begin
        targetFile := Format('index-40%.2d-%.2d.fits', [Index, i]);
        if not (FileExists(targetDir + targetFile) or FileExists(targetDir + targetFile + '.bz2')) then
          begin
          Log(targetFile);
          ITD_AddFile(uriBase + targetFile + '.bz2', targetDir + targetFile + '.bz2');
          end;
        end;
    end;
end;

function NextButtonClick(CurPageID: Integer): Boolean;
var
  curIndex : Integer;
  indexDir : String;
begin
  if CurPageID = IdxPageId then
    begin
    if NarrowFovCombo.ItemIndex > WideFovCombo.ItemIndex then
      begin
      Result := False;
      MsgBox(CustomMessage('ErrorIndexOrder'), mbError, MB_OK);
      end
    else
      begin
      Result := True;
      indexDir := AddBackslash(CygwinRootDir('C:\cygwin\')) + 'usr\share\astrometry\data\';
      Log('Adding download strings');
      Log(Format('WideFov %d, NarrowFov %d', [WideFovCombo.ItemIndex, NarrowFovCombo.ItemIndex]));
      ForceDirectories(indexDir);
      for curIndex := WideFovCombo.ItemIndex downto NarrowFovCombo.ItemIndex do
        begin
        AddIndexToDownload(curIndex, ServerSelection.State[IntlServerRadioBtn]);
        end;
      end;
    end
  else
    Result := True;
end;

procedure RebaseAndUncompress();
var
  targets, bunzip, rebase: String;
  ResultCode : Integer;
  Progress : TOutputProgressWizardPage;
begin;
  Progress := CreateOutputProgressPage(CustomMessage('UncompressTitle'), CustomMessage('UncompressDescription'));
  with Progress.ProgressBar do
  begin
    State := npbsNormal;
    Style := npbstMarquee;
    Visible := True;
  end;
  Progress.Show();
  try
    Log('Running rebase all just in case');
    rebase := AddBackslash(CygwinRootDir('C:\cygwin\')) + 'bin\ash.exe';
    ShellExec('', rebase, '/bin/rebaseall', '',SW_HIDE,ewWaitUntilTerminated,ResultCode);
    Log('Uncompressing astrometric indexes');
    targets :=  '/usr/share/astrometry/data/*.bz2';
    bunzip :=    AddBackslash(CygwinRootDir('C:\cygwin\')) + 'bin\bunzip2.exe';
    ShellExec('', bunzip, targets, '',SW_HIDE,ewWaitUntilTerminated,ResultCode);

  finally
    Progress.Hide;
  end;
end;

procedure DeinitializeSetup();
var
  IndexDir: String;
  FindRec: TFindRec;
begin
    IndexDir := AddBackslash(CygwinRootDir('C:\cygwin\')) + 'usr\share\astrometry\data\';
    if FindFirst(IndexDir+'\*.bz2', FindRec) then begin
    try
      repeat
        // delete all bz2-files, ignore directories just to be safe
        Log('Removing temporary file ' + FindRec.Name);
        DeleteFile(IndexDir + FindRec.Name);
      until not FindNext(FindRec);
    finally
      FindClose(FindRec);
    end;
  end;
end;

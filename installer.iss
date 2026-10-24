; Inno Setup script. Build: iscc /DAppVersion=0.1.0 installer.iss  (after build_exe.ps1)
#ifndef AppVersion
  #define AppVersion "0.1.0"
#endif

[Setup]
AppId={{6C1B2B7A-3E5D-4B79-9D0A-5A2B7B8C4F11}
AppName=Zuoya GMK67 Control
AppVersion={#AppVersion}
AppPublisher=Zuoya GMK67 Control contributors
DefaultDirName={autopf}\GMK67Control
DefaultGroupName=Zuoya GMK67 Control
DisableProgramGroupPage=yes
OutputDir=installer
OutputBaseFilename=GMK67Control-Setup
SetupIconFile=gmk67\icon.ico
UninstallDisplayIcon={app}\GMK67Control.exe
Compression=lzma2
SolidCompression=yes
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
LicenseFile=LICENSE
WizardStyle=modern

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "brazilianportuguese"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; Flags: unchecked
Name: "autostart"; Description: "Start with Windows"; Flags: unchecked

[Files]
Source: "dist\GMK67Control.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{autoprograms}\Zuoya GMK67 Control"; Filename: "{app}\GMK67Control.exe"
Name: "{autodesktop}\Zuoya GMK67 Control"; Filename: "{app}\GMK67Control.exe"; Tasks: desktopicon

[Registry]
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; ValueType: string; ValueName: "GMK67Control"; ValueData: """{app}\GMK67Control.exe"" --minimized"; Flags: uninsdeletevalue; Tasks: autostart

[Run]
Filename: "{app}\GMK67Control.exe"; Description: "{cm:LaunchProgram,Zuoya GMK67 Control}"; Flags: nowait postinstall skipifsilent

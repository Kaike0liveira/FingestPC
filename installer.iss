[Setup]
AppName=Fingest
AppVersion=1.0
DefaultDirName={pf}\Fingest
DefaultGroupName=Fingest
OutputBaseFilename=Fingest_Installer
Compression=lzma
SolidCompression=yes

[Files]
Source: "dist\run_app.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "README_ANDROID.md"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\Fingest"; Filename: "{app}\run_app.exe"
Name: "{userdesktop}\Fingest"; Filename: "{app}\run_app.exe"; Tasks: desktopicon

[Tasks]
Name: desktopicon; Description: "Create a &desktop icon"; GroupDescription: "Additional icons:"; Flags: unchecked

[Run]
Filename: "{app}\run_app.exe"; Description: "Start Fingest"; Flags: nowait postinstall skipifsilent

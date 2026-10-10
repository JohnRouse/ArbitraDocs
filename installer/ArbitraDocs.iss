#define MyAppName "ArbitraDocs"
#define MyAppVersion "0.2.0-beta"
#define MyAppPublisher "ArbitraDocs"
#define MyAppExeName "ArbitraDocs.exe"

[Setup]
AppId={{BBD03254-58B7-4D6F-A0AA-60B85EE17391}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={localappdata}\Programs\ArbitraDocs
DefaultGroupName=ArbitraDocs
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
OutputDir=..\artifacts\installer
OutputBaseFilename=ArbitraDocs_Setup_Beta
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
UninstallDisplayIcon={app}\{#MyAppExeName}
SetupLogging=yes

[Files]
Source: "..\artifacts\publish\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "..\artifacts\engine\ArbitraDocs.Engine.exe"; DestDir: "{app}\Engine"; Flags: ignoreversion

[Icons]
Name: "{autoprograms}\ArbitraDocs"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\ArbitraDocs"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Crear un acceso directo en el escritorio"; GroupDescription: "Accesos directos:"; Flags: unchecked

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Abrir ArbitraDocs"; Flags: nowait postinstall skipifsilent

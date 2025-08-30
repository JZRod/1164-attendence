; ----------------------------
; Attendance System Installer
; ----------------------------
[Setup]
AppName=Attendance System
AppVersion=1.0
DefaultDirName={autopf}\AttendanceSystem
DefaultGroupName=Attendance System
UninstallDisplayIcon={app}\1164-attendance-program.exe
OutputBaseFilename=AttendanceInstaller
Compression=lzma
SolidCompression=yes
WizardStyle=modern

; ----------------------------
; Files
; ----------------------------
[Files]
; Main executable
Source: "dist\1164-attendance-program.exe"; DestDir: "{app}"; Flags: ignoreversion

; Assets (logo, gear, icon)
Source: "assets\*"; DestDir: "{app}\assets"; Flags: ignoreversion recursesubdirs createallsubdirs

; Data folder (installed to Documents for persistence)
Source: "data\*"; DestDir: "{userdocs}\AttendanceSystemData"; Flags: onlyifdoesntexist recursesubdirs createallsubdirs

; ----------------------------
; Shortcuts
; ----------------------------
[Icons]
; Start Menu shortcut
Name: "{group}\Attendance System"; Filename: "{app}\1164-attendance-program.exe"; WorkingDir: "{app}"; IconFilename: "{app}\assets\icon.ico"

; Desktop shortcut
Name: "{commondesktop}\Attendance System"; Filename: "{app}\1164-attendance-program.exe"; WorkingDir: "{app}"; IconFilename: "{app}\assets\icon.ico"

; ----------------------------
; Run After Install
; ----------------------------
[Run]
Filename: "{app}\1164-attendance-program.exe"; Description: "Launch Attendance System"; Flags: nowait postinstall skipifsilent

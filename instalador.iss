; Instalador de Groundfeel (Inno Setup 6). Lo compila el workflow de release:
;   ISCC /DVersion=1.1.0 instalador.iss   ->  dist\VibracionURSA-Setup.exe
; Instala por usuario (sin administrador) en %LOCALAPPDATA%\Programs\VibracionURSA.

#ifndef Version
  #define Version "0.0.0"
#endif

[Setup]
AppId={{6C1E2D7A-5B4F-4E8B-9C3A-2F7D1E0B8A41}
AppName=Groundfeel
AppVersion={#Version}
AppVerName=Groundfeel {#Version}
AppPublisher=agustin320
AppPublisherURL=https://github.com/agustin320/vibracion-ursa
AppSupportURL=https://github.com/agustin320/vibracion-ursa/issues
AppUpdatesURL=https://github.com/agustin320/vibracion-ursa/releases
VersionInfoVersion={#Version}
VersionInfoProductName=Groundfeel
VersionInfoDescription=Groundfeel installer
PrivilegesRequired=lowest
DefaultDirName={localappdata}\Programs\VibracionURSA
DisableDirPage=yes
DefaultGroupName=Groundfeel
DisableProgramGroupPage=yes
OutputDir=dist
OutputBaseFilename=VibracionURSA-Setup
SetupIconFile=recursos\icono.ico
UninstallDisplayIcon={app}\VibracionURSA.exe
UninstallDisplayName=Groundfeel
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
LicenseFile=LICENSE
; Reason: la app la cierra el propio instalador (ver [Code]); el Restart Manager la mataría sin apagar motores.
CloseApplications=no

[Languages]
Name: "en"; MessagesFile: "compiler:Default.isl"
Name: "es"; MessagesFile: "compiler:Languages\Spanish.isl"

[CustomMessages]
en.Autostart=Start with Windows (recommended: it waits in the tray until the simulator opens)
es.Autostart=Iniciar con Windows (recomendado: espera en la bandeja hasta que abras el simulador)
en.Privacy=Privacy: the only internet connection is checking for and downloading updates from GitHub. No personal data is sent. It can be turned off in Settings.
es.Privacy=Privacidad: la única conexión a internet es buscar y bajar actualizaciones desde GitHub. No se envía ningún dato personal. Se puede desactivar en Ajustes.
en.SimAppPro=Remember to turn off SimAppPro's vibration for the joystick and the throttle.
es.SimAppPro=Acordate de apagar la vibración de SimAppPro para el joystick y el throttle.
en.Launch=Open Groundfeel now
es.Launch=Abrir Groundfeel ahora

[Tasks]
Name: "autostart"; Description: "{cm:Autostart}"

[Files]
Source: "dist\VibracionURSA\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "LICENSE"; DestDir: "{app}"; DestName: "LICENSE.txt"
Source: "THIRD-PARTY-NOTICES.txt"; DestDir: "{app}"

[InstallDelete]
; Reason: hasta la 1.5.1 el acceso directo se llamaba "URSA Rumble"; al actualizar quedaba duplicado.
Type: files; Name: "{userprograms}\URSA Rumble.lnk"

[Icons]
Name: "{userprograms}\Groundfeel"; Filename: "{app}\VibracionURSA.exe"

[Registry]
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; ValueType: string; ValueName: "VibracionURSA"; ValueData: """{app}\VibracionURSA.exe"""; Tasks: autostart; Flags: uninsdeletevalue

[Run]
Filename: "{app}\VibracionURSA.exe"; Description: "{cm:Launch}"; Flags: nowait postinstall skipifsilent
; Actualización automática (silenciosa): volver a abrir la app sola.
Filename: "{app}\VibracionURSA.exe"; Flags: nowait; Check: WizardSilent

[Code]
const
  MUTEX_APP = 'Global\vibracion_ursa_unica';
  EVENTO_SALIR = 'Local\vibracion_ursa_salir';   { mismo nombre que instancia.py }
  EVENT_MODIFY_STATE = $0002;

function OpenEvent(Acceso: Cardinal; Heredar: Boolean; Nombre: String): THandle;
  external 'OpenEventW@kernel32.dll stdcall';
function SetEvent(Evento: THandle): Boolean;
  external 'SetEvent@kernel32.dll stdcall';
function CloseHandle(Objeto: THandle): Boolean;
  external 'CloseHandle@kernel32.dll stdcall';

{ Pide a la app en marcha (esté donde esté) que cierre apagando los motores, y espera hasta 15 s. }
procedure CerrarApp();
var
  Evento: THandle;
  i: Integer;
begin
  if not CheckForMutexes(MUTEX_APP) then
    exit;
  Evento := OpenEvent(EVENT_MODIFY_STATE, False, EVENTO_SALIR);
  if Evento <> 0 then
  begin
    SetEvent(Evento);
    CloseHandle(Evento);
  end;
  for i := 1 to 50 do
  begin
    if not CheckForMutexes(MUTEX_APP) then
      exit;
    Sleep(300);
  end;
end;

function InitializeSetup(): Boolean;
begin
  CerrarApp();
  Result := True;
end;

function InitializeUninstall(): Boolean;
begin
  CerrarApp();
  Result := True;
end;

// Reason: "Iniciar con Windows" también se puede prender desde Ajustes, y ahí no lo registra el instalador:
// se borra siempre al desinstalar. (No hay [UninstallDelete] de la carpeta: Inno borra lo que instaló y
// borrar la carpeta entera sería peligroso si alguien instaló con /DIR= en una carpeta con otras cosas.)
procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
begin
  if CurUninstallStep = usUninstall then
    RegDeleteValue(HKEY_CURRENT_USER, 'Software\Microsoft\Windows\CurrentVersion\Run', 'VibracionURSA');
end;

procedure CurPageChanged(CurPageID: Integer);
begin
  if CurPageID = wpFinished then
    WizardForm.FinishedLabel.Caption := WizardForm.FinishedLabel.Caption + #13#10#13#10 +
      CustomMessage('Privacy') + #13#10#13#10 + CustomMessage('SimAppPro');
end;

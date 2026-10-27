"""Instalación por usuario (sin permisos de administrador), como Navigraph Simlink.

Al abrir el .exe descargado desde cualquier carpeta, se copia a %LOCALAPPDATA%\\Programs\\VibracionURSA, crea el acceso
directo en el menú Inicio, se registra para arrancar con Windows y en "Aplicaciones instaladas", y se relanza desde
ahí. Todo vive en HKCU: no toca el sistema ni otros usuarios.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
import winreg
from pathlib import Path

import rutas
from version import NOMBRE_APP, __version__

CLAVE_RUN = r"Software\Microsoft\Windows\CurrentVersion\Run"
CLAVE_DESINSTALAR = rf"Software\Microsoft\Windows\CurrentVersion\Uninstall\{NOMBRE_APP}"
NOMBRE_VISIBLE = "Vibración URSA"
SIN_VENTANA = 0x08000000   # CREATE_NO_WINDOW


def acceso_directo() -> Path:
    return (Path(os.environ["APPDATA"]) / "Microsoft" / "Windows" / "Start Menu" / "Programs"
            / f"{NOMBRE_VISIBLE}.lnk")


def esta_instalado_aca() -> bool:
    """True si este proceso corre desde la carpeta de instalación (o desde el código fuente)."""
    if not rutas.EMPAQUETADO:
        return True
    return Path(sys.executable).resolve().parent == rutas.carpeta_instalacion().resolve()


# ------------------------------------------------------------------ arranque con Windows
def arranca_con_windows() -> bool:
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, CLAVE_RUN) as k:
            winreg.QueryValueEx(k, NOMBRE_APP)
            return True
    except OSError:
        return False


def poner_arranque_con_windows(si: bool) -> None:
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, CLAVE_RUN, 0, winreg.KEY_SET_VALUE) as k:
        if si:
            winreg.SetValueEx(k, NOMBRE_APP, 0, winreg.REG_SZ, f'"{rutas.exe_instalado()}"')
        else:
            try:
                winreg.DeleteValue(k, NOMBRE_APP)
            except FileNotFoundError:
                pass


# ------------------------------------------------------------------ instalar / desinstalar
def _crear_acceso_directo(destino: Path) -> None:
    ps = ("$s=(New-Object -ComObject WScript.Shell).CreateShortcut($env:LNK);"
          "$s.TargetPath=$env:DESTINO;$s.WorkingDirectory=(Split-Path $env:DESTINO);$s.Save()")
    env = dict(os.environ, LNK=str(acceso_directo()), DESTINO=str(destino))
    subprocess.run(["powershell", "-NoProfile", "-NonInteractive", "-Command", ps], env=env,
                   creationflags=SIN_VENTANA, check=False, timeout=30)


def registrar_desinstalador() -> None:
    exe = rutas.exe_instalado()
    with winreg.CreateKey(winreg.HKEY_CURRENT_USER, CLAVE_DESINSTALAR) as k:
        for nombre, valor in (("DisplayName", NOMBRE_VISIBLE), ("DisplayVersion", __version__),
                              ("Publisher", "agustin320"), ("DisplayIcon", str(exe)),
                              ("InstallLocation", str(exe.parent)),
                              ("UninstallString", f'"{exe}" --desinstalar')):
            winreg.SetValueEx(k, nombre, 0, winreg.REG_SZ, valor)
        winreg.SetValueEx(k, "NoModify", 0, winreg.REG_DWORD, 1)
        winreg.SetValueEx(k, "NoRepair", 0, winreg.REG_DWORD, 1)


def instalar() -> Path:
    """Copia el .exe actual a la carpeta de instalación y registra todo. Devuelve el exe instalado."""
    destino = rutas.exe_instalado()
    destino.parent.mkdir(parents=True, exist_ok=True)
    if Path(sys.executable).resolve() != destino.resolve():
        shutil.copy2(sys.executable, destino)
    _crear_acceso_directo(destino)
    poner_arranque_con_windows(True)
    registrar_desinstalador()
    return destino


def desinstalar() -> None:
    """Saca el arranque, el acceso directo y la entrada de Aplicaciones; borra la carpeta al salir el proceso.

    Los ajustes del usuario (%APPDATA%\\VibracionURSA) se conservan por si reinstala.
    """
    poner_arranque_con_windows(False)
    for p in (acceso_directo(),):
        p.unlink(missing_ok=True)
    try:
        winreg.DeleteKey(winreg.HKEY_CURRENT_USER, CLAVE_DESINSTALAR)
    except FileNotFoundError:
        pass
    carpeta = rutas.carpeta_instalacion()
    if carpeta.is_dir():
        # Reason: un .exe en uso no se puede borrar a sí mismo; cmd espera unos segundos y borra la carpeta.
        subprocess.Popen(f'cmd /c timeout /t 3 /nobreak >nul & rmdir /s /q "{carpeta}"',
                         creationflags=SIN_VENTANA, close_fds=True)

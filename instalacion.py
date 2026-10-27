"""Integración con Windows de la versión instalada (el instalador es Inno Setup: instalador.iss).

La instalación, el acceso directo, la entrada en "Aplicaciones instaladas" y la desinstalación los hace el instalador
estándar. Reason: la primera versión se instalaba sola (se copiaba, se registraba y se relanzaba) y los antivirus con
análisis de comportamiento (Kaspersky "Vigía proactiva") la mataban como troyano genérico: es exactamente lo que hace
un dropper. Un instalador conocido no dispara esa heurística.
"""
from __future__ import annotations

import subprocess
import winreg

import rutas
from version import NOMBRE_APP

CLAVE_RUN = r"Software\Microsoft\Windows\CurrentVersion\Run"


def arranca_con_windows() -> bool:
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, CLAVE_RUN) as k:
            winreg.QueryValueEx(k, NOMBRE_APP)
            return True
    except OSError:
        return False


def poner_arranque_con_windows(si: bool) -> None:
    """Mismo valor que crea el instalador (tarea "Iniciar con Windows"), así el desinstalador lo borra igual."""
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, CLAVE_RUN, 0, winreg.KEY_SET_VALUE) as k:
        if si:
            winreg.SetValueEx(k, NOMBRE_APP, 0, winreg.REG_SZ, f'"{rutas.exe_instalado()}"')
        else:
            try:
                winreg.DeleteValue(k, NOMBRE_APP)
            except FileNotFoundError:
                pass


def desinstalador() -> rutas.Path | None:
    exe = rutas.carpeta_instalacion() / "unins000.exe"
    return exe if exe.is_file() else None


def abrir_desinstalador() -> bool:
    """Lanza el desinstalador de Inno Setup (él cierra la app pidiéndole --salir). False si no está instalada."""
    exe = desinstalador()
    if exe is None:
        return False
    subprocess.Popen([str(exe)], close_fds=True)
    return True

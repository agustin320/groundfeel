"""Dónde vive cada cosa, tanto corriendo desde el código fuente como empaquetado (.exe de PyInstaller).

- Recursos de solo lectura (config por defecto, SimConnect.dll, ícono): junto al código, o dentro del .exe.
- Datos del usuario (ajustes.json con lo que cambió respecto de config.json, vibracion.log): %APPDATA%\\VibracionURSA
  cuando está empaquetado; la carpeta del código cuando corre desde el fuente (así el desarrollo no toca la
  instalación). Las actualizaciones traen un config.json nuevo y los ajustes del usuario se respetan encima.
- Instalación del .exe: %LOCALAPPDATA%\\Programs\\VibracionURSA.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

from version import NOMBRE_APP

EMPAQUETADO = bool(getattr(sys, "frozen", False))
FUENTE = Path(__file__).resolve().parent
RECURSOS = Path(getattr(sys, "_MEIPASS", FUENTE))


def datos_usuario() -> Path:
    if not EMPAQUETADO:
        return FUENTE
    d = Path(os.environ.get("APPDATA", Path.home())) / NOMBRE_APP
    d.mkdir(parents=True, exist_ok=True)
    return d


def carpeta_instalacion() -> Path:
    return Path(os.environ.get("LOCALAPPDATA", Path.home())) / "Programs" / NOMBRE_APP


def exe_instalado() -> Path:
    return carpeta_instalacion() / f"{NOMBRE_APP}.exe"


def config_por_defecto() -> Path:
    return RECURSOS / "config.json"


def ajustes_usuario() -> Path:
    return datos_usuario() / "ajustes.json"


def dll_simconnect_candidatas() -> list[Path]:
    """SimConnect.dll: la que viene empaquetada, la del repo o una copiada a mano junto al código."""
    env = os.environ.get("SIMCONNECT_DLL")
    out = [Path(env)] if env else []
    out += [RECURSOS / "SimConnect.dll", FUENTE / "recursos" / "SimConnect.dll", FUENTE / "SimConnect.dll",
            Path(r"C:\MSFS 2024 SDK\SimConnect SDK\lib\SimConnect.dll")]
    return out


def icono() -> Path:
    return RECURSOS / "recursos" / "icono.ico" if not EMPAQUETADO else RECURSOS / "icono.ico"


def archivo_log() -> Path:
    return datos_usuario() / "vibracion.log"

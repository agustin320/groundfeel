"""Actualizaciones desde GitHub Releases: compara versiones, baja el .exe nuevo y lo reemplaza en caliente.

Windows no deja borrar un .exe en uso, pero sí renombrarlo: el actual pasa a .old, el nuevo ocupa su lugar y se
relanza con --esperar (espera a que este proceso suelte la instancia única). Al arrancar, el nuevo borra el .old.
"""
from __future__ import annotations

import json
import logging
import subprocess
import sys
import urllib.request
from dataclasses import dataclass
from pathlib import Path

import rutas
from version import NOMBRE_APP, REPO, __version__

log = logging.getLogger("vibracion")
API = f"https://api.github.com/repos/{REPO}/releases/latest"
ASSET = f"{NOMBRE_APP}.exe"


@dataclass
class Version:
    numero: str
    url_exe: str
    notas: str


def _tupla(v: str) -> tuple[int, ...]:
    partes = []
    for p in v.lstrip("vV").split("."):
        num = "".join(ch for ch in p if ch.isdigit())
        partes.append(int(num) if num else 0)
    return tuple(partes)


def es_mas_nueva(remota: str, local: str = __version__) -> bool:
    return _tupla(remota) > _tupla(local)


def buscar() -> Version | None:
    """Última versión publicada si es más nueva que la instalada; None si no hay o no se pudo consultar."""
    req = urllib.request.Request(API, headers={"Accept": "application/vnd.github+json",
                                               "User-Agent": f"{NOMBRE_APP}/{__version__}"})
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            datos = json.load(r)
    except Exception as ex:  # noqa: BLE001  (sin internet, límite de la API, etc.: se reintenta más tarde)
        log.info("no pude consultar actualizaciones: %s", ex)
        return None
    tag = datos.get("tag_name", "")
    url = next((a["browser_download_url"] for a in datos.get("assets", []) if a.get("name") == ASSET), "")
    if not tag or not url or not es_mas_nueva(tag):
        return None
    return Version(tag.lstrip("vV"), url, datos.get("body", ""))


def limpiar_restos() -> None:
    """Borra el .exe viejo que dejó una actualización anterior."""
    viejo = rutas.exe_instalado().with_suffix(".old")
    try:
        viejo.unlink(missing_ok=True)
    except OSError:
        pass


def aplicar(v: Version) -> bool:
    """Baja e instala la versión nueva y relanza el programa. True si quedó todo listo para salir."""
    exe = rutas.exe_instalado()
    if not rutas.EMPAQUETADO or Path(sys.executable).resolve() != exe.resolve():
        log.info("actualización %s disponible, pero sólo se aplica en la versión instalada", v.numero)
        return False
    nuevo, viejo = exe.with_suffix(".new"), exe.with_suffix(".old")
    try:
        log.info("bajando la versión %s", v.numero)
        req = urllib.request.Request(v.url_exe, headers={"User-Agent": f"{NOMBRE_APP}/{__version__}"})
        with urllib.request.urlopen(req, timeout=120) as r, open(nuevo, "wb") as f:
            while bloque := r.read(1 << 16):
                f.write(bloque)
        if nuevo.stat().st_size < 1_000_000:
            raise ValueError("el archivo bajado es demasiado chico")
        viejo.unlink(missing_ok=True)
        exe.rename(viejo)
        nuevo.rename(exe)
    except Exception as ex:  # noqa: BLE001
        log.warning("no pude actualizar: %s", ex)
        nuevo.unlink(missing_ok=True)
        if viejo.exists() and not exe.exists():
            viejo.rename(exe)
        return False
    subprocess.Popen([str(exe), "--esperar"], close_fds=True)
    log.info("actualizado a %s, reiniciando", v.numero)
    return True

"""Actualizaciones desde GitHub Releases: compara versiones, baja el instalador nuevo y lo corre en silencio.

Flujo: baja VibracionURSA-Setup.exe, verifica su SHA-256 contra el que publica GitHub, lo lanza con /VERYSILENT y
esta app se cierra (apagando los motores). El instalador espera a que se cierre, reemplaza los archivos y vuelve a
abrir la app. Es el mismo instalador que usa una persona a mano: nada de reemplazar .exe en caliente.
"""
from __future__ import annotations

import hashlib
import json
import logging
import os
import subprocess
import tempfile
import urllib.request
from dataclasses import dataclass
from pathlib import Path

import rutas
from version import NOMBRE_APP, REPO, __version__

log = logging.getLogger("vibracion")
API = f"https://api.github.com/repos/{REPO}/releases/latest"
ASSET = f"{NOMBRE_APP}-Setup.exe"


@dataclass
class Version:
    numero: str
    url: str
    sha256: str
    notas: str


def _tupla(v: str) -> tuple[int, ...]:
    partes = []
    for p in v.lstrip("vV").split("."):
        num = "".join(ch for ch in p if ch.isdigit())
        partes.append(int(num) if num else 0)
    return tuple(partes)


def es_mas_nueva(remota: str, local: str = __version__) -> bool:
    return _tupla(remota) > _tupla(local)


def _pedir(url: str, timeout: int) -> urllib.request.addinfourl:
    req = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json",
                                               "User-Agent": f"{NOMBRE_APP}/{__version__}"})
    return urllib.request.urlopen(req, timeout=timeout)


def buscar() -> Version | None:
    """Última versión publicada si es más nueva que la instalada; None si no hay o no se pudo consultar."""
    try:
        with _pedir(API, 15) as r:
            datos = json.load(r)
    except Exception as ex:  # noqa: BLE001  (sin internet, límite de la API, etc.: se reintenta más tarde)
        log.info("no pude consultar actualizaciones: %s", ex)
        return None
    tag = datos.get("tag_name", "")
    asset = next((a for a in datos.get("assets", []) if a.get("name") == ASSET), None)
    if not tag or not asset or not es_mas_nueva(tag):
        return None
    sha = str(asset.get("digest", "")).removeprefix("sha256:")
    return Version(tag.lstrip("vV"), asset["browser_download_url"], sha, datos.get("body", ""))


def aplicar(v: Version) -> bool:
    """Baja el instalador, lo verifica y lo lanza. True si quedó corriendo (la app tiene que cerrarse ya)."""
    if not rutas.EMPAQUETADO:
        log.info("actualización %s disponible; desde el código fuente no se aplica", v.numero)
        return False
    destino = Path(tempfile.gettempdir()) / f"{NOMBRE_APP}-Setup-{v.numero}.exe"
    try:
        log.info("bajando la versión %s", v.numero)
        h = hashlib.sha256()
        with _pedir(v.url, 120) as r, open(destino, "wb") as f:
            while bloque := r.read(1 << 16):
                f.write(bloque)
                h.update(bloque)
        if v.sha256 and h.hexdigest() != v.sha256.lower():
            raise ValueError("el instalador bajado no coincide con el publicado (SHA-256)")
    except Exception as ex:  # noqa: BLE001
        log.warning("no pude actualizar: %s", ex)
        destino.unlink(missing_ok=True)
        return False
    subprocess.Popen([str(destino), "/VERYSILENT", "/SUPPRESSMSGBOXES", "/NORESTART"], close_fds=True,
                     cwd=os.environ.get("TEMP"))
    log.info("instalando la versión %s; la app se reinicia sola", v.numero)
    return True

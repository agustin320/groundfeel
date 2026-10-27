"""Actualizaciones desde GitHub Releases: compara versiones, baja el instalador nuevo y lo corre en silencio.

Flujo: baja VibracionURSA-Update.exe (o -Setup.exe) sólo desde los releases de este repo, exige que GitHub publique su
SHA-256 y que coincida (si falta, no actualiza), lo lanza con /VERYSILENT y
esta app se cierra (apagando los motores). El instalador espera a que se cierre, reemplaza los archivos y vuelve a
abrir la app. Es el mismo instalador que usa una persona a mano: nada de reemplazar .exe en caliente.
"""
from __future__ import annotations

import hashlib
import json
import logging
import subprocess
import tempfile
import time
import urllib.request
from dataclasses import dataclass
from pathlib import Path

import rutas
from version import NOMBRE_APP, REPO, __version__

log = logging.getLogger("vibracion")
API = f"https://api.github.com/repos/{REPO}/releases/latest"
# Reason: el actualizador baja "-Update.exe" (el mismo instalador con otro nombre) para que las descargas de GitHub
# distingan instalaciones nuevas ("-Setup.exe") de actualizaciones, sin telemetría. Si no está, usa el Setup.
ASSETS = (f"{NOMBRE_APP}-Update.exe", f"{NOMBRE_APP}-Setup.exe")
PREFIJO_DESCARGA = f"https://github.com/{REPO}/releases/download/"


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


@dataclass
class EstadoActualizacion:
    """Lo que muestra la sección "Actualizaciones" de Ajustes."""
    buscando: bool = False
    ultima_consulta: float = 0.0       # time.time() de la última consulta que respondió
    pendiente: Version | None = None   # versión nueva encontrada, todavía sin instalar
    error: str = ""                    # por qué falló la última consulta ("" si anduvo)


def _ultima_publicada() -> Version | None:
    """Versión publicada si es más nueva que la instalada. Lanza excepción si no se pudo consultar."""
    with _pedir(API, 15) as r:
        datos = json.load(r)
    tag = datos.get("tag_name", "")
    por_nombre = {a.get("name"): a for a in datos.get("assets", [])}
    asset = next((por_nombre[n] for n in ASSETS if n in por_nombre), None)
    if not tag or not asset or not es_mas_nueva(tag):
        return None
    url = str(asset.get("browser_download_url", ""))
    sha = str(asset.get("digest", "")).removeprefix("sha256:").lower()
    # Falla cerrado: sin SHA-256 publicado o con una URL que no sea de los releases de este repo, no se ofrece.
    if not url.startswith(PREFIJO_DESCARGA) or len(sha) != 64:
        log.warning("la versión %s no trae descarga verificable (url=%s, sha=%r); no se ofrece", tag, url, sha)
        return None
    return Version(tag.lstrip("vV"), url, sha, datos.get("body", ""))


def consultar(estado: EstadoActualizacion) -> Version | None:
    """Consulta GitHub y deja el resultado en `estado`. Devuelve la versión nueva, si hay."""
    estado.buscando = True
    try:
        nueva = _ultima_publicada()
    except Exception as ex:  # noqa: BLE001  (sin internet, límite de la API, etc.: se reintenta más tarde)
        log.info("no pude consultar actualizaciones: %s", ex)
        estado.error = str(ex)[:80]
        return None
    finally:
        estado.buscando = False
    estado.error, estado.ultima_consulta = "", time.time()
    estado.pendiente = nueva or estado.pendiente
    return nueva


def aplicar(v: Version) -> bool:
    """Baja el instalador, lo verifica y lo lanza. True si quedó corriendo (la app tiene que cerrarse ya)."""
    if not rutas.EMPAQUETADO:
        log.info("actualización %s disponible; desde el código fuente no se aplica", v.numero)
        return False
    if not v.url.startswith(PREFIJO_DESCARGA) or len(v.sha256) != 64:
        log.warning("actualización %s rechazada: descarga no verificable", v.numero)
        return False
    # Reason: carpeta temporal nueva y privada, así nadie puede dejar un .exe esperando con el nombre que vamos a usar.
    destino = Path(tempfile.mkdtemp(prefix=f"{NOMBRE_APP}-")) / f"{NOMBRE_APP}-Setup-{v.numero}.exe"
    try:
        log.info("bajando la versión %s", v.numero)
        h = hashlib.sha256()
        with _pedir(v.url, 120) as r, open(destino, "wb") as f:
            while bloque := r.read(1 << 16):
                f.write(bloque)
                h.update(bloque)
        if h.hexdigest() != v.sha256:
            raise ValueError("el instalador bajado no coincide con el publicado (SHA-256)")
    except Exception as ex:  # noqa: BLE001
        log.warning("no pude actualizar: %s", ex)
        destino.unlink(missing_ok=True)
        return False
    subprocess.Popen([str(destino), "/VERYSILENT", "/SUPPRESSMSGBOXES", "/NORESTART"], close_fds=True,
                     cwd=str(destino.parent))
    log.info("instalando la versión %s; la app se reinicia sola", v.numero)
    return True

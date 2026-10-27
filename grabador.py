"""Grabador de vuelos: guarda lo que manda el simulador, frame a frame, para afinar perfiles y como prueba.

Cada grabación es un .jsonl.gz en %APPDATA%\\VibracionURSA\\grabaciones\\ (≈10 MB por hora). Primera línea: cabecera
con versión y avión; después una línea por frame: {"t": segundos, "d": {variable: valor}}. Se reproduce con
herramientas\\reproducir.py. Sólo contiene datos del simulador (nada personal) y no sale de la PC salvo que el usuario
la comparta.
"""
from __future__ import annotations

import gzip
import json
import logging
import re
import threading
import time
from pathlib import Path

import rutas
from version import __version__

log = logging.getLogger("vibracion")
MAX_S = 3 * 3600   # Reason: que una grabación olvidada no llene el disco; a las 3 h se corta sola.


def carpeta() -> Path:
    d = rutas.datos_usuario() / "grabaciones"
    d.mkdir(parents=True, exist_ok=True)
    return d


class Grabador:
    def __init__(self) -> None:
        self._f = None
        self._t0 = 0.0
        self.archivo: Path | None = None
        self._lock = threading.Lock()   # escribe el hilo de vibración; empieza/termina la interfaz

    @property
    def grabando(self) -> bool:
        return self._f is not None

    def empezar(self, avion: str) -> Path:
        self.terminar()
        with self._lock:
            return self._empezar(avion)

    def _empezar(self, avion: str) -> Path:
        limpio = re.sub(r"[^\w\-]+", "_", avion or "avion")[:40].strip("_") or "avion"
        self.archivo = carpeta() / f"{time.strftime('%Y%m%d-%H%M%S')}-{limpio}.jsonl.gz"
        self._f = gzip.open(self.archivo, "wt", encoding="utf-8")
        self._t0 = time.time()
        self._f.write(json.dumps({"version": __version__, "avion": avion, "inicio": time.strftime("%Y-%m-%d %H:%M:%S")})
                      + "\n")
        log.info("grabando vuelo en %s", self.archivo.name)
        return self.archivo

    def escribir(self, t: float, datos: dict[str, float]) -> None:
        if self._f is None or not datos:
            return
        if t - self._t0 > MAX_S:
            log.info("grabación cortada a las 3 h")
            self.terminar()
            return
        with self._lock:
            if self._f is not None:
                self._f.write(json.dumps({"t": round(t - self._t0, 3), "d": {k: round(v, 4) for k, v in datos.items()}},
                                         separators=(",", ":")) + "\n")

    def terminar(self) -> None:
        with self._lock:
            if self._f is None:
                return
            self._f.close()
            self._f = None
            log.info("grabación terminada: %s", self.archivo.name if self.archivo else "?")


def leer(archivo: Path) -> tuple[dict, list[tuple[float, dict[str, float]]]]:
    """(cabecera, [(t, datos), ...]) de una grabación."""
    with gzip.open(archivo, "rt", encoding="utf-8") as f:
        cabecera = json.loads(f.readline())
        frames = [(r["t"], r["d"]) for r in map(json.loads, f) if "t" in r]
    return cabecera, frames

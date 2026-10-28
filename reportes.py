"""Reporte de problemas y de errores inesperados, sin servidores y sin mandar nada sin permiso.

- Un error no previsto (excepción en cualquier hilo) se guarda en %APPDATA%\\VibracionURSA\\errores\\ con el detalle,
  y la app avisa con una notificación.
- "Reportar un problema" abre en el navegador un issue de GitHub ya completo (versión, Windows, dispositivos, último
  error y las últimas líneas del registro). La persona lo ve y decide si lo manda; si no, no sale nada de la PC.
- Antes de armar el texto se tapan datos personales: carpeta de usuario, nombre de usuario y nombre del equipo.
"""
from __future__ import annotations

import os
import platform
import sys
import threading
import time
import traceback
import urllib.parse
import webbrowser
from pathlib import Path

import rutas
from version import REPO, __version__

MAX_URL = 7500   # Reason: GitHub corta URLs muy largas; el cuerpo se recorta para que entre.


def carpeta_errores() -> Path:
    d = rutas.datos_usuario() / "errores"
    d.mkdir(parents=True, exist_ok=True)
    return d


def sanear(texto: str) -> str:
    """Tapa la carpeta de usuario, el nombre de usuario y el nombre del equipo."""
    reemplazos = [
        (os.environ.get("USERPROFILE", ""), "%USERPROFILE%"),
        (os.environ.get("USERNAME", ""), "<usuario>"),
        (os.environ.get("COMPUTERNAME", ""), "<equipo>"),
    ]
    for buscar, poner in reemplazos:
        if buscar and len(buscar) >= 3:
            texto = texto.replace(buscar, poner).replace(buscar.lower(), poner)
    return texto


# ------------------------------------------------------------------ errores inesperados
def guardar_error(tipo: type[BaseException], valor: BaseException, tb: object, hilo: str = "principal") -> Path | None:
    try:
        detalle = "".join(traceback.format_exception(tipo, valor, tb))
        archivo = carpeta_errores() / time.strftime("error-%Y%m%d-%H%M%S.txt")
        archivo.write_text(f"version: {__version__}\nhilo: {hilo}\nfecha: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                           f"{detalle}", encoding="utf-8")
        return archivo
    except Exception:  # noqa: BLE001  (reportar un error nunca puede romper la app)
        return None


HUBO_ERROR = threading.Event()   # la app de bandeja lo mira para avisar con una notificación


def registrar_error(hilo: str) -> None:
    """Para usar dentro de un `except`: guarda el error en curso y avisa."""
    if guardar_error(*sys.exc_info(), hilo=hilo):  # type: ignore[arg-type]
        HUBO_ERROR.set()


def instalar_capturador() -> None:
    """Captura excepciones no previstas del hilo principal y de los demás hilos."""
    def en_principal(tipo, valor, tb):
        if guardar_error(tipo, valor, tb):
            HUBO_ERROR.set()
        sys.__excepthook__(tipo, valor, tb)

    def en_hilo(args: threading.ExceptHookArgs) -> None:
        if args.exc_type is SystemExit:
            return
        if guardar_error(args.exc_type, args.exc_value, args.exc_traceback, getattr(args.thread, "name", "?")):
            HUBO_ERROR.set()

    sys.excepthook = en_principal
    threading.excepthook = en_hilo


def error_sin_reportar() -> Path | None:
    """El último error guardado que todavía no se reportó."""
    errores = sorted(carpeta_errores().glob("error-*.txt"))
    if not errores or errores[-1].with_suffix(".reportado").exists():
        return None
    return errores[-1]


# ------------------------------------------------------------------ reporte a GitHub
def _ultimas_lineas(n: int = 40) -> str:
    try:
        lineas = rutas.archivo_log().read_text(encoding="utf-8", errors="replace").splitlines()
        return "\n".join(lineas[-n:])
    except OSError:
        return "(sin registro)"


def armar_reporte(estado: object | None = None) -> tuple[str, str]:
    """(título, cuerpo en Markdown) del reporte, ya saneado."""
    error = error_sin_reportar()
    disp = ", ".join(getattr(estado, "dispositivos", []) or []) or "none"
    conectado = "yes" if getattr(estado, "conectado", False) else "no"
    partes = [
        "**What happened?** (please describe it here)\n\n\n",
        "**System**",
        f"- Groundfeel: {__version__}",
        f"- Windows: {platform.platform()}",
        f"- Devices found: {disp}",
        f"- Simulator connected: {conectado}",
    ]
    ajustes = rutas.ajustes_usuario()
    if ajustes.is_file():
        partes.append(f"\n**Custom settings**\n```json\n{ajustes.read_text(encoding='utf-8')[:800]}\n```")
    if error:
        partes.append(f"\n**Unexpected error**\n```\n{error.read_text(encoding='utf-8')[-2500:]}\n```")
    partes.append(f"\n**Last log lines**\n```\n{_ultimas_lineas()}\n```")
    titulo = f"[{__version__}] " + ("Unexpected error" if error else "Problem report")
    return titulo, sanear("\n".join(partes))


def abrir_reporte(estado: object | None = None) -> None:
    """Abre el issue prellenado en el navegador y marca el último error como reportado."""
    titulo, cuerpo = armar_reporte(estado)
    base = f"https://github.com/{REPO}/issues/new?labels=bug&title={urllib.parse.quote(titulo)}&body="
    # Reason: si no entra en la URL se recorta desde el principio del registro (lo más viejo, lo menos útil).
    while len(base) + len(urllib.parse.quote(cuerpo)) > MAX_URL and len(cuerpo) > 500:
        corte = cuerpo.find("**Last log lines**")
        cuerpo = cuerpo[:corte + 40] + cuerpo[corte + 40 + 200:] if corte >= 0 else cuerpo[:-200]
    webbrowser.open(base + urllib.parse.quote(cuerpo))
    error = error_sin_reportar()
    if error:
        error.with_suffix(".reportado").touch()

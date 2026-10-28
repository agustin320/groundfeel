"""Textos de la interfaz en 20 idiomas (idiomas/<código>.json; inglés es la base y el respaldo).

Idioma: ajuste "idioma" ("auto" o un código como "es", "fr", "ja"). En "auto" sigue al idioma de Windows; si Windows
está en un idioma que no tenemos, inglés. Para agregar o corregir un idioma alcanza con editar su .json: las claves
que falten salen en inglés.
"""
from __future__ import annotations

import ctypes
import json

import rutas

# Idioma principal de Windows (LANGID & 0x3FF) -> código de archivo.
WINDOWS: dict[int, str] = {
    0x09: "en", 0x0A: "es", 0x04: "zh", 0x39: "hi", 0x0C: "fr", 0x01: "ar", 0x45: "bn", 0x16: "pt", 0x19: "ru",
    0x20: "ur", 0x21: "id", 0x07: "de", 0x11: "ja", 0x4E: "mr", 0x4A: "te", 0x1F: "tr", 0x49: "ta", 0x2A: "vi",
    0x12: "ko", 0x10: "it",
}


def _cargar() -> dict[str, dict]:
    carpeta = rutas.RECURSOS / "idiomas"
    out = {}
    for archivo in sorted(carpeta.glob("*.json")):
        try:
            out[archivo.stem] = json.loads(archivo.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue   # Reason: un archivo de idioma roto no puede impedir que arranque la app; queda el inglés.
    return out


IDIOMAS: dict[str, dict] = _cargar()
_IDIOMA = "en"


def disponibles() -> list[tuple[str, str]]:
    """[(código, nombre en su propio idioma)], inglés primero y después alfabético por código."""
    codigos = sorted(IDIOMAS, key=lambda c: (c != "en", c))
    return [(c, IDIOMAS[c].get("nombre", c)) for c in codigos]


def idioma_windows() -> str:
    try:
        lang = ctypes.windll.kernel32.GetUserDefaultUILanguage()
    except (AttributeError, OSError):
        return "en"
    cod = WINDOWS.get(lang & 0x3FF, "en")
    return cod if cod in IDIOMAS else "en"


def elegir(preferencia: str) -> None:
    """Fija el idioma: un código disponible o "auto" (sigue a Windows)."""
    global _IDIOMA
    _IDIOMA = preferencia if preferencia in IDIOMAS else idioma_windows()


def idioma() -> str:
    return _IDIOMA


def _buscar(seccion: str, clave: str) -> str:
    for cod in (_IDIOMA, "en"):
        valor = IDIOMAS.get(cod, {}).get(seccion, {}).get(clave)
        if valor:
            return valor
    return clave


def t(clave: str, **valores: object) -> str:
    if clave == "app":
        return IDIOMAS.get(_IDIOMA, {}).get("app") or IDIOMAS.get("en", {}).get("app", "Groundfeel")
    texto = _buscar("textos", clave)
    return texto.format(**valores) if valores else texto


def efecto(nombre: str) -> str:
    return _buscar("efectos", nombre)

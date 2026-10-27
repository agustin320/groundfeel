"""Perfiles por avión: ajustes que se aplican solos según el avión cargado (perfiles/*.json).

Formato de un perfil:
    {"nombre": "iniBuilds A350", "coincide": ["A350"], "ajustes": {"motores": {"reversa": 0.6}}}

- "coincide": textos que se buscan (sin distinguir mayúsculas) en el nombre del avión que informa el simulador (TITLE).
  Gana el primer perfil, en orden alfabético de archivo, que coincida.
- "ajustes": misma estructura que config.json; se aplica encima de los valores por defecto. Los ajustes del usuario
  (ajustes.json) se aplican encima del perfil, así que sus intensidades siempre mandan.
Sin perfil que coincida se usan los valores por defecto ("genérico"): todo avión funciona igual, los perfiles sólo
afinan.
"""
from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field

import rutas

log = logging.getLogger("vibracion")


@dataclass
class Perfil:
    nombre: str
    coincide: list[str] = field(default_factory=list)
    ajustes: dict = field(default_factory=dict)
    archivo: str = ""


def cargar() -> list[Perfil]:
    out = []
    for archivo in sorted((rutas.RECURSOS / "perfiles").glob("*.json")):
        if archivo.name.startswith("_"):
            continue   # ejemplos y plantillas
        try:
            datos = json.loads(archivo.read_text(encoding="utf-8"))
            out.append(Perfil(datos["nombre"], [str(c) for c in datos.get("coincide", [])],
                              datos.get("ajustes", {}), archivo.name))
        except (OSError, KeyError, json.JSONDecodeError) as ex:
            log.warning("perfil %s ignorado: %s", archivo.name, ex)
    return out


def elegir(titulo: str, perfiles: list[Perfil]) -> Perfil | None:
    t = titulo.lower()
    if not t:
        return None
    return next((p for p in perfiles if any(c.lower() in t for c in p.coincide if c)), None)

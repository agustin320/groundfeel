"""Perfiles por avión: ajustes que se aplican solos según el avión cargado (perfiles/*.json).

Formato de un perfil:
    {"nombre": "iniBuilds A350", "coincide": ["A350"], "ajustes": {"motores": {"reversa": 0.6}}}

- "coincide": textos que se buscan (sin distinguir mayúsculas) en el nombre del avión que informa el simulador (TITLE).
  Gana el primer perfil, en orden alfabético de archivo, que coincida.
- "ajustes": misma estructura que config.json; se aplica encima de los valores por defecto. Los ajustes del usuario
  (ajustes.json) se aplican encima del perfil, así que sus intensidades siempre mandan.
- "lvars" (opcional): variables propias del avión (L:vars) que hay que leer, como {"vmax": ["L:I_PFD_VMAX", "Knots"]}.
- "fuentes" (opcional): qué variable estándar reemplaza cada L:var, como {"AIRSPEED BARBER POLE": "vmax"}. Si la L:var
  vale 0 (el avión no la tiene o todavía no la publicó) se usa la variable estándar.
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
    lvars: dict[str, tuple[str, str]] = field(default_factory=dict)
    fuentes: dict[str, str] = field(default_factory=dict)


def cargar() -> list[Perfil]:
    out = []
    for archivo in sorted((rutas.RECURSOS / "perfiles").glob("*.json")):
        if archivo.name.startswith("_"):
            continue   # ejemplos y plantillas
        try:
            datos = json.loads(archivo.read_text(encoding="utf-8"))
            lvars = {str(a): (str(v[0]), str(v[1])) for a, v in datos.get("lvars", {}).items()}
            fuentes = {}
            for clave, alias in datos.get("fuentes", {}).items():
                if alias in lvars:
                    fuentes[str(clave)] = str(alias)
                else:
                    log.warning("perfil %s: la fuente %s usa la L:var %r, que no está en \"lvars\"",
                                archivo.name, clave, alias)
            out.append(Perfil(datos["nombre"], [str(c) for c in datos.get("coincide", [])],
                              datos.get("ajustes", {}), archivo.name, lvars, fuentes))
        except (OSError, KeyError, json.JSONDecodeError) as ex:
            log.warning("perfil %s ignorado: %s", archivo.name, ex)
    return out


def aplicar_fuentes(d: dict[str, float], perfil: Perfil | None) -> dict[str, float]:
    """Reemplaza las variables estándar por las L:vars que el perfil declara (sólo si la L:var vale algo)."""
    if not perfil or not perfil.fuentes:
        return d
    d = dict(d)
    for clave, alias in perfil.fuentes.items():
        v = d.get(f"LVAR:{alias}", 0.0)
        if v:
            d[clave] = v
    return d


def elegir(titulo: str, perfiles: list[Perfil]) -> Perfil | None:
    t = titulo.lower()
    if not t:
        return None
    return next((p for p in perfiles if any(c.lower() in t for c in p.coincide if c)), None)

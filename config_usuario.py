"""Configuración = config.json (valores por defecto, viene con cada versión) + ajustes.json (lo que cambió el usuario).

Así una actualización puede mejorar los valores por defecto sin pisar lo que el usuario ajustó a mano.
"""
from __future__ import annotations

import copy
import json
import logging
from pathlib import Path

import rutas

log = logging.getLogger("vibracion")


def fusionar(base: dict, encima: dict) -> dict:
    """Copia de `base` con `encima` aplicado recursivamente (los dicts se mezclan, el resto se reemplaza)."""
    out = copy.deepcopy(base)
    for k, v in encima.items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = fusionar(out[k], v)
        else:
            out[k] = copy.deepcopy(v)
    return out


def _leer(ruta: Path) -> dict:
    if not ruta.is_file():
        return {}
    return json.loads(ruta.read_text(encoding="utf-8"))


class Config:
    def __init__(self, defecto: Path | None = None, usuario: Path | None = None) -> None:
        self.ruta_defecto = defecto or rutas.config_por_defecto()
        self.ruta_usuario = usuario or rutas.ajustes_usuario()
        self.defecto = _leer(self.ruta_defecto)
        self.usuario: dict = {}
        self.datos: dict = {}
        self._mtimes: tuple[float, float] = (-1.0, -1.0)
        # Reason: la ventana (hilo de tk) guarda y recarga ella misma; si el lazo mirara sólo el valor de retorno de
        # recargar() nunca se enteraría del cambio. Cada carga nueva sube la generación y el lazo compara contra ella.
        self.generacion = 0
        self.recargar()

    def _mtimes_actuales(self) -> tuple[float, float]:
        f = (self.ruta_defecto, self.ruta_usuario)
        return tuple(p.stat().st_mtime if p.is_file() else 0.0 for p in f)  # type: ignore[return-value]

    def recargar(self) -> bool:
        """Relee si alguno de los dos archivos cambió. Devuelve True si hay datos nuevos."""
        m = self._mtimes_actuales()
        if m == self._mtimes:
            return False
        self._mtimes = m
        try:
            self.defecto = _leer(self.ruta_defecto)
            self.usuario = _leer(self.ruta_usuario)
        except json.JSONDecodeError as ex:
            log.warning("configuración con error, sigo con la anterior: %s", ex)
            return False
        self.datos = fusionar(self.defecto, self.usuario)
        self.generacion += 1
        return True

    def obtener(self, *clave: str) -> object:
        d: object = self.datos
        for k in clave:
            d = d[k]  # type: ignore[index]
        return d

    def guardar(self, *clave: str, valor: object) -> None:
        """Guarda un ajuste del usuario (sólo la diferencia; el resto sigue a los valores por defecto)."""
        d = self.usuario
        for k in clave[:-1]:
            d = d.setdefault(k, {})
        d[clave[-1]] = valor
        self.ruta_usuario.write_text(json.dumps(self.usuario, ensure_ascii=False, indent=2), encoding="utf-8")
        self.recargar()

    def restablecer(self) -> None:
        """Vuelve todo a los valores por defecto."""
        self.usuario = {}
        if self.ruta_usuario.is_file():
            self.ruta_usuario.unlink()
        self._mtimes = (-1.0, -1.0)
        self.recargar()

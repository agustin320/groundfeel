"""Reproduce una grabación de vuelo con el motor de efectos actual (sin simulador ni hardware) y resume qué sintió.

Uso: venv\\Scripts\\python.exe herramientas\\reproducir.py <grabación.jsonl.gz> [--perfil archivo.json]

Sirve para afinar un perfil de avión con datos reales y para comprobar que un cambio no rompe nada: mismo vuelo,
antes y después. Las grabaciones se hacen desde la app (Ajustes → "Grabar vuelo") y quedan en
%APPDATA%\\VibracionURSA\\grabaciones\\.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import grabador  # noqa: E402
import perfiles  # noqa: E402
import rutas  # noqa: E402
from config_usuario import fusionar  # noqa: E402
from efectos import EFECTOS, Efectos  # noqa: E402


def reproducir(archivo: Path, perfil_extra: dict | None = None) -> dict:
    cabecera, frames = grabador.leer(archivo)
    defecto = json.loads(rutas.config_por_defecto().read_text(encoding="utf-8"))
    p = perfiles.elegir(cabecera.get("avion", ""), perfiles.cargar())
    cfg = fusionar(fusionar(defecto, p.ajustes if p else {}), perfil_extra or {})
    ef = Efectos(cfg)
    maximos = {e: 0.0 for e in EFECTOS}
    suma = {e: 0.0 for e in EFECTOS}
    salida_max = {"joystick": 0, "throttle_1": 0, "throttle_2": 0}
    saltos = {k: 0 for k in salida_max}
    previo = dict.fromkeys(salida_max, 0)
    for t, d in frames:
        e, s = ef.paso(d, t)
        for k, v in e.items():
            maximos[k] = max(maximos[k], v)
            suma[k] += v
        for k, v in s.items():
            salida_max[k] = max(salida_max[k], v)
            saltos[k] += (v > 0) != (previo[k] > 0)
            previo[k] = v
    n = max(1, len(frames))
    duracion = frames[-1][0] if frames else 0.0
    return {"avion": cabecera.get("avion", "?"), "perfil": p.nombre if p else "genérico", "frames": len(frames),
            "duracion_min": round(duracion / 60, 1),
            "efectos": {k: {"max": round(maximos[k], 2), "prom": round(suma[k] / n, 3)} for k in EFECTOS},
            "salida_max": salida_max,
            "prendido_apagado_por_min": {k: round(v / max(duracion / 60, 1e-6), 1) for k, v in saltos.items()}}


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("grabacion", type=Path)
    ap.add_argument("--perfil", type=Path, help="perfil a probar encima (sólo su bloque 'ajustes')")
    a = ap.parse_args()
    extra = json.loads(a.perfil.read_text(encoding="utf-8")).get("ajustes", {}) if a.perfil else None
    print(json.dumps(reproducir(a.grabacion, extra), ensure_ascii=False, indent=2))

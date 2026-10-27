"""Vibración realista para WinWing URSA MINOR 32 (joystick L + throttle Metal R) en MSFS 2024.

Uso:  venv\\Scripts\\python.exe vibracion.py                 (normal)
      venv\\Scripts\\python.exe vibracion.py --silencio      (calcula y registra, pero no mueve los motores)
      venv\\Scripts\\python.exe vibracion.py --con-simulador (se cierra solo 30 s después de cerrar el sim)
Requiere que la vibración de SimAppPro2 esté apagada para estos dispositivos (si no, se pisan).
"""
from __future__ import annotations

import ctypes
import json
import logging
import sys
import time
from logging.handlers import RotatingFileHandler
from pathlib import Path

from efectos import EFECTOS, Efectos
from motores import Motor
from sim_lector import LectorSim

RAIZ = Path(__file__).resolve().parent
HZ = 40
PASO_CUANTIZADO = 1   # Reason: resolución completa para que el rodaje crezca de a poco (cada décima de nudo).

log = logging.getLogger("vibracion")


def configurar_log() -> None:
    log.setLevel(logging.INFO)
    h = RotatingFileHandler(RAIZ / "vibracion.log", maxBytes=2_000_000, backupCount=2, encoding="utf-8")
    h.setFormatter(logging.Formatter("%(asctime)s %(message)s", "%H:%M:%S"))
    log.addHandler(h)
    if sys.stdout is not None:   # Reason: con pythonw (lanzado por el sim) no hay consola y stdout es None.
        c = logging.StreamHandler(sys.stdout)
        c.setFormatter(logging.Formatter("%(asctime)s %(message)s", "%H:%M:%S"))
        log.addHandler(c)


def instancia_unica() -> object:
    """Evita dos copias abiertas a la vez (se pelearían por los motores)."""
    mutex = ctypes.windll.kernel32.CreateMutexW(None, False, "Global\\vibracion_ursa_unica")
    if ctypes.windll.kernel32.GetLastError() == 183:
        print("Ya hay otra copia de vibracion.py corriendo.")
        sys.exit(1)
    return mutex


class Config:
    def __init__(self, ruta: Path) -> None:
        self.ruta, self.mtime, self.datos = ruta, 0.0, {}
        self.recargar()

    def recargar(self) -> bool:
        m = self.ruta.stat().st_mtime
        if m == self.mtime:
            return False
        try:
            self.datos = json.loads(self.ruta.read_text(encoding="utf-8"))
            self.mtime = m
            return True
        except json.JSONDecodeError as ex:
            log.warning("config.json con error, sigo con la anterior: %s", ex)
            self.mtime = m
            return False


def abrir_motores() -> dict[str, Motor]:
    out = {}
    for nombre in ("joystick", "throttle"):
        try:
            out[nombre] = Motor(nombre)
        except Exception as ex:  # noqa: BLE001
            log.warning("no pude abrir el %s: %s", nombre, ex)
    return out


_MOTORES_ABIERTOS: dict[str, Motor] = {}


def _apagar_todo() -> None:
    for m in list(_MOTORES_ABIERTOS.values()):
        try:
            m.cerrar()
        except Exception:  # noqa: BLE001
            pass
    _MOTORES_ABIERTOS.clear()


# Reason: si cierran la ventana de consola, Python no corre el `finally`; este manejador apaga los motores antes.
_HANDLER = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_uint)(lambda _evento: (_apagar_todo(), False)[1])


def main() -> None:
    configurar_log()
    _mutex = instancia_unica()
    ctypes.windll.kernel32.SetConsoleCtrlHandler(_HANDLER, True)
    silencio = "--silencio" in sys.argv
    con_simulador = "--con-simulador" in sys.argv   # lanzado desde exe.xml: se cierra cuando se cierra el sim
    visto_sim, t_sin_sim = False, time.time()
    cfg = Config(RAIZ / "config.json")
    ef = Efectos(cfg.datos)
    try:
        sim = LectorSim()
    except FileNotFoundError as ex:
        log.error("%s", ex)
        sys.exit(2)
    sim.iniciar()
    motores = _MOTORES_ABIERTOS
    if not silencio:
        motores.update(abrir_motores())
    log.info("arrancado (%s). Motores: %s", "silencio" if silencio else "normal", ", ".join(motores) or "ninguno")

    ultimo = {"joystick": -1, "throttle_1": -1, "throttle_2": -1}
    acum = {e: 0.0 for e in EFECTOS}
    n_acum, t_log, t_cfg, t_reabrir, conectado_prev = 0, time.time(), time.time(), time.time(), False
    ultimo_log: dict = {}
    try:
        while True:
            t0 = time.time()
            if t0 - t_cfg > 2:
                t_cfg = t0
                if cfg.recargar():
                    ef.cfg = cfg.datos
                    log.info("config.json recargado")
            conectado = sim.conectado.is_set() and sim.frescura() < 1.0
            if conectado != conectado_prev:
                log.info("simulador %s", "conectado" if conectado else "sin datos (motores apagados)")
                conectado_prev = conectado
            if conectado:
                visto_sim, t_sin_sim = True, t0
            elif con_simulador and visto_sim and t0 - t_sin_sim > 30:
                log.info("el simulador se cerró: termino")
                break
            if conectado:
                efectos, salida = ef.paso(sim.datos(), t0)
            else:
                efectos, salida = {e: 0.0 for e in EFECTOS}, {k: 0 for k in ultimo}
            if not silencio:
                if len(motores) < 2 and t0 - t_reabrir > 10:
                    t_reabrir = t0
                    for k, v in abrir_motores().items():
                        motores.setdefault(k, v)
                for clave, valor in salida.items():
                    v = 0 if valor < 1 else min(255, PASO_CUANTIZADO * round(valor / PASO_CUANTIZADO))
                    if v == ultimo[clave]:
                        continue
                    disp = "joystick" if clave == "joystick" else "throttle"
                    m = motores.get(disp)
                    if m is None:
                        continue
                    try:
                        if disp == "joystick":
                            m.poner(v)
                        else:
                            m.poner(v, m.indices[0] if clave == "throttle_1" else m.indices[1])
                        ultimo[clave] = v
                    except Exception as ex:  # noqa: BLE001  (dispositivo desenchufado: se reabre)
                        log.warning("error escribiendo al %s: %s", disp, ex)
                        motores.pop(disp, None)
            for e in EFECTOS:
                acum[e] = max(acum[e], efectos[e])
            n_acum += 1
            if t0 - t_log >= 1.0:
                activos = {e: round(v, 1) for e, v in acum.items() if v >= 0.02}
                # Reason: parado o en crucero el estado se repite cada segundo; solo se registra cuando cambia.
                if activos and activos != ultimo_log:
                    ultimo_log = activos
                    d = sim.datos()
                    log.info("efectos %s | salida %s | gs=%.0f ias=%.0f suelo=%d sup=%d lat=%.1f n1=%.0f", activos,
                             salida, d.get("GROUND VELOCITY", 0), d.get("AIRSPEED INDICATED", 0),
                             int(d.get("SIM ON GROUND", 0)), int(d.get("SURFACE TYPE", -1)),
                             d.get("VELOCITY BODY X", 0), d.get("TURB ENG N1:1", 0))
                acum = {e: 0.0 for e in EFECTOS}
                n_acum, t_log = 0, t0
            time.sleep(max(0.0, 1.0 / HZ - (time.time() - t0)))
    except KeyboardInterrupt:
        pass
    finally:
        _apagar_todo()
        log.info("detenido, motores apagados")


if __name__ == "__main__":
    main()

"""Vibración realista para WinWing URSA MINOR 32 (joystick L + throttle Metal R) en MSFS 2024 — línea de comandos.

La forma normal de usarlo es la app de bandeja (`bandeja.py`, o el .exe). Esto es para desarrollo:
      venv\\Scripts\\python.exe vibracion.py                 (normal)
      venv\\Scripts\\python.exe vibracion.py --silencio      (calcula y registra, pero no mueve los motores)
      venv\\Scripts\\python.exe vibracion.py --con-simulador (se cierra solo 30 s después de cerrar el sim)
Requiere que la vibración de SimAppPro2 esté apagada para estos dispositivos (si no, se pisan).
"""
from __future__ import annotations

import ctypes
import sys
import time

from instancia import instancia_unica
from motor_vibracion import Vibracion, configurar_log, log

_VIB: Vibracion | None = None


def _al_cerrar_consola(_evento: int) -> bool:
    # Reason: si cierran la ventana de consola, Python no corre el `finally`; esto apaga los motores antes.
    if _VIB:
        _VIB.detener(espera=1.0)
    return False


_HANDLER = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_uint)(_al_cerrar_consola)


def main() -> None:
    global _VIB
    configurar_log(consola=sys.stdout is not None)
    if not instancia_unica():
        print("Ya hay otra copia corriendo (¿la app de la bandeja?).")
        sys.exit(1)
    ctypes.windll.kernel32.SetConsoleCtrlHandler(_HANDLER, True)
    _VIB = Vibracion(silencio="--silencio" in sys.argv)
    try:
        _VIB.iniciar()
    except FileNotFoundError as ex:
        log.error("%s", ex)
        sys.exit(2)
    con_simulador = "--con-simulador" in sys.argv
    try:
        while _VIB.corriendo():
            time.sleep(0.5)
            if con_simulador and _VIB.visto_sim and not _VIB.estado.conectado and time.time() - _VIB.t_sin_sim > 30:
                log.info("el simulador se cerró: termino")
                break
    except KeyboardInterrupt:
        pass
    finally:
        _VIB.detener()


if __name__ == "__main__":
    main()

"""Una sola copia a la vez (dos copias se pelearían por los motores)."""
from __future__ import annotations

import ctypes
import time

ERROR_ALREADY_EXISTS = 183
_MUTEX = None


def instancia_unica(esperar_s: float = 0.0) -> bool:
    """True si esta es la única copia. Con `esperar_s` reintenta (relevo tras una actualización)."""
    global _MUTEX
    k32 = ctypes.windll.kernel32
    fin = time.time() + esperar_s
    while True:
        h = k32.CreateMutexW(None, False, "Global\\vibracion_ursa_unica")
        if k32.GetLastError() != ERROR_ALREADY_EXISTS:
            _MUTEX = h
            return True
        k32.CloseHandle(h)
        if time.time() >= fin:
            return False
        time.sleep(0.5)


def liberar() -> None:
    """Suelta la instancia única antes de lanzar la copia que nos reemplaza."""
    global _MUTEX
    if _MUTEX:
        ctypes.windll.kernel32.CloseHandle(_MUTEX)
        _MUTEX = None

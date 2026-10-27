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


EVENTO_SALIR = "Local\\vibracion_ursa_salir"
SYNCHRONIZE, EVENT_MODIFY_STATE, WAIT_OBJECT_0 = 0x00100000, 0x0002, 0


def esperar_pedido_de_salida(al_pedir) -> None:
    """Bloquea hasta que otro proceso (el instalador o --salir) pida cerrar; entonces llama `al_pedir()`."""
    k32 = ctypes.windll.kernel32
    h = k32.CreateEventW(None, True, False, EVENTO_SALIR)
    if h and k32.WaitForSingleObject(h, 0xFFFFFFFF) == WAIT_OBJECT_0:
        al_pedir()


def pedir_salida(espera_s: float = 15.0) -> bool:
    """Le pide a la copia en marcha que cierre (apagando motores) y espera que suelte la instancia única."""
    k32 = ctypes.windll.kernel32
    h = k32.OpenEventW(EVENT_MODIFY_STATE | SYNCHRONIZE, False, EVENTO_SALIR)
    if not h:
        return True   # no hay ninguna corriendo
    k32.SetEvent(h)
    k32.CloseHandle(h)
    fin = time.time() + espera_s
    while time.time() < fin:
        m = k32.OpenMutexW(SYNCHRONIZE, False, "Global\\vibracion_ursa_unica")
        if not m:
            return True
        k32.CloseHandle(m)
        time.sleep(0.3)
    return False


def liberar() -> None:
    """Suelta la instancia única antes de lanzar la copia que nos reemplaza."""
    global _MUTEX
    if _MUTEX:
        ctypes.windll.kernel32.CloseHandle(_MUTEX)
        _MUTEX = None

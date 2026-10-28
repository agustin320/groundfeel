"""Reloj del lazo de vibración: ticks a frecuencia fija, sin deriva, y con la cadencia real medida.

Reason: con `Event.wait(1/HZ - trabajo)` el período real dependía del cuanto del timer de Windows (15,6 ms por
defecto) y se acumulaba el atraso de cada vuelta. Acá el próximo tick es un instante absoluto (prox += período), se
duerme hasta 2 ms antes y se termina con espera activa sobre perf_counter. Si la PC se trabó (el lazo quedó más de un
período atrás), no se manda una ráfaga de ticks para "recuperar": se sigue desde ahora.
"""
from __future__ import annotations

import ctypes
import time
from collections.abc import Callable

HZ_ENVIO = 50
_MARGEN_S = 0.002


class Reloj:
    def __init__(self, hz: float = HZ_ENVIO, ahora: Callable[[], float] = time.perf_counter,
                 dormir: Callable[[float], object] = time.sleep) -> None:
        self.periodo = 1.0 / hz
        self._ahora, self._dormir = ahora, dormir
        self._prox = self._ahora() + self.periodo
        self._ultimo = self._ahora()
        self._dts: list[float] = []

    def esperar(self) -> float:
        """Bloquea hasta el próximo tick; devuelve el tiempo real desde el tick anterior (s)."""
        resto = self._prox - self._ahora() - _MARGEN_S
        if resto > 0:
            self._dormir(resto)
        while self._ahora() < self._prox:
            pass
        ahora = self._ahora()
        self._prox += self.periodo
        if ahora > self._prox:          # quedó más de un período atrás: no recuperar en ráfaga
            self._prox = ahora + self.periodo
        dt, self._ultimo = ahora - self._ultimo, ahora
        if len(self._dts) < 20_000:
            self._dts.append(dt)
        return dt

    def estadisticas(self) -> dict[str, float]:
        """Percentiles del intervalo real entre ticks (ms) desde la última lectura; la reinicia."""
        dts, self._dts = sorted(self._dts), []
        if not dts:
            return {"p50_ms": 0.0, "p99_ms": 0.0, "max_ms": 0.0}

        def p(q: float) -> float:
            return round(dts[min(len(dts) - 1, int(q * len(dts)))] * 1000, 1)
        return {"p50_ms": p(0.5), "p99_ms": p(0.99), "max_ms": round(dts[-1] * 1000, 1)}


def timer_fino(si: bool) -> None:
    """Sube (o restituye) la resolución del timer de Windows a 1 ms mientras corre el lazo."""
    try:
        winmm = ctypes.WinDLL("winmm")
        (winmm.timeBeginPeriod if si else winmm.timeEndPeriod)(1)
    except (OSError, AttributeError):  # fuera de Windows (CI de pruebas) no hace falta
        pass

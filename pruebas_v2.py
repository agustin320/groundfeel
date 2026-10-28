"""Pruebas de la 2.0 (cadencia, efectos de vuelo, L:vars, editor). Las corre pruebas.py al final.

Reason: pruebas.py pasaba las 400 líneas; estas reciben sus helpers por parámetro para no ejecutarlo dos veces.
"""
from __future__ import annotations

from collections.abc import Callable


def correr_todo(caso: Callable, correr: Callable, BASE: dict, CFG: dict) -> None:
    _cadencia(caso)
    _nyquist(caso)


def _cadencia(caso: Callable) -> None:
    from cadencia import Reloj

    class Tiempo:
        """Reloj falso: dormir() se pasa `extra` segundos; la espera activa avanza 0,1 ms por consulta."""

        def __init__(self, extra: float) -> None:
            self.t, self.extra = 0.0, extra

        def ahora(self) -> float:
            self.t += 0.0001
            return self.t

        def dormir(self, s: float) -> None:
            self.t += s + self.extra

    tf = Tiempo(0.003)
    r = Reloj(50, tf.ahora, tf.dormir)
    t0 = tf.t
    dts = [r.esperar() for _ in range(50)]
    transcurrido = tf.t - t0
    prom_ms = sum(dts[1:]) / len(dts[1:]) * 1000
    caso("reloj sin deriva", abs(prom_ms - 20.0) < 0.3 and abs(transcurrido - 1.0) < 0.03,
         f"período promedio {prom_ms:.2f} ms, 50 ticks en {transcurrido:.3f} s")

    tf = Tiempo(0.0)
    r = Reloj(50, tf.ahora, tf.dormir)
    for _ in range(5):
        r.esperar()
    tf.t += 0.200                          # la PC se trabó 200 ms
    r.esperar()
    siguiente = r.esperar()
    caso("reloj no recupera en ráfaga", siguiente > 0.015, f"tick después de la traba: {siguiente * 1000:.1f} ms")
    est = r.estadisticas()
    caso("reloj mide la cadencia", est["max_ms"] > 200 and r.estadisticas()["max_ms"] == 0.0, f"{est}")


def _nyquist(caso: Callable) -> None:
    import re
    from pathlib import Path

    from cadencia import HZ_ENVIO
    fuente = (Path(__file__).parent / "efectos.py").read_text(encoding="utf-8")
    fijas = [float(x) for x in re.findall(r"math\.sin\(2 \* math\.pi \* ([\d.]+)", fuente)]
    variables = [float(a) + float(b) for a, b in re.findall(r"\+= \(([\d.]+) \+ ([\d.]+) \* _clamp", fuente)]
    todas = fijas + variables
    caso("texturas bajo Nyquist", len(fijas) >= 4 and len(variables) >= 3 and max(todas) <= HZ_ENVIO / 4,
         f"{len(todas)} frecuencias, máx {max(todas)} Hz (tope {HZ_ENVIO / 4})")

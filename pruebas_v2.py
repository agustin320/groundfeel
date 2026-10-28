"""Pruebas de la 2.0 (cadencia, efectos de vuelo, L:vars, editor). Las corre pruebas.py al final.

Reason: pruebas.py pasaba las 400 líneas; estas reciben sus helpers por parámetro para no ejecutarlo dos veces.
"""
from __future__ import annotations

from collections.abc import Callable


def correr_todo(caso: Callable, correr: Callable, BASE: dict, CFG: dict) -> None:
    _cadencia(caso)
    _nyquist(caso)
    _vuelo(caso, correr)
    _toque(caso, correr, CFG)
    _arranque(caso, correr, CFG)


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


def _vuelo(caso: Callable, correr: Callable) -> None:
    aire = {"SIM ON GROUND": 0, "AIRSPEED INDICATED": 300, "GEAR CENTER POSITION": 0}
    mx_rolido, _, _ = correr(dict(aire, **{"SPOILERS LEFT POSITION": 0.6, "SPOILERS RIGHT POSITION": 0.0}))
    mx_sb, _, _ = correr(dict(aire, **{"SPOILERS LEFT POSITION": 1.0, "SPOILERS RIGHT POSITION": 1.0}))
    caso("spoilers de alabeo no vibran", mx_rolido["speedbrake"] == 0 and mx_sb["speedbrake"] > 0.2,
         f"alabeo {mx_rolido['speedbrake']:.2f} / speedbrake {mx_sb['speedbrake']:.2f}")

    def slats(d, i):
        d["LEADING EDGE FLAPS LEFT PERCENT"] = min(0.5, i / 80 * 0.5)

    mx_sl, _, _ = correr({"SIM ON GROUND": 0, "AIRSPEED INDICATED": 200, "GEAR CENTER POSITION": 0}, 2.0, None, slats)
    caso("slats solos mueven flaps", mx_sl["flaps"] > 0.1, f"flaps {mx_sl['flaps']:.2f}")

    def sv(ias, barber):
        mx, _, _ = correr({"SIM ON GROUND": 0, "AIRSPEED INDICATED": ias, "AIRSPEED BARBER POLE": barber,
                           "GEAR CENTER POSITION": 0})
        return mx.get("sobrevelocidad", -1)
    s_alto, s_bajo, s_sin = sv(360, 350), sv(345, 350), sv(360, 0)
    caso("sobrevelocidad", s_alto > 0.3 and s_bajo == 0 and s_sin == 0,
         f"+10 kt {s_alto:.2f} / -5 kt {s_bajo:.2f} / sin dato {s_sin:.2f}")


def _toque(caso: Callable, correr: Callable, CFG: dict) -> None:
    from efectos import Efectos

    def serie(por_pata: bool) -> list[tuple[float, float]]:
        """Aire a -400 fpm, toque de mains a 130 kt y nariz a los 2 s. (máx aterrizaje, máx rodadura) por tramo."""
        ef = Efectos(CFG)
        correr({"SIM ON GROUND": 0, "VERTICAL SPEED": -400, "AIRSPEED INDICATED": 130, "GROUND VELOCITY": 130}, 1.0, ef)
        suelo = {"SIM ON GROUND": 1, "AIRSPEED INDICATED": 130, "GROUND VELOCITY": 130,
                 "GEAR IS ON GROUND:1": int(por_pata), "GEAR IS ON GROUND:2": int(por_pata), "GEAR IS ON GROUND:0": 0}
        tramos = []
        for seg, nariz in ((0.5, 0), (0.8, 0), (0.7, 0), (0.6, int(por_pata))):
            mx, _, _ = correr(dict(suelo, **{"GEAR IS ON GROUND:0": nariz}), seg, ef)
            tramos.append((mx["aterrizaje"], mx["rodadura"]))
        return tramos

    (a0, r0), (_, r1), (a2, _), (a3, _) = serie(True)
    caso("toque de mains y después nariz", a0 > 0.4 and a2 < 0.05 and a3 > 0.15,
         f"mains {a0:.2f} / entre medio {a2:.2f} / nariz {a3:.2f}")
    caso("silencio en el toque", r0 == 0 and r1 > 0, f"rodadura primeros 0,5 s {r0:.2f} / después {r1:.2f}")
    (b0, _), _, _, (b3, _) = serie(False)
    caso("toque sin datos por pata", b0 > 0.4 and b3 < 0.05, f"mains {b0:.2f} / nariz {b3:.2f}")


def _arranque(caso: Callable, correr: Callable, CFG: dict) -> None:
    from efectos import Efectos
    apagado = {"TURB ENG N1:1": 0, "TURB ENG N1:2": 0, "TURB ENG N2:1": 0, "TURB ENG N2:2": 0}

    # Arranque del motor 1: starter 2 s (N2 sube a 20), ignición, aceleración hasta idle y en marcha.
    ef = Efectos(CFG)
    fases = []
    for seg, extra in ((2.0, {"GENERAL ENG STARTER:1": 1, "TURB ENG N2:1": 20}),
                       (0.4, {"GENERAL ENG STARTER:1": 1, "GENERAL ENG COMBUSTION:1": 1, "TURB ENG N2:1": 25,
                              "TURB ENG N1:1": 5}),
                       (2.0, {"GENERAL ENG STARTER:1": 1, "GENERAL ENG COMBUSTION:1": 1, "TURB ENG N2:1": 45,
                              "TURB ENG N1:1": 14})):
        mx, s, _ = correr(dict(apagado, **extra), seg, ef)
        fases.append((mx["motores"], s["throttle_1"], s["throttle_2"]))
    (st, st_t1, st_t2), (ig, _, _), (ac, _, _) = fases
    caso("arranque en 3 etapas", 0.03 < st < ig and ac > 0.03 and st_t1 > 0 and st_t2 == 0,
         f"starter {st:.2f} / ignición {ig:.2f} / aceleración {ac:.2f} · palancas {st_t1:.0f}/{st_t2:.0f}")

    # Arranque abortado: se corta el starter sin combustión → cae a 0 en menos de 2 s.
    ef = Efectos(CFG)
    correr(dict(apagado, **{"GENERAL ENG STARTER:1": 1, "TURB ENG N2:1": 15}), 2.0, ef)
    correr(dict(apagado, **{"TURB ENG N2:1": 10}), 1.5, ef)
    mx_ab, _, _ = correr(dict(apagado, **{"TURB ENG N2:1": 5}), 0.5, ef)
    caso("arranque abortado se apaga", mx_ab["motores"] < 0.01, f"después de 1,5 s {mx_ab['motores']:.3f}")

    # Cuatrimotor: arrancar el motor 3 mueve la palanca derecha y no la izquierda.
    cuatro = dict(apagado, **{"NUMBER OF ENGINES": 4, "GENERAL ENG STARTER:3": 1, "TURB ENG N2:3": 20})
    _, s4, _ = correr(cuatro, 2.0, Efectos(CFG))
    caso("4 motores: el 3 va a la palanca derecha", s4["throttle_2"] > 0 and s4["throttle_1"] == 0,
         f"izquierda {s4['throttle_1']:.0f} / derecha {s4['throttle_2']:.0f}")

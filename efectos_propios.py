"""Efectos propios: los arma el usuario en el editor (Efectos → Mis efectos) y se suman a los incorporados.

Un efecto propio toma una variable del simulador (cualquier variable de SimConnect o una L:var del avión), decide
cuándo está activo (disparo + umbral), pasa el valor por una curva de respuesta que dibuja el usuario y lo modula con
una forma (constante, pulso, golpe, seno, sierra). Se guarda en ajustes.json ("efectos_propios") y se comparte como
JSON.

Reason del límite de frecuencia: el lazo manda 50 valores por segundo y el motor tiene inercia; una forma de más de
F_MAX_HZ (un cuarto de la cadencia) llega deformada. El editor muestra la salida real, ya cuantizada a 50 Hz.
"""
from __future__ import annotations

import math
from dataclasses import asdict, dataclass, field

from cadencia import HZ_ENVIO

F_MAX_HZ = HZ_ENVIO / 4
DISPAROS = ("siempre", "sobre", "bajo", "entre", "booleano", "mientras_cambia")
FORMAS = ("constante", "pulso", "golpe", "seno", "sierra")
RUTEOS = ("joystick", "throttle", "ambos")
MEZCLAS = ("suma", "max")
_GOLPE_S = 0.15


@dataclass
class EfectoPropio:
    nombre: str = "Mi efecto"
    fuente: str = "AIRSPEED INDICATED"
    unidad: str = "Knots"
    disparo: str = "sobre"
    umbral: tuple[float, float] = (0.0, 100.0)
    histeresis: float = 0.0
    curva: list[tuple[float, float]] = field(default_factory=lambda: [(0.0, 0.0), (1.0, 1.0)])
    forma: str = "constante"
    hz: float = 5.0
    intensidad: float = 0.5
    ruteo: str = "ambos"
    mezcla: str = "suma"
    reemplaza: str = ""          # efecto incorporado que este reemplaza ("" = ninguno)
    activo: bool = True

    # ------------------------------------------------------------------ validación y JSON
    def validar(self) -> list[str]:
        """Errores legibles (claves de i18n con su detalle); vacío si el efecto se puede usar."""
        errores = []
        if not self.fuente.strip():
            errores.append("ep_err_fuente")
        if self.fuente.upper().startswith("L:") and (" " in self.fuente.strip() or not self.unidad.strip()):
            errores.append("ep_err_lvar")
        lo, hi = self.umbral
        if self.disparo != "booleano" and not hi > lo:
            errores.append("ep_err_umbral")
        xs = [p[0] for p in self.curva]
        if not 2 <= len(self.curva) <= 8 or any(b <= a for a, b in zip(xs, xs[1:], strict=False)) \
                or any(not (0 <= x <= 1 and 0 <= y <= 1) for x, y in self.curva):
            errores.append("ep_err_curva")
        if self.forma in ("pulso", "seno", "sierra") and not 0 < self.hz <= F_MAX_HZ:
            errores.append("ep_err_hz")
        if self.disparo not in DISPAROS or self.forma not in FORMAS or self.ruteo not in RUTEOS \
                or self.mezcla not in MEZCLAS:
            errores.append("ep_err_opcion")
        return errores

    def a_dict(self) -> dict:
        d = asdict(self)
        d["umbral"], d["curva"] = list(self.umbral), [list(p) for p in self.curva]
        return d

    @classmethod
    def desde_dict(cls, d: dict) -> EfectoPropio:
        base = cls()
        campos = {k: d[k] for k in base.a_dict() if k in d}
        if "umbral" in campos:
            campos["umbral"] = (float(campos["umbral"][0]), float(campos["umbral"][1]))
        if "curva" in campos:
            campos["curva"] = [(float(x), float(y)) for x, y in campos["curva"]]
        return cls(**campos)


PLANTILLAS: dict[str, EfectoPropio] = {
    # Valores calibrados con los efectos incorporados (golpe del tren, zumbido de motor, pulsos del antiskid).
    "golpe": EfectoPropio("Golpe", "GEAR HANDLE POSITION", "Bool", "booleano", (0.0, 1.0), 0.0,
                          [(0.0, 0.0), (1.0, 1.0)], "golpe", 5.0, 0.6),
    "zumbido": EfectoPropio("Zumbido", "TURB ENG N1:1", "Percent", "sobre", (20.0, 100.0), 1.0,
                            [(0.0, 0.15), (1.0, 0.6)], "seno", 9.0, 0.5),
    "pulsacion": EfectoPropio("Pulsación", "BRAKE LEFT POSITION", "Percent over 100", "sobre", (0.2, 1.0), 0.05,
                              [(0.0, 0.3), (1.0, 0.8)], "pulso", 4.0, 0.5),
    "creciente": EfectoPropio("Creciente", "AIRSPEED INDICATED", "Knots", "sobre", (250.0, 350.0), 5.0,
                              [(0.0, 0.0), (0.5, 0.2), (1.0, 1.0)], "constante", 5.0, 0.6),
}


def curva(puntos: list[tuple[float, float]], x: float) -> float:
    """Interpolación lineal por tramos; fuera del rango se queda en los extremos."""
    x = min(1.0, max(0.0, x))
    for (x0, y0), (x1, y1) in zip(puntos, puntos[1:], strict=False):
        if x <= x1:
            return y0 + (y1 - y0) * (x - x0) / (x1 - x0) if x1 > x0 else y1
    return puntos[-1][1]


class Evaluador:
    """Estado de un efecto propio entre ticks (histéresis, derivada, golpe de una sola vez, fase de la forma)."""

    def __init__(self, ef: EfectoPropio) -> None:
        self.ef = ef
        self.activo = False
        self.x_prev: float | None = None
        self.t_golpe = -99.0
        self.fase = 0.0
        self.vel = 0.0
        self.sim_t: float | None = None

    def valor(self, d: dict, t: float, dt: float) -> float:
        e = self.ef
        x = d.get(e.fuente, d.get("LVAR:" + e.fuente))
        if x is None:   # la variable todavía no llegó (o el avión no la tiene): no se evalúa nada
            self.x_prev, self.activo = None, False
            return 0.0
        lo, hi = e.umbral
        span = max(1e-9, hi - lo)
        h = e.histeresis
        if e.disparo == "mientras_cambia":
            # Derivada contra el tiempo del simulador: en un tick sin frame nuevo se repite la anterior (si no, el lazo
            # a 50 Hz ve frames repetidos del sim, deriva 0 y el efecto titila).
            sim_t = d.get("SIMULATION TIME")
            if self.x_prev is None:
                self.vel = 0.0
            elif sim_t is None or self.sim_t is None:
                self.vel = abs(x - self.x_prev) / dt if dt > 0 else self.vel
            elif sim_t > self.sim_t:
                self.vel = abs(x - self.x_prev) / (sim_t - self.sim_t)
            if sim_t is None or self.sim_t is None or sim_t > self.sim_t or self.x_prev is None:
                self.x_prev, self.sim_t = x, sim_t
            vel = self.vel
            activo, norm = vel > (lo - h if self.activo else lo), (vel - lo) / span
        elif e.disparo == "sobre":
            activo, norm = x > (lo - h if self.activo else lo), (x - lo) / span
        elif e.disparo == "bajo":
            activo, norm = x < (hi + h if self.activo else hi), (hi - x) / span
        elif e.disparo == "entre":
            activo, norm = lo <= x <= hi, (x - lo) / span
        elif e.disparo == "booleano":
            activo, norm = x >= 0.5, 1.0
        else:
            activo, norm = True, (x - lo) / span
        if e.disparo != "mientras_cambia":
            self.x_prev = x
        if activo and not self.activo:
            self.t_golpe = t
        self.activo = activo
        if not activo or not e.activo:
            return 0.0
        self.fase += e.hz * dt
        if e.forma == "pulso":
            onda = 1.0 if self.fase % 1.0 < 0.5 else 0.0
        elif e.forma == "seno":
            onda = 0.5 + 0.5 * math.sin(2 * math.pi * self.fase)
        elif e.forma == "sierra":
            onda = self.fase % 1.0
        elif e.forma == "golpe":
            onda = math.exp(-(t - self.t_golpe) / _GOLPE_S) if t - self.t_golpe < _GOLPE_S * 5 else 0.0
        else:
            onda = 1.0
        return max(0.0, min(1.0, e.intensidad * curva(e.curva, norm) * onda))


def cargar(lista: list[dict]) -> list[EfectoPropio]:
    """Los efectos propios válidos de la configuración (los inválidos se descartan sin romper el lazo)."""
    out = []
    for d in lista or []:
        try:
            ef = EfectoPropio.desde_dict(d)
        except (TypeError, ValueError, KeyError, IndexError):
            continue
        if not ef.validar():
            out.append(ef)
    return out


def serie_prueba(ef: EfectoPropio, segundos: float) -> list[float]:
    """Valores de la fuente para "Probar en el dispositivo": recorren el umbral para que el efecto se sienta entero.

    Booleano: se prende y se apaga cada 1 s (un golpe se repite). "Mientras cambia": la fuente cambia al ritmo del
    medio del rango. El resto: barrido del mínimo al máximo en 2,5 s, 1 s arriba, y de nuevo.
    """
    n, lo, hi = int(segundos * HZ_ENVIO), ef.umbral[0], ef.umbral[1]
    if ef.disparo == "booleano":
        return [1.0 if (i // HZ_ENVIO) % 2 == 0 else 0.0 for i in range(n)]
    if ef.disparo == "mientras_cambia":
        return [(lo + hi) / 2 * i / HZ_ENVIO for i in range(n)]
    ciclo = int(3.5 * HZ_ENVIO)
    barrido = int(2.5 * HZ_ENVIO)
    desde, hasta = (hi, lo) if ef.disparo == "bajo" else (lo, hi)
    return [desde + (hasta - desde) * min(1.0, (i % ciclo) / barrido) for i in range(n)]


def valores_de_grabacion(frames: list[dict], fuente: str) -> list[float]:
    """Valores de la fuente en una grabación, remuestreados a 50 Hz (mantiene el último valor entre frames)."""
    if not frames:
        return []
    out, i, t_fin = [], 0, frames[-1].get("t", 0.0)
    for k in range(int(t_fin * HZ_ENVIO) + 1):
        t = k / HZ_ENVIO
        while i + 1 < len(frames) and frames[i + 1].get("t", 0.0) <= t:
            i += 1
        d = frames[i].get("d", {})
        out.append(float(d.get(fuente, d.get("LVAR:" + fuente, 0.0))))
    return out


def vista_previa(ef: EfectoPropio, valores: list[float], cfg: dict, disp: str = "throttle") -> list[int]:
    """Lo que realmente le llega al motor (0..255) tick a tick, a 50 Hz, para una serie de valores de la fuente.

    Corre el mismo motor de efectos del lazo (zona muerta, pulsado bajo la zona muerta, ganancia del dispositivo,
    empujón de arranque) con los efectos incorporados apagados, así el editor muestra la salida real y no la curva
    ideal.
    """
    from efectos import EFECTOS, Efectos
    c = {**cfg, "efectos_propios": [ef.a_dict()],
         "mezcla": {k: {e: 0.0 for e in EFECTOS} for k in cfg["mezcla"]}}
    motor = Efectos(c)
    base = {"SIM ON GROUND": 1, "GROUND VELOCITY": 0.0, "SURFACE TYPE": 4, "NUMBER OF ENGINES": 2}
    dt, clave = 1.0 / HZ_ENVIO, "joystick" if disp == "joystick" else "throttle_1"
    out = []
    for i, x in enumerate(valores):
        d = dict(base, **{ef.fuente: x, "SIMULATION TIME": 1000.0 + i * dt})
        _, salida = motor.paso(d, i * dt)
        out.append(int(salida[clave]))
    return out

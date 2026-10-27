"""Rodaje con modelo físico: perfil de pista ISO 8608 + tren de nariz como cuarto de vehículo (2 masas).

Idea (método estándar de ingeniería para taxi sobre pista rugosa):
1. Perfil de la superficie: ruido blanco filtrado en el espacio con la densidad espectral de ISO 8608
   G(n) = G0·(n/n0)^-2. Al recorrerlo a velocidad v, la excitación en el tiempo sale sola: más rápido = golpes más
   seguidos y más fuertes. Se suman las juntas de las losas / luces de eje como lomitas cada `separacion_juntas_m`.
2. Tren de nariz: rueda (masa no suspendida + resorte del neumático) y amortiguador (resorte + amortiguación) que
   sostienen la porción de fuselaje sobre la nariz. Se integra en sub-pasos de 2,5 ms.
3. Lo que siente la mano: aceleración vertical de la cabina filtrada (se saca el cabeceo lento, < ~3 Hz), valor
   eficaz en una ventana corta, menos el umbral de detección, comprimido con la ley de Stevens (exponente ~0,8).
Devuelve una intensidad 0..1 que reemplaza a la rodadura heurística en el joystick.
"""
from __future__ import annotations

import math
import random

KT_A_MS = 0.514444
N0 = 0.1                 # ciclos/m: frecuencia espacial de referencia de ISO 8608
N_BAJA = 0.011           # ciclos/m: corte bajo del perfil (sin derivas infinitas)
SUBPASO = 0.0025         # s


class RodajeFisico:
    def __init__(self, cfg: dict) -> None:
        self.cfg = cfg
        self.z_perfil = 0.0          # altura del perfil bajo la rueda (m)
        self.x_junta = random.uniform(0, 1)
        self.zu = self.vu = 0.0      # rueda: posición / velocidad
        self.zs = self.vs = 0.0      # cabina: posición / velocidad
        self.a_prev = 0.0
        self.a_hp = 0.0              # aceleración de cabina filtrada (pasa altos)
        self.ms2 = 0.0               # media cuadrática móvil
        self.a_rms = 0.0

    def _g0(self, superficie: str) -> float:
        return self.cfg["rugosidad_g0"].get(superficie, self.cfg["rugosidad_g0"]["otra"]) * 1e-6

    def paso(self, gs_kt: float, superficie: str, en_tierra: bool, dt: float) -> float:
        c = self.cfg
        if not en_tierra or dt <= 0:
            self.__init__(c)
            return 0.0
        v = max(0.0, gs_kt) * KT_A_MS
        g0 = self._g0(superficie)
        ms, mu = c["masa_cabina_kg"], c["masa_rueda_kg"]
        ks, cs, kt = c["rigidez_amortiguador"], c["amortiguacion"], c["rigidez_neumatico"]
        n = max(1, int(round(dt / SUBPASO)))
        h = dt / n
        for _ in range(n):
            # Perfil ISO 8608 en el tiempo (ruido blanco filtrado de 1er orden).
            ruido = random.gauss(0.0, 1.0) * math.sqrt(h)
            self.z_perfil += (-2 * math.pi * N_BAJA * v * self.z_perfil * h
                              + 2 * math.pi * N0 * math.sqrt(g0 * v) * ruido)
            # Juntas de losas / luces: lomita de coseno de `ancho_junta_m` cada `separacion_juntas_m` (± irregular).
            self.x_junta += v * h / c["separacion_juntas_m"]
            fr = self.x_junta - math.floor(self.x_junta)
            ancho = c["ancho_junta_m"] / c["separacion_juntas_m"]
            junta = c["altura_junta_m"] * 0.5 * (1 - math.cos(2 * math.pi * fr / ancho)) if fr < ancho else 0.0
            zr = self.z_perfil + junta
            # Cuarto de vehículo (Euler semi-implícito).
            f_susp = ks * (self.zu - self.zs) + cs * (self.vu - self.vs)
            f_neum = kt * (zr - self.zu)
            self.vu += (f_neum - f_susp) / mu * h
            self.vs += f_susp / ms * h
            self.zu += self.vu * h
            self.zs += self.vs * h
            a_s = f_susp / ms
            # Pasa altos de 1er orden (~3 Hz): el cabeceo lento es movimiento, no vibración.
            alfa = 1.0 / (1.0 + 2 * math.pi * c["corte_hz"] * h)
            self.a_hp = alfa * (self.a_hp + a_s - self.a_prev)
            self.a_prev = a_s
            # Valor eficaz con ventana corta (constante de tiempo `ventana_s`).
            self.ms2 += (self.a_hp ** 2 - self.ms2) * (h / c["ventana_s"])
        self.a_rms = math.sqrt(max(0.0, self.ms2))
        # Umbral de detección de la mano: por debajo no se percibe; arriba, ley de Stevens.
        p = (max(0.0, self.a_rms - c["a_umbral"]) / c["a_ref"]) ** c["exponente_stevens"]
        return min(1.0, p)

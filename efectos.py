"""Motor de efectos: convierte el estado del simulador en intensidades de vibración (0..1) por efecto y por motor.

Todas las intensidades salen de `Efectos.paso(datos, t)`; no toca hardware. Ver config.json para las ganancias.
"""
from __future__ import annotations

import math
import random

from rodaje_fisico import RodajeFisico

G_FTS2 = 32.174
KT_A_MS = 0.514444

# Tipos de superficie de MSFS (SURFACE TYPE)
PAVIMENTO = {0, 4, 10, 15, 16, 17, 18, 19, 20, 23}
PASTO = {1, 3, 5, 6, 7}
RIPIO_TIERRA = {12, 14, 21, 22}

EFECTOS = ("rodadura", "rodaje", "sacudones", "aterrizaje", "tren", "flaps", "speedbrake", "motores", "reversa",
           "frenos", "aceleracion", "derrape", "perdida", "sobrevelocidad")


def _clamp(x: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return lo if x < lo else hi if x > hi else x


def _frac(x: float) -> float:
    return x - math.floor(x)


def _norm01(x: float) -> float:
    """Algunas variables vienen 0..1 y otras 0..100 según el avión: se normaliza a 0..1."""
    return _clamp(x / 100.0 if x > 1.5 else x)


class Efectos:
    def __init__(self, cfg: dict) -> None:
        self.cfg = cfg
        self.fase_juntas = 0.0
        self.gs_suave = 0.0
        self.fase_pulsado = 0.0
        self.rodaje_fis = RodajeFisico(cfg["rodaje_fisico"])
        self.sd_acum, self.t_fin_toque = 0.0, -99.0
        self.salida_prev = {"joystick": 0, "throttle_1": 0, "throttle_2": 0}
        self.prendido = {"joystick": False, "throttle_1": False, "throttle_2": False}
        self.ritmo_pulsado = 1.0
        self.n1_motor_prev = {n: 0.0 for n in range(1, 5)}
        self.t_arranque_motor = {n: -99.0 for n in range(1, 5)}
        self.arr = {n: {"t_starter": None, "t_ign": -99.0, "comb_prev": False, "v": 0.0} for n in range(1, 5)}
        self.mult_junta = 1.0
        self.en_tierra_prev: bool | None = None
        self.vs_aire = 0.0
        self.t_toque = -99.0
        self.amp_toque = 0.0
        self.tren_prev: float | None = None
        self.t_traba = -99.0
        self.t_destrabe = -99.0
        self.flaps_prev: float | None = None
        self.ay_lenta = 0.0
        self.t_prev: float | None = None
        self.sim_t_prev: float | None = None
        self.t_sim_quieto = 0.0
        # frenado
        self.decel_prev = 0.0
        self.t_golpe_freno, self.amp_golpe_freno = -99.0, 0.0
        self.fase_freno = 0.0
        self.t_proximo_antiskid, self.amp_antiskid, self.t_pulso_antiskid = 0.0, 0.0, -99.0
        self.frenando_reciente, self.t_detencion = -99.0, -99.0
        self.gs_prev = 0.0
        # aceleración
        self.n1_prev = 0.0
        self.paseo = 0.0
        self.spool = 0.0
        self.fase_spool = 0.0
        self.fase_acel = 0.0
        self.fase_sobrevel = 0.0
        self.nariz_prev = False
        self.amp_nariz, self.t_nariz = 0.0, -99.0
        self._dt = 0.0

    # ------------------------------------------------------------------ efectos individuales
    def _rodadura(self, d: dict, t: float, dt: float) -> float:
        c = self.cfg["rodadura"]
        # Reason: parado, la velocidad del sim tiembla entre 0 y ~0,5 kt; se suaviza y se exige 0,3 kt para arrancar.
        self.gs_suave += (d.get("GROUND VELOCITY", 0.0) - self.gs_suave) * _clamp(dt / 0.4)
        gs = self.gs_suave
        if not d.get("SIM ON GROUND") or gs < 0.3:
            return 0.0
        sup = int(d.get("SURFACE TYPE", 4))
        fs = c["factor_superficie"]
        f_sup = fs["pavimento"] if sup in PAVIMENTO else fs["pasto"] if sup in PASTO else \
            fs["ripio_tierra"] if sup in RIPIO_TIERRA else fs["otra"]
        irregular = sup in PASTO or sup in RIPIO_TIERRA
        s = _clamp(gs / c["velocidad_rumor_max_kt"])
        # Golpes de juntas/luces: uno cada `separacion_juntas_m`, cada vez más seguidos con la velocidad.
        fase_ant = self.fase_juntas
        self.fase_juntas += gs * KT_A_MS / c["separacion_juntas_m"] * dt
        if math.floor(self.fase_juntas) != math.floor(fase_ant):
            self.mult_junta = 1.0 + (random.uniform(-1, 1) * c["irregularidad_pasto"] if irregular else 0.0)
        ciclo = _frac(self.fase_juntas)
        duty = 0.18
        golpe = math.sin(math.pi * ciclo / duty) if ciclo < duty else 0.0
        # Arranque sutil: a paso de hombre casi no se siente; crece en curva con la velocidad.
        lento = c["piso_lento"]
        crece = lento + (1 - lento) * s ** c["curva_juntas"]
        juntas = c["golpe_juntas"] * golpe * crece * self.mult_junta
        # Rumor continuo: arranca apenas rueda en `arranque` (justo por encima de lo que el motor necesita para girar;
        # por debajo no se siente nada) y crece suave hasta `rumor_continuo` en la carrera de despegue.
        textura = 0.85 + 0.15 * math.sin(2 * math.pi * 9.0 * t)
        if irregular:
            textura *= 1.0 + random.uniform(-c["irregularidad_pasto"], c["irregularidad_pasto"]) * 0.5
        # Curva tipo raíz: sube rápido en las primeras décimas de nudo (cada 0,1 kt se nota) y se aplana arriba.
        rumor = (c["arranque"] + (c["rumor_continuo"] - c["arranque"]) * s ** c["curva"]) * textura
        return _clamp((juntas + rumor) * f_sup)

    def _sacudones(self, d: dict, dt: float) -> float:
        """Sacudones reales: aceleración vertical respecto de su media lenta (pista irregular, turbulencia)."""
        c = self.cfg["sacudones"]
        ay = d.get("ACCELERATION BODY Y", 0.0)
        k = _clamp(dt / 0.6)
        self.ay_lenta += (ay - self.ay_lenta) * k
        dev_g = abs(ay - self.ay_lenta) / G_FTS2
        return c["ganancia"] * _clamp((dev_g - c["umbral_g"]) / (c["max_g"] - c["umbral_g"]))

    def _aterrizaje(self, d: dict, t: float) -> float:
        c = self.cfg["aterrizaje"]
        en_tierra = bool(d.get("SIM ON GROUND"))
        if not en_tierra:
            self.vs_aire = d.get("VERTICAL SPEED", 0.0)
        # Reason: al cargar un vuelo el sim pasa de "en el aire" a "en tierra" con el avión quieto y disparaba un
        # toque falso; un aterrizaje real siempre es con velocidad.
        elif self.en_tierra_prev is False and d.get("GROUND VELOCITY", 0.0) > 30:
            hundimiento = abs(min(0.0, self.vs_aire))
            self.amp_toque = c["maximo"] * max(0.25, _clamp((hundimiento - c["vs_suave_fpm"]) /
                                                             (c["vs_duro_fpm"] - c["vs_suave_fpm"])))
            self.t_toque = t
        # Rueda de nariz: segundo golpe, más suave, cuando la pata delantera apoya después de las principales. Si el
        # avión no publica el contacto por pata (GEAR IS ON GROUND:0 siempre en 0), sólo queda el toque de las mains.
        nariz = bool(d.get("GEAR IS ON GROUND:0"))
        if (nariz and not self.nariz_prev and en_tierra and 0 < t - self.t_toque < 20
                and d.get("GROUND VELOCITY", 0.0) > 30):
            self.amp_nariz = c["nariz"] * max(0.4, self.amp_toque / c["maximo"])
            self.t_nariz = t
        self.nariz_prev = nariz
        self.en_tierra_prev = en_tierra
        textura = 0.75 + 0.25 * math.sin(2 * math.pi * 12 * t)
        v = 0.0
        for amp, t0 in ((self.amp_toque, self.t_toque), (self.amp_nariz, self.t_nariz)):
            if 0 <= t - t0 <= c["duracion_s"] * 3:
                v = max(v, amp * math.exp(-(t - t0) / c["duracion_s"]))
        return v * textura

    def _tren(self, d: dict, t: float) -> float:
        """Tren de aterrizaje como en el avión real: golpes, no un zumbido mientras se mueve.

        - Destrabe: al empezar a moverse se suelta el traba (uplock al bajar, downlock al subir): un golpe seco.
        - Tránsito: casi nada; si se configura, un rumor muy leve del aire sobre el tren.
        - Traba: al llegar abajo (downlock) o arriba (uplock) el golpe más fuerte, el "clunk" de la cabina.
        - Con el tren abajo en vuelo, el aire sobre las ruedas da un rumor suave que crece con la velocidad.
        Reason: antes vibraba parejo todo el tránsito (~10 s) y no se parecía a nada real.
        """
        c = self.cfg["tren"]
        g = _norm01(d.get("GEAR CENTER POSITION", 1.0))
        ias = d.get("AIRSPEED INDICATED", 0.0)
        prev = self.tren_prev if self.tren_prev is not None else g
        self.tren_prev = g
        if (prev >= 0.98 > g) or (prev <= 0.02 < g):
            self.t_destrabe = t
        if (prev < 0.98 <= g) or (prev > 0.02 >= g):
            self.t_traba = t
        por_aire = 0.6 + 0.4 * _clamp(ias / 200)   # con más velocidad el tren pelea más contra el aire
        v = 0.0
        dtd = t - self.t_destrabe
        if dtd < 0.4:
            v += c.get("golpe_destrabe", 0.35) * por_aire * math.exp(-dtd / 0.08)
        dtt = t - self.t_traba
        if dtt < 0.6:
            # Golpe principal y un rebote chico ~0,12 s después (el mecanismo asentándose).
            v += c["golpe_traba"] * por_aire * (math.exp(-dtt / 0.1) + 0.35 * math.exp(-abs(dtt - 0.12) / 0.04))
        if 0.02 < g < 0.98:
            v += c["transito"] * por_aire * (0.7 + 0.3 * random.random())
        if not d.get("SIM ON GROUND") and g >= 0.98:
            v += c["aire_tren_abajo"] * _clamp(ias / 250) ** 2 * (0.7 + 0.3 * random.random())
        return _clamp(v)

    def _flaps(self, d: dict, dt: float, t: float) -> float:
        # Reason: en algunos aviones los slats se mueven solos (sin flaps de borde de fuga): también es "flaps".
        f = (_norm01(d.get("TRAILING EDGE FLAPS LEFT PERCENT", 0.0)),
             _norm01(d.get("LEADING EDGE FLAPS LEFT PERCENT", 0.0)))
        prev = self.flaps_prev if self.flaps_prev is not None else f
        self.flaps_prev = f
        moviendo = dt > 0 and max(abs(f[0] - prev[0]), abs(f[1] - prev[1])) / dt > 0.004
        return self.cfg["flaps"]["movimiento"] * (0.7 + 0.3 * math.sin(2 * math.pi * 7 * t)) if moviendo else 0.0

    def _speedbrake(self, d: dict) -> float:
        c = self.cfg["speedbrake"]
        izq, der = _norm01(d.get("SPOILERS LEFT POSITION", 0.0)), _norm01(d.get("SPOILERS RIGHT POSITION", 0.0))
        # Reason: muchos aviones alabean con spoilers de un solo lado; eso no es freno aerodinámico y no debe vibrar.
        if abs(izq - der) > c.get("asimetria_max", 0.10):
            return 0.0
        sp = min(izq, der)
        if sp < 0.03:
            return 0.0
        textura = 0.6 + 0.4 * random.random()
        if d.get("SIM ON GROUND"):
            return _clamp(c["tierra"] * sp * _clamp(d.get("GROUND VELOCITY", 0.0) / 80)) * textura
        return _clamp(c["aire"] * sp * _clamp(d.get("AIRSPEED INDICATED", 0.0) / 300) ** 2 * 2.0) * textura

    def _sobrevelocidad(self, t: float, d: dict) -> float:
        """Velocidad por encima de la máxima del avión (barber pole): vibración que crece con el exceso."""
        c = self.cfg["sobrevelocidad"]
        barber = d.get("AIRSPEED BARBER POLE", 0.0)
        if barber < 50 or d.get("SIM ON GROUND"):     # el avión no la publica, o estamos en tierra
            return 0.0
        exceso = _clamp((d.get("AIRSPEED INDICATED", 0.0) - barber) / c["rango_kt"])
        if exceso <= 0:
            return 0.0
        self.fase_sobrevel += (5.0 + 7.0 * exceso) * self._dt
        return c["maximo"] * (0.35 + 0.65 * exceso) * (0.7 + 0.3 * math.sin(2 * math.pi * self.fase_sobrevel))

    def _potencia(self, d: dict, n: int) -> float:
        """Potencia del motor n en % (0..100), comparable entre tipos de avión.

        Jets: N1. Pistón (ENGINE TYPE 0) y turbohélice (5): no tienen N1, se usa el % de RPM máximas. Reason: con sólo
        N1 los efectos de motor no existían en un Cessna o un King Air.
        """
        if int(d.get("ENGINE TYPE", 1)) in (0, 5):
            return d.get(f"GENERAL ENG PCT MAX RPM:{n}", 0.0)
        return d.get(f"TURB ENG N1:{n}", 0.0)

    def _ralenti(self, d: dict) -> float:
        c = self.cfg["motores"]
        return c.get("rpm_idle_pct", 26.0) if int(d.get("ENGINE TYPE", 1)) in (0, 5) else c["n1_idle"]

    def _motor(self, d: dict, n: int, t: float, dt: float) -> tuple[float, float]:
        """(zumbido, reversa) del motor n (1 a 4). Qué palanca lo siente lo decide `_palancas`."""
        arranque = self._arranque(d, n, t, dt)
        z, r = self._motor_en_marcha(d, n, t, dt)
        return max(z, arranque), r

    def _arranque(self, d: dict, n: int, t: float, dt: float) -> float:
        """Puesta en marcha en etapas: starter (rampa; en pistón, golpes de arranque a 3 Hz), ignición (un golpe) y
        aceleración hasta el ralentí. En ralentí cede al zumbido continuo. Si se corta, cae suave (arranque abortado).
        """
        c, a = self.cfg["arranque"], self.arr[n]
        starter = bool(d.get(f"GENERAL ENG STARTER:{n}"))
        comb = bool(d.get(f"GENERAL ENG COMBUSTION:{n}"))
        idle, pot = self._ralenti(d), self._potencia(d, n)
        if comb and not a["comb_prev"] and pot < idle - 0.5:
            a["t_ign"] = t
        a["comb_prev"] = comb
        if not starter:
            a["t_starter"] = None
        elif a["t_starter"] is None:
            a["t_starter"] = t
        v = 0.0
        if starter and not comb:
            rampa = _clamp((t - a["t_starter"]) / c["rampa_s"])
            if int(d.get("ENGINE TYPE", 1)) in (0, 5):
                v = c["starter"] * rampa * (1.0 if _frac(t * 3.0) < 0.5 else 0.3)
            else:
                v = c["starter"] * rampa * (0.85 + 0.15 * random.random())
        elif comb and pot < idle - 0.5:
            v = c["aceleracion"] * (0.4 + 0.6 * _clamp(pot / idle))
        if 0 <= t - a["t_ign"] < 1.5:
            v = max(v, c["ignicion"] * math.exp(-(t - a["t_ign"]) / 0.3))
        a["v"] = max(v, a["v"] * math.exp(-dt / c["caida_s"])) if dt > 0 else v
        return a["v"]

    def _motor_en_marcha(self, d: dict, n: int, t: float, dt: float) -> tuple[float, float]:
        c = self.cfg["motores"]
        n1 = self._potencia(d, n)
        dn1 = (n1 - self.n1_motor_prev[n]) / dt if dt > 0 else 0.0
        self.n1_motor_prev[n] = n1
        # Puesta en marcha: mientras el motor gana vueltas hacia el ralentí, un rumor que crece con la potencia.
        idle = self._ralenti(d)
        if 2 < n1 < idle - 0.5 and dn1 > 0.05:
            self.t_arranque_motor[n] = t
        if n1 < idle - 0.5 and t - self.t_arranque_motor[n] < 1.0:
            return c["puesta_en_marcha"] * (0.3 + 0.7 * n1 / idle) * (0.75 + 0.25 * random.random()), 0.0
        if n1 < 15:
            return 0.0, 0.0
        x = _clamp((n1 - idle) / (100 - idle))
        # En ralentí queda un mínimo apenas perceptible; desde ahí crece con la potencia.
        piso = c["minimo_ralenti"]
        zumbido = (piso + (c["zumbido_tierra"] - piso) * x) if d.get("SIM ON GROUND") else c["zumbido_aire"] * x
        rev = _norm01(d.get(f"TURB ENG REVERSE NOZZLE PERCENT:{n}", 0.0))
        # Reason: el A320 de FBW no publica la tobera de reversa (quedó en 0 en el aterrizaje real del 26-10, con N1 77
        # frenando). Se infiere: en tierra, N1 alto y el avión desacelerando = reversa.
        # Sólo jets: un avión a pistón con RPM altas frenando no tiene reversa.
        es_jet = int(d.get("ENGINE TYPE", 1)) == 1
        if es_jet and d.get("SIM ON GROUND") and n1 > 35 and d.get("ACCELERATION BODY Z", 0.0) < -2.0:
            rev = max(rev, _clamp((n1 - 30) / 45))
        reversa = c["reversa"] * rev * (0.3 + 0.7 * x) * (0.7 + 0.3 * random.random()) if rev > 0.05 else 0.0
        return zumbido, reversa

    def _palancas(self, d: dict, t: float, dt: float) -> tuple[tuple[float, float], tuple[float, float]]:
        """(zumbido, reversa) de la palanca izquierda y la derecha según cuántos motores tiene el avión.

        1 motor: las dos palancas lo siguen. 2: uno por palanca. 3: el central va a las dos. 4: 1-2 izquierda, 3-4
        derecha (como los mandos de un cuatrimotor).
        """
        n_mot = min(4, max(1, int(d.get("NUMBER OF ENGINES", 2))))
        mot = {n: self._motor(d, n, t, dt) for n in range(1, n_mot + 1)}
        grupos = {1: ((1,), (1,)), 2: ((1,), (2,)), 3: ((1, 2), (2, 3)), 4: ((1, 2), (3, 4))}[n_mot]
        return tuple((max(mot[n][0] for n in g), max(mot[n][1] for n in g)) for g in grupos)  # type: ignore[return-value]

    def _frenos(self, d: dict, t: float, dt: float) -> float:
        """Frenado dinámico: golpe inicial (cabeceo), pulsos del antibloqueo, temblor que se hace más lento al perder
        velocidad, y un golpecito al detenerse."""
        c = self.cfg["frenos"]
        gs = d.get("GROUND VELOCITY", 0.0)
        en_tierra = bool(d.get("SIM ON GROUND"))
        decel = max(0.0, -d.get("ACCELERATION BODY Z", 0.0))          # ft/s², positivo al frenar
        freno = max(_norm01(d.get("BRAKE LEFT POSITION", 0.0)), _norm01(d.get("BRAKE RIGHT POSITION", 0.0)))
        # Golpe inicial: cuando la desaceleración sube rápido (jerk) aparece un golpe proporcional.
        tiron = (decel - self.decel_prev) / dt if dt > 0 else 0.0
        self.decel_prev = decel
        # Reason: casi parado no hay inercia que cabecee el avión; el golpe escala con la velocidad (nulo bajo 3 kt).
        por_velocidad = _clamp((gs - 3) / 25)
        if en_tierra and por_velocidad > 0 and tiron > c["tiron_umbral"] and t - self.t_golpe_freno > 0.6:
            self.t_golpe_freno = t
            self.amp_golpe_freno = c["golpe_inicial"] * _clamp(tiron / (3 * c["tiron_umbral"])) * por_velocidad
        v = 0.0
        dtg = t - self.t_golpe_freno
        if dtg < 0.5:
            v += self.amp_golpe_freno * math.exp(-dtg / 0.15)
        frenando = en_tierra and gs > 3 and decel > 2.5 and freno > 0.15
        if frenando:
            fuerza = _clamp(decel / 14)
            # Temblor ligado al giro de las ruedas: la frecuencia baja con la velocidad (de ~14 Hz a ~3 Hz).
            self.fase_freno += (3.0 + 9.0 * _clamp(gs / 140)) * dt
            onda = 0.5 + 0.5 * math.sin(2 * math.pi * self.fase_freno)
            por_vel = 0.2 + 0.8 * _clamp(gs / 40)
            v += c["temblor"] * fuerza * por_vel * (0.4 + 0.6 * onda) * (0.85 + 0.3 * random.random())
            # Antibloqueo: con freno fuerte y velocidad alta, pulsos irregulares de 6-12 por segundo.
            if freno > 0.6 and gs > 20 and decel > 8:
                if t >= self.t_proximo_antiskid:
                    self.t_pulso_antiskid = t
                    self.t_proximo_antiskid = t + random.uniform(1 / 12, 1 / 6)
                    self.amp_antiskid = c["antibloqueo"] * random.uniform(0.5, 1.0)
                v += self.amp_antiskid * math.exp(-(t - self.t_pulso_antiskid) / 0.03)
            self.frenando_reciente = t
        # Golpecito al detenerse después de frenar (la nariz se asienta).
        if self.gs_prev >= 1.0 > gs and en_tierra and t - self.frenando_reciente < 3:
            self.t_detencion = t
        self.gs_prev = gs
        if t - self.t_detencion < 0.4:
            v += c["golpe_detencion"] * math.exp(-(t - self.t_detencion) / 0.12)
        return _clamp(v)

    def _aceleracion(self, d: dict, t: float, dt: float) -> float:
        """Aceleración dinámica: empuje inicial al subir potencia, pulsación que se acelera con las vueltas del motor y
        una fuerza que acompaña la aceleración real con variaciones irregulares."""
        c = self.cfg["aceleracion"]
        n1 = max(self._potencia(d, 1), self._potencia(d, 2))
        dn1 = (n1 - self.n1_prev) / dt if dt > 0 else 0.0
        self.n1_prev = n1
        acel = max(0.0, d.get("ACCELERATION BODY Z", 0.0))             # ft/s², positivo al acelerar
        en_tierra = bool(d.get("SIM ON GROUND"))
        # Paseo aleatorio lento: la intensidad "respira" en vez de quedar plana.
        self.paseo += random.uniform(-1, 1) * dt * 2.5
        self.paseo = _clamp(self.paseo, -0.35, 0.35)
        v = 0.0
        # Empuje inicial: motores tomando vueltas rápido.
        if dn1 > c["spool_umbral"]:
            self.spool = min(1.0, self.spool + dt * 2.0)
        else:
            self.spool = max(0.0, self.spool - dt * 0.8)
        if self.spool > 0:
            self.fase_spool += (2.0 + 10.0 * _clamp((n1 - 20) / 70)) * dt
            # Reason: en vuelo el autothrust mueve el N1 todo el tiempo en la aproximación y el empuje pulsante se
            # sentía como pulsos sueltos en el throttle; en el aire queda al 30 %, como la fuerza de aceleración.
            en_aire = 1.0 if en_tierra else 0.3
            v += c["empuje_inicial"] * self.spool * en_aire * (0.5 + 0.5 * math.sin(2 * math.pi * self.fase_spool))
        # Fuerza de la aceleración real (en tierra se siente mucho más que en el aire).
        if acel > 1.0:
            fuerza = _clamp(acel / 10) * (1.0 if en_tierra else 0.3)
            self.fase_acel += (4.0 + 8.0 * _clamp((n1 - 20) / 70)) * dt
            pulso = 0.6 + 0.4 * math.sin(2 * math.pi * self.fase_acel)
            v += c["fuerza"] * fuerza * pulso * (1.0 + self.paseo)
        return _clamp(v)

    def _derrape(self, d: dict, t: float) -> float:
        """Ruedas derrapando de costado: vibración áspera e irregular que crece con la velocidad lateral."""
        c = self.cfg["derrape"]
        if not d.get("SIM ON GROUND") or d.get("GROUND VELOCITY", 0.0) < 3:
            return 0.0
        lateral = abs(d.get("VELOCITY BODY X", 0.0))                  # ft/s
        x = _clamp((lateral - c["umbral_fts"]) / (c["maximo_fts"] - c["umbral_fts"]))
        if x <= 0:
            return 0.0
        aspereza = 0.5 + 0.3 * math.sin(2 * math.pi * 11 * t) + 0.4 * random.random()
        return _clamp(c["fuerza"] * x * aspereza)

    def _perdida(self, d: dict, t: float) -> float:
        c = self.cfg["perdida"]
        if d.get("SIM ON GROUND") or d.get("AIRSPEED INDICATED", 0.0) < 60:
            return 0.0
        alpha = d.get("INCIDENCE ALPHA", 0.0)
        if alpha > 90:      # Reason: sin flujo el ángulo de ataque no tiene sentido (vale ~180 parado).
            alpha = 0.0
        x = _clamp((alpha - c["alpha_inicio_deg"]) / (c["alpha_full_deg"] - c["alpha_inicio_deg"]))
        if d.get("STALL WARNING"):
            x = max(x, 0.8)
        return c["buffet"] * x * (0.6 + 0.4 * random.random()) if x > 0 else 0.0

    # ------------------------------------------------------------------ paso completo
    def paso(self, d: dict, t: float) -> tuple[dict[str, float], dict[str, float]]:
        """Devuelve (efectos 0..1, salida por motor 0..255) para el frame actual."""
        dt = 0.0 if self.t_prev is None else max(0.0, min(0.2, t - self.t_prev))
        self.t_prev = t
        self._dt = dt
        # Pausa: el tiempo de simulación no avanza → todo apagado.
        sim_t = d.get("SIMULATION TIME", 0.0)
        if self.sim_t_prev is not None and sim_t <= self.sim_t_prev:
            self.t_sim_quieto += dt
        else:
            self.t_sim_quieto = 0.0
        self.sim_t_prev = sim_t
        if not d or self.t_sim_quieto > 0.3:
            return {e: 0.0 for e in EFECTOS}, {"joystick": 0, "throttle_1": 0, "throttle_2": 0}

        (m1, r1), (m2, r2) = self._palancas(d, t, dt)
        fisico = self.cfg.get("rodaje_modelo") == "fisico"
        rodaje = 0.0
        if fisico:
            sup = int(d.get("SURFACE TYPE", 4))
            nombre_sup = "pavimento" if sup in PAVIMENTO else "pasto" if sup in PASTO else \
                "ripio_tierra" if sup in RIPIO_TIERRA else "otra"
            self.rodaje_fis.cfg = self.cfg["rodaje_fisico"]
            rodaje = self.rodaje_fis.paso(d.get("GROUND VELOCITY", 0.0), nombre_sup, bool(d.get("SIM ON GROUND")), dt,
                                          d.get("TOTAL WEIGHT", 0.0))
        ef = {
            "rodadura": self._rodadura(d, t, dt),
            "rodaje": rodaje,
            "sacudones": self._sacudones(d, dt),
            "aterrizaje": self._aterrizaje(d, t),
            "tren": self._tren(d, t),
            "flaps": self._flaps(d, dt, t),
            "speedbrake": self._speedbrake(d),
            "motores": max(m1, m2),
            "reversa": max(r1, r2),
            "frenos": self._frenos(d, t, dt),
            "aceleracion": self._aceleracion(d, t, dt),
            "derrape": self._derrape(d, t),
            "perdida": self._perdida(d, t),
            "sobrevelocidad": self._sobrevelocidad(t, d),
        }
        # Ventana de silencio: en el toque sólo se siente el toque (lo demás lo taparía).
        if 0 <= t - self.t_toque < self.cfg["aterrizaje"].get("silencio_s", 0.0):
            ef = {e: (v if e == "aterrizaje" else 0.0) for e, v in ef.items()}
            m1 = r1 = m2 = r2 = 0.0
        mez, gan = self.cfg["mezcla"], self.cfg["ganancia_general"]
        # Los toquecitos van al ritmo de la velocidad (como las ruedas pasando por la pista): lentos al arrancar, más
        # seguidos al acelerar.
        pps = self.cfg["pulsos_por_segundo"]
        ritmo = pps["min"] + (pps["max"] - pps["min"]) * _clamp(self.gs_suave / pps["a_kt"])
        self.fase_pulsado += dt * ritmo
        self.ritmo_pulsado = ritmo

        def mezclar(disp: str, motor_n: tuple[float, float] | None = None, clave: str = "joystick") -> int:
            w = mez[disp]
            # Con el modelo físico el joystick usa "rodaje" en vez de la "rodadura" heurística (throttle: igual).
            omitir = {"motores", "reversa", "rodadura" if fisico and disp == "joystick" else "rodaje"}
            total = sum(ef[e] * w.get(e, 0.0) for e in EFECTOS if e not in omitir)
            mot, rev = motor_n if motor_n else (ef["motores"], ef["reversa"])
            total += mot * w["motores"] + rev * w["reversa"]
            # Reason: el motor no gira por debajo de cierto valor (zona muerta); con ganancias bajas todo caía ahí y
            # "no vibraba nada". Todo efecto real arranca justo en el borde de la zona muerta y la ganancia escala
            # lo que está por encima.
            if disp == "joystick" and self.cfg.get("joystick_solo_en_tierra") and not d.get("SIM ON GROUND"):
                return 0
            zm = self.cfg.get("zona_muerta", {}).get(disp, 0)
            # Histéresis: se prende al pasar el umbral y se apaga recién por debajo de la mitad. Reason: un efecto
            # suave con textura aleatoria (tren abajo en la aproximación) oscilaba justo en el umbral y, con la zona
            # muerta del throttle (20), el motor saltaba 0 ↔ 25 una y otra vez: se sentía como pulsos.
            umbral = self.cfg.get("umbral_efecto", 0.02)
            if total < (umbral * 0.5 if self.prendido[clave] else umbral):
                self.prendido[clave] = False
                return 0
            self.prendido[clave] = True
            bruto = 255 * gan[disp] * _clamp(total)
            # Por debajo de la zona muerta el motor no puede vibrar "más suave": se pulsa al mínimo con un ciclo
            # proporcional (golpecitos cortos y espaciados), que se siente más leve que un zumbido continuo.
            hasta = self.cfg.get("pulsado_hasta", {}).get(disp, 0)
            if bruto < hasta:
                # Toque corto: el motor no llega a tomar vueltas del todo y se siente leve; dura más si el efecto crece.
                tq = self.cfg["toque_s"]
                dur = tq["min"] + (tq["max"] - tq["min"]) * bruto / hasta
                if not fisico:
                    encendido = _frac(self.fase_pulsado) < dur * self.ritmo_pulsado
                    return int(zm + 1) if encendido else 0
                # Modulación sigma-delta: la fracción de tiempo encendido sigue a la intensidad, sin ritmo fijo; el
                # ritmo lo pone el propio perfil de la pista.
                if t < self.t_fin_toque:
                    return int(zm + 1)
                self.sd_acum += bruto / hasta * dt
                if self.sd_acum >= dur:
                    self.sd_acum -= dur
                    self.t_fin_toque = t + dur * random.uniform(0.8, 1.2)
                    return int(zm + 1)
                return 0
            if hasta:
                self.sd_acum = 0.0
            return int(round(zm + (255 - zm) * gan[disp] * _clamp(total) - hasta))

        def con_empujon(disp: str, v: int) -> int:
            # Empujón al arrancar (técnica de los fabricantes de motores de vibración): si el motor estaba quieto, el
            # primer frame va más fuerte para que tome vueltas rápido y el golpe se sienta nítido, no blando.
            emp = self.cfg.get("empujon_arranque", {}).get(disp, 0)
            if emp and v > 0 and self.salida_prev[disp] == 0:
                v = min(255, v + emp)
            self.salida_prev[disp] = v
            return v

        salida = {"joystick": con_empujon("joystick", mezclar("joystick")),
                  "throttle_1": mezclar("throttle", (m1, r1), "throttle_1"),
                  "throttle_2": mezclar("throttle", (m2, r2), "throttle_2")}
        return ef, salida

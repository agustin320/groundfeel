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
    _pausa(caso, correr, CFG)
    _lvars(caso)
    _propios(caso, correr, CFG)
    _probar_en_dispositivo(caso)
    _grabacion(caso)
    _config_en_vivo(caso)
    _datos_faltantes_y_frames(caso, CFG)
    _paquete_lvars(caso)
    _ralenti_bajo(caso, correr, CFG)


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

    # Arranque abortado: se corta el starter sin combustión -> cae a 0 en menos de 2 s.
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


def _pausa(caso: Callable, correr: Callable, CFG: dict) -> None:
    import struct

    from efectos import Efectos
    from sim_lector import leer_evento
    ef = Efectos(CFG)
    correr({"GROUND VELOCITY": 40, "TURB ENG N1:1": 60}, 1.0, ef)
    _, s, _ = correr({"GROUND VELOCITY": 40, "TURB ENG N1:1": 60, "PAUSA": 1}, 0.025, ef)
    caso("pausa por evento apaga en el tick siguiente", max(s.values()) == 0, f"salida {s}")
    raw = struct.pack("<IIIIII", 24, 6, 4, 0xFFFFFFFF, 1, 4)    # RECV_EVENT: grupo, evento 1, dato 4 (pausa activa)
    caso("lee el evento de pausa", leer_evento(raw) == (1, 4), f"{leer_evento(raw)}")


def _lvars(caso: Callable) -> None:
    import json
    import tempfile
    from pathlib import Path

    import perfiles
    import rutas
    tmp = Path(tempfile.mkdtemp())
    (tmp / "perfiles").mkdir()
    (tmp / "perfiles" / "estudio.json").write_text(json.dumps({
        "nombre": "Estudio", "coincide": ["Estudio"],
        "lvars": {"vmax": ["L:I_PFD_VMAX", "Knots"]},
        "fuentes": {"AIRSPEED BARBER POLE": "vmax", "TURB ENG N1:1": "no_declarada"}}), encoding="utf-8")
    original, rutas.RECURSOS = rutas.RECURSOS, tmp
    try:
        p = perfiles.cargar()[0]
    finally:
        rutas.RECURSOS = original
    d = {"AIRSPEED BARBER POLE": 350.0, "LVAR:vmax": 320.0, "TURB ENG N1:1": 40.0}
    con = perfiles.aplicar_fuentes(d, p)
    sin = perfiles.aplicar_fuentes(dict(d, **{"LVAR:vmax": 0.0}), p)
    caso("L:var del perfil reemplaza la fuente", con["AIRSPEED BARBER POLE"] == 320.0 and con["TURB ENG N1:1"] == 40.0
         and sin["AIRSPEED BARBER POLE"] == 350.0 and p.fuentes == {"AIRSPEED BARBER POLE": "vmax"}
         and p.lvars == {"vmax": ("L:I_PFD_VMAX", "Knots")},
         f"con L:var {con['AIRSPEED BARBER POLE']} / sin {sin['AIRSPEED BARBER POLE']} / fuentes {p.fuentes}")

    incluidos = perfiles.cargar()
    malos = [x.nombre for x in incluidos if any(a not in x.lvars for a in x.fuentes.values())]
    caso("perfiles incluidos válidos", len(incluidos) >= 2 and not malos,
         f"{len(incluidos)} perfiles, inválidos {malos}")


def _propios(caso: Callable, correr: Callable, CFG: dict) -> None:
    import copy

    from efectos import Efectos
    from efectos_propios import EfectoPropio, Evaluador, vista_previa

    malos = {"umbral": EfectoPropio(umbral=(300.0, 250.0)),
             "curva": EfectoPropio(curva=[(0.5, 0.0), (0.2, 1.0)]),
             "hz": EfectoPropio(forma="seno", hz=30.0),
             "lvar": EfectoPropio(fuente="L:MI VAR", unidad="Number")}
    errores = {k: v.validar() for k, v in malos.items()}
    caso("editor rechaza efectos mal armados", all(errores.values()) and not EfectoPropio().validar(), f"{errores}")

    ev = Evaluador(EfectoPropio(fuente="AIRSPEED INDICATED", disparo="sobre", umbral=(250.0, 300.0), intensidad=1.0))
    v275, v240 = ev.valor({"AIRSPEED INDICATED": 275.0}, 0.0, 0.02), ev.valor({"AIRSPEED INDICATED": 240.0}, 0.02, 0.02)
    caso("efecto propio lineal", abs(v275 - 0.5) < 1e-6 and v240 == 0, f"275 kt {v275:.2f} / 240 kt {v240:.2f}")

    e = EfectoPropio(nombre="Prueba", curva=[(0.0, 0.1), (0.4, 0.7), (1.0, 1.0)], forma="pulso", hz=4.0)
    caso("exportar e importar es idéntico", EfectoPropio.desde_dict(e.a_dict()) == e, "ida y vuelta")

    def con(cfg_extra: dict) -> dict:
        c = copy.deepcopy(CFG)
        for k, v in cfg_extra.items():
            c[k] = v
        return c
    alta = {"SIM ON GROUND": 0, "AIRSPEED INDICATED": 360, "AIRSPEED BARBER POLE": 350, "GEAR CENTER POSITION": 0}
    _, s_norm, _ = correr(alta, 1.0, Efectos(CFG))
    _, s_nada, _ = correr(alta, 1.0, Efectos(con({"ruteo": {"sobrevelocidad": "ninguno"}})))
    _, s_cero, _ = correr(alta, 1.0, Efectos(con({"intensidad_efecto": {"sobrevelocidad": 0.0}})))
    caso("ruteo e intensidad por efecto", s_norm["throttle_1"] > 10 and s_nada["throttle_1"] == 0
         and s_cero["throttle_1"] == 0, f"normal {s_norm['throttle_1']:.0f} / ninguno {s_nada['throttle_1']:.0f} / "
         f"intensidad 0 {s_cero['throttle_1']:.0f}")

    nunca = EfectoPropio(nombre="Mía", fuente="AIRSPEED INDICATED", umbral=(900.0, 1000.0), reemplaza="sobrevelocidad")
    mx_r, s_r, _ = correr(alta, 1.0, Efectos(con({"efectos_propios": [nunca.a_dict()]})))
    caso("efecto propio reemplaza al incorporado", mx_r["sobrevelocidad"] == 0 and s_r["throttle_1"] == 0,
         f"sobrevelocidad {mx_r['sobrevelocidad']} / throttle {s_r['throttle_1']:.0f}")

    suelo = EfectoPropio(nombre="Suelo", fuente="GROUND VELOCITY", umbral=(5.0, 30.0), intensidad=0.8, ruteo="throttle")
    _, s_base, _ = correr({"GROUND VELOCITY": 20}, 1.0, Efectos(CFG))
    _, s_suma, _ = correr({"GROUND VELOCITY": 20}, 1.0, Efectos(con({"efectos_propios": [suelo.a_dict()]})))
    caso("efecto propio suma a su dispositivo", s_suma["throttle_1"] > s_base["throttle_1"] + 20
         and abs(s_suma["joystick"] - s_base["joystick"]) < 1,
         f"throttle {s_base['throttle_1']:.0f} -> {s_suma['throttle_1']:.0f} / joystick {s_base['joystick']:.0f} -> "
         f"{s_suma['joystick']:.0f}")

    rampa = EfectoPropio(fuente="GROUND VELOCITY", umbral=(0.0, 10.0), intensidad=0.6)
    prev = vista_previa(rampa, [0.0] * 10 + [10.0] * 40, CFG)
    zm = CFG["zona_muerta"]["throttle"]
    caso("vista previa = salida real", max(prev[:10]) == 0 and min(prev[15:]) > zm,
         f"antes {prev[:3]} / después {prev[-3:]}")


def _probar_en_dispositivo(caso: Callable) -> None:
    from efectos_propios import EfectoPropio, serie_prueba
    from motor_vibracion import Vibracion
    boole = serie_prueba(EfectoPropio(disparo="booleano"), 3.0)
    bajo = serie_prueba(EfectoPropio(disparo="bajo", umbral=(10.0, 20.0)), 1.0)
    caso("serie de prueba recorre el umbral", boole[0] == 1 and boole[60] == 0 and boole[110] == 1
         and bajo[0] == 20.0 and bajo[-1] < 20.0,
         f"booleano {boole[0]}/{boole[60]}/{boole[110]}, bajo {bajo[0]}->{bajo[-1]:.1f}")
    v = Vibracion(silencio=True)
    v.probar(EfectoPropio(fuente="GROUND VELOCITY", umbral=(0.0, 10.0), intensidad=0.7, ruteo="throttle"), 2.0)
    caso("probar en el dispositivo", len(v._prueba) == 100 and max(x["throttle_1"] for x in v._prueba) > 0
         and max(x["joystick"] for x in v._prueba) == 0,
         f"{len(v._prueba)} ticks, throttle máx {max(x['throttle_1'] for x in v._prueba)}")


def _grabacion(caso: Callable) -> None:
    from efectos_propios import valores_de_grabacion
    frames = [{"t": 0.0, "d": {"A": 1.0}}, {"t": 0.1, "d": {"A": 2.0}}, {"t": 0.2, "d": {"LVAR:B": 5.0, "A": 3.0}}]
    va, vb = valores_de_grabacion(frames, "A"), valores_de_grabacion(frames, "B")
    caso("grabación remuestreada a 50 Hz", len(va) == 11 and va[0] == 1.0 and va[5] == 2.0 and va[10] == 3.0
         and vb[10] == 5.0, f"A {va} / B {vb[-1]}")


def _config_en_vivo(caso: Callable) -> None:
    """Lo que la ventana guarda tiene que llegarle al lazo aunque la ventana ya haya recargado la config."""
    import tempfile
    from pathlib import Path

    import rutas
    from config_usuario import Config
    from motor_vibracion import Vibracion
    cfg = Config(rutas.config_por_defecto(), Path(tempfile.mkdtemp()) / "ajustes.json")
    v = Vibracion(silencio=True, config=cfg)
    primera = v._config_nueva()
    cfg.guardar("intensidad_efecto", "frenos", valor=0.3)      # lo hace el hilo de tk
    segunda = v._config_nueva()
    tercera = v._config_nueva()
    caso("cambio de config llega al lazo", primera and segunda and not tercera,
         f"inicio {primera} / después de guardar {segunda} / sin cambios {tercera}")


def _datos_faltantes_y_frames(caso: Callable, CFG: dict) -> None:
    """Una variable que no llegó no dispara nada, y los ticks sin frame nuevo del sim no hacen titilar derivadas."""
    from efectos import Efectos
    from efectos_propios import EfectoPropio, Evaluador
    bajo = Evaluador(EfectoPropio(fuente="L:NO_EXISTE", disparo="bajo", umbral=(0.0, 100.0), intensidad=1.0))
    v_falta = bajo.valor({}, 0.0, 0.02)
    v_llega = bajo.valor({"LVAR:L:NO_EXISTE": 50.0}, 0.02, 0.02)
    camb = Evaluador(EfectoPropio(fuente="X", disparo="mientras_cambia", umbral=(1.0, 50.0), intensidad=1.0))
    camb.valor({}, 0.0, 0.02)
    v_salto = camb.valor({"X": 1000.0}, 0.02, 0.02)
    caso("variable ausente no dispara", v_falta == 0 and v_llega > 0 and v_salto == 0,
         f"falta {v_falta} / llega {v_llega:.2f} / aparece {v_salto}")

    # Flaps a 30 fps del sim con el lazo a 50 Hz: el frame se repite cada tanto; el efecto no puede caer a 0.
    ef = Efectos(CFG)
    base = {"SIM ON GROUND": 0, "AIRSPEED INDICATED": 200, "GEAR CENTER POSITION": 0, "SURFACE TYPE": 4}
    vals = []
    for i in range(100):
        t = i * 0.02
        frame = int(t * 30)
        d = dict(base, **{"SIMULATION TIME": 500.0 + frame / 30, "TRAILING EDGE FLAPS LEFT PERCENT": frame / 30 * 0.1})
        e, _ = ef.paso(d, t)
        vals.append(e["flaps"])
    caso("flaps no titilan con frames repetidos", min(vals[10:]) > 0, f"mínimo {min(vals[10:]):.3f}")


def _paquete_lvars(caso: Callable) -> None:
    import struct

    from sim_lector import leer_valores
    cab = struct.pack("<IIIIIIIIII", 0, 6, 8, 13, 0, 12, 0, 0, 1, 3)   # ... dwDefineCount = 3
    bueno = cab + struct.pack("<ddd", 1.0, 2.0, 3.0)
    corto = cab + struct.pack("<d", 1.0)
    caso("paquete de L:vars corto se descarta", leer_valores(bueno, 3) == [1.0, 2.0, 3.0]
         and leer_valores(corto, 3) is None, f"bueno {leer_valores(bueno, 3)} / corto {leer_valores(corto, 3)}")


def _ralenti_bajo(caso: Callable, correr: Callable, CFG: dict) -> None:
    """Un motor ya en marcha con ralentí por debajo del configurado no queda con el zumbido de 'aceleración'."""
    from efectos import Efectos
    en_marcha = {"GENERAL ENG COMBUSTION:1": 1, "GENERAL ENG COMBUSTION:2": 1, "TURB ENG N1:1": 17,
                 "TURB ENG N1:2": 17}
    mx, _, _ = correr(en_marcha, 3.0, Efectos(CFG))
    caso("ralentí bajo sin zumbido de arranque", mx["motores"] < 0.06, f"motores {mx['motores']:.3f}")

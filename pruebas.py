"""Pruebas del motor de efectos con escenarios sintéticos (sin simulador ni hardware).

Uso: venv\\Scripts\\python.exe pruebas.py   → imprime cada caso y falla con AssertionError si algo no cuadra.
"""
import json
import random
from pathlib import Path

from efectos import Efectos

CFG = json.loads((Path(__file__).parent / "config.json").read_text(encoding="utf-8"))
BASE = {"SIM ON GROUND": 1, "GROUND VELOCITY": 0, "SURFACE TYPE": 4, "AIRSPEED INDICATED": 0, "VERTICAL SPEED": 0,
        "ACCELERATION BODY Y": 0, "ACCELERATION BODY Z": 0, "GEAR CENTER POSITION": 1, "TRAILING EDGE FLAPS LEFT PERCENT": 0,
        "SPOILERS LEFT POSITION": 0, "TURB ENG N1:1": 21, "TURB ENG N1:2": 21, "TURB ENG REVERSE NOZZLE PERCENT:1": 0,
        "TURB ENG REVERSE NOZZLE PERCENT:2": 0, "STALL WARNING": 0, "INCIDENCE ALPHA": 3, "BRAKE LEFT POSITION": 0,
        "BRAKE RIGHT POSITION": 0, "SIMULATION TIME": 1000.0}


def correr(cambios: dict, seg: float = 4.0, ef: Efectos | None = None, cada_paso=None) -> tuple[dict, dict, Efectos]:
    """Corre `seg` segundos a 40 Hz; devuelve (máximo por efecto, promedio de salida, motor)."""
    random.seed(1)
    ef = ef or Efectos(CFG)
    d = dict(BASE, **cambios)
    mx, tot, n = {}, {"joystick": 0, "throttle_1": 0, "throttle_2": 0}, 0
    t = getattr(ef, "_t_test", 0.0)
    for i in range(int(seg * 40)):
        t += 0.025
        d["SIMULATION TIME"] = 1000.0 + t
        if cada_paso:
            cada_paso(d, i)
        e, s = ef.paso(dict(d), t)
        for k, v in e.items():
            mx[k] = max(mx.get(k, 0.0), v)
        for k, v in s.items():
            tot[k] += v
        n += 1
    ef._t_test = t
    return mx, {k: v / n for k, v in tot.items()}, ef


def caso(nombre: str, cond: bool, detalle: str) -> None:
    print(f"{'OK ' if cond else 'MAL'} {nombre}: {detalle}")
    assert cond, nombre


# 1. Parado en tierra con motores en idle: casi nada (solo zumbido leve en el acelerador)
_, s, _ = correr({})
caso("parado", s["joystick"] < 15 and s["throttle_1"] < 40, f"salida {s}")

# 2. Carreteo 15 kt asfalto vs pasto: el pasto vibra más
# Reason: a 15 kt el rodaje ahora es casi imperceptible a propósito; se compara a 40 kt, donde ya se siente.
# Reason: se comparan los efectos (0..1), no la salida: la zona muerta suma un piso fijo que achica la proporción.
e_asf, s_asf, _ = correr({"GROUND VELOCITY": 40})
e_pas, s_pas, _ = correr({"GROUND VELOCITY": 40, "SURFACE TYPE": 1})
caso("carreteo asfalto < pasto", e_pas["rodadura"] > e_asf["rodadura"] * 1.4,
     f"asfalto {e_asf['rodadura']:.2f} / pasto {e_pas['rodadura']:.2f}")

# 3. Carrera de despegue a 130 kt vibra más que carreteo a 15
e_rap, s_rap, _ = correr({"GROUND VELOCITY": 130, "AIRSPEED INDICATED": 130, "TURB ENG N1:1": 85, "TURB ENG N1:2": 85})
caso("despegue > carreteo", e_rap["rodadura"] > e_asf["rodadura"] * 1.5,
     f"130 kt {e_rap['rodadura']:.2f} / 40 kt {e_asf['rodadura']:.2f}")

# 4. Crucero estable: nada en el joystick
_, s_cru, _ = correr({"SIM ON GROUND": 0, "GROUND VELOCITY": 450, "AIRSPEED INDICATED": 270, "GEAR CENTER POSITION": 0,
                      "TURB ENG N1:1": 82, "TURB ENG N1:2": 82})
caso("crucero sin vibración", s_cru["joystick"] < 6, f"salida {s_cru}")

# 5. Pausa: tiempo de simulación quieto → todo en cero
ef = Efectos(CFG)
correr({"GROUND VELOCITY": 130}, 1.0, ef)


def congelar(d, i):
    d["SIMULATION TIME"] = 5.0


mx, s_pau, _ = correr({"GROUND VELOCITY": 130}, 1.0, ef, congelar)
caso("pausa apaga", s_pau["joystick"] < 15, f"promedio en pausa {s_pau['joystick']:.1f} (incluye 0,3 s de margen)")

# 6. Aterrizaje: duro (-700 fpm) pega más que suave (-100 fpm)


def aterrizar(vs):
    ef = Efectos(CFG)
    correr({"SIM ON GROUND": 0, "VERTICAL SPEED": vs, "AIRSPEED INDICATED": 135, "GROUND VELOCITY": 135}, 1.0, ef)
    mx, _, _ = correr({"SIM ON GROUND": 1, "VERTICAL SPEED": 0, "AIRSPEED INDICATED": 135, "GROUND VELOCITY": 135},
                      0.3, ef)
    return mx["aterrizaje"]


suave, duro = aterrizar(-100), aterrizar(-700)
caso("aterrizaje duro > suave", duro > suave * 2, f"suave {suave:.2f} / duro {duro:.2f}")

# 7. Tren en tránsito vibra, tren arriba en crucero no


def subir_tren(d, i):
    d["GEAR CENTER POSITION"] = max(0.0, 1.0 - i / 200)


mx, _, _ = correr({"SIM ON GROUND": 0, "AIRSPEED INDICATED": 170}, 3.0, None, subir_tren)
caso("tren en tránsito", mx["tren"] > 0.15, f"máximo tren {mx['tren']:.2f}")

# 7b. Bajar el tren (8 s): dos golpes (destrabe y traba) y casi nada en el medio, no un zumbido parejo.
ef_t = Efectos(CFG)
d_t = dict(BASE, **{"SIM ON GROUND": 0, "AIRSPEED INDICATED": 170, "GEAR CENTER POSITION": 0.0})
serie_t = []
for i in range(int(10 * 40)):
    tt = (i + 1) * 0.025
    d_t["SIMULATION TIME"] = 1000 + tt
    d_t["GEAR CENTER POSITION"] = _clamp01 = min(1.0, max(0.0, (tt - 1.0) / 8.0))
    e_t, _ = ef_t.paso(dict(d_t), tt)
    serie_t.append(e_t["tren"])
picos = sum(1 for a, b in zip(serie_t, serie_t[1:]) if a < 0.2 <= b)
medio = max(serie_t[int(3 * 40):int(8 * 40)])
caso("tren: golpes al destrabar y trabar", picos == 2 and medio < 0.05,
     f"{picos} golpes, máximo en el medio del recorrido {medio:.3f}")

# 8. Speedbrake en vuelo a 300 kt vibra más que sin speedbrake
mx_sb, _, _ = correr({"SIM ON GROUND": 0, "AIRSPEED INDICATED": 300, "SPOILERS LEFT POSITION": 1.0, "GEAR CENTER POSITION": 0})
caso("speedbrake", mx_sb["speedbrake"] > 0.2, f"máximo speedbrake {mx_sb['speedbrake']:.2f}")

# 9. Reversa: el motor del acelerador de ese motor vibra
_, s_rev, _ = correr({"GROUND VELOCITY": 100, "TURB ENG N1:1": 70, "TURB ENG REVERSE NOZZLE PERCENT:1": 1.0})
caso("reversa motor 1 > motor 2", s_rev["throttle_1"] > s_rev["throttle_2"] * 1.3,
     f"motor1 {s_rev['throttle_1']:.0f} / motor2 {s_rev['throttle_2']:.0f}")

# 10. Pérdida: alpha alto en vuelo → buffet; parado con alpha 179 → nada
mx_p, _, _ = correr({"SIM ON GROUND": 0, "AIRSPEED INDICATED": 120, "INCIDENCE ALPHA": 16, "GEAR CENTER POSITION": 0})
mx_0, _, _ = correr({"INCIDENCE ALPHA": 179})
caso("pérdida", mx_p["perdida"] > 0.4 and mx_0["perdida"] == 0, f"alpha16 {mx_p['perdida']:.2f} / parado {mx_0['perdida']}")

# 11. Turbulencia: sacudones verticales reales en vuelo se sienten


def turbulencia(d, i):
    d["ACCELERATION BODY Y"] = 8.0 * random.uniform(-1, 1)


mx_t, _, _ = correr({"SIM ON GROUND": 0, "AIRSPEED INDICATED": 250, "GEAR CENTER POSITION": 0}, 3.0, None, turbulencia)
caso("turbulencia", mx_t["sacudones"] > 0.2, f"máximo sacudones {mx_t['sacudones']:.2f}")


# 12. Frenado dinámico: golpe inicial al frenar, variación fuerte (no estática), temblor más lento a baja velocidad,
#     y golpecito al detenerse.
def serie_frenado(gs_ini: float, seg: float, frenar_desde: float = 0.5):
    import statistics
    ef = Efectos(CFG)
    random.seed(2)
    d = dict(BASE, **{"GROUND VELOCITY": gs_ini})
    t, gs, serie = 0.0, gs_ini, []
    for i in range(int(seg * 40)):
        t += 0.025
        d["SIMULATION TIME"] = 1000 + t
        frenando = t >= frenar_desde and gs > 0
        d["BRAKE LEFT POSITION"] = d["BRAKE RIGHT POSITION"] = 1.0 if frenando else 0.0
        d["ACCELERATION BODY Z"] = -12.0 if frenando else 0.0
        if frenando:
            gs = max(0.0, gs - 12.0 * 0.025 / 1.688)          # 12 ft/s² ≈ 7,1 kt/s
        d["GROUND VELOCITY"] = gs
        e, _ = ef.paso(dict(d), t)
        serie.append(e["frenos"])
    return serie, statistics


serie, st = serie_frenado(120, 20.0)
inicio = max(serie[20:40])
medio = serie[80:200]
caso("frenado: golpe inicial", inicio > 0.3, f"pico al pisar el freno {inicio:.2f}")
caso("frenado: varía (no estático)", st.pstdev(medio) > 0.05, f"desvío en plena frenada {st.pstdev(medio):.3f}")


def cruces(s):
    m = sum(s) / len(s)
    return sum(1 for a, b in zip(s, s[1:]) if (a - m) * (b - m) < 0)


rapido = cruces(serie[60:100])        # ~110 kt
lento_ini = int((120 - 15) / 7.1 * 40) + 20   # cuando va por ~15 kt
lento = cruces(serie[lento_ini:lento_ini + 40])
caso("frenado: temblor más lento al frenar", lento < rapido, f"oscilaciones/s rápido {rapido} vs lento {lento}")
fin = int((120 / 7.1 + 0.5) * 40)
caso("frenado: golpecito al detenerse", max(serie[fin - 4:fin + 16]) > 0.1, f"pico al parar {max(serie[fin - 4:fin + 16]):.2f}")


# 13. Aceleración dinámica: empuje inicial al subir potencia y pulsación con variación.
def serie_aceleracion():
    import statistics
    ef = Efectos(CFG)
    random.seed(3)
    d = dict(BASE)
    t, n1, serie = 0.0, 21.0, []
    for i in range(int(12 * 40)):
        t += 0.025
        d["SIMULATION TIME"] = 1000 + t
        if t > 1.0:
            n1 = min(85.0, n1 + 15.0 * 0.025)                 # motores tomando vueltas
        d["TURB ENG N1:1"] = d["TURB ENG N1:2"] = n1
        d["ACCELERATION BODY Z"] = 7.0 if n1 > 70 else 0.0
        e, _ = ef.paso(dict(d), t)
        serie.append(e["aceleracion"])
    return serie, statistics


serie, st = serie_aceleracion()
caso("aceleración: empuje inicial", max(serie[60:200]) > 0.12, f"pico mientras toman vueltas {max(serie[60:200]):.2f}")
caso("aceleración: varía (no estática)", st.pstdev(serie[250:]) > 0.03, f"desvío acelerando {st.pstdev(serie[250:]):.3f}")

# 14. Freno casi parado (menos de 1 kt): nada de golpe.
def freno_lento(d, i):
    on = i >= 20
    d["BRAKE LEFT POSITION"] = d["BRAKE RIGHT POSITION"] = 1.0 if on else 0.0
    d["ACCELERATION BODY Z"] = -3.0 if on else 0.0


mx_l, _, _ = correr({"GROUND VELOCITY": 0.8}, 2.0, None, freno_lento)
caso("freno casi parado sin golpe", mx_l["frenos"] < 0.05, f"máximo frenos {mx_l['frenos']:.2f}")

# 15. Derrape: ruedas yendo de costado vibran; giro normal sin velocidad lateral no.
mx_d, _, _ = correr({"GROUND VELOCITY": 20, "VELOCITY BODY X": 8.0})
mx_n, _, _ = correr({"GROUND VELOCITY": 20, "VELOCITY BODY X": 1.0})
caso("derrape", mx_d["derrape"] > 0.25 and mx_n["derrape"] == 0, f"derrapando {mx_d['derrape']:.2f} / normal {mx_n['derrape']}")

# 16. Motores: puesta en marcha se siente en el throttle; ralentí deja un mínimo; motor apagado nada.
def arrancar_motor1(d, i):
    d["TURB ENG N1:1"] = min(19.0, i * 0.025 * 1.0)      # 1 %/s, como un arranque real
    d["TURB ENG N1:2"] = 0.0


_, s_arr, _ = correr({}, 12.0, None, arrancar_motor1)
_, s_idle, _ = correr({"TURB ENG N1:1": 21, "TURB ENG N1:2": 21})
_, s_off, _ = correr({"TURB ENG N1:1": 0, "TURB ENG N1:2": 0})
caso("motor: puesta en marcha", s_arr["throttle_1"] > 8 and s_arr["throttle_2"] == 0,
     f"motor1 {s_arr['throttle_1']:.0f} / motor2 {s_arr['throttle_2']:.0f}")
# Reason: con zona muerta del throttle en 20 (medida en vivo: 16 no se siente) el ralentí queda alrededor de 34.
caso("motor: mínimo en ralentí", 20 < s_idle["throttle_1"] < 45 and s_off["throttle_1"] == 0,
     f"ralentí {s_idle['throttle_1']:.0f} / apagado {s_off['throttle_1']:.0f}")

# 17. Reversa sin la variable de la tobera (FBW A320): N1 alto frenando en tierra = reversa; acelerando no.
e_rv, _, _ = correr({"GROUND VELOCITY": 90, "TURB ENG N1:1": 77, "TURB ENG N1:2": 77, "ACCELERATION BODY Z": -6.0})
e_to, _, _ = correr({"GROUND VELOCITY": 90, "TURB ENG N1:1": 85, "TURB ENG N1:2": 85, "ACCELERATION BODY Z": 6.0})
caso("reversa inferida", e_rv["reversa"] > 0.3 and e_to["reversa"] == 0,
     f"frenando con N1 77 {e_rv['reversa']:.2f} / despegando {e_to['reversa']}")

# 18. Rodaje físico (joystick): nada parado, crece con la velocidad, pasto más que pista lisa.
def rodaje_medio(cambios: dict) -> float:
    ef = Efectos(CFG)
    random.seed(4)
    vals = []
    for i in range(600):
        t = (i + 1) * 0.025
        e, _ = ef.paso(dict(BASE, **cambios, **{"SIMULATION TIME": 1000 + t}), t)
        if i > 100:
            vals.append(e["rodaje"])
    return sum(vals) / len(vals)


r0, r5, r40, r140 = (rodaje_medio({"GROUND VELOCITY": v}) for v in (0, 5, 40, 140))
rp = rodaje_medio({"GROUND VELOCITY": 20, "SURFACE TYPE": 1})
r20 = rodaje_medio({"GROUND VELOCITY": 20})
caso("rodaje físico crece con la velocidad", r0 == 0 and r5 < r40 < r140,
     f"0 kt {r0:.2f} / 5 kt {r5:.2f} / 40 kt {r40:.2f} / 140 kt {r140:.2f}")
caso("rodaje físico: pasto > pista", rp > r20 * 1.5, f"pasto {rp:.2f} / pista {r20:.2f} a 20 kt")
# 19. Cargar un vuelo (en el aire -> en tierra con el avión quieto) no es un aterrizaje.
ef = Efectos(CFG)
correr({"SIM ON GROUND": 0, "GROUND VELOCITY": 0}, 0.5, ef)
mx_c, _, _ = correr({"SIM ON GROUND": 1, "GROUND VELOCITY": 0}, 0.5, ef)
caso("carga de vuelo sin toque falso", mx_c["aterrizaje"] == 0, f"aterrizaje {mx_c['aterrizaje']}")
# 20. Aproximación (tren abajo, autothrust moviendo el N1): el throttle no tiene que pulsar prendiendo y apagando.
def aproximacion(d, i):
    d["TURB ENG N1:1"] = d["TURB ENG N1:2"] = 30 + 8 * math.sin(i * 0.025 * 2 * math.pi / 6)   # A/THR cada 6 s


import math  # noqa: E402

ef = Efectos(CFG)
random.seed(5)
d = dict(BASE, **{"SIM ON GROUND": 0, "AIRSPEED INDICATED": 140, "GROUND VELOCITY": 140, "GEAR CENTER POSITION": 1,
                  "TRAILING EDGE FLAPS LEFT PERCENT": 1.0})
saltos, prev, mx_thr = 0, 0, 0
for i in range(int(60 * 40)):
    tt = (i + 1) * 0.025
    d["SIMULATION TIME"] = 1000 + tt
    aproximacion(d, i)
    _, s = ef.paso(dict(d), tt)
    saltos += (s["throttle_1"] > 0) != (prev > 0)
    prev, mx_thr = s["throttle_1"], max(mx_thr, s["throttle_1"])
caso("aproximación sin pulsos en el throttle", saltos <= 4, f"{saltos} saltos prendido/apagado en 60 s, máximo {mx_thr}")
# 21. Idiomas: los 20 archivos cargan, tienen todas las claves del inglés y los mismos marcadores ({v}, {e}...).
import re  # noqa: E402

import i18n  # noqa: E402

base = i18n.IDIOMAS["en"]
problemas = []
for cod, datos in i18n.IDIOMAS.items():
    for seccion in ("textos", "efectos"):
        for clave, texto_en in base[seccion].items():
            texto = datos.get(seccion, {}).get(clave)
            if not texto:
                problemas.append(f"{cod}:{clave} falta")
            elif sorted(re.findall(r"{\w+}", texto)) != sorted(re.findall(r"{\w+}", texto_en)):
                problemas.append(f"{cod}:{clave} marcadores distintos")
caso("idiomas completos", len(i18n.IDIOMAS) == 20 and not problemas,
     f"{len(i18n.IDIOMAS)} idiomas, problemas: {problemas[:5]}")
# 22. Reportes: se tapan la carpeta de usuario, el usuario y el equipo antes de armar el issue.
import os  # noqa: E402

import reportes  # noqa: E402

os.environ.update(USERPROFILE=r"C:\Users\pepe.perez", USERNAME="pepe.perez", COMPUTERNAME="PC-DE-PEPE")
saneado = reportes.sanear(r"error en C:\Users\pepe.perez\AppData\x.py usuario pepe.perez equipo PC-DE-PEPE")
caso("reporte sin datos personales", "pepe" not in saneado.lower() and "PC-DE-PEPE" not in saneado, saneado)
# 23. Actualizador: falla cerrado sin SHA-256 o con una descarga que no sea de los releases del repo.
import io  # noqa: E402
import json as _json  # noqa: E402

import actualizador  # noqa: E402

BUENO = f"https://github.com/{actualizador.REPO}/releases/download/v9.9.9/VibracionURSA-Update.exe"


def respuesta(assets):
    datos = {"tag_name": "v9.9.9", "body": "", "assets": assets}

    class R(io.BytesIO):
        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False
    return lambda url, timeout: R(_json.dumps(datos).encode())


casos_act = {
    "sin sha": [{"name": "VibracionURSA-Update.exe", "browser_download_url": BUENO}],
    "url ajena": [{"name": "VibracionURSA-Update.exe", "browser_download_url": "https://evil.example/x.exe",
                   "digest": "sha256:" + "a" * 64}],
}
original = actualizador._pedir
rechazos = {}
for nombre, assets in casos_act.items():
    actualizador._pedir = respuesta(assets)
    rechazos[nombre] = actualizador._ultima_publicada() is None
actualizador._pedir = respuesta([{"name": "VibracionURSA-Update.exe", "browser_download_url": BUENO,
                                  "digest": "sha256:" + "b" * 64}])
ok = actualizador._ultima_publicada()
actualizador._pedir = original
caso("actualizador falla cerrado", all(rechazos.values()) and ok is not None and ok.url == BUENO,
     f"rechazos {rechazos} / válido {ok.numero if ok else None}")
# 24. Avión a pistón: los efectos de motor siguen las RPM (no hay N1) y frenar con RPM altas no es reversa.
piston = {"ENGINE TYPE": 0, "NUMBER OF ENGINES": 1, "TURB ENG N1:1": 0, "TURB ENG N1:2": 0,
          "GENERAL ENG PCT MAX RPM:1": 80, "GENERAL ENG PCT MAX RPM:2": 0}
e_pi, s_pi, _ = correr(piston)
e_pf, _, _ = correr(dict(piston, **{"GROUND VELOCITY": 30, "ACCELERATION BODY Z": -6.0}))
caso("pistón: motor por RPM, sin reversa", e_pi["motores"] > 0.05 and s_pi["throttle_2"] > 0 and e_pf["reversa"] == 0,
     f"motores {e_pi['motores']:.2f}, palanca 2 {s_pi['throttle_2']:.0f}, reversa frenando {e_pf['reversa']}")

# 25. Perfiles: elige por el nombre del avión; el usuario manda sobre el perfil.
import perfiles  # noqa: E402
from config_usuario import fusionar  # noqa: E402

lista = [perfiles.Perfil("iniBuilds A350", ["A350"], {"motores": {"reversa": 0.9}}),
         perfiles.Perfil("FlyByWire A320", ["A32NX", "FlyByWire A320"], {})]
p_a350 = perfiles.elegir("iniBuilds A350-900 Aerolineas Argentinas", lista)
p_nada = perfiles.elegir("Cessna 172 Skyhawk", lista)
final = fusionar(fusionar(CFG, p_a350.ajustes), {"motores": {"reversa": 0.2}})
caso("perfiles por avión", p_a350.nombre == "iniBuilds A350" and p_nada is None
     and final["motores"]["reversa"] == 0.2 and final["motores"]["zumbido_tierra"] == CFG["motores"]["zumbido_tierra"],
     f"A350 -> {p_a350.nombre}, Cessna -> {p_nada}, reversa final {final['motores']['reversa']}")

# 26. Grabador: graba, se lee igual y se puede reproducir.
import sys  # noqa: E402
import tempfile  # noqa: E402

import grabador  # noqa: E402

grabador.carpeta = lambda: Path(tempfile.mkdtemp())
g = grabador.Grabador()
arch = g.empezar("Prueba 737")
for i in range(80):
    g.escribir(g._t0 + i * 0.025, dict(BASE, **{"GROUND VELOCITY": 20.0, "SIMULATION TIME": 1000 + i * 0.025}))
g.terminar()
cab, frames = grabador.leer(arch)
sys.path.insert(0, str(Path(__file__).parent / "herramientas"))
from reproducir import reproducir  # noqa: E402

res = reproducir(arch)
caso("grabar y reproducir", cab["avion"] == "Prueba 737" and len(frames) == 80 and res["frames"] == 80
     and res["efectos"]["rodaje"]["max"] > 0, f"{len(frames)} frames, rodaje máx {res['efectos']['rodaje']['max']}")
print("\nTodas las pruebas pasaron.")

"""Lazo de vibración en un hilo propio: lee el simulador, calcula los efectos y mueve los motores a 40 Hz.

Lo usan la app de bandeja (`bandeja.py`) y la línea de comandos (`vibracion.py`). Al detenerse SIEMPRE apaga los
motores: si el proceso muere de golpe quedan girando en el último valor.
"""
from __future__ import annotations

import logging
import threading
import time
from collections import deque
from dataclasses import dataclass, field
from logging.handlers import RotatingFileHandler

import perfiles
import reportes
import rutas
from cadencia import HZ_ENVIO, Reloj, timer_fino
from config_usuario import Config, fusionar
from efectos_propios import EfectoPropio, serie_prueba, vista_previa
from efectos import EFECTOS, Efectos
from efectos_propios import cargar as cargar_propios
from grabador import Grabador
from motores import Motor
from sim_lector import VARIABLES, LectorSim

HZ = HZ_ENVIO
log = logging.getLogger("vibracion")


def configurar_log(consola: bool = False) -> None:
    if log.handlers:
        return
    log.setLevel(logging.INFO)
    fmt = logging.Formatter("%(asctime)s %(message)s", "%H:%M:%S")
    h = RotatingFileHandler(rutas.archivo_log(), maxBytes=2_000_000, backupCount=2, encoding="utf-8")
    h.setFormatter(fmt)
    log.addHandler(h)
    if consola:
        c = logging.StreamHandler()
        c.setFormatter(fmt)
        log.addHandler(c)


@dataclass
class Estado:
    conectado: bool = False
    dispositivos: list[str] = field(default_factory=list)
    activos: dict[str, float] = field(default_factory=dict)
    pausado: bool = False
    error: str = ""
    avion: str = ""     # nombre que informa el simulador (TITLE)
    perfil: str = ""    # perfil aplicado ("" = genérico)
    vivo: dict = field(default_factory=dict)   # último tick: efectos, salida y datos crudos (monitor en vivo)


class Vibracion:
    def __init__(self, silencio: bool = False, config: Config | None = None) -> None:
        self.silencio = silencio
        self.cfg = config or Config()
        self.estado = Estado()
        self._parar = threading.Event()
        self._hilo: threading.Thread | None = None
        self._motores: dict[str, Motor] = {}
        self._sim: LectorSim | None = None
        self.t_sin_sim = time.time()
        self.visto_sim = False
        self._perfiles = perfiles.cargar()
        self._perfil_ajustes: dict = {}
        self._perfil: perfiles.Perfil | None = None
        self.grabador = Grabador()
        self.historial: deque[dict[str, int]] = deque(maxlen=HZ * 10)   # salida de los últimos 10 s (monitor)
        self._prueba: list[dict[str, int]] = []
        self._propios_src: object = None
        self._gen_aplicada = -1

    def probar(self, ef: EfectoPropio, segundos: float = 5.0) -> None:
        """Hace sonar un efecto propio en el hardware durante `segundos`, tal como lo va a mandar el lazo."""
        valores = serie_prueba(ef, segundos)
        joy = vista_previa(ef, valores, self.cfg.datos, "joystick") if ef.ruteo != "throttle" else [0] * len(valores)
        thr = vista_previa(ef, valores, self.cfg.datos, "throttle") if ef.ruteo != "joystick" else [0] * len(valores)
        self._prueba = [{"joystick": j, "throttle_1": t, "throttle_2": t} for j, t in zip(joy, thr, strict=True)]

    def _pedir_variables(self, sim: LectorSim) -> None:
        """L:vars del perfil + variables que usan los efectos propios y el lector no trae por defecto."""
        pedidas = dict(self._perfil.lvars) if self._perfil else {}
        for ef in cargar_propios(self.cfg.datos.get("efectos_propios", [])):
            if ef.fuente not in VARIABLES:
                pedidas[ef.fuente] = (ef.fuente, ef.unidad)
        sim.pedir_lvars(pedidas)

    def _config_nueva(self) -> bool:
        """True si hay una configuración que el lazo todavía no aplicó (la cargue quien la cargue)."""
        self.cfg.recargar()
        if self.cfg.generacion == self._gen_aplicada:
            return False
        self._gen_aplicada = self.cfg.generacion
        return True

    def grabar(self, si: bool) -> None:
        if si:
            self.grabador.empezar(self.estado.avion)
        else:
            self.grabador.terminar()

    # ------------------------------------------------------------------ control
    def iniciar(self) -> None:
        self._sim = LectorSim()          # FileNotFoundError si falta SimConnect.dll
        self._sim.iniciar()
        self._hilo = threading.Thread(target=self._lazo, daemon=True, name="vibracion")
        self._hilo.start()

    def detener(self, espera: float = 3.0) -> None:
        self._parar.set()
        if self._hilo:
            self._hilo.join(espera)
        self.grabador.terminar()
        self._apagar_todo()

    def corriendo(self) -> bool:
        return bool(self._hilo and self._hilo.is_alive())

    def pausar(self, si: bool) -> None:
        self.estado.pausado = si
        log.info("vibración %s", "en pausa" if si else "reanudada")

    # ------------------------------------------------------------------ motores
    def _abrir_motores(self) -> None:
        for nombre in ("joystick", "throttle"):
            if nombre in self._motores:
                continue
            try:
                self._motores[nombre] = Motor(nombre)
            except Exception as ex:  # noqa: BLE001  (no enchufado: se reintenta cada 10 s)
                log.debug("no pude abrir el %s: %s", nombre, ex)
        self.estado.dispositivos = sorted(self._motores)

    def _apagar_todo(self) -> None:
        for m in list(self._motores.values()):
            try:
                m.cerrar()
            except Exception:  # noqa: BLE001
                pass
        self._motores.clear()
        self.estado.dispositivos = []

    # ------------------------------------------------------------------ lazo
    def _lazo(self) -> None:
        sim = self._sim
        assert sim is not None
        ef = Efectos(self.cfg.datos)
        if not self.silencio:
            self._abrir_motores()
        log.info("arrancado (%s). Motores: %s", "silencio" if self.silencio else "normal",
                 ", ".join(self._motores) or "ninguno")
        ultimo = {"joystick": -1, "throttle_1": -1, "throttle_2": -1}
        acum = {e: 0.0 for e in EFECTOS}
        t_log = t_cfg = t_reabrir = t_cadencia = time.time()
        timer_fino(True)
        reloj = Reloj(HZ, dormir=self._parar.wait)
        conectado_prev, ultimo_log = False, {}
        try:
            while not self._parar.is_set():
                t0 = time.time()
                if t0 - t_cfg > 2:
                    t_cfg = t0
                    recargo = self._config_nueva()
                    avion = sim.avion()
                    if avion != self.estado.avion:
                        self.estado.avion = avion
                        p = perfiles.elegir(avion, self._perfiles)
                        self._perfil_ajustes = p.ajustes if p else {}
                        self._perfil = p
                        self._pedir_variables(sim)
                        self.estado.perfil = p.nombre if p else ""
                        log.info("avión: %s · perfil: %s", avion or "?", self.estado.perfil or "genérico")
                        recargo = True
                    if self.cfg.datos.get("efectos_propios") is not self._propios_src:
                        self._propios_src = self.cfg.datos.get("efectos_propios")
                        self._pedir_variables(sim)
                    if recargo:
                        # defecto <- perfil del avión <- ajustes del usuario (sus intensidades siempre mandan)
                        ef.cfg = fusionar(fusionar(self.cfg.defecto, self._perfil_ajustes), self.cfg.usuario)
                        log.info("configuración aplicada")
                conectado = sim.conectado.is_set() and sim.frescura() < 1.0
                if conectado != conectado_prev:
                    log.info("simulador %s", "conectado" if conectado else "sin datos (motores apagados)")
                    conectado_prev = conectado
                self.estado.conectado = conectado
                if conectado:
                    self.visto_sim, self.t_sin_sim = True, t0
                if conectado:
                    self.grabador.escribir(t0, sim.datos())
                if conectado and not self.estado.pausado:
                    efectos, salida = ef.paso(perfiles.aplicar_fuentes(sim.datos(), self._perfil), t0)
                else:
                    efectos, salida = {e: 0.0 for e in EFECTOS}, {k: 0 for k in ultimo}
                if self._prueba:
                    salida = self._prueba.pop(0)
                self.historial.append(dict(salida))
                self.estado.vivo = {"efectos": efectos, "salida": salida,
                                    "datos": sim.datos() if conectado else {}}
                if not self.silencio:
                    if len(self._motores) < 2 and t0 - t_reabrir > 10:
                        t_reabrir = t0
                        self._abrir_motores()
                    self._escribir(salida, ultimo)
                for e in EFECTOS:
                    acum[e] = max(acum[e], efectos[e])
                if t0 - t_log >= 1.0:
                    activos = {e: round(v, 1) for e, v in acum.items() if v >= 0.02}
                    self.estado.activos = activos
                    # Reason: parado o en crucero el estado se repite cada segundo; solo se registra cuando cambia.
                    if activos and activos != ultimo_log:
                        ultimo_log = activos
                        d = sim.datos()
                        log.info("efectos %s | salida %s | gs=%.0f ias=%.0f suelo=%d sup=%d lat=%.1f n1=%.0f",
                                 activos, salida, d.get("GROUND VELOCITY", 0), d.get("AIRSPEED INDICATED", 0),
                                 int(d.get("SIM ON GROUND", 0)), int(d.get("SURFACE TYPE", -1)),
                                 d.get("VELOCITY BODY X", 0), d.get("TURB ENG N1:1", 0))
                    acum = {e: 0.0 for e in EFECTOS}
                    t_log = t0
                if t0 - t_cadencia >= 60:
                    t_cadencia = t0
                    log.info("cadencia %s", reloj.estadisticas())
                reloj.esperar()
        except Exception as ex:  # noqa: BLE001
            log.exception("error en el lazo de vibración")
            reportes.registrar_error("vibracion")
            self.estado.error = str(ex)
        finally:
            timer_fino(False)
            self._apagar_todo()
            log.info("detenido, motores apagados")

    def _escribir(self, salida: dict[str, int], ultimo: dict[str, int]) -> None:
        for clave, valor in salida.items():
            v = 0 if valor < 1 else min(255, int(round(valor)))
            if v == ultimo[clave]:
                continue
            disp = "joystick" if clave == "joystick" else "throttle"
            m = self._motores.get(disp)
            if m is None:
                continue
            try:
                if disp == "joystick":
                    m.poner(v)
                else:
                    m.poner(v, m.indices[0] if clave == "throttle_1" else m.indices[1])
                ultimo[clave] = v
            except Exception as ex:  # noqa: BLE001  (dispositivo desenchufado: se reabre)
                log.warning("error escribiendo al %s: %s", disp, ex)
                self._motores.pop(disp, None)
                ultimo[clave] = -1

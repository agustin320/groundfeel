"""Lector SimConnect mínimo (solo lectura): una conexión, un grupo de variables cada frame visual.

Se reconecta solo si el simulador se cierra o todavía no está abierto. `datos()` devuelve una copia del último frame;
`frescura()` dice hace cuántos segundos llegó (para cortar la vibración si el sim deja de mandar).
"""
from __future__ import annotations

import ctypes as C
import threading
import time

import rutas

FLOAT64, STRING256 = 4, 9
PERIODO_VISUAL_FRAME, PERIODO_SEGUNDO = 2, 4
RECV_QUIT, RECV_EVENT, RECV_SIMOBJECT_DATA = 3, 4, 8
# Pausa por eventos del sim (más rápido que esperar a que SIMULATION TIME se congele). "Pause_EX1" trae banderas
# (pausa total, activa, de simulación); "Pause" es la versión vieja (1/0). Cualquiera distinta de 0 es pausa.
EVENTOS_PAUSA = {1: b"Pause_EX1", 2: b"Pause"}
GRUPO = 10
GRUPO_AVION = 11   # nombre del avión (texto): aparte, una vez por segundo
GRUPO_LVARS = 12   # L:vars del perfil del avión: se rearma al cambiar de avión

VARIABLES: dict[str, str] = {
    "SIM ON GROUND": "Bool",
    # Contacto por pata (0 nariz, 1 izquierda, 2 derecha): el golpe de la nariz después del de las principales.
    "GEAR IS ON GROUND:0": "Bool",
    "GEAR IS ON GROUND:1": "Bool",
    "GEAR IS ON GROUND:2": "Bool",
    "GROUND VELOCITY": "Knots",
    "SURFACE TYPE": "Enum",
    "AIRSPEED INDICATED": "Knots",
    "VERTICAL SPEED": "Feet per minute",
    "ACCELERATION BODY Y": "Feet per second squared",
    "ACCELERATION BODY Z": "Feet per second squared",
    # Reason: GEAR TOTAL PCT EXTENDED devuelve escalas raras según la unidad (0.01 con el tren abajo); la posición
    # de la rueda de nariz da 0..1 limpio.
    "GEAR CENTER POSITION": "Percent over 100",
    "TRAILING EDGE FLAPS LEFT PERCENT": "Percent over 100",
    "SPOILERS LEFT POSITION": "Percent over 100",
    # Simetría: los spoilers de alabeo (un solo lado) no son freno aerodinámico.
    "SPOILERS RIGHT POSITION": "Percent over 100",
    # Slats: en algunos aviones se mueven sin los flaps.
    "LEADING EDGE FLAPS LEFT PERCENT": "Percent over 100",
    # Velocidad máxima del avión (barber pole); 0 si no la publica.
    "AIRSPEED BARBER POLE": "Knots",
    "TURB ENG N1:1": "Percent",
    "TURB ENG N1:2": "Percent",
    "TURB ENG REVERSE NOZZLE PERCENT:1": "Percent",
    "TURB ENG REVERSE NOZZLE PERCENT:2": "Percent",
    "STALL WARNING": "Bool",
    "INCIDENCE ALPHA": "Degrees",
    "BRAKE LEFT POSITION": "Percent over 100",
    "BRAKE RIGHT POSITION": "Percent over 100",
    "SIMULATION TIME": "Seconds",
    # Velocidad lateral respecto del fuselaje: en tierra, si es alta, las ruedas están derrapando.
    "VELOCITY BODY X": "Feet per second",
    # Tipo de avión (perfiles): 0 pistón, 1 jet, 2 sin motor, 3 helicóptero, 5 turbohélice.
    "ENGINE TYPE": "Enum",
    "NUMBER OF ENGINES": "Number",
    # Puesta en marcha por etapas y cuatrimotores.
    "GENERAL ENG STARTER:1": "Bool",
    "GENERAL ENG COMBUSTION:1": "Bool",
    "GENERAL ENG STARTER:2": "Bool",
    "GENERAL ENG COMBUSTION:2": "Bool",
    "GENERAL ENG STARTER:3": "Bool",
    "GENERAL ENG COMBUSTION:3": "Bool",
    "GENERAL ENG STARTER:4": "Bool",
    "GENERAL ENG COMBUSTION:4": "Bool",
    "TURB ENG N1:3": "Percent",
    "TURB ENG REVERSE NOZZLE PERCENT:3": "Percent",
    "GENERAL ENG PCT MAX RPM:3": "Percent",
    "TURB ENG N1:4": "Percent",
    "TURB ENG REVERSE NOZZLE PERCENT:4": "Percent",
    "GENERAL ENG PCT MAX RPM:4": "Percent",
    # Potencia en aviones a pistón/turbohélice (no tienen N1): % de las RPM máximas.
    "GENERAL ENG PCT MAX RPM:1": "Percent",
    "GENERAL ENG PCT MAX RPM:2": "Percent",
    # Peso real: escala la masa del tren de nariz del modelo de rodaje.
    "TOTAL WEIGHT": "Pounds",
}


def cargar_simconnect() -> C.WinDLL:
    """Carga la primera SimConnect.dll que encuentre; si no hay, explica dónde conseguirla."""
    for ruta in rutas.dll_simconnect_candidatas():
        if ruta.is_file():
            return C.WinDLL(str(ruta))
    raise FileNotFoundError(
        "No encontré SimConnect.dll. Copiala del SDK de MSFS 2024 (SimConnect SDK\\lib\\SimConnect.dll) a la carpeta "
        "recursos\\ del programa, o indicá su ruta en la variable de entorno SIMCONNECT_DLL.")


def leer_evento(raw: bytes) -> tuple[int, int]:
    """(id de evento, dato) de un SIMCONNECT_RECV_EVENT: cabecera de 12 bytes, grupo, evento, dato."""
    return int.from_bytes(raw[16:20], "little"), int.from_bytes(raw[20:24], "little")


class RECV(C.Structure):
    _fields_ = [("dwSize", C.c_uint32), ("dwVersion", C.c_uint32), ("dwID", C.c_uint32)]


class LectorSim:
    def __init__(self, nombre: bytes = b"vibracion_ursa") -> None:
        self.nombre = nombre
        self.h = C.c_void_p()
        self._vals: dict[str, float] = {}
        self._avion = ""
        self._t_ultimo = 0.0
        self._pausa: dict[int, int] = {}
        self._lvars: list[tuple[str, str, str]] = []           # (alias, nombre, unidad) registradas
        self._lvars_pedidas: list[tuple[str, str, str]] | None = None
        self._lvals: dict[str, float] = {}
        self._lock = threading.Lock()
        self.conectado = threading.Event()
        self._vars = list(VARIABLES)
        self.dll = cargar_simconnect()

    def iniciar(self) -> None:
        threading.Thread(target=self._loop, daemon=True, name="simconnect").start()

    def datos(self) -> dict[str, float]:
        with self._lock:
            d = dict(self._vals)
            if d:
                d["PAUSA"] = 1.0 if any(self._pausa.values()) else 0.0
                d.update(self._lvals)
            return d

    def pedir_lvars(self, lvars: dict[str, tuple[str, str]]) -> None:
        """Pide leer estas L:vars ({alias: (nombre, unidad)}); el hilo de SimConnect las registra en su próxima vuelta.

        Llegan en datos() como "LVAR:<alias>". Una L:var que el avión no tiene vale 0.
        """
        with self._lock:
            self._lvars_pedidas = [(a, n, u) for a, (n, u) in lvars.items()]

    def _registrar_lvars(self) -> None:
        with self._lock:
            pedidas, self._lvars_pedidas = self._lvars_pedidas, None
        if pedidas is None:
            return
        self.dll.SimConnect_ClearDataDefinition(self.h, GRUPO_LVARS)
        for i, (_, nombre, unidad) in enumerate(pedidas):
            self.dll.SimConnect_AddToDataDefinition(self.h, GRUPO_LVARS, nombre.encode(), unidad.encode(), FLOAT64,
                                                    C.c_float(0), C.c_uint32(i))
        periodo = PERIODO_VISUAL_FRAME if pedidas else 0   # 0 = NEVER: deja de pedir
        self.dll.SimConnect_RequestDataOnSimObject(self.h, GRUPO_LVARS, GRUPO_LVARS, 0, periodo, 0, 0, 0, 0)
        with self._lock:
            self._lvars, self._lvals = pedidas, {}

    def avion(self) -> str:
        """Nombre del avión cargado (TITLE), o "" si todavía no llegó."""
        with self._lock:
            return self._avion

    def frescura(self) -> float:
        return time.time() - self._t_ultimo if self._t_ultimo else 1e9

    def _loop(self) -> None:
        while True:
            try:
                hr = self.dll.SimConnect_Open(C.byref(self.h), self.nombre, None, 0, None, 0)
                if hr != 0:
                    raise ConnectionError(f"sim no disponible ({hr & 0xFFFFFFFF:#x})")
                for i, v in enumerate(self._vars):
                    self.dll.SimConnect_AddToDataDefinition(self.h, GRUPO, v.encode(), VARIABLES[v].encode(),
                                                            FLOAT64, C.c_float(0), C.c_uint32(i))
                self.dll.SimConnect_RequestDataOnSimObject(self.h, GRUPO, GRUPO, 0, PERIODO_VISUAL_FRAME, 0, 0, 0, 0)
                self.dll.SimConnect_AddToDataDefinition(self.h, GRUPO_AVION, b"TITLE", None, STRING256,
                                                        C.c_float(0), C.c_uint32(0))
                self.dll.SimConnect_RequestDataOnSimObject(self.h, GRUPO_AVION, GRUPO_AVION, 0, PERIODO_SEGUNDO,
                                                           0, 0, 0, 0)
                for ev, nombre in EVENTOS_PAUSA.items():
                    self.dll.SimConnect_SubscribeToSystemEvent(self.h, ev, nombre)
                with self._lock:          # reconexión: volver a registrar las L:vars que ya estaban pedidas
                    if self._lvars_pedidas is None and self._lvars:
                        self._lvars_pedidas = list(self._lvars)
                self.conectado.set()
                self._bombear()
            except Exception:  # noqa: BLE001  (sim cerrado o caído: se reintenta)
                pass
            self.conectado.clear()
            with self._lock:
                self._vals.clear()
                self._pausa.clear()
            try:
                self.dll.SimConnect_Close(self.h)
            except Exception:  # noqa: BLE001
                pass
            time.sleep(3)

    def _bombear(self) -> None:
        p, cb = C.POINTER(RECV)(), C.c_uint32()
        n = len(self._vars)
        while True:
            self._registrar_lvars()
            hubo = False
            while self.dll.SimConnect_GetNextDispatch(self.h, C.byref(p), C.byref(cb)) == 0 and cb.value:
                hubo = True
                raw = C.string_at(p, cb.value)
                rid = p.contents.dwID
                if rid == RECV_QUIT:
                    raise ConnectionError("el simulador se cerró")
                if rid == RECV_EVENT:
                    ev, dato = leer_evento(raw)
                    if ev in EVENTOS_PAUSA:
                        with self._lock:
                            self._pausa[ev] = dato
                    continue
                pedido = int.from_bytes(raw[12:16], "little") if rid == RECV_SIMOBJECT_DATA else -1
                if pedido == GRUPO:
                    valores = (C.c_double * n).from_buffer_copy(raw[40:40 + 8 * n])
                    with self._lock:
                        self._vals = dict(zip(self._vars, valores, strict=True))
                        self._t_ultimo = time.time()
                elif pedido == GRUPO_LVARS and self._lvars:
                    m = len(self._lvars)
                    vals = (C.c_double * m).from_buffer_copy(raw[40:40 + 8 * m])
                    with self._lock:
                        self._lvals = {f"LVAR:{a}": v for (a, _, _), v in zip(self._lvars, vals, strict=True)}
                elif pedido == GRUPO_AVION:
                    titulo = raw[40:40 + 256].split(b"\0", 1)[0].decode("utf-8", errors="replace").strip()
                    with self._lock:
                        self._avion = titulo
            if not hubo:
                time.sleep(0.004)

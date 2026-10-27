"""Lector SimConnect mínimo (solo lectura): una conexión, un grupo de variables cada frame visual.

Se reconecta solo si el simulador se cierra o todavía no está abierto. `datos()` devuelve una copia del último frame;
`frescura()` dice hace cuántos segundos llegó (para cortar la vibración si el sim deja de mandar).
"""
from __future__ import annotations

import ctypes as C
import threading
import time

import rutas

FLOAT64 = 4
PERIODO_VISUAL_FRAME = 2
RECV_QUIT, RECV_SIMOBJECT_DATA = 3, 8
GRUPO = 10

VARIABLES: dict[str, str] = {
    "SIM ON GROUND": "Bool",
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
}


def cargar_simconnect() -> C.WinDLL:
    """Carga la primera SimConnect.dll que encuentre; si no hay, explica dónde conseguirla."""
    for ruta in rutas.dll_simconnect_candidatas():
        if ruta.is_file():
            return C.WinDLL(str(ruta))
    raise FileNotFoundError(
        "No encontré SimConnect.dll. Copiala del SDK de MSFS 2024 (SimConnect SDK\\lib\\SimConnect.dll) a la carpeta "
        "recursos\\ del programa, o indicá su ruta en la variable de entorno SIMCONNECT_DLL.")


class RECV(C.Structure):
    _fields_ = [("dwSize", C.c_uint32), ("dwVersion", C.c_uint32), ("dwID", C.c_uint32)]


class LectorSim:
    def __init__(self, nombre: bytes = b"vibracion_ursa") -> None:
        self.nombre = nombre
        self.h = C.c_void_p()
        self._vals: dict[str, float] = {}
        self._t_ultimo = 0.0
        self._lock = threading.Lock()
        self.conectado = threading.Event()
        self._vars = list(VARIABLES)
        self.dll = cargar_simconnect()

    def iniciar(self) -> None:
        threading.Thread(target=self._loop, daemon=True, name="simconnect").start()

    def datos(self) -> dict[str, float]:
        with self._lock:
            return dict(self._vals)

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
                self.conectado.set()
                self._bombear()
            except Exception:  # noqa: BLE001  (sim cerrado o caído: se reintenta)
                pass
            self.conectado.clear()
            with self._lock:
                self._vals.clear()
            try:
                self.dll.SimConnect_Close(self.h)
            except Exception:  # noqa: BLE001
                pass
            time.sleep(3)

    def _bombear(self) -> None:
        p, cb = C.POINTER(RECV)(), C.c_uint32()
        n = len(self._vars)
        while True:
            hubo = False
            while self.dll.SimConnect_GetNextDispatch(self.h, C.byref(p), C.byref(cb)) == 0 and cb.value:
                hubo = True
                raw = C.string_at(p, cb.value)
                rid = p.contents.dwID
                if rid == RECV_QUIT:
                    raise ConnectionError("el simulador se cerró")
                if rid == RECV_SIMOBJECT_DATA and int.from_bytes(raw[12:16], "little") == GRUPO:
                    valores = (C.c_double * n).from_buffer_copy(raw[40:40 + 8 * n])
                    with self._lock:
                        self._vals = dict(zip(self._vars, valores, strict=True))
                        self._t_ultimo = time.time()
            if not hubo:
                time.sleep(0.004)

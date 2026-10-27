"""Control de los motores de vibración WinWing (URSA MINOR 32 Joystick L y Throttle Metal R) por HID.

Protocolo (el mismo que usa SimAppPro2 para "luces" y motores, verificado contra el código abierto de
ursa-minor-ffb, licencia MIT): reporte 0x02 + [id de pieza LE (2 bytes), 00, 00, 03, 49, índice, valor].
- Joystick L: pieza 48903 (0xBF07), motor índice 0, reporte de 14 bytes.
- Throttle Metal R: pieza 47376 (0xB910), motores índice 14 y 16, reporte de 64 bytes.
"""
from __future__ import annotations

import threading
import time

import hid

VID = 0x4098
PID_JOYSTICK = 0xBC27
PID_THROTTLE = 0xB930

DISPOSITIVOS = {
    "joystick": {"pid": PID_JOYSTICK, "pieza": 48903, "motores": [0]},
    "throttle": {"pid": PID_THROTTLE, "pieza": 47376, "motores": [14, 16]},
}


def trama(pieza: int, indice: int, valor: int, largo: int) -> list[int]:
    """Arma el reporte HID de salida para una salida (motor/luz) de una pieza."""
    cuerpo = [pieza & 0xFF, pieza >> 8, 0x00, 0x00, 0x03, 0x49, indice, max(0, min(255, int(valor)))]
    buf = [0x02] + cuerpo
    return buf + [0] * (largo - len(buf))


class Motor:
    """Un dispositivo con uno o más motores. Solo escribe cuando cambia el valor (como SimAppPro)."""

    def __init__(self, nombre: str) -> None:
        cfg = DISPOSITIVOS[nombre]
        self.nombre, self.pieza, self.indices = nombre, cfg["pieza"], cfg["motores"]
        info = next((d for d in hid.enumerate(VID, cfg["pid"])), None)
        if info is None:
            raise RuntimeError(f"no encontré el {nombre} (PID 0x{cfg['pid']:04X})")
        self.dev = hid.device()
        self.dev.open_path(info["path"])
        self.largo = 14 if nombre == "joystick" else 64
        self.ultimo: dict[int, int] = {}
        self.lock = threading.Lock()

    def poner(self, valor: float, indice: int | None = None) -> None:
        """valor 0..255. indice None = todos los motores del dispositivo."""
        v = max(0, min(255, int(round(valor))))
        with self.lock:
            for i in ([indice] if indice is not None else self.indices):
                if self.ultimo.get(i) == v:
                    continue
                self.dev.write(trama(self.pieza, i, v, self.largo))
                self.ultimo[i] = v

    def apagar(self) -> None:
        self.ultimo.clear()
        self.poner(0)

    def cerrar(self) -> None:
        try:
            self.apagar()
        finally:
            self.dev.close()


if __name__ == "__main__":
    # Prueba manual: pulso corto en cada motor.
    for nombre in ("joystick", "throttle"):
        m = Motor(nombre)
        for i in m.indices:
            print(f"{nombre} motor {i}: 40% 1 s")
            m.poner(100, i)
            time.sleep(1.0)
            m.poner(0, i)
            time.sleep(0.5)
        m.cerrar()

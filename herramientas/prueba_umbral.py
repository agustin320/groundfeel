"""Mide desde qué valor empieza a sentirse cada motor (zona muerta).

Uso (con vibracion.py cerrado): python herramientas\\prueba_umbral.py joystick|throttle [espera_s]
Hace 8 golpes de 2 s con pausas de 2 s, de menor a mayor. Contá cuántos sentiste: el primero que se siente es la
zona muerta del motor; ese valor va en "zona_muerta" de config.json.
"""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from motores import Motor  # noqa: E402

VALORES = (12, 18, 24, 30, 40, 50, 65, 80)

nombre = sys.argv[1] if len(sys.argv) > 1 else "joystick"
espera = float(sys.argv[2]) if len(sys.argv) > 2 else 2.0
m = Motor(nombre)
try:
    m.apagar()
    time.sleep(espera)
    for v in VALORES:
        print(f"{time.strftime('%H:%M:%S')} valor {v}", flush=True)
        m.poner(v)
        time.sleep(2.0)
        m.poner(0)
        time.sleep(2.0)
finally:
    m.cerrar()

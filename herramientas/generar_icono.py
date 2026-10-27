"""Genera recursos/icono.ico (palanca con ondas de vibración). Uso: python herramientas\\generar_icono.py"""
from pathlib import Path

from PIL import Image, ImageDraw

RAIZ = Path(__file__).resolve().parent.parent
N = 256


def dibujar() -> Image.Image:
    im = Image.new("RGBA", (N, N), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((8, 8, N - 8, N - 8), radius=56, fill=(22, 36, 71, 255))
    blanco, celeste = (240, 244, 250, 255), (90, 170, 255, 255)
    # Base y palanca.
    d.rounded_rectangle((78, 186, 178, 214), radius=12, fill=blanco)
    d.line((128, 190, 128, 96), fill=blanco, width=18)
    d.ellipse((100, 60, 156, 116), fill=blanco)
    # Ondas de vibración a los costados.
    for r, ancho in ((52, 10), (80, 10)):
        caja = (128 - r, 88 - r, 128 + r, 88 + r)
        d.arc(caja, 200, 250, fill=celeste, width=ancho)
        d.arc(caja, 290, 340, fill=celeste, width=ancho)
    return im


if __name__ == "__main__":
    destino = RAIZ / "recursos" / "icono.ico"
    destino.parent.mkdir(exist_ok=True)
    dibujar().save(destino, sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
    print(f"listo: {destino}")

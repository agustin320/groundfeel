"""Verifica los enlaces internos de los .md del repo: archivos relativos que existan y anclas (#...) que existan.

Uso: python herramientas\\chequear_links.py   → lista los enlaces rotos y sale con código 1 si hay alguno.
Las anclas se calculan como GitHub: minúsculas, sin puntuación (salvo - y _), espacios → guiones.
"""
from __future__ import annotations

import re
import sys
import unicodedata
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
LINK = re.compile(r"\]\(([^)\s]+)\)")


def ancla(titulo: str) -> str:
    t = titulo.strip().lower()
    t = "".join(c for c in t if unicodedata.category(c)[0] in "LN" or c in " -_")
    return t.replace(" ", "-")


def anclas(md: Path) -> set[str]:
    texto = re.sub(r"```.*?```", "", md.read_text(encoding="utf-8"), flags=re.S)
    return {ancla(m.group(1)) for m in re.finditer(r"^#{1,6}\s+(.+)$", texto, flags=re.M)}


def rotos() -> list[str]:
    out = []
    for md in sorted(RAIZ.rglob("*.md")):
        if any(p in md.parts for p in ("venv", "build", "dist", "node_modules", ".git")):
            continue
        texto = re.sub(r"```.*?```", "", md.read_text(encoding="utf-8"), flags=re.S)
        for destino in LINK.findall(texto):
            if destino.startswith(("http://", "https://", "mailto:", "../../")):
                continue
            ruta, _, frag = destino.partition("#")
            objetivo = (md.parent / ruta).resolve() if ruta else md
            if not objetivo.exists():
                out.append(f"{md.relative_to(RAIZ)}: no existe {destino}")
            elif frag and objetivo.suffix == ".md" and frag.lower() not in anclas(objetivo):
                out.append(f"{md.relative_to(RAIZ)}: no existe el ancla {destino}")
    return out


if __name__ == "__main__":
    malos = rotos()
    print("\n".join(malos) or "sin enlaces rotos")
    sys.exit(1 if malos else 0)

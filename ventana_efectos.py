"""Ventana "Efectos" (tkinter, se abre desde Ajustes): tres pestañas.

- Efectos: una tarjeta por efecto incorporado con su intensidad, a qué dispositivo va (ruteo) y una barra en vivo.
- Monitor: lo que sale a cada motor en los últimos 10 s y las variables del simulador, en vivo.
- Mis efectos: el editor de efectos propios (efectos_propios.py), con la vista previa de lo que realmente recibe el
  motor, "Probar en el dispositivo", reproducir una grabación, plantillas y exportar/importar JSON.

Todo se guarda en ajustes.json y el lazo lo toma en menos de 2 segundos.
"""
from __future__ import annotations

import json
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

import grabador
import i18n
from efectos import EFECTOS
from efectos_propios import (DISPAROS, F_MAX_HZ, FORMAS, MEZCLAS, PLANTILLAS, RUTEOS, EfectoPropio, serie_prueba,
                             valores_de_grabacion, vista_previa)
from i18n import t
from motor_vibracion import HZ, Vibracion
from sim_lector import VARIABLES

RUTEO_EFECTO = ("ambos", "joystick", "throttle", "ninguno")
COLORES = {"joystick": "#0969da", "throttle_1": "#1a7f37", "throttle_2": "#9a6700"}
FONDO, GRILLA = "#ffffff", "#d0d7de"


class VentanaEfectos:
    def __init__(self, padre: tk.Misc, vib: Vibracion) -> None:
        self.vib, self.cfg = vib, vib.cfg
        self.top = tk.Toplevel(padre)
        self.top.title(t("ve_titulo"))
        self.top.resizable(False, False)
        cuaderno = ttk.Notebook(self.top, padding=8)
        cuaderno.grid()
        self.cuaderno = cuaderno
        self.pag_efectos = ttk.Frame(cuaderno, padding=10)
        self.pag_monitor = ttk.Frame(cuaderno, padding=10)
        self.pag_propios = ttk.Frame(cuaderno, padding=10)
        cuaderno.add(self.pag_efectos, text=t("ve_tab_efectos"))
        cuaderno.add(self.pag_monitor, text=t("ve_tab_monitor"))
        cuaderno.add(self.pag_propios, text=t("ve_tab_propios"))
        self._armar_efectos()
        self._armar_monitor()
        self._armar_propios()
        self._tarea: str | None = None
        self.top.protocol("WM_DELETE_WINDOW", self.cerrar)
        self._refrescar()

    # ================================================================== pestaña Efectos
    def _armar_efectos(self) -> None:
        p = self.pag_efectos
        for col, txt in enumerate(("", t("ve_intensidad"), t("ep_ruteo"), "")):
            ttk.Label(p, text=txt, foreground="#666").grid(row=0, column=col, sticky="w", padx=4)
        nombres_ruteo = [t("ve_ruteo_" + r) for r in RUTEO_EFECTO]
        self._barras: dict[str, tk.Canvas] = {}
        for fila, e in enumerate(EFECTOS, start=1):
            ttk.Label(p, text=i18n.efecto(e).capitalize()).grid(row=fila, column=0, sticky="w", padx=4, pady=2)
            var = tk.DoubleVar(value=float(self.cfg.datos.get("intensidad_efecto", {}).get(e, 1.0)))
            lbl = ttk.Label(p, width=5, anchor="e")
            esc = ttk.Scale(p, from_=0.0, to=2.0, variable=var, length=180)
            esc.grid(row=fila, column=1, padx=4)
            lbl.grid(row=fila, column=2, sticky="w")

            def mostrar(*_a: object, v: tk.DoubleVar = var, lb: ttk.Label = lbl) -> None:
                lb.config(text=f"{v.get() * 100:.0f} %")
            var.trace_add("write", mostrar)
            mostrar()
            esc.bind("<ButtonRelease-1>",
                     lambda _e, ef=e, v=var: self.cfg.guardar("intensidad_efecto", ef, valor=round(v.get(), 2)))
            combo = ttk.Combobox(p, values=nombres_ruteo, state="readonly", width=10)
            actual = self.cfg.datos.get("ruteo", {}).get(e, "ambos")
            combo.current(RUTEO_EFECTO.index(actual) if actual in RUTEO_EFECTO else 0)
            combo.grid(row=fila, column=3, padx=4)
            combo.bind("<<ComboboxSelected>>",
                       lambda _e, ef=e, c=combo: self.cfg.guardar("ruteo", ef, valor=RUTEO_EFECTO[c.current()]))
            barra = tk.Canvas(p, width=90, height=10, bg=FONDO, highlightthickness=1, highlightbackground=GRILLA)
            barra.grid(row=fila, column=4, padx=6)
            self._barras[e] = barra

    # ================================================================== pestaña Monitor
    def _armar_monitor(self) -> None:
        p = self.pag_monitor
        ttk.Label(p, text=t("ve_salida")).grid(row=0, column=0, sticky="w")
        self.scope = tk.Canvas(p, width=520, height=180, bg=FONDO, highlightthickness=1, highlightbackground=GRILLA)
        self.scope.grid(row=1, column=0, pady=(4, 2))
        leyenda = ttk.Frame(p)
        leyenda.grid(row=2, column=0, sticky="w")
        for i, (k, color) in enumerate(COLORES.items()):
            nombre = "Joystick" if k == "joystick" else f"Throttle {k[-1]}"
            tk.Label(leyenda, text="■ " + nombre, fg=color).grid(row=0, column=i, padx=(0, 12))
        ttk.Label(p, text=t("ve_datos")).grid(row=3, column=0, sticky="w", pady=(10, 0))
        self.txt_datos = tk.Text(p, width=70, height=12, font=("Consolas", 9), relief="flat", bg="#f6f8fa")
        self.txt_datos.grid(row=4, column=0, pady=(4, 0))

    def _dibujar_scope(self) -> None:
        c, hist = self.scope, list(self.vib.historial)
        c.delete("all")
        w, h = 520, 180
        for v in (0, 64, 128, 192, 255):
            y = h - 4 - v / 255 * (h - 8)
            c.create_line(0, y, w, y, fill=GRILLA)
        n = HZ * 10
        for clave, color in COLORES.items():
            pts = []
            for i, s in enumerate(hist[-n:]):
                pts += [i / n * w, h - 4 - s.get(clave, 0) / 255 * (h - 8)]
            if len(pts) >= 4:
                c.create_line(*pts, fill=color, width=1.5)

    def _mostrar_datos(self) -> None:
        datos = self.vib.estado.vivo.get("datos", {})
        texto = "\n".join(f"{k:<36} {v:>12.3f}" for k, v in sorted(datos.items())) if datos else t("ve_sin_sim")
        self.txt_datos.delete("1.0", "end")
        self.txt_datos.insert("1.0", texto)

    # ================================================================== pestaña Mis efectos
    def _propios(self) -> list[dict]:
        return list(self.cfg.datos.get("efectos_propios", []))

    def _armar_propios(self) -> None:
        p = self.pag_propios
        izq = ttk.Frame(p)
        izq.grid(row=0, column=0, sticky="ns", padx=(0, 12))
        self.lista = tk.Listbox(izq, width=22, height=14, exportselection=False)
        self.lista.grid(row=0, column=0, columnspan=2)
        self.lista.bind("<<ListboxSelect>>", lambda _e: self._cargar_seleccion())
        ttk.Button(izq, text=t("ep_nuevo"), command=lambda: self._editar(EfectoPropio())).grid(row=1, column=0,
                                                                                                 sticky="ew")
        ttk.Button(izq, text=t("ep_borrar"), command=self._borrar).grid(row=1, column=1, sticky="ew")
        plantillas = ttk.Menubutton(izq, text=t("ep_plantilla"))
        menu = tk.Menu(plantillas, tearoff=False)
        for clave, ef in PLANTILLAS.items():
            menu.add_command(label=t("ep_p_" + clave),
                             command=lambda e=ef: self._editar(EfectoPropio.desde_dict(e.a_dict())))
        plantillas["menu"] = menu
        plantillas.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(4, 0))
        ttk.Button(izq, text=t("ep_importar"), command=self._importar).grid(row=3, column=0, sticky="ew", pady=4)
        ttk.Button(izq, text=t("ep_exportar"), command=self._exportar).grid(row=3, column=1, sticky="ew", pady=4)

        f = self.form = ttk.Frame(p)
        f.grid(row=0, column=1, sticky="n")
        self.v: dict[str, tk.Variable] = {}

        def campo(fila: int, clave: str, widget: tk.Widget) -> None:
            ttk.Label(f, text=t("ep_" + clave)).grid(row=fila, column=0, sticky="w", pady=2)
            widget.grid(row=fila, column=1, columnspan=3, sticky="w", pady=2)

        def entrada(clave: str, ancho: int = 30) -> ttk.Entry:
            self.v[clave] = tk.StringVar()
            return ttk.Entry(f, textvariable=self.v[clave], width=ancho)

        def combo(clave: str, opciones: tuple[str, ...], prefijo: str, ancho: int = 16) -> ttk.Combobox:
            cb = ttk.Combobox(f, values=[t(prefijo + o) for o in opciones], state="readonly", width=ancho)
            cb.opciones = opciones  # type: ignore[attr-defined]
            cb.bind("<<ComboboxSelected>>", lambda _e: self._previa())
            return cb

        campo(0, "nombre", entrada("nombre"))
        self.cb_fuente = ttk.Combobox(f, values=sorted(VARIABLES), width=40)
        self.cb_fuente.bind("<<ComboboxSelected>>", lambda _e: self._fuente_elegida())
        campo(1, "fuente", self.cb_fuente)
        campo(2, "unidad", entrada("unidad", 18))
        self.cb_disparo = combo("disparo", DISPAROS, "ep_d_")
        campo(3, "disparo", self.cb_disparo)
        umb = ttk.Frame(f)
        self.v["min"], self.v["max"], self.v["histeresis"] = tk.StringVar(), tk.StringVar(), tk.StringVar()
        for i, k in enumerate(("min", "max", "histeresis")):
            ttk.Entry(umb, textvariable=self.v[k], width=9).grid(row=0, column=i, padx=(0, 6))
            self.v[k].trace_add("write", lambda *_a: self._previa())
        campo(4, "umbral", umb)
        self.curva_cv = tk.Canvas(f, width=260, height=130, bg=FONDO, highlightthickness=1,
                                  highlightbackground=GRILLA)
        campo(5, "curva", self.curva_cv)
        self.curva_cv.bind("<Button-1>", self._curva_click)
        self.curva_cv.bind("<B1-Motion>", self._curva_arrastre)
        self.curva_cv.bind("<Button-3>", self._curva_borrar)
        self.cb_forma = combo("forma", FORMAS, "ep_f_")
        campo(6, "forma", self.cb_forma)
        self.v["hz"], self.v["intensidad"] = tk.DoubleVar(value=5.0), tk.DoubleVar(value=0.5)
        for fila, k, hasta in ((7, "hz", F_MAX_HZ), (8, "intensidad", 1.0)):
            caja = ttk.Frame(f)
            esc = ttk.Scale(caja, from_=0.0 if k == "intensidad" else 0.5, to=hasta, variable=self.v[k], length=200,
                            command=lambda _x: self._previa())
            esc.grid(row=0, column=0)
            lbl = ttk.Label(caja, width=8)
            lbl.grid(row=0, column=1, padx=6)

            def mostrar(*_a: object, k: str = k, lbl: ttk.Label = lbl) -> None:
                v = float(self.v[k].get())
                lbl.config(text=f"{v:.1f} Hz" if k == "hz" else f"{v * 100:.0f} %")
            self.v[k].trace_add("write", mostrar)
            mostrar()
            campo(fila, k, caja)
        self.cb_ruteo = combo("ruteo", RUTEOS, "ve_ruteo_")
        campo(9, "ruteo", self.cb_ruteo)
        self.cb_mezcla = combo("mezcla", MEZCLAS, "ep_m_")
        campo(10, "mezcla", self.cb_mezcla)
        self.cb_reemplaza = ttk.Combobox(f, values=[t("ep_ninguno")] + [i18n.efecto(e) for e in EFECTOS],
                                         state="readonly", width=16)
        campo(11, "reemplaza", self.cb_reemplaza)
        self.v["activo"] = tk.BooleanVar(value=True)
        campo(12, "activo", ttk.Checkbutton(f, variable=self.v["activo"]))
        ttk.Label(f, text=t("ep_vista")).grid(row=13, column=0, columnspan=4, sticky="w", pady=(8, 0))
        self.previa_cv = tk.Canvas(f, width=360, height=90, bg=FONDO, highlightthickness=1, highlightbackground=GRILLA)
        self.previa_cv.grid(row=14, column=0, columnspan=4, sticky="w")
        self.lbl_msg = ttk.Label(f, foreground="#cf222e", wraplength=360)
        self.lbl_msg.grid(row=15, column=0, columnspan=4, sticky="w")
        bots = ttk.Frame(f)
        bots.grid(row=16, column=0, columnspan=4, sticky="e", pady=(6, 0))
        ttk.Button(bots, text=t("ep_replay"), command=self._replay).grid(row=0, column=0, padx=2)
        ttk.Button(bots, text=t("ep_probar"), command=self._probar).grid(row=0, column=1, padx=2)
        ttk.Button(bots, text=t("ep_guardar"), command=self._guardar).grid(row=0, column=2, padx=2)
        self._indice: int | None = None
        self._curva: list[tuple[float, float]] = []
        self._arrastrando: int | None = None
        self._replay_valores: list[float] | None = None
        self._recargar_lista()
        self._editar(EfectoPropio())

    # ------------------------------------------------------------------ formulario <-> EfectoPropio
    def _editar(self, ef: EfectoPropio, indice: int | None = None) -> None:
        self._indice, self._replay_valores = indice, None
        self.v["nombre"].set(ef.nombre)
        self.cb_fuente.set(ef.fuente)
        self.v["unidad"].set(ef.unidad)
        for cb, valor in ((self.cb_disparo, ef.disparo), (self.cb_forma, ef.forma), (self.cb_ruteo, ef.ruteo),
                          (self.cb_mezcla, ef.mezcla)):
            cb.current(cb.opciones.index(valor))  # type: ignore[attr-defined]
        self.v["min"].set(f"{ef.umbral[0]:g}")
        self.v["max"].set(f"{ef.umbral[1]:g}")
        self.v["histeresis"].set(f"{ef.histeresis:g}")
        self.v["hz"].set(ef.hz)
        self.v["intensidad"].set(ef.intensidad)
        self.cb_reemplaza.current(EFECTOS.index(ef.reemplaza) + 1 if ef.reemplaza in EFECTOS else 0)
        self.v["activo"].set(ef.activo)
        self._curva = list(ef.curva)
        self._dibujar_curva()
        self._previa()

    def _leer(self) -> EfectoPropio:
        def num(k: str) -> float:
            try:
                return float(str(self.v[k].get()).replace(",", "."))
            except ValueError:
                return float("nan")
        i = self.cb_reemplaza.current()
        return EfectoPropio(
            nombre=self.v["nombre"].get().strip() or "?", fuente=self.cb_fuente.get().strip(),
            unidad=self.v["unidad"].get().strip(), disparo=DISPAROS[self.cb_disparo.current()],
            umbral=(num("min"), num("max")), histeresis=num("histeresis") if num("histeresis") == num("histeresis")
            else 0.0, curva=list(self._curva), forma=FORMAS[self.cb_forma.current()],
            hz=round(float(self.v["hz"].get()), 1), intensidad=round(float(self.v["intensidad"].get()), 2),
            ruteo=RUTEOS[self.cb_ruteo.current()], mezcla=MEZCLAS[self.cb_mezcla.current()],
            reemplaza=EFECTOS[i - 1] if i > 0 else "", activo=bool(self.v["activo"].get()))

    def _fuente_elegida(self) -> None:
        if self.cb_fuente.get() in VARIABLES:
            self.v["unidad"].set(VARIABLES[self.cb_fuente.get()])
        self._previa()

    # ------------------------------------------------------------------ curva
    def _a_px(self, x: float, y: float) -> tuple[float, float]:
        return 8 + x * 244, 122 - y * 114

    def _de_px(self, px: float, py: float) -> tuple[float, float]:
        return min(1.0, max(0.0, (px - 8) / 244)), min(1.0, max(0.0, (122 - py) / 114))

    def _dibujar_curva(self) -> None:
        c = self.curva_cv
        c.delete("all")
        for g in (0.25, 0.5, 0.75):
            x, y = self._a_px(g, g)
            c.create_line(x, 8, x, 122, fill=GRILLA)
            c.create_line(8, y, 252, y, fill=GRILLA)
        pts = [v for p in self._curva for v in self._a_px(*p)]
        c.create_line(*pts, fill="#0969da", width=2)
        for x, y in self._curva:
            px, py = self._a_px(x, y)
            c.create_oval(px - 4, py - 4, px + 4, py + 4, fill="#0969da", outline="")

    def _punto_cercano(self, px: float, py: float) -> int | None:
        for i, p in enumerate(self._curva):
            qx, qy = self._a_px(*p)
            if abs(qx - px) < 8 and abs(qy - py) < 8:
                return i
        return None

    def _curva_click(self, ev: tk.Event) -> None:
        i = self._punto_cercano(ev.x, ev.y)
        if i is None and len(self._curva) < 8:
            x, y = self._de_px(ev.x, ev.y)
            if all(abs(x - p[0]) > 0.02 for p in self._curva):
                self._curva = sorted(self._curva + [(round(x, 3), round(y, 3))])
                i = self._punto_cercano(ev.x, ev.y)
        self._arrastrando = i
        self._dibujar_curva()
        self._previa()

    def _curva_arrastre(self, ev: tk.Event) -> None:
        i = self._arrastrando
        if i is None:
            return
        x, y = self._de_px(ev.x, ev.y)
        if i == 0:
            x = 0.0
        elif i == len(self._curva) - 1:
            x = 1.0
        else:   # entre sus vecinos: la curva siempre va de izquierda a derecha
            x = min(self._curva[i + 1][0] - 0.01, max(self._curva[i - 1][0] + 0.01, x))
        self._curva[i] = (round(x, 3), round(y, 3))
        self._dibujar_curva()
        self._previa()

    def _curva_borrar(self, ev: tk.Event) -> None:
        i = self._punto_cercano(ev.x, ev.y)
        if i not in (None, 0, len(self._curva) - 1):
            del self._curva[i]
            self._dibujar_curva()
            self._previa()

    # ------------------------------------------------------------------ vista previa, probar, replay
    def _previa(self) -> None:
        ef = self._leer()
        errores = ef.validar()
        self.lbl_msg.config(text=" ".join(t(e) for e in errores), foreground="#cf222e")
        c = self.previa_cv
        c.delete("all")
        if errores:
            return
        disp = "joystick" if ef.ruteo == "joystick" else "throttle"
        valores = self._replay_valores or serie_prueba(ef, 7.0)
        salida = vista_previa(ef, valores, self.cfg.datos, disp)
        w, h = 360, 90
        zm = self.cfg.datos.get("zona_muerta", {}).get(disp, 0)
        yz = h - 4 - zm / 255 * (h - 8)
        c.create_line(0, yz, w, yz, fill="#cf222e", dash=(3, 3))
        pts = []
        for i, s in enumerate(salida):
            pts += [i / max(1, len(salida) - 1) * w, h - 4 - s / 255 * (h - 8)]
        if len(pts) >= 4:
            c.create_line(*pts, fill=COLORES["throttle_1" if disp == "throttle" else "joystick"], width=1.5)

    def _probar(self) -> None:
        ef = self._leer()
        if not ef.validar():
            self.vib.probar(ef, 5.0)

    def _replay(self) -> None:
        archivo = filedialog.askopenfilename(parent=self.top, initialdir=str(grabador.carpeta()),
                                             filetypes=[("Groundfeel", "*.jsonl.gz")])
        if not archivo:
            return
        _cab, frames = grabador.leer(archivo)
        ef = self._leer()
        self._replay_valores = valores_de_grabacion(frames, ef.fuente)
        self._previa()
        pico = max(vista_previa(ef, self._replay_valores, self.cfg.datos), default=0)
        self.lbl_msg.config(text=t("ep_replay_res", n=round(len(self._replay_valores) / HZ), p=pico),
                            foreground="#1a7f37")

    # ------------------------------------------------------------------ lista, guardar, importar, exportar
    def _recargar_lista(self) -> None:
        self.lista.delete(0, "end")
        for d in self._propios():
            self.lista.insert("end", ("" if d.get("activo", True) else "○ ") + str(d.get("nombre", "?")))

    def _cargar_seleccion(self) -> None:
        sel = self.lista.curselection()
        if sel:
            self._editar(EfectoPropio.desde_dict(self._propios()[sel[0]]), sel[0])

    def _guardar(self) -> None:
        ef = self._leer()
        errores = ef.validar()
        if errores:
            self.lbl_msg.config(text=" ".join(t(e) for e in errores), foreground="#cf222e")
            return
        lista = self._propios()
        if self._indice is None:
            lista.append(ef.a_dict())
            self._indice = len(lista) - 1
        else:
            lista[self._indice] = ef.a_dict()
        self.cfg.guardar("efectos_propios", valor=lista)
        self._recargar_lista()
        self.lbl_msg.config(text=t("ep_guardado"), foreground="#1a7f37")

    def _borrar(self) -> None:
        if self._indice is None:
            return
        lista = self._propios()
        del lista[self._indice]
        self.cfg.guardar("efectos_propios", valor=lista)
        self._recargar_lista()
        self._editar(EfectoPropio())

    def _exportar(self) -> None:
        ef = self._leer()
        archivo = filedialog.asksaveasfilename(parent=self.top, defaultextension=".json",
                                               initialfile=f"{ef.nombre}.json", filetypes=[("JSON", "*.json")])
        if archivo:
            with open(archivo, "w", encoding="utf-8") as f:
                json.dump(ef.a_dict(), f, ensure_ascii=False, indent=2)

    def _importar(self) -> None:
        archivo = filedialog.askopenfilename(parent=self.top, filetypes=[("JSON", "*.json")])
        if not archivo:
            return
        try:
            with open(archivo, encoding="utf-8") as f:
                ef = EfectoPropio.desde_dict(json.load(f))
            errores = ef.validar()
        except (OSError, ValueError, TypeError, KeyError, IndexError) as ex:
            messagebox.showerror(t("ve_titulo"), str(ex), parent=self.top)
            return
        if errores:   # no se carga a medias en el formulario
            messagebox.showerror(t("ve_titulo"), " ".join(t(e) for e in errores), parent=self.top)
            return
        self._editar(ef)

    # ================================================================== refresco
    def _refrescar(self) -> None:
        pestaña = self.cuaderno.index(self.cuaderno.select())
        vivo = self.vib.estado.vivo
        if pestaña == 0:
            ef = vivo.get("efectos", {})
            for e, barra in self._barras.items():
                barra.delete("all")
                barra.create_rectangle(0, 0, 90 * min(1.0, ef.get(e, 0.0)), 10, fill="#0969da", outline="")
        elif pestaña == 1:
            self._dibujar_scope()
            self._mostrar_datos()
        self._tarea = self.top.after(100, self._refrescar)

    def cerrar(self) -> None:
        if self._tarea:
            self.top.after_cancel(self._tarea)
        self.top.destroy()

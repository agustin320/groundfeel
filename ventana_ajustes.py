"""Ventana de ajustes (tkinter): intensidades, opciones, idioma y estado en vivo. Corre en su propio hilo.

Cada cambio se guarda en ajustes.json (sólo la diferencia con los valores por defecto) y el lazo de vibración lo
toma en menos de 2 segundos, sin reiniciar.
"""
from __future__ import annotations

import ctypes
import os
import time
import tkinter as tk
from tkinter import ttk

import i18n
import instalacion
import rutas
from i18n import t
from motor_vibracion import Vibracion
from version import __version__

IDIOMAS = ("auto", "en", "es")
NOMBRE_IDIOMA = {"en": "English", "es": "Español"}


class VentanaAjustes:
    def __init__(self, vib: Vibracion, app: object | None = None) -> None:
        self.vib = vib
        self.app = app   # la App de la bandeja: estado de actualizaciones (app.act) y acciones
        self.cfg = vib.cfg
        try:   # Reason: sin esto Windows escala la ventana como imagen y se ve borrosa en monitores 4K.
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except (AttributeError, OSError):
            pass
        self.raiz = tk.Tk()
        self.raiz.resizable(False, False)
        try:
            self.raiz.iconbitmap(str(rutas.icono()))
        except tk.TclError:
            pass
        self.marco: ttk.Frame | None = None
        self._tarea_refresco: str | None = None
        self._armar()
        # Si nunca se consultó y la búsqueda automática está prendida, se consulta al abrir (sin apretar nada).
        if self.app and not self.app.act.ultima_consulta and self.cfg.datos.get("buscar_actualizaciones", True):
            self.app.buscar_ahora()

    # ------------------------------------------------------------------ armado
    def _deslizador(self, padre: ttk.Frame, fila: int, texto: str, clave: tuple[str, ...]) -> None:
        ttk.Label(padre, text=texto).grid(row=fila, column=0, sticky="w", pady=4)
        var = tk.DoubleVar(value=float(self.cfg.obtener(*clave)))
        etiqueta = ttk.Label(padre, width=6, anchor="e")
        var.trace_add("write", lambda *_a: etiqueta.config(text=f"{var.get() * 100:.0f} %"))

        def guardar(_e: object = None) -> None:
            self.cfg.guardar(*clave, valor=round(var.get(), 3))

        escala = ttk.Scale(padre, from_=0.0, to=1.0, variable=var, length=260)
        escala.grid(row=fila, column=1, padx=8)
        escala.bind("<ButtonRelease-1>", guardar)
        escala.bind("<KeyRelease>", guardar)
        etiqueta.grid(row=fila, column=2)
        etiqueta.config(text=f"{var.get() * 100:.0f} %")
        self._vars[clave] = var

    def _casilla(self, padre: ttk.Frame, fila: int, texto: str, valor: bool, al_cambiar) -> tk.BooleanVar:
        var = tk.BooleanVar(value=valor)
        ttk.Checkbutton(padre, text=texto, variable=var, command=lambda: al_cambiar(var.get())).grid(
            row=fila, column=0, columnspan=3, sticky="w", pady=3)
        return var

    def _armar(self) -> None:
        if self.marco is not None:
            self.marco.destroy()
        if self._tarea_refresco:
            self.raiz.after_cancel(self._tarea_refresco)
        self.raiz.title(t("titulo_ajustes", v=__version__))
        self._vars: dict[tuple[str, ...], tk.DoubleVar] = {}
        marco = self.marco = ttk.Frame(self.raiz, padding=16)
        marco.grid()

        estado = ttk.LabelFrame(marco, text=t("estado"), padding=10)
        estado.grid(row=0, column=0, sticky="ew")
        self.lbl_sim = ttk.Label(estado)
        self.lbl_sim.grid(row=0, column=0, sticky="w")
        self.lbl_disp = ttk.Label(estado)
        self.lbl_disp.grid(row=1, column=0, sticky="w")
        self.lbl_ef = ttk.Label(estado, wraplength=420)
        self.lbl_ef.grid(row=2, column=0, sticky="w")

        inten = ttk.LabelFrame(marco, text=t("intensidad"), padding=10)
        inten.grid(row=1, column=0, sticky="ew", pady=10)
        self._deslizador(inten, 0, "Joystick", ("ganancia_general", "joystick"))
        self._deslizador(inten, 1, "Throttle", ("ganancia_general", "throttle"))
        # Reason: a_ref es "la aceleración que se siente al 100 %": más bajo = rodaje más fuerte. Se muestra al revés
        # (fuerza = a_ref por defecto / a_ref) para que mover a la derecha sea "más".
        a_ref_def = float(self.cfg.defecto["rodaje_fisico"]["a_ref"])
        ttk.Label(inten, text=t("rodaje_joystick")).grid(row=2, column=0, sticky="w", pady=4)
        fuerza = tk.DoubleVar(value=a_ref_def / float(self.cfg.obtener("rodaje_fisico", "a_ref")))
        lbl_f = ttk.Label(inten, width=6, anchor="e")
        lbl_f.grid(row=2, column=2)
        fuerza.trace_add("write", lambda *_a: lbl_f.config(text=f"{fuerza.get() * 100:.0f} %"))
        esc = ttk.Scale(inten, from_=0.3, to=2.5, variable=fuerza, length=260)
        esc.grid(row=2, column=1, padx=8)
        lbl_f.config(text=f"{fuerza.get() * 100:.0f} %")

        def guardar_fuerza(_e: object = None) -> None:
            self.cfg.guardar("rodaje_fisico", "a_ref", valor=round(a_ref_def / max(0.05, fuerza.get()), 3))
        esc.bind("<ButtonRelease-1>", guardar_fuerza)
        esc.bind("<KeyRelease>", guardar_fuerza)
        self._fuerza = fuerza

        opciones = ttk.LabelFrame(marco, text=t("opciones"), padding=10)
        opciones.grid(row=2, column=0, sticky="ew")
        self._solo_tierra = self._casilla(opciones, 0, t("solo_tierra"),
                                          bool(self.cfg.obtener("joystick_solo_en_tierra")),
                                          lambda v: self.cfg.guardar("joystick_solo_en_tierra", valor=v))
        self._casilla(opciones, 1, t("pausar"), self.vib.estado.pausado, self.vib.pausar)
        if rutas.EMPAQUETADO:
            self._casilla(opciones, 2, t("menu_inicio_windows"), instalacion.arranca_con_windows(),
                          instalacion.poner_arranque_con_windows)
        fila_idioma = ttk.Frame(opciones)
        fila_idioma.grid(row=4, column=0, columnspan=3, sticky="w", pady=(6, 0))
        ttk.Label(fila_idioma, text=t("idioma")).grid(row=0, column=0, padx=(0, 8))
        etiquetas = [t("idioma_auto") if c == "auto" else NOMBRE_IDIOMA[c] for c in IDIOMAS]
        actual = str(self.cfg.obtener("idioma")) if "idioma" in self.cfg.datos else "auto"
        combo = ttk.Combobox(fila_idioma, values=etiquetas, state="readonly", width=22)
        combo.current(IDIOMAS.index(actual) if actual in IDIOMAS else 0)
        combo.grid(row=0, column=1)
        combo.bind("<<ComboboxSelected>>", lambda _e: self._cambiar_idioma(IDIOMAS[combo.current()]))

        act = ttk.LabelFrame(marco, text=t("actualizaciones"), padding=10)
        act.grid(row=3, column=0, sticky="ew", pady=(10, 0))
        ttk.Label(act, text=t("version_instalada", v=__version__)).grid(row=0, column=0, sticky="w")
        self.lbl_act = ttk.Label(act)
        self.lbl_act.grid(row=1, column=0, sticky="w", pady=(2, 6))
        botones_act = ttk.Frame(act)
        botones_act.grid(row=0, column=1, rowspan=2, sticky="e", padx=(16, 0))
        self.btn_buscar = ttk.Button(botones_act, text=t("act_buscar"),
                                     command=lambda: self.app and self.app.buscar_ahora())
        self.btn_buscar.grid(row=0, column=0, padx=2)
        self.btn_instalar = ttk.Button(botones_act, text=t("act_instalar"),
                                       command=lambda: self.app and self.app.actualizar_ahora())
        self.btn_instalar.grid(row=0, column=1, padx=2)
        act.columnconfigure(0, weight=1)
        self._casilla(act, 2, t("auto_actualizar"), bool(self.cfg.datos.get("buscar_actualizaciones", True)),
                      lambda v: self.cfg.guardar("buscar_actualizaciones", valor=v))
        ttk.Label(act, text=t("act_nota"), foreground="#666", wraplength=440).grid(row=3, column=0, columnspan=2,
                                                                                    sticky="w")

        botones = ttk.Frame(marco)
        botones.grid(row=4, column=0, sticky="e", pady=(12, 0))
        ttk.Button(botones, text=t("defecto"), command=self._restablecer).grid(row=0, column=0, padx=4)
        ttk.Button(botones, text=t("carpeta"),
                   command=lambda: os.startfile(rutas.datos_usuario())).grid(row=0, column=1, padx=4)
        ttk.Button(botones, text=t("cerrar"), command=self.cerrar).grid(row=0, column=2, padx=4)
        ttk.Label(marco, text=t("aviso_simapppro"), foreground="#666").grid(row=5, column=0, sticky="w",
                                                                              pady=(10, 0))
        self._refrescar()

    # ------------------------------------------------------------------ acciones
    def _cambiar_idioma(self, codigo: str) -> None:
        self.cfg.guardar("idioma", valor=codigo)
        i18n.elegir(codigo)
        self._armar()

    def _restablecer(self) -> None:
        self.cfg.restablecer()
        i18n.elegir(str(self.cfg.datos.get("idioma", "auto")))
        self._armar()

    def _refrescar(self) -> None:
        e = self.vib.estado
        self.lbl_sim.config(text=("● " + t("sim_conectado") if e.conectado else "○ " + t("sim_esperando"))
                            + ("  " + t("en_pausa") if e.pausado else ""))
        self.lbl_disp.config(text=t("dispositivos", d=", ".join(e.dispositivos) or t("ninguno")))
        activos = [i18n.efecto(k) for k, v in e.activos.items() if v >= 0.05]
        self.lbl_ef.config(text=t("vibrando", e=", ".join(activos) if activos else "—"))
        self._refrescar_actualizaciones()
        self._tarea_refresco = self.raiz.after(1000, self._refrescar)

    def _refrescar_actualizaciones(self) -> None:
        a = self.app.act if self.app else None
        if a is None:
            texto = t("act_sin_consultar")
        elif a.buscando:
            texto = t("act_buscando")
        elif a.pendiente:
            texto = t("act_nueva", v=a.pendiente.numero)
        elif a.error:
            texto = t("act_error", e=a.error)
        elif a.ultima_consulta:
            texto = t("act_al_dia", h=time.strftime("%H:%M", time.localtime(a.ultima_consulta)))
        else:
            texto = t("act_sin_consultar")
        self.lbl_act.config(text=texto)
        self.btn_buscar.state(["disabled"] if a is None or a.buscando else ["!disabled"])
        self.btn_instalar.state(["!disabled"] if a and a.pendiente and rutas.EMPAQUETADO else ["disabled"])

    def cerrar(self) -> None:
        if self._tarea_refresco:
            self.raiz.after_cancel(self._tarea_refresco)
        self.raiz.destroy()

    def mostrar(self) -> None:
        self.raiz.protocol("WM_DELETE_WINDOW", self.cerrar)
        self.raiz.mainloop()

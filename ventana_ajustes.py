"""Ventana de ajustes (tkinter): intensidades, opciones y estado en vivo. Corre en su propio hilo.

Cada cambio se guarda en ajustes.json (sólo la diferencia con los valores por defecto) y el lazo de vibración lo
toma en menos de 2 segundos, sin reiniciar.
"""
from __future__ import annotations

import ctypes
import os
import tkinter as tk
from tkinter import ttk

import instalacion
import rutas
from motor_vibracion import Vibracion
from version import __version__

NOMBRES_EFECTO = {"rodaje": "rodaje", "rodadura": "rodadura", "sacudones": "sacudones", "aterrizaje": "toque",
                  "tren": "tren", "flaps": "flaps", "speedbrake": "frenos aerod.", "motores": "motores",
                  "reversa": "reversa", "frenos": "frenos", "aceleracion": "aceleración", "derrape": "derrape",
                  "perdida": "pérdida"}


class VentanaAjustes:
    def __init__(self, vib: Vibracion) -> None:
        self.vib = vib
        self.cfg = vib.cfg
        try:   # Reason: sin esto Windows escala la ventana como imagen y se ve borrosa en monitores 4K.
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except (AttributeError, OSError):
            pass
        self.raiz = tk.Tk()
        self.raiz.title(f"Vibración URSA {__version__} — Ajustes")
        self.raiz.resizable(False, False)
        try:
            self.raiz.iconbitmap(str(rutas.icono()))
        except tk.TclError:
            pass
        self._armar()

    # ------------------------------------------------------------------ armado
    def _deslizador(self, padre: ttk.Frame, fila: int, texto: str, clave: tuple[str, ...], desde: float,
                    hasta: float, a_porcentaje: bool = True) -> None:
        ttk.Label(padre, text=texto).grid(row=fila, column=0, sticky="w", pady=4)
        var = tk.DoubleVar(value=float(self.cfg.obtener(*clave)))
        etiqueta = ttk.Label(padre, width=6, anchor="e")

        def mostrar(*_a: object) -> None:
            v = var.get()
            etiqueta.config(text=f"{v * 100:.0f} %" if a_porcentaje else f"{v:.2f}")

        def guardar(_e: object = None) -> None:
            self.cfg.guardar(*clave, valor=round(var.get(), 3))

        var.trace_add("write", mostrar)
        escala = ttk.Scale(padre, from_=desde, to=hasta, variable=var, length=260)
        escala.grid(row=fila, column=1, padx=8)
        escala.bind("<ButtonRelease-1>", guardar)
        escala.bind("<KeyRelease>", guardar)
        etiqueta.grid(row=fila, column=2)
        mostrar()
        self._vars[clave] = var

    def _casilla(self, padre: ttk.Frame, fila: int, texto: str, valor: bool, al_cambiar) -> tk.BooleanVar:
        var = tk.BooleanVar(value=valor)
        ttk.Checkbutton(padre, text=texto, variable=var, command=lambda: al_cambiar(var.get())).grid(
            row=fila, column=0, columnspan=3, sticky="w", pady=3)
        return var

    def _armar(self) -> None:
        self._vars: dict[tuple[str, ...], tk.DoubleVar] = {}
        marco = ttk.Frame(self.raiz, padding=16)
        marco.grid()

        estado = ttk.LabelFrame(marco, text="Estado", padding=10)
        estado.grid(row=0, column=0, sticky="ew")
        self.lbl_sim = ttk.Label(estado)
        self.lbl_sim.grid(row=0, column=0, sticky="w")
        self.lbl_disp = ttk.Label(estado)
        self.lbl_disp.grid(row=1, column=0, sticky="w")
        self.lbl_ef = ttk.Label(estado, wraplength=420)
        self.lbl_ef.grid(row=2, column=0, sticky="w")

        inten = ttk.LabelFrame(marco, text="Intensidad", padding=10)
        inten.grid(row=1, column=0, sticky="ew", pady=10)
        self._deslizador(inten, 0, "Joystick", ("ganancia_general", "joystick"), 0.0, 1.0)
        self._deslizador(inten, 1, "Throttle", ("ganancia_general", "throttle"), 0.0, 1.0)
        # Reason: a_ref es "la aceleración que se siente al 100 %": más bajo = rodaje más fuerte. Se muestra al revés
        # (fuerza = a_ref por defecto / a_ref) para que mover a la derecha sea "más".
        a_ref_def = float(self.cfg.defecto["rodaje_fisico"]["a_ref"])
        ttk.Label(inten, text="Rodaje (joystick)").grid(row=2, column=0, sticky="w", pady=4)
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

        opciones = ttk.LabelFrame(marco, text="Opciones", padding=10)
        opciones.grid(row=2, column=0, sticky="ew")
        self._solo_tierra = self._casilla(opciones, 0, "El joystick vibra sólo en tierra",
                      bool(self.cfg.obtener("joystick_solo_en_tierra")),
                      lambda v: self.cfg.guardar("joystick_solo_en_tierra", valor=v))
        self._casilla(opciones, 1, "Pausar la vibración", self.vib.estado.pausado, self.vib.pausar)
        if rutas.EMPAQUETADO:
            self._casilla(opciones, 2, "Iniciar con Windows", instalacion.arranca_con_windows(),
                          instalacion.poner_arranque_con_windows)

        botones = ttk.Frame(marco)
        botones.grid(row=3, column=0, sticky="e", pady=(12, 0))
        ttk.Button(botones, text="Valores por defecto", command=self._restablecer).grid(row=0, column=0, padx=4)
        ttk.Button(botones, text="Carpeta de ajustes",
                   command=lambda: os.startfile(rutas.datos_usuario())).grid(row=0, column=1, padx=4)
        ttk.Button(botones, text="Cerrar", command=self.raiz.destroy).grid(row=0, column=2, padx=4)
        ttk.Label(marco, text="Recordá apagar la vibración de SimAppPro para el joystick y el throttle.",
                  foreground="#666").grid(row=4, column=0, sticky="w", pady=(10, 0))
        self._refrescar()

    # ------------------------------------------------------------------ acciones
    def _restablecer(self) -> None:
        self.cfg.restablecer()
        for clave, var in self._vars.items():
            var.set(float(self.cfg.obtener(*clave)))
        self._fuerza.set(1.0)
        self._solo_tierra.set(bool(self.cfg.obtener("joystick_solo_en_tierra")))

    def _refrescar(self) -> None:
        e = self.vib.estado
        self.lbl_sim.config(text=("● Simulador conectado" if e.conectado else "○ Esperando al simulador")
                            + ("  (en pausa)" if e.pausado else ""))
        self.lbl_disp.config(text="Dispositivos: " + (", ".join(e.dispositivos) or "ninguno encontrado"))
        activos = [NOMBRES_EFECTO.get(k, k) for k, v in e.activos.items() if v >= 0.05]
        self.lbl_ef.config(text="Vibrando: " + (", ".join(activos) if activos else "—"))
        self.raiz.after(1000, self._refrescar)

    def mostrar(self) -> None:
        self.raiz.mainloop()

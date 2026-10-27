"""App de bandeja del sistema (entrada del .exe): corre la vibración en segundo plano y se actualiza sola.

La instala el instalador estándar (instalador.iss, Inno Setup). Uso:
     VibracionURSA.exe              (vive en la bandeja; si ya hay una copia corriendo, no hace nada)
     VibracionURSA.exe --esperar    (tras una actualización: espera a que termine de cerrar la copia anterior)
     VibracionURSA.exe --salir      (le pide a la copia en marcha que cierre apagando los motores; lo usa el
                                     desinstalador)
"""
from __future__ import annotations

import ctypes
import os
import sys
import threading
import time

import pystray
from PIL import Image

import actualizador
import i18n
import instalacion
import rutas
from config_usuario import Config
from i18n import t
from instancia import esperar_pedido_de_salida, instancia_unica, pedir_salida
from motor_vibracion import Vibracion, configurar_log, log
from version import __version__

CADA_ACTUALIZACION_S = 6 * 3600
MB_OK, MB_YESNO, MB_ICONINFO, MB_ICONQUESTION, MB_ICONERROR, IDYES = 0, 4, 0x40, 0x20, 0x10, 6


def mensaje(texto: str, estilo: int = MB_OK | MB_ICONINFO) -> int:
    return ctypes.windll.user32.MessageBoxW(None, texto, t("app"), estilo | 0x10000)  # MB_SETFOREGROUND


class App:
    def __init__(self) -> None:
        self.vib = Vibracion()
        self.pendiente: actualizador.Version | None = None
        self.ajustes_abiertos = False
        self.saliendo = False
        self.icono = pystray.Icon("VibracionURSA", Image.open(rutas.icono()), t("app"), self._menu())

    # ------------------------------------------------------------------ menú
    def _texto_estado(self, _item: object = None) -> str:
        e = self.vib.estado
        if e.error:
            return t("error", e=e.error[:60])
        sim = t("sim_conectado") if e.conectado else t("sim_esperando")
        disp = ", ".join(e.dispositivos) or t("sin_dispositivos")
        return f"{sim} · {disp}"

    def _menu(self) -> pystray.Menu:
        # Reason: los textos son funciones para que un cambio de idioma en Ajustes se vea sin reiniciar.
        item = pystray.MenuItem
        return pystray.Menu(
            item(lambda _i: f"{t('app')} {__version__}", None, enabled=False),
            item(self._texto_estado, None, enabled=False),
            pystray.Menu.SEPARATOR,
            item(lambda _i: t("menu_ajustes"), self._abrir_ajustes, default=True),
            item(lambda _i: t("menu_pausar"), self._pausar, checked=lambda _i: self.vib.estado.pausado),
            item(lambda _i: t("menu_inicio_windows"), self._autoarranque,
                 checked=lambda _i: instalacion.arranca_con_windows(), visible=rutas.EMPAQUETADO),
            pystray.Menu.SEPARATOR,
            item(lambda _i: t("menu_actualizar_a", v=self.pendiente.numero) if self.pendiente else "",
                 self._actualizar_ya, visible=lambda _i: self.pendiente is not None),
            item(lambda _i: t("menu_buscar"), self._buscar_manual),
            item(lambda _i: t("menu_registro"), lambda: os.startfile(rutas.archivo_log())),
            item(lambda _i: t("menu_desinstalar"), self._desinstalar, visible=rutas.EMPAQUETADO),
            item(lambda _i: t("menu_salir"), self._salir),
        )

    def _pausar(self) -> None:
        self.vib.pausar(not self.vib.estado.pausado)

    def _autoarranque(self) -> None:
        instalacion.poner_arranque_con_windows(not instalacion.arranca_con_windows())

    def _abrir_ajustes(self) -> None:
        if self.ajustes_abiertos:
            return
        self.ajustes_abiertos = True

        def correr() -> None:
            from ventana_ajustes import VentanaAjustes   # Reason: tkinter sólo se carga si se abre la ventana.
            try:
                VentanaAjustes(self.vib).mostrar()
            finally:
                self.ajustes_abiertos = False

        threading.Thread(target=correr, daemon=True, name="ajustes").start()

    def _salir(self) -> None:
        self.saliendo = True
        self.vib.detener()
        self.icono.stop()

    def _desinstalar(self) -> None:
        # Reason: el desinstalador de Inno Setup cierra esta copia con --salir (motores apagados) y pregunta solo.
        instalacion.abrir_desinstalador()

    # ------------------------------------------------------------------ actualizaciones
    def _buscar_manual(self) -> None:
        def correr() -> None:
            v = actualizador.buscar()
            if v:
                self.pendiente = v
                self.icono.update_menu()
                self.icono.notify(t("hay_version", v=v.numero), t("app"))
            else:
                self.icono.notify(t("ultima_version", v=__version__), t("app"))
        threading.Thread(target=correr, daemon=True).start()

    def _actualizar_ya(self) -> None:
        if self.pendiente:
            self._aplicar(self.pendiente)

    def _aplicar(self, v: actualizador.Version) -> None:
        self.vib.detener()
        if actualizador.aplicar(v):
            self.saliendo = True
            self.icono.stop()
        else:
            self.vib = Vibracion()
            self.vib.iniciar()
            self.icono.notify(t("no_actualizo"), t("app"))

    def _vigilar(self) -> None:
        """Refresca el menú y aplica actualizaciones sola cuando el simulador no está abierto."""
        proxima = time.time() + 30
        while not self.saliendo:
            time.sleep(2)
            i18n.elegir(str(self.vib.cfg.datos.get("idioma", "auto")))
            self.icono.title = f"{t('app')}\n{self._texto_estado()}"[:127]
            self.icono.update_menu()
            # Reason: la búsqueda automática es la única conexión a internet; el usuario la puede apagar en Ajustes.
            if time.time() >= proxima and self.vib.cfg.datos.get("buscar_actualizaciones", True):
                proxima = time.time() + CADA_ACTUALIZACION_S
                self.pendiente = actualizador.buscar() or self.pendiente
            # Reason: nunca cortar la vibración en pleno vuelo; se actualiza con el sim cerrado.
            if self.pendiente and not self.vib.estado.conectado and rutas.EMPAQUETADO:
                log.info("aplicando actualización automática %s", self.pendiente.numero)
                v, self.pendiente = self.pendiente, None
                self._aplicar(v)

    # ------------------------------------------------------------------ arranque
    def correr(self) -> None:
        try:
            self.vib.iniciar()
        except FileNotFoundError as ex:
            mensaje(str(ex), MB_OK | MB_ICONERROR)
            return

        def al_aparecer(icono: pystray.Icon) -> None:
            icono.visible = True
            threading.Thread(target=self._vigilar, daemon=True, name="vigilar").start()
            threading.Thread(target=esperar_pedido_de_salida, args=(self._salir,), daemon=True,
                             name="pedido-salida").start()

        self.icono.run(setup=al_aparecer)


def main() -> None:
    args = sys.argv[1:]
    configurar_log()
    i18n.elegir(str(Config().datos.get("idioma", "auto")))
    if "--salir" in args:
        sys.exit(0 if pedir_salida() else 1)
    if not instancia_unica(esperar_s=20 if "--esperar" in args else 0):
        return
    log.info("app de bandeja %s iniciada", __version__)
    App().correr()


if __name__ == "__main__":
    main()

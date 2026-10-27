"""Textos de la interfaz en inglés y castellano.

Idioma: ajuste "idioma" ("auto", "es" o "en"). En "auto" sigue al idioma de Windows: castellano si Windows está en
español, inglés en cualquier otro caso.
"""
from __future__ import annotations

import ctypes

LANG_SPANISH = 0x0A
_IDIOMA = "en"

TEXTOS: dict[str, dict[str, str]] = {
    "app": {"es": "Vibración URSA", "en": "URSA Rumble"},
    # Estado
    "sim_conectado": {"es": "Simulador conectado", "en": "Simulator connected"},
    "sim_esperando": {"es": "Esperando al simulador", "en": "Waiting for the simulator"},
    "sin_dispositivos": {"es": "sin dispositivos", "en": "no devices"},
    "error": {"es": "Error: {e}", "en": "Error: {e}"},
    "en_pausa": {"es": "(en pausa)", "en": "(paused)"},
    "dispositivos": {"es": "Dispositivos: {d}", "en": "Devices: {d}"},
    "ninguno": {"es": "ninguno encontrado", "en": "none found"},
    "vibrando": {"es": "Vibrando: {e}", "en": "Vibrating: {e}"},
    # Menú
    "menu_ajustes": {"es": "Ajustes…", "en": "Settings…"},
    "menu_pausar": {"es": "Pausar vibración", "en": "Pause vibration"},
    "menu_inicio_windows": {"es": "Iniciar con Windows", "en": "Start with Windows"},
    "menu_actualizar_a": {"es": "Actualizar a la versión {v}", "en": "Update to version {v}"},
    "menu_buscar": {"es": "Buscar actualizaciones", "en": "Check for updates"},
    "menu_registro": {"es": "Ver registro", "en": "View log"},
    "menu_desinstalar": {"es": "Desinstalar…", "en": "Uninstall…"},
    "menu_salir": {"es": "Salir", "en": "Exit"},
    # Avisos
    "hay_version": {"es": "Hay una versión nueva ({v}). Elegí «Actualizar» en el menú.",
                    "en": "A new version ({v}) is available. Choose “Update” in the menu."},
    "ultima_version": {"es": "Tenés la última versión ({v}).", "en": "You have the latest version ({v})."},
    "no_actualizo": {"es": "No se pudo actualizar; sigue la versión actual. Ver el registro.",
                     "en": "The update failed; the current version keeps running. See the log."},
    "confirmar_desinstalar": {"es": "¿Desinstalar Vibración URSA? Tus ajustes se guardan por si lo volvés a instalar.",
                              "en": "Uninstall URSA Rumble? Your settings are kept in case you reinstall."},
    "desinstalado": {"es": "Vibración URSA se desinstaló.", "en": "URSA Rumble was uninstalled."},
    "ya_instalado": {"es": "Vibración URSA ya está instalada y corriendo (ícono en la bandeja, junto al reloj).\n"
                           "Las actualizaciones llegan solas.",
                     "en": "URSA Rumble is already installed and running (tray icon, next to the clock).\n"
                           "Updates arrive automatically."},
    "instalado": {"es": "Listo: Vibración URSA quedó instalada.\n\nVive en la bandeja del sistema (junto al reloj), "
                        "arranca con Windows y se actualiza sola.\nAcordate de apagar la vibración de SimAppPro para "
                        "el joystick y el throttle.",
                  "en": "Done: URSA Rumble is installed.\n\nIt lives in the system tray (next to the clock), starts "
                        "with Windows and updates itself.\nRemember to turn off SimAppPro's vibration for the joystick "
                        "and the throttle."},
    "falta_simconnect": {"es": "No encontré SimConnect.dll.", "en": "SimConnect.dll not found."},
    # Ventana de ajustes
    "titulo_ajustes": {"es": "Vibración URSA {v} — Ajustes", "en": "URSA Rumble {v} — Settings"},
    "estado": {"es": "Estado", "en": "Status"},
    "intensidad": {"es": "Intensidad", "en": "Intensity"},
    "rodaje_joystick": {"es": "Rodaje (joystick)", "en": "Ground roll (joystick)"},
    "opciones": {"es": "Opciones", "en": "Options"},
    "solo_tierra": {"es": "El joystick vibra sólo en tierra", "en": "Joystick vibrates on the ground only"},
    "pausar": {"es": "Pausar la vibración", "en": "Pause vibration"},
    "idioma": {"es": "Idioma", "en": "Language"},
    "idioma_auto": {"es": "Automático (Windows)", "en": "Automatic (Windows)"},
    "reabrir": {"es": "El idioma se aplica al reabrir esta ventana.", "en": "The language applies when you reopen "
                                                                           "this window."},
    "defecto": {"es": "Valores por defecto", "en": "Restore defaults"},
    "carpeta": {"es": "Carpeta de ajustes", "en": "Settings folder"},
    "cerrar": {"es": "Cerrar", "en": "Close"},
    "aviso_simapppro": {"es": "Recordá apagar la vibración de SimAppPro para el joystick y el throttle.",
                        "en": "Remember to turn off SimAppPro's vibration for the joystick and the throttle."},
}

EFECTOS: dict[str, dict[str, str]] = {
    "rodaje": {"es": "rodaje", "en": "ground roll"}, "rodadura": {"es": "rodadura", "en": "rolling"},
    "sacudones": {"es": "sacudones", "en": "bumps"}, "aterrizaje": {"es": "toque", "en": "touchdown"},
    "tren": {"es": "tren", "en": "gear"}, "flaps": {"es": "flaps", "en": "flaps"},
    "speedbrake": {"es": "frenos aerod.", "en": "speedbrakes"}, "motores": {"es": "motores", "en": "engines"},
    "reversa": {"es": "reversa", "en": "reverse"}, "frenos": {"es": "frenos", "en": "brakes"},
    "aceleracion": {"es": "aceleración", "en": "acceleration"}, "derrape": {"es": "derrape", "en": "skid"},
    "perdida": {"es": "pérdida", "en": "stall"},
}


def idioma_windows() -> str:
    try:
        lang = ctypes.windll.kernel32.GetUserDefaultUILanguage()
    except (AttributeError, OSError):
        return "en"
    return "es" if lang & 0x3FF == LANG_SPANISH else "en"


def elegir(preferencia: str) -> None:
    """Fija el idioma: "es", "en" o "auto" (sigue a Windows)."""
    global _IDIOMA
    _IDIOMA = preferencia if preferencia in ("es", "en") else idioma_windows()


def idioma() -> str:
    return _IDIOMA


def t(clave: str, **valores: object) -> str:
    texto = TEXTOS[clave].get(_IDIOMA) or TEXTOS[clave]["en"]
    return texto.format(**valores) if valores else texto


def efecto(nombre: str) -> str:
    return EFECTOS.get(nombre, {}).get(_IDIOMA, nombre)

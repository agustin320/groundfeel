# Vibración URSA

[English](README.md) · **Español**

📖 **[Guía de usuario](docs/GUIA_DE_USUARIO.md)** · [Registro de cambios](CHANGELOG.md)

🚀 **Guía rápida:** [English](docs/quickstart/en.md) · [Español](docs/quickstart/es.md) · [中文](docs/quickstart/zh.md) · [हिन्दी](docs/quickstart/hi.md) · [Français](docs/quickstart/fr.md) · [العربية](docs/quickstart/ar.md) · [বাংলা](docs/quickstart/bn.md) · [Português](docs/quickstart/pt.md) · [Русский](docs/quickstart/ru.md) · [اردو](docs/quickstart/ur.md) · [Bahasa Indonesia](docs/quickstart/id.md) · [Deutsch](docs/quickstart/de.md) · [日本語](docs/quickstart/ja.md) · [मराठी](docs/quickstart/mr.md) · [తెలుగు](docs/quickstart/te.md) · [Türkçe](docs/quickstart/tr.md) · [தமிழ்](docs/quickstart/ta.md) · [Tiếng Việt](docs/quickstart/vi.md) · [한국어](docs/quickstart/ko.md) · [Italiano](docs/quickstart/it.md)

Vibración realista para el **WinWing URSA MINOR 32** (joystick L + throttle Metal R) en **Microsoft Flight Simulator 2024**.

Reemplaza la vibración de SimAppPro por efectos calculados a partir del estado real del avión: rodaje según la superficie y la velocidad, toque en pista, frenos con antibloqueo, spool de los motores, reversa, derrape, tren, flaps, frenos aerodinámicos y pérdida.

## Requisitos

- Windows 10/11.
- WinWing URSA MINOR 32: joystick L y/o throttle Metal R.
- **La vibración de SimAppPro tiene que estar apagada** para estos dispositivos. Si no, los dos programas se pisan.

## Instalación

1. Bajá `VibracionURSA-Setup.exe` de la [última versión](../../releases/latest).
2. Abrilo. Es un instalador estándar (Inno Setup). Instala sólo para tu usuario, sin pedir permisos de administrador, en `%LOCALAPPDATA%\Programs\VibracionURSA`. Queda en el menú Inicio y en "Aplicaciones instaladas".
3. Listo. Vive en la **bandeja del sistema**, junto al reloj, y **arranca con Windows** (es una opción del instalador que podés destildar). Cuando abrís el simulador se conecta solo.

> Hasta que las versiones salgan firmadas (ver [Política de firma de código](#política-de-firma-de-código)), Windows SmartScreen puede avisar que el editor no es conocido. Elegí "Más información → Ejecutar de todas formas". Cada versión la arma GitHub Actions a partir del código de este repositorio, y en la página de la versión figura el SHA-256 de cada archivo.

### Actualizaciones

Son automáticas. La app consulta GitHub unos segundos después de arrancar y después cada 6 horas. Con el simulador cerrado, nunca en pleno vuelo, baja el instalador nuevo sólo desde los releases de este repositorio, exige que coincida con el SHA-256 que publica GitHub (si falta o no coincide, no actualiza) y lo corre en silencio. También podés forzarlo desde el menú de la bandeja con "Buscar actualizaciones", o desactivar la búsqueda automática en Ajustes. Tus ajustes se conservan.

### Desinstalar

Menú de la bandeja → "Desinstalar…", o desde "Aplicaciones instaladas" de Windows. Tus ajustes quedan en `%APPDATA%\VibracionURSA` por si lo volvés a instalar.

### Antivirus

Algunos antivirus marcaron las primeras versiones (1.0.x) con detecciones genéricas por comportamiento, como `PDM:Trojan.Win32.Generic`. Esas versiones se instalaban solas copiando el `.exe`, algo que se parece a lo que hace un programa malicioso. Desde la 1.1.0 se usa un instalador estándar y el programa ya no es un único archivo que se autodescomprime. Si tu antivirus igual se queja, abrí un issue.

## Uso

La interfaz está disponible en 20 idiomas: inglés, chino mandarín, hindi, castellano, francés, árabe, bengalí, portugués, ruso, urdu, indonesio, alemán, japonés, maratí, telugu, turco, tamil, vietnamita, coreano e italiano. Sigue el idioma de Windows y, si no lo tiene, usa inglés. Se puede cambiar en Ajustes → Idioma. Las traducciones están en `idiomas/<código>.json` y las correcciones son bienvenidas.

Click derecho en el ícono de la bandeja:

- **Ajustes**: intensidad del joystick, del throttle y del rodaje; si el joystick vibra sólo en tierra; pausa; iniciar con Windows. Muestra en vivo si el simulador está conectado, qué dispositivos encontró y qué está vibrando. Los cambios se aplican al instante.
- **Pausar vibración**, **Ver registro**, **Buscar actualizaciones**, **Reportar un problema**, **Desinstalar**, **Salir**.

### Reportar problemas y errores

"Reportar un problema" (en el menú de la bandeja o en Ajustes) abre en el navegador un issue de GitHub ya completo. Trae la versión, Windows, los dispositivos, el último error inesperado y las últimas líneas del registro. Tu carpeta de usuario, tu nombre de usuario y el nombre del equipo van tapados. Vos revisás todo y decidís si lo mandás: no se envía nada solo.

Si la app tiene un error inesperado, guarda el detalle en `%APPDATA%\VibracionURSA\errores\` y avisa con una notificación para que lo puedas reportar.

En pausa del simulador no vibra nada.

## Efectos

| Efecto | Qué se siente | Dónde |
|---|---|---|
| Rodaje | Modelo físico: perfil de pista ISO 8608 más juntas de losas, tren de nariz con resortes, percepción de la mano. Pasto, ripio y tierra vibran mucho más que el asfalto. | Joystick |
| Rodadura | Golpecitos de juntas y rumor que crecen con la velocidad. | Throttle |
| Toque en pista | Golpe proporcional a la velocidad de descenso. | Ambos |
| Frenos | Golpe inicial, temblor de ruedas que se hace más lento al frenar, pulsos de antibloqueo y un golpecito al detenerse. | Ambos |
| Motores | Mínimo en ralentí, rumor durante la puesta en marcha, zumbido que crece con la potencia. Cada palanca sigue a su motor. | Throttle |
| Spool / aceleración | Empuje al subir potencia y pulsación que acompaña la aceleración real. | Ambos |
| Reversa | Vibración fuerte en la palanca de cada motor. Si el avión no la publica (A320 de FlyByWire), se deduce de N1 alto frenando en tierra. | Throttle |
| Derrape | Vibración áspera cuando las ruedas van de costado. | Ambos |
| Tren, flaps, frenos aerodinámicos, pérdida, turbulencia | Según su estado. | Ambos |

### Aviones

Funciona con cualquier avión. Los efectos salen de datos que todos los aviones publican, y la app se adapta:

- **Tipo de motor:** los jets siguen el N1; los aviones a pistón y los turbohélices siguen las RPM. En un monomotor, las dos palancas siguen al único motor. La reversa sólo se deduce en jets.
- **Peso:** el modelo de rodaje escala el tren de nariz con el peso real, así que un Cessna vibra más rápido y seco que un A350.
- **Perfiles por avión** (`perfiles/*.json`): afinan los valores por defecto y se aplican solos cuando coincide el nombre del avión cargado. En Ajustes → Estado se ven el avión y el perfil activo. Tus ajustes siempre mandan sobre el perfil. Para escribir uno, mirá `perfiles/_ejemplo.json`.
- **Grabar un vuelo** (menú de la bandeja o Ajustes → "Grabar vuelo") guarda los datos del simulador en `%APPDATA%\VibracionURSA\grabaciones\`. No tiene datos personales y no sale de tu PC. `herramientas\reproducir.py` lo reproduce para afinar un perfil. Las grabaciones compartidas en un issue ayudan a sumar perfiles de más aviones.
Por defecto el joystick vibra **sólo en tierra** (`"joystick_solo_en_tierra": true`).

## Ajustes avanzados

Lo más común se cambia desde la ventana de Ajustes. Para el resto:

- `config.json` trae los valores por defecto. Viene con cada versión, así que no lo edites.
- Tus cambios van en `ajustes.json`, dentro de `%APPDATA%\VibracionURSA` (en la ventana de Ajustes: "Carpeta de ajustes"). Ahí guardás sólo lo que querés cambiar, con la misma estructura que `config.json`. Por ejemplo: `{"frenos": {"antibloqueo": 0.5}}`.
- Los cambios se aplican al guardar, sin reiniciar. Las actualizaciones respetan tus ajustes.

Claves principales:

- `ganancia_general`: intensidad global de cada dispositivo (0 a 1).
- `zona_muerta`: valor mínimo (0 a 255) desde el que gira cada motor. Todo efecto arranca ahí. Se mide con `herramientas\prueba_umbral.py`.
- `pulsado_hasta` y `toque_s`: por debajo de la zona muerta, el joystick da toques cortos en lugar de un zumbido continuo.
- `mezcla`: cuánto de cada efecto va al joystick y cuánto al throttle.
- `rodaje_fisico`:
  - `rugosidad_g0`: rugosidad de cada superficie.
  - `a_umbral`: desde dónde se siente.
  - `a_ref`: fuerza del rodaje.
  - `altura_junta_m`: juntas de las losas.
- `rodaje_modelo`: `"fisico"` (por defecto) o `"heuristico"`, el rodaje anterior basado en reglas.
- Cada efecto tiene su bloque con sus intensidades: `frenos`, `motores`, `aceleracion`, `derrape`, etc.

## Cómo funciona

```
SimConnect (cada frame) ──> sim_lector.py ──> efectos.py ──> motores.py ──> HID (WinWing)
                                                 └─ rodaje_fisico.py
```

- `sim_lector.py`: lee las variables del simulador, sólo lectura. Se reconecta solo.
- `efectos.py`: calcula cada efecto entre 0 y 1 y lo mezcla por motor. Detecta la pausa y compensa la zona muerta.
- `rodaje_fisico.py`:
  - Genera el perfil de la superficie como ruido filtrado con la densidad espectral de ISO 8608.
  - Simula el tren de nariz como un cuarto de vehículo de dos masas, integrado cada 2,5 ms.
  - Aplica a la aceleración de la cabina un umbral de detección y la ley de Stevens.
- `motores.py`: protocolo HID de los motores, reporte `0x02` + `[pieza LE, 00, 00, 03, 49, índice, valor]`.
  - Joystick L: pieza `0xBF07`, motor índice 0.
  - Throttle Metal R: pieza `0xB910`, motores índices 14 y 16.
- `motor_vibracion.py`:
  - Lazo principal a 40 Hz, en un hilo.
  - Recarga la configuración en caliente.
  - Siempre apaga los motores al detenerse.
  - Registro en `vibracion.log`: sólo anota cuando cambian los efectos activos.
- `bandeja.py`: la app (entrada del `.exe`). Se apoya en `ventana_ajustes.py`, `instalacion.py` (arranque con Windows y desinstalador; el instalador es `instalador.iss`, Inno Setup), `actualizador.py` (GitHub Releases) e `i18n.py` (textos de la interfaz).
- `config_usuario.py`: `config.json` (valores por defecto) más `ajustes.json` (lo que cambiaste vos).

## Desarrollo

```
instalar.bat                            (una vez: entorno de Python y dependencias)
venv\Scripts\python.exe bandeja.py      (la app de bandeja, desde el código; no se instala)
venv\Scripts\python.exe vibracion.py    (sin bandeja, con consola; también --silencio y --con-simulador)
venv\Scripts\python.exe pruebas.py      (pruebas sintéticas, sin simulador ni hardware)
venv\Scripts\pyinstaller VibracionURSA.spec   (genera dist\VibracionURSA\)
ISCC /DVersion=1.1.0 instalador.iss          (genera dist\VibracionURSA-Setup.exe; necesita Inno Setup 6)
```

Las pruebas cubren, entre otros: parado, carreteo en asfalto contra pasto, despegue, crucero, pausa, aterrizaje suave contra duro, frenado, aceleración, motores, reversa, derrape y rodaje físico. Corren en GitHub Actions en cada push.

**Publicar una versión:** subí `__version__` en `version.py`, hacé commit y empujá un tag igual (`git tag v1.0.1 && git push --tags`). GitHub Actions corre las pruebas, arma el programa y el instalador, los firma con SignPath (cuando esté configurado; cada firma se aprueba a mano) y publica el instalador en Releases. Las apps instaladas lo toman solas.

`recursos/SimConnect.dll` es la librería cliente redistribuible del SDK de MSFS 2024, de Microsoft. Se incluye para que el programa funcione sin instalar el SDK.

## Problemas comunes

- **No vibra nada:**
  - La ventana de Ajustes muestra si el simulador está conectado y qué dispositivos encontró.
  - El detalle está en "Ver registro".
  - Revisá que la vibración de SimAppPro esté apagada.
- **Un motor quedó vibrando:** pasa si el programa se cierra de golpe, por ejemplo matándolo desde el Administrador de tareas. Volvé a abrirlo: al arrancar apaga los motores.
- **Algo se siente demasiado fuerte o débil:** ajustalo en la ventana de Ajustes.

## Política de firma de código

La política oficial (Code signing policy) está en el [README en inglés](README.md#code-signing-policy). En resumen:

- **Estado: pendiente.** Las versiones todavía no están firmadas; la solicitud a SignPath Foundation no está aprobada.
- Firma de código gratuita provista por [SignPath.io](https://about.signpath.io/), certificado de [SignPath Foundation](https://signpath.org/).
- Commiters, revisores y aprobadores: [agustin320](https://github.com/agustin320).
- Sólo se firman binarios armados por GitHub Actions a partir del código de este repositorio, con aprobación manual de cada firma.

### Privacidad

El programa no envía ningún dato personal. Su única conexión de red es a GitHub, para buscar y bajar actualizaciones: unos segundos después de arrancar y cada 6 horas. Como cualquier pedido web, GitHub recibe tu IP y la versión de la app. Se puede desactivar en Ajustes. "Iniciar con Windows" agrega un valor en `HKCU\...\CurrentVersion\Run` (opcional, en el instalador o en Ajustes) y el desinstalador siempre lo borra. Licencias de terceros: `THIRD-PARTY-NOTICES.txt`. Lee el simulador por SimConnect y sólo escribe en los motores de vibración de los dispositivos WinWing.

## Créditos

- El protocolo HID de los motores se basó en [ursa-minor-ffb](https://github.com/rtroncoso/ursa-minor-ffb) de rtroncoso (MIT).
- Proyecto independiente, sin relación con WinWing ni con Microsoft.

## Licencia

MIT. Ver [LICENSE](LICENSE).

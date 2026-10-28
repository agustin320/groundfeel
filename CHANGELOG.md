# Changelog / Registro de cambios

## 1.5.1

**English**
- **No more turbulence on the throttle:** in-flight bumps now only reach the joystick. On the throttle they felt like
  big isolated pulses, and in the real aircraft turbulence is not felt in the levers.

**Español**
- **La turbulencia ya no llega al throttle:** los sacudones en vuelo quedan sólo en el joystick. En las palancas se
  sentían como pulsos grandes sueltos, y en el avión real la turbulencia no se siente en el throttle.

## 1.5.0

**English**
- **Any aircraft:** piston and turboprop engines now drive the engine effects (RPM instead of N1); single-engine
  aircraft use both throttle motors; reverse is only inferred on jets.
- **Ground roll by weight:** the nose-gear model scales with the aircraft's real weight (a Cessna feels quicker and
  drier, an A350 heavier).
- **Aircraft profiles** (`perfiles/*.json`), applied automatically by aircraft name. Settings shows the aircraft and
  profile. Included: FlyByWire A32NX (reference) and iniBuilds A350 (to be tuned).
- **Record flight** (tray menu / Settings) and `herramientas\reproducir.py` to tune profiles with real data.
- **Landing gear feels real:** a bump when it unlocks and a "clunk" with a small rebound when it locks, instead of a
  continuous vibration while it travels.

**Español**
- **Cualquier avión:** los motores a pistón y turbohélice manejan los efectos de motor (RPM en vez de N1); en
  monomotores las dos palancas siguen al motor; la reversa sólo se deduce en jets.
- **Rodaje según el peso:** el modelo del tren de nariz se escala con el peso real (un Cessna más rápido y seco, un
  A350 más pesado).
- **Perfiles por avión** (`perfiles/*.json`), que se aplican solos según el nombre del avión. Ajustes muestra el
  avión y el perfil. Incluidos: FlyByWire A32NX (referencia) e iniBuilds A350 (a calibrar).
- **Grabar vuelo** (menú de la bandeja / Ajustes) y `herramientas\reproducir.py` para afinar perfiles con datos reales.
- **Tren de aterrizaje real:** un golpe al destrabarse y un "clunk" con rebote al trabarse, en vez de vibrar todo el
  recorrido.

## 1.4.1

**English**
- **After an update the app tells you:** a notification says it was updated and the Settings window opens.
- **Safer updates:** the updater only downloads from this project's GitHub releases and refuses to install unless the
  SHA-256 published by GitHub matches. Downloads go to a fresh private temporary folder.
- **Installer:** "Start with Windows" is always removed on uninstall, even if it was turned on from Settings. Third-party
  license notices are installed with the app (`THIRD-PARTY-NOTICES.txt`).
- **Security:** the installed app only loads its own bundled `SimConnect.dll`. Build pipeline hardened (pinned actions
  and tool versions).
- **Docs:** user guide in English and Spanish under `docs/`, README corrected (update checks, privacy, signing status).
- New releases also publish `VibracionURSA-Update.exe` (same installer), used by the built-in updater, so download
  counts tell new installs apart from updates without any telemetry.

**Español**
- **Después de actualizarse avisa:** una notificación dice que se actualizó y se abre la ventana de Ajustes.
- **Actualizaciones más seguras:** sólo baja de los releases de este proyecto en GitHub y no instala si el SHA-256
  publicado por GitHub no coincide. La descarga va a una carpeta temporal nueva y privada.
- **Instalador:** "Iniciar con Windows" se borra siempre al desinstalar, aunque se haya activado desde Ajustes. Se
  instalan los avisos de licencias de terceros (`THIRD-PARTY-NOTICES.txt`).
- **Seguridad:** la app instalada sólo carga su propia `SimConnect.dll`. Compilación automática endurecida.
- **Documentación:** guía de usuario en inglés y castellano en `docs/`; README corregido.
- Cada versión publica además `VibracionURSA-Update.exe` (el mismo instalador), que usa el actualizador: así las
  descargas separan instalaciones nuevas de actualizaciones sin telemetría.

## 1.3.0

**English**
- **Report a problem** (tray menu and Settings): opens a pre-filled GitHub issue (version, Windows, devices, last
  error, last log lines) with your user name, user folder and computer name masked. Nothing is sent unless you submit it.
- **Unexpected errors** are saved locally and you get a notification so you can report them.

**Español**
- **Reportar un problema** (menú de la bandeja y Ajustes): abre un issue de GitHub ya completo y saneado. No se envía
  nada si no lo mandás.
- **Errores inesperados:** se guardan en la PC y avisa con una notificación para que los puedas reportar.

## 1.2.0

### English

**English** · [Español](#vibración-ursa-120--notas-de-versión)

Released: October 27, 2026 · Download: `VibracionURSA-Setup.exe` from the [release page](https://github.com/agustin320/vibracion-ursa/releases/tag/v1.2.0)

URSA Rumble replaces SimAppPro's vibration on the WinWing URSA MINOR 32 (joystick L and throttle Metal R) with effects computed from what your aircraft is really doing in MSFS 2024. This release rounds up everything that changed since the first public version (1.0.0).

## Highlights

- **Your language.** The app now speaks 20 languages and follows your Windows language automatically.
- **Smoother approaches.** The throttle no longer gives random pulses on final with the gear down and the autothrust working.
- **Clean flight loading.** No more phantom touchdown bump when a flight loads on the ground.
- **Standard installer and automatic updates**, with a new Updates section in Settings so you always know where you stand.

## New

- **20 interface languages:** English, Mandarin Chinese, Hindi, Spanish, French, Arabic, Bengali, Portuguese, Russian, Urdu, Indonesian, German, Japanese, Marathi, Telugu, Turkish, Tamil, Vietnamese, Korean and Italian. The app picks your Windows language (English if yours isn't on the list), and you can change it any time in **Settings → Language** without restarting.
- **Standard installer.** One `VibracionURSA-Setup.exe` that installs for your Windows user only, without admin rights. You get a Start menu entry, an entry in Windows "Installed apps", an optional "Start with Windows" checkbox and a proper uninstaller.
- **Automatic updates.** Every 6 hours the app checks GitHub for a new version. It only installs when the simulator is closed, never mid-flight, after checking that the download matches the published file (SHA-256). Your settings are kept.
- **Updates section in Settings.** See the installed version and the last check, and use **Check now** and **Update now**. You can turn automatic updates off with one checkbox.
- **Status colors.**
  - In Settings: green when the simulator is connected, both devices are found or you're up to date; orange when paused or only one device is found; blue when a new version is available or something is vibrating; red for errors or no devices.
  - In the tray: a colored dot on the icon (green connected, gray waiting for the simulator, orange paused).

## Fixed

- **Throttle pulses during the approach.** With the gear down and the autothrust constantly adjusting power, the throttle motors could switch on and off over and over, which felt like loose pulses. The throttle now stays smooth on final, and the power-change "push" is toned down in the air.
- **False touchdown when loading a flight.** Spawning on the ground no longer triggers a landing bump. Touchdown is only felt on a real landing.
- **Antivirus warnings on 1.0.x.** The 1.0.x builds copied themselves to install, which some antivirus products (for example Kaspersky, `PDM:Trojan.Win32.Generic`) flagged as suspicious. Since 1.1.0 the app uses a standard installer and is no longer a single self-extracting file.
- **Installing over a running copy.** The installer and the uninstaller now close the running app cleanly first, turning the motors off, wherever it was running from.

## Known issues

- **SmartScreen warning.** The builds are not code-signed yet (signing through SignPath is being set up). Windows may say the publisher is unknown: click **More info → Run anyway**. Every release is built by GitHub Actions from the public source, and the SHA-256 of the installer is listed on the release page.
- **Machine translations.** Except for English and Spanish, the interface translations were generated automatically and may contain awkward or wrong wording. Corrections are welcome as issues or pull requests (`idiomas/<code>.json`).
- **The installer itself is only in English and Spanish**, even though the app has 20 languages.
- **Coming from 1.0.0 or 1.0.1?** Those versions look for a file that newer releases no longer publish, so they won't update by themselves. Download `VibracionURSA-Setup.exe` once and run it; from then on, updates are automatic.
- **Engine-related effects need a turbine aircraft.** Engine hum, spool and reverse are driven by turbine N1, so they may not appear on piston aircraft.

## Upgrading

- From 1.1.x: nothing to do. The app updates itself the next time the simulator is closed, or use **Settings → Update now**.
- From 1.0.x: download and run the installer manually (see Known issues).
- Remember to keep **SimAppPro's vibration turned off** for the joystick and the throttle.

---

### Español

[English](#ursa-rumble-120--release-notes) · **Español**

Publicada: 27 de octubre de 2026 · Descarga: `VibracionURSA-Setup.exe` desde la [página de la versión](https://github.com/agustin320/vibracion-ursa/releases/tag/v1.2.0)

Vibración URSA reemplaza la vibración de SimAppPro en el WinWing URSA MINOR 32 (joystick L y throttle Metal R) por efectos calculados a partir de lo que hace tu avión en MSFS 2024. Esta versión resume todo lo que cambió desde la primera versión pública (1.0.0).

## Lo más importante

- **En tu idioma.** La app ahora está en 20 idiomas y sigue sola el idioma de Windows.
- **Aproximaciones más limpias.** El throttle ya no da pulsos sueltos en final con el tren abajo y el autothrust trabajando.
- **Carga de vuelo sin sorpresas.** Se terminó el golpe de "toque" fantasma al cargar un vuelo en tierra.
- **Instalador estándar y actualizaciones automáticas**, con una sección nueva de Actualizaciones en Ajustes para saber siempre cómo estás.

## Novedades

- **20 idiomas en la interfaz:** inglés, chino mandarín, hindi, castellano, francés, árabe, bengalí, portugués, ruso, urdu, indonesio, alemán, japonés, maratí, telugu, turco, tamil, vietnamita, coreano e italiano. Toma el idioma de Windows (inglés si el tuyo no está) y lo podés cambiar cuando quieras en **Ajustes → Idioma**, sin reiniciar.
- **Instalador estándar.** Un solo `VibracionURSA-Setup.exe` que instala sólo para tu usuario de Windows, sin permisos de administrador. Queda en el menú Inicio y en "Aplicaciones instaladas", con una casilla opcional para iniciar con Windows y un desinstalador como corresponde.
- **Actualizaciones automáticas.** Cada 6 horas la app busca una versión nueva en GitHub. Sólo instala con el simulador cerrado, nunca en pleno vuelo, y antes verifica que lo bajado coincida con el archivo publicado (SHA-256). Tus ajustes se conservan.
- **Sección Actualizaciones en Ajustes.** Muestra la versión instalada y la última consulta, con los botones **Buscar ahora** y **Actualizar ahora**. Las actualizaciones automáticas se apagan con una casilla.
- **Colores de estado.**
  - En Ajustes: verde con el simulador conectado, los dos dispositivos encontrados o la app al día; naranja en pausa o con un solo dispositivo; azul cuando hay versión nueva o algo está vibrando; rojo ante un error o sin dispositivos.
  - En la bandeja: un punto de color en el ícono (verde conectado, gris esperando al simulador, naranja en pausa).

## Arreglos

- **Pulsos en el throttle durante la aproximación.** Con el tren abajo y el autothrust corrigiendo potencia todo el tiempo, los motores del throttle podían prenderse y apagarse una y otra vez, y se sentía como pulsos sueltos. Ahora el throttle queda suave en final, y el "empuje" al cambiar potencia es más leve en el aire.
- **Toque falso al cargar un vuelo.** Aparecer en tierra ya no dispara el golpe de aterrizaje. El toque sólo se siente en un aterrizaje de verdad.
- **Avisos de antivirus en la 1.0.x.** Las versiones 1.0.x se copiaban a sí mismas para instalarse, y algunos antivirus (por ejemplo Kaspersky, `PDM:Trojan.Win32.Generic`) lo tomaban como sospechoso. Desde la 1.1.0 se usa un instalador estándar y el programa ya no es un único archivo que se autodescomprime.
- **Instalar con la app abierta.** El instalador y el desinstalador ahora cierran primero la app en marcha, apagando los motores, esté donde esté.

## Problemas conocidos

- **Aviso de SmartScreen.** Las versiones todavía no salen firmadas (la firma con SignPath está en preparación). Windows puede decir que el editor es desconocido: elegí **Más información → Ejecutar de todas formas**. Cada versión la arma GitHub Actions a partir del código público, y el SHA-256 del instalador figura en la página de la versión.
- **Traducciones automáticas.** Salvo inglés y castellano, las traducciones de la interfaz se generaron automáticamente y pueden tener frases raras o errores. Las correcciones son bienvenidas como issue o pull request (`idiomas/<código>.json`).
- **El instalador en sí está sólo en inglés y castellano**, aunque la app tenga 20 idiomas.
- **¿Venís de la 1.0.0 o la 1.0.1?** Esas versiones buscan un archivo que las nuevas ya no publican, así que no se actualizan solas. Bajá `VibracionURSA-Setup.exe` una vez y corrélo; de ahí en adelante las actualizaciones son automáticas.
- **Los efectos de motor necesitan un avión a turbina.** El zumbido, el spool y la reversa salen del N1 de turbina, así que en aviones a pistón pueden no aparecer.

## Cómo actualizar

- Desde la 1.1.x: no hay que hacer nada. La app se actualiza sola la próxima vez que cierres el simulador, o usá **Ajustes → Actualizar ahora**.
- Desde la 1.0.x: bajá y corré el instalador a mano (ver Problemas conocidos).
- Acordate de dejar **apagada la vibración de SimAppPro** para el joystick y el throttle.

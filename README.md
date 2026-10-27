# URSA Rumble (Vibración URSA)

**English** · [Español](README.es.md)

Realistic vibration for the **WinWing URSA MINOR 32** (joystick L + throttle Metal R) in **Microsoft Flight Simulator 2024**.

It replaces SimAppPro's vibration with effects computed from the aircraft's real state: ground roll by surface and speed, touchdown, wheel brakes with anti-skid, engine spool, reverse thrust, tire skid, landing gear, flaps, speedbrakes and stall buffet.

## Requirements

- Windows 10/11.
- WinWing URSA MINOR 32: joystick L and/or throttle Metal R.
- **SimAppPro's vibration must be turned off** for these devices, otherwise both programs fight over the motors.

## Install

1. Download `VibracionURSA.exe` from the [latest release](../../releases/latest).
2. Run it. It installs itself for your user, without admin rights, in `%LOCALAPPDATA%\Programs\VibracionURSA`. It also appears in the Start menu and in "Installed apps".
3. Done. It lives in the **system tray** next to the clock and **starts with Windows**. It connects by itself when the simulator opens.

> Windows SmartScreen may warn that the publisher is unknown, because the program isn't code-signed. Click "More info → Run anyway".

### Updates

Updates are automatic. Every 6 hours the app checks GitHub for a new version and updates itself while the simulator is closed, never mid-flight. You can also use "Check for updates" in the tray menu. Your settings are kept.

### Uninstall

Tray menu → "Uninstall…", or from Windows "Installed apps". Your settings stay in `%APPDATA%\VibracionURSA` in case you reinstall.

## Usage

The interface is in English or Spanish, following the Windows language. You can change it in Settings → Language.

Right-click the tray icon:

- **Settings**:
  - Joystick, throttle and ground-roll intensity.
  - Whether the joystick vibrates on the ground only.
  - Pause, and start with Windows.
  - A live view of the simulator connection, the devices found and which effects are vibrating.
  - Changes apply instantly.
- **Pause vibration**, **View log**, **Check for updates**, **Uninstall**, **Exit**.

Nothing vibrates while the simulator is paused.

## Effects

| Effect | What you feel | Where |
|---|---|---|
| Ground roll | Physical model: an ISO 8608 runway profile plus slab joints, a nose gear with springs, and how the hand perceives vibration. Grass, gravel and dirt shake much more than asphalt. | Joystick |
| Rolling | Joint bumps and a rumble that grow with speed. | Throttle |
| Touchdown | A bump proportional to the descent rate. | Both |
| Wheel brakes | Initial jolt, wheel tremor that slows down as you brake, anti-skid pulses and a small bump when stopping. | Both |
| Engines | A minimum at idle, a rumble during engine start, and a hum that grows with power. Each lever follows its own engine. | Throttle |
| Spool / acceleration | A push when power goes up and a pulsation that follows the real acceleration. | Both |
| Reverse | Strong vibration on each engine's lever. If the aircraft doesn't publish it (FlyByWire A320), it's inferred from high N1 while decelerating on the ground. | Throttle |
| Skid | A rough vibration when the tires slide sideways. | Both |
| Gear, flaps, speedbrakes, stall, turbulence | According to their state. | Both |

By default the joystick vibrates **on the ground only** (`"joystick_solo_en_tierra": true`).

## Advanced settings

The common options are in the Settings window. For everything else:

- `config.json` holds the defaults. It ships with every version, so don't edit it.
- Your changes go in `ajustes.json`, inside `%APPDATA%\VibracionURSA` (Settings → "Settings folder").
  - Put only what you want to change there, with the same structure as `config.json`. For example: `{"frenos": {"antibloqueo": 0.5}}`.
  - Changes apply on save, without restarting. Updates keep your settings.

Main keys (names are in Spanish):

- `ganancia_general`: overall intensity per device (0 to 1).
- `zona_muerta`: the minimum value (0 to 255) at which each motor starts spinning. Every effect starts there. Measure it with `herramientas\prueba_umbral.py`.
- `pulsado_hasta` and `toque_s`: below the dead zone, the joystick gives short taps instead of a continuous hum.
- `mezcla`: how much of each effect goes to the joystick and how much to the throttle.
- `rodaje_fisico` (ground-roll model):
  - `rugosidad_g0`: roughness per surface.
  - `a_umbral`: where it starts being felt.
  - `a_ref`: ground-roll strength.
  - `altura_junta_m`: slab joint height.
- `rodaje_modelo`: `"fisico"` (default) or `"heuristico"`, the older rule-based ground roll.
- Each effect has its own block of intensities: `frenos`, `motores`, `aceleracion`, `derrape`, etc.

## How it works

```
SimConnect (every frame) ──> sim_lector.py ──> efectos.py ──> motores.py ──> HID (WinWing)
                                                  └─ rodaje_fisico.py
```

- `sim_lector.py`: reads the simulator variables, read-only. It reconnects by itself.
- `efectos.py`: computes each effect from 0 to 1 and mixes them per motor. It detects pause and compensates for the motors' dead zone.
- `rodaje_fisico.py`:
  - Generates the surface profile as noise filtered with the ISO 8608 spectral density.
  - Simulates the nose gear as a two-mass quarter-car model, integrated every 2.5 ms.
  - Applies a detection threshold and Stevens' power law to the cockpit acceleration.
- `motores.py`: the motors' HID protocol, report `0x02` + `[part LE, 00, 00, 03, 49, index, value]`.
  - Joystick L: part `0xBF07`, motor index 0.
  - Throttle Metal R: part `0xB910`, motor indexes 14 and 16.
- `motor_vibracion.py`:
  - Main loop at 40 Hz, in a thread.
  - Reloads the configuration live.
  - Always turns the motors off when it stops.
- `bandeja.py`: the app (entry point of the `.exe`). It relies on:
  - `ventana_ajustes.py`: the Settings window.
  - `instalacion.py`: per-user install in HKCU.
  - `actualizador.py`: updates from GitHub Releases.
  - `i18n.py`: interface texts.
- `config_usuario.py`: `config.json` (defaults) plus `ajustes.json` (your changes).

## Development

```
instalar.bat                            (once: Python environment and dependencies)
venv\Scripts\python.exe bandeja.py      (tray app from source; it doesn't install itself)
venv\Scripts\python.exe vibracion.py    (console, no tray; also --silencio and --con-simulador)
venv\Scripts\python.exe pruebas.py      (synthetic tests, no simulator or hardware needed)
venv\Scripts\pyinstaller VibracionURSA.spec   (builds dist\VibracionURSA.exe)
```

The tests run on GitHub Actions on every push.

**Releasing:**

1. Bump `__version__` in `version.py` and commit.
2. Push a matching tag: `git tag v1.0.1 && git push --tags`.
3. GitHub Actions runs the tests, builds the `.exe` and publishes it to Releases. Installed apps pick it up by themselves.

`recursos/SimConnect.dll` is the redistributable client library from Microsoft's MSFS 2024 SDK. It's bundled so the program works without the SDK installed.

## Troubleshooting

- **Nothing vibrates:**
  - The Settings window shows whether the simulator is connected and which devices were found.
  - "View log" has the details.
  - Check that SimAppPro's vibration is off.
- **A motor keeps vibrating:** this happens if the program is killed abruptly, for example from Task Manager. Open it again: it turns the motors off when it starts.
- **Something feels too strong or too weak:** adjust it in the Settings window.

## Credits

- The motors' HID protocol is based on [ursa-minor-ffb](https://github.com/rtroncoso/ursa-minor-ffb) by rtroncoso (MIT).
- Independent project, not affiliated with WinWing or Microsoft.

## License

MIT. See [LICENSE](LICENSE).

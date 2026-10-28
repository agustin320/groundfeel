# Groundfeel

*Formerly "URSA Rumble". Independent project, not affiliated with WinWing.*

**English** · [Español](README.es.md)

📖 **[User guide](docs/USER_GUIDE.md)** · [Changelog](CHANGELOG.md)

🚀 **Quick start:** [English](docs/quickstart/en.md) · [Español](docs/quickstart/es.md) · [中文](docs/quickstart/zh.md) · [हिन्दी](docs/quickstart/hi.md) · [Français](docs/quickstart/fr.md) · [العربية](docs/quickstart/ar.md) · [বাংলা](docs/quickstart/bn.md) · [Português](docs/quickstart/pt.md) · [Русский](docs/quickstart/ru.md) · [اردو](docs/quickstart/ur.md) · [Bahasa Indonesia](docs/quickstart/id.md) · [Deutsch](docs/quickstart/de.md) · [日本語](docs/quickstart/ja.md) · [मराठी](docs/quickstart/mr.md) · [తెలుగు](docs/quickstart/te.md) · [Türkçe](docs/quickstart/tr.md) · [தமிழ்](docs/quickstart/ta.md) · [Tiếng Việt](docs/quickstart/vi.md) · [한국어](docs/quickstart/ko.md) · [Italiano](docs/quickstart/it.md)

Realistic vibration for the **WinWing URSA MINOR 32** (joystick L + throttle Metal R) in **Microsoft Flight Simulator 2024**.

It replaces SimAppPro's vibration with effects computed from the aircraft's real state: ground roll by surface and speed, touchdown, wheel brakes with anti-skid, engine spool, reverse thrust, tire skid, landing gear, flaps, speedbrakes and stall buffet.

## Requirements

- Windows 10/11.
- WinWing URSA MINOR 32: joystick L and/or throttle Metal R.
- **SimAppPro's vibration must be turned off** for these devices, otherwise both programs fight over the motors.

## Install

1. Download `VibracionURSA-Setup.exe` from the [latest release](../../releases/latest).
2. Run it. It's a standard installer (Inno Setup) and installs for your user only, without admin rights, in `%LOCALAPPDATA%\Programs\VibracionURSA`. It also appears in the Start menu and in "Installed apps".
3. Done. It lives in the **system tray** next to the clock and **starts with Windows** (an installer option you can untick). It connects by itself when the simulator opens.

> Until the builds are code-signed (see [Code signing policy](#code-signing-policy)), Windows SmartScreen may warn that the publisher is unknown: click "More info → Run anyway". Each release is built by GitHub Actions from this repository's source; the SHA-256 of every file is shown on the release page.

### Updates

Updates are automatic. The app checks GitHub a few seconds after it starts and then every 6 hours. When the simulator is closed, never mid-flight, it downloads the new installer only from this repository's releases, requires the SHA-256 published by GitHub to match (if it is missing or different, it does not update), and runs it silently. You can also use "Check for updates" in the tray menu, or turn automatic checks off in Settings. Your settings are kept.

### Uninstall

Tray menu → "Uninstall…", or from Windows "Installed apps". Your settings stay in `%APPDATA%\VibracionURSA` in case you reinstall.

## Usage

The interface is available in 20 languages: English, Mandarin Chinese, Hindi, Spanish, French, Arabic, Bengali, Portuguese, Russian, Urdu, Indonesian, German, Japanese, Marathi, Telugu, Turkish, Tamil, Vietnamese, Korean and Italian. It follows the Windows language and falls back to English; you can change it in Settings → Language. Translations live in `idiomas/<code>.json` and corrections are welcome.

Right-click the tray icon:

- **Settings**:
  - Joystick, throttle and ground-roll intensity.
  - Whether the joystick vibrates on the ground only.
  - Pause, and start with Windows.
  - A live view of the simulator connection, the devices found and which effects are vibrating.
  - Changes apply instantly.
- **Pause vibration**, **View log**, **Check for updates**, **Report a problem**, **Uninstall**, **Exit**.

### Reporting problems and errors

"Report a problem" (tray menu or Settings) opens a pre-filled GitHub issue in your browser. It includes the app version, Windows version, devices found, the last unexpected error and the last log lines. Your user folder, user name and computer name are masked. You review everything and decide whether to submit it: nothing is sent automatically.

If the app hits an unexpected error, it saves the details in `%APPDATA%\VibracionURSA\errores\` and shows a notification so you can report it.

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
| Gear, flaps, speedbrakes, stall | According to their state. | Both |
| Turbulence | Real vertical jolts in flight. | Joystick |

### Aircraft support

Any MSFS 2024 aircraft works (MSFS 2020 is untested). The effects come from data every aircraft publishes, and the app adapts to it:

- **Engine type:** jets follow N1, while piston and turboprop aircraft follow propeller/engine RPM. Single-engine aircraft drive both throttle motors. Reverse thrust is inferred only on jets.
- **Weight:** the ground-roll model scales the nose gear with the aircraft's real weight, so a Cessna rattles quicker and drier than an A350.
- **Aircraft profiles** (`perfiles/*.json`) fine-tune the defaults. They apply automatically when the loaded aircraft's name matches; Settings → Status shows the aircraft and the active profile. Your own settings always win over a profile. See `perfiles/_ejemplo.json` to write one.
- **Recording a flight** (tray menu or Settings → "Record flight") saves the simulator data to `%APPDATA%\VibracionURSA\grabaciones\`. It contains no personal data and stays on your PC. `herramientas\reproducir.py` replays it to tune a profile. Recordings shared through an issue help add profiles for more aircraft.
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
  - `instalacion.py`: start with Windows and the uninstaller. The installer itself is `instalador.iss` (Inno Setup).
  - `actualizador.py`: updates from GitHub Releases.
  - `i18n.py`: interface texts.
- `config_usuario.py`: `config.json` (defaults) plus `ajustes.json` (your changes).

## Development

```
instalar.bat                            (once: Python environment and dependencies)
venv\Scripts\python.exe bandeja.py      (tray app from source; it doesn't install itself)
venv\Scripts\python.exe vibracion.py    (console, no tray; also --silencio and --con-simulador)
venv\Scripts\python.exe pruebas.py      (synthetic tests, no simulator or hardware needed)
venv\Scripts\pyinstaller VibracionURSA.spec   (builds dist\VibracionURSA\)
ISCC /DVersion=1.1.0 instalador.iss          (builds dist\VibracionURSA-Setup.exe; needs Inno Setup 6)
```

The tests run on GitHub Actions on every push.

**Releasing:**

1. Bump `__version__` in `version.py` and commit.
2. Push a matching tag: `git tag v1.0.1 && git push --tags`.
3. GitHub Actions runs the tests, builds the program and the installer, signs both with SignPath (once configured; each signing request is approved manually) and publishes the installer to Releases. Installed apps pick it up by themselves.

`recursos/SimConnect.dll` is the redistributable client library from Microsoft's MSFS 2024 SDK. It's bundled so the program works without the SDK installed.

## Troubleshooting

- **Nothing vibrates:**
  - The Settings window shows whether the simulator is connected and which devices were found.
  - "View log" has the details.
  - Check that SimAppPro's vibration is off.
- **A motor keeps vibrating:** this happens if the program is killed abruptly, for example from Task Manager. Open it again: it turns the motors off when it starts.
- **Something feels too strong or too weak:** adjust it in the Settings window.

## Code signing policy

> **Status: pending.** Builds are not code-signed yet; the application to SignPath Foundation has not been approved. This section describes the policy that will apply once it is.

Free code signing provided by [SignPath.io](https://about.signpath.io/), certificate by [SignPath Foundation](https://signpath.org/).

- Committers and reviewers: [agustin320](https://github.com/agustin320)
- Approvers: [agustin320](https://github.com/agustin320)

Only binaries built by GitHub Actions from this repository's source are signed. Every signing request is approved manually.

### Privacy

This program does not send any personal data and has no telemetry; error reports are only sent if you submit the pre-filled GitHub issue yourself. Its only network connection is to GitHub (`api.github.com` and GitHub release downloads) to check for and download updates: a few seconds after start and every 6 hours. Like any web request, GitHub receives your IP address and the app version (in the User-Agent). You can turn this off in Settings ("Check for and install updates automatically"). GitHub's privacy statement applies to those requests: https://docs.github.com/site-policy/privacy-policies/github-general-privacy-statement

The program reads the simulator through SimConnect and writes only to the WinWing devices' vibration motors. "Start with Windows" adds a value under `HKCU\Software\Microsoft\Windows\CurrentVersion\Run` (optional, in the installer or in Settings); the uninstaller always removes it. The app folder, Start menu shortcut and that value are the only things installed. Third-party licenses: `THIRD-PARTY-NOTICES.txt`.

## Credits

- The motors' HID protocol is based on [ursa-minor-ffb](https://github.com/rtroncoso/ursa-minor-ffb) by rtroncoso (MIT).
- Independent project, not affiliated with WinWing or Microsoft.

## License

MIT. See [LICENSE](LICENSE).

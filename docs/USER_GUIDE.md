# Groundfeel — User Manual

Version 1.4 · For pilots using the WinWing URSA MINOR 32 in Microsoft Flight Simulator 2024

---

## Contents

1. [What Groundfeel does](#1-what-groundfeel-does)
2. [What you need](#2-what-you-need)
3. [Installation](#3-installation)
4. [First use: turn off SimAppPro's vibration](#4-first-use-turn-off-simapppros-vibration)
5. [The tray icon and its menu](#5-the-tray-icon-and-its-menu)
6. [What you feel in each phase of flight](#6-what-you-feel-in-each-phase-of-flight)
7. [The Settings window, control by control](#7-the-settings-window-control-by-control)
8. [Updates](#8-updates)
9. [Languages](#9-languages)
10. [Uninstalling](#10-uninstalling)
11. [FAQ and troubleshooting](#11-faq-and-troubleshooting)

---

## 1. What Groundfeel does

Groundfeel is a free, open-source app (MIT license) that drives the vibration motors in your **WinWing URSA MINOR 32 joystick L** and **throttle Metal R**. It replaces SimAppPro's vibration with effects based on what your aircraft is really doing in MSFS 2024: the surface you're rolling on, your speed, how hard you land, how hard you brake, engine power, reverse thrust, gear, flaps and more.

- It sits quietly in the Windows **system tray**, next to the clock.
- It connects to the simulator by itself when MSFS opens.
- It only **reads** the simulator. It never changes anything in your flight.
- It never sends personal data. Its only internet connection is checking GitHub for updates, and you can turn that off.

> Groundfeel is an independent project. It isn't affiliated with WinWing or Microsoft.

---

## 2. What you need

| Item | Details |
|---|---|
| Operating system | Windows 10 or Windows 11 |
| Simulator | Microsoft Flight Simulator 2024 |
| Hardware | WinWing URSA MINOR 32: joystick L, throttle Metal R, or both |
| SimAppPro | Can stay installed, but **its vibration must be off** for these two devices (see [section 4](#4-first-use-turn-off-simapppros-vibration)) |
| Admin rights | Not needed |

---

## 3. Installation

### Step 1 — Download

1. Go to the latest release: https://github.com/agustin320/vibracion-ursa/releases/latest
2. Under **Assets**, download **`VibracionURSA-Setup.exe`**.

[CAPTURE: GitHub release page with the "Assets" section open and VibracionURSA-Setup.exe highlighted]

> Only download the installer from that page. The SHA-256 of the file is shown there if you want to check it.

### Step 2 — Get past the SmartScreen warning

The installer isn't code-signed yet, so Windows may show a blue **"Windows protected your PC"** window saying the publisher is unknown. This is expected for new, unsigned apps.

1. Click **More info**.
2. Click **Run anyway**.

[CAPTURE: SmartScreen window "Windows protected your PC" with the "More info" link highlighted]

[CAPTURE: the same window after clicking "More info", with the "Run anyway" button highlighted]

### Step 3 — Run the installer

1. Choose the installer language (English or Spanish).
2. Accept the license (MIT).
3. Choose whether to **Start with Windows**. Recommended: the app waits in the tray, uses no vibration until the simulator opens, and you never have to remember to launch it.
4. Click **Install**.
5. On the last page, read the privacy and SimAppPro notes, leave **"Open Groundfeel now"** ticked and click **Finish**.

[CAPTURE: installer page with the "Start with Windows" checkbox]

[CAPTURE: final installer page with the privacy note, the SimAppPro reminder and "Open Groundfeel now"]

Where things go:

| What | Where |
|---|---|
| The program | `%LOCALAPPDATA%\Programs\VibracionURSA` (installed for your user only) |
| Your settings and the log | `%APPDATA%\VibracionURSA` |
| Shortcut | Start menu → **Groundfeel** |
| Uninstall entry | Windows Settings → Apps → Installed apps |

### Step 4 — Find the tray icon

Look for the Groundfeel icon next to the clock. If you don't see it, click the small **^** arrow to show hidden icons. You can drag it onto the taskbar so it's always visible.

[CAPTURE: Windows taskbar with the hidden-icons area open and the Groundfeel icon highlighted]

---

## 4. First use: turn off SimAppPro's vibration

If SimAppPro's vibration is on, both programs fight over the same motors and you'll feel a mess of effects. Before your first flight:

1. Open **SimAppPro**.
2. Select the **URSA MINOR 32 joystick L**.
3. Turn its **vibration** off.
4. Do the same for the **throttle Metal R**.
5. Keep SimAppPro installed if you use it for buttons, axes or lights. Only the vibration has to be off.

[CAPTURE: SimAppPro with the joystick's vibration option turned off]

[CAPTURE: SimAppPro with the throttle's vibration option turned off]

Then:

1. Plug in your joystick and throttle (if they aren't already).
2. Start MSFS 2024 and load a flight.
3. Open **Settings** from the tray icon and check the **Status** box: you should see "Simulator connected" in green and both devices listed.

---

## 5. The tray icon and its menu

### The colored dot

| Dot | Meaning |
|---|---|
| Green | Connected to the simulator and receiving data |
| Gray | Waiting for the simulator |
| Orange | Vibration paused |

Hover over the icon to see the connection status and the devices found.

### Right-click menu

[CAPTURE: right-click menu of the tray icon]

| Item | What it does |
|---|---|
| Groundfeel 1.4.0 | Shows the installed version (not clickable) |
| Status line | Simulator connected or waiting, and the devices found (not clickable) |
| **Settings…** | Opens the Settings window (also the icon's default action) |
| **Pause vibration** | Turns all vibration off until you untick it |
| **Start with Windows** | Turns automatic start on or off |
| **Update to version X** | Only appears when a new version is available |
| **Check for updates** | Checks now and tells you the result |
| **View log** | Opens the log file, useful for troubleshooting |
| **Report a problem…** | Opens a pre-filled GitHub issue in your browser (see FAQ) |
| **Uninstall…** | Starts the Windows uninstaller |
| **Exit** | Closes the app and turns the motors off |

---

## 6. What you feel in each phase of flight

**Where the vibration goes:**

- The **joystick** carries ground effects: ground roll, touchdown, brakes and skid. By default it **only vibrates on the ground** and goes quiet once you're airborne. You can change that in Settings.
- The **throttle** carries engines, power changes and reverse, plus a share of everything else. **Each lever follows its own engine.**

When the simulator is paused, nothing vibrates.

> Engine hum, spool and reverse are based on turbine N1, so they may not appear on piston aircraft.

### Engine start

| What happens | What you feel | Where |
|---|---|---|
| Engine spinning up to idle | A rumble that grows as the engine gains speed | Throttle (that engine's lever) |
| Engine at idle | A minimum hum, barely noticeable | Throttle |

### Taxi

| What happens | What you feel | Where |
|---|---|---|
| Rolling on asphalt or concrete | A fine texture plus light bumps from slab joints and centerline lights, more frequent as you speed up | Joystick |
| Rolling on grass, gravel or dirt | Much rougher and more irregular than on asphalt | Joystick |
| Rolling in general | Joint bumps and a rumble that grow with speed | Throttle |
| Adding power to get moving | A short push while the engines spool up | Both |
| Turning too fast, tires sliding sideways | A rough, irregular vibration | Both |
| Braking | See [Brakes](#brakes) | Both |

At walking pace you barely feel anything. The ground roll gets stronger and quicker with speed, as in a real aircraft.

### Takeoff

| What happens | What you feel | Where |
|---|---|---|
| Thrust levers forward | A push while the engines spool, then a hum that grows with power | Throttle, a little in the joystick |
| Acceleration down the runway | A pulsation that follows the real acceleration | Both |
| Takeoff roll | Ground roll and joint bumps getting faster and stronger | Both |
| Liftoff | The joystick goes quiet (if "Joystick vibrates on the ground only" is on) | Joystick |

### Landing gear

| What happens | What you feel | Where |
|---|---|---|
| Gear starting to move (unlocking) | A dry bump, stronger at higher airspeed; then nothing while it travels | Throttle (and joystick if not ground-only) |
| Gear locking up or down | The main "clunk", with a small rebound | Throttle (and joystick if not ground-only) |
| Flying with the gear down | A light rumble that grows with airspeed | Throttle (and joystick if not ground-only) |

### Flaps and speedbrakes

| What happens | What you feel | Where |
|---|---|---|
| Flaps moving | A light vibration while they move; nothing once they stop | Throttle (and joystick if not ground-only) |
| Speedbrakes out in flight | A buffet that grows with deployment and airspeed | Throttle (and joystick if not ground-only) |
| Ground spoilers after touchdown | A vibration that fades as you slow down | Both |

### Cruise

| What happens | What you feel | Where |
|---|---|---|
| Steady flight | A soft engine hum that follows power | Throttle |
| Turbulence | Bumps that follow the real vertical jolts | Throttle (and joystick if not ground-only) |
| Approaching a stall / stall warning | Buffet | Throttle (and joystick if not ground-only) |

### Approach

| What happens | What you feel | Where |
|---|---|---|
| Gear down, flaps extending | The gear rumble and flap vibration described above | Throttle |
| Autothrust adjusting power | A steady hum that follows power, without loose pulses (fixed in 1.1.5) | Throttle |
| Speedbrakes | Buffet according to deployment and airspeed | Throttle |

### Touchdown

| What happens | What you feel | Where |
|---|---|---|
| Main wheels touching down | A bump proportional to your rate of descent: soft for a smooth landing, hard for a firm one. Even a very smooth landing gives a small bump. | Both |
| Rollout | Ground roll comes back on the joystick | Joystick |

Loading a flight already on the ground does **not** give a touchdown bump: it's only felt on a real landing, at speed.

### Reverse thrust

| What happens | What you feel | Where |
|---|---|---|
| Reversers deployed | A strong vibration on each engine's lever, growing with power | Throttle |

If the aircraft doesn't report reverse thrust to the simulator (for example the FlyByWire A320), Groundfeel detects it from high engine power while decelerating on the ground.

### Brakes

| What happens | What you feel | Where |
|---|---|---|
| Applying the brakes at speed | A first jolt as the nose dips (none when almost stopped) | Both |
| Braking | A wheel tremor that gets slower as you lose speed | Both |
| Hard braking at high speed | Irregular anti-skid pulses | Both |
| Coming to a stop after braking | A small bump as the nose settles | Both |

---

## 7. The Settings window, control by control

Open it from the tray icon → **Settings…**. **Every change applies within about two seconds, without restarting**, so you can tweak it with the simulator running.

[CAPTURE: full Settings window with its five sections: Status, Intensity, Options, Updates and the bottom buttons]

### Status

Live view, refreshed every second.

| Line | What it shows | Colors |
|---|---|---|
| Simulator | "Simulator connected" or "Waiting for the simulator"; "(paused)" when vibration is paused | Green connected · Gray waiting · Orange paused |
| Devices | The devices found: joystick, throttle | Green both · Orange only one · Red none |
| Vibrating | The effects vibrating right now (for example "ground roll, engines") | Blue when something is vibrating · Gray when nothing is |

[CAPTURE: Status box with "Simulator connected" in green, both devices and "Vibrating: ground roll, engines" in blue]

Effect names you may see in "Vibrating":

| Name | What it is |
|---|---|
| ground roll | Joystick ground roll (surface and speed) |
| rolling | Joints and rumble while rolling |
| bumps | Vertical jolts: uneven ground, turbulence |
| touchdown | Landing bump |
| gear | Gear moving, locking, or down in flight |
| flaps | Flaps moving |
| speedbrakes | Speedbrakes or ground spoilers |
| engines | Engine start and engine hum |
| reverse | Reverse thrust |
| brakes | Wheel brakes and anti-skid |
| acceleration | Spool and acceleration push |
| skid | Tires sliding sideways |
| stall | Stall buffet |

### Intensity

| Control | Range | What it does |
|---|---|---|
| **Joystick** | 0 – 100 % | Overall strength of everything the joystick does |
| **Throttle** | 0 – 100 % | Overall strength of everything the throttle does (both levers) |
| **Ground roll (joystick)** | 30 – 250 % | Strength of the joystick's ground roll only. 100 % is the default; move right for more, left for less |

Drag the slider and release it: the new value is saved when you let go. The number on the right shows the current value.

> Tip: if the taxi feels too busy but you like the touchdown and brakes, lower **Ground roll (joystick)** instead of **Joystick**.

### Options

| Control | What it does |
|---|---|
| **Joystick vibrates on the ground only** | On by default. The joystick goes quiet in flight; gear, flaps, turbulence and stall are only felt in the throttle. Untick it to feel them in the stick too |
| **Pause vibration** | Turns all vibration off (same as the tray menu) |
| **Start with Windows** | Starts the app with Windows (same as the tray menu) |
| **Language** | "Automatic (Windows)" or any of the 20 languages. The window redraws immediately in the new language |

### Updates

| Control | What it does |
|---|---|
| Installed version | The version you're running |
| Status line | "Not checked yet" · "Checking…" · "✔ Up to date (checked at HH:MM)" in green · "⬆ New version available: X" in blue · "Couldn't check: …" in red |
| **Check now** | Checks GitHub right away |
| **Update now** | Installs the new version right away. Only enabled when there is one. Vibration stops for a moment and the app reopens by itself |
| **Check for and install updates automatically** | On by default. Off means the app never connects to the internet on its own |

[CAPTURE: Updates section showing "⬆ New version available" in blue and the "Update now" button enabled]

### Bottom buttons

| Button | What it does |
|---|---|
| **Restore defaults** | Removes all your changes, including the language, and goes back to the default values |
| **Settings folder** | Opens `%APPDATA%\VibracionURSA`, where your settings and the log live |
| **Close** | Closes the window. The app keeps running in the tray |
| **Report a problem** | Same as the tray menu item: opens a pre-filled GitHub issue |

The gray line at the bottom reminds you to turn off SimAppPro's vibration.

### Advanced settings (optional)

Everything in the window covers normal use. For fine-tuning each effect (for example anti-skid strength), advanced users can edit `ajustes.json` in the settings folder. The README on GitHub explains it. The key names are in Spanish, and anything you put there survives updates.

---

## 8. Updates

| Question | Answer |
|---|---|
| How often does it check? | A few seconds after starting, then every 6 hours |
| When does it install? | Only when the simulator is **closed**, never mid-flight |
| Is it safe? | It downloads the same installer you'd download by hand, only from this project's GitHub releases, and refuses to run it unless it matches the SHA-256 published by GitHub |
| Do I lose my settings? | No |
| Can I update by hand? | Yes: tray menu → **Update to version X**, or **Settings → Update now** |
| Can I turn it off? | Yes: untick **Check for and install updates automatically** in Settings |

When a new version is found, Windows shows a notification and the tray menu gets an **Update to version X** item. If an update fails, the current version keeps running and the reason is in the log.

> **On 1.0.0 or 1.0.1?** Those early versions can't update themselves to the new installer. Download `VibracionURSA-Setup.exe` once and run it.

---

## 9. Languages

The app is available in 20 languages: English, Mandarin Chinese, Hindi, Spanish, French, Arabic, Bengali, Portuguese, Russian, Urdu, Indonesian, German, Japanese, Marathi, Telugu, Turkish, Tamil, Vietnamese, Korean and Italian.

- **Automatic (Windows)**: uses your Windows display language, or English if yours isn't available.
- To choose one: **Settings → Language**. It changes immediately, menus included.
- The installer itself is in English or Spanish only.
- Except for English and Spanish, the translations were made automatically. If you see a mistake, please report it on GitHub.

[CAPTURE: Language drop-down open in Settings showing the list of languages]

---

## 10. Uninstalling

1. Tray menu → **Uninstall…**, or Windows Settings → Apps → Installed apps → **Groundfeel** → Uninstall.
2. The uninstaller closes the app first and turns the motors off.
3. Confirm.

Your settings stay in `%APPDATA%\VibracionURSA` in case you reinstall. To remove everything, delete that folder after uninstalling.

If you want SimAppPro to handle vibration again, turn its vibration back on for the joystick and the throttle.

---

## 11. FAQ and troubleshooting

### Nothing vibrates

Check in this order:

1. **Is the app running?** Look for the icon in the tray. If it's not there, open **Groundfeel** from the Start menu.
2. **Open Settings → Status.**
   - "Waiting for the simulator" → see [It doesn't detect the simulator](#it-doesnt-detect-the-simulator).
   - "Devices: none found" in red → check the USB cables. The app looks for the devices again every 10 seconds, so you don't need to restart it.
   - "(paused)" in orange → untick **Pause vibration**.
3. **Is the simulator paused?** Nothing vibrates while MSFS is paused.
4. **Are you in the air with only the joystick?** By default the joystick only vibrates on the ground. Untick **Joystick vibrates on the ground only** if you want it in flight.
5. **Intensity at 0 %?** Check the sliders.
6. **Is SimAppPro's vibration really off?** If both programs drive the motors, the results are unpredictable.
7. **Piston aircraft?** Engine effects may not appear (they're based on turbine N1), but ground roll, touchdown and brakes still work.
8. Still nothing → tray menu → **View log** and attach it to an issue on GitHub.

### It vibrates all the time

- **SimAppPro's vibration is still on.** This is the most common cause. Turn it off for both devices.
- Look at **Settings → Status → Vibrating** to see which effect is active:
  - "engines" on the throttle with engines running is normal: there's a minimum hum at idle.
  - "ground roll" or "rolling" while stopped → you may be creeping forward slowly. Set the parking brake.
- Lower the intensity if a normal effect is simply too strong for you.
- Need silence for a moment? **Pause vibration** from the tray menu.

### Kaspersky or another antivirus blocks it

- Versions **1.0.x** were flagged by some antivirus products (for example Kaspersky, `PDM:Trojan.Win32.Generic`) because they installed themselves by copying the `.exe`. Update to 1.1.0 or later, which uses a standard installer.
- If your antivirus still blocks a current version:
  1. Make sure you downloaded it from the official release page, and compare its SHA-256 with the one shown there.
  2. If it matches, you can restore it from quarantine and add an exception for `%LOCALAPPDATA%\Programs\VibracionURSA`, following your antivirus' own instructions.
  3. Please open an issue on GitHub naming the antivirus and the detection, so it can be reported as a false positive.
- The code is public, every build is made by GitHub Actions from that code, and the app's only network connection is to GitHub for updates.

### A motor stayed vibrating

This happens if the app was closed abruptly (for example killed from Task Manager or a crash) while a motor was running.

1. Open **Groundfeel** again from the Start menu. When it starts, it turns the motors off.
2. If it's already running and the motor keeps going, choose **Exit** from the tray menu and open it again.
3. As a last resort, unplug and replug the device's USB cable.

To avoid it, always close the app with **Exit** from the tray menu.

### It doesn't detect the simulator

- Groundfeel is made for **MSFS 2024**.
- It connects by itself: there's no need to start it in any particular order. Give it a few seconds once a flight is loading or loaded.
- "Simulator connected" means it's receiving data from the aircraft.
- If it stays on "Waiting for the simulator" with a flight loaded:
  1. Choose **Exit** in the tray menu and open Groundfeel again from the Start menu.
  2. Check the log (**View log**) for errors and include it in an issue.

### Other questions

| Question | Answer |
|---|---|
| Do I need both devices? | No. It works with the joystick only, the throttle only, or both. With only one, the Devices line shows orange, which is just informational |
| Does it change my flight or my aircraft? | No. It only reads the simulator and only writes to the vibration motors |
| Does it work with MSFS 2020? | It's made and tested for MSFS 2024 |
| I opened it twice and nothing happened | Only one copy runs at a time. Look for the icon in the tray |
| The touchdown is too strong / too soft | It follows your descent rate. Adjust the overall strength with the **Joystick** and **Throttle** sliders |
| Where's the log? | Tray menu → **View log**, or `%APPDATA%\VibracionURSA\vibracion.log` |
| How do I report a bug or a translation mistake? | Tray menu → **Report a problem…**. It opens a GitHub issue already filled in with the version, Windows, devices, the last unexpected error and the last log lines, with your user name, user folder and computer name masked. Review it, describe what happened and submit it. Nothing is sent unless you submit it |
| It said "Groundfeel hit an unexpected error" | The details were saved in `%APPDATA%\VibracionURSA\errores\`. Use **Report a problem…** so it can be fixed |

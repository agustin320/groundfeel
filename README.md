# Vibración URSA

Vibración realista para el **WinWing URSA MINOR 32** (joystick L + throttle Metal R) en **Microsoft Flight Simulator 2024**.

Reemplaza la vibración de SimAppPro por efectos calculados a partir del estado real del avión: rodaje según la superficie y la velocidad, toque en pista, frenos con antibloqueo, spool de los motores, reversa, derrape, tren, flaps, frenos aerodinámicos y pérdida.

> **English summary:** realistic rumble for the WinWing URSA MINOR 32 joystick and throttle in MSFS 2024. It reads the sim via SimConnect and drives the devices' vibration motors over HID. Ground roll on the joystick uses a physical model: an ISO 8608 runway profile and a two-mass nose-gear model. Windows only. Comments and docs are in Spanish.

## Requisitos

- Windows 10/11 con Python 3.11 o superior.
- MSFS 2024 y su SDK. Del SDK se usa `SimConnect.dll`.
- WinWing URSA MINOR 32: joystick L y/o throttle Metal R.
- **La vibración de SimAppPro tiene que estar apagada** para estos dispositivos. Si no, los dos programas se pisan.

## Instalación

1. Descargá o cloná este repositorio.
2. Copiá `SimConnect.dll` a la carpeta del programa. Está en el SDK de MSFS 2024, en `SimConnect SDK\lib\SimConnect.dll`. Otra opción: definir la variable de entorno `SIMCONNECT_DLL` con su ruta.
3. Doble click en `instalar.bat` (una sola vez).

## Uso

1. Abrí el simulador.
2. Doble click en `iniciar_vibracion.bat`. Se abre una ventana: dejala abierta.
3. Para apagarlo, cerrá esa ventana. Los motores se apagan solos.

El programa se reconecta solo si el simulador todavía no abrió o si se reinicia. En pausa no vibra nada.

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

Por defecto el joystick vibra **sólo en tierra** (`"joystick_solo_en_tierra": true`).

## Ajustes (`config.json`)

Los cambios se aplican al guardar, sin reiniciar.

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
- `vibracion.py`:
  - Lazo principal a 40 Hz.
  - Una sola instancia a la vez.
  - Recarga `config.json` en caliente.
  - Apaga los motores al cerrar la ventana.
  - Registro en `vibracion.log`: sólo anota cuando cambian los efectos activos.

## Pruebas

```
venv\Scripts\python.exe pruebas.py
```

Escenarios sintéticos sin simulador ni hardware. Algunos ejemplos: parado, carreteo en asfalto contra pasto, despegue, crucero, pausa, aterrizaje suave contra duro, frenado, aceleración, motores, reversa, derrape y rodaje físico. Corren también en GitHub Actions en cada push.

## Problemas comunes

- **No vibra nada:**
  - Fijate en `vibracion.log` si dice `simulador conectado` y `Motores: joystick, throttle`.
  - Revisá que la vibración de SimAppPro esté apagada.
- **Un motor quedó vibrando:** pasa si el programa se cierra de golpe, por ejemplo matándolo desde el Administrador de tareas. Volvé a abrirlo: al arrancar apaga los motores.
- **Algo se siente demasiado fuerte o débil:** ajustá `config.json` y guardá.

## Créditos

- El protocolo HID de los motores se basó en [ursa-minor-ffb](https://github.com/rtroncoso/ursa-minor-ffb) de rtroncoso (MIT).
- Proyecto independiente, sin relación con WinWing ni con Microsoft.

## Licencia

MIT. Ver [LICENSE](LICENSE).

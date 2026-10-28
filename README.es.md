<div align="center">
<img src="assets/logo.png" alt="Logo de Groundfeel" width="220">

# ✈️ Groundfeel
### Vibración realista en tierra y en vuelo para joysticks y throttles WinWing

[![Licencia: MIT](https://img.shields.io/badge/Licencia-MIT-blue.svg)](LICENSE)
![Plataforma: Windows](https://img.shields.io/badge/Plataforma-Windows%2010%2F11-lightgrey.svg)
![Hecho en Python](https://img.shields.io/badge/Hecho%20en-Python%203.13-3776AB.svg)
[![Última versión](https://img.shields.io/github/v/release/agustin320/groundfeel)](../../releases/latest)
[![Descargas](https://img.shields.io/github/downloads/agustin320/groundfeel/total)](../../releases)

*Respuesta táctil para el joystick y el throttle **WinWing URSA MINOR 32** en **Microsoft Flight Simulator 2024**,
calculada a partir de lo que de verdad está haciendo tu avión.*

[English](README.md) · **Español** · 📖 [Guía de usuario](docs/GUIA_DE_USUARIO.md) · [Registro de cambios](CHANGELOG.md)

🚀 **Guía rápida:** [English](docs/quickstart/en.md) · [Español](docs/quickstart/es.md) · [中文](docs/quickstart/zh.md) · [हिन्दी](docs/quickstart/hi.md) · [Français](docs/quickstart/fr.md) · [العربية](docs/quickstart/ar.md) · [বাংলা](docs/quickstart/bn.md) · [Português](docs/quickstart/pt.md) · [Русский](docs/quickstart/ru.md) · [اردو](docs/quickstart/ur.md) · [Bahasa Indonesia](docs/quickstart/id.md) · [Deutsch](docs/quickstart/de.md) · [日本語](docs/quickstart/ja.md) · [मराठी](docs/quickstart/mr.md) · [తెలుగు](docs/quickstart/te.md) · [Türkçe](docs/quickstart/tr.md) · [தமிழ்](docs/quickstart/ta.md) · [Tiếng Việt](docs/quickstart/vi.md) · [한국어](docs/quickstart/ko.md) · [Italiano](docs/quickstart/it.md)

</div>

---

## 🌟 Qué es

Groundfeel reemplaza la vibración de SimAppPro por efectos calculados a partir del estado real del avión: un modelo
físico de rodaje que distingue asfalto de pasto y un Cessna de un A350, frenos con antibloqueo, reversa, toque en
pista y apoyo de la rueda de nariz, arranque y spool de motores, tren, flaps y slats, frenos aerodinámicos,
sobrevelocidad y pérdida. Vive en la bandeja del sistema, se actualiza sola, habla 20 idiomas y te deja armar tus
propios efectos.

<img src="assets/screenshot-effects.png" alt="Ventana Efectos de Groundfeel: intensidad, ruteo y barra en vivo por efecto" width="640">

Cada efecto incorporado tiene su intensidad y se puede mandar al joystick, al throttle, a los dos o a ninguno. La
barra de la derecha lo muestra en vivo.

*Antes "Vibración URSA" / "URSA Rumble". Proyecto independiente, sin relación con WinWing ni con Microsoft.*

| Simulador | Conexión | Notas |
|---|---|---|
| Microsoft Flight Simulator 2024 | SimConnect | Cualquier avión; perfiles por avión y L:Vars |
| Microsoft Flight Simulator 2020 | SimConnect | Sin probar: se agradecen reportes |

| Hardware | Estado |
|---|---|
| WinWing URSA MINOR 32 Joystick L | ✅ Verificado |
| WinWing URSA MINOR 32 Throttle Metal R | ✅ Verificado |
| Otros modelos WinWing / WINCTRL | Previstos para una versión siguiente |

## 📥 Descarga e instalación

1. Bajá `VibracionURSA-Setup.exe` de la [última versión](../../releases/latest).
2. Abrilo. Es un instalador estándar (Inno Setup) que instala sólo para tu usuario, sin permisos de administrador, en
   `%LOCALAPPDATA%\Programs\VibracionURSA`, con acceso en el menú Inicio y desinstalador.
3. **Apagá la vibración de SimAppPro** para el joystick y el throttle, así los dos programas no se pisan.

> Hasta que las versiones salgan firmadas (ver [Política de firma de código](#política-de-firma-de-código)), Windows
> SmartScreen puede avisar que el editor no es conocido: elegí "Más información → Ejecutar de todas formas". Cada
> versión la arma GitHub Actions a partir del código de este repositorio, y en la página de la versión figura el
> SHA-256 de cada archivo.

### Primer uso

Groundfeel vive en la **bandeja del sistema**, junto al reloj, y **arranca con Windows** (opción del instalador que
podés destildar). Cuando abrís el simulador se conecta solo. Clic derecho en el ícono → **Ajustes** muestra si el
simulador y los dispositivos están conectados y qué efectos están vibrando; **Efectos…** abre las tarjetas de
efectos, el monitor en vivo y el editor.

### Actualizaciones

Son automáticas. La app consulta GitHub unos segundos después de arrancar y después cada 6 horas. Con el simulador
cerrado (nunca en pleno vuelo) baja el instalador nuevo sólo de las versiones de este repositorio, exige que coincida
el SHA-256 que publica GitHub (si falta o no coincide, no actualiza), lo corre en silencio y te avisa cuando terminó.
También podés usar "Buscar actualizaciones" o apagar la búsqueda automática en Ajustes. Tus ajustes se conservan.

**Desinstalar:** menú de la bandeja → "Desinstalar…", o "Aplicaciones instaladas" de Windows. Tus ajustes quedan en
`%APPDATA%\VibracionURSA`.

## 🚀 Funciones principales

### 1. 🛬 Física de suelo según superficie y peso
- Un perfil de pista ISO 8608 más las juntas de las losas alimenta un modelo de tren de nariz de dos masas, integrado
  cada 2,5 ms y escalado por el **peso real** del avión. Pasto, ripio y tierra sacuden mucho más que el asfalto; un
  Cessna vibra más rápido y más seco que un A350.
- La fuerza del **toque** sigue a la velocidad de descenso, y después la **rueda de nariz** apoya con su propio golpe,
  más suave. Durante 0,8 s lo demás se calla para que el toque no quede tapado.

### 2. 🛑 Frenos, antibloqueo, reversa y derrape
- Un tirón inicial, un temblor que se hace más lento con las ruedas, pulsos de antibloqueo y un golpecito al detenerte.
- **Reversa** en la palanca de cada motor, deducida de N1 y la desaceleración en los aviones que no la publican
  (A32NX de FlyByWire).
- Una vibración áspera cuando las ruedas derrapan de costado.

### 3. ✈️ Eventos de vuelo
- **Tren de aterrizaje:** un golpe al destrabarse y un "clunk" con un rebote chico al trabarse; nada mientras recorre.
- **Flaps y slats:** los dos cuentan como movimiento, así se cubren los aviones cuyos slats se mueven solos.
- **Frenos aerodinámicos:** sólo con los dos lados desplegados, así los spoilers de alabeo en un viraje nunca los
  disparan.
- **Sobrevelocidad:** crece con cuánto pasaste la velocidad máxima del avión (barber pole).
- **Pérdida:** un buffet que crece con el ángulo de ataque, antes de la bocina.
- **Turbulencia:** los golpes verticales reales, sólo en el joystick.

### 4. 🔥 Motores, palanca por palanca
- Cada palanca del throttle sigue a su motor. Con 1 motor, las dos palancas; con 3, el central en las dos; con 4, los
  motores 1-2 en la palanca izquierda y 3-4 en la derecha.
- **Arranque por etapas:** rampa del starter (golpes de arranque en motores a pistón), un golpe en la ignición,
  aceleración hasta el ralentí y una caída suave si el arranque se aborta. Después, un zumbido que crece con la
  potencia: N1 en jets, RPM en pistón y turbohélice.

### 5. 🧩 Perfiles por avión y L:Vars
- Los perfiles (`perfiles/*.json`) se aplican solos según el nombre del avión y pueden leer las **L:Vars** propias del
  avión: se declaran en `"lvars"` y en `"fuentes"` se elige qué variable estándar reemplaza cada una. Una L:Var que el
  avión no tiene vale 0 y se usa la variable estándar.
- **Grabar vuelo** (menú de la bandeja o Ajustes) guarda los datos del simulador en
  `%APPDATA%\VibracionURSA\grabaciones\` para afinar perfiles con vuelos reales.

### 6. 🛠️ Armá tus propios efectos
<img src="assets/screenshot-editor.png" alt="Editor de efectos de Groundfeel: curva, forma y la salida real del motor" width="640">

- **Cualquier variable:** elegí una variable del simulador o escribí una L:Var y su unidad.
- **Cuándo se dispara:** siempre, por encima, por debajo, entre, prendido/apagado o mientras cambia, con histéresis.
- **Curva de respuesta** que dibujás con el mouse (clic para agregar un punto, arrastrar, clic derecho para borrar) y
  una **forma**: constante, pulso, golpe, seno o sierra, hasta 12,5 Hz.
- **Mirá lo que de verdad recibe el motor:** la vista previa corre el mismo motor que el lazo en vivo (50 Hz, zona
  muerta, pulsado debajo de ella y empujón de arranque), no una curva ideal.
- **Probar en el dispositivo** lo hace sonar 5 s en tu hardware; **Reproducir una grabación** pasa uno de tus vuelos
  grabados por el efecto.
- Arrancá desde una plantilla (Golpe, Zumbido, Pulsación, Creciente), mandalo al joystick, al throttle o a los dos,
  sumalo o tomá el máximo, y si querés **reemplazá** un efecto incorporado. Los efectos se comparten como JSON.

### 7. 📈 Monitor en vivo
- La salida de cada motor en los últimos 10 segundos y todas las variables del simulador que la app está leyendo, en
  vivo.
- El lazo corre a 50 Hz fijos con el timer de Windows a 1 ms, y cada minuto registra en el log su cadencia real (p50 /
  p99 / máx).

### 8. 🌍 20 idiomas · 🔒 privacidad
- Inglés, chino mandarín, hindi, castellano, francés, árabe, bengalí, portugués, ruso, urdu, indonesio, alemán,
  japonés, maratí, telugu, turco, tamil, vietnamita, coreano e italiano. Sigue a Windows; se cambia en Ajustes.
- **Sin telemetría.** "Reportar un problema" abre un issue de GitHub prellenado con tu carpeta de usuario, tu nombre de
  usuario y el de tu PC tapados; vos lo revisás y decidís si lo mandás.

## 🎮 Efectos en detalle

| Efecto | Qué sentís | Dónde |
|---|---|---|
| Rodaje | Modelo físico según superficie, velocidad y peso. | Joystick |
| Rodadura | Golpes de las juntas y un rumor que crecen con la velocidad. | Throttle |
| Toque | Un golpe según la velocidad de descenso, y después la rueda de nariz. | Ambos |
| Frenos | Tirón, temblor de las ruedas, pulsos de antibloqueo, golpe al detenerse. | Ambos |
| Motores | Arranque por etapas, mínimo en ralentí, zumbido con la potencia, por palanca. | Throttle |
| Spool / aceleración | Un empujón cuando sube la potencia y después la aceleración real. | Ambos |
| Reversa | Vibración fuerte en la palanca de cada motor. | Throttle |
| Derrape | Vibración áspera cuando las ruedas se deslizan de costado. | Ambos |
| Tren, flaps/slats, frenos aerodinámicos, pérdida, sobrevelocidad | Según su estado. | Ambos |
| Turbulencia | Los golpes verticales reales en vuelo. | Joystick |

Por defecto el joystick vibra **sólo en tierra**; destildalo en Ajustes para sentir los efectos de vuelo también en
el bastón. Todo se puede re-rutear en **Efectos…**.

### Ajustes avanzados

`config.json` tiene los valores por defecto (viene con cada versión: no lo edites). Tus cambios van en
`ajustes.json`, en `%APPDATA%\VibracionURSA` (Ajustes → "Carpeta de ajustes"), con la misma estructura; por ejemplo
`{"frenos": {"antibloqueo": 0.5}}`. Se aplican al guardar, sin reiniciar. Claves principales: `ganancia_general`,
`zona_muerta`, `mezcla`, `ruteo`, `intensidad_efecto`, `efectos_propios`, `rodaje_fisico` y un bloque por efecto.

## 🛠️ Requisitos y compilación

- Windows 10/11, MSFS 2024, WinWing URSA MINOR 32 joystick L y/o throttle Metal R.

```
instalar.bat                            (una vez: entorno de Python y dependencias)
venv\Scripts\python.exe bandeja.py      (la app de la bandeja desde el código)
venv\Scripts\python.exe pruebas.py      (pruebas, sin simulador ni hardware)
venv\Scripts\pyinstaller VibracionURSA.spec
ISCC /DVersion=1.7.0 instalador.iss     (necesita Inno Setup 6)
```

Cómo funciona: `sim_lector.py` (SimConnect, sólo lectura) → `efectos.py` + `rodaje_fisico.py` + `efectos_propios.py`
→ `motores.py` (HID, reporte `0x02` + `[pieza LE, 00, 00, 03, 49, índice, valor]`), todo movido por
`motor_vibracion.py` a 50 Hz. Para publicar: subir `version.py` y empujar un tag `vX.Y.Z`; GitHub Actions prueba,
compila y publica. `recursos/SimConnect.dll` es la biblioteca cliente redistribuible del SDK de MSFS 2024 de Microsoft.

**Problemas comunes:** Ajustes muestra la conexión con el simulador y los dispositivos encontrados; "Ver registro"
tiene el detalle. Si un motor quedó vibrando porque la app se cerró de golpe, abrila de nuevo: apaga los motores al
arrancar.

## 📌 Agradecimientos

- El protocolo HID de los motores se basa en [ursa-minor-ffb](https://github.com/rtroncoso/ursa-minor-ffb) de
  rtroncoso (MIT).
- Varias ideas de los eventos de vuelo (simetría de spoilers, slats, sobrevelocidad contra la barber pole, toque por
  pata, arranque por etapas) y el editor de efectos se inspiraron en
  [Aurora Vibra](https://github.com/chegevarko1982/aurora-vibra) (MIT), una gran opción si volás en X-Plane o War
  Thunder.

## Política de firma de código

La política oficial (Code signing policy) está en el [README en inglés](README.md#code-signing-policy). En resumen:
todavía no hay firma (la solicitud a SignPath Foundation no fue aprobada); cuando esté, sólo se van a firmar los
binarios que arma GitHub Actions desde el código de este repositorio, y cada pedido de firma se aprueba a mano.

### Privacidad

No se manda ningún dato personal y no hay telemetría. La única conexión de red es a GitHub (`api.github.com` y las
descargas de versiones) para buscar y bajar actualizaciones, unos segundos después de arrancar y cada 6 horas, y se
puede apagar en Ajustes. Como en cualquier pedido web, GitHub recibe tu dirección IP y la versión de la app; aplica la
[declaración de privacidad de GitHub](https://docs.github.com/site-policy/privacy-policies/github-general-privacy-statement).
El programa lee el simulador por SimConnect y escribe sólo en los motores de vibración de WinWing. "Iniciar con
Windows" agrega un valor en `HKCU\Software\Microsoft\Windows\CurrentVersion\Run`, que el desinstalador borra.
Licencias de terceros: `THIRD-PARTY-NOTICES.txt`.

## 📜 Licencia

MIT. Ver [LICENSE](LICENSE).

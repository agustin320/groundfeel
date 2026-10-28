# Groundfeel — Manual de usuario

Versión 1.6 · Para pilotos con el WinWing URSA MINOR 32 en Microsoft Flight Simulator 2024

> En inglés la app se llama **Groundfeel**. Es el mismo programa: el nombre cambia según el idioma.

---

## Contenido

1. [Qué hace Groundfeel](#1-qué-hace-groundfeel)
2. [Qué necesitás](#2-qué-necesitás)
3. [Instalación](#3-instalación)
4. [Primer uso: apagar la vibración de SimAppPro](#4-primer-uso-apagar-la-vibración-de-simapppro)
5. [El ícono de la bandeja y su menú](#5-el-ícono-de-la-bandeja-y-su-menú)
6. [Qué se siente en cada fase del vuelo](#6-qué-se-siente-en-cada-fase-del-vuelo)
7. [La ventana de Ajustes, control por control](#7-la-ventana-de-ajustes-control-por-control)
8. [Actualizaciones](#8-actualizaciones)
9. [Idiomas](#9-idiomas)
10. [Desinstalar](#10-desinstalar)
11. [Preguntas frecuentes y solución de problemas](#11-preguntas-frecuentes-y-solución-de-problemas)

---

## 1. Qué hace Groundfeel

Groundfeel es una app gratuita y de código abierto (licencia MIT) que maneja los motores de vibración del **joystick L** y del **throttle Metal R** del **WinWing URSA MINOR 32**. Reemplaza la vibración de SimAppPro por efectos basados en lo que hace tu avión en MSFS 2024: la superficie por la que rodás, la velocidad, qué tan fuerte aterrizás y frenás, la potencia de los motores, la reversa, el tren, los flaps y más.

- Vive tranquila en la **bandeja del sistema** de Windows, junto al reloj.
- Se conecta sola al simulador cuando abrís MSFS.
- Sólo **lee** el simulador. Nunca cambia nada de tu vuelo.
- No envía datos personales. Su única conexión a internet es buscar actualizaciones en GitHub, y se puede apagar.

> Groundfeel es un proyecto independiente, sin relación con WinWing ni con Microsoft.

---

## 2. Qué necesitás

| Qué | Detalle |
|---|---|
| Sistema operativo | Windows 10 u 11 |
| Simulador | Microsoft Flight Simulator 2024 |
| Hardware | WinWing URSA MINOR 32: joystick L, throttle Metal R, o los dos |
| SimAppPro | Puede seguir instalado, pero **su vibración tiene que estar apagada** para estos dos dispositivos (ver [sección 4](#4-primer-uso-apagar-la-vibración-de-simapppro)) |
| Permisos de administrador | No hacen falta |

---

## 3. Instalación

### Paso 1 — Bajar el instalador

1. Entrá a la última versión: https://github.com/agustin320/vibracion-ursa/releases/latest
2. En **Assets**, bajá **`VibracionURSA-Setup.exe`**.

[CAPTURA: página de la versión en GitHub con la sección "Assets" abierta y VibracionURSA-Setup.exe resaltado]

> Bajá el instalador sólo desde esa página. Ahí figura el SHA-256 del archivo, por si lo querés verificar.

### Paso 2 — Pasar el aviso de SmartScreen

El instalador todavía no está firmado, así que Windows puede mostrar una ventana azul que dice **"Windows protegió su PC"** y que el editor es desconocido. Es lo normal con apps nuevas sin firma.

1. Hacé click en **Más información**.
2. Hacé click en **Ejecutar de todas formas**.

[CAPTURA: ventana de SmartScreen "Windows protegió su PC" con el enlace "Más información" resaltado]

[CAPTURA: la misma ventana después de "Más información", con el botón "Ejecutar de todas formas" resaltado]

### Paso 3 — Correr el instalador

1. Elegí el idioma del instalador (inglés o castellano).
2. Aceptá la licencia (MIT).
3. Elegí si querés **Iniciar con Windows**. Recomendado: la app espera en la bandeja sin hacer vibrar nada hasta que abrís el simulador, y no tenés que acordarte de abrirla.
4. Hacé click en **Instalar**.
5. En la última pantalla, leé las notas de privacidad y de SimAppPro, dejá tildado **"Abrir Groundfeel ahora"** y hacé click en **Finalizar**.

[CAPTURA: pantalla del instalador con la casilla "Iniciar con Windows"]

[CAPTURA: pantalla final del instalador con la nota de privacidad, el recordatorio de SimAppPro y "Abrir Groundfeel ahora"]

Dónde queda cada cosa:

| Qué | Dónde |
|---|---|
| El programa | `%LOCALAPPDATA%\Programs\VibracionURSA` (sólo para tu usuario) |
| Tus ajustes y el registro | `%APPDATA%\VibracionURSA` |
| Acceso directo | Menú Inicio → **Groundfeel** |
| Para desinstalar | Configuración de Windows → Aplicaciones → Aplicaciones instaladas |

### Paso 4 — Encontrar el ícono en la bandeja

Buscá el ícono junto al reloj. Si no lo ves, hacé click en la flechita **^** que muestra los íconos ocultos. Lo podés arrastrar a la barra de tareas para tenerlo siempre a la vista.

[CAPTURA: barra de tareas de Windows con los íconos ocultos desplegados y el ícono de Groundfeel resaltado]

---

## 4. Primer uso: apagar la vibración de SimAppPro

Si la vibración de SimAppPro queda prendida, los dos programas se pelean por los mismos motores y se siente cualquier cosa. Antes del primer vuelo:

1. Abrí **SimAppPro**.
2. Elegí el **joystick L del URSA MINOR 32**.
3. Apagá su **vibración**.
4. Hacé lo mismo con el **throttle Metal R**.
5. Si usás SimAppPro para botones, ejes o luces, dejalo instalado. Sólo tiene que estar apagada la vibración.

[CAPTURA: SimAppPro con la opción de vibración del joystick apagada]

[CAPTURA: SimAppPro con la opción de vibración del throttle apagada]

Después:

1. Enchufá el joystick y el throttle, si no lo están.
2. Abrí MSFS 2024 y cargá un vuelo.
3. Abrí **Ajustes** desde el ícono de la bandeja y mirá el recuadro **Estado**: tendría que decir "Simulador conectado" en verde y mostrar los dos dispositivos.

---

## 5. El ícono de la bandeja y su menú

### El punto de color

| Punto | Qué significa |
|---|---|
| Verde | Conectado al simulador y recibiendo datos |
| Gris | Esperando al simulador |
| Naranja | Vibración en pausa |

Si dejás el mouse sobre el ícono, ves el estado de la conexión y los dispositivos encontrados.

### Menú con click derecho

[CAPTURA: menú del ícono de la bandeja abierto con click derecho]

| Opción | Qué hace |
|---|---|
| Groundfeel 1.2.0 | Muestra la versión instalada (no se puede tocar) |
| Línea de estado | Simulador conectado o esperando, y los dispositivos encontrados (no se puede tocar) |
| **Ajustes…** | Abre la ventana de Ajustes (también es la acción por defecto del ícono) |
| **Pausar vibración** | Apaga toda la vibración hasta que la destildes |
| **Iniciar con Windows** | Prende o apaga el arranque automático |
| **Actualizar a la versión X** | Sólo aparece cuando hay una versión nueva |
| **Buscar actualizaciones** | Busca en el momento y te avisa el resultado |
| **Ver registro** | Abre el archivo de registro, útil si algo falla |
| **Reportar un problema…** | Abre en el navegador un issue de GitHub ya completo (ver preguntas frecuentes) |
| **Desinstalar…** | Abre el desinstalador de Windows |
| **Salir** | Cierra la app y apaga los motores |

---

## 6. Qué se siente en cada fase del vuelo

**Adónde va la vibración:**

- El **joystick** lleva lo que pasa en el suelo: rodaje, toque, frenos y derrape. Por defecto **vibra sólo en tierra** y se queda quieto cuando despegás. Se cambia en Ajustes.
- El **throttle** lleva los motores, los cambios de potencia y la reversa, más una parte de todo lo demás. **Cada palanca sigue a su motor.**

Con el simulador en pausa no vibra nada.

> Los efectos de motor siguen el N1 en los jets y las RPM en los aviones a pistón y turbohélice. La reversa sólo se deduce en jets.

### Puesta en marcha

| Qué pasa | Qué se siente | Dónde |
|---|---|---|
| El motor gana vueltas hasta el ralentí | Un rumor que crece a medida que el motor toma vueltas | Throttle (la palanca de ese motor) |
| Motor en ralentí | Un zumbido mínimo, apenas perceptible | Throttle |

### Rodaje

| Qué pasa | Qué se siente | Dónde |
|---|---|---|
| Rodar sobre asfalto u hormigón | Una textura fina y golpecitos de las juntas de las losas y las luces de eje, más seguidos cuanto más rápido vas | Joystick |
| Rodar sobre pasto, ripio o tierra | Mucho más áspero e irregular que en asfalto | Joystick |
| Rodar en general | Golpecitos de juntas y un rumor que crecen con la velocidad | Throttle |
| Dar potencia para arrancar | Un empuje corto mientras los motores toman vueltas | Ambos |
| Girar demasiado rápido, con las ruedas yendo de costado | Una vibración áspera e irregular | Ambos |
| Frenar | Ver [Frenos](#frenos) | Ambos |

A paso de hombre casi no se siente nada. El rodaje se vuelve más fuerte y más rápido con la velocidad, como en un avión real.

### Despegue

| Qué pasa | Qué se siente | Dónde |
|---|---|---|
| Palancas adelante | Un empuje mientras los motores toman vueltas, y después un zumbido que crece con la potencia | Throttle, un poco en el joystick |
| Aceleración en la pista | Una pulsación que acompaña la aceleración real | Ambos |
| Carrera de despegue | Rodaje y golpes de juntas cada vez más rápidos y fuertes | Ambos |
| Al dejar el suelo | El joystick se queda quieto (si está tildado "El joystick vibra sólo en tierra") | Joystick |

### Tren de aterrizaje

| Qué pasa | Qué se siente | Dónde |
|---|---|---|
| Tren empezando a moverse (se destraba) | Un golpe seco, más fuerte con más velocidad; después nada mientras se mueve | Throttle (y joystick si no está en "sólo en tierra") |
| Tren trabando arriba o abajo | El "clunk" principal, con un rebote chico | Throttle (y joystick si no está en "sólo en tierra") |
| Volar con el tren abajo | Un rumor suave que crece con la velocidad | Throttle (y joystick si no está en "sólo en tierra") |

### Flaps y frenos aerodinámicos

| Qué pasa | Qué se siente | Dónde |
|---|---|---|
| Flaps moviéndose | Una vibración suave mientras se mueven; nada cuando se quedan quietos | Throttle (y joystick si no está en "sólo en tierra") |
| Frenos aerodinámicos afuera en vuelo | Un sacudón que crece con la apertura y la velocidad | Throttle (y joystick si no está en "sólo en tierra") |
| Spoilers en tierra después del toque | Una vibración que se apaga a medida que frenás | Ambos |

### Crucero

| Qué pasa | Qué se siente | Dónde |
|---|---|---|
| Vuelo estable | Un zumbido de motor suave que sigue a la potencia | Throttle |
| Turbulencia | Sacudones que siguen a los golpes verticales reales | Sólo joystick, si destildás "El joystick vibra sólo en tierra" (al throttle nunca llega) |
| Cerca de la pérdida / aviso de pérdida | Buffet | Throttle (y joystick si no está en "sólo en tierra") |

### Aproximación

| Qué pasa | Qué se siente | Dónde |
|---|---|---|
| Tren abajo, flaps saliendo | El rumor del tren y la vibración de los flaps que se describen arriba | Throttle |
| Autothrust corrigiendo potencia | Un zumbido parejo que sigue a la potencia, sin pulsos sueltos (arreglado en la 1.1.5) | Throttle |
| Frenos aerodinámicos | Sacudón según la apertura y la velocidad | Throttle |

### Toque

| Qué pasa | Qué se siente | Dónde |
|---|---|---|
| Las ruedas principales tocan la pista | Un golpe proporcional a la velocidad de descenso: suave si aterrizás suave, fuerte si aterrizás firme. Hasta un aterrizaje muy suave da un golpecito. | Ambos |
| Carrera de aterrizaje | Vuelve el rodaje en el joystick | Joystick |

Cargar un vuelo que ya arranca en tierra **no** da golpe de toque: sólo se siente en un aterrizaje de verdad, con velocidad.

### Reversa

| Qué pasa | Qué se siente | Dónde |
|---|---|---|
| Reversores desplegados | Una vibración fuerte en la palanca de cada motor, que crece con la potencia | Throttle |

Si el avión no le informa la reversa al simulador (por ejemplo, el A320 de FlyByWire), Groundfeel la deduce de la potencia alta mientras el avión desacelera en tierra.

### Frenos

| Qué pasa | Qué se siente | Dónde |
|---|---|---|
| Frenar con velocidad | Un primer golpe cuando la nariz se hunde (nada si estás casi parado) | Ambos |
| Frenando | Un temblor de ruedas que se hace más lento a medida que perdés velocidad | Ambos |
| Frenada fuerte a alta velocidad | Pulsos irregulares del antibloqueo | Ambos |
| Detenerse después de frenar | Un golpecito cuando la nariz se asienta | Ambos |

---

## 7. La ventana de Ajustes, control por control

Se abre desde el ícono de la bandeja → **Ajustes…**. **Cada cambio se aplica en unos dos segundos, sin reiniciar**, así que la podés ajustar con el simulador andando.

[CAPTURA: ventana de Ajustes completa con sus cinco partes: Estado, Intensidad, Opciones, Actualizaciones y los botones de abajo]

### Estado

Vista en vivo, se refresca cada segundo.

| Línea | Qué muestra | Colores |
|---|---|---|
| Simulador | "Simulador conectado" o "Esperando al simulador"; "(en pausa)" si la vibración está en pausa | Verde conectado · Gris esperando · Naranja en pausa |
| Dispositivos | Los dispositivos encontrados: joystick, throttle | Verde los dos · Naranja sólo uno · Rojo ninguno |
| Vibrando | Los efectos que están vibrando en ese momento (por ejemplo "rodaje, motores") | Azul si algo vibra · Gris si no vibra nada |

[CAPTURA: recuadro Estado con "Simulador conectado" en verde, los dos dispositivos y "Vibrando: rodaje, motores" en azul]

Nombres de efectos que podés ver en "Vibrando":

| Nombre | Qué es |
|---|---|
| rodaje | Rodaje del joystick (superficie y velocidad) |
| rodadura | Juntas y rumor al rodar |
| sacudones | Golpes verticales: pista despareja, turbulencia |
| toque | Golpe del toque |
| tren | Tren moviéndose, trabando o abajo en vuelo |
| flaps | Flaps moviéndose |
| frenos aerod. | Frenos aerodinámicos (speedbrakes) o spoilers en tierra |
| motores | Puesta en marcha y zumbido de motor |
| reversa | Reversa |
| frenos | Frenos de ruedas y antibloqueo |
| aceleración | Spool y empuje al acelerar |
| derrape | Ruedas yendo de costado |
| pérdida | Buffet de pérdida |

### Intensidad

| Control | Rango | Qué hace |
|---|---|---|
| **Joystick** | 0 – 100 % | Fuerza general de todo lo que hace el joystick |
| **Throttle** | 0 – 100 % | Fuerza general de todo lo que hace el throttle (las dos palancas) |
| **Rodaje (joystick)** | 30 – 250 % | Fuerza sólo del rodaje en el joystick. 100 % es el valor por defecto; a la derecha es más, a la izquierda menos |

Arrastrá el deslizador y soltalo: el valor se guarda al soltar. El número de la derecha muestra el valor actual.

> Consejo: si el rodaje te resulta demasiado movido pero te gustan el toque y los frenos, bajá **Rodaje (joystick)** en lugar de **Joystick**.

### Opciones

| Control | Qué hace |
|---|---|
| **El joystick vibra sólo en tierra** | Prendido por defecto. El joystick se queda quieto en vuelo; tren, flaps y pérdida se sienten sólo en el throttle, y la turbulencia no se siente. Destildalo para sentirlos también en el bastón |
| **Pausar la vibración** | Apaga toda la vibración (igual que en el menú de la bandeja) |
| **Iniciar con Windows** | Abre la app al iniciar Windows (igual que en el menú de la bandeja) |
| **Idioma** | "Automático (Windows)" o cualquiera de los 20 idiomas. La ventana se redibuja al instante en el idioma nuevo |

### Actualizaciones

| Control | Qué hace |
|---|---|
| Versión instalada | La versión que estás usando |
| Línea de estado | "Todavía no se consultó" · "Buscando…" · "✔ Está actualizada (consultado a las HH:MM)" en verde · "⬆ Hay una versión nueva: X" en azul · "No se pudo consultar: …" en rojo |
| **Buscar ahora** | Consulta GitHub en el momento |
| **Actualizar ahora** | Instala la versión nueva en el momento. Sólo se habilita cuando hay una. La vibración se corta un instante y la app se vuelve a abrir sola |
| **Buscar e instalar actualizaciones automáticamente** | Prendido por defecto. Apagado, la app nunca se conecta sola a internet |

[CAPTURA: sección Actualizaciones con "⬆ Hay una versión nueva" en azul y el botón "Actualizar ahora" habilitado]

### Botones de abajo

| Botón | Qué hace |
|---|---|
| **Valores por defecto** | Borra todos tus cambios, incluido el idioma, y vuelve a los valores de fábrica |
| **Carpeta de ajustes** | Abre `%APPDATA%\VibracionURSA`, donde están tus ajustes y el registro |
| **Cerrar** | Cierra la ventana. La app sigue en la bandeja |
| **Reportar un problema** | Igual que en el menú de la bandeja: abre un issue de GitHub ya completo |

La línea gris de abajo te recuerda apagar la vibración de SimAppPro.

### Ajustes avanzados (opcional)

La ventana cubre el uso normal. Para afinar cada efecto (por ejemplo, la fuerza del antibloqueo), los usuarios avanzados pueden editar `ajustes.json` en la carpeta de ajustes. El README de GitHub lo explica. Lo que pongas ahí se conserva en las actualizaciones.

---

## 8. Actualizaciones

| Pregunta | Respuesta |
|---|---|
| ¿Cada cuánto busca? | Unos segundos después de abrirse, y después cada 6 horas |
| ¿Cuándo instala? | Sólo con el simulador **cerrado**, nunca en pleno vuelo |
| ¿Es seguro? | Baja el mismo instalador que bajarías a mano y lo verifica contra el SHA-256 que publica GitHub antes de correrlo |
| ¿Pierdo mis ajustes? | No |
| ¿Puedo actualizar a mano? | Sí: menú de la bandeja → **Actualizar a la versión X**, o **Ajustes → Actualizar ahora** |
| ¿Se puede apagar? | Sí: destildá **Buscar e instalar actualizaciones automáticamente** en Ajustes |

Cuando encuentra una versión nueva, Windows muestra una notificación y aparece **Actualizar a la versión X** en el menú de la bandeja. Si una actualización falla, sigue andando la versión actual y el motivo queda en el registro.

> **¿Tenés la 1.0.0 o la 1.0.1?** Esas primeras versiones no pueden pasarse solas al instalador nuevo. Bajá `VibracionURSA-Setup.exe` una vez y corrélo.

---

## 9. Idiomas

La app está en 20 idiomas: inglés, chino mandarín, hindi, castellano, francés, árabe, bengalí, portugués, ruso, urdu, indonesio, alemán, japonés, maratí, telugu, turco, tamil, vietnamita, coreano e italiano.

- **Automático (Windows)**: usa el idioma de Windows, o inglés si el tuyo no está.
- Para elegir uno: **Ajustes → Idioma**. Cambia al instante, menús incluidos.
- El instalador en sí está sólo en inglés o castellano.
- Salvo inglés y castellano, las traducciones se hicieron automáticamente. Si ves un error, avisá en GitHub.

[CAPTURA: lista desplegable de Idioma abierta en Ajustes, con los idiomas disponibles]

---

## 10. Desinstalar

1. Menú de la bandeja → **Desinstalar…**, o Configuración de Windows → Aplicaciones → Aplicaciones instaladas → **Groundfeel** → Desinstalar.
2. El desinstalador primero cierra la app y apaga los motores.
3. Confirmá.

Tus ajustes quedan en `%APPDATA%\VibracionURSA` por si lo volvés a instalar. Para no dejar nada, borrá esa carpeta después de desinstalar.

Si querés que SimAppPro vuelva a manejar la vibración, prendé de nuevo su vibración para el joystick y el throttle.

---

## 11. Preguntas frecuentes y solución de problemas

### No vibra nada

Revisá en este orden:

1. **¿La app está abierta?** Buscá el ícono en la bandeja. Si no está, abrí **Groundfeel** desde el menú Inicio.
2. **Abrí Ajustes → Estado.**
   - "Esperando al simulador" → ver [No detecta el simulador](#no-detecta-el-simulador).
   - "Dispositivos: ninguno encontrado" en rojo → revisá los cables USB. La app vuelve a buscar los dispositivos cada 10 segundos, así que no hace falta reiniciarla.
   - "(en pausa)" en naranja → destildá **Pausar la vibración**.
3. **¿El simulador está en pausa?** Con MSFS en pausa no vibra nada.
4. **¿Estás en el aire y sólo mirás el joystick?** Por defecto el joystick vibra sólo en tierra. Destildá **El joystick vibra sólo en tierra** si lo querés también en vuelo.
5. **¿La intensidad está en 0 %?** Revisá los deslizadores.
6. **¿La vibración de SimAppPro está realmente apagada?** Si los dos programas manejan los motores, el resultado es impredecible.
7. **¿Avión a pistón o turbohélice?** Los efectos de motor siguen las RPM en vez del N1, y la reversa no se deduce. El rodaje, el toque y los frenos funcionan igual.
8. Si sigue sin vibrar → menú de la bandeja → **Ver registro** y adjuntalo en un issue de GitHub.

### Vibra todo el tiempo

- **La vibración de SimAppPro sigue prendida.** Es la causa más común. Apagala para los dos dispositivos.
- Mirá **Ajustes → Estado → Vibrando** para ver qué efecto está activo:
  - "motores" en el throttle con los motores andando es normal: en ralentí queda un zumbido mínimo.
  - "rodaje" o "rodadura" con el avión parado → puede que te estés moviendo muy despacio. Poné el freno de estacionamiento.
- Bajá la intensidad si un efecto normal te resulta demasiado fuerte.
- ¿Necesitás silencio un rato? **Pausar vibración** desde el menú de la bandeja.

### Kaspersky u otro antivirus lo bloquea

- Las versiones **1.0.x** fueron marcadas por algunos antivirus (por ejemplo Kaspersky, `PDM:Trojan.Win32.Generic`) porque se instalaban solas copiando el `.exe`. Actualizá a la 1.1.0 o posterior, que usa un instalador estándar.
- Si tu antivirus igual bloquea una versión actual:
  1. Asegurate de haberla bajado de la página oficial de versiones y compará su SHA-256 con el que figura ahí.
  2. Si coincide, podés sacarla de cuarentena y agregar una excepción para `%LOCALAPPDATA%\Programs\VibracionURSA`, siguiendo las instrucciones de tu antivirus.
  3. Abrí un issue en GitHub con el nombre del antivirus y de la detección, para reportarlo como falso positivo.
- El código es público, cada versión la arma GitHub Actions a partir de ese código, y la única conexión de red de la app es a GitHub para las actualizaciones.

### Un motor quedó vibrando

Pasa si la app se cerró de golpe (por ejemplo, matándola desde el Administrador de tareas o por un cuelgue) con un motor andando.

1. Volvé a abrir **Groundfeel** desde el menú Inicio. Al arrancar, apaga los motores.
2. Si ya estaba abierta y el motor sigue, elegí **Salir** en el menú de la bandeja y abrila de nuevo.
3. Como último recurso, desenchufá y volvé a enchufar el cable USB del dispositivo.

Para evitarlo, cerrá siempre la app con **Salir** desde el menú de la bandeja.

### No detecta el simulador

- Groundfeel está hecha para **MSFS 2024**.
- Se conecta sola: no hace falta abrir las cosas en un orden especial. Dale unos segundos cuando el vuelo está cargando o ya cargado.
- "Simulador conectado" significa que está recibiendo datos del avión.
- Si se queda en "Esperando al simulador" con un vuelo cargado:
  1. Elegí **Salir** en el menú de la bandeja y volvé a abrir Groundfeel desde el menú Inicio.
  2. Revisá el registro (**Ver registro**) por si hay errores e incluilo en un issue.

### Otras preguntas

| Pregunta | Respuesta |
|---|---|
| ¿Necesito los dos dispositivos? | No. Funciona sólo con el joystick, sólo con el throttle, o con los dos. Con uno solo la línea de Dispositivos se ve en naranja, que es sólo informativo |
| ¿Cambia algo de mi vuelo o de mi avión? | No. Sólo lee el simulador y sólo escribe en los motores de vibración |
| ¿Anda con MSFS 2020? | Está hecha y probada para MSFS 2024. En MSFS 2020 no está probada: si la usás, contanos cómo te fue en un issue |
| La abrí dos veces y no pasó nada | Corre una sola copia a la vez. Buscá el ícono en la bandeja |
| El toque se siente muy fuerte / muy suave | Sigue a tu velocidad de descenso. La fuerza general se ajusta con los deslizadores **Joystick** y **Throttle** |
| ¿Dónde está el registro? | Menú de la bandeja → **Ver registro**, o `%APPDATA%\VibracionURSA\vibracion.log` |
| ¿Cómo aviso de un error o de una traducción mal hecha? | https://github.com/agustin320/vibracion-ursa/issues — si podés, adjuntá el registro |

### Reportar un problema

Menú de la bandeja → **Reportar un problema…** (o el botón en Ajustes). Se abre en el navegador un issue de GitHub ya completo con la versión, Windows, los dispositivos, el último error inesperado y las últimas líneas del registro. Tu nombre de usuario, tu carpeta de usuario y el nombre del equipo van tapados. Lo revisás, contás qué pasó y lo mandás: no se envía nada si vos no lo mandás.

Si aparece el aviso «Groundfeel tuvo un error inesperado», el detalle quedó guardado en `%APPDATA%\VibracionURSA\errores\`: usá **Reportar un problema…** para que se pueda arreglar.

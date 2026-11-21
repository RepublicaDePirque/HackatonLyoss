# Implementación del prototipo

Cómo está construida la app (`index.html`) respecto del diseño (`docs/PRD.md`, `design/`). Última actualización: 21 de noviembre de 2026.

## Pantallas

Todo vive en `index.html`, una pantalla a la vez (el botón «atrás» del teléfono vuelve a la anterior).

| Pantalla | Qué hace | Plantilla de origen |
|---|---|---|
| Portada | El logo sobre fondo oscuro (el del propio logo, sin importar el tema del teléfono) y «Toca para empezar»; al tocar entra a Permiso. `?debug`, `?demo` y `#mapa` la saltan. El logo es una versión reducida (`assets/logo/logo-portada.jpg`, 25 KB) del original de 1,2 MB, con un borde difuminado para que no se vea su cuadrado. Viene activa en el HTML: se pinta antes de que cargue el JavaScript. | — |
| Permiso | Explica la señal (incluido el color de la luz: azul lejos, roja cerca) y pide ubicación y brújula con un toque (requisito de iPhone). Alternativas: ver solo el mapa (el plano sin destino: tocar un edificio lo vuelve destino) o un recorrido de ejemplo. Si el permiso falla, dice por qué y qué hacer, en español y sin la ruta de ajustes de iPhone. | `Permiso.tpl.html` |
| Buscar | «Está pasando» (eventos en curso), «Cerca de ti» (aparece con la primera posición del GPS, y la lista se reordena sola), «Próximos eventos» (14 días) y «Todos los destinos» (37), ordenados por distancia en línea recta. Los destinos que repiten un edificio (Casino, Arquitectura, Física, Informática, Humanísticos y Admisión) salen solo al buscarlos. Busca por nombre, lugar o letra («C»), y también eventos; el rótulo del buscador queda para lectores de pantalla. Marca «con fotos». Estado vacío. El pie dice «Distancias en línea recta.», «Buscando tu ubicación…» o «Activa la ubicación para ver qué tan lejos queda cada lugar.». Botón de Ajustes. Ver `docs/eventos-y-trayecto.md`. |
| Ajustes | Hoja desde «¿A dónde vas?»: «Voy apurado», «Modo voz», «Voz de la app» (solo con el modo voz encendido) y una leyenda del color de la luz (azul lejos, rojo cerca). El modo voz ya no se activa desde la brújula; «Activar con modo voz (sin mirar la pantalla)» sigue en la bienvenida. | — | `Buscar.tpl.html` |
| Brújula | Luz en el borde (el «resplandor»; color OKLCH: azul lejos, morado, rojo cerca), flecha o mapa, con selector fijo (Luz / Flecha / Mapa). Cifra en metros al centro, mensaje de estado, pista siempre visible. Sin ubicación aparece «Activar ubicación»; esperando el GPS, el título dice «Buscando tu ubicación…». La luz y la flecha se describen al lector de pantalla («Edificio A queda a tu derecha»). Sin destino (el plano), la pastilla dice «Plano del campus» y no hay selector ni «Ya llegué»; el modo voz no habla. | `Brujula.tpl.html` |
| Tarjetas | Por fases (`docs/eventos-y-trayecto.md`): nada en los primeros 15 m; después, una a la vez, un evento en curso cerca del camino («Ir ahí» lo vuelve destino) o un dato curioso de la zona (tocar la tarjeta abre una hoja con «Seguir caminando»), con 30 m entre tarjetas, y cada una se retira sola a los 60 m; a 60 m o menos, «Así se ve al llegar» con la foto del lado por el que llegas (si es de otro lado, lo dice). Van dentro de la base de la brújula, sobre la pista, también en el modo mapa. Con 500 px de alto o menos no se muestran (la foto igual se ve en «¿Es este el lugar?»). «Voy apurado» apaga las del camino. | `Brujula.tpl.html` |
| Confirmar llegada | Cuando el GPS detecta que estás adentro de la zona (a una profundidad proporcional al tamaño de la zona: 60 % de lo más adentro que se puede estar, entre 1,5 y 4,5 m; las zonas chicas exigen 1,6 a 2,4 m y los edificios grandes 4,5 m), se abre «¿Es este el lugar?» con la foto del destino para compararla con lo que ves; sin foto muestra la letra y el detalle. «Sí, llegué» pasa a la llegada; «Aún no llego» lo pospone hasta que te alejes 25 m. «Reportar esta foto» está en esta hoja (solo para fotos de la comunidad). «Ya llegué» también pregunta si el destino tiene foto. En el recorrido de ejemplo se confirma sola a los 3,5 s. |
| Llegada | Tras confirmar: «¿Sabías que…?», tomar y publicar una foto; no muestra la foto del lugar (se vio al acercarte y en «¿Es este el lugar?»). Sin foto de la comunidad, invita a tomar la primera. «Aún no llego» vuelve a la brújula y «Elegir otro destino» a la búsqueda. | `Llegada.tpl.html` |
| Recorrido de ejemplo | De la Entrada Av. Los Placeres al Edificio A, de unos 35 s, con dato en el trayecto, foto y llegada. Sin píldora aparte: la pastilla del destino lleva la etiqueta «ejemplo» y se sale con el botón atrás. | `Demo.tpl.html` |

Ajustes, la hoja del dato y «¿Es este el lugar?» son `<dialog>` abiertos con `showModal()`: dejan inerte el resto, llevan el foco al título y se cierran con Escape o tocando afuera (en «¿Es este el lugar?» equivale a «Aún no llego»).

Tema claro y oscuro según el teléfono. Con «reducir movimiento» se quitan las animaciones. Tipografías (Chakra Petch e Instrument Sans) alojadas en `fonts/` para que la PWA funcione sin conexión.

## Archivos

| Archivo | Contenido | Se regenera con |
|---|---|---|
| `index.html` | Interfaz y lógica | A mano |
| `js/generado/grafo.js` | Caminos del campus y destinos, desde OpenStreetMap | `python3 tools/generar-grafo.py` (necesita internet) |
| `js/generado/contornos.js` | Contornos de edificios y patios (los 37 destinos tienen cuadro), y destinos extra | `python3 tools/contornos.py` (necesita numpy, scipy, matplotlib y pillow) |
| `js/generado/datos.js` | Nombre, letra, detalle, pista y foto (con su lado) de cada destino, y los eventos | `python3 tools/generar-datos.py` (lee `data/edificios.json` y `data/eventos.json`) |
| `data/eventos.json` | Eventos curados por el equipo. Los actuales son de ejemplo (`ejemplo: true`, con horario relativo a cuando se abre la app) y la app los marca «ejemplo» | A mano |
| `assets/img/` | Mapas del diseño (claro y oscuro) y fotos con licencia libre de A, B y F | — |
| `assets/fuentes.css`, `assets/fonts/` | Tipografías | — |
| `js/fotos.js` | Comprimir, publicar, leer y reportar fotos compartidas (Firestore) | A mano |
| `js/escaleras.js` | «Evitar escaleras»: compara caminos y cuenta escaleras. Con el botón activo, cada tramo de escalera suma 400 m de costo en vez de quedar prohibido, así que si no hay camino sin escaleras se entrega el de menos | A mano (prueba: `node tests/probar-escaleras.js`) |
| `js/voz.js` | Modo voz para personas ciegas | A mano (prueba: `node tests/probar-voz.js`) |
| `sw.js` | Caché para usarla sin conexión | Subir `CACHE` al cambiar archivos |

## Cómo probarla

| Enlace | Para qué |
|---|---|
| `/` | Flujo real (pide GPS y brújula; necesita HTTPS) |
| `/?demo` | Arranca directo el recorrido de ejemplo |
| `/?voz` | Activa el modo voz con la voz de la app (`js/voz.js`); se combina con `demo` o `debug` |
| `/?debug` | Panel para mover la posición y el rumbo sin GPS; el mapa dibuja los caminos y tocar el plano te mueve |
| `/#mapa` | Abre directo en modo mapa |
| `/?tema=claro` o `?tema=oscuro` | Fuerza el tema |

Se pueden combinar: `/?debug&tema=claro`.

## Dónde la implementación se aparta del PRD

- **El mapa puede girar con el rumbo** (botón ↻, apagado por defecto). El PRD decidió que no gira; por defecto se respeta (orientación del plano) y el giro es opcional. Una brújula con la N, arriba a la izquierda bajo la cabecera, marca dónde queda el norte porque el plano no está orientado así; los controles y el crédito de OpenStreetMap van sobre la base medida.
- **El resplandor se mueve en 0,7 s** (posición) y 1,4 s (tamaño y color), no 1,4 s en todo: con la brújula del teléfono emitiendo decenas de lecturas por segundo, 1,4 s en la posición se sentía arrastrado.
- **Las fotos de la comunidad se publican en Firestore** (`js/fotos.js`, reglas en `firebase/firestore.rules`; JPEG de máximo 1024 px y ≤ 290 000 caracteres, que es lo que aceptan las reglas). Se piden al elegir el destino y `fotoDe()` las lee de una caché en memoria, porque se llama al dibujar. Sin conexión la foto queda en el teléfono (`localStorage`). Las reglas exigen el lado del edificio desde el que se tomó (`ladoFoto()`: N, E, S u O). Con 3 reportes una foto deja de mostrarse; borrarlas es manual, desde la consola de Firebase. La pantalla de publicar avisa que la foto pasa a dominio público (CC0).
- **«Vas bien»** solo aparece si no te estás alejando (compara con lo más cerca que estuviste en los últimos 20 s), por la crítica de diseño que señala que el mensaje fijo refuerza rumbos equivocados.
- **El color del resplandor va de azul a rojo pasando por morado** (el diseño iba de azul a naranja). Cada luz es un degradado que llega a transparente en el borde de su caja, sin `filter: blur`: el desenfoque dejaba ver la caja cuadrada en algunos móviles. Además las luces se difuminan con una máscara cerca del borde de arriba y de abajo y su centro entra 56 px en la pantalla: en Safari el borde de la página no es el de la pantalla (hay barras del navegador y del sistema) y cortar la luz en seco, justo donde es más fuerte, dibujaba un rectángulo. La barra fina queda fuera de la máscara, en el borde. El resplandor, la barra y la flecha giran con un suavizado por tiempo (`senal` en `index.html`) por el camino más corto, así que 359° → 1° no da una vuelta entera ni se arrastra con cada lectura del GPS.
- **Calibración del plano**: la app usa 0,4601 m/px y 155,3°; `data/georef.json` da 0,4666 m/px y 154,8°. Las dos coinciden a 1 a 6 m (máximo en los bordes del plano), así que no hay desfase relevante. Si se unifican, hay que cambiar también `tools/generar-grafo.py`.

## Entradas de los edificios

La señal apunta a la **puerta** del edificio (no a su borde) y la ruta termina ahí.

- **Datos:** `data/entradas.json` es la fuente (exportado de `marcar-entradas.html`). `python3 tools/generar-entradas.py` lo valida y escribe `js/generado/entradas.js`. Hoy hay 41 puertas en 20 edificios (42 marcadas, una descartada), marcadas a mano sobre el plano, **aproximadas**: falta afinarlas en terreno.
- **En la app:** cada puerta es un nodo del grafo, unido al camino más cercano que no atraviese el edificio. Si el destino tiene varias, elige la de menor costo desde donde estás (se recalcula cada 1,5 s y no cambia de puerta por menos de 20 m de diferencia).
- **Evitar escaleras:** una puerta marcada «con escalera» cuenta como un tramo de escalera, así que con la opción activa se prefiere una puerta sin escaleras si existe. Si no existe (B, F y T no tienen ninguna marcada), usa la que hay: nunca queda sin ruta. Con la opción apagada también pesa un poco (15 m).
- **Pista y mapa:** la pista muestra «Entrada principal · con escalera» y el mapa dibuja las puertas del destino (verde sin escaleras, rojo con escalera, gris sin confirmar), con un aro en la elegida.
- **La llegada no cambia:** sigue midiéndose contra la zona del edificio (ver arriba), no contra la puerta.
- **Destinos que comparten edificio:** Casino, Arquitectura, Comedores y Gimnasio 1 usan solo las puertas cuyo nombre los menciona (`PUERTA_PALABRA` en `index.html`).
- **Sin puertas marcadas** (Federación, Entrada Placeres, Comedores, Gimnasio 1 sin puertas propias, patios y canchas) la señal sigue apuntando al borde.
- **Puertas descartadas:** el generador omite las que quedan a más de 25 m de su edificio. Hoy una: «Entrada calle edificio IDP» (asignada al R, queda a 52 m; es el Edificio Matta/IDP, que no es un destino).
- **Para agregar o afinar:** marcar en `marcar-entradas.html`, guardar el JSON en `data/entradas.json` y correr el generador. La prueba `node tests/probar-entradas.js` valida los datos.

## Pasos por dentro de edificios

Atajos que cruzan un edificio de puerta a puerta (un pasillo del A, por ejemplo). La ruta los usa cuando acortan el camino.

- **Cómo marcarlos:** en `marcar-entradas.html`, cambiar a **«Pasos»** arriba. Tocar la puerta de partida (el punto se pega a la puerta ya marcada), tocar cada esquina del pasillo y terminar en la otra puerta; luego «Terminar paso» y completar la descripción, si se puede pasar sin escaleras y un aviso opcional (por ejemplo «solo en horario de clases»). Tocar un paso guardado lo edita. «Cargar lo guardado en el proyecto» trae `data/entradas.json` (puertas y pasos) para seguir desde ahí.
- **Datos:** el JSON exportado trae `entradas` y `pasos`. Guardarlo en `data/entradas.json` y correr `python3 tools/generar-entradas.py` (valida, y avisa si un extremo no coincide con una puerta o si un paso mide más de 250 m).
- **En la app:** cada punto del trazo es un nodo del grafo; los extremos se unen a la puerta marcada a 6 m o menos (si no hay, al camino más cercano). Los tramos cuentan por su largo real, sin penalización. Si el paso está marcado «con escalera», pesa como una escalera y «evitar escaleras» lo esquiva.
- **Aviso en la ruta:** «Atajo por dentro (Edificio A) en unos 20 m» y, ya adentro, «Vas por dentro (Edificio A)», con el aviso del paso al final. En el mapa el tramo va con puntos (las escaleras van con rayas).
- **Posición:** estando dentro del edificio, la posición se ajusta al paso; desde la calle no (si no, te «pegaría» a un pasillo al otro lado del muro).
- **Cadenas:** un paso puede visitar varias puertas seguidas (los pasillos del B y del C se marcaron así). Cualquier punto del trazo que caiga a 6 m o menos de una puerta es esa puerta, no solo los extremos. Cada tramo entre dos puertas es una recta, aunque el pasillo real tenga esquinas.
- **Hoy hay 11 pasos** (A ×4, B, C, D, F, M, P y R2). Sobre los 820 pares de puertas, 505 (61 %) acortan, con una mediana de 77 m y un máximo de 753 m. Casi todo lo grande viene de P2, que antes quedaba sin conexión (rodeo de ~800 m) y ahora se llega por el paso P→P2 (46 m). 12 pares suman unos metros pero evitan escaleras (cada tramo con escalera pesa 15 m); ninguno cuesta más que antes.
- **Pasos «con escalera»:** el de R2 («Escaleras R»), el de M (entre pisos) y el A «entrada principal a biblioteca y patio central» cuentan como escalera.
- **Limitación:** no hay forma de saber si un pasillo está abierto a cierta hora; el campo de aviso es la única forma de advertirlo.


## Herramienta temporal: marcar entradas

`marcar-entradas.html` (en Pages: `/marcar-entradas.html`) sirve para levantar la puerta de cada edificio y exportar un `entradas.json`. No es parte de la app ni de su caché; se borra cuando las entradas estén integradas.

- Elige el edificio arriba (o toca cerca de uno: lo detecta a 20 m y pega la puerta a su borde si está a 8 m o menos), toca la puerta en el plano y guarda con una descripción y si se puede entrar sin escaleras (sí, no, no sé).
- «⌖» muestra tu ubicación y «Marcar donde estoy» marca con el GPS (avisa si la precisión es peor que ±15 m; tocar el plano es más preciso).
- Se guarda solo en el teléfono mientras se trabaja. «Lista» muestra el avance, los edificios que faltan y el resultado para copiar, descargar o compartir.
- Tocar una marca la edita o la borra. Admite varias puertas por edificio.

## Supuestos en los contornos

- **Comedores** es la parte norte del bloque D (OpenStreetMap lo dibuja separado; el plano lo trae dentro del cuadro de D). Su contorno sale de OSM recortado al cuadro de D. Elegir «Edificio D» también se cumple al entrar a Comedores, porque está dentro de D.
- **Innovación Tecnológica** se asignó al edificio rotulado «Edificio Bari» en el plano (borde izquierdo): tiene la misma forma que el polígono de OSM y queda en el mismo lugar, pero es una inferencia, **por confirmar**.
- **Cafetería Vivendum** es el Edificio Q (confirmado por el equipo, igual que en OpenStreetMap). Su contorno es el edificio que el plano oficial rotula «O».

## Contenido de ejemplo que hay que reemplazar

`ZONAS` y `SABIAS` en `tools/generar-datos.py` salen de las plantillas del diseño y **no están verificados**: el dato «Era el hall de montaje» (Edificio C) y el «Sabías que» del reloj del A y del C. Ver `docs/pendientes-datos.md`, sección 4.

## Lo que no está probado

La interfaz se probó ejecutando su código con un DOM simulado (flujo, estados, recorrido de ejemplo, mapa, tema claro y oscuro), no en un teléfono. Falta revisar en uno real: el aspecto de las pantallas, el desempeño de los gestos del mapa, la brújula con el teléfono en la mano y la cámara para tomar la foto.

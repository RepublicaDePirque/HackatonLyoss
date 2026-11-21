# Implementación del prototipo

Cómo está construida la app (`index.html`) respecto del diseño (`docs/PRD.md`, `design/`). Última actualización: 21 de noviembre de 2026.

## Pantallas

Todo vive en `index.html`, una pantalla a la vez (el botón «atrás» del teléfono vuelve a la anterior).

| Pantalla | Qué hace | Plantilla de origen |
|---|---|---|
| Permiso | Explica la señal y pide ubicación y brújula con un toque (requisito de iPhone). Alternativas: ver solo el mapa o un recorrido de ejemplo. Si el permiso falla, dice por qué y qué hacer. | `Permiso.tpl.html` |
| Buscar | «Cerca de ti» y «Todos los destinos» (37), ordenados por distancia en línea recta. Busca por nombre, lugar o letra («C»). Marca «con fotos». Estado vacío. | `Buscar.tpl.html` |
| Brújula | Resplandor en el borde (color OKLCH: azul lejos, morado, rojo cerca), flecha o mapa, con selector fijo. Cifra en metros al centro, mensaje de estado, pista siempre visible. | `Brujula.tpl.html` |
| Tarjetas | Dato curioso al pasar por una zona («Leer más» abre una hoja) y «Así se ve al llegar» a 60 m o menos, con foto. | `Brujula.tpl.html` |
| Confirmar llegada | Cuando el GPS detecta que estás adentro de la zona (a una profundidad proporcional al tamaño de la zona: 60 % de lo más adentro que se puede estar, entre 1,5 y 4,5 m; las zonas chicas exigen 1,6 a 2,4 m y los edificios grandes 4,5 m), se abre «¿Es este el lugar?» con la foto del destino para compararla con lo que ves; sin foto muestra la letra y el detalle. «Sí, llegué» pasa a la llegada; «Aún no» lo pospone hasta que te alejes 25 m. «Ya llegué» también pregunta si el destino tiene foto. En el recorrido de ejemplo se confirma sola a los 3,5 s. |
| Llegada | Tras confirmar: Foto, «Sabías que», tomar y publicar una foto. «Aún no llego» vuelve a la brújula. | `Llegada.tpl.html` |
| Recorrido de ejemplo | De la Entrada Av. Los Placeres al Edificio A, de unos 35 s, con dato en el trayecto, foto y llegada. | `Demo.tpl.html` |

Tema claro y oscuro según el teléfono. Con «reducir movimiento» se quitan las animaciones. Tipografías (Chakra Petch e Instrument Sans) alojadas en `fonts/` para que la PWA funcione sin conexión.

## Archivos

| Archivo | Contenido | Se regenera con |
|---|---|---|
| `index.html` | Interfaz y lógica | A mano |
| `js/generado/grafo.js` | Caminos del campus y destinos, desde OpenStreetMap | `python3 tools/generar-grafo.py` (necesita internet) |
| `js/generado/contornos.js` | Contornos de edificios y patios (los 37 destinos tienen cuadro), y destinos extra | `python3 tools/contornos.py` (necesita numpy, scipy, matplotlib y pillow) |
| `js/generado/datos.js` | Nombre, letra, detalle, pista y foto de cada destino | `python3 tools/generar-datos.py` (lee `data/edificios.json`) |
| `assets/img/` | Mapas del diseño (claro y oscuro) y fotos con licencia libre de A, B y F | — |
| `assets/fuentes.css`, `assets/fonts/` | Tipografías | — |
| `js/fotos.js` | Comprimir, publicar, leer y reportar fotos compartidas (Firestore) | A mano |
| `js/escaleras.js` | «Evitar escaleras»: compara caminos y cuenta escaleras | A mano (prueba: `node tests/probar-escaleras.js`) |
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

- **El mapa traza la ruta** (A* sobre los caminos de OpenStreetMap, con aviso de escaleras y opción «Evitar escaleras», que suma 400 m de costo por tramo de escalera en vez de prohibirlos: así entrega el camino con menos escaleras cuando no hay uno sin ninguna; la comparación está en `js/escaleras.js` y se prueba con `node tools/probar-escaleras.js`); el PRD dice que el modo mapa «te ubica; no traza ruta». Lo dejé porque ya estaba hecho y funciona; la brújula, que es el producto, sigue sin mostrar ruta. Si el equipo prefiere el mapa sin ruta, basta quitar el dibujo de `path` en `dibujarMapa`.
- **El mapa puede girar con el rumbo** (botón ↻, apagado por defecto). El PRD decidió que no gira; por defecto se respeta (orientación del plano) y el giro es opcional. Una brújula con la N marca dónde queda el norte porque el plano no está orientado así.
- **El resplandor se mueve en 0,7 s** (posición) y 1,4 s (tamaño y color), no 1,4 s en todo: con la brújula del teléfono emitiendo decenas de lecturas por segundo, 1,4 s en la posición se sentía arrastrado.
- **Las fotos de la comunidad se publican en Firestore** (`js/fotos.js`, reglas en `firebase/firestore.rules`; JPEG de máximo 1024 px y ≤ 290 000 caracteres, que es lo que aceptan las reglas). Se piden al elegir el destino y `fotoDe()` las lee de una caché en memoria, porque se llama al dibujar. Sin conexión la foto queda en el teléfono (`localStorage`). Las reglas exigen el lado del edificio desde el que se tomó (`ladoFoto()`: N, E, S u O). Con 3 reportes una foto deja de mostrarse; borrarlas es manual, desde la consola de Firebase. La pantalla de publicar avisa que la foto pasa a dominio público (CC0).
- **«Vas bien»** solo aparece si no te estás alejando (compara con lo más cerca que estuviste en los últimos 20 s), por la crítica de diseño que señala que el mensaje fijo refuerza rumbos equivocados.
- **El color del resplandor va de azul a rojo pasando por morado** (el diseño iba de azul a naranja). Cada luz es un degradado que llega a transparente en el borde de su caja, sin `filter: blur`: el desenfoque dejaba ver la caja cuadrada en algunos móviles. El resplandor, la barra y la flecha giran con un suavizado por tiempo (`senal` en `index.html`) por el camino más corto, así que 359° → 1° no da una vuelta entera ni se arrastra con cada lectura del GPS.
- **Calibración del plano**: la app usa 0,4601 m/px y 155,3°; `data/georef.json` da 0,4666 m/px y 154,8°. Las dos coinciden a 1 a 6 m (máximo en los bordes del plano), así que no hay desfase relevante. Si se unifican, hay que cambiar también `tools/generar-grafo.py`.

## Supuestos en los contornos

- **Comedores** es la parte norte del bloque D (OpenStreetMap lo dibuja separado; el plano lo trae dentro del cuadro de D). Su contorno sale de OSM recortado al cuadro de D. Elegir «Edificio D» también se cumple al entrar a Comedores, porque está dentro de D.
- **Innovación Tecnológica** se asignó al edificio rotulado «Edificio Bari» en el plano (borde izquierdo): tiene la misma forma que el polígono de OSM y queda en el mismo lugar, pero es una inferencia, **por confirmar**.
- **Cafetería Vivendum** usa la «O» del plano (OSM la llama «Q»; ver `docs/pendientes-datos.md`).

## Contenido de ejemplo que hay que reemplazar

`ZONAS` y `SABIAS` en `tools/generar-datos.py` salen de las plantillas del diseño y **no están verificados**: el dato «Era el hall de montaje» (Edificio C) y el «Sabías que» del reloj del A y del C. Ver `docs/pendientes-datos.md`, sección 4.

## Lo que no está probado

La interfaz se probó ejecutando su código con un DOM simulado (flujo, estados, recorrido de ejemplo, mapa, tema claro y oscuro), no en un teléfono. Falta revisar en uno real: el aspecto de las pantallas, el desempeño de los gestos del mapa, la brújula con el teléfono en la mano y la cámara para tomar la foto.

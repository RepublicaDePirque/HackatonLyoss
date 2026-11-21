# Implementación del prototipo

Cómo está construida la app (`index.html`) respecto del diseño (`docs/PRD.md`, `design/`). Última actualización: 21 de noviembre de 2026.

## Pantallas

Todo vive en `index.html`, una pantalla a la vez (el botón «atrás» del teléfono vuelve a la anterior).

| Pantalla | Qué hace | Plantilla de origen |
|---|---|---|
| Permiso | Explica la señal y pide ubicación y brújula con un toque (requisito de iPhone). Alternativas: ver solo el mapa o un recorrido de ejemplo. Si el permiso falla, dice por qué y qué hacer. | `Permiso.tpl.html` |
| Buscar | «Cerca de ti» y «Todos los destinos» (37), ordenados por distancia en línea recta. Busca por nombre, lugar o letra («C»). Marca «con fotos». Estado vacío. | `Buscar.tpl.html` |
| Brújula | Resplandor en el borde (color OKLCH, frío→cálido según cercanía), flecha o mapa, con selector fijo. Cifra en metros al centro, mensaje de estado, pista siempre visible. | `Brujula.tpl.html` |
| Tarjetas | Dato curioso al pasar por una zona («Leer más» abre una hoja) y «Así se ve al llegar» a 60 m o menos, con foto. | `Brujula.tpl.html` |
| Llegada | Automática al estar adentro del cuadro del edificio o patio, al menos 3 m bajo el borde (menos en zonas angostas); botón «Ya llegué» por si el GPS falla. Foto, «Sabías que», tomar y publicar una foto. «Aún no llego» vuelve a la brújula. | `Llegada.tpl.html` |
| Recorrido de ejemplo | De la Entrada Av. Los Placeres al Edificio A, de unos 35 s, con dato en el trayecto, foto y llegada. | `Demo.tpl.html` |

Tema claro y oscuro según el teléfono. Con «reducir movimiento» se quitan las animaciones. Tipografías (Chakra Petch e Instrument Sans) alojadas en `fonts/` para que la PWA funcione sin conexión.

## Archivos

| Archivo | Contenido | Se regenera con |
|---|---|---|
| `index.html` | Interfaz y lógica | A mano |
| `grafo.js` | Caminos del campus y destinos, desde OpenStreetMap | `python3 tools/generar-grafo.py` (necesita internet) |
| `contornos.js` | Contornos de edificios y patios (los 37 destinos tienen cuadro), y destinos extra | `python3 tools/contornos.py` (necesita numpy, scipy, matplotlib y pillow) |
| `datos.js` | Nombre, letra, detalle, pista y foto de cada destino | `python3 tools/generar-datos.py` (lee `data/edificios.json`) |
| `img/` | Mapas del diseño (claro y oscuro) y fotos con licencia libre de A, B y F | — |
| `fuentes.css`, `fonts/` | Tipografías | — |
| `sw.js` | Caché para usarla sin conexión | Subir `CACHE` al cambiar archivos |

## Cómo probarla

| Enlace | Para qué |
|---|---|
| `/` | Flujo real (pide GPS y brújula; necesita HTTPS) |
| `/?demo` | Arranca directo el recorrido de ejemplo |
| `/?debug` | Panel para mover la posición y el rumbo sin GPS; el mapa dibuja los caminos y tocar el plano te mueve |
| `/#mapa` | Abre directo en modo mapa |
| `/?tema=claro` o `?tema=oscuro` | Fuerza el tema |

Se pueden combinar: `/?debug&tema=claro`.

## Dónde la implementación se aparta del PRD

- **El mapa traza la ruta** (A* sobre los caminos de OpenStreetMap, con aviso de escaleras y opción «sin escaleras»); el PRD dice que el modo mapa «te ubica; no traza ruta». Lo dejé porque ya estaba hecho y funciona; la brújula, que es el producto, sigue sin mostrar ruta. Si el equipo prefiere el mapa sin ruta, basta quitar el dibujo de `path` en `dibujarMapa`.
- **El mapa puede girar con el rumbo** (botón ↻, apagado por defecto). El PRD decidió que no gira; por defecto se respeta (orientación del plano) y el giro es opcional. Una brújula con la N marca dónde queda el norte porque el plano no está orientado así.
- **El resplandor se mueve en 0,7 s** (posición) y 1,4 s (tamaño y color), no 1,4 s en todo: con la brújula del teléfono emitiendo decenas de lecturas por segundo, 1,4 s en la posición se sentía arrastrado.
- **Las fotos de la comunidad se guardan solo en el teléfono** (`localStorage`, JPEG de máximo 900 px). El PRD deja sin definir dónde se guardan y cómo se moderan; mientras tanto no hay publicación real. La pantalla lo avisa.
- **«Vas bien»** solo aparece si no te estás alejando (compara con lo más cerca que estuviste en los últimos 20 s), por la crítica de diseño que señala que el mensaje fijo refuerza rumbos equivocados.
- **Calibración del plano**: la app usa 0,4601 m/px y 155,3°; `data/georef.json` da 0,4666 m/px y 154,8°. Las dos coinciden a 1 a 6 m (máximo en los bordes del plano), así que no hay desfase relevante. Si se unifican, hay que cambiar también `tools/generar-grafo.py`.

## Supuestos en los contornos

- **Comedores** es la parte norte del bloque D (OpenStreetMap lo dibuja separado; el plano lo trae dentro del cuadro de D). Su contorno sale de OSM recortado al cuadro de D. Elegir «Edificio D» también se cumple al entrar a Comedores, porque está dentro de D.
- **Innovación Tecnológica** se asignó al edificio rotulado «Edificio Bari» en el plano (borde izquierdo): tiene la misma forma que el polígono de OSM y queda en el mismo lugar, pero es una inferencia, **por confirmar**.
- **Cafetería Vivendum** usa la «O» del plano (OSM la llama «Q»; ver `docs/pendientes-datos.md`).

## Contenido de ejemplo que hay que reemplazar

`ZONAS` y `SABIAS` en `tools/generar-datos.py` salen de las plantillas del diseño y **no están verificados**: el dato «Era el hall de montaje» (Edificio C) y el «Sabías que» del reloj del A y del C. Ver `docs/pendientes-datos.md`, sección 4.

## Lo que no está probado

La interfaz se probó ejecutando su código con un DOM simulado (flujo, estados, recorrido de ejemplo, mapa, tema claro y oscuro), no en un teléfono. Falta revisar en uno real: el aspecto de las pantallas, el desempeño de los gestos del mapa, la brújula con el teléfono en la mano y la cámara para tomar la foto.

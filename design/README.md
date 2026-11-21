# Diseño

Prototipo de interfaz de la brújula de campus, hecho en un lienzo de Claude Design.

- Lienzo: https://claude.ai/artifact/9QBL5netmQnFH2GxkA11tr (privado; se comparte desde su menú Share).
- `lienzo/`: copia de las pantallas (`*.dc.html`) y del índice del lienzo (`canvas.json`). Son la fuente del diseño, no una app: se renderizan solo dentro del lienzo, que aporta el runtime (`support.js`).
  - Fila principal: Permiso, Buscar, Main (brújula), Dato, Cerca, Llegada, Mapa y Demo (flujo animado de 30 s).
  - Fila de estados: Flecha, Detras, Aleja, Impreciso, SinGps, MapaClaro, BuscarVacio y LlegadaSinFoto.
  - `DatosMapa.dc.html` es el tablero de datos reales (mapa, destinos y puntos de interés).
- `plantillas/`: cinco plantillas (`Brujula`, `Buscar`, `Llegada`, `Permiso`, `Demo`). Las variantes del lienzo son la misma plantilla con otros valores por defecto, así que se edita la plantilla y se regenera:
  - `python3 design/scripts/generar.py design <canvas.json publicado>` reescribe `lienzo/` y conserva los tableros ajenos del `canvas.json` publicado.
  - `node design/scripts/probar.mjs design/lienzo` comprueba que cada tablero compila y que no le falta ningún valor.
- `assets/`: el mapa rasterizado en tema claro y oscuro (desde `data/mapa-casa-central.svg`, a 2×) y la foto del Edificio A (Alexxxos, CC BY-SA 3.0, Wikimedia Commons). En el lienzo se sirven como `/_blob/<id>`: mapa claro `f6dcd4fd…`, mapa oscuro `6895b4d9…`, foto `090edd59…`.
- Decisiones de interfaz (paleta, movimiento, tipografía, modos de señal, estados): `docs/PRD.md`.
- Crítica de diseño: `.impeccable/critique/`.

# PRD — Brújula de campus

Documento vivo. Se actualiza a medida que el equipo va especificando el producto.
Hackathon LYOSS USM 2026, desafío «Campus sin barreras». Última actualización: 21 de noviembre de 2026.

## 1. Problema

Orientarse en Casa Central (Valparaíso) es difícil para quien no conoce el campus: cerro, desniveles, edificios nombrados con letras y poca información para ubicarse. Las soluciones habituales (mapa con ruta giro a giro) llevan al destino, pero no ayudan a conocer el lugar.

## 2. Usuario

- Principal: mechones y estudiantes en general que no conocen bien el campus.
- Fuera del core (trabajo futuro): personas ciegas y personas en silla de ruedas.

## 3. Propuesta

Una aplicación tipo brújula: el usuario elige un destino y ve una señal que apunta hacia él, con la distancia. No se le muestra una ruta ni un mapa giro a giro; decide por dónde caminar y, en el trayecto, descubre el campus.

Filosofía: la barrera se reduce cuando la persona conoce su universidad. La app guía sin sustituir la exploración, y la comunidad ayuda al siguiente que llega.

## 4. Alcance del prototipo

| Función | Estado | Detalle |
|---|---|---|
| Brújula con distancia | Core | Resplandor direccional en el borde de la pantalla (no una flecha): el borde brilla del lado del destino. Lejos, estrecho y frío; cerca, ancho y cálido. La cifra en metros queda al centro. |
| Información para no perderse | Core | Pista textual por destino e indicador de si el usuario se acerca o se aleja. |
| Datos curiosos por zona | Core | Al pasar por ciertas coordenadas, una tarjeta compacta brota desde abajo sobre la misma pantalla de brújula, con transición suave; se toca para ampliar. |
| Señal alternativa: flecha | Core | Selector en la brújula para quien no entienda el resplandor: Luz, Flecha o Mapa. |
| Modo mapa | Core (segunda modalidad) | Versión más simple: el plano de Casa Central con otra piel visual, la posición del usuario y el destino. Te ubica; no traza ruta. |
| Fotos comunitarias | Core | Al llegar, el usuario puede dejar una foto del destino para quien venga después. |
| Modo simulado | Core (demo) | Recorrido simulado para presentar en sala sin depender del GPS. |
| QR como ancla de ubicación | Idea suelta | Por definir. |
| Accesibilidad (ciegos, silla de ruedas) | Trabajo futuro | — |
| Asignación de salas accesible | Trabajo futuro | Idea alternativa descartada para el prototipo. |

## 5. Flujo principal

1. Elegir destino (búsqueda o lista de edificios).
2. Seguir la brújula: señal, distancia, pista.
3. En el trayecto: tarjetas de datos curiosos al entrar en una zona.
4. Llegada: ver fotos de la comunidad y dejar la propia.

## 6. Decisiones técnicas

- Plataforma: web/PWA, se abre con un enlace desde cualquier teléfono.
- Campus: Casa Central. Plano de referencia en `docs/plano-casa-central.png`.
- Flujo de trabajo: explorar el diseño visual primero y luego implementar en código.
- Lienzo de diseño: https://claude.ai/artifact/9QBL5netmQnFH2GxkA11tr (privado hasta compartirlo).

### Decisiones de interfaz

- Señal: resplandor en el borde de la pantalla, estilo indicador direccional radial de videojuego. Un arco ancho representa con honestidad el error de la brújula (hasta unos 30°).
- Paleta «confort» (la sensación buscada: sé que voy a llegar). Tema claro y oscuro.
  - Oscuro: fondo `#15131F`, texto `#F5F1EA`, texto secundario `#B3ADBF`, superficies translúcidas `rgba(40,36,56,0.62)`.
  - Claro: fondo `#F6F1EA`, texto `#1D1A26`, texto secundario `#5E5869`, superficies translúcidas `rgba(255,255,255,0.68)`.
  - Resplandor lejos (calma): azul `#8FA6FF` y lila `#B79CFF`.
  - Resplandor cerca (calidez): naranja `#FF8A3D` y rosa `#FF5C7A`. El color se interpola según la cercanía.
  - Llegada y comunidad (vivo, saturado): coral `#FF5C39` y amarillo `#FFB800`. El mismo coral marca todo lo que viene de otros estudiantes (fotos, conteos, botón de aportar), de modo que llegar se lee como sumarse a la comunidad.
  - Decidido: paleta propia, sin colores institucionales de la USM. La sensación de comunidad la lleva solo el color, sin conteos ni indicadores de otros estudiantes.
- Movimiento: fluido y lento. Curva `cubic-bezier(0.22, 1, 0.36, 1)`, entre 900 y 1400 ms; el resplandor «respira» en ciclos de 5 a 7 s; las superficies son de vidrio esmerilado (desenfoque de fondo).
- Mensaje de confianza en la brújula: «Vas bien. Vas a llegar.»
- Tipografía: Chakra Petch (títulos y cifras) e Instrument Sans (texto).

### Ubicación y mapa

- La posición sale de la API de geolocalización del navegador, gratuita y sin clave; no hace falta una API de Google para eso.
- Modo mapa, decidido: mapa propio redibujado desde los contornos de OpenStreetMap (`data/mapa-casa-central.svg`), con la paleta de la app. No usa Leaflet ni teselas, así que funciona sin conexión a un servidor de mapas.
- El mapa usa las mismas coordenadas de píxel que el plano oficial (1311×1006). La conversión GPS → píxel es una transformación afín guardada en `data/georef.json`; plano y OpenStreetMap calzan con 1 a 2 m de error.
- El plano no tiene el norte arriba: «arriba» apunta al sur-sureste (rumbo ~155°) y la escala es 0,47 m por píxel. Las coordenadas de la rama `wip/brujula` quedan desplazadas 10 a 30 m respecto de esta referencia.

### Datos del campus (`data/`)

- `edificios.json`: 17 edificios con lat/lng, píxel, pista, foto y licencia. Destinos de la demo: C, A, F, M, P, Biblioteca (U), Comedores y Federación.
- `puntos-interes.json`: 31 puntos (accesos, comida, cajeros, deporte, salud, fotocopias, patios) y la lista de pendientes.
- `huellas-edificios.geojson`: contornos de los edificios, para calcular la llegada por cercanía al borde.
- Atribución obligatoria en la app: «© colaboradores de OpenStreetMap».

## 7. Restricciones conocidas

- En iPhone, la brújula del navegador exige un toque del usuario para dar permiso y requiere HTTPS.
- El GPS del teléfono ronda los 5 m a cielo abierto y empeora entre edificios; radio de llegada sugerido: unos 20 m.
- El navegador no detecta zonas en segundo plano: los datos curiosos solo aparecen con la página abierta.
- La señal directa puede apuntar a través de un edificio o un desnivel; por eso la pista textual es parte del core.

## 8. Pitch

- Abrir con comunidad (fotos) y descubrimiento (datos), contado a través de la flecha.
- Afirmación defendible: la gente acepta caminar más para conocer el entorno (ver `docs/fuentes.md`).
- No afirmar que sin ruta se aprende más: la evidencia no lo respalda.
- Diferenciación: la flecha sin mapa ya existe (Crowsflight, Actionbound, CSUMB GPS); lo propio es combinarla con fotos comunitarias del destino y datos por zona, en un campus concreto y sin instalar nada.

## 9. Supuestos y pendientes

- Datos del campus: las coordenadas salen de OpenStreetMap contrastado con el plano oficial; no se midieron en terreno y marcan el centro del edificio, no su puerta.
- Estimado o sin verificar: la ubicación de la Federación (el plano y OpenStreetMap no coinciden), las pistas (borradores redactados desde el plano) y el contenido de cada edificio (aportado por el equipo).
- Fotos con licencia libre solo para A, F y B (Wikimedia Commons; las de A y B con la letra inferida). C, M, P, Biblioteca, Comedores y Federación: pendientes de sacar en terreno.
- Sin ubicar (trabajo futuro): cajero BancoEstado, testamento de la entrada y memorial del reloj de sol. Los datos de Google Maps no se extrajeron: API de pago y términos que no permiten copiarlos en bloque.
- Datos curiosos por zona: sin recolectar.
- Sin definir: nombre del producto, moderación de fotos, dónde se guardan las fotos, stack concreto.
- Sin confirmar: entregables y ponderaciones de las bases oficiales, hora de entrega, tamaño del equipo.

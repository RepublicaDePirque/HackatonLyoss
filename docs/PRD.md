# PRD — Brújula de campus

Documento vivo. Se actualiza a medida que el equipo va especificando el producto.
Hackathon LYOSS USM 2026, desafío «Campus sin barreras». Última actualización: 21 de noviembre de 2026.

## 1. Problema

Orientarse en Casa Central (Valparaíso) es difícil para quien no conoce el campus: cerro, desniveles, edificios nombrados con letras y poca información para ubicarse. Las soluciones habituales (mapa con ruta giro a giro) llevan al destino, pero no ayudan a conocer el lugar.

## 2. Usuario

- Principal: mechones y estudiantes en general que no conocen bien el campus.
- Personas ciegas o con baja visión: modo voz (ver alcance).
- Personas con movilidad reducida (muletas, una lesión, cansancio): «Evitar escaleras» (ver alcance).
- Fuera de alcance: personas en silla de ruedas; el campus hoy no es recorrible en silla.

## 3. Propuesta

Una aplicación tipo brújula: el usuario elige un destino y ve una señal que apunta hacia él, con la distancia. La brújula no muestra una ruta ni indicaciones giro a giro; la persona decide por dónde caminar y, en el trayecto, descubre el campus. Quien prefiera ver el camino tiene el modo mapa, que sí lo dibuja.

Filosofía: la barrera se reduce cuando la persona conoce su universidad. La app guía sin sustituir la exploración, y la comunidad ayuda al siguiente que llega.

## 4. Alcance del prototipo

| Función | Estado | Detalle |
|---|---|---|
| Brújula con distancia | Core | Resplandor direccional en el borde de la pantalla (no una flecha): el borde brilla del lado del destino. Lejos, estrecho y frío; cerca, ancho y cálido. La cifra en metros queda al centro. |
| Información para no perderse | Core | Pista textual por destino, siempre visible, y un mensaje según el estado: vas bien, te estás alejando, está detrás de ti (con ícono de girar) o casi llegas. Con GPS impreciso la luz se ensancha y se avisa; sin ubicación se ofrece el mapa. |
| Datos curiosos por zona | Core | Al pasar por ciertas coordenadas, una tarjeta compacta brota desde abajo sobre la misma pantalla de brújula, con transición suave. «Leer más» la abre en una hoja; se puede cerrar. |
| Señal alternativa: flecha | Core | Selector fijo en la brújula, para quien no entienda el resplandor: Resplandor, Flecha o Mapa. Con la flecha, el resplandor baja a un tono tenue. |
| Modo mapa | Core (segunda modalidad) | Versión más simple: el plano de Casa Central con otra piel visual, la posición del usuario («Tú», con un cono hacia donde mira) y el destino. Siempre traza la ruta por los caminos del campus (A* sobre OpenStreetMap), con aviso de escaleras. La brújula sigue sin ruta. |
| Fotos comunitarias | Core | En los últimos 60 m aparece la tarjeta «Así se ve al llegar» con la foto del destino. Al llegar se ve la foto y el usuario puede dejar la suya, sin nombre, para quien venga después. Si el destino no tiene fotos, se invita a ser el primero. |
| Modo simulado | Core (demo) | Recorrido simulado para presentar en sala sin depender del GPS. |
| QR como ancla de ubicación | Idea suelta | No se define aún, por decisión del equipo (ver «Punto de entrada» en la sección 9). |
| Evitar escaleras (movilidad reducida) | Prototipo | Para quien puede caminar pero le cuestan las escaleras: muletas, una lesión, cansancio. En el modo mapa, el botón «Evitar escaleras» elige el camino sin escaleras y dice cuánto se alarga («Sin escaleras: 285 m, 125 m más. El camino corto tiene 1 escalera»). Si no existe, ofrece el que tiene menos y lo dice. |
| Silla de ruedas | Fuera de alcance | Casa Central está en un cerro y hoy no es recorrible en silla de ruedas; prometer una ruta sería falso. |
| Modo voz (personas ciegas) | Prototipo | La misma brújula dicha en palabras, con el modelo «faro + entorno» de Soundscape: dirección en horas del reloj y distancia («Edificio A, a las 2, 120 metros»), avisos cada 25 m, edificios que quedan al lado, datos curiosos, escaleras y llegada. Botón grande «¿Dónde está?». Lo lee el lector de pantalla del teléfono (VoiceOver o TalkBack); «Voz de la app» es opcional. En Android vibra cuando el teléfono apunta al destino. |
| Asignación de salas accesible | Trabajo futuro | Idea alternativa descartada para el prototipo. |

## 5. Flujo principal

0. Primera vez: una pantalla explica la señal y pide ubicación y brújula con un toque (requisito de iPhone). Quien no acepta puede ver solo el mapa. Decidido: el mapa se abre sin destino, con su posición y los edificios, y al tocar un edificio queda elegido. **Falta implementarlo**: hoy abre con el Edificio A como destino, sin que la persona lo elija.
1. Elegir destino: búsqueda (por nombre, lugar o letra; decidido que no lee códigos de sala como «C-210» ni incluye servicios, porque los mechones buscan por letra o nombre del edificio) y lista con «Cerca de ti» y «Todos los destinos», distancia en línea recta y marca «con fotos».
2. Seguir la brújula: señal, distancia, pista.
3. En el trayecto: tarjetas de datos curiosos al entrar en una zona.
4. Últimos 60 m: foto de cómo se ve el destino.
5. Llegada: el GPS la detecta (al estar adentro del cuadro del edificio, según su huella en `huellas-edificios.geojson`), y antes de pasar a la llegada la persona lo confirma con la foto del destino («¿Es este el lugar?»: «Sí, llegué» / «Aún no»), porque el GPS puede errar 5 a 15 m y los edificios están pegados. Un botón secundario «Ya llegué» queda por si el GPS falla. La pantalla de llegada muestra la foto, un dato y la invitación a dejar la propia; «Aún no llego» devuelve a la brújula.

Recorrido de la demo: de la Entrada Av. Los Placeres al Edificio A (205 m en línea recta), pasando junto al Edificio C (dato: era el hall de montaje). Se eligió el A porque tiene foto con licencia libre.

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
  - Resplandor según la distancia (decidido después del diseño, para que el color diga «frío o caliente» sin leer la cifra): azul `#5B8CFF` si está lejos, morado `#A66BFF` a mitad de camino y rojo `#FF3D4F` cuando está cerca (0 m = rojo, 220 m o más = azul). El color se interpola en espacio OKLCH para que el paso no se ensucie. Una franja fina en el borde marca el punto exacto, y un velo suave detrás de la cifra mantiene el contraste.
  - Llegada y comunidad (vivo, saturado): coral `#FF5C39` y amarillo `#FFB800`. La pantalla de llegada es un degradado coral → amarillo con texto oscuro. El mismo coral marca lo que viene de otros estudiantes (la marca «con fotos» y el botón de aportar), de modo que llegar se lee como sumarse a la comunidad.
  - Decidido: paleta propia, sin colores institucionales de la USM. La sensación de comunidad la lleva solo el color, sin conteos ni indicadores de otros estudiantes.
- Movimiento: fluido y lento. Curva `cubic-bezier(0.22, 1, 0.36, 1)`, entre 900 y 1400 ms; el resplandor «respira» en ciclos de 5 a 7 s; las superficies son de vidrio esmerilado (desenfoque de fondo). Con «reducir movimiento» activado se quitan las animaciones.
- Mensaje de confianza en la brújula: «Vas bien. Vas a llegar.» Cambia según el estado (ver alcance).
- Estructura fija de la brújula: arriba, el destino; al centro, la cifra y el mensaje; abajo, la pista, el selector de señal y «Ya llegué». Las tarjetas flotan sobre esa base, así que nada salta de lugar.
- Lienzo: la fila principal tiene 8 pantallas (permiso, destino, brújula, dato, casi llegas, llegada, mapa y demo animada de 30 s). La segunda fila tiene los estados: flecha, detrás, alejándose, GPS impreciso, sin ubicación, mapa claro, búsqueda vacía y llegada sin fotos.
- Tipografía: Chakra Petch (títulos y cifras) e Instrument Sans (texto).

### Ubicación y mapa

- La posición sale de la API de geolocalización del navegador, gratuita y sin clave; no hace falta una API de Google para eso.
- Modo mapa, decidido: mapa propio redibujado desde los contornos de OpenStreetMap (`data/mapa-casa-central.svg`), con la paleta de la app. No usa Leaflet ni teselas, así que funciona sin conexión a un servidor de mapas.
- El mapa usa las mismas coordenadas de píxel que el plano oficial (1311×1006). La conversión GPS → píxel es una transformación afín guardada en `data/georef.json`; plano y OpenStreetMap calzan con 1 a 2 m de error.
- El plano no tiene el norte arriba: «arriba» apunta al sur-sureste (rumbo ~155°) y la escala es 0,47 m por píxel. Las coordenadas de la rama `wip/brujula` quedan desplazadas 10 a 30 m respecto de esta referencia. La rama `map` asume norte arriba y 0,5 m por píxel: si se reutiliza su visor, hay que cambiarle la calibración por `georef.json`.
- Decidido: el modo mapa se muestra con la orientación del plano (Av. Los Placeres arriba, Av. España abajo), que es como lo conoce la comunidad, y no gira con el teléfono. El cono del usuario apunta a rumbo real − 155° en pantalla.

### Datos del campus (`data/`)

- `edificios.json`: 17 edificios con lat/lng, píxel, pista, foto y licencia. Destinos de la demo: C, A, F, M, P, Biblioteca (U), Comedores y Federación.
- `mapa-edificios-limpio.svg`: capa para el modo mapa, con fondo transparente: solo edificios, caminos del campus y las dos avenidas de referencia.
- `puntos-interes.json`: 32 puntos (accesos, comida, cajeros, deporte, salud, fotocopias, patios) y la lista de pendientes.
- `huellas-edificios.geojson`: contornos de los edificios, para calcular la llegada por cercanía al borde.
- Atribución obligatoria en la app: «© colaboradores de OpenStreetMap».

## 7. Restricciones conocidas

- En iPhone, la brújula del navegador exige un toque del usuario para dar permiso y requiere HTTPS.
- El GPS del teléfono ronda los 5 m a cielo abierto y empeora entre edificios; la llegada se da al estar adentro del cuadro del edificio, a una profundidad proporcional al tamaño de cada zona (60 % de lo más adentro que se puede estar, entre 1,5 y 4,5 m; `ADENTRO_*` en `index.html`); con el error del GPS, «Ya llegué» queda como respaldo.
- El navegador no detecta zonas en segundo plano: los datos curiosos solo aparecen con la página abierta.
- La señal directa puede apuntar a través de un edificio o un desnivel; por eso la pista textual es parte del core.

### Límites de «Evitar escaleras»

- Solo conoce las escaleras marcadas en OpenStreetMap. Si falta una en esos datos, la app la trata como camino plano.
- No considera pendientes, superficies, anchos ni cuál es la puerta de cada edificio. El aviso «No considera pendientes» va siempre en pantalla.
- Sin validar en terreno. En los datos actuales, 78 de 420 pares de destinos no tienen camino sin escaleras; entre ellos, todo lo que pasa por el Acceso Av. España.

### Límites del modo voz

- Orienta, no reemplaza al bastón ni al perro guía: no detecta obstáculos ni da una ruta paso a paso.
- Exige llevar el teléfono en la mano, plano y con la pantalla encendida: la brújula mide hacia dónde apunta el teléfono, y una web se suspende con la pantalla bloqueada.
- Las pistas actuales son visuales («el edificio de la torre»). Faltan pistas táctiles o sonoras por destino, redactadas en terreno.
- Probado con el recorrido simulado en un navegador de escritorio. Sin probar con VoiceOver ni TalkBack en un teléfono, ni con personas ciegas.

## 8. Pitch

- Abrir con comunidad (fotos) y descubrimiento (datos), contado a través de la flecha.
- Afirmación defendible: la gente acepta caminar más para conocer el entorno (ver `docs/fuentes.md`).
- No afirmar que sin ruta se aprende más: la evidencia no lo respalda.
- Diferenciación: la flecha sin mapa ya existe (Crowsflight, Actionbound, CSUMB GPS); lo propio es combinarla con fotos comunitarias del destino y datos por zona, en un campus concreto y sin instalar nada.

## 9. Supuestos y pendientes

- Datos del campus: las coordenadas salen de OpenStreetMap contrastado con el plano oficial; no se midieron en terreno y marcan el centro del edificio, no su puerta.
- Federación: en pasaje Valdés, frente a la portería del M (confirmado por el equipo).
- Estimado o sin verificar: las pistas (borradores redactados desde el plano) y el contenido de cada edificio (aportado por el equipo).
- Fotos con licencia libre solo para A, F y B (Wikimedia Commons; las de A y B con la letra inferida). C, M, P, Biblioteca, Comedores y Federación: pendientes de sacar en terreno.
- Sin ubicar (trabajo futuro): testamento de la entrada y memorial del reloj de sol; no figuran en OpenStreetMap. Cajero BancoEstado: hay un cajero sin banco indicado en Av. Los Placeres que podría serlo, por confirmar.
- La cafetería Vivendum es el Edificio Q, confirmado por el equipo y coincidente con OpenStreetMap; el plano oficial la rotula «O». El punto del edificio P es el centro de P y P2 juntos. Los datos de Google Maps no se extrajeron: API de pago y términos que no permiten copiarlos en bloque.
- Datos curiosos por zona: sin recolectar.
- Punto de entrada: sin definir por ahora, por decisión del equipo (QR en las entradas del campus o enlace previo). Hoy la app siempre parte en la bienvenida, aunque la persona ya haya pasado por ella.
- Sin definir: nombre del producto, moderación de fotos, dónde se guardan las fotos, stack concreto.
- Sin confirmar: entregables y ponderaciones de las bases oficiales, hora de entrega, tamaño del equipo.

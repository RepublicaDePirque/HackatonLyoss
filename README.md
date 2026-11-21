# Solem

<img src="assets/logo/logo.png" alt="Logo de Solem: un faro con un haz dorado" width="120">

Hackathon LYOSS USM 2026, desafío «Campus sin barreras».

## Propósito

Orientarse en Casa Central (USM, Valparaíso) es difícil para quien no conoce el campus: hay cerro, desniveles y edificios nombrados con letras. Las apps habituales llevan al destino con una ruta giro a giro, pero no ayudan a conocer el lugar.

Solem propone otra cosa: eliges un destino y el borde de la pantalla brilla hacia él, con la distancia. No te damos una ruta; tú decides por dónde caminar y, en el trayecto, descubres el campus. La idea de fondo es que la barrera se reduce cuando la persona conoce su universidad, y que la comunidad ayuda al siguiente que llega, por ejemplo con fotos de cómo se ve cada edificio.

Pensada primero para mechones y estudiantes que no conocen bien el campus. Es una web/PWA: se abre con un enlace, sin instalar nada.

Más detalle: [docs/PRD.md](docs/PRD.md) (producto y decisiones de diseño), [docs/implementacion.md](docs/implementacion.md) (cómo está construida) y [docs/pendientes-datos.md](docs/pendientes-datos.md) (datos que faltan).

## Funcionalidades

- **Portada con el logo.** Al abrir la app aparece el logo y «Toca para empezar»; al tocar se entra a la bienvenida.
- **Brújula con resplandor.** El borde de la pantalla brilla del lado del destino: frío y estrecho si está lejos, cálido y ancho si está cerca. La cifra en metros queda al centro. Se puede cambiar a una flecha o al mapa.
- **Ayuda para no perderse.** Una pista de texto por destino siempre visible y un mensaje según el estado: vas bien, te estás alejando, está detrás de ti o casi llegas. Si el GPS es impreciso, lo avisa.
- **37 destinos con buscador.** Lista «Cerca de ti» y «Todos los destinos», ordenados por distancia; busca por nombre, lugar o letra («C»). Marca los que tienen fotos.
- **Datos curiosos por zona.** Al pasar por ciertos lugares aparece una tarjeta con un dato del campus.
- **Llegada.** Automática al entrar al cuadro del edificio o patio (con un margen de 5 m por el error del GPS), con botón «Ya llegué» por si el GPS falla.
- **Fotos de cómo se ve el destino.** En los últimos 60 m aparece «Así se ve al llegar», y al llegar el usuario puede tomar y dejar su propia foto, que verán los demás estudiantes. Quien vea una foto inadecuada puede reportarla: con 3 reportes deja de mostrarse.
- **Mapa del campus.** Plano de Casa Central con tu posición, el destino y la ruta sobre los caminos de OpenStreetMap, con aviso de escaleras.
- **Puertas de los edificios.** La señal y la ruta apuntan a la **puerta** del edificio, no a su borde: hay 41 puertas marcadas en 20 edificios. Si un edificio tiene varias, la app elige la de menor costo desde donde estás. La pista dice «Entrada principal · con escalera» y el mapa dibuja las puertas (verde sin escaleras, rojo con escalera, gris sin confirmar).
- **Atajos por dentro de edificios.** Hay 11 pasos marcados que cruzan un edificio de puerta a puerta (un pasillo del A, por ejemplo). La ruta los usa cuando acortan el camino y avisa «Atajo por dentro (Edificio A) en ~20 m»; en el mapa van con puntos. Si el paso tiene escalera, «Evitar escaleras» lo esquiva.
- **Evitar escaleras (movilidad reducida).** En el modo mapa, el botón «Evitar escaleras» elige el camino sin escaleras y dice cuánto se alarga («Sin escaleras: 285 m, 125 m más»). Si no existe uno, ofrece el que tiene menos y lo avisa. Es para quien puede caminar pero le cuestan las escaleras (muletas, una lesión, cansancio); **no es una ruta para silla de ruedas**.
- **Modo voz (personas ciegas o con baja visión).** La misma brújula dicha en palabras, con el modelo «faro + entorno»: dirección en horas del reloj y distancia («Edificio A, a las 2, 120 metros»), avisos cada 25 m, edificios que quedan al lado, datos curiosos, escaleras y llegada. Habla con una voz propia de la app y también lo lee el lector de pantalla del teléfono (VoiceOver o TalkBack); quien ya lo usa puede apagar «Voz de la app» para no oír dos voces. No detecta obstáculos ni da una ruta paso a paso: eso lo resuelven el bastón o el perro guía.
- **Recorrido de ejemplo.** Un recorrido simulado de unos 35 s para mostrar la app sin depender del GPS.
- **Tema claro y oscuro** según el teléfono, y animaciones reducidas si el usuario lo pide.
- **Funciona sin conexión** e instalable en la pantalla de inicio.

### Estado actual

- Las fotos de la comunidad se publican en Firestore ([js/fotos.js](js/fotos.js) y [firebase/firestore.rules](firebase/firestore.rules)) y las ve cualquiera que elija ese destino. Si no hay conexión, la foto queda guardada solo en el teléfono (`localStorage`). Todavía no hay moderación activa más allá de los reportes: las fotos se borran a mano desde la consola de Firebase.
- Los datos curiosos y varias pistas son contenido de ejemplo sin verificar. Faltan fotos propias de varios edificios y validar las coordenadas en terreno. La lista completa está en [docs/pendientes-datos.md](docs/pendientes-datos.md).
- Las puertas y los pasos por dentro están marcados a mano sobre el plano, así que son **aproximados**: falta afinarlos en terreno. No se sabe si un pasillo está abierto a cierta hora; el aviso de cada paso es la única forma de advertirlo. Los edificios J, Federación, Comedores y Gimnasio 1 aún no tienen puerta propia y la señal apunta a su borde.
- La interfaz se probó con un DOM simulado, no en un teléfono real.
- «Evitar escaleras» solo conoce las escaleras marcadas en OpenStreetMap y no considera pendientes, superficies ni puertas. En los datos actuales, 78 de 420 pares de destinos no tienen camino sin escaleras.
- El modo voz se probó con el recorrido simulado en un navegador de escritorio, no con VoiceOver o TalkBack en un teléfono ni con personas ciegas.
- Fuera del alcance del prototipo: una ruta para silla de ruedas (Casa Central está en un cerro y prometerla sería falso) y la asignación de salas accesible. Los límites completos están en [docs/PRD.md](docs/PRD.md).

## Estructura del repositorio

Lo que necesita el navegador está en la raíz y en `js/` y `assets/`; el resto es material de apoyo. `index.html`, `sw.js` y `manifest.webmanifest` quedan en la raíz porque GitHub Pages sirve desde ahí y el service worker solo controla los archivos que están a su nivel o debajo.

```
.
├── index.html               La app: pantallas, brújula, mapa y lógica principal
├── sw.js                    Service worker: la app funciona sin conexión
├── manifest.webmanifest     Datos para instalarla en la pantalla de inicio
├── marcar-entradas.html     Herramienta temporal para marcar puertas y pasos por dentro (no es parte de la app)
├── js/
│   ├── escaleras.js         «Evitar escaleras»: compara caminos y cuenta escaleras
│   ├── voz.js               Modo voz para personas ciegas
│   ├── fotos.js             Fotos compartidas: comprimir, publicar, leer y reportar (Firestore)
│   └── generado/            Datos del campus, creados por los scripts de tools/ (no editar a mano)
│       ├── grafo.js         Caminos y destinos, desde OpenStreetMap
│       ├── contornos.js     Contornos de edificios y patios, calcados del plano
│       ├── entradas.js      Puertas de los edificios y pasos por dentro, desde data/entradas.json
│       └── datos.js         Nombre, pista y foto de cada destino
├── assets/
│   ├── img/                 Mapas claro y oscuro y fotos de fachada con licencia libre
│   ├── fonts/, fuentes.css  Tipografías (Chakra Petch e Instrument Sans)
│   ├── icons/               Íconos de la app (180, 192 y 512 px)
│   ├── logo/                Logo del proyecto y su versión liviana para la portada
│   └── plano.jpeg           Plano oficial de Casa Central
├── data/                    Datos fuente: edificios, puertas y pasos (entradas.json), puntos de interés, georreferencia y datos curiosos
├── tools/                   Scripts de Python que generan js/generado/
├── tests/                   Pruebas del modo voz, de «Evitar escaleras», de la señal de la brújula, de la portada y de las entradas
├── firebase/                Reglas de seguridad de Firestore
├── design/                  Prototipo de interfaz (lienzo, plantillas y scripts del diseño)
├── docs/                    PRD, implementación, fuentes, pendientes de datos y enunciado del hackatón
├── LICENSE
└── README.md
```

## Cómo ejecutarla

No tiene dependencias ni paso de compilación: es un sitio estático.

```bash
git clone https://github.com/RepublicaDePirque/HackatonLyoss.git
cd HackatonLyoss
python3 -m http.server 8000
```

Abre <http://localhost:8000>. El GPS y la brújula reales solo funcionan por HTTPS (o en `localhost`), por ejemplo publicando el repo en GitHub Pages (*Settings → Pages*). En iPhone la brújula además exige un toque del usuario para dar el permiso, por eso la app lo pide en la primera pantalla.

| Enlace | Para qué |
|---|---|
| `/` | Flujo real (pide GPS y brújula; necesita HTTPS) |
| `/?demo` | Arranca directo el recorrido de ejemplo |
| `/?voz` | Activa el modo voz con la voz de la app (se combina con `demo` o `debug`) |
| `/?debug` | Panel para mover la posición y el rumbo sin GPS |
| `/#mapa` | Abre directo en modo mapa |
| `/?tema=claro` o `/?tema=oscuro` | Fuerza el tema |

Se pueden combinar, por ejemplo `/?debug&tema=claro`. Si cambias archivos que usa el service worker, sube el número de `CACHE` en [sw.js](sw.js) para que los teléfonos descarguen la versión nueva.

### Pruebas

Necesitan solo Node.js, sin instalar nada:

```bash
node tests/probar-escaleras.js
node tests/probar-voz.js
node tests/probar-senal.js
node tests/probar-portada.js
node tests/probar-entradas.js
```

La primera revisa, sobre el grafo real y los 420 pares de destinos, que «Evitar escaleras» nunca deje sin ruta y use cero escaleras cuando se puede. La segunda revisa las frases del modo voz. La tercera revisa los colores de la señal (azul lejos, morado, rojo cerca) y que la flecha y la luz giren por el camino corto. La cuarta revisa que la portada esté bien cableada y que su logo sea liviano. La quinta revisa que las 41 puertas y los 11 pasos por dentro sean coherentes con los contornos, el plano y los destinos, y que `index.html` los use.

### Regenerar los datos del campus (opcional)

Solo hace falta si cambias el mapa o los destinos. Necesitas Python 3; `contornos.py` además necesita `numpy`, `scipy`, `pillow` y `matplotlib`.

| Script | Genera | Notas |
|---|---|---|
| `python3 tools/generar-grafo.py` | `js/generado/grafo.js` (caminos y destinos) | Necesita internet (Overpass API) |
| `python3 tools/contornos.py` | `js/generado/contornos.js` (contornos de edificios y patios) | Con `--preview` solo deja una imagen de revisión |
| `python3 tools/generar-datos.py` | `js/generado/datos.js` (nombre, pista y foto de cada destino) | Lee `data/edificios.json` |
| `python3 tools/generar-entradas.py` | `js/generado/entradas.js` (puertas y pasos por dentro) | Lee `data/entradas.json`, que se exporta desde `marcar-entradas.html`; avisa de puertas lejanas y pasos muy largos |

### Fotos compartidas con Firebase (opcional)

Sin esto la app funciona igual: las fotos se guardan solo en el teléfono. El `firebaseConfig` de [js/fotos.js](js/fotos.js) apunta al proyecto del equipo original. **Si haces un fork, crea el tuyo**, para no escribir en su base de datos:

1. En la [consola de Firebase](https://console.firebase.google.com/) crea un proyecto y registra una app web.
2. Activa *Authentication → Anonymous* y crea una base *Firestore*.
3. Pega el contenido de [firebase/firestore.rules](firebase/firestore.rules) en *Firestore → Reglas* y publícalo.
4. Reemplaza `FIREBASE_CONFIG` en [js/fotos.js](js/fotos.js) por el de tu proyecto. Ese objeto es público por diseño; la seguridad está en las reglas.
5. En Google Cloud (*APIs y servicios → Credenciales*) restringe la API key a tu dominio.

Las reglas limitan cada foto a ~300 KB en JPEG y solo dejan sumar reportes (no editar ni borrar). Las fotos con 3 o más reportes dejan de mostrarse; para eliminarlas hay que hacerlo desde la consola.

## Tecnologías, APIs y servicios

| Categoría | Qué se usa |
|---|---|
| Lenguajes | HTML, CSS y JavaScript; Python 3 para los scripts de datos; Node.js solo para las pruebas |
| Frameworks y librerías de la app | Ninguno: JavaScript puro, canvas 2D para la brújula y el mapa |
| Librerías de los scripts | NumPy, SciPy, Pillow y Matplotlib (`tools/contornos.py`) |
| APIs del navegador | Geolocalización, orientación del dispositivo (brújula), Service Worker, `localStorage`, cámara (`<input capture>`), síntesis de voz y vibración (modo voz) |
| Datos de mapas | OpenStreetMap vía Overpass API (caminos, contornos y puntos de interés), contrastado con el plano oficial |
| Rutas | Algoritmo A* propio sobre el grafo de caminos |
| Servicios externos | Firebase Authentication (anónima) y Firestore, con el SDK 10.12.2 desde el CDN de Google; GitHub Pages para publicar |
| Tipografías | Chakra Petch e Instrument Sans, alojadas en `assets/fonts/` |

## Herramientas de inteligencia artificial

Todo el equipo usó **Claude** (Anthropic) durante el desarrollo: **Claude Code** para escribir y revisar código y documentación, y **Claude Design** para el prototipo de interfaz (el lienzo está en [design/](design/)). El **logo** se creó con **GPT** (OpenAI). Las decisiones de producto, el diseño y la revisión del resultado son del equipo.

## Integrantes

| Integrante | Rol principal |
|---|---|
| Agustín Venegas Fellenberg | Mapa y rutas: plano calibrado, grafo de OpenStreetMap, A* y camino sin escaleras. Integró la interfaz, la llegada y la herramienta de entradas |
| Eduardo Ignacio Morales | Producto y accesibilidad: PRD, prototipo de interfaz, datos del campus, modo voz y evitar escaleras |
| Pía Correa Brenni | Base y comunidad: PWA con GPS y brújula, contornos de edificios, fotos comunitarias con Firebase, logo e identidad de Solem |

## Licencia

- **Código:** [MIT](LICENSE) © 2026 Equipo Solem.
- **Fotos subidas por usuarios:** quien publique una foto la entrega al dominio público bajo [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/deed.es). Las fotos compartidas viven en la base de datos del servicio, no en este repo.
- **Datos y material de terceros:** conservan su propia licencia (ver abajo); la MIT no los cubre.

## Atribuciones

- Datos de caminos y edificios: © colaboradores de [OpenStreetMap](https://www.openstreetmap.org/copyright), licencia [ODbL](https://opendatacommons.org/licenses/odbl/).
- Fotos de fachada de Wikimedia Commons (autor y licencia de cada una en `data/edificios.json`):
  - Edificio A: Alexxxos, CC BY-SA 3.0.
  - Edificio F: Falk2, CC BY-SA 4.0.
  - Edificio B: Carigval.97, CC BY 4.0.
- El plano del campus (`assets/plano.jpeg`) proviene de [infraestructura.usm.cl](https://infraestructura.usm.cl/informacion-general/) y no está cubierto por la licencia MIT; sus derechos pertenecen a la USM.
- Las fuentes citadas en el pitch están en [docs/fuentes.md](docs/fuentes.md).

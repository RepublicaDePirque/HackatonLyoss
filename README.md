# Brújula USM

<img src="logo.png" alt="Logo de Brújula USM: un faro con un haz dorado" width="120">

Hackathon LYOSS USM 2026, desafío «Campus sin barreras».

## Propósito

Orientarse en Casa Central (USM, Valparaíso) es difícil para quien no conoce el campus: hay cerro, desniveles y edificios nombrados con letras. Las apps habituales llevan al destino con una ruta giro a giro, pero no ayudan a conocer el lugar.

Brújula USM propone otra cosa: eliges un destino y el borde de la pantalla brilla hacia él, con la distancia. No te damos una ruta; tú decides por dónde caminar y, en el trayecto, descubres el campus. La idea de fondo es que la barrera se reduce cuando la persona conoce su universidad, y que la comunidad ayuda al siguiente que llega, por ejemplo con fotos de cómo se ve cada edificio.

Pensada primero para mechones y estudiantes que no conocen bien el campus. Es una web/PWA: se abre con un enlace, sin instalar nada.

Más detalle: [docs/PRD.md](docs/PRD.md) (producto y decisiones de diseño), [docs/implementacion.md](docs/implementacion.md) (cómo está construida) y [docs/pendientes-datos.md](docs/pendientes-datos.md) (datos que faltan).

## Funcionalidades

- **Brújula con resplandor.** El borde de la pantalla brilla del lado del destino: frío y estrecho si está lejos, cálido y ancho si está cerca. La cifra en metros queda al centro. Se puede cambiar a una flecha o al mapa.
- **Ayuda para no perderse.** Una pista de texto por destino siempre visible y un mensaje según el estado: vas bien, te estás alejando, está detrás de ti o casi llegas. Si el GPS es impreciso, lo avisa.
- **37 destinos con buscador.** Lista «Cerca de ti» y «Todos los destinos», ordenados por distancia; busca por nombre, lugar o letra («C»). Marca los que tienen fotos.
- **Datos curiosos por zona.** Al pasar por ciertos lugares aparece una tarjeta con un dato del campus.
- **Llegada.** Automática al entrar al cuadro del edificio o patio (con un margen de 5 m por el error del GPS), con botón «Ya llegué» por si el GPS falla.
- **Fotos de cómo se ve el destino.** En los últimos 60 m aparece «Así se ve al llegar», y al llegar el usuario puede tomar y dejar su propia foto.
- **Mapa del campus.** Plano de Casa Central con tu posición, el destino y la ruta sobre los caminos de OpenStreetMap, con aviso de escaleras y la opción «sin escaleras».
- **Recorrido de ejemplo.** Un recorrido simulado de unos 35 s para mostrar la app sin depender del GPS.
- **Tema claro y oscuro** según el teléfono, y animaciones reducidas si el usuario lo pide.
- **Funciona sin conexión** e instalable en la pantalla de inicio.

### Estado actual

- Las fotos de la comunidad hoy **se guardan solo en el teléfono** (`localStorage`); todavía no se comparten entre personas. El código para subirlas a Firestore existe ([fotos.js](fotos.js) y [firebase/firestore.rules](firebase/firestore.rules)), pero **aún no está conectado** a la interfaz.
- Los datos curiosos y varias pistas son contenido de ejemplo sin verificar. Faltan fotos propias de varios edificios y validar las coordenadas en terreno. La lista completa está en [docs/pendientes-datos.md](docs/pendientes-datos.md).
- La interfaz se probó con un DOM simulado, no en un teléfono real.
- Fuera del alcance del prototipo: accesibilidad para personas ciegas y en silla de ruedas (hay trabajo previo en la rama `accesibilidad/modo-voz`) y asignación de salas.

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
| `/?debug` | Panel para mover la posición y el rumbo sin GPS |
| `/#mapa` | Abre directo en modo mapa |
| `/?tema=claro` o `/?tema=oscuro` | Fuerza el tema |

Se pueden combinar, por ejemplo `/?debug&tema=claro`. Si cambias archivos que usa el service worker, sube el número de `CACHE` en [sw.js](sw.js) para que los teléfonos descarguen la versión nueva.

### Regenerar los datos del campus (opcional)

Solo hace falta si cambias el mapa o los destinos. Necesitas Python 3; `contornos.py` además necesita `numpy`, `scipy`, `pillow` y `matplotlib`.

| Script | Genera | Notas |
|---|---|---|
| `python3 tools/generar-grafo.py` | `grafo.js` (caminos y destinos) | Necesita internet (Overpass API) |
| `python3 tools/contornos.py` | `contornos.js` (contornos de edificios y patios) | Con `--preview` solo deja una imagen de revisión |
| `python3 tools/generar-datos.py` | `datos.js` (nombre, pista y foto de cada destino) | Lee `data/edificios.json` |

### Fotos compartidas con Firebase (opcional, aún no conectado a la interfaz)

El `firebaseConfig` de [fotos.js](fotos.js) apunta al proyecto del equipo original. **Si haces un fork, crea el tuyo**, para no escribir en su base de datos:

1. En la [consola de Firebase](https://console.firebase.google.com/) crea un proyecto y registra una app web.
2. Activa *Authentication → Anonymous* y crea una base *Firestore*.
3. Pega el contenido de [firebase/firestore.rules](firebase/firestore.rules) en *Firestore → Reglas* y publícalo.
4. Reemplaza `FIREBASE_CONFIG` en [fotos.js](fotos.js) por el de tu proyecto. Ese objeto es público por diseño; la seguridad está en las reglas.
5. En Google Cloud (*APIs y servicios → Credenciales*) restringe la API key a tu dominio.

Las reglas limitan cada foto a ~300 KB en JPEG y solo dejan sumar reportes (no editar ni borrar). Las fotos con 3 o más reportes dejan de mostrarse; para eliminarlas hay que hacerlo desde la consola.

## Tecnologías, APIs y servicios

| Categoría | Qué se usa |
|---|---|
| Lenguajes | HTML, CSS y JavaScript (módulos ES); Python 3 para los scripts de datos |
| Frameworks y librerías de la app | Ninguno: JavaScript puro, canvas 2D para la brújula y el mapa |
| Librerías de los scripts | NumPy, SciPy, Pillow y Matplotlib (`tools/contornos.py`) |
| APIs del navegador | Geolocalización, orientación del dispositivo (brújula), Service Worker, `localStorage`, cámara (`<input capture>`) |
| Datos de mapas | OpenStreetMap vía Overpass API (caminos, contornos y puntos de interés), contrastado con el plano oficial |
| Rutas | Algoritmo A* propio sobre el grafo de caminos |
| Servicios externos | Firebase Authentication (anónima) y Firestore, con el SDK 10.12.2 desde el CDN de Google; GitHub Pages para publicar |
| Tipografías | Chakra Petch e Instrument Sans, alojadas en `fonts/` |

## Herramientas de inteligencia artificial

Todo el equipo usó **Claude** (Anthropic) durante el desarrollo: **Claude Code** para escribir y revisar código y documentación, y **Claude Design** para el prototipo de interfaz (el lienzo está en [design/](design/)). El **logo** se creó con **GPT** (OpenAI). Las decisiones de producto, el diseño y la revisión del resultado son del equipo.

## Integrantes

| Integrante | Rol principal |
|---|---|
| Agustín Venegas Fellenberg | Visor de mapa e integración de toda la aplicación |
| Eduardo Ignacio Morales | Producto (PRD), prototipo de interfaz, datos del campus y accesibilidad |
| Pía Correa Brenni | Base de la app (PWA, GPS y brújula), grafo de caminos, contornos de edificios, llegada por cercanía al borde y fotos comunitarias con Firebase |

## Licencia

- **Código:** [MIT](LICENSE) © 2026 Equipo Brújula USM.
- **Fotos subidas por usuarios:** quien publique una foto la entrega al dominio público bajo [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/deed.es). Las fotos compartidas viven en la base de datos del servicio, no en este repo.
- **Datos y material de terceros:** conservan su propia licencia (ver abajo); la MIT no los cubre.

## Atribuciones

- Datos de caminos y edificios: © colaboradores de [OpenStreetMap](https://www.openstreetmap.org/copyright), licencia [ODbL](https://opendatacommons.org/licenses/odbl/).
- Fotos de fachada de Wikimedia Commons (autor y licencia de cada una en `data/edificios.json`):
  - Edificio A: Alexxxos, CC BY-SA 3.0.
  - Edificio F: Falk2, CC BY-SA 4.0.
  - Edificio B: Carigval.97, CC BY 4.0.
- El plano del campus (`plano.jpeg`) proviene de [infraestructura.usm.cl](https://infraestructura.usm.cl/informacion-general/) y no está cubierto por la licencia MIT; sus derechos pertenecen a la USM.
- Las fuentes citadas en el pitch están en [docs/fuentes.md](docs/fuentes.md).

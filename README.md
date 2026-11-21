# Brújula USM

<img src="logo.png" alt="Logo de Brújula USM: un faro con un haz dorado" width="120">

Una brújula para orientarse en Casa Central (USM, Valparaíso). Eliges un destino y ves hacia dónde queda y a qué distancia. No te lleva de la mano con giros: tú decides por dónde caminar y, en el camino, conoces el campus. Al llegar ves cómo se ve el edificio y puedes dejar tu propia foto para quien venga después.

Hackathon LYOSS USM 2026, desafío «Campus sin barreras». Es una web/PWA: se abre con un enlace, sin instalar nada, y se publica con GitHub Pages.

## Qué hace hoy

- **Brújula con distancia.** Apunta hacia el borde más cercano del edificio o patio de destino (no hacia un punto en el centro) y muestra la dirección cardinal y los metros en línea recta.
- **Aviso de llegada.** Cuando estás a 15 m del borde del edificio, la brújula muestra «Estás llegando».
- **Tiempo y ruta a pie estimados.** Calcula un camino sobre los senderos del campus (algoritmo A*) y muestra distancia y minutos aproximados.
- **Mapa del campus.** Pestaña con el plano de Casa Central, tu posición, el destino y la ruta que falta. Se puede arrastrar, hacer zoom y tocar un edificio para elegirlo como destino.
- **Ruta sin escaleras.** Un botón activa el modo accesible, que evita los tramos con escaleras.
- **21 destinos.** Edificios A, B, C, D, E, F, K, L, M, M2, P, Q (Cafetería Vivendum), R, T, U (Biblioteca), Comedores, Innovación Tecnológica, Gimnasio 1, Museo Institucional, Patio Central y el acceso por Av. España.
- **Posición ajustada al camino.** Si estás a menos de 40 m de un sendero, la posición se «pega» a él para que la ruta no salte; si estás más lejos, avisa «lejos del camino».
- **Funciona sin conexión.** El service worker guarda la app y el plano, así que sigue andando sin internet (siempre intenta primero la versión nueva).
- **Instalable.** Tiene manifest e íconos, así que se puede agregar a la pantalla de inicio.
- **Fotos comunitarias (en construcción).** La captura, compresión y subida de fotos ya funcionan, con el lado del edificio (N/S/E/O) desde el que se tomaron. Solo se usan hoy en un panel de prueba (ver más abajo); falta la pantalla final del diseño.
- **Modo de prueba.** Con `?debug` en la URL se puede simular la posición y el rumbo sin salir de casa.

### Lo que falta

- La interfaz final del diseño (resplandor direccional, pantalla de llegada con foto, datos curiosos por zona). La interfaz actual es funcional, no la definitiva.
- Conectar las fotos comunitarias a esa interfaz. Hoy solo existe el panel de prueba.
- Medir la precisión real del GPS en el campus y validar en terreno las coordenadas.

## Tecnologías

- **Web/PWA sin compilación:** HTML, CSS y JavaScript (módulos ES). No hay framework ni paso de build.
- **Canvas 2D** para dibujar la brújula y el mapa.
- **APIs del navegador:** Geolocalización (`watchPosition`), orientación del dispositivo (`DeviceOrientationEvent`) y Service Worker.
- **Grafo de caminos de OpenStreetMap**, consultado con la Overpass API, y búsqueda de rutas con A*.
- **Contornos de edificios** calcados del plano oficial con Python (NumPy, SciPy, Pillow y Matplotlib).
- **Firebase** para las fotos: Authentication anónima y Firestore, sin Cloud Storage. Las fotos se comprimen a JPEG (máximo ~250 KB y 1024 px) y se guardan en base64.
- **GitHub Pages** para el despliegue.

## Estructura del repo

| Archivo | Qué es |
|---|---|
| [index.html](index.html) | La app: interfaz, brújula, mapa, cálculo de rutas y panel de prueba de fotos |
| [grafo.js](grafo.js) | Caminos y destinos del campus (generado con `tools/generar-grafo.py`) |
| [contornos.js](contornos.js) | Contornos de edificios y patios (generado con `tools/contornos.py`) |
| [fotos.js](fotos.js) | Captura, compresión, subida y lectura de fotos con Firestore |
| [sw.js](sw.js) | Service worker para uso sin conexión |
| [manifest.webmanifest](manifest.webmanifest) | Datos para instalar la app |
| [plano.jpeg](plano.jpeg) | Plano del campus, base del mapa |
| [firebase/firestore.rules](firebase/firestore.rules) | Reglas de seguridad de la base de datos |
| [tools/](tools) | Scripts que regeneran `grafo.js` y `contornos.js` |

## Cómo levantarlo

No necesita instalar nada. Clona el repo y sírvelo como sitio estático:

```bash
git clone https://github.com/RepublicaDePirque/HackatonLyoss.git
cd HackatonLyoss
python3 -m http.server 8000
```

Abre <http://localhost:8000>. La geolocalización solo funciona en `localhost` o con HTTPS.

- **Sin salir de casa:** abre <http://localhost:8000/?debug>. Aparece un simulador para mover tu posición (tocando el mapa) y girar el celular, más el panel de prueba de fotos.
- **En un teléfono real:** publícalo en GitHub Pages (*Settings → Pages*), que da HTTPS. En iPhone la brújula pide HTTPS y un toque del usuario para dar permiso; por eso la app tiene el botón «Activar ubicación y brújula».
- **Si cambias archivos que usa el service worker:** súbele el número a `CACHE` en [sw.js](sw.js) para que los teléfonos descarguen la versión nueva.

### Regenerar los datos del campus

Estos pasos solo hacen falta si cambias el mapa o los destinos.

- **Caminos y destinos** (`grafo.js`): necesita internet y solo la biblioteca estándar de Python. Si algo falta en el mapa, se corrige en openstreetmap.org y se vuelve a correr.

  ```bash
  python3 tools/generar-grafo.py
  ```

- **Contornos de edificios** (`contornos.js`): necesita `numpy`, `scipy`, `pillow` y `matplotlib`.

  ```bash
  pip install numpy scipy pillow matplotlib
  python3 tools/contornos.py
  ```

  Para revisar el resultado sin escribir nada: `python3 tools/contornos.py --preview`, que deja una imagen en `tools/preview.png`.

### Fotos comunitarias: usa tu propio proyecto Firebase

Las fotos se guardan en Firestore. El `firebaseConfig` de [fotos.js](fotos.js) apunta al proyecto del equipo original; **si haces un fork, no lo uses**, porque tus pruebas escribirían en su base de datos. Crea el tuyo:

1. En la [consola de Firebase](https://console.firebase.google.com/) crea un proyecto y registra una app web.
2. Activa *Authentication → Anonymous* y crea una base *Firestore*.
3. Pega el contenido de [firebase/firestore.rules](firebase/firestore.rules) en *Firestore → Reglas* y publícalo.
4. Reemplaza `FIREBASE_CONFIG` en [fotos.js](fotos.js) por el de tu proyecto. Ese objeto es público por diseño; la seguridad está en las reglas.
5. En Google Cloud (*APIs y servicios → Credenciales*) restringe la API key a tu dominio de Pages.

Las reglas limitan cada foto a ~300 KB en JPEG y solo dejan sumar reportes (no editar ni borrar). Las fotos con 3 o más reportes dejan de mostrarse; para eliminarlas hay que hacerlo desde la consola de Firebase. Al comprimir se vuelve a dibujar la imagen, lo que elimina sus metadatos (EXIF y GPS).

## Licencia

- **Código:** [MIT](LICENSE) © 2026 Equipo Brújula USM.
- **Fotos subidas por usuarios:** quien publica una foto la entrega al dominio público bajo [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/deed.es). La app lo avisa antes de publicar. Las fotos viven en la base de datos del servicio, no en este repo.
- **Datos y material de terceros:** conservan su propia licencia (ver abajo); la MIT no los cubre.

## Atribuciones

- Datos de caminos y edificios: © colaboradores de [OpenStreetMap](https://www.openstreetmap.org/copyright), licencia [ODbL](https://opendatacommons.org/licenses/odbl/). La app lo indica en la pestaña Mapa.
- Fotos de fachada de Wikimedia Commons (el autor y la licencia de cada una están en `data/edificios.json`, que viene en la rama de diseño):
  - Edificio A: Alexxxos, CC BY-SA 3.0.
  - Edificio F: Falk2, CC BY-SA 4.0.
  - Edificio B: Carigval.97, CC BY 4.0.
- El plano del campus (`plano.jpeg`) proviene de [infraestructura.usm.cl](https://infraestructura.usm.cl/informacion-general/) y no está cubierto por la licencia MIT; sus derechos pertenecen a la USM.

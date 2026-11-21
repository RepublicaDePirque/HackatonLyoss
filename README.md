# Brújula USM

Una brújula para orientarse en Casa Central (USM, Valparaíso). Eliges un destino y ves hacia dónde queda y a qué distancia, sin ruta giro a giro: tú decides por dónde caminar y, en el camino, conoces el campus. Al llegar ves cómo se ve el edificio y puedes dejar tu propia foto para quien venga después.

Hackathon LYOSS USM 2026, desafío «Campus sin barreras». Es una web/PWA: se abre con un enlace, sin instalar nada. Se publica con GitHub Pages.

## Correr tu propia copia

La app es estática (HTML y JavaScript, sin paso de compilación).

1. Clona el repo y sírvelo en local (la geolocalización funciona en `localhost` y en HTTPS):

   ```bash
   python3 -m http.server 8000
   ```

2. Para publicarla, activa GitHub Pages en tu fork (*Settings → Pages*).

### Fotos comunitarias: usa tu propio proyecto Firebase

Las fotos se guardan en Firestore. El `firebaseConfig` de [fotos.js](fotos.js) apunta al proyecto del equipo original; **si haces un fork, no lo uses**, porque tus pruebas escribirían en su base de datos. Crea el tuyo:

1. En la [consola de Firebase](https://console.firebase.google.com/) crea un proyecto y registra una app web.
2. Activa *Authentication → Anonymous* y crea una base *Firestore*.
3. Pega el contenido de [firebase/firestore.rules](firebase/firestore.rules) en *Firestore → Reglas* y publícalo.
4. Reemplaza `FIREBASE_CONFIG` en [fotos.js](fotos.js) por el de tu proyecto. Ese objeto es público por diseño; la seguridad está en las reglas.
5. En Google Cloud (*APIs y servicios → Credenciales*) restringe la API key a tu dominio de Pages.

Las fotos con 3 o más reportes dejan de mostrarse. Para borrarlas hay que hacerlo desde la consola de Firebase.

## Licencia

- **Código:** [MIT](LICENSE) © 2026 Equipo Brújula USM.
- **Fotos subidas por usuarios:** quien publica una foto la entrega al dominio público bajo [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/deed.es). La app lo avisa antes de publicar. Las fotos viven en la base de datos del servicio, no en este repo.
- **Datos y material de terceros:** conservan su propia licencia (ver abajo); la MIT no los cubre.

## Atribuciones

- Datos de caminos y edificios: © colaboradores de [OpenStreetMap](https://www.openstreetmap.org/copyright), licencia [ODbL](https://opendatacommons.org/licenses/odbl/). Esta atribución también debe mostrarse dentro de la app.
- Fotos de fachada de Wikimedia Commons (el autor y la licencia de cada una están en `data/edificios.json`, que viene en la rama de diseño):
  - Edificio A: Alexxxos, CC BY-SA 3.0.
  - Edificio F: Falk2, CC BY-SA 4.0.
  - Edificio B: Carigval.97, CC BY 4.0.
- El plano del campus (`plano.jpeg`) proviene de [infraestructura.usm.cl](https://infraestructura.usm.cl/informacion-general/) y no está cubierto por la licencia MIT; sus derechos pertenecen a la USM.

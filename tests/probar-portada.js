// Pruebas de la portada (logo primero; al tocar se entra a la app): node tests/probar-portada.js
// Revisa el cableado en index.html, que el logo exista y sea liviano (la app se guarda para usarla sin conexión)
// y que el service worker lo incluya.
const assert = require("assert"), fs = require("fs"), path = require("path");
const raiz = path.join(__dirname, "..");
const html = fs.readFileSync(path.join(raiz, "index.html"), "utf8");
const sw = fs.readFileSync(path.join(raiz, "sw.js"), "utf8");

const logo = html.match(/<img src="(assets\/logo\/[^"]+)"[^>]*>/);
assert(logo, "la portada debe mostrar el logo");
const archivo = path.join(raiz, logo[1]);
assert(fs.existsSync(archivo), `no existe ${logo[1]}`);
const kb = fs.statSync(archivo).size / 1024;
assert(kb < 100, `el logo de la portada pesa ${kb.toFixed(0)} KB: debe ser liviano (usa una versión reducida, no el original)`);
assert(sw.includes(`"${logo[1]}"`), "sw.js debe guardar el logo de la portada para usarlo sin conexión");
console.log(`ok: el logo de la portada existe (${kb.toFixed(0)} KB) y está en la caché del service worker`);

assert(/<main id="vPortada" class="vista"/.test(html), "falta la pantalla vPortada");
assert(/<button id="btnPortada"[^>]*aria-label=/.test(html), "el botón de la portada debe tener nombre accesible");
assert(/const VISTAS = \["portada",/.test(html), "VISTAS debe incluir «portada»");
assert(html.includes('history.replaceState({ v: "portada" }'), "el historial debe partir en la portada");
assert(html.includes('$("btnPortada").onclick = () => ir("permiso")'), "tocar la portada debe llevar a la bienvenida");
// el arranque normal muestra la portada; ?debug, ?demo y #mapa entran directo
assert(/else ir\("portada", false\);\s*<\/script>/.test(html), "sin parámetros la app debe partir en la portada");
assert(/else if \(DEBUG \|\| location\.hash === "#mapa"\)/.test(html), "?debug y #mapa deben entrar sin pasar por la portada");
console.log("ok: la portada está cableada: se muestra al abrir, tocar lleva a la bienvenida, ?debug/?demo/#mapa la saltan");

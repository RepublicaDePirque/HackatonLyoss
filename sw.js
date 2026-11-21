// Network-first: siempre intenta la versión nueva (revalidando, sin usar el caché HTTP de 10 min de GitHub Pages);
// sin internet usa la copia guardada.
const CACHE = "brujula-v11";
const FILES = ["./", "index.html", "js/generado/grafo.js", "js/generado/contornos.js", "js/generado/datos.js", "js/fotos.js", "js/escaleras.js", "js/voz.js", "assets/fuentes.css", "manifest.webmanifest", "assets/icons/icon-180.png", "assets/icons/icon-192.png", "assets/icons/icon-512.png", "assets/img/mapa-claro.png", "assets/img/mapa-oscuro.png", "assets/img/edificio-a.jpg", "assets/img/edificio-b.jpg", "assets/img/edificio-f.jpg", "assets/fonts/ChakraPetch-500.woff2", "assets/fonts/ChakraPetch-600.woff2", "assets/fonts/ChakraPetch-700.woff2", "assets/fonts/InstrumentSans-400.woff2", "assets/fonts/InstrumentSans-500.woff2", "assets/fonts/InstrumentSans-600.woff2"];
self.addEventListener("install", e => { e.waitUntil(caches.open(CACHE).then(c => c.addAll(FILES))); self.skipWaiting(); });
self.addEventListener("activate", e => {
  e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== CACHE).map(k => caches.delete(k)))).then(() => self.clients.claim()));
});
self.addEventListener("fetch", e => {
  if (e.request.method !== "GET" || new URL(e.request.url).origin !== location.origin) return;
  e.respondWith(
    fetch(e.request, { cache: "no-cache" }).then(r => { const copy = r.clone(); caches.open(CACHE).then(c => c.put(e.request, copy)); return r; })
      .catch(() => caches.match(e.request).then(r => r || caches.match("index.html")))
  );
});

// Network-first: siempre intenta la versión nueva (revalidando, sin usar el caché HTTP de 10 min de GitHub Pages);
// sin internet usa la copia guardada.
const CACHE = "brujula-v8";
const FILES = ["./", "index.html", "grafo.js", "contornos.js", "datos.js", "fotos.js", "escaleras.js", "voz.js", "fuentes.css", "manifest.webmanifest", "icon-180.png", "icon-192.png", "icon-512.png", "img/mapa-claro.png", "img/mapa-oscuro.png", "img/edificio-a.jpg", "img/edificio-b.jpg", "img/edificio-f.jpg", "fonts/ChakraPetch-500.woff2", "fonts/ChakraPetch-600.woff2", "fonts/ChakraPetch-700.woff2", "fonts/InstrumentSans-400.woff2", "fonts/InstrumentSans-500.woff2", "fonts/InstrumentSans-600.woff2"];
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

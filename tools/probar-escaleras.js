// Pruebas de «Evitar escaleras»: node tools/probar-escaleras.js
// 1) frases y conteo; 2) sobre el grafo real, que evitar escaleras nunca deje sin ruta y que use cero si se puede.
const assert = require("assert"), fs = require("fs"), path = require("path");
const { contarEscaleras, fraseEscaleras } = require("../escaleras.js");
const esc = new Set(["b|c", "c|d", "e|f"]), es = (a, b) => esc.has(a + "|" + b);
assert.strictEqual(contarEscaleras(["a", "b", "c", "d", "e", "f"], es), 2);   // b-c-d es una sola escalera
assert.strictEqual(contarEscaleras(["a", "b"], es), 0);
const fin = " No considera pendientes.";
assert.strictEqual(fraseEscaleras({ corto: { m: 180, esc: 0 }, evita: { m: 180, esc: 0 } }), "Este camino no tiene escaleras." + fin);
assert.strictEqual(fraseEscaleras({ corto: { m: 181, esc: 2 }, evita: { m: 242, esc: 0 } }), "Sin escaleras: 240 m, 60 m más. El camino corto tiene 2 escaleras." + fin);
assert.strictEqual(fraseEscaleras({ corto: { m: 100, esc: 3 }, evita: { m: 150, esc: 1 } }), "No hay camino sin escaleras. Este tiene 1 escalera; el corto tiene 3." + fin);
assert.strictEqual(fraseEscaleras({ corto: { m: 100, esc: 1 }, evita: { m: 100, esc: 1 } }), "No hay camino sin escaleras: este tiene 1 escalera." + fin);

// Grafo real: mismo costo que astar() de index.html (15 m por tramo de escalera, 400 m al evitarlas).
const G = new Function(fs.readFileSync(path.join(__dirname, "../grafo.js"), "utf8") + "; return GRAFO;")();
const R = 6371000, rad = d => d * Math.PI / 180;
const dist = (a, b) => { const dLat = rad(b[0] - a[0]), dLon = rad(b[1] - a[1]), h = Math.sin(dLat / 2) ** 2 + Math.cos(rad(a[0])) * Math.cos(rad(b[0])) * Math.sin(dLon / 2) ** 2; return 2 * R * Math.asin(Math.sqrt(h)); };
const adj = G.nodos.map(() => []);
for (const [a, b, t] of G.aristas) { adj[a].push([b, t === 1]); adj[b].push([a, t === 1]); }
function ruta(ini, fin, penal, sinEsc) {            // Dijkstra simple; devuelve { m, tramosEsc } o null
  const costo = new Map([[ini, 0]]), previo = new Map(), hecho = new Set();
  for (;;) {
    let u = -1, mejor = Infinity;
    for (const [k, c] of costo) if (!hecho.has(k) && c < mejor) { mejor = c; u = k; }
    if (u < 0) return null;
    if (u === fin) break;
    hecho.add(u);
    for (const [v, e] of adj[u]) {
      if (e && sinEsc) continue;
      const c = mejor + dist(G.nodos[u], G.nodos[v]) + (e ? penal : 0);
      if (c < (costo.get(v) ?? Infinity)) { costo.set(v, c); previo.set(v, [u, e]); }
    }
  }
  let m = 0, tramosEsc = 0;
  for (let v = fin; previo.has(v);) { const [u, e] = previo.get(v); m += dist(G.nodos[u], G.nodos[v]); if (e) tramosEsc++; v = u; }
  return { m, tramosEsc };
}
let pares = 0, conAhorro = 0, sinOpcion = 0;
const D = G.destinos;
for (let i = 0; i < D.length; i++) for (let j = 0; j < D.length; j++) {
  if (i === j || D[i].nodo === D[j].nodo) continue;
  const corto = ruta(D[i].nodo, D[j].nodo, 15, false); if (!corto) continue;
  const evita = ruta(D[i].nodo, D[j].nodo, 400, false), estricto = ruta(D[i].nodo, D[j].nodo, 0, true);
  pares++;
  assert(evita, `sin ruta al evitar: ${D[i].nombre} -> ${D[j].nombre}`);
  if (estricto) assert.strictEqual(evita.tramosEsc, 0, `había camino sin escaleras: ${D[i].nombre} -> ${D[j].nombre}`);
  else { sinOpcion++; assert(evita.tramosEsc <= corto.tramosEsc); }
  if (evita.tramosEsc < corto.tramosEsc) conAhorro++;
}
console.log(`ok: ${pares} pares de destinos; en ${conAhorro} evitar escaleras cambia el camino; ${sinOpcion} no tienen camino sin escaleras`);

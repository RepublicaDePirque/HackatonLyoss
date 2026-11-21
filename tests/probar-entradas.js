// Pruebas de las entradas de los edificios: node tests/probar-entradas.js
// Revisa que js/generado/entradas.js (de data/entradas.json) sea coherente con los contornos, el plano y los destinos,
// y que index.html lo use. La elección de puerta se prueba aparte, con el código de la página.
const assert = require("assert"), fs = require("fs"), path = require("path");
const leer = f => fs.readFileSync(path.join(__dirname, "..", f), "utf8");
const { ENTRADAS, PASOS } = new Function(leer("js/generado/entradas.js") + "; return { ENTRADAS, PASOS };")();
const CONTORNOS = new Function(leer("js/generado/contornos.js") + "; return CONTORNOS;")();
const fuente = JSON.parse(leer("data/entradas.json"));
const MPP = fuente.calibracion.mpp, MAX_M = 25;

const distPoli = (px, py, poly) => {                 // metros al contorno (0 si está adentro)
  let dentro = false, mejor = Infinity;
  for (let i = 0, j = poly.length - 1; i < poly.length; j = i++) {
    const [x1, y1] = poly[j], [x2, y2] = poly[i], dx = x2 - x1, dy = y2 - y1, L2 = dx * dx + dy * dy;
    if ((y1 > py) !== (y2 > py) && px < (x2 - x1) * (py - y1) / (y2 - y1) + x1) dentro = !dentro;
    const t = L2 ? Math.max(0, Math.min(1, ((px - x1) * dx + (py - y1) * dy) / L2)) : 0;
    mejor = Math.min(mejor, Math.hypot(px - (x1 + t * dx), py - (y1 + t * dy)));
  }
  return dentro ? 0 : mejor * MPP;
};
const grupo = { P: ["P", "P2"], R: ["R", "R2"] };

let puertas = 0;
for (const [k, lista] of Object.entries(ENTRADAS)) {
  assert.ok(CONTORNOS.edificios[k], `el edificio «${k}» no tiene contorno`);
  assert.ok(lista.length > 0, `«${k}» sin puertas`);
  for (const e of lista) {
    puertas++;
    assert.ok(e.n && typeof e.n === "string", `puerta sin descripción en ${k}`);
    assert.ok(e.px > -60 && e.px < 1371 && e.py > -60 && e.py < 1066, `${k} «${e.n}» fuera del plano`);
    assert.ok([true, false, null].includes(e.a), `${k} «${e.n}»: accesible debe ser true, false o null`);
    const d = Math.min(...(grupo[k] || [k]).map(g => distPoli(e.px, e.py, CONTORNOS.edificios[g])));
    assert.ok(d <= MAX_M, `${k} «${e.n}» queda a ${d.toFixed(0)} m de su edificio (máx. ${MAX_M})`);
  }
}
// Todo lo que está en data/entradas.json está en la salida, salvo lo descartado por quedar lejos de su edificio.
const enFuente = fuente.entradas.length, omitidas = enFuente - puertas;
assert.ok(omitidas >= 0 && omitidas <= 3, `se omitieron ${omitidas} puertas: revisar con tools/generar-entradas.py`);
// Cada edificio con puertas corresponde a un destino de la app (P2 y R2 son parte de P y R).
const destinos = new Set([...Object.values(CONTORNOS.areaDe), ...CONTORNOS.extra.map(e => e.area)]);
for (const k of Object.keys(ENTRADAS)) assert.ok(destinos.has(k) || ["P2", "R2"].includes(k), `«${k}» tiene puertas pero ningún destino lo usa`);
// Pasos por dentro de edificios (atajos de puerta a puerta): trazos válidos dentro del plano y de un edificio que existe.
for (const s of PASOS) {
  assert.ok(CONTORNOS.edificios[s.k], `paso «${s.n}»: el edificio «${s.k}» no tiene contorno`);
  assert.ok(Array.isArray(s.p) && s.p.length >= 2, `paso «${s.n}»: necesita al menos 2 puntos`);
  for (const [x, y] of s.p) assert.ok(x > -60 && x < 1371 && y > -60 && y < 1066, `paso «${s.n}»: un punto cae fuera del plano`);
  assert.ok([true, false, null].includes(s.a), `paso «${s.n}»: accesible debe ser true, false o null`);
  const largo = s.p.reduce((t, q, i) => i ? t + Math.hypot(q[0] - s.p[i - 1][0], q[1] - s.p[i - 1][1]) * MPP : 0, 0);
  assert.ok(largo > 3 && largo <= 250, `paso «${s.n}» mide ${largo.toFixed(0)} m: ¿está bien trazado?`);
}
assert.strictEqual(PASOS.length, (fuente.pasos || []).length, "algún paso de data/entradas.json no llegó a la salida: correr tools/generar-entradas.py");
// La página carga las entradas y las usa.
const html = leer("index.html"), sw = leer("sw.js");
assert.ok(html.includes('src="js/generado/entradas.js"'), "index.html no carga entradas.js");
assert.ok(/function elegirPuerta/.test(html) && /function miraDe/.test(html), "index.html no elige puerta");
assert.ok(/function conectarPasos/.test(html) && /function interiorAdelante/.test(html), "index.html no usa los pasos por dentro");
assert.ok(sw.includes("js/generado/entradas.js"), "sw.js no guarda entradas.js para usarse sin conexión");

console.log(`ok: ${puertas} puertas en ${Object.keys(ENTRADAS).length} edificios (${omitidas} omitida${omitidas === 1 ? "" : "s"} por quedar lejos de su edificio) y ${PASOS.length} paso${PASOS.length === 1 ? "" : "s"} por dentro`);

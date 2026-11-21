// Pruebas de la señal de la brújula (resplandor, barra y flecha): node tests/probar-senal.js
// 1) colores: azul lejos, morado a mitad de camino, rojo cerca; 2) la luz no usa blur y su degradado llega a 0 en el borde de la caja;
// 3) el giro toma el camino corto (359° → 1° no da una vuelta entera) y converge.
// Extrae el bloque «Resplandor» de index.html y lo ejecuta con un DOM mínimo.
const assert = require("assert"), fs = require("fs"), path = require("path"), vm = require("vm");

const html = fs.readFileSync(path.join(__dirname, "../index.html"), "utf8");
const ini = html.indexOf("// ---------- Resplandor");
const fin = html.indexOf("function pintarLuz(ev) {");
assert(ini > 0 && fin > ini, "no encontré el bloque «Resplandor» en index.html");

const els = {};
const el = () => ({ style: {}, firstElementChild: { style: {} }, setAttribute() {} });
const cola = [];
const ctx = {
  Math, Date, console, performance: { now: () => 0 },
  toRad: d => d * Math.PI / 180,
  $: id => els[id] || (els[id] = el()),
  requestAnimationFrame: f => { cola.push(f); return cola.length; },
  matchMedia: () => ({ matches: false }),
};
ctx.window = ctx;
vm.createContext(ctx);
vm.runInContext(html.slice(ini, fin) + "\n;globalThis.__t = { colorDist, luzSuave, CURVA_G1, CURVA_G2, senal, girarSenal, moverSenal };", ctx);
const T = ctx.__t;

// --- 1) colores
const rgb = s => s.match(/\d+/g).map(Number);
const [lr, lg, lb] = rgb(T.colorDist(0)), [mr, mg, mb] = rgb(T.colorDist(0.5)), [cr, cg, cb] = rgb(T.colorDist(1));
assert(lb > lr && lb > lg, `lejos debe ser azul: ${T.colorDist(0)}`);
assert(mr > mg && mb > mg && mb > 150, `a mitad de camino debe ser morado: ${T.colorDist(0.5)}`);
assert(cr > 200 && cg < 110 && cb < 130, `cerca debe ser rojo: ${T.colorDist(1)}`);
assert(T.colorDist(-5) === T.colorDist(0) && T.colorDist(9) === T.colorDist(1), "c fuera de [0, 1] se recorta");
console.log(`ok: colores lejos ${T.colorDist(0)}, medio ${T.colorDist(0.5)}, cerca ${T.colorDist(1)}`);

// --- 2) luz sin caja visible
for (const curva of [T.CURVA_G1, T.CURVA_G2]) {
  const g = T.luzSuave("rgb(10,20,30)", curva);
  assert(g.includes("closest-side"), "el degradado debe medirse hasta el lado más cercano");
  assert(/rgba\(10,20,30,0\) 100%\)$/.test(g), "el degradado debe terminar transparente en el borde de la caja");
  const alfas = curva.map(([, a]) => a);
  assert(alfas.every((a, i) => i === 0 || a <= alfas[i - 1]), "la opacidad solo puede bajar");
}
assert(!/filter\s*:\s*blur|blur\(\$\{/.test(html.slice(html.indexOf("function pintarLuz"), html.indexOf("// ---------- Evaluación"))), "pintarLuz no debe usar blur");
console.log("ok: la luz es un degradado que llega a 0 antes del borde, sin blur");

// --- 3) giro por el camino corto
const correr = () => { let n = 0, t = 0; while (cola.length && n++ < 600) { t += 16; cola.shift()(t); } return n; };
T.senal.p = { W: 390, H: 844, cx: 195, cy: 422, largo: 100, grosor: 5 };
T.girarSenal(359); assert.strictEqual(T.senal.actual, 359, "el primer valor se fija sin animar");
T.girarSenal(1);
const vistos = [];
for (let i = 0; i < 200 && cola.length; i++) { const f = cola.shift(); f((i + 1) * 16); vistos.push(((T.senal.actual % 360) + 360) % 360); }
assert(vistos.length > 5, "debe animar en varios cuadros");
assert(vistos.every(a => a >= 358.9 || a <= 1.1), `359° → 1° debe pasar por el norte, no dar la vuelta: ${vistos.slice(0, 6).map(a => a.toFixed(1))}`);
assert(Math.abs(((T.senal.actual - 1 + 540) % 360) - 180) < 0.1, "converge al ángulo meta");
console.log(`ok: 359° → 1° en ${vistos.length} cuadros sin dar la vuelta`);

T.girarSenal(180); correr(); T.girarSenal(0); correr();
assert(Math.abs(((T.senal.actual % 360) + 360) % 360) < 0.1 || Math.abs(((T.senal.actual % 360) + 360) % 360 - 360) < 0.1, "vuelve al norte");
// la barra queda dentro de la pantalla en todos los ángulos
for (let a = 0; a < 360; a += 15) {
  T.senal.actual = a; T.moverSenal();
  const b = els.barra.style, l = parseFloat(b.left), t = parseFloat(b.top), w = parseFloat(b.width), h = parseFloat(b.height);
  assert(l >= 0 && t >= 0 && l + w <= 390 + 0.01 && t + h <= 844 + 0.01, `la barra se sale de la pantalla a ${a}°: ${l},${t},${w},${h}`);
}
console.log("ok: la barra queda dentro de la pantalla en los 24 ángulos revisados");

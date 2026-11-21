// «Evitar escaleras», para movilidad reducida (muletas, una lesión, cansancio). No es una ruta para silla de
// ruedas: solo conoce las escaleras marcadas en OpenStreetMap; no sabe de pendientes, superficies ni puertas.
// Se carga después del script de index.html y usa sus globales (state, astar, graph, stairs, pathLen, distance, nearest, destNode).

// Una escalera larga puede venir en varios tramos seguidos: se cuenta como una.
function contarEscaleras(path, esEscalera) {
  let n = 0, dentro = false;
  for (let i = 0; i < path.length - 1; i++) {
    const e = esEscalera(path[i], path[i + 1]);
    if (e && !dentro) n++;
    dentro = e;
  }
  return n;
}
const plural = n => n === 1 ? "1 escalera" : n + " escaleras";
const red5 = m => Math.round(m / 5) * 5;

// r = { corto: { m, esc }, evita: { m, esc } }: el camino más corto y el que evita escaleras.
function fraseEscaleras(r) {
  const fin = " No considera pendientes.";
  if (!r) return "";
  if (r.corto.esc === 0) return "Este camino no tiene escaleras." + fin;
  const extra = red5(r.evita.m - r.corto.m);
  if (r.evita.esc === 0)
    return `Sin escaleras: ${red5(r.evita.m)} m` + (extra > 0 ? `, ${extra} m más` : "") + `. El camino corto tiene ${plural(r.corto.esc)}.` + fin;
  if (r.evita.esc < r.corto.esc)
    return `No hay camino sin escaleras. Este tiene ${plural(r.evita.esc)}; el corto tiene ${r.corto.esc}.` + fin;
  return `No hay camino sin escaleras: este tiene ${plural(r.evita.esc)}.` + fin;
}

// Compara ambos caminos desde donde estás. No parte del siguiente nodo de la ruta (g.target): ese nodo ya
// pertenece al camino elegido y sesgaría la comparación. A lo más una vez por segundo: la brújula dibuja ~60 veces.
let _resEsc = { clave: "", t: 0, r: null };
function resumenEscaleras(g) {
  if (!g) return null;
  const inicios = g.onGraph ? [g.snap.a, g.snap.b] : [nearest(graph, state.user)];
  const clave = inicios.join("|") + "|" + destNode(), ahora = Date.now();
  if (_resEsc.clave === clave && ahora - _resEsc.t < 1000) return _resEsc.r;
  const esEsc = (a, b) => stairs.has(a + "|" + b);
  const era = state.accesible, medir = evitar => {
    state.accesible = evitar;
    let mejor = null;
    for (const ini of inicios) {
      const p = astar(graph, ini, destNode()); if (!p) continue;
      let tramos = 0; for (let i = 0; i < p.length - 1; i++) if (esEsc(p[i], p[i + 1])) tramos++;
      const m = distance(g.pos, graph[ini]) + pathLen(p), costo = m + tramos * (evitar ? PENAL_EVITAR : PENAL_ESCALERA);
      if (!mejor || costo < mejor.costo) mejor = { m, costo, esc: contarEscaleras(p, esEsc) };
    }
    return mejor;
  };
  let corto, evita;
  try { corto = medir(false); evita = medir(true); } finally { state.accesible = era; }
  _resEsc = { clave, t: ahora, r: corto && evita ? { corto, evita } : null };
  return _resEsc.r;
}

if (typeof module !== "undefined") module.exports = { contarEscaleras, fraseEscaleras };

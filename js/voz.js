// Modo voz: la misma brújula dicha en palabras, para personas ciegas o con baja visión.
// Modelo «faro + entorno»: dirección en horas del reloj, distancia y lo que hay alrededor. No da una ruta
// ni detecta obstáculos: eso lo resuelven el bastón o el perro guía.
// Se carga después del script de index.html y usa sus globales (state, evaluar, info, AREAS, ZONAS…).

// ---------- Frases (funciones puras) ----------
// rel = grados en sentido horario entre hacia donde apunta el teléfono y el destino (0 = justo adelante).
const vozNorm = rel => ((rel % 360) + 360) % 360;
const horaReloj = rel => Math.round(vozNorm(rel) / 30) % 12 || 12;
const fraseHora = rel => { const h = horaReloj(rel); return h === 1 ? "a la 1" : "a las " + h; };
const ladoDe = rel => { const r = vozNorm(rel); return r <= 30 || r >= 330 ? "adelante" : r < 150 ? "a tu derecha" : r <= 210 ? "detrás de ti" : "a tu izquierda"; };
const fraseMetros = m => m === 1 ? "1 metro" : m + " metros";
const fraseDonde = (nombre, rel, m) => `${nombre}, ${fraseHora(rel)}, ${fraseMetros(m)}`;

if (typeof module !== "undefined") module.exports = { horaReloj, fraseHora, ladoDe, fraseDonde };

if (typeof document !== "undefined") (function () {
  const MIN_ENTRE_AVISOS = 6000;   // ms: no hablar encima de lo anterior
  const PASO_M = 25;               // avisa cada 25 m de avance
  const CERCA_M = 25;              // un edificio «está al lado» a 25 m o menos de su borde
  const APUNTA = 15;               // grados: el teléfono «apunta» al destino dentro de ±15°

  const V = { on: false, hablar: false, ultimo: 0, dest: null, tramo: null, estado: "", vistos: new Set(), zona: null, alerta: "", apunta: false, timer: null };
  const guardar = (k, v) => { try { localStorage.setItem(k, v ? "1" : ""); } catch (e) {} };
  const leer = k => { try { return !!localStorage.getItem(k); } catch (e) { return false; } };

  // ---------- Interfaz (se inyecta aquí para no tocar el marcado de index.html) ----------
  const css = document.createElement("style");
  css.textContent = `
    .voz-solo-lector { position:absolute; width:1px; height:1px; overflow:hidden; clip-path:inset(50%); white-space:nowrap; }
    #vozDonde { display:none; min-height:96px; border:0; border-radius:22px; background:var(--fg); color:var(--bg); font-family:'Chakra Petch',sans-serif; font-weight:700; font-size:26px; }
    #vozDicho { display:none; font-size:17px; line-height:1.4; font-weight:600; text-align:center; min-height:48px; }
    .voz-fila { display:flex; gap:8px; }
    .voz-fila button { flex:1 1 0; min-height:44px; border-radius:22px; border:1px solid var(--line); background:transparent; color:var(--fg); font-size:15px; font-weight:600; }
    .voz-fila button[aria-pressed="true"] { background:var(--fg); color:var(--bg); }
    #vozHablar { display:none; }
    .modo-voz #vozDonde, .modo-voz #vozDicho { display:block; }
    .modo-voz #vozHablar { display:block; }
    .modo-voz .pista, .modo-voz .selector { display:none; }
    #btnVoz { min-height:48px; border-radius:18px; border:1px solid var(--line); background:transparent; color:var(--fg); font-size:16px; font-weight:600; width:100%; }
  `;
  document.head.appendChild(css);

  const live = document.createElement("div");
  live.id = "vozLive"; live.className = "voz-solo-lector"; live.setAttribute("aria-live", "assertive"); live.setAttribute("aria-atomic", "true");
  document.body.appendChild(live);

  const btnVoz = document.createElement("button");
  btnVoz.id = "btnVoz"; btnVoz.textContent = "Activar con modo voz (sin mirar la pantalla)";
  $("btnActivar").insertAdjacentElement("afterend", btnVoz);

  const base = $("base");
  base.insertAdjacentHTML("afterbegin",
    `<p id="vozDicho" aria-hidden="true"></p>
     <button id="vozDonde" aria-label="¿Dónde está mi destino?">¿Dónde está?</button>`);
  $("btnYaLlegue").insertAdjacentHTML("beforebegin",
    `<div class="voz-fila">
       <button id="vozModo" aria-pressed="false">Modo voz</button>
       <button id="vozHablar" aria-pressed="false">Voz de la app</button>
     </div>`);

  // ---------- Salida: lector de pantalla (región viva) y, opcional, la voz de la app ----------
  let vozEs = null;
  const elegirVoz = () => {
    const vs = (window.speechSynthesis && speechSynthesis.getVoices()) || [];
    vozEs = vs.find(v => /^es[-_](CL|419|MX|US)/i.test(v.lang)) || vs.find(v => /^es/i.test(v.lang)) || null;
  };
  if (window.speechSynthesis) { elegirVoz(); speechSynthesis.onvoiceschanged = elegirVoz; }

  function decir(texto, urgente) {
    if (!V.on || !texto) return;
    const ahora = Date.now();
    V.ultimo = ahora;
    live.textContent = ""; setTimeout(() => { live.textContent = texto; }, 60);        // vaciar primero: así el lector repite frases iguales
    $("vozDicho").textContent = texto;
    if (V.hablar && window.speechSynthesis) {
      try {
        if (urgente) speechSynthesis.cancel();
        const u = new SpeechSynthesisUtterance(texto);
        u.lang = vozEs ? vozEs.lang : "es-CL"; if (vozEs) u.voice = vozEs;
        speechSynthesis.speak(u);
      } catch (e) {}
    }
  }

  // ---------- Qué se dice ----------
  const DESTINO_DE_AREA = {};
  for (const id in INFO) { const a = areaOf(id); if (a && !(a in DESTINO_DE_AREA)) DESTINO_DE_AREA[a] = INFO[id].nombre; }
  const EDIFICIOS = Object.keys(CONTORNOS.edificios).filter(k => DESTINO_DE_AREA[k]);

  function dondeEsta() {
    const nombre = info(state.destId).nombre;
    if (!tieneUbicacion()) return "Todavía no sabemos dónde estás. " + (state.gpsError || "Buscando señal de GPS.");
    const ev = evaluar();
    if (ev.llego) return "Estás " + enDestino(nombre) + ".";
    return fraseDonde(nombre, ev.rel, ev.m) + (ev.impreciso ? ". La señal es imprecisa." : ".");
  }

  function reiniciar() {
    V.dest = state.destId; V.tramo = null; V.estado = ""; V.vistos = new Set(); V.zona = null; V.alerta = "";
  }

  function paso() {
    if (!V.on) return;
    if (state.vista === "llegada" && V.dest === state.destId && V.estado !== "llego") {   // la brújula ya cambió de pantalla
      V.estado = "llego"; const d = info(state.destId);
      decir(`Llegaste ${aDestino(d.nombre)}. ${d.pista || ""}`, true); return;
    }
    if (state.vista !== "brujula") return;
    if (!tieneUbicacion()) { if (V.estado !== "sin") { V.estado = "sin"; decir("Todavía no sabemos dónde estás. Mantén el teléfono en la mano, al aire libre."); } return; }
    const nombre = info(state.destId).nombre, i = info(state.destId);
    if (V.dest !== state.destId) {
      reiniciar();
      decir(`Vas ${aDestino(nombre)}. ${dondeEsta()} ${i.pista || ""} Sostén el teléfono plano, apuntando hacia donde caminas.`, true);
      const ev0 = evaluar(); V.tramo = Math.floor(ev0.m / PASO_M);
      return;
    }
    const ev = evaluar();

    // 1. estado: llegada, detrás, alejándose, casi
    const detras = ev.rel > 135 && ev.rel < 225;
    const estado = ev.llego ? "llego" : ev.aleja ? "aleja" : detras ? "detras" : ev.dArea <= 60 ? "casi" : "bien";
    if (estado !== V.estado) {
      const antes = V.estado; V.estado = estado;
      if (estado === "llego") { decir(`Llegaste ${aDestino(nombre)}. ${i.pista || ""}`, true); return; }
      if (estado === "aleja") { decir(`Te estás alejando. ${fraseDonde(nombre, ev.rel, ev.m)}.`, true); return; }
      if (estado === "detras") { decir(`${nombre} está detrás de ti. Date vuelta.`, true); return; }
      if (estado === "casi") { decir(`Casi llegas. ${fraseDonde(nombre, ev.rel, ev.m)}.`, true); return; }
      if (antes === "aleja" || antes === "detras") { decir(`Vas bien. ${fraseDonde(nombre, ev.rel, ev.m)}.`); return; }
    }
    if (ev.llego) return;

    // 2. escaleras (el texto lo calcula la brújula)
    const alerta = ($("alerta").textContent || "").replace(/^[^\wÁÉÍÓÚáéíóúÑñ]+/, "");
    if (alerta !== V.alerta) { V.alerta = alerta; if (alerta) { decir("Atención. " + alerta + ".", true); return; } }

    // Lo que sigue no es urgente: espera su turno sin darse por dicho, para que nada se pierda.
    if (Date.now() - V.ultimo < MIN_ENTRE_AVISOS) return;

    // 3. dato curioso de la zona
    if (state.zona && V.zona !== state.zona.id) { V.zona = state.zona.id; decir(`${state.zona.titulo}. ${state.zona.gancho}. ${state.zona.texto}`); return; }

    // 4. entorno: edificios al lado, una vez cada uno
    const propia = areaOf(state.destId);
    for (const k of EDIFICIOS) {
      if (V.vistos.has(k) || (propia && grupo(propia).includes(k)) || k === propia) continue;
      const c = nearestOnArea(state.user, k);
      if (c.d > CERCA_M) continue;
      V.vistos.add(k);
      const lado = c.d < 2 ? "junto a ti" : ladoDe(bearing(state.user, c) - state.heading);
      decir(`${DESTINO_DE_AREA[k]}, ${lado}.`);
      return;
    }

    // 5. avance: cada 25 m
    const tramo = Math.floor(ev.m / PASO_M);
    if (V.tramo === null) V.tramo = tramo;
    if (tramo < V.tramo) { V.tramo = tramo; decir(`${fraseHora(ev.rel)}, ${fraseMetros(ev.m)}.`.replace(/^a/, "A")); }
    else if (tramo > V.tramo) V.tramo = tramo;
  }

  // Android: un pulso cuando el teléfono queda apuntando al destino (en iPhone la web no vibra).
  function pulso() {
    if (!V.on || state.vista !== "brujula" || !tieneUbicacion()) return;
    const aim = miraDe();                                       // la puerta elegida (o el borde si no hay puertas marcadas)
    const rel = vozNorm(bearing(state.user, aim) - state.heading), apunta = rel <= APUNTA || rel >= 360 - APUNTA;
    if (apunta && !V.apunta) vibrar(60);
    V.apunta = apunta;
  }

  // ---------- Encendido y apagado ----------
  function aplicar() {
    $("vBrujula").classList.toggle("modo-voz", V.on);
    $("vozModo").setAttribute("aria-pressed", V.on);
    $("vozHablar").setAttribute("aria-pressed", V.hablar);
    ["titulo", "bajada"].forEach(id => $(id).setAttribute("aria-live", V.on ? "off" : "polite"));   // la región viva ya lo dice
    clearInterval(V.timer); clearInterval(V.timerPulso);
    if (V.on) { V.timer = setInterval(paso, 1000); V.timerPulso = setInterval(pulso, 200); }
    else if (window.speechSynthesis) speechSynthesis.cancel();
    if (typeof render === "function") render();
  }
  function setVoz(on) { V.on = on; guardar("modoVoz", on); V.dest = null; aplicar(); if (on && state.vista === "brujula") paso(); }
  function setHablar(on) { V.hablar = on; guardar("vozApp", on); aplicar(); if (on) decir("Voz de la app activada.", true); }

  $("vozModo").onclick = () => setVoz(!V.on);
  $("vozHablar").onclick = () => setHablar(!V.hablar);
  $("vozDonde").onclick = () => decir(dondeEsta(), true);
  btnVoz.onclick = () => {
    V.on = true; guardar("modoVoz", true); aplicar();
    decir("Modo voz activado. Elige un destino.", true);     // dentro del toque: así iOS deja hablar a la app después
    $("btnActivar").click();
  };

  const p = new URLSearchParams(location.search);
  V.on = p.has("voz") || leer("modoVoz");
  V.hablar = p.has("voz") || leer("vozApp");
  aplicar();
  window.VOZ = { estado: V, paso, dondeEsta };               // para pruebas
})();

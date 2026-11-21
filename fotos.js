// Fotos comunitarias: capturar, comprimir, publicar y leer (Firestore, sin Cloud Storage).
// Módulo ES; expone window.Fotos. Sin UI: el diseño solo llama a esta API.
//   Fotos.capturarFoto()                    -> { dataUrl, bytes } | null   (llamar desde un toque del usuario)
//   Fotos.ladoDesde(pos, areaKey)           -> "N"|"S"|"E"|"O"|null        (null si está dentro o sin contorno)
//   Fotos.ladoAproximacion(destId, desde)   -> lado por el que llega la ruta al destino
//   Fotos.publicarFoto(edificio, lado, dataUrl) -> id
//   Fotos.fotoPara(edificio, lado)          -> { id, foto, lado, reportes, creada } | null
//   Fotos.reportar(id)
// Usa los globales de index.html: AREAS, grupo, toXY, nearestOnPoly, graph, astar, nearest, areaOf, state, destNode.

import { initializeApp } from "https://www.gstatic.com/firebasejs/10.12.2/firebase-app.js";
import { getAuth, signInAnonymously } from "https://www.gstatic.com/firebasejs/10.12.2/firebase-auth.js";
import { getFirestore, collection, addDoc, getDocs, updateDoc, doc, increment, query, where, limit, serverTimestamp }
  from "https://www.gstatic.com/firebasejs/10.12.2/firebase-firestore.js";

// Pegar aquí el firebaseConfig de la consola (es público; la seguridad está en firebase/firestore.rules).
const FIREBASE_CONFIG = {
  apiKey: "AIzaSyAgJbb4BpPz2YSiVdyYomGc981GgkqbJlk",
  authDomain: "brujula-usm.firebaseapp.com",
  projectId: "brujula-usm",
  storageBucket: "brujula-usm.firebasestorage.app",
  messagingSenderId: "83058628910",
  appId: "1:83058628910:web:d9d7c2e2e64687e17502bf",
};
const MAX_BYTES = 250_000;   // tamaño objetivo del JPEG (el documento de Firestore admite 1 MB; la regla pide ≤ 300 KB en base64)
const MAX_LADO_PX = 1024;
const OCULTAR_REPORTES = 3;

let _db = null;
async function db() {
  if (_db) return _db;
  const app = initializeApp(FIREBASE_CONFIG);
  await signInAnonymously(getAuth(app));
  return (_db = getFirestore(app));
}

// ---------- Captura y compresión (el re-dibujado en canvas elimina EXIF/GPS) ----------
async function comprimir(file) {
  const bmp = await createImageBitmap(file, { imageOrientation: "from-image" });
  const k = Math.min(1, MAX_LADO_PX / Math.max(bmp.width, bmp.height));
  const c = document.createElement("canvas");
  c.width = Math.round(bmp.width * k); c.height = Math.round(bmp.height * k);
  c.getContext("2d").drawImage(bmp, 0, 0, c.width, c.height);
  let q = 0.8, dataUrl;
  do { dataUrl = c.toDataURL("image/jpeg", q); q -= 0.1; } while (dataUrl.length * 0.75 > MAX_BYTES && q > 0.2);
  return { dataUrl, bytes: Math.round(dataUrl.length * 0.75) };
}

function capturarFoto() {
  return new Promise((resolve, reject) => {
    const inp = document.createElement("input");
    inp.type = "file"; inp.accept = "image/*"; inp.capture = "environment";
    inp.onchange = async () => {
      const f = inp.files[0];
      if (!f) return resolve(null);
      try { resolve(await comprimir(f)); } catch (e) { reject(e); }
    };
    inp.oncancel = () => resolve(null);
    inp.click();
  });
}

// ---------- Lado del edificio ----------
// Lado = hacia dónde queda el punto respecto del borde más cercano del edificio (si estás al este, es el lado E).
function ladoDesde(pos, areaKey) {
  const q = toXY(pos); let best = { d: Infinity };
  for (const k of grupo(areaKey)) { const r = nearestOnPoly(q, AREAS[k]); if (r.d < best.d) best = r; }
  if (!isFinite(best.d) || best.d < 0.5) return null;                // dentro del edificio o sin contorno
  const dx = q.x - best.x, dy = q.y - best.y;                        // x = este, y = norte
  return Math.abs(dx) > Math.abs(dy) ? (dx > 0 ? "E" : "O") : (dy > 0 ? "N" : "S");
}

// Lado por el que llega la ruta: el penúltimo nodo del camino al destino, visto desde el borde.
function ladoAproximacion(destId, desde = state.user) {
  const area = areaOf(destId); if (!area) return null;
  const path = astar(graph, nearest(graph, desde), destNode());
  const prev = path && path.length > 1 ? graph[path[path.length - 2]] : desde;
  return ladoDesde(prev, area);
}

// ---------- Firestore ----------
async function publicarFoto(edificio, lado, dataUrl) {
  if (!["N", "S", "E", "O"].includes(lado)) throw new Error("Lado inválido");
  const r = await addDoc(collection(await db(), "fotos"),
    { edificio, lado, foto: dataUrl, reportes: 0, creada: serverTimestamp() });
  return r.id;
}

// Foto del lado pedido (la más reciente con pocos reportes); si no hay, cualquiera del edificio.
// Consulta solo por edificio y filtra en el cliente para no necesitar índice compuesto.
async function fotoPara(edificio, lado) {
  const snap = await getDocs(query(collection(await db(), "fotos"), where("edificio", "==", edificio), limit(30)));
  const fotos = snap.docs.map(d => ({ id: d.id, ...d.data() }))
    .filter(f => (f.reportes || 0) < OCULTAR_REPORTES)
    .sort((a, b) => (b.creada?.seconds || 0) - (a.creada?.seconds || 0));
  return fotos.find(f => f.lado === lado) || fotos[0] || null;
}

async function reportar(id) {
  await updateDoc(doc(await db(), "fotos", id), { reportes: increment(1) });
}

window.Fotos = { capturarFoto, ladoDesde, ladoAproximacion, publicarFoto, fotoPara, reportar };

// Fotos comunitarias: comprimir, publicar y leer (Firestore, sin Cloud Storage).
// Script clásico (sin import estático): el SDK de Firebase se descarga solo cuando hace falta, así que
// si no hay conexión este archivo carga igual y las funciones fallan con un error que la interfaz captura.
// Expone window.Fotos:
//   Fotos.comprimir(file)                   -> dataUrl JPEG que cabe en la regla de Firestore (re-dibujado: sin EXIF/GPS)
//   Fotos.publicarFoto(edificio, lado, dataUrl) -> id
//   Fotos.fotosDe(edificio)                 -> [{ id, foto, lado, reportes, creada }] visibles, la más reciente primero
//   Fotos.reportar(id)
// `lado` (N, S, E u O) es el lado del edificio desde el que se tomó la foto; lo exigen las reglas.

(function () {
  // Es público por diseño; la seguridad está en firebase/firestore.rules y en la restricción de la API key por dominio.
  const FIREBASE_CONFIG = {
    apiKey: "AIzaSyAgJbb4BpPz2YSiVdyYomGc981GgkqbJlk",
    authDomain: "brujula-usm.firebaseapp.com",
    projectId: "brujula-usm",
    storageBucket: "brujula-usm.firebasestorage.app",
    messagingSenderId: "83058628910",
    appId: "1:83058628910:web:d9d7c2e2e64687e17502bf",
  };
  const SDK = "https://www.gstatic.com/firebasejs/10.12.2/";
  const MAX_CHARS = 290_000;   // la regla pide que el string de la foto (data URL en base64) tenga ≤ 300000 caracteres
  const MAX_LADO_PX = 1024;
  const OCULTAR_REPORTES = 3;

  let _fb = null;
  function firebase() {
    if (!_fb) _fb = (async () => {
      const [app, auth, fs] = await Promise.all([
        import(SDK + "firebase-app.js"), import(SDK + "firebase-auth.js"), import(SDK + "firebase-firestore.js"),
      ]);
      const a = app.initializeApp(FIREBASE_CONFIG);
      await auth.signInAnonymously(auth.getAuth(a));
      return { fs, db: fs.getFirestore(a) };
    })().catch(e => { _fb = null; throw e; });       // si falla (sin red), el próximo intento vuelve a probar
    return _fb;
  }

  // ---------- Compresión ----------
  async function aBitmap(file) {
    try { return await createImageBitmap(file, { imageOrientation: "from-image" }); }
    catch (e) { return await createImageBitmap(file); }
  }
  async function comprimir(file) {
    const bmp = await aBitmap(file);
    for (let lado = MAX_LADO_PX; lado >= 480; lado = Math.round(lado * 0.8)) {
      const k = Math.min(1, lado / Math.max(bmp.width, bmp.height));
      const c = document.createElement("canvas");
      c.width = Math.round(bmp.width * k); c.height = Math.round(bmp.height * k);
      c.getContext("2d").drawImage(bmp, 0, 0, c.width, c.height);
      for (let q = 0.8; q >= 0.4; q -= 0.1) {
        const dataUrl = c.toDataURL("image/jpeg", q);
        if (dataUrl.length <= MAX_CHARS) return dataUrl;
      }
    }
    throw new Error("La foto no cabe en el tamaño permitido");
  }

  // ---------- Firestore ----------
  async function publicarFoto(edificio, lado, dataUrl) {
    if (!["N", "S", "E", "O"].includes(lado)) throw new Error("Lado inválido");
    const { fs, db } = await firebase();
    const r = await fs.addDoc(fs.collection(db, "fotos"),
      { edificio, lado, foto: dataUrl, reportes: 0, creada: fs.serverTimestamp() });
    return r.id;
  }

  // Consulta solo por edificio y filtra en el cliente para no necesitar un índice compuesto.
  async function fotosDe(edificio) {
    const { fs, db } = await firebase();
    const snap = await fs.getDocs(fs.query(fs.collection(db, "fotos"), fs.where("edificio", "==", edificio), fs.limit(30)));
    return snap.docs.map(d => ({ id: d.id, ...d.data() }))
      .filter(f => (f.reportes || 0) < OCULTAR_REPORTES)
      .sort((a, b) => (b.creada?.seconds || 0) - (a.creada?.seconds || 0));
  }

  async function reportar(id) {
    const { fs, db } = await firebase();
    await fs.updateDoc(fs.doc(db, "fotos", id), { reportes: fs.increment(1) });
  }

  window.Fotos = { comprimir, publicarFoto, fotosDe, reportar };
})();

#!/usr/bin/env python3
"""Genera js/generado/entradas.js (las puertas de los edificios) desde data/entradas.json.

Uso:  python3 tools/generar-entradas.py

data/entradas.json sale de marcar-entradas.html («Lista» > Copiar o Descargar). Para sumar o afinar puertas:
marcarlas ahí, guardar el JSON nuevo en data/entradas.json y volver a correr este script.
Solo se usan el edificio (clave del contorno), la descripción, el píxel del plano y si se entra sin escaleras:
lat/lng se recalculan en la app con la calibración, así que no hace falta que estén al día.
"""
import json, math, pathlib, re, sys

RAIZ = pathlib.Path(__file__).resolve().parent.parent
datos = json.load(open(RAIZ / "data/entradas.json", encoding="utf-8"))
contornos = json.loads(re.search(r"const CONTORNOS = (.*);", (RAIZ / "js/generado/contornos.js").read_text(encoding="utf-8")).group(1))["edificios"]
W, H, MPP = 1311, 1006, datos["calibracion"]["mpp"]

MAX_DIST_M = 25    # una puerta a más de esto del contorno de su edificio se descarta: casi seguro está mal asignada


def dist_a_contorno(px, py, poly):                          # metros del punto al contorno (0 si está adentro)
    dentro, mejor = False, 1e9
    for i in range(len(poly)):
        (x1, y1), (x2, y2) = poly[i - 1], poly[i]
        if (y1 > py) != (y2 > py) and px < (x2 - x1) * (py - y1) / (y2 - y1) + x1: dentro = not dentro
        dx, dy = x2 - x1, y2 - y1; L2 = dx * dx + dy * dy
        t = 0 if not L2 else max(0, min(1, ((px - x1) * dx + (py - y1) * dy) / L2))
        mejor = min(mejor, math.hypot(px - (x1 + t * dx), py - (y1 + t * dy)))
    return 0 if dentro else mejor * MPP


salida, errores, avisos, omitidas = {}, [], [], []
for i, e in enumerate(datos["entradas"], 1):
    k = e["edificio"]
    if k not in contornos:
        errores.append(f"entrada {i}: el edificio «{k}» no existe en contornos.js"); continue
    if not (-60 <= e["px"] <= W + 60 and -60 <= e["py"] <= H + 60):
        errores.append(f"entrada {i} ({k}): el punto ({e['px']}, {e['py']}) cae fuera del plano"); continue
    acc = e.get("accesible")
    if acc not in (True, False, None):
        errores.append(f"entrada {i} ({k}): «accesible» debe ser true, false o null"); continue
    nombre = (e.get("punto") or "").strip() or "Entrada"
    lejos = min(dist_a_contorno(e["px"], e["py"], contornos[g]) for g in {"P": ["P", "P2"], "R": ["R", "R2"]}.get(k, [k]))
    if lejos > MAX_DIST_M:
        omitidas.append(f"{k} «{nombre}»: queda a {lejos:.0f} m de su edificio (¿es de otro edificio?)"); continue
    for o in salida.get(k, []):
        if math.hypot(o["px"] - e["px"], o["py"] - e["py"]) * MPP < 3:
            avisos.append(f"{k}: «{nombre}» y «{o['n']}» están a menos de 3 m (¿repetida?)")
    salida.setdefault(k, []).append({"n": nombre, "px": round(e["px"], 1), "py": round(e["py"], 1), "a": acc})

# ---- pasos por dentro de edificios (atajos de puerta a puerta) ----
pasos = []
puertas_px = [(e["px"], e["py"]) for lista in salida.values() for e in lista]
for i, p in enumerate(datos.get("pasos", []), 1):
    k, pts, nom = p.get("edificio"), [(q["px"], q["py"]) for q in p.get("puntos", [])], (p.get("descripcion") or "").strip() or "Paso por dentro"
    if k not in contornos: errores.append(f"paso {i}: el edificio «{k}» no existe en contornos.js"); continue
    if len(pts) < 2: errores.append(f"paso {i} («{nom}»): necesita al menos 2 puntos"); continue
    if any(not (-60 <= x <= W + 60 and -60 <= y <= H + 60) for x, y in pts): errores.append(f"paso {i} («{nom}»): un punto cae fuera del plano"); continue
    acc = p.get("accesible")
    if acc not in (True, False, None): errores.append(f"paso {i} («{nom}»): «accesible» debe ser true, false o null"); continue
    # un paso puede ser una cadena que visita varias puertas: se revisa cada tramo, no el total
    tramos = [math.hypot(pts[j][0] - pts[j - 1][0], pts[j][1] - pts[j - 1][1]) * MPP for j in range(1, len(pts))]
    if max(tramos) > 200: avisos.append(f"paso «{nom}»: un tramo mide {max(tramos):.0f} m (¿está bien trazado?)")
    for extremo in (pts[0], pts[-1]):                      # un extremo sin puerta cerca se conecta al camino más cercano
        if not puertas_px or min(math.hypot(extremo[0] - a, extremo[1] - b) for a, b in puertas_px) * MPP > 6:
            avisos.append(f"paso «{nom}»: un extremo no coincide con una puerta marcada (a más de 6 m): se unirá al camino más cercano"); break
    pasos.append({"n": nom, "k": k, "p": [[round(x, 1), round(y, 1)] for x, y in pts], "a": acc, "h": (p.get("nota") or "").strip()})

if errores:
    print("ERRORES:"); [print("  -", x) for x in errores]; sys.exit(1)
(RAIZ / "js/generado/entradas.js").write_text(
    "// GENERADO por tools/generar-entradas.py desde data/entradas.json. No editar a mano.\n"
    "// n = descripción · px, py = píxel del plano · a = se entra sin escaleras (true), con escalera (false) o sin confirmar (null)\n"
    "const ENTRADAS = " + json.dumps(salida, ensure_ascii=False, separators=(",", ":")) + ";\n"
    "// PASOS: atajos por dentro de edificios, de puerta a puerta. n = descripción · k = edificio · p = puntos [px, py] en orden · a = sin escaleras (true), con escalera (false) o sin confirmar (null) · h = aviso (horario, acceso)\n"
    "const PASOS = " + json.dumps(pasos, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")
n = sum(len(v) for v in salida.values())
print(f"js/generado/entradas.js: {n} puertas en {len(salida)} edificios, {len(pasos)} pasos por dentro")
sin = sorted(set(contornos) - set(salida))
print("edificios con contorno y sin puerta:", ", ".join(sin) or "ninguno")
for a in avisos: print("  aviso:", a)
for o in omitidas: print("  OMITIDA:", o)

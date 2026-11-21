#!/usr/bin/env python3
"""Genera js/generado/grafo.js (caminos peatonales del campus) desde OpenStreetMap.

Uso:  python3 tools/generar-grafo.py        (necesita internet; la app luego funciona sin conexión)

- Baja de OSM los senderos, escaleras y calles de la zona que cubre assets/plano.jpeg.
- Simplifica la geometría, une los edificios con nombre al nodo de camino más cercano
  y deja solo la parte conectada del grafo.
- Si algo falta en el mapa, se corrige en openstreetmap.org y se vuelve a correr este script.

Datos de caminos © colaboradores de OpenStreetMap (licencia ODbL).
"""
import json, math, sys, time, urllib.request, urllib.error, urllib.parse, datetime, collections, pathlib

# ---- calibración del plano: debe coincidir con PLANO y ORIGIN de index.html ----
ORIGIN = (-33.034358, -71.595779)          # lat, lng del píxel (AX, AY)
MPP, ROT, AX, AY, W, H = 0.4601, 155.3, 810, 850, 1311, 1006

# Lugares que OSM no trae con nombre: píxel del plano -> se une al camino más cercano
LUGARES_MANUALES = [
    ("acceso-espana", "Acceso Av. España", (810, 850)),
    ("patio-central", "Patio Central", (873, 680)),
    ("edificio-b", "Edificio B", (947, 555)),
]
RENOMBRAR = {"Edificio Comerdores": "Edificio Comedores"}   # error de tipeo en OSM
MAX_DIST_EDIFICIO = 45      # m: más lejos que esto de un camino, el edificio no se agrega
EPS_SIMPLIFICAR = 1.5       # m, tolerancia de Ramer-Douglas-Peucker
DIST_COSTURA = 15           # m: un sendero que termina a menos de esto de otro se enlaza a él
HIGHWAYS = "footway|path|steps|pedestrian|service|living_street|residential|track|cycleway|unclassified"

KLAT = 111320.0
KLNG = KLAT * math.cos(math.radians(ORIGIN[0]))
rot = math.radians(ROT)


def plano_a_latlng(px, py):
    X, Y = (px - AX) * MPP, (AY - py) * MPP
    e = X * math.cos(rot) + Y * math.sin(rot)
    n = -X * math.sin(rot) + Y * math.cos(rot)
    return ORIGIN[0] + n / KLAT, ORIGIN[1] + e / KLNG


def xy(lat, lng):
    return ((lng - ORIGIN[1]) * KLNG, (lat - ORIGIN[0]) * KLAT)


def dentro_plano(lat, lng):
    e, n = xy(lat, lng)
    X, Y = e * math.cos(rot) - n * math.sin(rot), e * math.sin(rot) + n * math.cos(rot)
    px, py = AX + X / MPP, AY - Y / MPP
    return -20 <= px <= W + 20 and -20 <= py <= H + 20


def overpass(consulta):
    req = urllib.request.Request(
        "https://overpass-api.de/api/interpreter",
        data=urllib.parse.urlencode({"data": consulta}).encode(),
        headers={"User-Agent": "plano-calibracion/1.0", "Accept": "application/json"})
    for intento in range(5):                      # Overpass a veces responde 429/502/504: se reintenta
        try:
            with urllib.request.urlopen(req, timeout=90) as r:
                return json.load(r)["elements"]
        except urllib.error.HTTPError as err:
            if err.code not in (429, 502, 503, 504) or intento == 4:
                raise
            espera = 10 * (intento + 1)
            print(f"  Overpass respondió {err.code}, reintento en {espera} s…")
            time.sleep(espera)


def rdp(pts, eps):
    if len(pts) < 3:
        return pts
    (x1, y1), (x2, y2) = pts[0], pts[-1]
    dx, dy = x2 - x1, y2 - y1
    L2 = dx * dx + dy * dy
    dmax, imax = 0, 0
    for i in range(1, len(pts) - 1):
        px, py = pts[i]
        t = 0 if not L2 else max(0, min(1, ((px - x1) * dx + (py - y1) * dy) / L2))
        d = math.hypot(px - (x1 + t * dx), py - (y1 + t * dy))
        if d > dmax:
            dmax, imax = d, i
    if dmax <= eps:
        return [pts[0], pts[-1]]
    return rdp(pts[:imax + 1], eps)[:-1] + rdp(pts[imax:], eps)


def dist_punto_segmento(p, a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]
    L2 = dx * dx + dy * dy
    t = 0 if not L2 else max(0, min(1, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / L2))
    return math.hypot(p[0] - (a[0] + t * dx), p[1] - (a[1] + t * dy))


def main():
    # bbox del plano (esquinas -> lat/lng)
    esq = [plano_a_latlng(x, y) for x, y in ((0, 0), (W, 0), (0, H), (W, H))]
    s, n = min(c[0] for c in esq), max(c[0] for c in esq)
    o, e = min(c[1] for c in esq), max(c[1] for c in esq)
    bbox = f"{s},{o},{n},{e}"
    print("bbox", bbox)

    vias = overpass(f'[out:json][timeout:80];way["highway"~"^({HIGHWAYS})$"]({bbox});out body geom;')
    edificios = overpass(f'[out:json][timeout:80];way["building"]["name"]({bbox});out geom;')
    print(len(vias), "vías,", len(edificios), "edificios con nombre")

    # ---- filtrar vías ----
    validas = []
    for w in vias:
        t = w.get("tags", {})
        # OSM marca como access=private los caminos internos del campus (es una universidad privada),
        # que son justo los que usan los estudiantes: solo se excluye lo prohibido para peatones.
        if t.get("access") == "no" or t.get("foot") == "no" or t.get("indoor"):
            continue
        if "geometry" not in w:
            continue
        validas.append(w)

    # nodos compartidos entre vías (cruces) y extremos: se conservan siempre
    uso = collections.Counter()
    for w in validas:
        for nid in w["nodes"]:
            uso[nid] += 1
    coords = {}
    for w in validas:
        for nid, g in zip(w["nodes"], w["geometry"]):
            if g:
                coords[nid] = (g["lat"], g["lon"])

    aristas = {}   # (a,b) ordenado -> tipo (0 camino, 1 escalera)
    for w in validas:
        ids = [i for i in w["nodes"] if i in coords]
        if len(ids) < 2:
            continue
        tipo = 1 if w["tags"].get("highway") == "steps" else 0
        clave = [k for k, i in enumerate(ids) if k in (0, len(ids) - 1) or uso[i] > 1]
        for a, b in zip(clave, clave[1:]):
            tramo = ids[a:b + 1]
            pts = [xy(*coords[i]) for i in tramo]
            keep = rdp(pts, EPS_SIMPLIFICAR)
            idx = [tramo[pts.index(p)] for p in keep]
            for u, v in zip(idx, idx[1:]):
                if u != v and dentro_plano(*coords[u]) and dentro_plano(*coords[v]):
                    aristas[tuple(sorted((u, v)))] = max(aristas.get(tuple(sorted((u, v))), 0), tipo)

    # ---- costura: en OSM muchos senderos terminan pegados a otro sin compartir nodo ----
    def componentes(ar):
        padre = {}
        def raiz(x):
            while padre.setdefault(x, x) != x:
                padre[x] = padre[padre[x]]; x = padre[x]
            return x
        for u, v in ar:
            padre[raiz(u)] = raiz(v)
        grupos = collections.defaultdict(set)
        for x in list(padre):
            grupos[raiz(x)].add(x)
        return sorted(grupos.values(), key=len, reverse=True)

    def mejor_enlace(nodos, segmentos):
        """Nodo más cercano a algún segmento: (distancia, nodo, (a,b), t)."""
        mejor = None
        for u in nodos:
            p = xy(*coords[u])
            for (a, b) in segmentos:
                A, B = xy(*coords[a]), xy(*coords[b])
                dx, dy = B[0] - A[0], B[1] - A[1]
                L2 = dx * dx + dy * dy
                t = 0 if not L2 else max(0, min(1, ((p[0] - A[0]) * dx + (p[1] - A[1]) * dy) / L2))
                d = math.hypot(p[0] - (A[0] + t * dx), p[1] - (A[1] + t * dy))
                if mejor is None or d < mejor[0]:
                    mejor = (d, u, (a, b), t)
        return mejor

    siguiente = [-1]
    enlaces = []
    while True:
        comps = componentes(aristas)
        if len(comps) < 2:
            break
        grado = collections.Counter(x for ab in aristas for x in ab)
        principal_c = comps[0]
        seg_principal = [ab for ab in aristas if ab[0] in principal_c]
        extremos_principal = [x for x in principal_c if grado[x] == 1]
        candidatos = []
        for c in comps[1:]:
            seg_c = [ab for ab in aristas if ab[0] in c]
            m = mejor_enlace(c, seg_principal)                       # nodo de c -> tramo del principal
            if m: candidatos.append((m[0], m[1], m[2], m[3]))
            m2 = mejor_enlace(extremos_principal, seg_c)             # extremo libre del principal -> tramo de c
            if m2: candidatos.append((m2[0], m2[1], m2[2], m2[3]))
        candidatos = [c for c in candidatos if c[0] <= DIST_COSTURA]
        if not candidatos:
            break
        d, u, (a, b), t = min(candidatos, key=lambda c: c[0])
        A, B = xy(*coords[a]), xy(*coords[b])
        L = math.hypot(B[0] - A[0], B[1] - A[1])
        if t * L < 2:   w = a
        elif (1 - t) * L < 2: w = b
        else:
            w = siguiente[0]; siguiente[0] -= 1
            coords[w] = (coords[a][0] + t * (coords[b][0] - coords[a][0]), coords[a][1] + t * (coords[b][1] - coords[a][1]))
            tipo = aristas.pop((a, b))
            aristas[tuple(sorted((a, w)))] = tipo; aristas[tuple(sorted((w, b)))] = tipo
        if u != w:
            aristas[tuple(sorted((u, w)))] = 0
        enlaces.append(round(d, 1))
    print(f"costura: {len(enlaces)} enlaces añadidos (distancias en m: {enlaces})")

    # ---- componente conexa principal ----
    adj = collections.defaultdict(set)
    for u, v in aristas:
        adj[u].add(v); adj[v].add(u)
    visto, comps = set(), []
    for ini in adj:
        if ini in visto:
            continue
        comp, cola = {ini}, [ini]
        while cola:
            x = cola.pop()
            for y in adj[x]:
                if y not in comp:
                    comp.add(y); cola.append(y)
        visto |= comp
        comps.append(comp)
    comps.sort(key=len, reverse=True)
    print("componentes:", [len(c) for c in comps[:6]], "…")

    # ---- destinos: edificios con nombre -> nodo de camino más cercano al contorno ----
    def nodo_mas_cercano_a_contorno(poly, candidatos):
        mejor, md = None, 1e9
        for nid in candidatos:
            p = xy(*coords[nid])
            d = min(dist_punto_segmento(p, poly[i], poly[i + 1]) for i in range(len(poly) - 1))
            if d < md:
                mejor, md = nid, d
        return mejor, md

    principal = comps[0]
    destinos = []
    for w in edificios:
        nombre = w["tags"].get("name", "")
        if not nombre.startswith(("Edificio", "Gimnasio", "Museo")) or "geometry" not in w:
            continue
        if any(x in nombre for x in ("apartments",)) or w["tags"].get("building") == "apartments":
            continue
        poly = [xy(g["lat"], g["lon"]) for g in w["geometry"]]
        if len(poly) < 4 or not dentro_plano(w["geometry"][0]["lat"], w["geometry"][0]["lon"]):
            continue
        nid, d = nodo_mas_cercano_a_contorno(poly, principal)
        nombre = RENOMBRAR.get(nombre, nombre)
        if d > MAX_DIST_EDIFICIO:
            print(f"  (omitido: {nombre}, camino a {d:.0f} m)")
            continue
        destinos.append((nombre, nid, d))
    for slug, nombre, (px, py) in LUGARES_MANUALES:
        p = xy(*plano_a_latlng(px, py))
        nid = min(principal, key=lambda i: math.hypot(*(a - b for a, b in zip(xy(*coords[i]), p))))
        destinos.append((nombre, nid, math.hypot(*(a - b for a, b in zip(xy(*coords[nid]), p)))))

    # quitar duplicados por nombre (OSM repite algunos edificios grandes) y ordenar
    unicos = {}
    for nombre, nid, d in destinos:
        if nombre not in unicos or d < unicos[nombre][1]:
            unicos[nombre] = (nid, d)

    # ---- reducir a lo que sirve: nodos de la componente principal ----
    usados = sorted({i for ab in aristas for i in ab if i in principal})
    pos = {nid: k for k, nid in enumerate(usados)}
    out_aristas = [[pos[a], pos[b], t] for (a, b), t in aristas.items() if a in pos and b in pos]
    out_dest = []
    for nombre, (nid, d) in sorted(unicos.items()):
        slug = nombre.lower().replace("ñ", "n").replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u")
        slug = "-".join(filter(None, "".join(c if c.isalnum() else "-" for c in slug).split("-")))
        out_dest.append({"id": slug, "nombre": nombre, "nodo": pos[nid]})
        print(f"  {nombre:45s} nodo {pos[nid]:4d}  a {d:4.0f} m del contorno")

    datos = {
        "fuente": "© colaboradores de OpenStreetMap (ODbL)",
        "generado": datetime.date.today().isoformat(),
        "nodos": [[round(coords[i][0], 6), round(coords[i][1], 6)] for i in usados],
        "aristas": out_aristas,          # [a, b, tipo]  tipo: 0 camino, 1 escalera
        "destinos": out_dest,
    }
    esc = sum(1 for a in out_aristas if a[2] == 1)
    print(f"grafo: {len(usados)} nodos, {len(out_aristas)} aristas ({esc} de escaleras), {len(out_dest)} destinos")
    ruta = pathlib.Path(__file__).resolve().parent.parent / "js" / "generado" / "grafo.js"
    ruta.write_text(
        "// GENERADO por tools/generar-grafo.py desde OpenStreetMap. No editar a mano.\n"
        "const GRAFO = " + json.dumps(datos, ensure_ascii=False, separators=(",", ":")) + ";\n",
        encoding="utf-8")
    print("escrito", ruta, f"({ruta.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()

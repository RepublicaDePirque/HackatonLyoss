#!/usr/bin/env python3
"""Calca los contornos de edificios y patios desde plano.jpeg y genera contornos.js.

Cada edificio se aísla con una semilla (un píxel dentro del edificio, en píxeles del plano): se rellena
lo que encierran las líneas negras gruesas y se extrae el contorno. Los patios sin línea que los cierre
se trazan a mano (SPACE_POLYS). Todo queda en píxeles del plano; index.html lo pasa a metros con la
calibración del mapa (fromPlan), así que no depende de la georreferenciación de este script.

Uso:  python3 tools/contornos.py             (escribe contornos.js)
      python3 tools/contornos.py --preview   (solo tools/preview.png, para revisar)
"""
import sys, os, json
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
PLANO = os.path.join(ROOT, "plano.jpeg"); SALIDA = os.path.join(ROOT, "contornos.js")

# Semillas (x, y) en píxeles del plano: un punto dentro de cada edificio.
# Con 4 valores más se corta por filas (ymin, ymax) porque dos edificios comparten contorno.
SEEDS = {
  "A": (815, 690), "B": (825, 485), "C": (765, 390),
  "D": (962, 660, None, 707), "E": (962, 660, 707, None),   # D y E están dibujados como un solo contorno
  "F": (947, 777),                                           # F2 es parte de F
  "M": (363, 488), "M2": (412, 523), "R": (435, 317), "R2": (485, 360),
  "U": (737, 652), "P": (775, 250), "P2": (775, 170), "federacion": (735, 245),
  "H": (602, 750), "I": (767, 855), "J": (949, 330), "K": (970, 435), "O": (995, 550), "T": (1227, 825),
  "L": (619, 598),                                           # Tribuna: edificio fino junto a la cancha
  # «Edificio Bari» en el plano, al borde izquierdo. Se asume que es el «Edificio de Innovación Tecnológica» de OSM:
  # tiene la misma forma (franja larga con una muesca abajo) y queda en el mismo lugar, pero el polígono de OSM sale
  # corrido ~15 px porque la calibración se extrapola lejos del campus. Por eso se traza del plano. Por confirmar.
  "bari": (142, 620),
}
# Gimnasio 1: el tramo de A entre el cuerpo principal y B. Se recorta de B y se suma a A.
NECK = (793, 586, 846, 629)
# Espacios abiertos: semilla y, opcional, rectángulo (x1, y1, x2, y2) para no escapar por zonas abiertas.
SPACE_SEEDS = {
  "patio_central": ((870, 660), (845, 586, 915, 735)),
  "patio_biblioteca": ((762, 640), None),            # entre U y A
  "ceibos": ((1005, 775), (960, 738, 1055, 812)),
  "magnolios": ((690, 500), (655, 470, 722, 572)),
  "piscina": ((775, 515), (761, 502, 889, 564)),     # patio interior de B
}
# Espacios sin línea que los cierre: polígono trazado a mano (px del plano).
SPACE_POLYS = {
  "patio_canon": [(1060, 759), (1136, 759), (1136, 803), (1060, 803)],   # a la derecha de Ceibos
  "cancha_tenis": [(1060, 684), (1096, 666), (1131, 729), (1106, 743), (1094, 744)],
  "patio_calistenia": [(632, 552), (650, 548), (668, 556), (680, 572), (680, 700), (650, 703), (618, 700), (616, 676), (630, 672), (630, 570)],
  "cancha": [(450, 475), (602, 475), (602, 700), (450, 700)],            # cancha 11x11 (8007), no las gradas
}
# Edificios que el plano no dibuja como contorno propio (hoy solo Comedores): polígono de OpenStreetMap pasado a píxeles del plano
# con la calibración de index.html (0,4601 m/px, giro 155,3°, píxel 810,850 = -33.034358, -71.595779).
OSM_POLYS = {
  # «Edificio Comerdores» (sic) en OSM: la parte norte del bloque D, con una muesca. En el plano forma un solo cuadro
  # con D, así que se recorta al contorno de D (CLIP_A_D) para que calce con las líneas del plano.
  "comedores": [(1017, 631), (1024, 631), (1024, 610), (922, 608), (922, 624), (956, 624), (956, 636), (964, 636), (964, 653), (1000, 654), (1000, 631)],
}
CLIP_A_D = ["comedores"]
# Edificios que cuentan como uno solo al llegar (P2 es parte de P, R2 de R).
GROUPS = {"P": ["P", "P2"], "R": ["R", "R2"]}

# Destinos del mapa (grafo.js) -> área cuyo borde indica la brújula.
AREA_DE = {
  "acceso-av-espana": "I", "edificio-a": "A", "edificio-b": "B", "edificio-c": "C", "edificio-d": "D",
  "edificio-e": "E", "edificio-f": "F", "edificio-k-ciac": "K", "edificio-m": "M",
  "edificio-m2-gimnasio-2": "M2", "edificio-p": "P", "edificio-r": "R", "edificio-t": "T",
  "edificio-u-biblioteca": "U", "gimnasio-1": "gimnasio1", "museo-institucional-utfsm": "H",
  "patio-central": "patio_central",
  "edificio-l-tribuna": "L", "edificio-comedores": "comedores", "edificio-de-innovacion-tecnologica": "bari",
  "edificio-q-cafeteria-vivendum": "O",                      # OSM la llama «Q»; en el plano oficial es la «O»
}
# Destinos que el grafo no trae: nombre como lo conoce un mechón y el área donde están.
EXTRA = [
  ("casino", "Casino (Edificio D, piso 1)", "D"),
  ("arquitectura", "Arquitectura (Edificio D, pisos 2 y 3)", "D"),
  ("fisica", "Física (Edificio E)", "E"),
  ("informatica", "Informática, Matemática, Industrias y Comercial (Edificio F)", "F"),
  ("humanisticos", "Humanísticos (Edificio T)", "T"),
  ("admision", "Admisión (Patio central)", "patio_central"),
  ("federacion", "Federación", "federacion"),
  ("entrada-placeres", "Entrada Placeres", "J"),
  ("patio-biblioteca", "Patio de la biblioteca", "patio_biblioteca"),
  ("patio-ceibos", "Patio Ceibos", "ceibos"),
  ("patio-magnolios", "Patio de los Magnolios", "magnolios"),
  ("patio-canon", "Patio del Cañón", "patio_canon"),
  ("piscina", "Piscina (patio de B)", "piscina"),
  ("patio-calistenia", "Patio de calistenia", "patio_calistenia"),
  ("cancha-11x11", "Cancha 11x11", "cancha"),
  ("cancha-tenis", "Cancha de tenis", "cancha_tenis"),
]


def rdp(p, e):
    if len(p) < 3: return p
    a, b = np.array(p[0]), np.array(p[-1]); d = b - a; L = np.hypot(*d)
    cruz = lambda u, v: u[0] * v[1] - u[1] * v[0]               # np.cross ya no acepta vectores 2D (numpy 2)
    ds = [abs(cruz(d, np.array(q) - a)) / L if L else np.hypot(*(np.array(q) - a)) for q in p[1:-1]]
    i = int(np.argmax(ds)) + 1
    if ds[i - 1] > e: return rdp(p[:i + 1], e)[:-1] + rdp(p[i:], e)
    return [p[0], p[-1]]


def contorno(lab, seed, h, w, clip=None, add=None, sub=None):
    m = lab == lab[seed[1], seed[0]]
    if clip:
        cm = np.zeros_like(m); cm[clip[1]:clip[3], clip[0]:clip[2]] = True; m = m & cm
    if len(seed) > 2:                                           # corte por filas
        ymin, ymax = seed[2], seed[3]; rows = np.arange(h)[:, None]
        if ymin is not None: m = m & (rows >= ymin)
        if ymax is not None: m = m & (rows < ymax)
    if add is not None: m = m | add
    if sub is not None: m = m & ~sub
    area = int(m.sum())
    if area > 40000 or area < 30: return None, area            # fuga o semilla en una línea
    m = ndi.binary_fill_holes(ndi.binary_closing(m, iterations=2))
    m = ndi.binary_dilation(m, iterations=2)                    # hasta el centro de la línea negra
    return trazar(m), area


def trazar(m):                                                  # contorno exterior de una máscara, simplificado
    ys, xs = np.where(m); x0, y0 = max(xs.min() - 3, 0), max(ys.min() - 3, 0)
    sub_ = np.pad(m[y0:ys.max() + 4, x0:xs.max() + 4].astype(float), 1)
    segs = max(plt.contour(sub_, [0.5]).allsegs[0], key=len)
    pts = [(x - 1 + x0, y - 1 + y0) for x, y in segs]
    return rdp(pts, 0.8)[:-1]


def mascara(poly, h, w):                                        # polígono (px del plano) -> máscara booleana
    im = Image.new("L", (w, h), 0); ImageDraw.Draw(im).polygon([tuple(p) for p in poly], fill=1)
    return np.array(im).astype(bool)


def main():
    gray = np.array(Image.open(PLANO).convert("L")).astype(int); h, w = gray.shape
    bar = ndi.binary_dilation(gray <= 115, iterations=1)
    lab, _ = ndi.label(~bar)
    neck = np.zeros_like(lab, bool); neck[NECK[1]:NECK[3], NECK[0]:NECK[2]] = True
    neck &= lab == lab[485, 825]
    edificios, espacios = {}, {}
    for k, s in {**SEEDS, "gimnasio1": (825, 485)}.items():
        poly, area = contorno(lab, s, h, w, clip=NECK if k == "gimnasio1" else None,
                              add=neck if k == "A" else None, sub=neck if k == "B" else None)
        print(f"{k:11s} área={area:6d} px  ", f"{len(poly)} vértices" if poly else "DESCARTADO (fuga o semilla mala)")
        if poly: edificios[k] = poly
    for k, poly in OSM_POLYS.items():
        if k in CLIP_A_D and "D" in edificios:                  # recorta al cuadro negro de D
            m = mascara(poly, h, w) & mascara(edificios["D"], h, w)
            poly = trazar(m); print(f"{k:11s} recortado al contorno de D: {int(m.sum()):6d} px   {len(poly)} vértices")
        else:
            print(f"{k:11s} de OpenStreetMap:           {len(poly)} vértices")
        edificios[k] = poly
    for k, (s, clip) in SPACE_SEEDS.items():
        poly, area = contorno(lab, s, h, w, clip)
        print(f"{k:16s} área={area:6d} px  ", f"{len(poly)} vértices" if poly else "DESCARTADO")
        if poly: espacios[k] = poly
    espacios.update(SPACE_POLYS)
    img = Image.open(PLANO).convert("RGB"); d = ImageDraw.Draw(img)
    for p in edificios.values(): d.line(p + [p[0]], fill=(255, 0, 0), width=2)
    for p in espacios.values(): d.line(list(p) + [p[0]], fill=(0, 160, 0), width=2)
    img.save(os.path.join(HERE, "preview.png"))
    if "--preview" in sys.argv: return
    fmt = lambda poly: [[round(float(x), 1), round(float(y), 1)] for x, y in poly]
    datos = {"edificios": {k: fmt(p) for k, p in edificios.items()}, "espacios": {k: fmt(p) for k, p in espacios.items()},
             "grupos": GROUPS, "areaDe": AREA_DE, "extra": [{"id": i, "nombre": n, "area": a} for i, n, a in EXTRA]}
    with open(SALIDA, "w") as f:
        f.write("// GENERADO por tools/contornos.py desde plano.jpeg (coordenadas = píxeles del plano). No editar a mano.\n")
        f.write("const CONTORNOS = " + json.dumps(datos, ensure_ascii=False, separators=(",", ":")) + ";\n")
    print("escrito", SALIDA)

main()

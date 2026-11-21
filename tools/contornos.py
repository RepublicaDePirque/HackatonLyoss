#!/usr/bin/env python3
"""Calca los contornos de los edificios desde plano.jpeg y actualiza BUILDINGS en index.html.

Cada edificio se aísla con una semilla (un píxel dentro del edificio, en coordenadas del plano):
se rellena lo que encierran las líneas negras gruesas y se extrae el contorno.
Uso:  python3 tools/contornos.py            (actualiza index.html)
      python3 tools/contornos.py --preview  (solo genera tools/preview.png)
Georreferencia: transformación de semejanza con 3 puntos reales (ver REF).
"""
import sys, re, math, os
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as ndi
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
PLANO = os.path.join(ROOT, "plano.jpeg"); HTML = os.path.join(ROOT, "index.html")

# Semillas (x, y) en píxeles del plano: un punto dentro de cada edificio.
SEEDS = {
  "A": (815, 690), "B": (825, 485), "C": (765, 390),
  # D y E (y F y F2) están dibujados como un solo contorno: se separan cortando por fila (ymin, ymax).
  "D": (962, 660, None, 707), "E": (962, 660, 707, None),
  "F": (947, 777),   # F2 es parte de F
  "M": (363, 488), "M2": (412, 523), "R": (435, 317),
  "R2": (485, 360), "U": (737, 652), "P": (775, 250), "federacion": (735, 245), "P2": (775, 170), "H": (602, 750),
  "I": (767, 855), "J": (949, 330), "K": (970, 435), "O": (995, 550), "T": (1227, 825),
}
# Gimnasio 1: el tramo de A entre el cuerpo principal y B. Se recorta de B y se suma a A.
NECK = (793, 586, 846, 629)
# Espacios abiertos (patios): semilla y, opcional, rectángulo (x1, y1, x2, y2) para no escapar por zonas abiertas.
SPACE_SEEDS = {
  "patio_central": ((870, 660), (845, 586, 915, 735)),
  "ceibos": ((1005, 775), (960, 738, 1055, 812)),
  "magnolios": ((690, 500), (655, 470, 722, 572)),
  "piscina": ((775, 515), (761, 502, 889, 564)),
}
# Espacios sin línea negra que los cierre: polígono trazado a mano (px del plano).
SPACE_POLYS = {
  "patio_canon": [(1060, 759), (1136, 759), (1136, 803), (1060, 803)],   # a la derecha de Ceibos
  "patio_calistenia": [(632, 552), (650, 548), (668, 556), (680, 572), (680, 700), (650, 703), (618, 700), (616, 676), (630, 672), (630, 570)],
}
# Puntos de referencia reales: (px, py) del plano -> (lat, lng)
lat0, lng0 = -33.034172, -71.595702
REF = [((949, 330), (-33.036665, -71.595144)), ((775, 855), (lat0, lng0)), ((340, 455), (-33.034867, -71.592865))]

def enu(lat, lng): return ((lng - lng0) * 111320 * math.cos(math.radians(lat0)), (lat - lat0) * 111320)
P = np.array([[p[0], -p[1]] for p, _ in REF], float); E = np.array([enu(*g) for _, g in REF], float)
pc, ec = P.mean(0), E.mean(0); A_ = P - pc; B_ = E - ec
a = (A_[:, 0] * B_[:, 0] + A_[:, 1] * B_[:, 1]).sum(); b = (A_[:, 0] * B_[:, 1] - A_[:, 1] * B_[:, 0]).sum()
SC = math.hypot(a, b) / (A_ ** 2).sum(); TH = math.atan2(b, a)
R = np.array([[math.cos(TH), -math.sin(TH)], [math.sin(TH), math.cos(TH)]])
tr = lambda u, v: tuple(((np.array([u, -v], float) - pc) @ R.T) * SC + ec)

def rdp(p, e):
    if len(p) < 3: return p
    a, b = np.array(p[0]), np.array(p[-1]); d = b - a; L = np.hypot(*d)
    ds = [abs(np.cross(d, np.array(q) - a)) / L if L else np.hypot(*(np.array(q) - a)) for q in p[1:-1]]
    i = int(np.argmax(ds)) + 1
    if ds[i - 1] > e: return rdp(p[:i + 1], e)[:-1] + rdp(p[i:], e)
    return [p[0], p[-1]]

def contorno(lab, seed, h, w, clip=None, add=None, sub=None):
    m = lab == lab[seed[1], seed[0]]
    if len(seed) > 4:                                            # corte por columnas (xmin, xmax)
        cols = np.arange(w)[None, :]
        if seed[4] is not None: m = m & (cols >= seed[4])
        if seed[5] is not None: m = m & (cols < seed[5])
    if clip:
        cm = np.zeros_like(m); cm[clip[1]:clip[3], clip[0]:clip[2]] = True; m = m & cm
    if len(seed) > 2:                                            # corte por filas
        ymin, ymax = seed[2], seed[3]; rows = np.arange(h)[:, None]
        if ymin is not None: m = m & (rows >= ymin)
        if ymax is not None: m = m & (rows < ymax)
    if add is not None: m = m | add
    if sub is not None: m = m & ~sub
    area = int(m.sum())
    if area > 40000 or area < 30: return None, area            # fuga o semilla en una línea
    m = ndi.binary_fill_holes(ndi.binary_closing(m, iterations=2))
    m = ndi.binary_dilation(m, iterations=2)                    # hasta el centro de la línea negra
    ys, xs = np.where(m); x0, y0 = max(xs.min() - 3, 0), max(ys.min() - 3, 0)
    sub = np.pad(m[y0:ys.max() + 4, x0:xs.max() + 4].astype(float), 1)
    segs = max(plt.contour(sub, [0.5]).allsegs[0], key=len)
    pts = [(x - 1 + x0, y - 1 + y0) for x, y in segs]
    return rdp(pts, 0.8)[:-1], area

def main():
    gray = np.array(Image.open(PLANO).convert("L")).astype(int); h, w = gray.shape
    bar = ndi.binary_dilation(gray <= 115, iterations=1)
    lab, _ = ndi.label(~bar)
    polys = {}
    neck = np.zeros_like(lab, bool); neck[NECK[1]:NECK[3], NECK[0]:NECK[2]] = True
    neck &= lab == lab[485, 825]
    SEEDS["gimnasio1"] = (825, 485)
    for k, s in SEEDS.items():
        poly, area = contorno(lab, s, h, w, clip=NECK if k == "gimnasio1" else None,
                              add=neck if k == "A" else None, sub=neck if k == "B" else None)
        print(f"{k:4s} área={area:6d} px  ", f"{len(poly)} vértices" if poly else "DESCARTADO (fuga o semilla mala)")
        if poly: polys[k] = poly
    spaces = {}
    for k, (s, clip) in SPACE_SEEDS.items():
        poly, area = contorno(lab, s, h, w, clip)
        print(f"{k:14s} área={area:6d} px  ", f"{len(poly)} vértices" if poly else "DESCARTADO")
        if poly: spaces[k] = poly
    for k, poly in SPACE_POLYS.items(): spaces[k] = poly
    img = Image.open(PLANO).convert("RGB"); d = ImageDraw.Draw(img)
    for k, p in polys.items(): d.line(p + [p[0]], fill=(255, 0, 0), width=2)
    for k, p in spaces.items(): d.line(p + [p[0]], fill=(0, 160, 0), width=2)
    img.save(os.path.join(HERE, "preview.png"))
    if "--preview" in sys.argv: return
    html = open(HTML).read()
    keep = re.search(r"  cancha: \[.*?\],\n", html).group(0)       # la cancha no es un edificio: se mantiene
    block = "const BUILDINGS = {\n" + "".join(
        f"  {k}: [" + ",".join("[%.1f,%.1f]" % tr(x, y) for x, y in p) + "],\n" for k, p in polys.items()) + keep + "};"
    block += "\nconst SPACES = {\n" + "".join(
        f"  {k}: [" + ",".join("[%.1f,%.1f]" % tr(x, y) for x, y in p) + "],\n" for k, p in spaces.items()) + "};"
    html, c = re.subn(r"const BUILDINGS = \{.*?\n\};(\nconst SPACES = \{.*?\n\};)?", lambda m: block, html, flags=re.S)
    # Las puertas (destinos de edificio) se ajustan al punto más cercano del nuevo borde.
    dest = dict(re.findall(r'(\w+):"(\w+)"', re.search(r"const DEST_BLD = \{(.*?)\};", html).group(1)))
    for nid, bk in dest.items():
        if nid in ("r_port", "cancha") or bk not in polys: continue
        m_ = re.search(r'N\("%s","([^"]*)",\s*([-\d.]+),\s*([-\d.]+)\)' % nid, html)
        px, py = float(m_.group(2)), float(m_.group(3)); q = [tr(x, y) for x, y in polys[bk]]; best = None
        for i in range(len(q)):
            (x1, y1), (x2, y2) = q[i], q[(i + 1) % len(q)]; dx, dy = x2 - x1, y2 - y1; L2 = dx * dx + dy * dy
            tt = max(0, min(1, ((px - x1) * dx + (py - y1) * dy) / L2)) if L2 else 0
            cx, cy = x1 + tt * dx, y1 + tt * dy; dd = math.hypot(px - cx, py - cy)
            if not best or dd < best[0]: best = (dd, cx, cy)
        if best[0] < 25:
            html = html.replace(m_.group(0), 'N("%s","%s",%8.1f,%8.1f)' % (nid, m_.group(1), best[1], best[2]))
            print(f"puerta {nid}: movida {best[0]:.1f} m al borde de {bk}")
    open(HTML, "w").write(html); print("BUILDINGS actualizado:", c)

main()

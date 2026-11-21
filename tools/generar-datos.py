#!/usr/bin/env python3
"""Genera js/generado/datos.js (textos de la interfaz por destino) desde data/edificios.json.

Uso:  python3 tools/generar-datos.py

- Une cada destino de la app (ids de grafo.js y contornos.js) con su letra, detalle, pista y foto.
- Las pistas están marcadas «borrador» en data/edificios.json: redactadas desde el plano, validar en terreno.
- Los datos curiosos (ZONAS y SABIAS) vienen de las plantillas del diseño (design/plantillas/): son de
  EJEMPLO y no están verificados. Hay que reemplazarlos por datos recolectados (ver docs/pendientes-datos.md).
"""
import json, pathlib

RAIZ = pathlib.Path(__file__).resolve().parent.parent
edif = {e["id"]: e for e in json.load(open(RAIZ / "data/edificios.json", encoding="utf-8"))["edificios"]}

# id del destino en la app -> (nombre en la lista, letra de la insignia, detalle, id en edificios.json para pista/foto)
# Los textos salen de los nombres de OpenStreetMap, de data/edificios.json y de las plantillas del diseño.
DESTINOS = {
    "acceso-av-espana":                    ("Acceso Av. España", "", "Entrada desde Av. España", None),
    "entrada-placeres":                    ("Entrada Av. Los Placeres", "", "Acceso por Av. Los Placeres", None),
    "edificio-a":                          ("Edificio A", "A", "La torre, sobre Av. España", "a"),
    "edificio-b":                          ("Edificio B", "B", "Rodea el patio de la piscina", "b"),
    "edificio-c":                          ("Edificio C", "C", "Salas de clases", "c"),
    "edificio-d":                          ("Edificio D", "D", "Casino y Arquitectura", "d"),
    "edificio-comedores":                  ("Comedores", "D", "Casino, piso 1 del Edificio D", "comedores"),
    "edificio-e":                          ("Edificio E", "E", "Física", "e"),
    "edificio-f":                          ("Edificio F", "F", "Informática, Matemática, Industrias y Comercial", "f"),
    "edificio-k-ciac":                     ("Edificio K", "K", "CIAC", "k"),
    "edificio-l-tribuna":                  ("Tribuna", "L", "Edificio L", "l"),
    "edificio-m":                          ("Edificio M", "M", "Salas de clases", "m"),
    "edificio-m2-gimnasio-2":              ("Gimnasio 2", "M2", "Edificio M2", "m2"),
    "edificio-p":                          ("Edificio P", "P", "Salas de clases", "p"),
    "edificio-q-cafeteria-vivendum":       ("Cafetería Vivendum", "Q", "Edificio Q", "vivendum"),
    "edificio-r":                          ("Edificio R", "R", "Portería Diego Portales", "r"),
    "edificio-t":                          ("Edificio T", "T", "Humanísticos", "t"),
    "edificio-u-biblioteca":               ("Biblioteca", "U", "Edificio U", "u"),
    "edificio-de-innovacion-tecnologica":  ("Innovación Tecnológica", "", "Edificio de Innovación Tecnológica", None),
    "gimnasio-1":                          ("Gimnasio 1", "", "Dentro del Edificio A", None),
    "museo-institucional-utfsm":           ("Museo Institucional", "H", "Edificio H", None),
    "patio-central":                       ("Patio Central", "", "Entre los edificios A, B y D", None),
    "casino":                              ("Casino", "D", "Edificio D, piso 1", "comedores"),
    "arquitectura":                        ("Arquitectura", "D", "Edificio D, pisos 2 y 3", "d"),
    "fisica":                              ("Física", "E", "Edificio E", "e"),
    "informatica":                         ("Informática, Matemática, Industrias y Comercial", "F", "Edificio F", "f"),
    "humanisticos":                        ("Humanísticos", "T", "Edificio T", "t"),
    "admision":                            ("Admisión", "", "Patio central", None),
    "federacion":                          ("Federación", "Fe", "En pasaje Valdés, frente a la portería del M", "federacion"),
    "patio-biblioteca":                    ("Patio de la biblioteca", "", "Junto al Edificio U", None),
    "patio-ceibos":                        ("Patio Ceibos", "", "Patio", None),
    "patio-magnolios":                     ("Patio de los Magnolios", "", "Patio", None),
    "patio-canon":                         ("Patio del Cañón", "", "A la derecha de Ceibos", None),
    "piscina":                             ("Piscina", "", "En el patio del Edificio B", None),
    "patio-calistenia":                    ("Patio de calistenia", "", "Patio", None),
    "cancha-11x11":                        ("Cancha 11x11", "", "Cancha", None),
    "cancha-tenis":                        ("Cancha de tenis", "", "Cancha", None),
}

# Fotos con licencia libre ya descargadas en assets/img/ (autor y licencia vienen de data/edificios.json).
PIES = {"a": "Fachada hacia Av. España, con su torre.", "f": "Vista desde la ciclovía, al otro lado de Av. España.",
        "b": "Fachada hacia la piscina."}

info = {}
for did, (nombre, letra, detalle, eid) in DESTINOS.items():
    e = edif.get(eid) if eid else None
    d = {"nombre": nombre, "letra": letra, "detalle": detalle}
    if e and e.get("pista"):
        d["pista"] = e["pista"]
    if e and e.get("foto") and (RAIZ / f"assets/img/edificio-{eid}.jpg").exists():
        f = e["foto"]
        d["foto"] = {"src": f"assets/img/edificio-{eid}.jpg", "autor": f["autor"], "licencia": f["licencia"],
                     "pie": PIES.get(eid, ""), "pagina": f["pagina"]}
    info[did] = d

# ⚠ DATOS DE EJEMPLO tomados de las plantillas del diseño. Sin verificar: reemplazar por datos reales.
zonas = [
    {"id": "hall-de-montaje", "area": "C", "radio": 30, "ejemplo": True,
     "titulo": "Pasas junto al Edificio C", "gancho": "Era el hall de montaje",
     "texto": "Aquí se armaban los aparatos que estudiaban los de Mecánica.",
     "etiqueta": "Edificio C · Salas de clases",
     "mas": ["Antes de tener salas de clases, el Edificio C fue el hall de montaje de la universidad: ahí se armaban los aparatos que estudiaban los alumnos de Mecánica.",
             "Es el edificio más largo del campus y corre paralelo a Av. Los Placeres."]},
]
sabias = {
    "edificio-a": "Su reloj funciona con un sistema eléctrico suizo, anterior a los relojes de cuarzo.",
    "edificio-c": "Fue el hall de montaje: aquí se armaban los aparatos que estudiaban los de Mecánica.",
}

salida = ("// GENERADO por tools/generar-datos.py desde data/edificios.json. No editar a mano.\n"
          "// ZONAS y SABIAS son datos de EJEMPLO del diseño, sin verificar.\n"
          f"const INFO = {json.dumps(info, ensure_ascii=False, separators=(',', ':'))};\n"
          f"const ZONAS = {json.dumps(zonas, ensure_ascii=False, separators=(',', ':'))};\n"
          f"const SABIAS = {json.dumps(sabias, ensure_ascii=False, separators=(',', ':'))};\n")
(RAIZ / "js/generado/datos.js").write_text(salida, encoding="utf-8")
print(f"js/generado/datos.js: {len(info)} destinos, {sum(1 for d in info.values() if 'foto' in d)} con foto, "
      f"{sum(1 for d in info.values() if 'pista' in d)} con pista, {len(zonas)} zona(s) de datos")

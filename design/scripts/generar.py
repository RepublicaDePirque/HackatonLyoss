import json, sys, pathlib
# Uso: python3 design/scripts/generar.py design <canvas.json publicado> [carpeta de salida]
# El canvas.json publicado se lee para conservar los tableros de otras personas (p. ej. DatosMapa).
base = pathlib.Path(sys.argv[1])
tpl = base / 'plantillas'
out = pathlib.Path(sys.argv[3]) if len(sys.argv) > 3 else base / 'lienzo'
vivo = json.loads(pathlib.Path(sys.argv[2]).read_text())

TEMA = {"editor": "enum", "options": ["oscuro", "claro"], "section": "Aspecto"}
BRUJ = {
	"rumbo": {"editor": "range", "min": 0, "max": 359, "step": 1, "unit": "°", "section": "Señal"},
	"metros": {"editor": "range", "min": 0, "max": 250, "step": 5, "unit": " m", "section": "Señal"},
	"senal": {"editor": "enum", "options": ["resplandor", "flecha", "mapa"], "section": "Señal"},
	"tendencia": {"editor": "enum", "options": ["acerca", "aleja"], "section": "Señal"},
	"gps": {"editor": "enum", "options": ["bueno", "impreciso", "sin"], "section": "Ubicación"},
	"tema": TEMA,
	"dato": {"editor": "boolean", "section": "Aspecto"},
}
BUSC = {"tema": TEMA, "consulta": {"editor": "enum", "options": ["ninguna", "gimnasio", "edificio"], "section": "Estado"}}
LLEG = {"destino": {"editor": "enum", "options": ["A", "C"], "section": "Estado"}, "estado": {"editor": "enum", "options": ["inicio", "vista", "gracias"], "section": "Estado"}}
SOLO_TEMA = {"tema": TEMA}

b = lambda **k: {"rumbo": 32, "metros": 205, "senal": "resplandor", "tendencia": "acerca", "gps": "bueno", "tema": "oscuro", "dato": False, **k}

# (archivo, plantilla, esquema, defaults, titulo de la pagina, titulo del tablero, fila)
V = [
	("Permiso", "Permiso", SOLO_TEMA, {"tema": "oscuro"}, "Antes de empezar", "1 · Antes de empezar", 0),
	("Buscar", "Buscar", BUSC, {"tema": "oscuro", "consulta": "ninguna"}, "Elegir destino", "2 · Elegir destino", 0),
	("Main", "Brujula", BRUJ, b(), "Brújula de resplandor", "3 · Brújula: resplandor, en la entrada", 0),
	("Dato", "Brujula", BRUJ, b(rumbo=330, metros=125, tema="claro", dato=True), "Dato curioso al pasar", "4 · Dato al pasar por el C (claro)", 0),
	("Cerca", "Brujula", BRUJ, b(rumbo=350, metros=50), "Casi llegas", "5 · Casi llegas: foto de la entrada", 0),
	("Llegada", "Llegada", LLEG, {"destino": "A", "estado": "inicio"}, "Llegada", "6 · Llegada y foto", 0),
	("Mapa", "Brujula", BRUJ, b(senal="mapa", metros=125, rumbo=20), "Modo mapa", "7 · Modo mapa: te ubica, sin ruta", 0),
	("Demo", "Demo", SOLO_TEMA, {"tema": "oscuro"}, "Flujo animado", "8 · Flujo animado (30 s)", 0),
	("Flecha", "Brujula", BRUJ, b(senal="flecha", metros=125, rumbo=40), "Señal de flecha", "Señal alternativa: flecha", 1),
	("Detras", "Brujula", BRUJ, b(rumbo=180, metros=150), "Destino detrás", "Destino detrás de ti", 1),
	("Aleja", "Brujula", BRUJ, b(rumbo=110, metros=170, tendencia="aleja", tema="claro"), "Te estás alejando", "Te estás alejando (claro)", 1),
	("Impreciso", "Brujula", BRUJ, b(rumbo=20, metros=140, gps="impreciso"), "GPS impreciso", "GPS impreciso: luz más ancha", 1),
	("SinGps", "Brujula", BRUJ, b(gps="sin"), "Sin ubicación", "Sin ubicación", 1),
	("MapaClaro", "Brujula", BRUJ, b(senal="mapa", metros=125, rumbo=20, tema="claro"), "Modo mapa claro", "Modo mapa, tema claro", 1),
	("BuscarVacio", "Buscar", BUSC, {"tema": "oscuro", "consulta": "gimnasio"}, "Búsqueda sin resultados", "Búsqueda sin resultados", 1),
	("LlegadaSinFoto", "Llegada", LLEG, {"destino": "C", "estado": "inicio"}, "Llegada sin fotos", "Llegada sin fotos todavía", 1),
]

boards, orden = {}, []
cols = [0, 0]
FILA_Y = [0, 2304]
for nombre, plantilla, esquema, defaults, titulo, tablero, fila in V:
	props = {k: {**v, "default": defaults[k]} for k, v in esquema.items()}
	props["$preview"] = {"width": 390, "height": 844}
	html = (tpl / f"{plantilla}.tpl.html").read_text()
	html = html.replace("__TITULO__", titulo).replace("__PROPS__", json.dumps(props, ensure_ascii=False)).replace("__DEFAULTS__", json.dumps(defaults, ensure_ascii=False))
	assert "__" not in html.replace("__proto__", ""), nombre
	assert "'" not in json.dumps(props, ensure_ascii=False)
	(out / f"{nombre}.dc.html").write_text(html)
	f = f"{nombre}.dc.html"
	boards[f] = {"x": cols[fila] * 470, "y": FILA_Y[fila], "w": 390, "h": 844, "title": tablero, "is_interactive": True}
	cols[fila] += 1
	orden.append(f)

# conservar tableros ajenos (lyoss-2)
for f, v in vivo["boards"].items():
	if f not in boards:
		boards[f] = v
		orden.insert(8, f) if fila == 1 else orden.append(f)
dm = boards.get("DatosMapa.dc.html")
if dm and dm["title"].startswith("7 · "):
	dm["title"] = dm["title"][4:]

canvas = {**vivo, "boards": boards, "order": orden}
canvas["notes"] = {
	**vivo.get("notes", {}),
	"titulo": {"x": 0, "y": -300, "text": "Flujo principal: de elegir destino a dejar una foto", "kind": "title1", "maxW": 8 * 470 - 80},
	"estados": {"x": 0, "y": 2054, "text": "Estados: cuando algo no sale perfecto", "kind": "title1", "maxW": 8 * 470 - 80},
}
(out / "canvas.json").write_text(json.dumps(canvas, ensure_ascii=False))
print(json.dumps(orden, ensure_ascii=False))
print(sorted(p.name for p in out.iterdir()))

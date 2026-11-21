# Rasteriza data/mapa-casa-central.svg en tema claro y oscuro para el lienzo.
# rsvg-convert no entiende var(): se sustituyen las variables de cada tema y se quita el @media.
# Uso: python3 design/scripts/rasterizar.py data/mapa-casa-central.svg <carpeta de salida>
import re, sys, subprocess, pathlib
src = pathlib.Path(sys.argv[1]).read_text()
out = pathlib.Path(sys.argv[2]); out.mkdir(parents=True, exist_ok=True)
for tema in ('claro', 'oscuro'):
	bloque = re.search(r'\.mapa\.' + tema + r'\{([^}]*)\}', src).group(1)
	vars_ = dict(re.findall(r'--([\w-]+):([^;}]+)', bloque))
	svg = re.sub(r'\s*@media[^{]*\{\.mapa\{[^}]*\}\}', '', src)
	svg = re.sub(r'var\(--([\w-]+)\)', lambda m: vars_[m.group(1)], svg)
	(out / f'mapa-{tema}.svg').write_text(svg)
	subprocess.run(['rsvg-convert', '-w', '2000', '-o', str(out / f'mapa-{tema}.png'), str(out / f'mapa-{tema}.svg')], check=True)
	print(tema, (out / f'mapa-{tema}.png').stat().st_size)

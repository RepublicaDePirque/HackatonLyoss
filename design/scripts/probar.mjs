import fs from 'fs';
const dir = process.argv[2];
for (const f of fs.readdirSync(dir).filter(f => f.endsWith('.dc.html'))) {
	const html = fs.readFileSync(`${dir}/${f}`, 'utf8');
	const m = html.match(/<script type="text\/x-dc"[^>]*>([\s\S]*?)<\/script>/);
	const props = JSON.parse(html.match(/data-props='([^']*)'/)[1]);
	const src = `class DCLogic { setState(s){ this.state = {...(this.state||{}), ...s}; } }\nglobal.window = { matchMedia: () => ({ matches: false }) };\n${m[1]}\nreturn Component;`;
	const Component = new Function(src)();
	const c = new Component(); c.props = {}; c.state = { t: 14 };
	const vals = c.renderVals();
	const holes = [...html.matchAll(/\{\{([\w.]+)\}\}/g)].map(x => x[1]).filter(h => !h.includes('.') && !['true','false'].includes(h));
	const faltan = [...new Set(holes)].filter(h => !(h in vals));
	console.log(f, faltan.length ? 'FALTAN ' + faltan.join(',') : 'ok', Object.keys(props).length);
}

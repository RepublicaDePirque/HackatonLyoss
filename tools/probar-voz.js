// Pruebas de las frases del modo voz: node tools/probar-voz.js
const assert = require("assert");
const { horaReloj, fraseHora, ladoDe, fraseDonde } = require("../voz.js");
const horas = [[0, 12], [14, 12], [16, 1], [44, 1], [46, 2], [90, 3], [180, 6], [271, 9], [345, 12], [359, 12], [-90, 9], [720, 12]];
for (const [rel, h] of horas) assert.strictEqual(horaReloj(rel), h, `horaReloj(${rel})`);
assert.strictEqual(fraseHora(30), "a la 1");
assert.strictEqual(fraseHora(60), "a las 2");
const lados = [[0, "adelante"], [30, "adelante"], [44, "a tu derecha"], [90, "a tu derecha"], [180, "detrás de ti"], [271, "a tu izquierda"], [359, "adelante"]];
for (const [rel, l] of lados) assert.strictEqual(ladoDe(rel), l, `ladoDe(${rel})`);
assert.strictEqual(fraseDonde("Edificio A", 60, 120), "Edificio A, a las 2, 120 metros");
console.log("ok:", horas.length + lados.length + 3, "comprobaciones");

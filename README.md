# Brújula USM

Prototipo para la Hackathon LYOSS USM 2026, desafío «Campus sin barreras». Una brújula para orientarse en Casa Central (Valparaíso): eliges un destino y el borde de la pantalla brilla hacia él, con la distancia. No te damos una ruta; descubres el campus en el camino.

- Producto y decisiones de diseño: [`docs/PRD.md`](docs/PRD.md)
- Cómo está construida y cómo probarla: [`docs/implementacion.md`](docs/implementacion.md)
- Datos que faltan: [`docs/pendientes-datos.md`](docs/pendientes-datos.md)

## Probarla

No tiene dependencias ni paso de compilación.

```
python3 -m http.server 8000
```

Abre `http://localhost:8000/?debug` (mover la posición sin GPS) o `http://localhost:8000/?demo` (recorrido de ejemplo). Agrega `&voz` para el modo voz, que dice en voz alta la dirección y la distancia (`node tools/probar-voz.js` prueba sus frases). El GPS y la brújula reales solo funcionan por HTTPS, por ejemplo publicada en GitHub Pages.

Datos de mapa y caminos © colaboradores de OpenStreetMap (ODbL).

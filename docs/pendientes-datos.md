# Pendientes de datos del campus

Lista única de lo que falta recolectar para Casa Central. Quien consiga un dato lo anota aquí con su fuente y avisa para integrarlo en `data/`.

Última actualización: 21 de noviembre de 2026.

## Cómo entregar un dato

- Coordenadas en grados decimales, latitud y longitud (ejemplo: `-33.034172, -71.595702`). En Google Maps: clic derecho sobre el lugar y se copian.
- Indicar la fuente: «GPS en terreno», «Google Maps a mano» u otra.
- Fotos: propias del equipo, con el nombre de quien la sacó. No usar fotos de usm.cl ni de Google.

## 1. Lugares que el equipo está recolectando (Google Maps y terreno)

No se extrajeron datos de Google Maps de forma automática: su API es de pago y sus términos no permiten copiarlos en bloque. Se cargan a mano.

| Lugar | Estado | Nota |
|---|---|---|
| Cajero BancoEstado | Pendiente | OpenStreetMap tiene un cajero sin banco indicado en Av. Los Placeres (`-33.036625, -71.595195`). Confirmar si es este. |
| Testamento de Federico Santa María (entrada) | Pendiente | No figura en OpenStreetMap. |
| Memorial del reloj de sol | Pendiente | No figura en OpenStreetMap. |
| Otros servicios que solo aparezcan en Google Maps | Pendiente | Agregar filas a esta tabla. |

## 2. Fotos de fachada

Con foto de licencia libre (Wikimedia Commons): A, F y B. En A y B la letra se dedujo por la ubicación; confirmar que la foto corresponde.

Pendientes de sacar en terreno, destinos de la demo primero:

| Edificio | Estado |
|---|---|
| C | Pendiente |
| M | Pendiente |
| P | Pendiente |
| Biblioteca (U) | Pendiente |
| Comedores / Casino (D) | Pendiente |
| Federación de Estudiantes | Pendiente |
| D, E, K, M2, R, T, Tribuna (L), Cafetería Vivendum | Pendiente, fuera de la demo |

## 3. Por validar en terreno

- **Pistas**: las de `data/edificios.json` son borradores escritos mirando el plano. Revisar que describan lo que se ve al caminar.
- **Qué hay en cada edificio** (`que_hay`): viene de la rama `wip/brujula`, sin verificar.
- **Punto del edificio P**: es el centro de P y P2 juntos; queda unos 20 m corrido hacia el P2. Tomar el punto de la entrada.
- **Puertas**: todas las coordenadas marcan el centro del edificio, no la puerta. Tomar la puerta de los ocho destinos de la demo. En curso: Agustín las marca en terreno con `marcar-entradas.html`, que exporta un `entradas.json`.
- **Puntos de interés de OpenStreetMap** (32): no se comprobó que sigan existiendo.
- **Precisión real**: el ajuste entre plano y OpenStreetMap da 1 a 2 m, pero no se midió contra el GPS de un teléfono en el campus.

## 4. Sin recolectar

- **Datos curiosos por zona**: no hay ninguno con zona definida. Candidato con fuente: el Obelisco a Diego Portales (Av. Los Placeres, junto al R), que según OpenStreetMap encargó Nicanor Parra; verificar la historia antes de usarla.
- **Zonas** (polígonos o radios) donde se dispara cada dato curioso.

## 5. Coordinación con el resto del repo

- Las ramas `map` y `wip/brujula` usan otra calibración del plano (norte arriba y 0,5 m por píxel; o tres puntos con 10 a 30 m de desfase). La referencia vigente es `data/georef.json`: arriba del plano = rumbo 154,8°, 0,4666 m por píxel.

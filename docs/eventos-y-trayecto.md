# Eventos, llegada según el lado y tarjetas del trayecto

Diseño acordado con el usuario el 21 de noviembre de 2026 (rama `diseno/eventos-y-trayecto`). Complementa `docs/PRD.md`.

## Decisiones

| Tema | Decisión |
|---|---|
| Alcance | Se implementa hoy, para la demo. |
| Eventos | Curados por el equipo en `data/eventos.json`. No hay publicación desde la app (trabajo futuro). |
| Dónde se ven | En «¿A dónde vas?», junto a los lugares: «Está pasando» arriba y «Próximos eventos» más abajo. Elegir un evento lleva la brújula a su lugar. |
| Llegada según el lado | La foto que se muestra es la del lado del edificio por el que llegas. Si no hay foto de ese lado, se muestra otra y se avisa que es de otro lado. |
| Trayecto | Las tarjetas siguen fases por distancia, una a la vez. Se muestran también en el modo mapa, salvo en pantallas de 500 px de alto o menos. |
| «Voy apurado» | Va en Ajustes (botón en «¿A dónde vas?»), no en la brújula, para no sumar controles. Apaga los datos y los eventos del camino. |

## Fases del trayecto

| Fase | Cuándo | Qué se muestra |
|---|---|---|
| Partida | Los primeros 15 m caminados | Señal, distancia y pista. Ninguna tarjeta: primero hay que orientarse. |
| Trayecto | Más de 60 m del destino | Una tarjeta a la vez: primero un evento que está pasando cerca (a 35 m o menos de su lugar), si no, un dato curioso de la zona. Entre una tarjeta y la siguiente hay que caminar al menos 30 m. Cada tarjeta se retira sola tras 60 m caminados, o con la X. |
| Llegando | 60 m o menos | Solo la foto «Así se ve al llegar», del lado por el que llegas. |
| Llegada | Dentro de la zona de llegada | «¿Es este el lugar?» con la misma foto y, al confirmar, la pantalla de llegada con «¿Sabías que…?» y la invitación a dejar tu foto (sin mostrar la foto del lugar: ya se vio al acercarte y en «¿Es este el lugar?»). |

- Las tarjetas van dentro de la base de la brújula, sobre la pista, y empujan la señal hacia arriba; no flotan sobre la pantalla. Son compactas: rótulo, gancho en hasta 2 líneas y, en los eventos, una línea «lugar · hasta las HH:MM»; flecha › y botón X.
- Tocar la tarjeta abre una hoja con el dato completo (en un evento: el texto, la descripción y quién organiza) y «Seguir caminando». En los eventos la hoja suma «Ir ahí», que cambia el destino a ese lugar; en el recorrido de ejemplo no aparece.
- La tarjeta de un evento dice «Está pasando cerca»; en los de ejemplo, «Evento de ejemplo». Su texto es «Ahora en <lugar>, hasta las HH:MM.»
- Nunca se muestra una tarjeta del propio destino durante el trayecto: eso queda para la llegada.
- Con «Voy apurado» no hay tarjetas de trayecto; la foto «Así se ve al llegar» se mantiene, porque ayuda a reconocer el lugar.
- El modo voz anuncia las tarjetas igual que hoy (lee `state.zona`).
- En el modo mapa, los controles y el crédito de OpenStreetMap se ubican sobre la base medida (con la tarjeta incluida), así que no chocan con ella. La foto «Así se ve al llegar» se puede cerrar con la X.
- Pantallas bajas: con 700 px de alto o menos la pista pierde su rótulo visible y, mientras hay una tarjeta, se oculta la bajada (la frase bajo «Vas bien…»). Con 500 px o menos (320×454 o teléfono horizontal) no se muestran tarjetas del trayecto ni la foto «Así se ve al llegar», en ningún modo; la foto igual se ve en «¿Es este el lugar?».

## Foto según el lado

- El lado es N, E, S u O geográficos: la dirección desde el borde más cercano del edificio hacia la persona (`ladoFoto()` en `index.html`, la misma que se guarda al publicar una foto).
- Se calcula mientras te acercas, fuera del edificio. Una vez adentro se conserva el último lado conocido.
- Prioridad: foto oficial del mismo lado, foto de la comunidad del mismo lado, y después cualquier foto (oficial primero) con el aviso «Así se ve desde otro lado» en la tarjeta y una advertencia en «¿Es este el lugar?».
- Fotos oficiales con lado (campo `foto.lado` en `data/edificios.json`): A y F son del lado de Av. España (N), calculado desde la posición de la toma descrita en su pie. La de B es del patio de la piscina, que queda dentro del contorno del B: no tiene lado.
- En la demo (de Av. Los Placeres al A) se llega al A por el lado del campus, no por Av. España: la app muestra la foto del A avisando que es de otro lado. Es justamente el caso que motivó esta función; se resuelve con fotos de la comunidad de ese lado.

## Eventos

- Campos: `id`, `titulo`, `lugar` (id de un destino de la app), `donde` (sala o piso, opcional), `organiza`, `descripcion`, y `inicio`/`fin` en ISO 8601 con zona horaria (`2026-11-21T10:00:00-03:00`).
- Los eventos de ejemplo usan `relativo` (`inicio_min`, `dur_min`, en minutos desde que se abre la app) para que la demo siempre tenga algo «pasando ahora». Van marcados `ejemplo: true` y la app les pone la etiqueta «ejemplo».
- «Está pasando»: empezó y no ha terminado. «Próximos»: empieza dentro de los próximos 14 días. Los demás no se muestran.
- Texto de tiempo: «Ahora · hasta las 13:00», «Hoy, 18:00», «Mañana, 18:00», «En 9 días».
- La búsqueda también encuentra eventos por nombre, organizador o lugar.

## Límites

- Los eventos de ejemplo no son reales. El equipo debe reemplazarlos por eventos con fuente antes de presentarlos como tales.
- La foto según el lado depende de que existan fotos de cada lado. Hoy hay fotos oficiales solo de A, B y F; las demás vendrán de la comunidad.
- El lado se calcula con el GPS, que yerra 5 a 15 m: junto a una esquina puede elegir el lado vecino.
- Las distancias del trayecto se miden sobre la posición GPS; con mucho ruido, la persona puede «caminar» algunos metros sin moverse. Se cuenta un tramo solo cuando la posición se aleja 2 m o más de la anterior.

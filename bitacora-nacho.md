# Bitácora — Campus sin barreras

Hackathon LYOSS USM 2026 · 21 de noviembre de 2026
Equipo: Pia, Agustín y yo (Eduardo Ignacio).

Este documento retrata la visión de nuestro producto y cómo llegamos a ella. El detalle técnico está en `docs/PRD.md`.

## 01 Contexto

En términos simples, nuestra aplicación es móvil y parte de una necesidad básica: llegar como usuario de un punto A a uno B dentro del campus.

Elegimos Casa Central (Valparaíso). Está en un cerro, con desniveles y escaleras, y sus edificios se nombran con letras que no le dicen nada a quien llega por primera vez.

Primero perfilemos a los distintos tipos de usuario que podrían llegar a utilizar esta aplicación:

- **Estudiante de primer año  (o estudiante de la universidad):** cuando uno llega por primera vez a una universidad, no sabe cuál es el edificio A, B o C, dónde está el casino para comer (hay dos) ni a qué laboratorio ir.
- **Personas con discapacidad:**
  - **Silla de ruedas:** si una persona en silla de ruedas quiere llegar a ciertos edificios, hay ciertas **rutas** que solo puede tomar (sin escaleras ni desniveles fuertes).
  - **Persona con visibilidad reducida:** al no tener visión, su canal preferente es el audio. En su versión idílica más completa, la aplicación debería guiarla indicándole cuánto girar y hacia dónde ir. El problema es que la versión de solo brújula no le sirve; por eso su segunda funcionalidad debería ser un mapa con un camino trazado de verdad (A*).

## 02 Problemática

La dificultad concreta que abordamos es la **barrera de orientación**: la información disponible no basta para ubicarse en un campus que no se conoce.

- Los edificios tienen letras, no nombres que se entiendan.
- El cerro y los desniveles hacen que el camino directo choque con edificios o escaleras.
- Las soluciones habituales (mapa con ruta giro a giro) llevan al destino, pero no ayudan a conocer el lugar. Al día siguiente, el mechón sigue igual de perdido (por el lado técnico conviene no tener un pathfinding grafico)

## 03 El desafío

Respondemos así a lo que el enunciado deja libre:

| Libertad del desafío | Nuestra respuesta |
|---|---|
| Qué dificultad | Orientarse sin conocer el campus. |
| A qué estudiantes | Mechones y estudiantes en general que no conocen el campus. Las personas en silla de ruedas y las personas ciegas son la segunda etapa (ver «Accesibilidad»). |
| Qué aspecto mejorar | La información para orientarse, y que en el camino la persona conozca su universidad. |
| Qué tecnologías | Web/PWA (se abre con un enlace, sin instalar nada), GPS y brújula del navegador, y un mapa propio georreferenciado. |
| Cómo demostrarlo | Modo simulado: un recorrido de la Entrada Av. Los Placeres al Edificio A (205 m), pasando junto al Edificio C. |

**Filosofía.** Queremos quitar las barreras de orientación **de raíz**: la barrera baja cuando la persona conoce su universidad. La app guía sin reemplazar la exploración, y la comunidad ayuda al siguiente que llega.

**Propuesta.** Una aplicación móvil que entrega distintas maneras de ubicarse dentro del campus.

Por un lado, apuesta por el factor aventura: indicaciones más vagas para que el estudiante descubra los edificios y el campus en general de una manera más interactiva y educativa. Su modo principal es una brújula: el usuario solo ve una señal visual que le indica hacia dónde queda su destino. En el camino va descubriendo la universidad (barreras de orientación), los datos curiosos generan *engagement* y él mismo puede colaborar subiendo fotos.

Por otro lado, ofrece maneras más precisas para quien las necesite: la flecha, el mapa del campus y entrega tambien una funcionalidad para las personas con visibilidad reducida y para las personas con movilidad reducida
.
- **Resplandor direccional:** el borde de la pantalla brilla del lado del destino, como el indicador de sonido de Fortnite. Lejos, la luz es estrecha y fría; cerca, ancha y cálida. Al centro va la distancia en metros. No hay ruta: el camino lo elige la persona.
- **Información para no perderse:** una pista escrita por destino (por ejemplo, «el edificio de la torre, arriba de la escalinata de Av. España») y mensajes según la situación: vas bien, te estás alejando, está detrás de ti, casi llegas.
- **Datos curiosos por zona:** al pasar por un lugar aparece una tarjeta. Algunos que juntamos:
  - el C fue el hall de montaje de Mecánica;
  - el reloj del A usa un sistema eléctrico suizo anterior al cuarzo;
  - Labcomp era una sala de bowling;
  - el E y el F eran dormitorios;
  - el H, hoy museo, era la casa del rector.
- **Otra señal para quien no entienda la luz:** selector Resplandor / Flecha / Mapa. El mapa te ubica en el plano del campus.
- **Fotos de la comunidad:** en los últimos 60 m aparece la foto de cómo se ve el destino. Al llegar, puedes dejar la tuya (sin nombre) para quien venga después.
- **Llegada:** automática por GPS, a 20 m o menos del borde del edificio, con un botón «Ya llegué» por si el GPS falla.

**Accesibilidad (lo que estamos explorando).** Nos falta resolver la accesibilidad de los dos últimos usuarios; en esa parte todavía estamos experimentando. Sabemos que necesitamos una segunda funcionalidad, mucho más precisa y orientada a las capacidades físicas de cada persona:

- **Silla de ruedas:** rutas sin escaleras. El grafo de la rama `wip/brujula` ya marca una escalera en una arista, pero el A* todavía no lo usa.
- **Persona ciega:** guía por audio con giros y distancias, apoyada en un camino trazado.
- **Por discutir:** en el núcleo decidimos que el mapa ubica sin trazar ruta, mientras que esta funcionalidad sí la necesita. Falta acordar cómo conviven las dos.

## 04 Resultado esperado

El enunciado pide un prototipo funcional, no un producto terminado. Esto es lo que tenemos al cierre de la mañana:

| Parte | Estado |
|---|---|
| Diseño completo de la interfaz: 8 pantallas, 8 estados y una demo animada | Listo (lienzo en Claude Design, copiado en `design/`) |
| Datos del campus: 17 edificios, 32 puntos de interés, contornos y mapa propio | Listo (`data/`) |
| GPS y brújula en iPhone y Android, app instalable (PWA) | Listo (rama `main`) |
| Visor de mapa con zoom | Listo (rama `map`), pero hay que corregir su calibración |
| Llegada por cercanía al borde del edificio; brújula que apunta al borde más cercano | Listo (rama `wip/brujula`) |
| Resplandor, pistas y datos curiosos en código | Falta |
| Fotos comunitarias (cámara, subida, almacenamiento, moderación) | Falta |
| Fotos de C, M, P, Biblioteca, Comedores y Federación | Falta (sacarlas en terreno) |
| Publicación con HTTPS (la brújula del iPhone lo exige) | Falta |
| Accesibilidad (silla de ruedas y ciegos) | En exploración |

## 05 Información y recursos

**Fuentes que usamos:**

- Plano oficial de Casa Central (infraestructura.usm.cl), en `docs/plano-casa-central.png`.
- OpenStreetMap, para los contornos de los edificios. Hay que atribuirlo en la app: «© colaboradores de OpenStreetMap».
- Wikimedia Commons, para las fotos con licencia libre del A, F y B.
- Datos curiosos aportados por el equipo (`datos-freak.md`).
- Mazurkiewicz et al. (2023), https://doi.org/10.3390/ijgi12020027: la gente acepta caminar más si así conoce su entorno. No afirmamos que sin ruta se aprenda más, porque la evidencia no lo respalda.

**Supuestos y limitaciones:**

- Las coordenadas marcan el centro del edificio, no su puerta. No se midieron en terreno.
- Las pistas son borradores redactados desde el plano.
- Existen dos georreferencias: la nuestra (OpenStreetMap contra el plano, 1 a 2 m de error) y la de `wip/brujula` (3 lecturas de GPS). Difieren en 10 a 30 m y no sabemos cuál se acerca más al terreno.
- El GPS ronda los 5 m a cielo abierto y empeora entre edificios.
- El navegador no detecta zonas con la página cerrada: los datos curiosos solo aparecen con la app abierta.
- La señal directa puede apuntar a través de un edificio o un desnivel; por eso la pista escrita es parte del núcleo.

## 06 Consideraciones generales

**Uso de IA generativa.**

- Usamos Claude Code en dos sesiones paralelas: una para el producto, el PRD y el diseño, y otra para los datos y el mapa.
- Usamos Claude Design para el prototipo de interfaz.
- Los commits de las ramas `main` y `map` registran coautoría de Claude.

**Cómo apuntamos a cada criterio de evaluación:**

| Criterio | Nuestro argumento |
|---|---|
| Impacto | Ataca un problema que vive quien llega por primera vez a Casa Central; la segunda etapa llega a quienes enfrentan barreras físicas. |
| Innovación | La brújula sin mapa ya existe (Crowsflight, Actionbound, CSUMB GPS). Lo nuestro es combinarla con datos por zona y fotos de la comunidad, en un campus concreto y sin instalar nada. |
| Ejecución y funcionalidad | Sensores reales en el teléfono, datos georreferenciados del campus y una demo simulada que no depende del GPS en sala. |
| Presentación y documentación | PRD vivo, fuentes citadas, supuestos declarados y esta bitácora. |
| UX/UI | Una paleta de calma (sé que voy a llegar) que se vuelve coral y amarilla al llegar, movimiento lento y estados para cuando algo falla. |

## Equipo y roles

- **Pia:** la base de la app (PWA, GPS y brújula) en `main`; luego, en `wip/brujula`, el grafo real del campus, los contornos de los edificios y la llegada por cercanía al borde.
- **Agustín:** el visor de mapa (rama `map`). Ahora integrará toda la aplicación.
- **Yo:** producto (PRD), prototipo de interfaz y datos del campus. Ahora me ocuparé de garantizar la accesibilidad para personas en silla de ruedas y personas ciegas.

## Dificultades al momento de colaborar

- **Overlap de pega:**
  - `map` y `wip/brujula` reescribieron el mismo bloque del grafo con modelos incompatibles: 17 nodos en píxeles frente a 31 en metros.
  - Terminamos con dos georreferencias distintas.
  - `main` y `map` partieron trazando ruta, mientras el producto decía «sin ruta».
- **Definir roles:** la integración quedó a cargo de Agustín y la accesibilidad, a mi cargo.
- **Brainstorming al inicio:** dudamos entre dos ideas (asignación de salas accesible y la brújula). Elegimos la brújula y dejamos la otra como trabajo futuro.

## Pendientes

- Acordar si el mapa traza ruta: no para mechones, sí para la capa accesible.
- Elegir una sola georreferencia para todo el código.
- Integrar en una sola app: la base de `wip/brujula`, el visor de `map` recalibrado y la interfaz del lienzo.
- Sacar en terreno las fotos que faltan y asignar a cada dato curioso su zona.
- Publicar con HTTPS para probar en iPhone.

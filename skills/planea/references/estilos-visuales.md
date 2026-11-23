# Estilos visuales de referencia

Cinco estilos lúdicos inspirados en el lenguaje visual de los juegos educativos web. Sirven como punto de partida para la identidad visual de un proyecto ([diseño de recursos](diseno-recursos.md) §2) y para los juegos ([juegos didácticos](juegos-didacticos.md)).

Reglas:
- Tomar del estilo sus **rasgos de género**: estructura, jerarquía, formas, ritmo y tipo de retroalimentación.
- **No copiar** nombres, logotipos, mascotas, personajes, colores de marca, sonidos ni pantallas de ningún producto comercial. Los tokens de esta guía son propios y ajustables.
- Todo estilo debe cumplir el estándar obligatorio de layout: legibilidad, contraste (todo par texto/fondo de 4.5:1 o más), funcionar en blanco y negro y no partir bloques entre páginas.
- Elegir un estilo base por proyecto y adaptarlo al tema. Se pueden mezclar rasgos de varios con moderación.
- **Tipografía:** cada token de fuente es una pila: fuentes nombradas (licencia libre, OFL) y luego el respaldo `R` = `system-ui, 'Segoe UI', Arial, sans-serif` (`Rd` = `Impact, 'Arial Black', sans-serif` para títulos display). Usar la fuente nombrada solo si está instalada o si el usuario permite incrustar un archivo local con licencia libre; si no, usar el respaldo ([diseño de recursos](diseno-recursos.md) §2).
- **Tamaños para proyección:** los mínimos de [diseño de recursos](diseno-recursos.md) §3 mandan sobre los rangos de los tokens.

## 1. Bloques de respuesta
*Género: quiz en vivo proyectado con respuestas por color y figura.*

**Rasgos.** Fondo oscuro y saturado. Respuestas en bloques grandes de color, cada uno con una figura. Tipografía geométrica muy gruesa. Temporizador visible y ritmo rápido. Pantalla compartida (proyector) separada de la respuesta del alumno.

**Layout**
- Pregunta en una banda clara arriba, a todo lo ancho.
- Imagen o dato al centro, temporizador circular a un lado y contador de respuestas al otro.
- Rejilla 2×2 de respuestas en el 35–40 % inferior.
- Al final, podio de 3 barras con los equipos.

**Tokens**
| Rol | Valor de partida |
| --- | --- |
| Fondo | violeta profundo `#3a1f73` o azul noche `#1c2a5a` |
| Banda de pregunta | blanco `#ffffff`, texto `#1d1d2b` |
| Opciones (color + figura) | A `#c43c40` triángulo · B `#2f6fdb` círculo · C `#e9a92c` cuadrado · D `#23824a` rombo; texto blanco, salvo en C: `#1d1d2b` |
| Tipografía | pila: Montserrat, Poppins, Lexend, `R`; peso 800; pregunta en mayúscula inicial |
| Radio y sombra | 8–10 px; sombra dura `0 4px 0` en un tono más oscuro del bloque |
| Tamaños (proyección) | título ≥ 64 px; pregunta 48–56 px; opciones 32–40 px; temporizador 64 px |

**Usos.** Juegos de respuesta simultánea con tarjetas de colores, repasos de cierre y láminas de preguntas para proyectar. En impresión: tarjetas A–D y hojas de registro de respuestas.

**Impresión.** La figura y la letra identifican la opción sin color; fondo claro en papel.

## 2. Ruleta de categorías
*Género: trivia por categorías con ruleta y personajes-objeto.*

**Rasgos.** Cada categoría tiene color, ícono y un personaje hecho a partir de un objeto. Una ruleta central decide la categoría. El avance se marca por tercios hasta ganar una insignia. Tipografía redondeada de caricatura. Tono alegre y coleccionable.

**Layout**
- Ruleta al centro con 5–6 sectores y un sector comodín.
- Barra de progreso segmentada abajo.
- Fila de insignias ganadas arriba.
- La pregunta aparece en una tarjeta que ocupa casi toda la pantalla, con el color de la categoría en el encabezado.

**Tokens**
| Rol | Valor de partida |
| --- | --- |
| Categorías (luminancias distintas para blanco y negro) | `#2570c8` · `#3aa655` · `#f08a24` · `#f2c230` · `#e0559a` · `#c63a31`; comodín `#6b3fb5`. Texto blanco en el primero, el sexto y el comodín; `#111111` en los demás |
| Fondo | degradado suave del color comodín o un claro `#f4f1fb` |
| Tipografía | títulos: pila Baloo 2, Fredoka, Nunito, `R`, peso 700–800; texto: pila Nunito, `R`, peso 600 |
| Radio | 16–24 px; contorno de 3 px más oscuro en tarjetas y botones |
| Íconos | un ícono simple y grueso por categoría, siempre con su nombre |

**Usos.** Repaso interdisciplinario: cada disciplina del campo es una categoría (ESP, ING, ART, LILM o física, química, matemáticas). También maratón de tablero impreso y álbum de insignias por equipo.

**Impresión.** Cada categoría se distingue por ícono y nombre, no solo por color.

## 3. Gamificado amable
*Género: aprendizaje por niveles con botones táctiles y progreso visible.*

**Rasgos.** Lienzo blanco con mucho aire y un solo color de acento intenso. Botones «pulsables» con labio inferior duro, sin sombras difusas. Esquinas muy redondeadas. Etiquetas en mayúsculas con espaciado. Texto en gris oscuro en lugar de negro. Ilustraciones planas de formas redondeadas que cargan la emoción. Progreso, rachas y logros.

**Layout**
- Columna central estrecha (máximo 600–700 px en pantalla).
- Barra de progreso arriba.
- Una tarea por pantalla o bloque.
- Botón principal ancho abajo.
- Retroalimentación en un panel inferior de color (acierto o error), con la explicación.

**Tokens**
| Rol | Valor de partida |
| --- | --- |
| Fondo | `#ffffff`; bandas de sección `#eef7ff` |
| Acento y labio | verde `#2f7d12` sobre `#256310` con texto blanco, o el acento del proyecto con un labio un 20 % más oscuro (el texto del botón llega a 4.5:1) |
| Secundario | azul `#0b6aa8` para enlaces y botones secundarios |
| Texto | `#3f3f46` principal, `#52525b` secundario, `#656570` atenuado (4.5:1 o más sobre `#ffffff` y `#eef7ff`) |
| Bordes | `#e4e4e7`, de 2 px |
| Tipografía | pila: Nunito, Fredoka, Baloo 2, `R`; cuerpo 500–600; botones 700 en MAYÚSCULAS con +0.05 em |
| Radio y profundidad | 12–16 px; `box-shadow: 0 4px 0 <labio>`; al pulsar baja 4 px |

**Usos.** Hojas de trabajo por niveles (nivel 1, 2 y 3 según Bloom), rutas de aprendizaje, autoevaluación con casillas de logro, fichas de práctica y juegos de práctica individual proyectados.

**Impresión.** Los «niveles» como recuadros numerados; el acento solo en títulos y casillas.

## 4. Arcade de personajes
*Género: quiz combinado con un modo de juego (carrera, monedas, mejoras) y personajes coleccionables.*

**Rasgos.** Personajes simples tipo estampa, con contorno grueso. Monedas, mejoras y modos de juego. Sombras duras desplazadas y bordes negros gruesos, al estilo neobrutalista. Fondos con patrón. Títulos con tipografía display con carácter. Mucho contraste y energía.

**Layout**
- Marcador y monedas en una barra superior.
- Escenario del modo de juego al centro (pista de carrera, mapa, tablero).
- Pregunta en un panel emergente.
- Tienda o mejoras en tarjetas laterales.

**Tokens**
| Rol | Valor de partida |
| --- | --- |
| Fondo | color vivo con patrón suave (puntos, cuadrícula) `#ffd84d` / `#7fd1ff` |
| Superficies | blanco `#ffffff` con borde `#111111` de 3 px |
| Sombra | dura y desplazada: `4px 4px 0 #111111` |
| Acentos (texto `#111111` encima) | `#ff5a5f`, `#3ddc97`, `#8b78ff` |
| Tipografía | títulos: pila Lilita One, Bungee, Luckiest Guy, `Rd`; texto: pila Nunito, Rubik, `R`, peso 600; tipografía pixel solo en títulos cortos |
| Radio | 6–12 px |

**Usos.** Juegos de carrera por equipos, álbumes de estampas o tarjetas coleccionables (un personaje por concepto) y tableros impresos con fichas. Diseñar personajes propios del tema: un átomo, una gota, una figura geométrica.

**Impresión.** Funciona muy bien en blanco y negro gracias a los contornos y sombras duras.

## 5. Tarjetas de práctica temáticas
*Género: práctica a ritmo propio con tarjetas limpias, temas intercambiables y retroalimentación explicada.*

**Rasgos.** Fondo de color o ilustración temática. Tarjetas blancas grandes y limpias. Opciones en lista o rejilla con número o letra. Barra de progreso. Tras responder, un aviso de acierto o error con explicación breve. Recompensas ligeras (monedas, insignias). Aspecto pulido y sobrio, sin ruido visual.

**Layout**
- Barra superior con progreso y número de pregunta.
- Tarjeta central con la pregunta e imagen opcional.
- Opciones en 2×2 o en lista vertical.
- Aviso de retroalimentación con la explicación y el botón «siguiente».

**Tokens**
| Rol | Valor de partida |
| --- | --- |
| Fondo | tema del proyecto (ilustración suave o color `#5b3cc4`, `#0f766e`, `#1e3a8a`) |
| Tarjeta | `#ffffff`, radio de 16–20 px, sombra suave `0 8px 24px rgba(0,0,0,.12)` |
| Opciones | tonos medios distintos, con letra y número, y texto de 4.5:1 o más; borde de 2 px al seleccionar |
| Retroalimentación | acierto `#15803d` / error `#dc2626` con ícono y texto (sobre `#ffffff`, 4.5:1 o más), nunca solo color |
| Tipografía | pila: Inter, Rubik, Lexend, `R`; cuerpo 500, títulos 700 |

**Usos.** Fichas de práctica, cuestionarios de recuperación, exámenes formativos y hojas de trabajo con temas visuales por proyecto. Es el más sobrio: conviene en Saberes y Pensamiento Científico y en instrumentos de evaluación.

**Impresión.** Tarjetas como recuadros con borde fino; el tema solo en el encabezado.

## Elegir el estilo
| Situación | Estilo sugerido |
| --- | --- |
| Repaso grupal rápido proyectado | 1 Bloques de respuesta |
| Repaso que integra disciplinas o temas | 2 Ruleta de categorías |
| Práctica por niveles, autoevaluación, rutas | 3 Gamificado amable |
| Juego por equipos con avance, coleccionables | 4 Arcade de personajes |
| Fichas, práctica individual, evaluación formativa | 5 Tarjetas de práctica temáticas |

Ajustar los tokens del estilo elegido al tema y presentarlos en la identidad visual del proyecto antes de producir recursos:
1. Sustituir el acento y los colores de apoyo por los de la paleta del tema, conservando el rol de cada token.
2. Recalcular el contraste de cada par texto/fondo (4.5:1 o más) y revisar el resultado en escala de grises; cambiar el color del texto o ajustar el tono hasta cumplirlo.
3. Fijar una pila de títulos y una de texto con respaldo del sistema, y anotar los valores finales en la identidad.

## Fuentes consultadas (23/11/2026)
Sirven de contexto: no se nombran ni se imitan en ningún recurso.
- Kahoot!. *Brand guidelines* (2020) y *Illustrations and colors*. kahoot.com/library.
- Barker, M. (2020). *Shape language: Duolingo's art style*. Duolingo Blog. blog.duolingo.com/shape-language-duolingos-art-style/
- Monotype (2022). *The Duolingo font: exploring Feather*. monotype.com
- Tastekit. *Duolingo design spec — colors, typography, components*. tastekit.dev/gallery/apps/duolingo (análisis no oficial).
- Made Good Designs (2026). *Trivia Crack brand guidelines* (interpretación no oficial). madegooddesigns.com/trivia-crack-brand-guidelines/
- Razak, C. (2023). *Learning games: Blooket vs Kahoot vs Gimkit vs Quizizz*. slideswith.com
- Feinsilber, J. (2018). *The design challenge of Gimkit 1.0*. The Gimkit Blog, Medium.
- Bhatt, S. *Making learning gamified for students at Quizizz* (caso de diseño). shubhambhatt.com

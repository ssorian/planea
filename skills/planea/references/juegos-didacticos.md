# Juegos didácticos

Los juegos son un recurso de práctica y repaso, no de evaluación sumativa. Incluir uno solo si sirve al PDA de la sesión; nunca como relleno.

## Cuándo usar un juego
| Momento | Uso | Bloom que cubre por defecto |
| --- | --- | --- |
| Activación de saberes (inicio) | Explorar qué sabe el grupo antes de enseñar | Recordar, comprender |
| Repaso (cierre o sesión previa a la evaluación) | Fijar datos, vocabulario, procedimientos | Recordar, comprender, aplicar |
| Recuperación | Retomar lo que el diagnóstico o el resumen del juego marcó como débil | Comprender, aplicar |

Un juego de respuesta corta se queda en recordar y comprender. Para subir de nivel:
- **Aplicar:** plantear casos o problemas nuevos, no definiciones.
- **Analizar:** pedir que comparen, clasifiquen o expliquen por qué una opción no es correcta.
- **Evaluar:** pedir justificar la respuesta antes de revelarla («¿qué evidencia la apoya?»).
- **Crear:** que cada equipo redacte las preguntas y respuestas del siguiente juego y las valide con el docente.

Declarar en la sesión el nivel de Bloom real que trabaja el juego; no atribuirle más del que alcanza.

## Reglas
1. Participan **todos**: elegir juegos en los que cada alumno responde (tarjetas, equipos con roles rotativos); evitar los de turno único donde la mayoría espera.
2. Sin humillar: no exhibir errores individuales ni castigar. El error es información; comentarlo con el grupo.
3. Equipos **mixtos** en nivel y afinidad; rotar la integración entre sesiones.
4. Tiempo acotado: 10–20 minutos; fijar duración y número de rondas antes de empezar.
5. Respuestas **verificadas** antes de jugar: contrastarlas con el libro o la fuente del PDA. Nunca generar preguntas con respuestas sin revisar; el kit no trae contenido.
6. Premiar el proceso (argumentar, colaborar), no solo el puntaje. No usar el resultado como calificación.
7. Prever **alternativa impresa** si no hay proyector, energía o computadora: tarjetas de colores impresas y preguntas leídas por el docente, o un juego sin pantalla del catálogo.
8. Cerrar siempre con una pregunta de metacognición («¿qué tema me costó?») y anotar qué reforzar.

## Juegos digitales del kit
Kit en `~/.pi/agent/skills/planea/assets/kit-juegos/` (instrucciones, esquemas JSON y controles en su `README.md`). Cada juego es un HTML único que funciona con doble clic, sin internet.

| Juego | Mecánica | Uso didáctico |
| --- | --- | --- |
| `encuesta` «La comunidad opina» | Pregunta con 4–8 respuestas ocultas con puntos; 3 errores; dos equipos | Activación de saberes y vocabulario: respuestas que el grupo conoce o puede predecir. Pedir las respuestas más frecuentes de una encuesta real hecha antes al grupo |
| `tarjetas` «Tarjetas de colores» | Quiz sin celulares: el grupo levanta tarjeta A–D; el docente anota cuántos acertaron; resumen por pregunta y tema | Repaso y diagnóstico rápido de todo el grupo. Imprimir tarjetas con `kit-recursos/ejemplos/tarjetas-colores.tsx`. Usar el campo `tema` para saber qué reforzar |
| `tablero` «Tablero de categorías» | Categorías × valores; celda abre pregunta; puntos a equipos | Repaso por temas con dificultad creciente: valor bajo = recordar, valor alto = aplicar o justificar |
| `ruleta` «Ruleta» | Giro animado sobre nombres o preguntas; opción de no repetir | Elegir quién participa con equidad; sortear preguntas o roles; es complemento de otros juegos |

Flujo para producir un juego digital:
1. Redactar los datos JSON desde los PDA y los contenidos reales de la sesión; verificar cada respuesta.
2. Construir: `bun ~/.pi/agent/skills/planea/assets/kit-juegos/construir.ts <juego> <datos.json> <salida.html>`. Corregir los errores que reporte el validador.
3. Capturar con `capturar.ts` (mismo kit) y **revisar la imagen**: texto completo, legible y sin cortes.
4. Probar el HTML en el navegador antes de entregarlo.

Para `tarjetas`, producir también las tarjetas A–D (copia del ejemplo del kit-recursos) y mencionar en la sesión que se imprimen una por alumno o pareja.

## Juegos sin pantalla
| Juego | Mecánica breve | Uso didáctico | Material |
| --- | --- | --- | --- |
| Lotería de conceptos | Tablas con conceptos o imágenes; el docente lee definiciones y los alumnos marcan el concepto | Vocabulario y definiciones (recordar, comprender) | Tablas impresas (kit React → PDF), fichas o frijoles, tarjetas de definiciones |
| Basta temático | Por columnas de categorías del tema, escribir en tiempo fijo una palabra que inicie con la letra sorteada | Vocabulario y clasificación | Hoja con categorías; cronómetro |
| Maratón de tablero impreso | Tablero de casillas con preguntas por nivel; equipos avanzan al acertar | Repaso largo por unidad | Tablero y tarjetas de preguntas impresos; dado; fichas |
| Verdadero/falso corporal | Enunciados leídos; el grupo se mueve a un lado (verdadero) o a otro (falso) y justifica | Corregir ideas previas; activar saberes | Enunciados verificados; espacio libre |
| Bingo de conceptos | Cartón con conceptos; el docente lee características y se marca el que corresponde | Relacionar concepto y característica | Cartones impresos; tarjetas de pistas |
| Reto de pistas tipo escape | Equipos resuelven una secuencia de pistas (problema, texto, acertijo) para abrir un «candado» de respuesta final | Aplicar y analizar; trabajo colaborativo | Sobres con pistas; clave de respuesta; cronómetro |
| Papa caliente de preguntas | Pasar un objeto mientras el docente cuenta o marca el tiempo; quien lo tiene al parar responde o elige a quien ayude | Repaso con participación; baja presión | Objeto blando; tarjetas o lista de preguntas |
| Rally por estaciones | Equipos rotan por estaciones con una tarea breve cada una (problema, lectura, experimento) | Aplicar y practicar varias habilidades | Tarjetas de estación; hoja de registro; cronómetro |

Para cada uno: elaborar tarjetas, tablas o tableros con el kit React → PDF (ver [recursos](recursos-react-pdf.md)) y entregar las reglas de una cuarta de página.

## Enlazar el juego como anexo
1. Guardar el HTML en `Recursos/` del proyecto con nombre estable `anexo-NN-nombre.html`, y los datos en `Recursos/fuente/anexo-NN-nombre.json`.
2. Generar la **captura real** de pantalla con `capturar.ts` (con `--teclas` para mostrar un estado representativo) y usarla como vista previa en ANEXOS. No inventar ni dibujar la vista previa.
3. En ANEXOS indicar el nombre del archivo, que se abre con doble clic en el navegador (Edge o Chrome en Windows), que no requiere internet y los atajos esenciales (`F` pantalla completa, `H` ayuda).
4. En la sesión citar el anexo en la actividad donde se juega y declarar el nivel de Bloom, el tiempo y la alternativa impresa.
5. Identificar el material como «Elaboración propia con apoyo de IA». Usar nombres propios del juego; no emplear nombres, logotipos, música ni tableros de concursos comerciales.

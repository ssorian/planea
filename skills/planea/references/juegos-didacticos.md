# Juegos didácticos: cómo diseñarlos

No hay juegos prefabricados. Diseñar cada juego para el PDA y la sesión concreta, a partir de una mecánica sencilla y conocida, con fuerte apoyo visual. Construirlo solo cuando el diseño esté aprobado.

## 1. Partir del propósito
- Definir qué PDA y qué nivel de Bloom practica el juego. El juego es un medio de práctica de recuperación, aplicación o discusión, nunca un relleno.
- Ubicarlo en la sesión: activar saberes previos (inicio), practicar (desarrollo) o recuperar lo aprendido (cierre).
- Duración: 5–15 minutos, incluidas las reglas. Reglas explicables en menos de un minuto.
- Cerrar con una reflexión breve: ¿qué fue difícil?, ¿qué aprendimos?

## 2. Elegir una mecánica sencilla
| Mecánica | Cómo se juega | Bloom habitual | Cómo subir de nivel |
| --- | --- | --- | --- |
| Respuesta simultánea | Todos levantan a la vez una tarjeta de color (A–D), una pizarrita o los dedos | 1–2 | Opciones que exigen aplicar o analizar; pedir a un alumno que justifique su elección |
| Respuestas ocultas por equipos | Adivinar las respuestas más frecuentes de una encuesta del grupo o la comunidad | 1–2 | Encuesta sobre causas, consecuencias o soluciones; justificar cada respuesta |
| Tablero de categorías | Elegir categoría y valor; más valor, más difícil | 1–4 | Valores altos con problemas, casos o análisis |
| Azar (ruleta, dado, papelitos) | El azar elige quién responde o qué pregunta | Según la pregunta | Preguntas abiertas de evaluar o crear |
| Emparejar (memorama) | Unir concepto con definición, imagen, ejemplo o traducción | 1–2 | Pares de causa-efecto, problema-solución |
| Ordenar | Poner en secuencia pasos, hechos, etapas o párrafos | 2–3 | Justificar el orden; detectar el paso que falta |
| Clasificar | Repartir tarjetas en grupos o «canastas» | 2–4 | Que los equipos inventen el criterio de clasificación |
| Adivinar con pistas | «¿Quién o qué soy?»: pistas de lo general a lo específico | 1–3 | Que los equipos escriban las pistas |
| Carrera de casillas | Avanzar en un tablero al acertar retos | Según los retos | Retos de aplicación en casillas especiales |
| Lotería o bingo | Marcar el concepto cuando se lee su definición o ejemplo | 1–2 | Leer ejemplos o situaciones, no definiciones |
| Basta temático | Escribir una palabra por categoría con una letra dada | 1–2 | Categorías de relación: «causa de…», «ejemplo de…» |
| Verdadero o falso corporal | Moverse a un lado del salón según la respuesta | 1–2 | Afirmaciones con trampa; corregir la falsa |
| Reto de pistas (tipo escape) | Resolver acertijos encadenados para abrir el siguiente | 3–4 | Acertijos que combinan contenidos |
| Estaciones o rally | Equipos rotan por estaciones con retos distintos | 2–6 | Una estación de crear o evaluar |

Combinar o adaptar mecánicas está permitido; inventar reglas complejas no. Usar nombres y aspecto propios: no copiar nombres, logotipos, música ni diseño de programas de televisión o aplicaciones comerciales.

## 3. Reglas didácticas
- **Participación de todos:** preferir respuesta simultánea o por equipos sobre turnos individuales donde la mayoría espera.
- **Sin celulares:** tarjetas de colores, pizarritas, papel, cuerpo o proyector.
- **Equipos mixtos y rotación de roles** (vocero, anotador, verificador).
- **Retroalimentación inmediata:** tras cada respuesta, mostrar la correcta y explicar brevemente por qué.
- **El error es seguro:** no exhibir a nadie, no eliminar jugadores y no restar puntos de forma humillante.
- **Competencia sana:** entre equipos, con marcador visible; reconocer también el esfuerzo y la mejora.
- **Contenido verificado:** cada pregunta tiene respuesta correcta revisada; sin ambigüedades ni trampas injustas.
- **Registro formativo:** anotar qué preguntas fallaron más para retomarlas.
- **DUA:** apoyo visual y oral en cada pregunta, tiempo suficiente y roles que no dependan solo de la lectura.

## 4. Diseño visual
Tomar como base uno de los [estilos visuales de referencia](estilos-visuales.md) (bloques de respuesta, ruleta de categorías, gamificado amable, arcade de personajes, tarjetas temáticas) y aplicar estas reglas:
- **Una idea por pantalla o tarjeta;** poco texto y palabras clave en lugar de párrafos.
- **Legible de lejos:** tamaños mínimos para proyección, lámina de grupo y tarjetas según [diseño de recursos](diseno-recursos.md) §3 (fuente única).
- **Alto contraste** y paleta reducida: 1 color de acento y colores fijos para las opciones.
- **Nunca solo color:** cada opción lleva color, letra y figura (A rojo triángulo, B azul círculo, C amarillo cuadrado, D verde rombo).
- **Íconos e imágenes que expliquen,** no que decoren: diagramas, fotos reales o ilustraciones pertinentes.
- **Retroalimentación muy visible:** correcto/incorrecto con color, ícono y la respuesta escrita.
- **Marcador y tiempo siempre visibles** cuando el juego los usa.
- **Animaciones breves** (menos de 1 segundo), solo para mostrar un cambio de estado.
- **Coherencia:** la misma estructura en todas las pantallas o tarjetas del juego.

## 5. Elegir el formato
| Situación del aula | Formato |
| --- | --- |
| Sin proyector o sin electricidad confiable | Impreso: tarjetas, tableros, cartas, hojas de registro (diseño de recursos → PDF) |
| Con proyector o televisión | Proyectado: página HTML sin internet (ver §6) |
| Sin materiales | Corporal u oral: verdadero/falso con movimiento, adivinanzas, papa caliente de preguntas |

Ofrecer siempre una alternativa impresa u oral del juego proyectado.

## 6. Construir un juego proyectado (Vite)
Solo con el diseño aprobado. Comandos en [herramientas](herramientas.md); la primera ejecución descarga paquetes y requiere permiso.
1. Crear el proyecto en `Recursos/juegos/<nombre>/` del proyecto didáctico: `npm create vite@latest <nombre> -- --template react-ts`; añadir `vite-plugin-singlefile` para que el build sea un solo HTML que funcione con doble clic y sin internet.
2. Separar los datos (preguntas, respuestas, puntos) en un JSON y validarlos al construir; la lógica no contiene contenido curricular.
3. Controles por teclado y ratón; atajos visibles en una pantalla de ayuda; pantalla completa.
4. Sin recursos externos: tipografías como pila con respaldo del sistema (fuente nombrada solo si está instalada o el usuario permite incrustar un archivo local con licencia libre; ver [diseño de recursos](diseno-recursos.md) §2), imágenes locales incrustadas, sin sonidos con derechos.
5. Construir, abrir el HTML con Playwright y capturar cada estado del juego (ver [herramientas](herramientas.md)); revisar las capturas de cada estado del juego; buscar en el HTML que no haya URL externas.
6. Guardar el HTML final en `Recursos/juegos/<nombre>/` y la captura real de la pantalla principal como vista previa en ANEXOS.

## 7. Ficha del juego (para el diseño)
Presentar cada juego con (ficha llena en el [ejemplo de campo](../assets/ejemplo-campo.md)): nombre propio, PDA y nivel de Bloom, momento de la sesión, mecánica y reglas en 3–5 pasos, organización, material, tiempo, retroalimentación prevista, variantes DUA, alternativa sin proyector y lista de preguntas con su respuesta verificada.

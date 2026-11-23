# Diseño de recursos

No hay plantillas ni componentes. Los cinco [estilos visuales de referencia](estilos-visuales.md) son puntos de partida y sus tokens se ajustan al tema del proyecto. Diseñar cada recurso para su actividad y su PDA, con libertad visual, dentro de un estándar de layout que garantiza que se lea, se use y se imprima bien. Como base técnica (no visual), partir de [esqueleto-recurso.html](../assets/esqueleto-recurso.html). Al terminarlo, convertirlo a PDF.

## 1. Decidir antes de diseñar
| Necesidad | Decisión |
| --- | --- |
| Ya existe un material adecuado | Usarlo según [materiales existentes](materiales-existentes.md) |
| Texto exacto (fichas, hojas, instrumentos, tarjetas, guías, organizadores, lecturas) | Diseñar en HTML (o React) y convertir a PDF |
| Figura de apoyo: animal, planta, vehículo, objeto, diagrama | Dibujarla en SVG o React según [figuras](figuras-html.md) |
| Ilustración detallada, escena, portada o portadilla | Generar la imagen e insertarla en el recurso HTML si lleva texto |
| Juego | [juegos didácticos](juegos-didacticos.md) |

No pedir texto largo dentro de imágenes generadas: sale con errores. El texto va en HTML y la imagen se inserta.

Para cada recurso fijar: propósito y PDA, quién lo usa (alumno, equipo, docente), momento de la sesión, cómo se usa (leer, escribir, recortar, proyectar, pegar en el cuaderno), número de páginas y si se imprime en blanco y negro.

## 2. Identidad visual del proyecto (libre)
Antes de crear el primer recurso de un proyecto, proponer en el diseño una identidad breve y aplicarla a todos sus recursos:
- **Paleta:** 1 color de acento, 1–2 de apoyo y neutros, inspirados en el tema (por ejemplo, tierra y verdes para un proyecto sobre el territorio; azules para flotabilidad).
- **Tipografía:** una para títulos con carácter y una para texto muy legible. Cada token de fuente es una pila con respaldo del sistema (`system-ui, 'Segoe UI', Arial, sans-serif`); la fuente nombrada se usa solo si está instalada o si el usuario permite incrustar un archivo local con licencia libre; si no, se usa el respaldo.
- **Motivo gráfico:** un elemento que dé unidad (ilustración, forma, textura, ícono, borde).
- **Tono de las ilustraciones:** coherente en todo el proyecto.

Partir de uno de los [estilos visuales de referencia](estilos-visuales.md) y adaptarlo al tema. Para que el resultado se vea elaborado (color 60-30-10 con paletas por campo formativo, sistema de formas, estilo de ilustración, encabezados, pasos, globos, insignias y recetas por tipo de recurso, con sus dosis), seguir [calidad visual](calidad-visual.md). La identidad cambia entre proyectos y campos; no reutilizar la misma por inercia. Si el usuario da una identidad o una plantilla, seguirla.

## 3. Estándar de layout
| Nivel | Reglas |
| --- | --- |
| **Obligatorio** (legibilidad y uso) | Cuerpo de texto de 10 pt o más (tablas de 9 pt como mínimo absoluto); contraste de texto de 4.5:1 o más; funciona en blanco y negro (el color nunca es la única señal); márgenes imprimibles de 10 mm o más; ningún bloque partido entre páginas (tablas, reactivos, figuras, recuadros); consigna visible en la misma página que la tarea; espacio de respuesta suficiente para escribir a mano; sin dependencias de internet; **material proyectado: pregunta ≥ 48 px, título ≥ 64 px, opciones ≥ 32 px** (fuente única de estos tamaños) |
| **Recomendado** (estándar de partida, ajustable) | Carta vertical; márgenes de 12–18 mm; retícula de 1 columna para leer, 2 para comparar y malla regular para recortables; jerarquía de 3 niveles; renglones de 8–9 mm; título 16–22 pt, cuerpo 10.5–12 pt, tarjetas 18 pt o más, láminas de pared 28 pt o más |
| **Libre** (diseño) | Paleta, tipografías, composición, ilustraciones, íconos, fondos, bordes, orientación y formato no estándar (tríptico, media carta, tarjetas, póster), siempre que se cumpla lo obligatorio |

## 4. Zonas de una hoja
Orden de lectura recomendado; adaptar o fusionar zonas según el recurso:
1. **Encabezado:** título; anexo, campo y grado.
2. **Datos:** nombre o equipo, grupo, fecha (solo si el recurso se entrega).
3. **Consigna:** en infinitivo, breve y destacada.
4. **Contenido o tarea:** el cuerpo del recurso.
5. **Respuesta o registro:** espacios, puntaje, retroalimentación.
6. **Créditos:** «Elaboración propia con apoyo de IA» o «Adaptado de…» con su fuente (citar según [materiales existentes](materiales-existentes.md#citar)).

Separar en archivos o páginas distintas la hoja del alumno, la clave del docente y el material para recortar.

## 5. Qué lleva cada tipo de recurso
| Recurso | Contenido mínimo |
| --- | --- |
| Ficha informativa | Idea central destacada, 3–5 bloques breves con subtítulo, una figura o diagrama, glosario si hace falta, fuente |
| Hoja de trabajo | Ejercicios numerados de menor a mayor nivel de Bloom, con espacio de respuesta |
| Lámina o infografía | Un mensaje principal, 5–7 bloques como máximo, cifras grandes, íconos con texto |
| Organizador gráfico | Estructura vacía o semillena, espacio para escribir a mano, una casilla resuelta como ejemplo |
| Tarjetas | Malla regular con líneas de corte, texto grande; anverso y reverso alineados |
| Guía de entrevista u observación | Propósito, datos, preguntas numeradas con espacio, cierre |
| Lectura | Una columna, interlineado de 1.4–1.5, párrafos cortos, preguntas antes y después; nunca como imagen |
| Instrumentos de evaluación | Según [instrumentos](instrumentos-evaluacion.md); columnas de nivel de igual ancho y clave en un archivo aparte |
| Material para proyectar | 16:9, una idea por pantalla |

## 6. Construir
- Un HTML autocontenido por recurso, con su propio CSS. Usar React solo si conviene generar contenido repetitivo con datos.
- Guardar la fuente en `Recursos/fuente/` con nombre estable `NN-<nombre>` (NN = número de anexo, ver [estado del proyecto](estado-proyecto.md)) e imágenes con rutas relativas.
- Usar unidades físicas (`mm`, `pt`), `@page` para tamaño y márgenes, y `break-inside: avoid` en los bloques.
- En recursos de varias páginas, pensar la paginación desde el diseño (qué va en cada hoja), no solo al final.

## 7. Revisar y convertir a PDF
Cuando el recurso esté terminado:
1. Convertir con el navegador sin ventana y generar vistas previas (ver [herramientas](herramientas.md)).
2. Revisar las vistas previas página por página:
   - texto completo, sin cortes ni desbordes;
   - ortografía, cifras, unidades y respuestas;
   - legibilidad y contraste, también en blanco y negro;
   - número de páginas esperado;
   - imágenes nítidas;
   - nada partido entre páginas.
3. Corregir en la fuente y volver a convertir; nunca editar el PDF.
   - Si sobra poco para que quepa en la página: acortar textos, poner bloques lado a lado, reducir márgenes dentro del rango y compactar tablas sin bajar de los mínimos.
   - Si sobra mucho: dividir en hojas completas por sección. No dejar un bloque solo en una página; mover bloques enteros.
4. Entregar el PDF en `Recursos/NN-<nombre>.pdf` y usar la vista previa de la primera página en ANEXOS.

# Diseño de recursos

No hay recursos ni componentes prefabricados. Diseñar cada recurso para su actividad y su PDA, construirlo en HTML (o React) con su propio CSS y, al terminarlo, convertirlo a PDF.

## 1. Decidir antes de diseñar
| Necesidad | Decisión |
| --- | --- |
| Ya existe un material adecuado | Usarlo según [materiales existentes](materiales-existentes.md) |
| Texto exacto (fichas, hojas, instrumentos, tarjetas, guías, organizadores, lecturas) | Diseñar en HTML/React y convertir a PDF |
| Ilustración, escena, portada o portadilla | Generar la imagen (`openai_image`) e insertarla en el recurso HTML si lleva texto |
| Juego | [juegos didácticos](juegos-didacticos.md) |

No pedir texto largo dentro de imágenes generadas: sale con errores. El texto va en HTML y la imagen se inserta.

Para cada recurso fijar primero: propósito y PDA, quién lo usa (alumno, equipo, docente), momento de la sesión, cómo se usa (leer, escribir, recortar, proyectar, pegar en el cuaderno), número de páginas y si se imprime en blanco y negro.

## 2. Principios de layout
- **Página:** carta vertical por defecto (`@page { size: letter; margin: 15–18mm; }`). Usar horizontal solo para tablas anchas o láminas. Respetar el tamaño que pida el usuario.
- **Retícula:** 1 columna para lectura; 2 columnas para comparar o para tarjetas; malla regular para recortables. Alinear todo a la retícula y usar márgenes iguales.
- **Jerarquía en tres niveles como máximo:** título, subtítulo y cuerpo. El ojo debe ver primero qué es y qué hacer.
- **Orden de lectura:** encabezado (título, campo, grado, anexo) → datos del alumno → consigna → contenido → espacio de respuesta → créditos.
- **Espacio en blanco:** dejar aire alrededor de los bloques; no llenar la página. Espacio de respuesta proporcional a lo que se espera escribir (renglones de 8–9 mm).
- **Agrupar por proximidad:** lo relacionado junto y separado de lo demás; recuadros solo cuando ayuden a separar tareas.
- **Saltos de página:** sin tablas, reactivos ni figuras partidos (`break-inside: avoid`); en tablas largas, repetir el encabezado.
- **Una página, una función:** separar hoja del alumno, clave del docente y material para recortar.

## 3. Diseño visual
- **Tipografía:** sans serif legible y disponible sin internet (fuentes del sistema o incrustadas). Tamaños: cuerpo 11–12 pt, títulos 16–20 pt, tarjetas 18 pt o más, láminas para pared 28 pt o más. No usar texto de menos de 9 pt.
- **Color:** paleta sobria con 1 color de acento, 1–2 de apoyo y neutros. Contraste de texto de 4.5:1 como mínimo. Debe funcionar impreso en blanco y negro: no depender del color; usar también forma, texto o patrón.
- **Imágenes:** deben explicar, no decorar. Resolución suficiente para imprimir; pie con fuente o crédito. Ilustraciones generadas en estilo sobrio, animado y minimalista, coherente en todo el proyecto.
- **Íconos:** simples y consistentes (mismo grosor y estilo), siempre acompañados de texto.
- **Ciencias y matemáticas:** priorizar diagramas, tablas y relaciones; unidades y símbolos correctos; sin adornos.
- **Identidad del proyecto:** los recursos de un mismo campo comparten encabezado, paleta y estilo.
- **Accesibilidad:** texto real (no imágenes de texto), lenguaje claro, consignas cortas en infinitivo e instrucciones visibles en la misma página.

## 4. Qué lleva cada tipo de recurso
| Recurso | Estructura y reglas |
| --- | --- |
| Ficha informativa | Título, idea central destacada, 3–5 bloques breves con subtítulo, una figura o diagrama, glosario si hace falta, fuente |
| Hoja de trabajo | Encabezado, datos del alumno, consigna, ejercicios numerados de menor a mayor nivel de Bloom, espacio de respuesta suficiente |
| Lámina o infografía | Un mensaje principal, lectura en Z o en columnas, máximo 5–7 bloques, cifras grandes, íconos con texto |
| Organizador gráfico (mapa, cuadro comparativo, línea de tiempo, diagrama de Venn, causa-efecto) | Estructura vacía o semillena, espacio para escribir a mano, ejemplo de una casilla resuelto |
| Tarjetas (vocabulario, roles, preguntas, recortables) | Malla regular con líneas de corte, texto grande, anverso y reverso alineados si se imprimen por ambos lados |
| Guía de entrevista u observación | Propósito, datos de la persona o del lugar, preguntas numeradas con espacio, cierre y agradecimiento |
| Lectura | Texto maquetado a una columna, interlineado de 1.4–1.5, párrafos cortos, preguntas antes y después; nunca como imagen |
| Rúbrica, lista de cotejo, escala, examen | Seguir [instrumentos](instrumentos-evaluacion.md); tablas con encabezado claro, columnas de nivel de igual ancho, campos de registro vacíos; clave en archivo aparte |
| Material para proyectar | Formato 16:9, una idea por pantalla, letra de 32 px o más |

## 5. Construir
- Un archivo HTML autocontenido por recurso, o un `.tsx` si conviene generar partes con datos (tablas largas, tarjetas repetidas). CSS propio en el archivo o en un `.css` junto a él.
- Guardar la fuente en `Recursos/fuente/` con nombre estable `anexo-NN-nombre` e imágenes con rutas relativas.
- Usar unidades físicas (`mm`, `pt`) para impresión y `@page` para el tamaño.
- Sin recursos de internet: nada de fuentes, scripts ni imágenes remotas.
- Identificar «Elaboración propia con apoyo de IA» o «Adaptado de…» con su fuente.

## 6. Revisar y convertir a PDF
Cuando el recurso esté terminado:
1. Convertir con el [conversor](../assets/conversor-pdf/README.md): `bun convertir.tsx <recurso.html|.tsx> <Recursos/> --png`.
2. Abrir las vistas previas PNG y revisar página por página:
   - texto completo, sin cortes ni desbordes;
   - ortografía, cifras, unidades y respuestas;
   - legibilidad y contraste, también en blanco y negro;
   - número de páginas esperado;
   - imágenes nítidas;
   - nada partido entre páginas.
3. Corregir en la fuente y volver a convertir; nunca editar el PDF.
4. Entregar el PDF en `Recursos/` y usar el PNG de la primera página como vista previa en ANEXOS.

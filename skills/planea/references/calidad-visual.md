# Calidad visual de los recursos

Guía para que fichas, hojas, láminas, tarjetas, organizadores, instrumentos y pantallas de juego se vean **elaborados y profesionales** sin perder claridad. Público: alumnado de telesecundaria (12–15 años). Complementa [diseño de recursos](diseno-recursos.md), [estilos visuales](estilos-visuales.md) y [figuras](figuras-html.md); **no los sustituye**.

Regla de prioridad: el estándar obligatorio de [diseño de recursos](diseno-recursos.md) §3 (legibilidad, contraste ≥ 4.5:1, funciona en blanco y negro, márgenes ≥ 10 mm, nada partido entre páginas) manda sobre cualquier recurso decorativo de esta guía. Si un adorno estorba, se quita.

Regla transversal: inspirarse en **géneros y principios** (cómic, infografía, papel recortado, cartel), nunca copiar marcas, personajes, mascotas ni materiales con derechos. Los criterios marcados «(criterio de la skill)» son heurísticas propias, no resultados de investigación.

## 1. Principios con evidencia
Un recurso elaborado es uno donde cada elemento visual **hace trabajo**: dirige la mirada, agrupa, explica o motiva. El acabado viene de la coherencia y el cuidado, no de la cantidad.

| Principio | Qué hacer | Qué evitar | Fuente |
| --- | --- | --- | --- |
| **Imagen + palabra** | Acompañar el texto clave con una figura, diagrama o ilustración que explique | Páginas solo de texto, o imágenes que no explican | Mayer (2023): texto con ilustraciones superó al texto solo (d = 1.35, mediana de 13 comparaciones) |
| **Coherencia** | Quitar todo lo que no apoye el aprendizaje: íconos de relleno, datos curiosos ajenos, fondos recargados | «Detalles seductores» (anécdotas, imágenes llamativas pero irrelevantes) | Mayer (2023): 18 de 19 pruebas, d = 0.86; PhET (Adams, 2006): lo innecesario distrae y puede activar ideas erróneas |
| **Señalización** | Resaltar lo esencial con títulos, numeración, flechas, negritas y color de acento, **con moderación** | Resaltarlo todo; el efecto es mayor cuando las señales son escasas | Mayer (2023): 26 de 28 pruebas, d = 0.70 |
| **Contigüidad espacial** | Poner cada etiqueta, leyenda o explicación **pegada** a la parte de la figura que describe (línea guía corta) | Leyendas al pie o en una lista lejos del dibujo; claves de color en otra página | Mayer (2023): 9 de 9 pruebas, d = 0.82 |
| **Segmentación** | Dividir procesos largos en pasos o bloques cortos, uno por recuadro o por pantalla | Un bloque continuo de instrucciones | Mayer (2023): 7 de 7 pruebas, d = 0.67 (estudiado en lecciones con animación; aplicarlo al papel es una extrapolación razonable) |
| **Agrupar (Gestalt)** | Proximidad: lo relacionado va junto y lo distinto, separado por espacio. Similitud: mismo color/forma = misma categoría. Cierre: un recuadro o fondo suave agrupa sin necesidad de líneas | Espaciado uniforme que no agrupa nada; el mismo color para cosas distintas | Learning Guild, «Gestalt Your Graphics» |
| **Consistencia** | Un mismo objeto o concepto se dibuja igual y con el mismo color en todo el proyecto | Representar lo mismo de formas distintas: el alumnado lo percibe como cosas distintas | PhET (Adams, 2006) |
| **Diseño emocional** | Formas redondeadas y colores cálidos para generar emoción positiva; en adolescentes de 13–15 años el beneficio en aprendizaje apareció al combinar un diseño atractivo con interacción (hacer algo con el material) | Creer que solo «embellecer» sube el aprendizaje | Plass (2017) sobre Um et al. (2011); Shangguan et al. (2019) |

Carga cognitiva: el diseño debe reducir el esfuerzo que no enseña (leer una clave lejana, descifrar un orden, ignorar adornos) para dejar capacidad al contenido (Mayer, 2023). Aplicarlo así: **un mensaje principal por página o pantalla**, 3 niveles de jerarquía, texto breve.

## 2. Color
### 2.1 Estructura 60-30-10
- **60 % base neutra** (papel cálido o casi blanco): fondo de la hoja y de los espacios de escritura.
- **30 % color principal**: encabezados, recuadros de sección, bandas, fondos de tarjeta.
- **10 % acento**: lo que debe saltar a la vista (número de paso, insignia, la respuesta, la llamada, el botón).
- Fuente: Vision Australia; la regla es una proporción de partida, no una ley. Añadir **patrones o texturas** además del color ayuda a quien no distingue colores.

### 2.2 Derivar una paleta del tema
1. Elegir 1 imagen mental del tema (el mar, la semilla, una plaza, un circuito) y de ahí el **color principal**.
2. Acento = color **cálido y contrastante** con el principal (o su complementario), más saturado.
3. Neutros: papel con un matiz del principal (no blanco puro ni gris frío) y **tinta** casi negra con el mismo matiz (no negro puro).
4. Un color de apoyo opcional para una segunda categoría.
5. Total: ≤ 5 colores más neutros. Máximo 3 colores con significado en un mismo recurso (por ejemplo, tres niveles o tres categorías).
6. Guardar la paleta como variables CSS del proyecto y **no salir de ella**.
7. Color con significado: asignar un color por categoría y repetirlo en todos los recursos del proyecto (PhET, Adams, 2006: el alumnado espera consistencia del color). **Nunca** solo color: añadir forma, ícono, patrón o etiqueta (BBC GEL, infografías; NN/g).
8. Los neutros dominan y el color resalta: la paleta contenida hace que lo importante destaque (BBC GEL).
9. Registro por edad: la BBC varía tipografía, ilustración y color entre primaria y secundaria: más calmado y maduro para mayores (BBC GEL, Bitesize). Para 12–15 años: colores vivos pero con tinta oscura y menos «infantil» (sin tonos pastel azucarados ni mascotas de guardería).

### 2.3 Cuatro paletas de ejemplo (una por campo formativo)
Son punto de partida; adaptarlas al tema. Tinta = color del texto. Los rellenos de acento y apoyo **llevan contorno de tinta de 1.5–2 pt** para que se vean en blanco y negro y para separarlos del papel.

| Campo | Papel (60 %) | Tinta (texto) | Principal (30 %) | Claro (30 %) | Acento (10 %) | Apoyo |
| --- | --- | --- | --- | --- | --- | --- |
| Lenguajes | `#FFF8EE` | `#2B2133` | `#6B2D5C` ciruela | `#F6E3EE` | `#F26B3F` coral | `#FFC857` |
| Saberes y Pensamiento Científico | `#F3FAFB` | `#12313A` | `#0B6E8A` azul petróleo | `#D6F0F5` | `#FF8A1F` naranja | `#4FBF8B` |
| Ética, Naturaleza y Sociedades | `#FAF6EC` | `#2A2A1E` | `#2F6B3F` verde bosque | `#E3EEDC` | `#E07A5F` terracota | `#E0A526` |
| De lo Humano y lo Comunitario | `#FFF6F2` | `#2E2A3B` | `#A3235B` frambuesa | `#FBE3EC` | `#2DB6AC` turquesa | `#F7B731` |

Uso fijo: texto de cuerpo = tinta sobre papel o claro; encabezados = texto blanco sobre principal, o principal sobre papel/claro; **texto sobre acento o apoyo = siempre tinta, nunca blanco**; el acento y el apoyo no se usan como color de texto sobre papel.

### 2.4 Contraste calculado (WCAG 2.2, criterio 1.4.3: 4.5:1 para texto normal)
Calculado con la fórmula de luminancia relativa de WCAG con un script temporal. Todos los pares propuestos cumplen ≥ 4.5:1.

| Campo | Tinta/papel | Blanco/principal | Principal/papel | Tinta/claro | Principal/claro | Tinta/acento | Tinta/apoyo |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Lenguajes | 14.56 | 9.74 | 9.24 | 12.53 | 7.95 | 5.08 | 9.98 |
| Saberes | 13.03 | 5.81 | 5.50 | 11.56 | 4.88 | 5.84 | 6.00 |
| Ética | 13.43 | 6.37 | 5.90 | 12.10 | 5.32 | 4.91 | 6.61 |
| Humano | 13.05 | 7.12 | 6.69 | 11.45 | 5.87 | 5.56 | 7.79 |

Ajustes hechos al calcular: el coral, el terracota, el turquesa y el verde de apoyo iniciales **fallaban** con tinta (3.3–4.5) y se aclararon hasta pasar. Toda paleta nueva se calcula igual antes de usarla; el texto grande (≥ 18 pt o ≥ 14 pt en negrita) admite 3:1, pero en este estándar se exige 4.5:1 siempre.

Impresión: los fondos de color solo se imprimen si el CSS fuerza el color (`print-color-adjust: exact`); comprobarlo en la vista previa del PDF.

## 3. Formas y lenguaje visual
| Forma | Comunica | Usar para |
| --- | --- | --- |
| Círculo, óvalo, esquinas muy redondas | Suave, amable, accesible | Insignias, números de paso, personajes, botones, tarjetas de juego |
| Cuadrado, rectángulo | Sólido, confiable, estable | Estructura: recuadros de datos, tablas, instrumentos, organizadores |
| Triángulo, flecha, forma angulosa | Dinámico, dirección, alerta | Flechas de flujo, cintas, señales de «¡atención!», retos |

Fuente: Walt Disney Family Museum, «Shape Language». Matiz: las formas no significan una sola cosa y se pueden mezclar; demasiadas puntas restan claridad.

Sistema de formas coherente (criterio de la skill) — fijar al inicio del proyecto y repetir:
```css
:root{ --r-chico:2mm; --r-medio:4mm; --r-grande:7mm; --trazo:1.6pt; --tinta:#2B2133; }
.caja{ border:var(--trazo) solid var(--tinta); border-radius:var(--r-medio); }
```
- **Radios**: usar solo 2 o 3 valores (chico, medio, grande) en todo el recurso.
- **Contorno**: un solo grosor (1.5–2 pt) y un solo color (tinta). Sombra dura opcional (desplazada 1–1.5 mm, sin difuminar) en el 10 % de los elementos.
- **Figuras de acento**: 1 forma geométrica de apoyo (círculo, semicírculo, ola, hoja, estrella de 5 puntas) que se repite como motivo en encabezado, números e insignias.
- **Ritmo**: cajas de la misma familia comparten radio; los elementos de acento rompen el patrón a propósito y son pocos.
- Registro: campos humanos y comunitarios, redondeado cálido; campos científicos, más geométrico y angular; juegos, redondeado con sombra dura.

## 4. Ilustración
### 4.1 Estilos y cuándo elegir cada uno
| Estilo | Conviene para | Cuidado |
| --- | --- | --- |
| **Plano (flat)**, colores sólidos sin sombras | Casi todo; es el más fiable en impresión y fácil de mantener coherente | La forma debe leerse solo por la silueta |
| **Línea / monolínea** | Íconos, diagramas, procedimientos, hojas para colorear y completar | Grosor suficiente para el tamaño final |
| **Geométrico / modular** | Familias de figuras que «pertenecen» juntas, matemáticas, tecnología | Puede verse frío; calentar con color |
| **Silueta / papel recortado** | Láminas y carteles legibles a distancia; historia y tradición | Sin detalle interior; pocas capas |
| **Isométrico** | Mapas, planos, procesos, sitios y maquetas | Etiquetas en una leyenda numerada: el texto pequeño se pierde |
| **Cómic** (viñetas, globos) | Escenarios de conducta, ética, convivencia, lectura de situaciones | Escribir primero los diálogos y después dimensionar las viñetas |
| **Pictogramas (Isotype)** | Cantidades y proporciones | Decir qué representa un símbolo |

Fuentes: 4over4 (estilos que imprimen bien: plano, línea, geométrico, silueta y papel recortado); Hungry Minds (cuándo usar cada estilo en materiales de aprendizaje).

### 4.2 Mantener la coherencia
1. **Un estilo principal por proyecto**; uno secundario solo para un momento puntual (por ejemplo, un cómic dentro de un proyecto plano). Registrarlo en el diseño del proyecto (Hungry Minds).
2. Mismo grosor de línea, misma paleta, mismo nivel de detalle y mismas proporciones en todas las figuras.
3. Tono: demasiado simple se siente juguetón, demasiado detallado se siente real o serio; elegir según el público y el tema. Menos detalle cuanto más pequeña es la imagen (BBC GEL).
4. Pocos puntos de control en las curvas: formas limpias (BBC GEL).
5. Probar el estilo en **tres piezas** (una hoja, una tarjeta, una pantalla) antes de producir todo (Hungry Minds).
6. Evitar estereotipos de género, edad u origen en los personajes (SLI).

### 4.3 Combinar fuentes de imagen
| Fuente | Usar para | Regla |
| --- | --- | --- |
| **SVG propio** | Diagramas, figuras repetidas, insignias, marcos, patrones | Estilo base del proyecto; ver [figuras](figuras-html.md) |
| **Ilustración generada** | Portadas, portadillas, escenas, fondos | Sin texto dentro de la imagen; mismo estilo pedido en todas; insertarla como imagen y poner el texto en HTML |
| **Íconos de biblioteca** | Categorías, instrucciones, materiales | Una sola familia y grosor; ajustar color a la paleta ([figuras](figuras-html.md) §5) |

Si los tres orígenes no comparten estilo, unificarlos con el mismo recuadro, paleta y contorno, o usar solo uno.

## 5. Recursos de composición que dan acabado
Dosis: son límites de partida (criterio de la skill) para una **página carta**; reducir en piezas pequeñas.

| Recurso | Cómo usarlo | Dosis |
| --- | --- | --- |
| **Encabezado con motivo gráfico** | Banda de color principal con el título en blanco, una forma de acento o ilustración pequeña a un lado, número o campo en una insignia | 1 por página; ≤ 20 % de la altura |
| **Numeración grande de pasos** | Círculo o forma de acento con número en tinta (≥ 14 mm) y un título corto del paso; flecha entre pasos | 1 número por paso; 3–6 pasos |
| **Llamadas / globos** | Globo con pico hacia el elemento al que se refiere; para diálogos, pensamientos, «sabías que», dato clave | ≤ 3 por página; 1 sola idea cada una |
| **Diagramas etiquetados** | Figura central grande, etiquetas **pegadas** a la parte (línea guía corta, sin cruzarse), numeración si hay leyenda | Etiqueta ≥ 9 pt; ≤ 8 etiquetas |
| **Viñetas de cómic** | Cuadros con contorno, globos de texto grande, un personaje propio del tema | 3–6 viñetas; sin personajes con derechos |
| **Insignias y sellos** | Círculo o escudo con ícono para nivel, logro, tipo de actividad, «reto» | ≤ 3 por página; mismas formas en todo el proyecto |
| **Cintas y banners** | Para títulos de sección o etiquetas especiales | ≤ 1–2 por página |
| **Fondos con patrón sutil** | Puntos, rayas, ondas o cuadrícula en un tono del claro, solo en bandas o márgenes, nunca detrás del texto | Patrón de contraste ≤ 10 % respecto del fondo; ≤ 30 % de la superficie |
| **Texturas** (papel, grano) | Solo como capa suave en el fondo; si hay riesgo de impresión, usar color plano | Opacidad ≤ 8 %; evitarlas si son imágenes pesadas |
| **Marcos y bordes** | Marco doble o con esquinas decoradas en láminas, diplomas, tarjetas | 1 marco por pieza; no dentro de otro marco |
| **Íconos con texto** | Ícono junto a la palabra o instrucción que ilustra | ≥ 15 mm si son aislados; misma familia |
| **Espacio en blanco** | Usarlo para agrupar y guiar el recorrido de lectura (SLI) | ≥ 25 % de la página sin elementos |

Reglas de uso:
- **Nada decorativo detrás o encima del texto**: no usar fondos de patrón o foto con alto contraste bajo el texto (SLI).
- Cada recurso decorativo debe tener una **función** (guiar, agrupar, motivar). Si solo adorna, quitarlo (NN/g; SLI).
- Lo decorativo no invade el espacio de respuesta.

## 6. Recetas por tipo de recurso
Cada receta es un conjunto de elementos y su composición; adaptar la paleta y el estilo del proyecto.

| Recurso | Receta elaborada |
| --- | --- |
| **Ficha informativa** | Encabezado con banda principal e insignia del campo; frase central en un globo grande; 3–5 bloques con subtítulo y un ícono; figura etiquetada junto al bloque que explica; recuadro «Dato clave» con acento; glosario al pie en caja clara |
| **Hoja de trabajo** | Encabezado compacto; ejercicios con **número grande en círculo de acento**; insignia de nivel (●, ●●, ●●●) para Bloom; renglones o cuadros de respuesta con borde redondeado suave; una ilustración pequeña por sección; casilla de autoevaluación al final |
| **Lámina / infografía** | Un mensaje en título grande; figura central grande; 5–7 bloques alrededor con etiquetas pegadas; cifras gigantes en acento; flechas que marcan el recorrido; fondo plano con patrón sutil en bandas; leyenda de íconos |
| **Tarjetas** | Marco de la misma familia en todas; color de borde o banda según categoría **más** ícono y nombre; ilustración o ícono grande arriba; texto ≥ 18 pt; esquina con número o insignia; reverso con patrón del proyecto y línea de corte |
| **Organizador gráfico** | Estructura con formas de una sola familia (cajas redondeadas y flechas); casilla resuelta como ejemplo en acento; colores por categoría con símbolo; espacio generoso de escritura; título central en cinta |
| **Instrumento de evaluación** | Estilo sobrio: rectángulos y tabla limpia; encabezados de nivel con forma distinta además del color (●, ▲, ■); banda principal; íconos de nivel; sin ilustración dentro de la tabla; columnas de igual ancho |
| **Pantalla de juego (proyectada)** | Fondo plano, 3 niveles de jerarquía; pregunta y opciones muy grandes en tarjetas de formas redondeadas con contorno y sombra dura; **color + símbolo** por opción (●, ▲, ■, ◆); insignias de puntaje; retroalimentación con ícono y color; mínimos de [diseño de recursos](diseno-recursos.md) §3 |
| **Lectura** | Una columna; título con capitular o motivo; sin patrón de fondo; imágenes con pie; recuadros de «Antes de leer» y «Después de leer» con ícono |
| **Guía de entrevista / observación** | Encabezado con ícono de la actividad; preguntas numeradas en círculos; espacio para escribir en caja con borde suave; recuadro de «Consejos» con globo |

## 7. Básico vs. elaborado
| Básico | Elaborado |
| --- | --- |
| Texto negro sobre blanco, títulos solo en negrita | Paleta del tema con 60-30-10; encabezado con motivo |
| Lista de instrucciones | Pasos con números grandes, ícono y flecha |
| Figura suelta con leyenda abajo | Figura con etiquetas pegadas y línea guía |
| Muchos tamaños y colores sin orden | 3 niveles de jerarquía y radios coherentes |
| Clip art mezclado | Un solo estilo, una sola familia de íconos |
| Cuadros sin diseño | Recuadros con radio, contorno y color de la familia |
| Color como única señal | Color + forma + etiqueta |

Señales de **exceso o ruido** (si aparece una, simplificar):
- más de 5 colores con significado o más de 2 tipografías;
- ≥ 3 estilos de ilustración, mezcla de íconos de línea y planos, o cualquier emoji;
- patrones, texturas o sombras difusas que compiten con el texto;
- más de 3 globos, insignias o cintas por página; marcos dentro de marcos;
- degradados, filtros o transparencias complejas (se rasterizan y se imprimen peor; 4over4);
- ilustración más grande o llamativa que el dato que explica (NN/g);
- no se distingue la jerarquía al entrecerrar los ojos, o la hoja pierde información en blanco y negro;
- texto o elementos pegados al borde; bloques partidos.

## 8. Fuentes consultadas (fecha de consulta: 23/11/2026)
Todas leídas antes de citarlas; las afirmaciones sin cita son criterio de la skill.

- Mayer, R. E. (2023). *Research-Based Principles for Designing Multimedia Instruction* (capítulo, desde p. 143; American Psychological Association, 2023; PDF alojado por University of New Hampshire). https://www.unh.edu/teaching-learning-resource-hub/sites/default/files/media/2023-06/itow-research-based-principles-for-designing-multimedia-instruction-mayer.pdf
- Mayer, R. E. (2024). *The Past, Present, and Future of the Cognitive Theory of Multimedia Learning*. Educational Psychology Review. https://link.springer.com/article/10.1007/s10648-023-09842-1
- University of Washington School of Medicine, Analytics & Learning Technologies. *Principles for Teaching With Multimedia* (resumen de los principios de Mayer). https://sites.uw.edu/somlearningtech/principles-for-teaching-with-multimedia/
- Learning Guild. *Gestalt Your Graphics: Improving Instructional Graphics* (autoría no indicada en la página consultada). https://www.learningguild.com/articles/157/gestalt-your-graphics-improving-instructional-graphics/
- Adams, W. (2006). *PhET Look and Feel*. PhET Interactive Simulations, University of Colorado Boulder. https://phet.colorado.edu/publications/PhET%20Look%20and%20Feel.pdf
- Plass, J. L. (2017). *What do Emotions have to do with Learning?* Gedankenspiele. http://janplass.com/index.php/2017/03/21/emotional-design-learning/
- Shangguan, C., Wang, Z., Gong, S. et al. (2020). *More Attractive or More Interactive? The Effects of Multi-Leveled Emotional Design on Middle School Students’ Multimedia Learning*. Frontiers in Psychology. https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2019.03065/full (solo el resumen y la introducción fueron leídos con detalle)
- BBC GEL. *How to design infographics*. https://www.bbc.co.uk/gel/features/how-to-design-infographics
- BBC GEL. *Rebranding BBC Bitesize: How to keep your cool as a UX designer*. https://www.bbc.co.uk/gel/features/rebranding-bbc-bitesize
- Nielsen Norman Group, Kane, L. (2018). *Designing Effective Infographics*. https://www.nngroup.com/articles/designing-effective-infographics/
- Science Literacy Infographics (SLI). *Infographic Style Guide*. http://science-infographics.org/revising-critiquing/infographic-style-guide/
- Vision Australia. *Creating accessible digital colour palettes using the 60-30-10 design rule*. https://www.visionaustralia.org/business-consulting/digital-access/Creating-accessible-digital-colour-palettes-60-30-10-design-rule
- W3C WAI. *Understanding Success Criterion 1.4.3: Contrast (Minimum)* (WCAG 2.2). https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum
- The Walt Disney Family Museum. *Shape Language* (Tales & Tools). https://www.waltdisney.org/sites/default/files/2020-04/T&T_ShapeLang_v9.pdf
- 4over4. *10 Vector Illustration Styles That Print Sharp at Any Size*. https://www.4over4.com/article/vector-illustration-styles-for-print-design
- Hungry Minds, Peart, M. *Design styles for learning: 52 looks*. https://hungryminds.com.au/resources/visual-design-for-learning/design-styles-for-learning/

No se pudieron leer (y por tanto no se citan): el PDF «12 Principles of Multimedia» (NYU) y la página de Gestalt de tcbok.org. No se encontró en las búsquedas una guía de diseño visual publicada de Oak National Academy, OpenStax, Khan Academy ni de los libros de texto de la SEP que se pudiera leer y citar; no se atribuye nada a ellas.

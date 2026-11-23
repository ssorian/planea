# Estructura de la planeación

Estructura de referencia de una planeación terminada. Si el usuario da otra planeación modelo, seguir esa y señalar las diferencias. Ejemplo trabajado de filas y celdas: [ejemplo de campo](../assets/ejemplo-campo.md).

Este archivo es la fuente única de las reglas de referencias a anexos, texto sin rojo, ANEXOS 2×2 sin bordes y numeración continua.

## Orden del documento
1. Portada → presentación y contextos (áulico, escolar, comunitario) → lista de asistencia.
2. Por cada campo formativo, en este orden:
   1. **Portadilla:** campo, nombre del proyecto, imagen, grado, fechas y docente en formación.
   2. **Contenido científico:** 1–2 páginas, organizadas por rangos de sesiones («Fundamento disciplinar para las sesiones 1 a 4»), con fuentes para el docente al final.
   3. **Tablas del proyecto:** T1 ficha, T2 proyecto parcial de aula, T3 proyecto académico, T4 momento 4, T5 sugerencias y recursos.
3. **ANEXOS de todos los campos**, juntos al final, después del último campo.
4. Hoja de firmas.

## Qué se hace en cada tabla
Leyenda: **Conservar** = texto del RAIPA sin cambios · **Llenar** = dato confirmado por el usuario · **Rediseñar** = contenido propio según el diseño aprobado.

### T1 Ficha
| Campo | Acción |
| --- | --- |
| Campo formativo, disciplinas, contenido integrado, subcontenidos, ejes articuladores | Conservar |
| Escuela, CCT, docentes (practicante y titular), turno, grado, grupo | Llenar |
| Duración | Llenar: «N sesiones de X minutos · semanas, horas» |
| Fecha | Llenar: rango de la jornada |
| Proyectos de aula, escuela y comunidad | Rediseñar: cómo se vincula el proyecto en cada nivel |

### T2 Proyecto parcial de aula
| Campo | Acción |
| --- | --- |
| Título del PPA | Conservar |
| Momento 1: vinculación con otros campos | Conservar; señalar las vinculaciones que no encajan |
| Momento 1: estrategias nacionales | Rediseñar: cómo se aplican en este grupo |
| Momento 2: INSUMOS | Rediseñar: organización del grupo, materiales, espacios y equipos |
| Momento 2: CRONOGRAMA | Rediseñar como **tabla Word nativa y editable** dentro de la celda: sesión, fecha, etapa, actividad principal, producto, anexos |
| Momento 2: AJUSTES RAZONABLES | Rediseñar: medidas concretas (solo con información confirmada del grupo) |

### T3 Proyecto académico (Momento 3)
La tabla crece: el RAIPA trae una fila por etapa; la planeación agrega filas para sesiones y fuentes.

| Fila o etapa | Acción |
| --- | --- |
| Encabezado: FECHA | Llenar: rango de la jornada |
| Título del proyecto académico, contenidos por disciplina | Conservar |
| 1. ¿Qué haremos?: intención, verbos, estrategia detonadora | Conservar |
| 2. ¡Ese es el problema!: situaciones 1 y 2 | Rediseñar (adaptarlas al grupo) |
| 2. PDA | Conservar el texto completo; puede moverse a una fila propia «PDA del proyecto» |
| 3. ¡Una propuesta de solución!: objetivos | Conservar |
| **4. Paso a paso** | Rediseñar: una fila de organización general + **una fila por sesión** (ver abajo) |
| **5. Distintas fuentes de consulta** | Rediseñar: una fila de criterio general + **una fila por fuente** (referencia y URL a la izquierda; uso, sesión y anexo a la derecha) |
| 6. Unimos las piezas y 7. ¡Ya lo tenemos! | Rediseñar (pueden unirse): proceso por sesión; **productos parciales y producto definitivo** a la derecha |

### T4 Momento 4 (integración)
Reemplazar los ejercicios del RAIPA por la integración propia del diseño (cómo se consolidan los aprendizajes en el producto final).

### T5 Sugerencias y recursos
Reemplazar las sugerencias del RAIPA por sugerencias propias para el docente (preparación, materiales, riesgos) y la bibliografía por **«RECURSOS POR SESIÓN»**: sesión → anexos y materiales.

## Fila de sesión (T3, etapa 4)
| Columna de actividades | Columna derecha |
| --- | --- |
| **Fecha: 5 de octubre de 2026 · SESIÓN 1 · Título** | **PRODUCTO** — lo que entrega la sesión |
| **Inicio.** … | **RECURSOS** — `(Anexo N): Tipo Título`, uno por línea, y materiales físicos |
| **Desarrollo.** … | **PDA:** claves trabajadas |
| **Cierre.** … | |

- Cada recurso se cita **en el lugar exacto de la actividad que lo usa**, con referencia directa y el anexo en negrita:
  - «Se procederá a jugar un minijuego de repaso (**Anexo 2**).»
  - «Se verá el video ¿Qué es identidad? (**Anexo 7**).»
  - «Se leerá el apartado Identidad cultural (**Anexo 3**) por turnos.»
- **Sin texto en rojo.** Solo «Anexo N» va en negrita; el resto, con el formato del párrafo.
- Indicar el tiempo de cada momento cuando el diseño lo fije.

## Anexos
- **Numeración continua entre campos:** si Lenguajes termina en el Anexo 16, el siguiente campo empieza en el 17.
- **Un mismo material conserva su número** aunque se use en varias sesiones o campos. El número se asigna una sola vez en `planea/materiales.csv` ([estado del proyecto](estado-proyecto.md)).
- **Formato:** hojas tituladas «ANEXOS» con una tabla de **2×2 sin bordes visibles** (4 anexos por hoja); la última hoja puede quedar incompleta, con las celdas sobrantes vacías.
- **Cada celda contiene solo:**
  1. el título en negrita: «**Anexo N** Tipo Título»;
  2. la vista previa real del recurso (primera página, captura o imagen);
  3. **si es video:** su carátula (miniatura real del video) y, debajo, la URL completa y clicable.
- **Sin instrucciones, créditos ni descripciones** en la celda: el uso va en la sesión, y la fuente y el crédito en la etapa 5 de T3.
- **Cadena verificable:** sesión → (**Anexo N**) → celda de ANEXOS → archivo en `Recursos/`.

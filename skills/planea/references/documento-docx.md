# Documento DOCX

## Estructura de la planeación
Seguir el orden y el formato de la planeación modelo indicada por el usuario. Estructura habitual:
1. Portada (datos confirmados de escuela, grupo, jornada y docente en formación; debe caber en una hoja).
2. Presentación y contextos (escolar, comunitario, áulico).
3. Lista de asistencia.
4. Por cada campo formativo:
   - Portadilla: nombre del proyecto, imagen, grado, fechas y docente en formación.
   - Contenido científico: fundamento disciplinar y fuentes del docente.
   - Tablas del proyecto (ficha, PPA, desarrollo de actividades por etapa, integración, sugerencias y recursos) con FECHA y CRONOGRAMA llenos y las sesiones diseñadas.
   - ANEXOS del campo.
5. Hoja de firmas.

Insertar las secciones de campo en la posición indicada por el usuario o por `AGENTS.md`. Copiar las tablas del RAIPA conservando la redacción de contenidos y PDA; reescribir o reemplazar actividades según el diseño aprobado.

## Edición técnica
Seguir las reglas de DOCX de [herramientas](herramientas.md): leer poco, editar en una copia, preservar el formato a nivel de run, no cambiar la estructura de las tablas, copiar estilos y numeración junto con el contenido y mantener IDs únicos.

## Consignas y formato
- Consignas para el alumnado en infinitivo, de 1–3 frases, en rojo `#C00000`, con el número de anexo en negrita, junto a la actividad que las usa.
- Heredar la fuente efectiva del párrafo vecino; no imponer tamaños globales.
- CRONOGRAMA como tabla Word nativa y editable dentro de su celda: sesión, fecha, etapa/actividad, tiempo, recursos/anexos, evidencia.

## Verificación del documento
- Reabrir con una biblioteca distinta de la que editó (por ejemplo, python-docx y `zipfile`) y parsear todas las partes XML.
- Comparar antes y después: tablas, filas, celdas, secciones e imágenes; contenidos y PDA idénticos al RAIPA.
- Toda relación apunta a un archivo existente; sin medios huérfanos; IDs únicos (comparados con el original).
- Renderizar si hay LibreOffice; si no, declarar que la revisión visual la hace el usuario en Word.

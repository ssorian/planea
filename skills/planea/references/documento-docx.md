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
- Comprobar herramientas con `command -v` o importación de Python. Preferir python-docx cuando esté instalado.
- Sin python-docx: usar `zipfile` de la biblioteca estándar y empalmar hijos del body como texto; no reescribir `document.xml` con ElementTree (renombra prefijos y rompe `mc:Ignorable`).
- Conservar relaciones, tipos de contenido, estilos, numeración, encabezados, pies y secciones. Al copiar imágenes, agregar su relación y su entrada en `[Content_Types].xml`.
- Mantener únicos `w14:paraId`, `w14:textId`, ids de dibujos (`wp:docPr id`) y marcadores.
- Al borrar contenido, retirar medios huérfanos.
- Trabajar sobre la entrega acordada; no sobrescribir originales ni archivos de referencia. Si existe un archivo de bloqueo de Word/LibreOffice, pedir cerrar el documento antes de escribir.

## Consignas y formato
- Consignas para el alumnado en infinitivo, de 1–3 frases, en rojo `#C00000`, con el número de anexo en negrita, junto a la actividad que las usa.
- Heredar la fuente efectiva del párrafo vecino; no imponer tamaños globales.
- CRONOGRAMA como tabla Word nativa y editable dentro de su celda: sesión, fecha, etapa/actividad, tiempo, recursos/anexos, evidencia.

## Verificación del documento
- Reabrir el ZIP y parsear todas las partes XML.
- Contar tablas, secciones e imágenes antes y después; comprobar que contenidos y PDA coinciden con el RAIPA.
- Comprobar unicidad de paraId e ids de dibujos y que toda relación apunte a un archivo existente.
- Renderizar si hay renderizador; si no, declarar que la revisión visual la hace el usuario en Word.

## Herramienta docx_tool
Script de la skill: `~/.pi/agent/skills/planea/assets/herramientas-docx/docx_tool.py` (solo biblioteca estándar; referencia de comandos en `assets/herramientas-docx/README.md`).
- Linux/macOS: `python3 -I ~/.pi/agent/skills/planea/assets/herramientas-docx/docx_tool.py <comando> archivo.docx ...`
- Windows: `py -I docx_tool.py <comando> ...` o `python -I docx_tool.py <comando> ...` (desde la carpeta del script o con su ruta completa).

Reglas para el agente:
1. Mapear primero: `info`, luego `mapa` (hijos del body) y `tablas --tabla N` (celdas). No abrir el XML ni leer el DOCX completo en el contexto.
2. Leer solo lo necesario: `texto --desde N --hasta M` o `buscar "patrón"` para localizar; usar `--ancho` solo si el truncado impide decidir.
3. Editar por coordenadas: `editar-celdas cambios.json -o salida.docx` (`T2F3C1`, anidadas `T2F3C1.T0F0C0`) o `reemplazar` para textos dentro de un run. Reutilizar tablas con `copiar origen.docx --desde --hasta --antes` (incluye imágenes y relaciones); no insertar XML crudo con `r:embed`.
4. Escribir siempre a un archivo nuevo con `-o`; nunca usar `--sobrescribir` sobre la entrega acordada ni sobre el RAIPA o la planeación modelo.
5. Después de cada edición: `verificar salida.docx` (comparar con el `verificar` del original: los duplicados preexistentes no son fallos propios) y `comparar original.docx salida.docx` (tras editar texto debe dar SIN DIFERENCIAS; tras copiar o borrar, las diferencias esperadas deben coincidir con lo hecho).
6. `copiar` también copia estilos y numeraciones que falten (renumera `numId`/`abstractNumId`) y conserva los estilos del destino con el mismo `styleId`; revisar su línea resumen (`numeraciones`, `estilos copiados`, `estilos coincidentes conservados`). La revisión visual la hace el usuario en Word.

# Documento DOCX

## Estructura de la planeación
Seguir [estructura de la planeación](estructura-planeacion.md): orden del documento, qué se conserva, llena o rediseña en cada tabla, filas de sesión y formato de ANEXOS. Insertar las secciones de campo en la posición indicada por el usuario o por `AGENTS.md`.

## Edición técnica
Seguir las reglas de DOCX de [herramientas](herramientas.md): leer poco, editar en una copia, preservar el formato a nivel de run, no cambiar la estructura de las tablas, copiar estilos y numeración junto con el contenido y mantener IDs únicos.

## Referencias y formato
- Citar cada recurso en la actividad que lo usa, con referencia directa y el anexo en negrita: «Se verá el video … (**Anexo 7**)». Sin texto en rojo.
- Heredar la fuente efectiva del párrafo vecino; no imponer tamaños globales.
- CRONOGRAMA como tabla Word nativa y editable dentro de su celda.
- ANEXOS: tablas 2×2 sin bordes visibles (bordes `nil`), numeración continua entre campos.

## Verificación del documento
- Reabrir con una biblioteca distinta de la que editó (por ejemplo, python-docx y `zipfile`) y parsear todas las partes XML.
- Comparar antes y después: tablas, filas, celdas, secciones e imágenes; contenidos y PDA idénticos al RAIPA.
- Toda relación apunta a un archivo existente; sin medios huérfanos; IDs únicos (comparados con el original).
- Renderizar si hay LibreOffice; si no, declarar que la revisión visual la hace el usuario en Word.

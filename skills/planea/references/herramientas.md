# Herramientas

La skill trae sus herramientas en `assets/herramientas/` (ver [README](../assets/herramientas/README.md) para la sintaxis completa). Solo usan la biblioteca estándar de Python 3.9+, salvo `pdf_vista.py`. Invocar siempre con `-I`: `python3 -I <skill>/assets/herramientas/<script>.py …` (Windows: `py -I` o `python -I`). Comprobar antes qué hay: `command -v python3 uv`.

## Tarea → comando
`D="python3 -I <skill>/assets/herramientas/docx_tool.py"`

| Tarea | Comando |
| --- | --- |
| Resumen del DOCX | `$D info a.docx` |
| Mapear estructura (pocos tokens) | `$D mapa a.docx --solo-tablas`; `$D tablas a.docx --tabla N --filas A-B` |
| Leer celdas, texto o buscar | `$D leer-celdas a.docx T3F16C2` · `$D texto a.docx --desde B` · `$D buscar a.docx "patrón"` |
| Editar celdas (con `**negrita**`) | `$D editar-celdas a.docx cambios.json -o b.docx`; `$D reemplazar …` |
| Copiar tablas o bloques entre DOCX | `$D copiar destino.docx origen.docx --desde B --hasta B --antes B -o s.docx` |
| Filas de sesión | `$D duplicar-fila …`, `$D borrar-filas …`, `$D vmerge …` |
| Cronograma nativo | `$D tabla-en-celda a.docx T2F4C3 datos.json -o b.docx` |
| Hojas de ANEXOS | `$D anexos a.docx anexos.json --antes B -o b.docx` |
| Comprobar texto intocable | `$D conservado destino.docx origen.docx --celdas …` |
| Integridad y diferencias | `$D verificar a.docx` · `$D comparar a.docx b.docx` |
| Revisión visual del DOCX | `$D render a.docx --dir DIR` (código 3: sin renderizador) |
| Recurso HTML → PDF | `python3 -I …/html_a_pdf.py recurso.html salida.pdf` (Edge, Chrome o Chromium del sistema; código 3 si no hay) |
| Vista previa y páginas de un PDF | `uv run …/pdf_vista.py archivo.pdf --dir DIR` (PyMuPDF); sin uv, Poppler con `python3 -I …/pdf_vista.py` |
| Ilustraciones | Generación de imágenes del agente, o materiales existentes con licencia |
| Investigación | Búsqueda web y lectura de páginas; solo fuentes locales si no hay red |

## Alternativas (solo si hacen falta, con permiso para descargar)
- `markitdown`, `pandoc` o `python-docx` (`uvx` / `uv run --with`) para lo que `docx_tool.py` no cubra.
- Playwright (`uv run --with playwright`) si no hay navegador del sistema o hace falta capturar un juego.
- **Juego proyectado:** HTML único por defecto. Vite + React solo si el juego lo necesita y con permiso; requiere Node.js.

## Reglas para DOCX
- **Copia de trabajo** en `planea/trabajo/`; salida en `salida/`. Nunca sobrescribir originales ni la planeación modelo.
- Si hay archivo de bloqueo (`.~lock.*#`, `~$*`), pedir cerrar el documento.
- **No cambiar la estructura** al editar contenido, salvo con los comandos de filas y tablas; confirmar con `comparar`.
- **IDs únicos:** `verificar` los revisa; comparar con el original, que puede traer duplicados propios.
- Sin renderizador (`render` devuelve 3): la revisión visual queda pendiente para el usuario en Word.

## Reglas para PDF
- Convertir solo recursos terminados; corregir en la fuente y volver a convertir; nunca editar el PDF.
- Revisar las vistas previas página por página ([diseño de recursos](diseno-recursos.md)).
- Recursos sin dependencias de red: fuentes del sistema o incrustadas e imágenes locales.

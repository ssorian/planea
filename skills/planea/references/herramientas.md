# Herramientas

La skill no trae código. Solo se necesitan **Node.js** (`npx`) y **uv** (`uvx`, `uv run --with`): con ellos se ejecuta al momento todo lo demás, sin instalaciones globales. Antes de usar una herramienta, comprobar qué hay (`command -v node uv`). La primera ejecución descarga paquetes (y Playwright descarga su Chromium con `uvx playwright install chromium`): pedir permiso si el entorno o el usuario lo exigen. Escribir los scripts auxiliares en una carpeta temporal o en `Recursos/fuente/`, nunca dentro de la skill.

## Elegir la herramienta
| Tarea | Comando o herramienta (vía uv o Node) | Alternativa si ya existe en el equipo |
| --- | --- | --- |
| Leer un DOCX con pocos tokens | `uvx --from 'markitdown[docx]' markitdown archivo.docx` (Markdown con tablas) | `pandoc -t markdown` |
| Mapear tablas y celdas | Script con python-docx (`uv run --with python-docx python mapa.py`): una línea por celda única (`T2 F3 C1 "texto…"`) | `zipfile` + lectura de XML |
| Editar texto, celdas y tablas | python-docx: `uv run --with python-docx python script.py` | lxml para lo que python-docx no cubre (`--with lxml`) |
| Copiar tablas o secciones entre documentos (con estilos, numeración e imágenes) | docxcompose: `uv run --with docxcompose python script.py` | python-docx + copia manual de relaciones, estilos y numeración |
| Validar un DOCX | Reabrir con python-docx y con `zipfile`; comparar conteos antes y después | LibreOffice (`soffice --headless --convert-to pdf`) para renderizar |
| Recurso HTML → PDF | Playwright con uv: `uv run --with playwright python a_pdf.py`, con `page.pdf(path=…, prefer_css_page_size=True, print_background=True)` | Chromium, Chrome o Edge del sistema: `--headless --no-pdf-header-footer --print-to-pdf=salida.pdf recurso.html`; o `npx playwright pdf` (usa `--paper-format`, no el `@page`) |
| Recurso React → PDF | Renderizar a HTML estático con `react-dom/server` (`npx tsx render.tsx`, con React instalado en `Recursos/fuente/`) y convertir el HTML | Construir con Vite y convertir el resultado |
| Vista previa y conteo de páginas | PyMuPDF: `uv run --with pymupdf python vista.py` (`page.get_pixmap(dpi=110).save(…)`, `len(doc)`) | Poppler: `pdftoppm -png -r 110` y `pdfinfo` |
| Captura de un juego o una pantalla | Playwright: `page.screenshot(path=…)` en cada estado | `npx playwright screenshot <url> captura.png` |
| Juego proyectado | `npm create vite@latest <nombre> -- --template react-ts`, `vite-plugin-singlefile` y `npx vite build` | HTML único escrito a mano |
| Ilustraciones | Generación de imágenes del agente (`openai_image` u otra) | Materiales existentes con licencia |
| Investigación | Búsqueda web y lectura de páginas del agente | Solo fuentes locales si no hay red |

En Windows: `uv run` y `npx` funcionan igual. Para scripts Python, `uv run` elige el intérprete; no hace falta `py` ni `python3`.

## Reglas para DOCX
- **Leer poco:** mapear primero la estructura y luego leer solo los rangos necesarios. No volcar el XML ni el documento completo al contexto.
- **Editar en una copia;** nunca sobrescribir originales ni la planeación modelo. Si hay un archivo de bloqueo (`.~lock.*#`, `~$*`), pedir cerrar el documento.
- **Preservar el formato a nivel de run:** escribir en el primer run de cada párrafo y vaciar los demás; no usar `cell.text = …` cuando el formato importa.
- **Celdas combinadas:** deduplicarlas por identidad (`cell._tc`); python-docx devuelve la misma celda varias veces.
- **No cambiar la estructura** al editar contenido: filas, columnas, `gridSpan`, `vMerge`, anchos y bordes. Comparar los conteos antes y después.
- **Copiar entre documentos:** usar docxcompose o copiar también las relaciones (imágenes, enlaces), los estilos que falten y las definiciones de numeración (`w:num` + `w:abstractNum`, con IDs nuevos sin colisión). Sin numeración, las listas copiadas se rompen.
- **IDs únicos:** `w14:paraId`, `w14:textId`, `wp:docPr@id` y marcadores. Comparar con el original, que puede traer duplicados propios.
- **Sin bibliotecas:** si no hay python-docx ni red, usar `zipfile` y empalmar texto sobre `word/document.xml`. No reserializar con ElementTree: renombra prefijos y rompe `mc:Ignorable`.
- **Revisión visual:** sin renderizador, declararla pendiente para el usuario en Word.

## Reglas para PDF
- Convertir solo recursos terminados; corregir en la fuente y volver a convertir; nunca editar el PDF.
- Revisar siempre las vistas previas página por página (ver [diseño de recursos](diseno-recursos.md)).
- Recursos sin dependencias de red: fuentes del sistema o incrustadas e imágenes locales.

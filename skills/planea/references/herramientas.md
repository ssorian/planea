# Herramientas

La skill no trae código. Usar herramientas existentes, de preferencia ejecutadas al momento sin instalación global (`uvx`, `uv run --with`, `npx`, `bunx`). Antes de usar una, comprobar que está disponible (`command -v`, importación). La primera ejecución descarga paquetes: pedir permiso si el entorno o el usuario lo exigen. Escribir los scripts auxiliares en una carpeta temporal o en `Recursos/fuente/`, nunca dentro de la skill.

## Elegir la herramienta
| Tarea | Primera opción | Alternativas |
| --- | --- | --- |
| Leer un DOCX con pocos tokens | `uvx --from 'markitdown[docx]' markitdown archivo.docx` (Markdown con tablas) | Script con python-docx que imprima un mapa compacto; `pandoc -t markdown` si está instalado |
| Mapear tablas y celdas | Script con python-docx: una línea por celda única (`T2 F3 C1 "texto…"`) | `zipfile` + lectura de XML |
| Editar texto, celdas y tablas | python-docx: `uv run --with python-docx python script.py` | lxml para lo que python-docx no cubre |
| Copiar tablas o secciones entre documentos (con estilos, numeración e imágenes) | docxcompose: `uv run --with docxcompose python script.py` | python-docx + copia manual de relaciones, estilos y numeración |
| Validar un DOCX | Reabrir con python-docx y con `zipfile`; comparar conteos antes y después | `soffice --headless --convert-to pdf` para renderizar, si hay LibreOffice |
| Recurso HTML → PDF | Chromium, Chrome o Edge sin ventana: `chromium --headless --no-pdf-header-footer --print-to-pdf=salida.pdf recurso.html` | `npx playwright pdf file:///ruta/recurso.html salida.pdf` |
| Recurso React → PDF | Renderizar a HTML estático (`react-dom/server`, `bunx`/`bun` en `Recursos/fuente/`) y convertir el HTML | Construir con Vite y convertir el HTML resultante |
| Vista previa y conteo de páginas | `pdftoppm -png -r 110 salida.pdf vista` y `pdfinfo salida.pdf` (Poppler) | Captura del navegador: `chromium --headless --screenshot=vista.png --window-size=850,1100 recurso.html` |
| Juego proyectado | `bunx create-vite@latest <nombre> --template react-ts` + `vite-plugin-singlefile` | HTML único escrito a mano |
| Ilustraciones | `openai_image` (u otra herramienta de imágenes del agente) | Materiales existentes con licencia |
| Investigación | Búsqueda web y lectura de páginas del agente | Solo fuentes locales si no hay red |

En Windows: `py` o `python` en lugar de `python3`; el navegador suele ser `msedge.exe` (Edge viene instalado). En macOS: `/Applications/Google Chrome.app/Contents/MacOS/Google Chrome`.

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

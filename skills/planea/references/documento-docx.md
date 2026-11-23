# Documento DOCX

Reglas de formato (orden, tablas, fila de sesión, referencias a anexos, sin rojo, ANEXOS 2×2, numeración): [estructura de la planeación](estructura-planeacion.md). Sintaxis: [herramientas](../assets/herramientas/README.md). Trabajar sobre copias en `planea/trabajo/` y dejar el resultado en `salida/`. Insertar las secciones donde indique el usuario o `planea/estado.md`.

`D="python3 -I <skill>/assets/herramientas/docx_tool.py"`

## Flujo
1. **Mapear:** `$D mapa raipa.docx --solo-tablas` y `$D tablas … --filas A-B`; leer solo lo necesario.
2. **Copiar** las tablas del RAIPA a la planeación: `$D copiar plan.docx raipa.docx --desde B --hasta B --antes B -o p1.docx`.
3. **Filas de sesión:** `$D duplicar-fila p1.docx T3F16 --veces N --vaciar --independientes … -o p2.docx`; ajustar combinaciones con `vmerge`; `borrar-filas` si sobran.
4. **Editar** con `editar-celdas` (JSON de coordenadas; `**Anexo N**` en negrita). Para ver el formato actual, `leer-celdas`.
5. **Cronograma:** `tabla-en-celda … T2F4C3 cronograma.json` (tabla nativa en la celda).
6. **Anexos:** `anexos … anexos.json --antes B` con los números de `planea/materiales.csv`.
7. **Intocables:** `conservado plan.docx raipa.docx --celdas …` sobre contenidos y PDA; debe dar `OK` en todo.
8. **Verificar:** `verificar` (comparar con los avisos del original) y `comparar` con el original.
9. **Revisión visual:** `render plan.docx --dir DIR` y luego `uv run …/pdf_vista.py DIR/plan.pdf`; revisar portada, portadillas y anexos. Código 3: declararla pendiente para el usuario en Word.

Heredar la fuente del párrafo vecino; no imponer tamaños globales. Al cerrar, mover el DOCX final a `salida/` y limpiar `planea/trabajo/`.

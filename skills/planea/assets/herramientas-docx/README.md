# herramientas-docx

`docx_tool.py` lee y edita DOCX con pocos tokens. Solo biblioteca estándar de Python 3 (sin python-docx ni lxml). Compatible con Linux, macOS y Windows.

Ruta instalada: `~/.pi/agent/skills/planea/assets/herramientas-docx/docx_tool.py`

Invocación (siempre con `-I`):

```bash
python3 -I ~/.pi/agent/skills/planea/assets/herramientas-docx/docx_tool.py <comando> archivo.docx [opciones]
# Windows:  py -I docx_tool.py <comando> ...   o   python -I docx_tool.py <comando> ...
```

Abajo, `docx_tool` abrevia esa invocación.

## Principios
- `word/document.xml` nunca se reserializa: se localizan los elementos por desplazamientos de texto y se edita por empalme. Prefijos, `mc:Ignorable` y declaraciones de la raíz quedan idénticos (solo `copiar`/`insertar` añaden un `xmlns` si el fragmento usa un prefijo que el destino no declara).
- El ZIP se reescribe conservando el resto de partes sin cambios y en el mismo orden (`[Content_Types].xml` primero).
- Nunca se sobrescribe la entrada: los comandos que escriben exigen `-o salida.docx` (o `--sobrescribir`). Se rechaza escribir si existe un archivo de bloqueo de Word/LibreOffice.
- `--ancho N` (en comandos de lectura) cambia el truncado de textos (60 por defecto).
- Códigos de salida: 0 correcto, 1 hay diferencias/problemas, 2 error de uso.

## Lectura

| Comando | Qué hace |
|---|---|
| `info a.docx` | Tamaño, partes, párrafos/tablas/secciones/imágenes, encabezados y pies, comentarios, cambios controlados, macros, firmas. |
| `mapa a.docx [--desde N --hasta M]` | Un hijo del body por línea. |
| `tablas a.docx [--tabla N]` | Una celda por línea con coordenadas. |
| `texto a.docx --desde N [--hasta M]` | Texto completo de esos hijos del body. |
| `buscar a.docx "patrón" [--regex] [--sensible] [--max N]` | Coincidencias con ubicación. |

```text
$ docx_tool mapa a.docx --desde 104 --hasta 108
B104 P ""
B105 P [IMG3] "FUENTE: https://telesecundaria.sep.gob.mx/Repositorio/Mater…"
B106 T1 16x4 [IMG1] "CAMPO FORMATIVO"
B107 P ""
B108 T2 9x4 "PROYECTO PARCIAL DE AULA"
```

- `B#` es el índice de hijo del body (se usa en `--desde/--hasta/--antes`; también se acepta `B12`). Marcas: `[SALTO-PAG]`, `[SALTO-SECC(tipo)]`, `[IMG n]`, `[LST]`, `[est=Heading1]`; `SECT` es el `sectPr` final; `X:nombre` es otro elemento (marcadores, etc.).
- `T#` numera las tablas de primer nivel del body desde 0; `RxC` son filas × columnas de la rejilla.

```text
$ docx_tool tablas a.docx --tabla 2
# T2 9x4 grid=562,709,1418,11439
T2F0C0 [span=4] "PROYECTO PARCIAL DE AULA"
T2F4C0 [vmerge-ini] "MOMENTO 1"
T2F5C0 [vmerge] ""
T2F4C3 "Lenguajes: / Contenido integrado 6: La función creativa de …"
```

- Coordenada de celda `T2F3C1` = tabla 2, fila 3, celda física 1 (no columna de rejilla; `[span=n]` indica `gridSpan`). Tabla anidada: `T2F3C1.T0F0C0`.
- Varios párrafos de una celda se muestran unidos con ` / `. `buscar` indica `/pN` cuando la celda tiene varios párrafos y `xN` si hay N coincidencias en el párrafo.
- `texto` imprime por tabla una línea por fila: `F3: celda0 | celda1 | …` (la posición es la celda física).

## Edición

```bash
# Celdas por coordenada: texto o lista de párrafos
echo '{"T2F4C3": ["Párrafo 1", "Párrafo 2"], "T0F1C1": "Nuevo texto"}' > cambios.json
docx_tool editar-celdas a.docx cambios.json -o b.docx

# Reemplazo dentro de runs (opcional: --max N, --desde/--hasta de body)
docx_tool reemplazar a.docx "Trimestre II" "Trimestre III" -o b.docx
```

`editar-celdas`: escribe en el primer run con texto de cada párrafo y vacía los demás runs (conserva `rPr`, `pPr`, `tcPr`, `tblPr`, rejilla). Reutiliza los párrafos existentes; si faltan, clona `pPr`/`rPr` del último; si sobran, los elimina (excepto los que tengan imágenes, que solo se vacían). `\n` en un texto genera `<w:br/>` y `\t` genera `<w:tab/>`. Todo o nada: si una coordenada no existe no se escribe nada.

`reemplazar`: distingue mayúsculas; las coincidencias que cruzan runs **no se aplican** y se informan con su ubicación (editarlas con `editar-celdas`).

## Reutilizar y mover contenido

```bash
docx_tool extraer a.docx fragmento.xml --desde 106 --hasta 114      # XML crudo de B106..B114
docx_tool insertar b.docx fragmento.xml --antes 80 -o c.docx          # sin imágenes/relaciones

# Entre documentos, incluidas imágenes y enlaces (copia media, relaciones, content types):
docx_tool copiar destino.docx origen.docx --desde 106 --hasta 114 --antes 80 -o salida.docx

docx_tool borrar a.docx --desde 106 --hasta 114 [--limpiar-media] -o b.docx
```

- `--antes K` inserta antes del hijo K (nunca después del `sectPr` final).
- `copiar`: crea relaciones nuevas con ids únicos (reutiliza una existente idéntica), copia media (reutiliza la identica por contenido, renombra si el nombre choca), añade `Default`/`Override` de content types que falten, reasigna `w14:paraId`/`w14:textId`, `wp:docPr@id` e ids de marcadores duplicados, y declara en la raíz del destino los prefijos que falten. Además copia **numeración y estilos** (ver abajo) e imprime una línea resumen: `numeraciones: 94→25,…; estilos copiados: …; estilos coincidentes conservados: …`.
- Numeración: por cada `w:numId` del fragmento (y de los estilos copiados) copia el `w:num` y su `w:abstractNum` a `numbering.xml` del destino con `numId`/`abstractNumId`/`nsid` nuevos sin colisión, remapea `w:numId`, inserta los `abstractNum` antes de los `w:num`, y crea `numbering.xml` (con relación y `Override`) si el destino no lo tiene. Empalme de texto: se conservan atributos `w14:`/`w15:` y se declaran en la raíz los prefijos que falten.
- Estilos: para cada `pStyle`/`rStyle`/`tblStyle` usado y ausente en el destino (por `styleId`) copia el `w:style` del origen, con `basedOn`/`link`/`next` recursivos si faltan. Si el `styleId` ya existe, se conserva el del destino (no se sobrescribe) y se informa. Los estilos copiados pierden `w:default`.
- Un párrafo copiado con salto de sección arrastra también sus encabezados/pies (se copian como partes nuevas).
- `borrar --limpiar-media` elimina relaciones que dejan de usarse y las partes que queden sin referencias.

## Comprobación

```bash
docx_tool verificar b.docx           # OK, o lista de PROBLEMAS (y AVISOS)
docx_tool comparar a.docx b.docx     # SIN DIFERENCIAS estructurales, o lista de diferencias
```

`verificar` comprueba: ZIP íntegro, `[Content_Types].xml` primero y tipos para todas las partes, todas las partes XML bien formadas (con prefijos declarados), relaciones que apuntan a partes existentes, `r:id` con relación, `paraId` y `docPr` duplicados en `document.xml` (problema), partes huérfanas y duplicados en otras partes o de `textId` (aviso), y conteos. Compara siempre con `verificar` del documento original: duplicados preexistentes no son fallos de tu edición.

`comparar` contrasta conteos (tablas, filas, celdas, imágenes, secciones), `tblGrid`, `gridSpan` y `vMerge` por tabla (incluidas anidadas), y las declaraciones de la raíz y `mc:Ignorable`. No compara texto ni número de párrafos.

## Limitaciones
- Se asume el prefijo `w:` para WordprocessingML (lo habitual en Word y LibreOffice).
- Cuadros de texto, dibujos y objetos (`w:drawing`, `w:pict`, `w:txbxContent`) no se recorren: su texto no aparece en `texto`/`buscar` ni se edita.
- Tablas dentro de controles de contenido (`w:sdt`) del body no tienen coordenada `T#`; sí se leen como `SDT` en `mapa`/`texto`.
- Encabezados, pies, notas y comentarios no se editan (solo `info` los resume).
- Los cambios controlados no se registran: las ediciones son directas.
- `copiar` no copia viñetas de imagen (`numPicBullet`; avisa), ni estilos vinculados desde `w:abstractNum/w:lvl/w:pStyle`. Si el destino no tiene `styles.xml`, no copia estilos.
- Sin render: la revisión visual la hace el usuario en Word.

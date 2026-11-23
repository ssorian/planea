# herramientas: `docx_tool.py`

Lee y edita DOCX con pocos tokens. Solo biblioteca estándar (Python ≥ 3.9; Linux, macOS, Windows). Invocación, siempre con `-I`:

```bash
python3 -I docx_tool.py <comando> archivo.docx [opciones]     # Windows: py -I / python -I
```

- `word/document.xml` **nunca se reserializa**: se edita por empalme de texto; prefijos y `mc:Ignorable` quedan intactos.
- Los comandos que escriben exigen `-o salida.docx` (o `--sobrescribir`) y rechazan escribir si el documento está abierto (archivo `~$`/`.~lock`).
- Todo o nada: ante un error no se escribe nada. Mensajes en español.
- Códigos: `0` correcto · `1` diferencias/problemas · `2` error de uso · `3` sin renderizador (`render`).

## Coordenadas
| Forma | Significa |
|---|---|
| `B12` (o `12`) | hijo 12 del body (párrafo, tabla, `SECT` final…) |
| `T3` | tabla de primer nivel 3 (desde 0) |
| `T3F16` | fila 16 de T3 · **fila** (duplicar, borrar, leer, conservado) |
| `T3F16C2` | celda **física** 2 de esa fila (no columna de rejilla; `[span=n]` = `gridSpan`) |
| `T2F5C3.T0F1C0` | tabla anidada 0 dentro de T2F5C3, fila 1, celda 0 |
| `…/p1` | párrafo 1 de la celda (solo en salidas) |

## Lectura
| Comando | Qué hace |
|---|---|
| `info a.docx` | tamaño, partes, párrafos/tablas/secciones/imágenes, encabezados, comentarios, macros |
| `mapa a.docx [--desde B --hasta B] [--solo-tablas]` | un hijo del body por línea: `B106 T1 16x4 [IMG1] "texto"`; `--solo-tablas` imprime solo las tablas |
| `tablas a.docx [--tabla N] [--filas A-B]` | una celda por línea (`T2F4C0 [vmerge-ini] "…"`); `--filas 16` o `16-20` (inclusive, requiere `--tabla`) |
| `leer-celdas a.docx COORD…` | JSON `{"T3F16C2": ["párrafo 1", …]}`; `**…**` donde hay negrita; acepta fila `T3F16` y anidadas; las tablas anidadas se anotan como `"COORD.T0": "(tabla anidada 4x3)"` |
| `texto a.docx --desde B [--hasta B]` | texto completo de esos hijos |
| `buscar a.docx "patrón" [--regex] [--sensible] [--max N]` | coincidencias con coordenada |

`--ancho N` cambia el truncado (60). Marcas de `mapa`: `[SALTO-PAG]`, `[SALTO-SECC(tipo)]`, `[IMGn]`, `[LST]`, `[est=…]`.

## Edición de texto
| Comando | Qué hace |
|---|---|
| `editar-celdas a.docx cambios.json -o b.docx` | `{"T2F4C3": "texto" \| ["p1","p2"]}`. Escribe en el primer run con texto de cada párrafo (conserva formato); clona el último párrafo si faltan y elimina los sobrantes. `\n` = salto, `\t` = tabulador. |
| `reemplazar a.docx "viejo" "nuevo" [--max N --desde B --hasta B] -o b.docx` | dentro de runs; las coincidencias que cruzan runs se avisan, no se aplican |

**Negrita parcial:** `**…**` en el texto deja un run por segmento (`**Desarrollo.** Se lee (**Anexo 3**).`). `\*` es un asterisco literal; `**` sin cerrar es error con la coordenada. La salida de `leer-celdas` se puede pasar tal cual a `editar-celdas` (ignora las claves `COORD.T0` de tablas anidadas).

## Filas y tablas
| Comando | Qué hace |
|---|---|
| `duplicar-fila a.docx T3F16 --veces N [--vaciar] [--independientes C3,C4] -o b.docx` | N clones justo después. En los clones `vMerge restart` pasa a continuar la combinación; `--independientes` quita `vMerge` de esas celdas físicas; `--vaciar` deja un párrafo vacío por celda (conserva `pPr` y el `rPr` del primer run con texto). IDs nuevos. |
| `borrar-filas a.docx T3F20 [--hasta F22] [--forzar] -o b.docx` | rechaza borrar todas las filas y borrar un `vmerge-ini` cuya combinación sigue debajo (nombra la celda); `--forzar` promueve la primera celda `continue` superviviente y avisa de que el texto inicial se pierde |
| `vmerge a.docx T3F16C1 --estado ninguno\|inicio\|continua -o b.docx` | pone o quita `w:vMerge` en la celda |
| `tabla-en-celda a.docx T2F4C3 datos.json -o b.docx` | inserta una tabla anidada al final de la celda; queda como `T2F4C3.T0` (la siguiente, `.T1`) |
| `copiar destino.docx origen.docx --desde B --hasta B --antes B -o s.docx` | copia hijos del body entre documentos con imágenes, relaciones, numeración y estilos |
| `extraer a.docx frag.xml --desde B [--hasta B]` · `insertar a.docx frag.xml --antes B -o b.docx` | XML crudo (sin relaciones; para imágenes usa `copiar`) |
| `borrar a.docx --desde B [--hasta B] [--limpiar-media] -o b.docx` | borra hijos del body |

`datos.json` de `tabla-en-celda`: `{"encabezados": ["Sesión","Fecha"], "filas": [["1","**Lunes**"]], "anchos": [1,2], "bordes": true}`. `anchos` son proporciones; el ancho total es el de la celda menos 200 twips; el encabezado va en negrita y repite en cada página; `bordes: false` quita las líneas.

## Anexos
| Comando | Qué hace |
|---|---|
| `anexos a.docx anexos.json --antes B97 -o b.docx` | hojas de ANEXOS antes de B97: por cada 4 anexos, título centrado con salto de página y tabla 2×2 sin bordes (imagen escalada y URL clicable) |

```json
{"titulo": "ANEXOS", "anexos": [
  {"n": 4, "titulo": "Video Qué es identidad", "imagen": "img/a.png", "url": "https://example.org/v"},
  {"n": 5, "titulo": "Lectura"}]}
```
`n` consecutivos (desde cualquier número); `imagen` (PNG/JPEG/GIF) relativa al JSON; `url` http(s). Solo «Anexo N» va en negrita. Usa la página y márgenes de la sección donde cae `--antes`. Salida: `OK: 5 anexos en 2 hojas antes de B97`.

## Verificación
| Comando | Qué hace |
|---|---|
| `verificar a.docx` | ZIP, content types, XML bien formado, relaciones, ids duplicados, **celda que no termina en `w:p`** y **tabla sin filas** (Word da el archivo por dañado). Compáralo con el original: los avisos previos no son tuyos |
| `comparar a.docx b.docx` | conteos, `tblGrid`, `gridSpan`, `vMerge` por tabla; código 1 si difieren |
| `conservado destino.docx origen.docx --celdas T1F0C1,T3F4 [--desde B --hasta B]` | cada párrafo no vacío de esas celdas del **origen** (NFC, espacios colapsados) debe estar en el destino (en un párrafo o en consecutivos unidos). `--celdas @lista.txt` (una por línea). Salida `OK T3F4C3 (3 párrafos)` / `FALTA T3F4C3/p1 "…"`; código 1 si falta algo |
| `render a.docx [--dir DIR]` | DOCX → PDF con LibreOffice (`soffice`) o, en Windows, Word por COM; imprime la ruta del PDF. Sin ninguno: `SIN RENDERIZADOR…` y código 3 (la revisión visual queda para el usuario en Word) |

## Flujo de ejemplo (datos inventados)
```bash
D="python3 -I docx_tool.py"
$D mapa raipa.docx --desde 100 --hasta 120 --solo-tablas               # ¿dónde está el proyecto?
$D copiar plan.docx raipa.docx --desde 106 --hasta 114 --antes 79 -o p1.docx   # bloque con sus imágenes
$D duplicar-fila p1.docx T3F16 --veces 2 --vaciar --independientes C1,C3 -o p2.docx
$D vmerge p2.docx T3F18C1 --estado inicio -o p3.docx                   # reabrir la combinación bajo los clones
$D editar-celdas p3.docx sesiones.json -o p4.docx                      # {"T3F17C2": "**Inicio.** Se lee (**Anexo 4**)."}
$D tabla-en-celda p4.docx T2F4C3 cronograma.json -o p5.docx
$D anexos p5.docx anexos.json --antes 99 -o p6.docx
$D conservado p6.docx raipa.docx --celdas T3F4C3,T3F14C3 --desde B79 --hasta B90
$D verificar p6.docx
$D render p6.docx --dir pdf                                          # código 3 = revisar en Word
```

## Limitaciones
- Se asume el prefijo `w:`. Cuadros de texto, dibujos y objetos no se recorren. Tablas dentro de `w:sdt` no tienen coordenada `T#`.
- No se editan encabezados, pies ni comentarios; los cambios no se registran como controlados.
- La negrita de `leer-celdas` es la de `w:b` directo del run (no la heredada de un estilo).
- `anexos`: imágenes a 96 ppp y sin ampliar; sin PDF no hay comprobación visual del encaje.

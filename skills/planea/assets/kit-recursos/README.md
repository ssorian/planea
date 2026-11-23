# Kit de recursos imprimibles (React → PDF)

Requisitos: `bun` y un navegador Chromium (Chromium, Chrome o Edge; se detecta en Linux, macOS y Windows, o se define con `PLANEA_NAVEGADOR`). Opcionales: `pdfinfo` y `pdftoppm` (Poppler). Sin Poppler, la salida JSON indica `vista: captura-navegador` y la vista previa es solo aproximada de la primera página. Las dependencias ya están en `node_modules`; si falta la carpeta, `bun install` necesita internet y permiso.

## Crear un recurso
1. Crear `<proyecto>/Recursos/fuente/anexo-NN-nombre.tsx` fuera de esta carpeta. Importar los componentes con ruta absoluta o relativa a este kit.
2. Exportar `meta = { nombre: "anexo-NN-nombre", pagina: "letter" }` (`"letter landscape"` para tablas anchas, `"A4"` si se pide).
3. Exportar por defecto un componente con una o más `<Hoja>`.
4. Renderizar:
   ```
   bun ~/.pi/agent/skills/planea/assets/kit-recursos/render.tsx <recurso.tsx> <carpeta-salida> --png
   ```
   Imprime JSON con la ruta del PDF, el número de páginas y los PNG de vista previa (110 ppp).

## Componentes (`componentes.tsx`)
| Componente | Uso |
| --- | --- |
| `Hoja` | Una página (salto de página después) |
| `Encabezado` | Título, anexo, campo y grado |
| `CamposAlumno` | Renglones para nombre, grupo y fecha |
| `Consigna` | Instrucción destacada en infinitivo |
| `Rubrica` | Criterios × niveles; valida que haya un descriptor por nivel |
| `ListaCotejo` | Indicadores con Sí/No y observaciones |
| `EscalaEstimativa` | Conductas × frecuencia |
| `Examen` / `ClaveExamen` | Reactivos de opción múltiple, abiertos y de relación; la clave va en otro archivo |
| `Retroalimentacion` | Recuadro para comentarios |
| `Figura` | Imagen local con pie y crédito |
| `Credito` | Autoría o fuente |

Para fichas, láminas o tarjetas se puede escribir JSX y CSS propio en el recurso; mantener la paleta de `estilos.css`.

Las imágenes se cargan con rutas relativas al archivo `.tsx`. Las ilustraciones se generan con `openai_image` y se insertan con `Figura`.

`ejemplos/rubrica-ejemplo.tsx` muestra la estructura; sus textos son solo ilustrativos.

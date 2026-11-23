# Conversor de recursos a PDF

Convierte un recurso terminado (HTML o React) a PDF con un navegador Chromium sin ventana. No aporta diseño: el layout y los estilos son del recurso (ver `references/diseno-recursos.md`).

## Requisitos
- `bun`. Las dependencias (`react`, `react-dom`) se instalan con el instalador o con `bun install`.
- Chromium, Google Chrome o Microsoft Edge; se detecta en Linux, macOS y Windows. Si no, definir `PLANEA_NAVEGADOR` con la ruta del ejecutable.
- Opcional: Poppler (`pdfinfo`, `pdftoppm`) para contar páginas y generar las vistas previas de todas las páginas. Sin Poppler, se cuentan las páginas del PDF directamente y la vista previa es una captura aproximada de la primera pantalla (`"vista": "captura-navegador…"`).

## Uso
```
bun ~/.pi/agent/skills/planea/assets/conversor-pdf/convertir.tsx <recurso.html|recurso.tsx> <carpeta-salida> [--png] [--html] [--pagina "letter landscape"]
```
- **`.html`:** se imprime tal cual; el tamaño de página sale de su `@page`, o de `--pagina`.
- **`.tsx`:** exporta por defecto un componente sin props y, opcionalmente, `meta = { nombre, pagina, css }`, con `css` relativo al `.tsx`.
- **`--png`:** genera vistas previas a 110 ppp.
- **`--html`:** conserva el HTML intermedio de un `.tsx`.
- **Rutas:** las imágenes se resuelven relativas al archivo del recurso.

Imprime un JSON: `{ pdf, paginas, png, vista }`. Si falta el archivo o la extensión no es válida, sale con código 2.

En Windows: `bun convertir.tsx recurso.html Recursos --png` desde PowerShell, con Edge detectado automáticamente.

# planea

Skill para agentes de IA (Pi, Claude Code, Codex y compatibles con `SKILL.md`) que diseña y produce **planeaciones didácticas de telesecundaria NEM** a partir del RAIPA.

Trae instrucciones y guías, más tres herramientas pequeñas en Python (leer y editar DOCX, HTML a PDF y vista previa de PDF) con sus pruebas. Le dice al agente qué hacer, con qué criterios y con qué herramientas.

## Qué cubre
- **Análisis del RAIPA:** temas, PDA, productos, tiempos, incongruencias y fuentes.
- **Diseño de proyectos y sesiones** con la taxonomía de Bloom revisada, las metodologías sociocríticas de la NEM, el DUA y modelos de sesión (5E, liberación gradual, Kolb, Gagné, Marzano).
- **Investigación de actividades que funcionan y de materiales existentes** (videos, imágenes, hojas, diapositivas): criterios de selección, licencias y citas.
- **Instrumentos de evaluación:** rúbricas, listas de cotejo, escalas, exámenes con tabla de especificaciones, autoevaluación y coevaluación.
- **Diseño de recursos:**
  - estándar de layout (lo obligatorio, lo recomendado y lo libre) y una identidad visual propia para cada proyecto;
  - estructura de cada tipo de recurso;
  - al terminar, conversión a PDF y revisión de las vistas previas.
- **Estilos visuales de referencia:** cinco estilos lúdicos (bloques de respuesta, ruleta de categorías, gamificado amable, arcade de personajes y tarjetas temáticas), con layout, tokens propios y usos, inspirados en juegos educativos web sin copiar sus marcas.
- **Diseño de juegos didácticos:** mecánicas sencillas, reglas didácticas y diseño muy visual; impresos, corporales o proyectados.
- **Estructura de la planeación:** qué se conserva, llena o rediseña en cada tabla del RAIPA, una fila por sesión, referencias directas a anexos y ANEXOS en tablas 2×2 sin bordes.
- **Edición de la planeación en Word** con `docx_tool.py`: mapa, lectura y edición de celdas con negrita, filas de sesión, cronograma, anexos, comprobación de lo intocable, verificación y render.
- **Recursos a PDF** con `html_a_pdf.py` y vistas previas con `pdf_vista.py`.
- **Estado del proyecto** en la carpeta de trabajo del usuario (`planea/estado.md`, ver abajo).

Contenidos, subcontenidos y PDA del RAIPA nunca se modifican. Todo lo demás se rediseña y se presenta para aprobación antes de producirlo.

## Instalación
Copiar la carpeta `skills/planea` a la carpeta de skills del agente:

| Agente | Carpeta |
| --- | --- |
| Pi | `~/.pi/agent/skills/` |
| Claude Code | `~/.claude/skills/` |
| Codex (CLI, app e IDE) | `~/.agents/skills/` (personal) o `.agents/skills/` en la raíz del repositorio (proyecto) |
| Otros | `~/.agents/skills/` o la que indique el agente |

Pi también lee `~/.agents/skills/`: si usas Pi y Codex, instala solo ahí para no tener la skill duplicada. En Codex, reinicia la sesión tras instalar; se invoca sola por su descripción o con `$planea`.

```bash
git clone https://github.com/ssorian/planea.git
cp -r planea/skills/planea ~/.pi/agent/skills/        # Linux/macOS
```
```powershell
git clone https://github.com/ssorian/planea.git
Copy-Item -Recurse planea\skills\planea $HOME\.pi\agent\skills\   # Windows
```
Para actualizar: `git pull` y volver a copiar. Para desarrollo se puede usar un enlace simbólico (en Windows, una unión de directorio: `New-Item -ItemType Junction`).

### Pedirle a un agente que la instale
> Instala la skill planea desde https://github.com/ssorian/planea: copia la carpeta `skills/planea` del repositorio a mi carpeta de skills, confirma que existe `SKILL.md` y dime si faltan Python 3.9+, un navegador Chromium/Chrome/Edge o uv en este equipo.

## Dependencias
| Dependencia | Para qué |
| --- | --- |
| Python 3.9+ (suele venir en el sistema) | `docx_tool.py` y `html_a_pdf.py`, solo con biblioteca estándar |
| Chromium, Chrome o Edge | `html_a_pdf.py` (también sirve el de la caché de Playwright) |
| [uv](https://docs.astral.sh/uv/) | solo para `pdf_vista.py` con PyMuPDF; alternativa: Poppler (`pdftoppm`) con `python3 -I` |
| LibreOffice (o Word en Windows) | opcional, para `docx_tool.py render` |
| [Node.js](https://nodejs.org) | solo para juegos proyectados con Vite + React, si el juego lo necesita |

Si falta una herramienta, el agente lo dice y pide permiso antes de descargar o instalar nada. Las herramientas se invocan con `python3 -I` (Windows: `py -I`); sintaxis en [`assets/herramientas/README.md`](skills/planea/assets/herramientas/README.md).

## Carpeta de trabajo del usuario
La skill guarda lo confirmado y lo aprobado en la carpeta donde trabajas, no dentro de la skill:
```
<carpeta de trabajo>/
├── planea/            # estado.md, materiales.csv, diseno-<proyecto>.md, trabajo/
├── Recursos/          # fuentes HTML, PDF numerados por anexo, juegos
└── salida/            # planeación DOCX producida
```
Detalle en [`estado-proyecto.md`](skills/planea/references/estado-proyecto.md).

## Estructura
```
skills/planea/
├── SKILL.md          # contrato principal: reglas, decisiones y pasos
├── references/       # guías que el agente carga según la tarea
│   ├── diseno-proyecto.md · metodologias.md · construccion-sesiones.md
│   ├── investigacion-actividades.md · materiales-existentes.md
│   ├── instrumentos-evaluacion.md · diseno-recursos.md · juegos-didacticos.md
│   ├── estilos-visuales.md · estructura-planeacion.md
│   ├── documento-docx.md · herramientas.md
│   └── estado-proyecto.md · glosario.md
└── assets/
    ├── plantilla-sesion.md · ficha-actividad.md · plantilla-estado.md
    ├── ejemplo-campo.md · lista-verificacion.md · catalogo-materiales.csv
    ├── esqueleto-recurso.html
    └── herramientas/ # docx_tool.py · html_a_pdf.py · pdf_vista.py · README.md
pruebas/              # test_docx_tool.py · test_recursos.py
.github/workflows/    # pruebas.yml (CI)
```

## Pruebas
```bash
python3 -m unittest discover -s pruebas
```

## Uso
Pide a tu agente, por ejemplo: «Analiza el campo de Lenguajes del RAIPA y propón las sesiones», «Diseña la rúbrica del producto final» o «Propón un juego de repaso para el cierre de la sesión 3».

## Licencia
Apache-2.0.

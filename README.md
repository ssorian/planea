# planea

Skill para agentes de IA (Pi, Claude Code y compatibles con `SKILL.md`) que diseña y produce **planeaciones didácticas de telesecundaria NEM** a partir del RAIPA.

Son solo instrucciones y guías: no trae código, plantillas ni estilos fijos. Le dice al agente qué hacer, con qué criterios y con qué herramientas existentes.

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
- **Edición de la planeación en Word**, con reglas para conservar formato, estilos, numeración e imágenes.

Contenidos, subcontenidos y PDA del RAIPA nunca se modifican. Todo lo demás se rediseña y se presenta para aprobación antes de producirlo.

## Instalación
Copiar la carpeta `skills/planea` a la carpeta de skills del agente:

| Agente | Carpeta |
| --- | --- |
| Pi | `~/.pi/agent/skills/` |
| Claude Code | `~/.claude/skills/` |
| Otros | `~/.agents/skills/` o la que indique el agente |

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
> Instala la skill planea desde https://github.com/ssorian/planea: copia la carpeta `skills/planea` del repositorio a mi carpeta de skills, confirma que existe `SKILL.md` y dime qué herramientas de `references/herramientas.md` faltan en este equipo.

## Herramientas que usará el agente
No hace falta instalarlas antes. El agente comprueba qué hay y, con permiso, ejecuta lo que falte al momento con `uvx`, `uv run --with`, `npx` o `bunx`.

| Herramienta | Para qué | Recomendación |
| --- | --- | --- |
| [uv](https://docs.astral.sh/uv/) | Ejecutar `python-docx`, `docxcompose` y `markitdown` sin instalación global | Muy recomendado |
| Python 3.9+ | Scripts auxiliares para Word | Necesario para editar DOCX |
| Chromium, Google Chrome o Microsoft Edge | Pasar recursos HTML a PDF y hacer capturas | Necesario para PDF (Edge ya viene en Windows) |
| Node.js con `npx`, o [Bun](https://bun.sh) con `bunx` | Playwright, React y Vite cuando hagan falta | Opcional |
| Poppler (`pdftoppm`, `pdfinfo`) | Vistas previas y conteo de páginas | Recomendado |
| LibreOffice | Renderizar DOCX para revisarlo | Opcional |
| Búsqueda web y generación de imágenes del agente | Investigar materiales e ilustrar recursos | Recomendado |

Instalación rápida de lo recomendado:
- **Windows:** `winget install astral-sh.uv Python.Python.3.12`; Poppler con `scoop install poppler`.
- **Debian/Ubuntu:** `curl -LsSf https://astral.sh/uv/install.sh | sh` y `sudo apt install python3 chromium poppler-utils`.
- **Arch:** `sudo pacman -S uv python chromium poppler`.
- **macOS:** `brew install uv python poppler` y `brew install --cask google-chrome`.

## Estructura
```
skills/planea/
├── SKILL.md          # contrato principal: reglas, decisiones y pasos
├── references/       # guías que el agente carga según la tarea
│   ├── diseno-proyecto.md · metodologias.md · construccion-sesiones.md
│   ├── investigacion-actividades.md · materiales-existentes.md
│   ├── instrumentos-evaluacion.md · diseno-recursos.md · juegos-didacticos.md
│   ├── estilos-visuales.md
│   └── documento-docx.md · herramientas.md
└── assets/           # plantillas de registro y lista de verificación (texto)
```

## Uso
Pide a tu agente, por ejemplo: «Analiza el campo de Lenguajes del RAIPA y propón las sesiones», «Diseña la rúbrica del producto final» o «Propón un juego de repaso para el cierre de la sesión 3».

## Licencia
Apache-2.0.

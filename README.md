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
> Instala la skill planea desde https://github.com/ssorian/planea: copia la carpeta `skills/planea` del repositorio a mi carpeta de skills, confirma que existe `SKILL.md` y y dime si faltan Node.js o uv en este equipo.

## Dependencias
Solo dos:

| Dependencia | Para qué |
| --- | --- |
| [Node.js](https://nodejs.org) (incluye `npx`) | Vite, React y Playwright cuando hagan falta |
| [uv](https://docs.astral.sh/uv/) (incluye `uvx`) | Python y sus bibliotecas al momento: `python-docx`, `docxcompose`, `markitdown`, `pymupdf`, `playwright` |

Todo lo demás lo obtiene el agente al usarlo, sin instalaciones globales. La primera vez descarga paquetes (y el Chromium de Playwright), por lo que pedirá permiso y necesitará internet; después funciona sin conexión.

Instalación:
- **Windows:** `winget install OpenJS.NodeJS.LTS astral-sh.uv`
- **macOS:** `brew install node uv`
- **Linux:** Node.js con el gestor de paquetes de la distribución (o [nvm](https://github.com/nvm-sh/nvm)/[fnm](https://github.com/Schniz/fnm)); uv con `curl -LsSf https://astral.sh/uv/install.sh | sh`

Si el equipo ya tiene Chromium, Chrome, Edge, Poppler o LibreOffice, el agente puede usarlos, pero no son necesarios.

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

# planea

Skill para agentes de IA (Pi, Claude Code y compatibles con `SKILL.md`) que diseña y produce **planeaciones didácticas de telesecundaria NEM** a partir del RAIPA.

## Qué hace
- **Analiza el RAIPA:** temas, PDA, productos, tiempos, incongruencias y fuentes.
- **Diseña proyectos y sesiones** con la taxonomía de Bloom revisada, las metodologías sociocríticas de la NEM, el DUA y modelos de sesión (5E, liberación gradual, Kolb, Gagné, Marzano).
- **Investiga actividades que funcionan y materiales existentes** (videos, imágenes, hojas, diapositivas), con criterios de selección, licencias y citas.
- **Crea instrumentos de evaluación:** rúbricas, listas de cotejo, escalas, exámenes con tabla de especificaciones, autoevaluación y coevaluación.
- **Produce recursos imprimibles** con React → PDF (Chromium sin ventana).
- **Orienta el diseño de juegos didácticos**: mecánicas sencillas (respuesta simultánea con tarjetas de colores, respuestas ocultas por equipos, tablero de categorías, memorama, lotería, rally…), reglas didácticas, diseño muy visual y cómo construirlos impresos o proyectados con Vite cuando se aprueban.
- **Lee y edita la planeación en Word** con `docx_tool.py`, que conserva el formato y gasta pocos tokens.

Contenidos, subcontenidos y PDA del RAIPA nunca se modifican. Todo lo demás se rediseña y se presenta para aprobación antes de producirlo.

## Instalación

### Linux y macOS
```bash
curl -fsSL https://raw.githubusercontent.com/ssorian/planea/main/install.sh | bash
```
o desde un clon:
```bash
git clone https://github.com/ssorian/planea.git && cd planea && ./install.sh
```

### Windows (PowerShell)
```powershell
& ([scriptblock]::Create((irm https://raw.githubusercontent.com/ssorian/planea/main/install.ps1)))
```
o desde un clon:
```powershell
git clone https://github.com/ssorian/planea.git; cd planea
powershell -ExecutionPolicy Bypass -File .\install.ps1
```
Si no hay `git`, el instalador descarga el ZIP del repositorio.

### Opciones
| Linux/macOS | Windows | Efecto |
| --- | --- | --- |
| `--destino pi\|claude\|agents\|todos\|RUTA` | `-Destino …` | Carpeta de skills. Por defecto, las que ya existan (`~/.pi/agent/skills`, `~/.claude/skills`, `~/.agents/skills`). |
| `--enlace` | `-Enlace` | Enlace al clon para desarrollo (en Windows, unión de directorio; no requiere administrador). |
| `--sin-dependencias` | `-SinDependencias` | No instala React ni Vite en los kits. |
| `--desinstalar` | `-Desinstalar` | Quita la skill. |

### Pedirle a un agente que la instale
Copiar en Pi, Claude Code u otro agente con terminal:

> Instala la skill planea desde https://github.com/ssorian/planea siguiendo su README: usa `install.sh` en Linux/macOS o `install.ps1` en Windows, sin opciones salvo que yo indique otra cosa. Luego confirma que existe `SKILL.md` en la carpeta de skills y dime qué requisitos faltan.

## Dependencias

### Programas del sistema
| Programa | Para qué | ¿Obligatorio? |
| --- | --- | --- |
| Agente compatible con `SKILL.md` (Pi, Claude Code u otro) | Usar la skill | Sí |
| [Bun](https://bun.sh) 1.1+ (o Node.js 20+ con npm) | Kit PDF (y juegos proyectados con Vite, si se construyen) | Sí, para crear recursos |
| Navegador Chromium: Chromium, Google Chrome o Microsoft Edge | Generar PDF y capturas | Sí, para PDF; Edge ya viene en Windows |
| Python 3.9+ | `docx_tool.py` (solo biblioteca estándar, sin paquetes extra) | Sí, para leer y editar Word |
| Git | Instalar desde un clon y actualizar | Opcional (en Windows el instalador puede bajar el ZIP) |
| Poppler (`pdftoppm`, `pdfinfo`) | Vista previa de todas las páginas del PDF | Opcional; sin él se usa una captura aproximada de la primera página |

El navegador se detecta solo. Si no lo encuentra, definir `PLANEA_NAVEGADOR` con la ruta del ejecutable.

### Cómo instalarlas
**Windows** (PowerShell con `winget`):
```powershell
powershell -c "irm bun.sh/install.ps1 | iex"   # Bun
winget install Python.Python.3.12
winget install Git.Git                         # opcional
scoop install poppler                          # opcional (requiere Scoop)
```
**Debian/Ubuntu:**
```bash
curl -fsSL https://bun.sh/install | bash
sudo apt install python3 chromium poppler-utils git
```
**Arch Linux:**
```bash
curl -fsSL https://bun.sh/install | bash
sudo pacman -S python chromium poppler git
```
**macOS** (Homebrew):
```bash
curl -fsSL https://bun.sh/install | bash
brew install python poppler git
brew install --cask google-chrome
```

### Paquetes de JavaScript
El instalador los instala solo con `bun install` (o `npm install`) dentro del kit. Esto requiere internet la primera vez; después todo funciona sin conexión.

| Kit | Paquetes |
| --- | --- |
| `kit-recursos` (React → PDF) | `react`, `react-dom` |

Con `--sin-dependencias` (`-SinDependencias` en Windows) se omiten; después se pueden instalar con `bun install` en el kit.

Los juegos proyectados no traen dependencias preinstaladas: cuando se aprueba uno, el agente crea su proyecto con Vite (`vite`, `@vitejs/plugin-react`, `vite-plugin-singlefile`, React), lo que requiere internet la primera vez.

### Opcional en el agente
- Búsqueda web, para investigar actividades y materiales.
- Generación de imágenes (por ejemplo, `openai_image` en Pi), para las ilustraciones. Sin ella, la skill usa materiales existentes o recursos de solo texto.

## Estructura
```
skills/planea/
├── SKILL.md                    # contrato principal
├── references/                 # módulos que el agente carga según la tarea
└── assets/
    ├── kit-recursos/           # React → PDF (fichas, rúbricas, exámenes)
    ├── herramientas-docx/      # docx_tool.py
    └── plantillas y catálogos
```

## Uso
Pide a tu agente, por ejemplo: «Analiza el campo de Lenguajes del RAIPA y propón las sesiones», «Haz la rúbrica del producto final» o «Propón un juego de repaso para el cierre de la sesión 3».

## Licencia
Apache-2.0. La guía de juegos pide mecánicas de género con nombres y diseño propios, sin afiliación a programas de televisión ni aplicaciones.

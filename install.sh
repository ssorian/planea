#!/usr/bin/env bash
# Instalador de la skill «planea».
# Uso:
#   ./install.sh [--destino pi|claude|agents|todos|RUTA] [--enlace] [--sin-dependencias] [--desinstalar]
#   curl -fsSL https://raw.githubusercontent.com/ssorian/planea/main/install.sh | bash -s -- [opciones]
set -euo pipefail

REPO_URL="https://github.com/ssorian/planea.git"
NOMBRE="planea"
DESTINO=""
ENLACE=0
DEPENDENCIAS=1
DESINSTALAR=0

ayuda() {
  sed -n '2,6p' "$0" 2>/dev/null | sed 's/^# \{0,1\}//'
  cat <<'EOF'

Opciones:
  --destino D         pi (~/.pi/agent/skills), claude (~/.claude/skills),
                      agents (~/.agents/skills), todos, o una ruta de carpeta de skills.
                      Por defecto: los destinos cuyas carpetas ya existen; si no hay ninguno, pi.
  --enlace            Crear un enlace simbólico al repositorio en vez de copiar (para desarrollo).
  --sin-dependencias  No instalar dependencias de los kits (React, Vite).
  --desinstalar       Quitar la skill de los destinos.
  -h, --ayuda         Mostrar esta ayuda.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --destino) DESTINO="${2:?Falta el valor de --destino}"; shift 2 ;;
    --enlace) ENLACE=1; shift ;;
    --sin-dependencias) DEPENDENCIAS=0; shift ;;
    --desinstalar) DESINSTALAR=1; shift ;;
    -h|--ayuda|--help) ayuda; exit 0 ;;
    *) echo "Opción desconocida: $1" >&2; ayuda; exit 2 ;;
  esac
done

carpeta_de() {
  case "$1" in
    pi) echo "$HOME/.pi/agent/skills" ;;
    claude) echo "$HOME/.claude/skills" ;;
    agents) echo "$HOME/.agents/skills" ;;
    *) echo "$1" ;;
  esac
}

destinos=()
if [[ -z "$DESTINO" ]]; then
  for d in pi claude agents; do
    [[ -d "$(carpeta_de "$d")" ]] && destinos+=("$(carpeta_de "$d")")
  done
  [[ ${#destinos[@]} -eq 0 ]] && destinos=("$(carpeta_de pi)")
elif [[ "$DESTINO" == "todos" ]]; then
  destinos=("$(carpeta_de pi)" "$(carpeta_de claude)" "$(carpeta_de agents)")
else
  destinos=("$(carpeta_de "$DESTINO")")
fi

if [[ $DESINSTALAR -eq 1 ]]; then
  for base in "${destinos[@]}"; do
    objetivo="$base/$NOMBRE"
    if [[ -L "$objetivo" || -d "$objetivo" ]]; then
      rm -rf "$objetivo"; echo "Eliminada: $objetivo"
    fi
  done
  exit 0
fi

# Localizar el código: repositorio local o clon temporal (instalación por curl).
ORIGEN=""
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" 2>/dev/null && pwd || true)"
if [[ -n "$script_dir" && -f "$script_dir/skills/$NOMBRE/SKILL.md" ]]; then
  ORIGEN="$script_dir/skills/$NOMBRE"
else
  command -v git >/dev/null || { echo "Se necesita git para descargar la skill." >&2; exit 1; }
  tmp="$(mktemp -d)"; trap 'rm -rf "$tmp"' EXIT
  git clone --depth 1 -q "$REPO_URL" "$tmp/planea"
  ORIGEN="$tmp/planea/skills/$NOMBRE"
  if [[ $ENLACE -eq 1 ]]; then echo "--enlace requiere ejecutar el instalador desde un clon local." >&2; exit 2; fi
fi

instalar_dependencias() {
  local skill="$1"
  [[ $DEPENDENCIAS -eq 1 ]] || return 0
  local gestor=""
  if command -v bun >/dev/null; then gestor="bun install"
  elif command -v npm >/dev/null; then gestor="npm install --no-audit --no-fund"
  else echo "Aviso: no hay bun ni npm; los kits no tendrán dependencias." >&2; return 0; fi
  for kit in kit-recursos; do
    if [[ -f "$skill/assets/$kit/package.json" ]]; then
      echo "Instalando dependencias de $kit…"
      (cd "$skill/assets/$kit" && $gestor >/dev/null)
    fi
  done
}

instalado=""
for base in "${destinos[@]}"; do
  mkdir -p "$base"
  objetivo="$base/$NOMBRE"
  if [[ -L "$objetivo" || -e "$objetivo" ]]; then
    if [[ -L "$objetivo" ]] || { [[ -f "$objetivo/SKILL.md" ]] && grep -q "^name: $NOMBRE$" "$objetivo/SKILL.md"; }; then
      rm -rf "$objetivo"
    else
      echo "Error: $objetivo existe y no es una instalación de $NOMBRE; no se sobrescribe." >&2; exit 1
    fi
  fi
  if [[ $ENLACE -eq 1 ]]; then
    ln -s "$ORIGEN" "$objetivo"
    [[ -z "$instalado" ]] && instalar_dependencias "$ORIGEN"
  else
    mkdir -p "$objetivo"
    (cd "$ORIGEN" && tar --exclude=node_modules --exclude=dist -cf - .) | (cd "$objetivo" && tar -xf -)
    instalar_dependencias "$objetivo"
  fi
  instalado="$objetivo"
  echo "Instalada: $objetivo"
done

echo
echo "Requisitos opcionales detectados:"
for h in bun chromium python3 pdftoppm pdfinfo; do
  if command -v "$h" >/dev/null; then echo "  ✓ $h"; else echo "  ✗ $h"; fi
done
command -v chromium >/dev/null || command -v google-chrome >/dev/null || command -v chromium-browser >/dev/null \
  || echo "Aviso: sin Chromium no se pueden generar PDF ni capturas." >&2

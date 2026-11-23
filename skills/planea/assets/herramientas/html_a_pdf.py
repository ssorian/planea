#!/usr/bin/env python3
"""Convierte un HTML en PDF con el navegador Chromium/Chrome/Edge ya instalado.

Uso: python3 -I html_a_pdf.py entrada.html salida.pdf [--navegador RUTA] [--espera-ms N]

Solo usa la biblioteca estándar. Respeta el tamaño de @page del CSS.
Códigos de salida: 0 correcto, 1 fallo del navegador, 2 argumentos o entrada
inválidos, 3 no hay navegador disponible.
"""
import argparse
import glob
import ntpath
import os
import posixpath
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

NOMBRES_PATH = (
    "chromium", "chromium-browser", "google-chrome", "google-chrome-stable",
    "microsoft-edge", "msedge", "chrome",
)
LIMITE_SEGUNDOS = 120

MENSAJE_SIN_NAVEGADOR = """\
Error: no se encontró un navegador Chromium, Chrome o Edge.
Alternativas:
  - Instale Google Chrome, Microsoft Edge o Chromium y vuelva a ejecutar.
  - Indique la ruta con --navegador RUTA o con la variable PLANEA_NAVEGADOR.
  - Si la persona usuaria da su permiso, puede descargarse Chromium con Playwright
    (pip install playwright && python -m playwright install chromium).
    No lo haga sin ese permiso."""


def _rutas_habituales(plataforma, env):
    """Rutas fijas de Edge y Chrome, en orden de preferencia (Edge primero)."""
    if plataforma == "win32":
        j = ntpath.join
        bases = []
        for var, defecto in (("ProgramFiles", r"C:\Program Files"),
                             ("ProgramFiles(x86)", r"C:\Program Files (x86)")):
            bases.append(env.get(var) or defecto)
        rutas = [j(b, "Microsoft", "Edge", "Application", "msedge.exe") for b in bases]
        rutas += [j(b, "Google", "Chrome", "Application", "chrome.exe") for b in bases]
        local = env.get("LOCALAPPDATA")
        if local:
            rutas.append(j(local, "Google", "Chrome", "Application", "chrome.exe"))
        return rutas
    if plataforma == "darwin":
        return [
            "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            "/Applications/Chromium.app/Contents/MacOS/Chromium",
        ]
    return []


def _patrones_playwright(plataforma, env):
    if plataforma == "win32":
        local = env.get("LOCALAPPDATA")
        if not local:
            return []
        base = ntpath.join(local, "ms-playwright")
        return [
            ntpath.join(base, "chromium_headless_shell-*", "chrome-headless-shell-win*", "chrome-headless-shell.exe"),
            ntpath.join(base, "chromium-*", "chrome-win*", "chrome.exe"),
        ]
    home = env.get("HOME") or os.path.expanduser("~")
    if plataforma == "darwin":
        base = posixpath.join(home, "Library", "Caches", "ms-playwright")
        return [
            posixpath.join(base, "chromium_headless_shell-*", "chrome-headless-shell-mac*", "chrome-headless-shell"),
            posixpath.join(base, "chromium-*", "chrome-mac*", "Chromium.app", "Contents", "MacOS", "Chromium"),
            posixpath.join(base, "chromium-*", "chrome-mac*", "Google Chrome for Testing.app",
                           "Contents", "MacOS", "Google Chrome for Testing"),
        ]
    base = posixpath.join(home, ".cache", "ms-playwright")
    return [
        posixpath.join(base, "chromium_headless_shell-*", "chrome-headless-shell-linux*", "chrome-headless-shell"),
        posixpath.join(base, "chromium-*", "chrome-linux*", "chrome"),
    ]


def buscar_navegador(explicito=None, which=shutil.which, exists=os.path.exists,
                     env=None, plataforma=None, listar=None):
    """Devuelve la ruta del navegador o None. Todas las dependencias son inyectables.

    Orden: explícito, PLANEA_NAVEGADOR, nombres en PATH, rutas habituales de
    Edge/Chrome, caché de Playwright. Una ruta que no existe se descarta.
    """
    env = os.environ if env is None else env
    plataforma = sys.platform if plataforma is None else plataforma
    listar = listar or (lambda patron: sorted(glob.glob(patron), reverse=True))

    if explicito:
        return explicito if exists(explicito) else None  # una ruta explícita errónea no se sustituye en silencio
    desde_entorno = env.get("PLANEA_NAVEGADOR")
    if desde_entorno and exists(desde_entorno):
        return desde_entorno
    for nombre in NOMBRES_PATH:
        ruta = which(nombre)
        if ruta:
            return ruta
    for ruta in _rutas_habituales(plataforma, env):
        if exists(ruta):
            return ruta
    for patron in _patrones_playwright(plataforma, env):
        for ruta in listar(patron):
            if exists(ruta):
                return ruta
    return None


def construir_comando(navegador, entrada, salida, perfil, espera_ms):
    entrada = Path(entrada).resolve()
    salida = Path(salida).resolve()
    cmd = [
        str(navegador),
        "--headless",
        "--disable-gpu",
        "--no-first-run",
        "--no-default-browser-check",
        "--no-pdf-header-footer",
        "--print-to-pdf=" + str(salida),
        "--user-data-dir=" + str(Path(perfil).resolve()),
    ]
    if espera_ms:
        cmd.append("--virtual-time-budget=%d" % espera_ms)
    cmd.append(entrada.as_uri())
    return cmd


def contar_paginas(datos):
    """Cuenta páginas leyendo el PDF en bruto; None si no es fiable.

    Cuenta objetos /Type /Page y los contrasta con /Count del árbol de páginas.
    """
    if not datos.startswith(b"%PDF"):
        return None
    paginas = len(re.findall(rb"/Type\s*/Page(?![A-Za-z])", datos))
    cuentas = [int(c) for c in re.findall(rb"/Count\s+(\d+)", datos)]
    if paginas == 0:
        return None
    if cuentas and max(cuentas) != paginas:
        return None
    return paginas


class _Formateador(argparse.HelpFormatter):
    def add_usage(self, usage, actions, groups, prefix=None):
        super().add_usage(usage, actions, groups, prefix or "Uso: ")


class _Parser(argparse.ArgumentParser):
    def __init__(self, *a, **kw):
        super().__init__(*a, formatter_class=_Formateador, **kw)
        self._positionals.title = "argumentos"
        self._optionals.title = "opciones"

    def error(self, mensaje):
        self.print_usage(sys.stderr)
        print("Error: argumentos inválidos o incompletos. Use --help para ver la ayuda.", file=sys.stderr)
        self.exit(2)


def _parser():
    p = _Parser(
        prog="html_a_pdf.py",
        usage="%(prog)s entrada.html salida.pdf [--navegador RUTA] [--espera-ms N]",
        description="Convierte un HTML en PDF usando el navegador Chromium, Chrome o Edge del equipo.",
        add_help=False,
    )
    p.add_argument("-h", "--help", action="help", help="muestra esta ayuda y termina")
    p.add_argument("entrada", help="archivo HTML de entrada")
    p.add_argument("salida", help="archivo PDF de salida")
    p.add_argument("--navegador", metavar="RUTA", help="ruta del ejecutable del navegador")
    p.add_argument("--espera-ms", type=int, metavar="N", default=None,
                   help="milisegundos de tiempo virtual para esperar scripts y fuentes")
    return p


def main(argv=None, buscar=buscar_navegador):
    parser = _parser()
    try:
        args = parser.parse_args(argv)
    except SystemExit as e:
        return e.code if e.code in (0, None) else 2
    entrada = Path(args.entrada)
    salida = Path(args.salida)
    if not entrada.is_file():
        print("Error: la entrada no existe: %s" % entrada, file=sys.stderr)
        return 2
    if salida.resolve() == entrada.resolve():
        print("Error: la salida no puede ser el mismo archivo que la entrada.", file=sys.stderr)
        return 2
    if args.espera_ms is not None and args.espera_ms < 0:
        print("Error: --espera-ms debe ser un entero no negativo.", file=sys.stderr)
        return 2
    if args.navegador and not os.path.exists(args.navegador):
        print("Error: el navegador indicado no existe: %s" % args.navegador, file=sys.stderr)
        return 3
    navegador = buscar(explicito=args.navegador)
    if not navegador:
        print(MENSAJE_SIN_NAVEGADOR, file=sys.stderr)
        return 3

    salida.parent.mkdir(parents=True, exist_ok=True)
    if salida.exists():
        salida.unlink()
    perfil = tempfile.mkdtemp(prefix="planea-navegador-")
    try:
        cmd = construir_comando(navegador, entrada, salida, perfil, args.espera_ms)
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=LIMITE_SEGUNDOS,
                                  errors="replace")
        except subprocess.TimeoutExpired:
            print("Error: el navegador superó el límite de %d s." % LIMITE_SEGUNDOS, file=sys.stderr)
            return 1
        except OSError as e:
            print("Error: no se pudo ejecutar el navegador (%s): %s" % (navegador, e), file=sys.stderr)
            return 1
    finally:
        shutil.rmtree(perfil, ignore_errors=True)

    if proc.returncode != 0 or not salida.is_file() or salida.stat().st_size == 0:
        print("Error: el navegador no generó el PDF (código %s)." % proc.returncode, file=sys.stderr)
        if proc.stderr:
            print(proc.stderr.strip()[-800:], file=sys.stderr)
        return 1

    n = contar_paginas(salida.read_bytes())
    if n is None:
        print("OK %s (no se pudo contar las páginas con fiabilidad)" % args.salida)
    else:
        print("OK %s páginas=%d" % (args.salida, n))
    return 0


if __name__ == "__main__":
    sys.exit(main())

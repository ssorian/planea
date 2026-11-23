#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["pymupdf>=1.24,<2"]
# ///
"""Convierte las páginas de un PDF en PNG para revisarlas.

Uso: uv run pdf_vista.py archivo.pdf [--dir DIR] [--dpi 110] [--paginas 1-3]

Con pymupdf (uv run) lo usa; si no puede importarse, recurre a pdftoppm y
pdfinfo (Poppler). Códigos de salida: 0 correcto, 1 fallo al renderizar,
2 argumentos inválidos, 3 no hay motor disponible.
"""
import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path

MENSAJE_SIN_MOTOR = """\
Error: no hay forma de renderizar el PDF.
Opciones:
  - Ejecute con uv, que instala pymupdf por usted: uv run pdf_vista.py archivo.pdf
  - O instale Poppler (pdftoppm y pdfinfo): apt install poppler-utils,
    brew install poppler, o en Windows 'choco install poppler' / 'scoop install poppler'."""


def parsear_paginas(texto, total):
    """'1-3' -> (1, 3); '2' -> (2, 2); None -> (1, total). Recorta el final al total."""
    if not texto:
        return (1, total)
    m = re.fullmatch(r"(\d+)(?:-(\d+))?", texto.strip())
    if not m:
        raise ValueError("rango de páginas inválido: %r (use 2 o 1-3)" % texto)
    a = int(m.group(1))
    b = int(m.group(2)) if m.group(2) else a
    if a < 1 or b < a:
        raise ValueError("rango de páginas inválido: %r" % texto)
    if a > total:
        raise ValueError("el PDF solo tiene %d páginas" % total)
    return (a, min(b, total))


def elegir_motor(tiene_pymupdf, which=shutil.which):
    if tiene_pymupdf:
        return "pymupdf"
    if which("pdftoppm") and which("pdfinfo"):
        return "poppler"
    return None


def _importar_pymupdf():
    try:
        import pymupdf  # noqa: F401
        return pymupdf
    except ImportError:
        try:
            import fitz  # noqa: F401
            return fitz
        except ImportError:
            return None


def _ruta_png(directorio, pdf, n):
    return Path(directorio) / ("%s-p%02d.png" % (pdf.stem, n))


def _informar(total, ancho, alto, rutas):
    print("páginas=%d tamaño=%sx%spt" % (total, _fmt(ancho), _fmt(alto)))
    for r in rutas:
        print(r)


def _fmt(x):
    x = float(x)
    return str(int(round(x))) if abs(x - round(x)) < 0.05 else ("%.1f" % x)


def con_pymupdf(modulo, pdf, directorio, dpi, texto_paginas):
    doc = modulo.open(str(pdf))
    total = doc.page_count
    a, b = parsear_paginas(texto_paginas, total)
    ancho, alto = doc[0].rect.width, doc[0].rect.height
    rutas = []
    for n in range(a, b + 1):
        destino = _ruta_png(directorio, pdf, n)
        doc[n - 1].get_pixmap(dpi=dpi).save(str(destino))
        rutas.append(destino)
    doc.close()
    _informar(total, ancho, alto, rutas)


def con_poppler(pdf, directorio, dpi, texto_paginas):
    info = subprocess.run(["pdfinfo", str(pdf)], capture_output=True, text=True, errors="replace")
    if info.returncode != 0:
        raise RuntimeError("pdfinfo falló: " + info.stderr.strip())
    mp = re.search(r"^Pages:\s+(\d+)", info.stdout, re.M)
    ms = re.search(r"^Page size:\s+([\d.]+)\s+x\s+([\d.]+)", info.stdout, re.M)
    if not mp or not ms:
        raise RuntimeError("no se pudo leer páginas o tamaño con pdfinfo")
    total = int(mp.group(1))
    a, b = parsear_paginas(texto_paginas, total)
    rutas = []
    for n in range(a, b + 1):
        destino = _ruta_png(directorio, pdf, n)
        prefijo = destino.with_suffix("")
        r = subprocess.run(["pdftoppm", "-r", str(dpi), "-f", str(n), "-l", str(n),
                            "-png", "-singlefile", str(pdf), str(prefijo)],
                           capture_output=True, text=True, errors="replace")
        if r.returncode != 0 or not destino.is_file():
            raise RuntimeError("pdftoppm falló en la página %d: %s" % (n, r.stderr.strip()))
        rutas.append(destino)
    _informar(total, ms.group(1), ms.group(2), rutas)


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


def main(argv=None, which=shutil.which, tiene_pymupdf=None):
    p = _Parser(
        prog="pdf_vista.py",
        usage="%(prog)s archivo.pdf [--dir DIR] [--dpi 110] [--paginas 1-3]",
        description="Convierte las páginas de un PDF en imágenes PNG para revisarlas.",
        add_help=False,
    )
    p.add_argument("-h", "--help", action="help", help="muestra esta ayuda y termina")
    p.add_argument("archivo", help="archivo PDF")
    p.add_argument("--dir", metavar="DIR", default=None,
                   help="carpeta de salida (por defecto, la del PDF)")
    p.add_argument("--dpi", type=int, default=110, help="resolución (por defecto 110)")
    p.add_argument("--paginas", metavar="A-B", default=None, help="páginas a generar, p. ej. 1-3")
    try:
        args = p.parse_args(argv)
    except SystemExit as e:
        return e.code if e.code in (0, None) else 2

    pdf = Path(args.archivo)
    if not pdf.is_file():
        print("Error: el PDF no existe: %s" % pdf, file=sys.stderr)
        return 2
    if args.dpi < 10 or args.dpi > 1200:
        print("Error: --dpi debe estar entre 10 y 1200.", file=sys.stderr)
        return 2

    modulo = _importar_pymupdf() if tiene_pymupdf is None else (object() if tiene_pymupdf else None)
    motor = elegir_motor(modulo is not None, which)
    if motor is None:
        print(MENSAJE_SIN_MOTOR, file=sys.stderr)
        return 3

    directorio = Path(args.dir) if args.dir else pdf.resolve().parent
    directorio.mkdir(parents=True, exist_ok=True)
    try:
        if motor == "pymupdf":
            con_pymupdf(modulo, pdf, directorio, args.dpi, args.paginas)
        else:
            con_poppler(pdf, directorio, args.dpi, args.paginas)
    except ValueError as e:
        print("Error: %s" % e, file=sys.stderr)
        return 2
    except Exception as e:  # PDF dañado, fallo del motor
        print("Error al renderizar: %s" % e, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

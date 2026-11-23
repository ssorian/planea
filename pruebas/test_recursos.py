"""Pruebas de html_a_pdf.py y pdf_vista.py (solo biblioteca estándar)."""
import importlib.util
import io
import ntpath
import os
import posixpath
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
HERRAMIENTAS = RAIZ / "skills" / "planea" / "assets" / "herramientas"


def cargar(nombre):
    ruta = HERRAMIENTAS / (nombre + ".py")
    spec = importlib.util.spec_from_file_location(nombre, ruta)
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


def ejecutar(funcion, *args, **kw):
    out, err = io.StringIO(), io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        try:
            codigo = funcion(*args, **kw)
        except SystemExit as e:
            codigo = e.code
    return codigo, out.getvalue(), err.getvalue()


def buscar(modulo, existentes=(), en_path=(), env=None, plataforma="linux", explicito=None, listar=None):
    existentes = set(existentes)
    en_path = dict(en_path)
    return modulo.buscar_navegador(
        explicito=explicito,
        which=lambda n: en_path.get(n),
        exists=lambda p: p in existentes or p in en_path.values(),
        env=env or {},
        plataforma=plataforma,
        listar=listar or (lambda patron: []),
    )


class TestBuscarNavegador(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m = cargar("html_a_pdf")

    def test_explicito_gana_a_todo(self):
        r = buscar(self.m, existentes=["/x/mi"], en_path={"chromium": "/usr/bin/chromium"},
                   env={"PLANEA_NAVEGADOR": "/y/env"}, explicito="/x/mi")
        self.assertEqual(r, "/x/mi")

    def test_variable_entorno_antes_que_path(self):
        r = buscar(self.m, existentes=["/y/env"], en_path={"chromium": "/usr/bin/chromium"},
                   env={"PLANEA_NAVEGADOR": "/y/env"})
        self.assertEqual(r, "/y/env")

    def test_explicito_inexistente_no_se_ignora_en_silencio(self):
        r = buscar(self.m, en_path={"chromium": "/usr/bin/chromium"}, explicito="/no/existe")
        self.assertIsNone(r)

    def test_entorno_inexistente_se_salta(self):
        r = buscar(self.m, en_path={"chromium": "/usr/bin/chromium"},
                   env={"PLANEA_NAVEGADOR": "/no/existe"})
        self.assertEqual(r, "/usr/bin/chromium")

    def test_orden_de_nombres_en_path(self):
        r = buscar(self.m, en_path={"google-chrome": "/u/gc", "chromium-browser": "/u/cb"})
        self.assertEqual(r, "/u/cb")
        r = buscar(self.m, en_path={"msedge": "/u/ms", "chrome": "/u/c"})
        self.assertEqual(r, "/u/ms")

    def test_path_antes_que_rutas_habituales(self):
        edge = ntpath.join(r"C:\Program Files (x86)", "Microsoft", "Edge", "Application", "msedge.exe")
        r = buscar(self.m, existentes=[edge], en_path={"chrome": "C:/c.exe"}, plataforma="win32",
                   env={"ProgramFiles(x86)": r"C:\Program Files (x86)"})
        self.assertEqual(r, "C:/c.exe")

    def test_windows_edge_antes_que_chrome(self):
        env = {"ProgramFiles": r"C:\Program Files", "ProgramFiles(x86)": r"C:\Program Files (x86)"}
        edge = ntpath.join(env["ProgramFiles(x86)"], "Microsoft", "Edge", "Application", "msedge.exe")
        chrome = ntpath.join(env["ProgramFiles"], "Google", "Chrome", "Application", "chrome.exe")
        self.assertEqual(buscar(self.m, existentes=[edge, chrome], env=env, plataforma="win32"), edge)
        self.assertEqual(buscar(self.m, existentes=[chrome], env=env, plataforma="win32"), chrome)

    def test_windows_program_files_antes_que_x86(self):
        env = {"ProgramFiles": r"C:\Program Files", "ProgramFiles(x86)": r"C:\Program Files (x86)"}
        a = ntpath.join(env["ProgramFiles"], "Microsoft", "Edge", "Application", "msedge.exe")
        b = ntpath.join(env["ProgramFiles(x86)"], "Microsoft", "Edge", "Application", "msedge.exe")
        self.assertEqual(buscar(self.m, existentes=[a, b], env=env, plataforma="win32"), a)

    def test_macos_aplicaciones(self):
        chrome = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        edge = "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"
        self.assertEqual(buscar(self.m, existentes=[chrome], plataforma="darwin"), chrome)
        self.assertEqual(buscar(self.m, existentes=[chrome, edge], plataforma="darwin"), edge)

    def test_playwright_es_el_ultimo_recurso(self):
        visto = []

        def listar(patron):
            visto.append(patron)
            return ["/h/.cache/ms-playwright/chromium-1100/chrome-linux/chrome"]

        r = buscar(self.m, existentes=["/h/.cache/ms-playwright/chromium-1100/chrome-linux/chrome"],
                   listar=listar, plataforma="linux")
        self.assertTrue(r.endswith("chrome-linux/chrome"))
        self.assertTrue(any("ms-playwright" in p for p in visto))
        # con un navegador en PATH, ni siquiera se consulta la caché
        visto.clear()
        r = buscar(self.m, en_path={"chromium": "/usr/bin/chromium"}, listar=listar)
        self.assertEqual(r, "/usr/bin/chromium")
        self.assertEqual(visto, [])

    def test_nada_devuelve_none(self):
        for plat in ("linux", "win32", "darwin"):
            self.assertIsNone(buscar(self.m, plataforma=plat))


class TestComandoYUtilidades(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m = cargar("html_a_pdf")

    def test_comando_basico(self):
        with tempfile.TemporaryDirectory(dir=_tmp()) as d:
            entrada = Path(d) / "a b.html"
            salida = Path(d) / "s.pdf"
            cmd = self.m.construir_comando("/usr/bin/chromium", entrada, salida, Path(d) / "perfil", None)
        self.assertEqual(cmd[0], "/usr/bin/chromium")
        self.assertIn("--headless", cmd)
        self.assertIn("--no-pdf-header-footer", cmd)
        self.assertIn("--print-to-pdf=" + str(salida.resolve()), cmd)
        self.assertTrue(any(a.startswith("--user-data-dir=") for a in cmd))
        self.assertTrue(cmd[-1].startswith("file://"))
        self.assertIn("%20", cmd[-1])
        self.assertFalse(any(a.startswith("--virtual-time-budget") for a in cmd))

    def test_espera_ms_a_virtual_time_budget(self):
        cmd = self.m.construir_comando("n", Path("/tmp/a.html"), Path("/tmp/s.pdf"), Path("/tmp/p"), 1500)
        self.assertIn("--virtual-time-budget=1500", cmd)

    def test_contar_paginas(self):
        pdf = b"%PDF-1.4\n1 0 obj\n<</Type /Pages /Count 2 /Kids [2 0 R 3 0 R]>>\nendobj\n" \
              b"2 0 obj\n<</Type /Page /Parent 1 0 R>>\nendobj\n3 0 obj\n<</Type/Page/Parent 1 0 R>>\nendobj\n"
        self.assertEqual(self.m.contar_paginas(pdf), 2)

    def test_contar_paginas_no_fiable_devuelve_none(self):
        self.assertIsNone(self.m.contar_paginas(b"no es un pdf"))
        discrepa = b"<</Type /Pages /Count 5>> <</Type /Page>>"
        self.assertIsNone(self.m.contar_paginas(discrepa))


class TestCodigosDeSalida(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m = cargar("html_a_pdf")

    def test_sin_navegador_codigo_3_con_alternativa(self):
        with tempfile.TemporaryDirectory(dir=_tmp()) as d:
            h = Path(d) / "a.html"
            h.write_text("<p>hola</p>", encoding="utf-8")
            codigo, out, err = ejecutar(self.m.main, [str(h), str(Path(d) / "s.pdf")],
                                        buscar=lambda explicito=None: None)
        self.assertEqual(codigo, 3)
        texto = err.lower()
        self.assertIn("chrome", texto)
        self.assertIn("edge", texto)
        self.assertIn("chromium", texto)
        self.assertIn("playwright", texto)
        self.assertIn("permiso", texto)

    def test_entrada_inexistente_error_claro(self):
        with tempfile.TemporaryDirectory(dir=_tmp()) as d:
            codigo, out, err = ejecutar(self.m.main, [str(Path(d) / "no.html"), str(Path(d) / "s.pdf")],
                                        buscar=lambda explicito=None: "/x")
        self.assertEqual(codigo, 2)
        self.assertIn("no existe", err)

    def test_no_sobrescribe_la_entrada(self):
        with tempfile.TemporaryDirectory(dir=_tmp()) as d:
            h = Path(d) / "a.html"
            h.write_text("<p>hola</p>", encoding="utf-8")
            codigo, out, err = ejecutar(self.m.main, [str(h), str(h)],
                                        buscar=lambda explicito=None: "/x")
            self.assertNotEqual(codigo, 0)
            self.assertEqual(h.read_text(encoding="utf-8"), "<p>hola</p>")
        self.assertIn("entrada", err)

    def test_ayuda_en_espanol(self):
        codigo, out, err = ejecutar(self.m.main, ["--help"])
        self.assertEqual(codigo, 0)
        self.assertIn("--navegador", out)
        self.assertIn("--espera-ms", out)
        self.assertIn("Uso:", out)
        self.assertIn("argumentos", out)
        self.assertNotIn("usage", out.lower())
        self.assertNotIn("positional", out.lower())

    def test_error_de_argumentos_en_espanol_codigo_2(self):
        codigo, out, err = ejecutar(self.m.main, [])
        self.assertEqual(codigo, 2)
        self.assertIn("Error", err)
        self.assertNotIn("the following", err)


def _tmp():
    d = Path(os.environ.get("PLANEA_TMP", "/tmp/planea-work/out-recursos"))
    if sys.platform == "win32" or not d.parent.exists():
        return None
    d.mkdir(parents=True, exist_ok=True)
    return str(d)


def _html_dos_paginas(css_page="size: letter; margin: 0"):
    return ("<!doctype html><meta charset='utf-8'><style>@page{%s} body{margin:0;font-family:sans-serif} h1{margin:0}"
            ".p{page-break-after:always;height:5in}</style>"
            "<div class='p'><h1>Página uno</h1></div><div><h1>Página dos</h1></div>") % css_page


def _mediabox(pdf_bytes):
    m = re.search(rb"/MediaBox\s*\[\s*0\s+0\s+([\d.]+)\s+([\d.]+)\s*\]", pdf_bytes)
    return (float(m.group(1)), float(m.group(2))) if m else None


NAVEGADOR = None
try:
    NAVEGADOR = cargar("html_a_pdf").buscar_navegador()
except Exception:  # pragma: no cover
    NAVEGADOR = None


@unittest.skipUnless(NAVEGADOR, "No hay navegador Chromium/Chrome/Edge detectable")
class TestIntegracionNavegador(unittest.TestCase):
    def _convertir(self, css_page):
        with tempfile.TemporaryDirectory(dir=_tmp()) as d:
            h = Path(d) / "doc.html"
            h.write_text(_html_dos_paginas(css_page), encoding="utf-8")
            pdf = Path(d) / "doc.pdf"
            proc = subprocess.run(
                [sys.executable, "-I", str(HERRAMIENTAS / "html_a_pdf.py"), str(h), str(pdf)],
                capture_output=True, text=True, timeout=180)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            return proc.stdout, pdf.read_bytes(), h.read_text(encoding="utf-8")

    def test_dos_paginas_carta(self):
        out, datos, html = self._convertir("size: letter; margin: 0")
        self.assertIn("OK ", out)
        self.assertIn("páginas=2", out)
        self.assertEqual(_mediabox(datos), (612.0, 792.0))
        self.assertIn("Página uno", html)

    def test_tamano_propio_a5(self):
        out, datos, _ = self._convertir("size: 148mm 210mm; margin: 0")
        w, h = _mediabox(datos)
        self.assertAlmostEqual(w, 148 / 25.4 * 72, delta=1.5)
        self.assertAlmostEqual(h, 210 / 25.4 * 72, delta=1.5)


def _pdf_minimo(n_paginas=2, w=612, h=792):
    objs = [b"<</Type /Catalog /Pages 2 0 R>>"]
    kids = " ".join("%d 0 R" % (3 + i) for i in range(n_paginas))
    objs.append(("<</Type /Pages /Count %d /Kids [%s]>>" % (n_paginas, kids)).encode())
    for _ in range(n_paginas):
        objs.append(("<</Type /Page /Parent 2 0 R /MediaBox [0 0 %d %d]>>" % (w, h)).encode())
    cuerpo = b"%PDF-1.4\n"
    offs = []
    for i, o in enumerate(objs, 1):
        offs.append(len(cuerpo))
        cuerpo += b"%d 0 obj\n" % i + o + b"\nendobj\n"
    xref = len(cuerpo)
    cuerpo += b"xref\n0 %d\n0000000000 65535 f \n" % (len(objs) + 1)
    for o in offs:
        cuerpo += b"%010d 00000 n \n" % o
    cuerpo += b"trailer\n<</Size %d /Root 1 0 R>>\nstartxref\n%d\n%%%%EOF\n" % (len(objs) + 1, xref)
    return cuerpo


class TestPdfVistaPuro(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m = cargar("pdf_vista")

    def test_rango_de_paginas(self):
        self.assertEqual(self.m.parsear_paginas("1-3", 10), (1, 3))
        self.assertEqual(self.m.parsear_paginas("2", 10), (2, 2))
        self.assertEqual(self.m.parsear_paginas(None, 4), (1, 4))
        self.assertEqual(self.m.parsear_paginas("2-99", 4), (2, 4))

    def test_rango_invalido(self):
        for malo in ("0-2", "3-1", "a-b", "5"):
            with self.assertRaises(ValueError):
                self.m.parsear_paginas(malo, 4)

    def test_elegir_motor(self):
        hay = lambda n: "/usr/bin/" + n
        self.assertEqual(self.m.elegir_motor(True, hay), "pymupdf")
        self.assertEqual(self.m.elegir_motor(False, hay), "poppler")
        self.assertIsNone(self.m.elegir_motor(False, lambda n: None))
        self.assertIsNone(self.m.elegir_motor(False, lambda n: "/x/pdftoppm" if n == "pdftoppm" else None))

    def test_sin_motor_codigo_3_con_instrucciones(self):
        with tempfile.TemporaryDirectory(dir=_tmp()) as d:
            pdf = Path(d) / "a.pdf"
            pdf.write_bytes(_pdf_minimo())
            codigo, out, err = ejecutar(self.m.main, [str(pdf), "--dir", d],
                                        which=lambda n: None, tiene_pymupdf=False)
        self.assertEqual(codigo, 3)
        self.assertIn("uv run", err)
        self.assertIn("poppler", err.lower())

    def test_pdf_inexistente(self):
        codigo, out, err = ejecutar(self.m.main, ["/no/existe.pdf"], which=lambda n: None,
                                    tiene_pymupdf=False)
        self.assertEqual(codigo, 2)
        self.assertIn("no existe", err)


@unittest.skipUnless(shutil.which("pdftoppm") and shutil.which("pdfinfo"), "Poppler no disponible")
class TestPdfVistaPoppler(unittest.TestCase):
    def test_renderiza_por_poppler(self):
        m = cargar("pdf_vista")
        with tempfile.TemporaryDirectory(dir=_tmp()) as d:
            pdf = Path(d) / "doc.pdf"
            pdf.write_bytes(_pdf_minimo(3))
            salida = Path(d) / "png"
            codigo, out, err = ejecutar(m.main, [str(pdf), "--dir", str(salida), "--dpi", "50",
                                                 "--paginas", "1-2"], tiene_pymupdf=False)
            self.assertEqual(codigo, 0, err)
            lineas = out.strip().splitlines()
            self.assertEqual(lineas[0], "páginas=3 tamaño=612x792pt")
            self.assertEqual(len(lineas), 3)
            for i, l in enumerate(lineas[1:], 1):
                self.assertTrue(l.endswith("doc-p%02d.png" % i), l)
                self.assertEqual(Path(l).read_bytes()[:8], b"\x89PNG\r\n\x1a\n")
            self.assertFalse((salida / "doc-p03.png").exists())


if __name__ == "__main__":
    unittest.main()

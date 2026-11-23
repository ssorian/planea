#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Pruebas de skills/planea/assets/herramientas/docx_tool.py (solo unittest).

Las fixtures se generan aquí con zipfile y cadenas XML; no hay binarios en el repo.
Ejecutar: python3 -I pruebas/test_docx_tool.py   (o python3 -m unittest pruebas.test_docx_tool)
"""
import contextlib
import io
import json
import os
import re
import struct
import sys
import tempfile
import unittest
import zipfile
import zlib
import xml.etree.ElementTree as ET
from pathlib import Path

HERR = Path(__file__).resolve().parents[1] / 'skills' / 'planea' / 'assets' / 'herramientas'
sys.path.insert(0, str(HERR))
if os.environ.get('DOCX_TOOL_PATH'):      # p. ej. contrastar la clase Regresion con una versión anterior
    import importlib.util
    _spec = importlib.util.spec_from_file_location('docx_tool', os.environ['DOCX_TOOL_PATH'])
    T = importlib.util.module_from_spec(_spec)
    sys.modules['docx_tool'] = T
    _spec.loader.exec_module(T)
else:
    import docx_tool as T  # noqa: E402

W = T.W_NS
WN = '{%s}' % W
NS_BASE = ('xmlns:w="%s" xmlns:r="%s" xmlns:w14="%s" xmlns:mc="%s" mc:Ignorable="w14"' % (
    W, T.R_NS, T.KNOWN_NS['w14'], T.KNOWN_NS['mc']))
NS_DRAW = ' xmlns:wp="%s" xmlns:a="%s" xmlns:pic="%s"' % (T.KNOWN_NS['wp'], T.KNOWN_NS['a'], T.KNOWN_NS['pic'])

CT = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
      '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
      '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
      '<Default Extension="xml" ContentType="application/xml"/>'
      '<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
      '</Types>')
RELS = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" Type="%s/officeDocument" Target="word/document.xml"/></Relationships>' % T.R_NS)
DOCRELS = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
           '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"></Relationships>')
SECT = ('<w:sectPr><w:pgSz w:w="12240" w:h="15840"/>'
        '<w:pgMar w:top="1440" w:right="1440" w:bottom="1440" w:left="1440" w:header="720" w:footer="720" w:gutter="0"/></w:sectPr>')


# ------------------------------------------------------------ generadores XML
def r_(text, bold=False, rpr=''):
    b = '<w:b/><w:bCs/>' if bold else ''
    inner = rpr + b
    sp = ' xml:space="preserve"' if text != text.strip() else ''
    return '<w:r>%s<w:t%s>%s</w:t></w:r>' % ('<w:rPr>%s</w:rPr>' % inner if inner else '', sp, T.esc(text))


def p_(*runs, ppr=''):
    return '<w:p>%s%s</w:p>' % ('<w:pPr>%s</w:pPr>' % ppr if ppr else '', ''.join(runs))


def tc_(*content, w=None, span=None, vm=None):
    pr = ''
    if w:
        pr += '<w:tcW w:w="%d" w:type="dxa"/>' % w
    if span:
        pr += '<w:gridSpan w:val="%d"/>' % span
    if vm == 'restart':
        pr += '<w:vMerge w:val="restart"/>'
    elif vm == 'continue':
        pr += '<w:vMerge/>'
    body = ''.join(content) or '<w:p/>'
    return '<w:tc>%s%s</w:tc>' % ('<w:tcPr>%s</w:tcPr>' % pr if pr else '', body)


def tr_(*cells, pr=''):
    return '<w:tr>%s%s</w:tr>' % ('<w:trPr>%s</w:trPr>' % pr if pr else '', ''.join(cells))


def tbl_(grid, *rows):
    g = ''.join('<w:gridCol w:w="%d"/>' % x for x in grid)
    return '<w:tbl><w:tblPr><w:tblW w:w="0" w:type="auto"/></w:tblPr><w:tblGrid>%s</w:tblGrid>%s</w:tbl>' % (g, ''.join(rows))


def make_docx(path, body, ns=NS_BASE, sect=SECT, extra=None, content_types=CT, docrels=DOCRELS):
    doc = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<w:document %s><w:body>%s%s</w:body></w:document>'
           % (ns, body, sect))
    with zipfile.ZipFile(str(path), 'w', zipfile.ZIP_DEFLATED) as z:
        z.writestr('[Content_Types].xml', content_types)
        z.writestr('_rels/.rels', RELS)
        z.writestr('word/document.xml', doc)
        if docrels is not None:
            z.writestr('word/_rels/document.xml.rels', docrels)
        for n, b in (extra or {}).items():
            z.writestr(n, b)
    return Path(path)


def png_bytes(w, h, color=(200, 30, 30)):
    def chunk(t, d):
        c = struct.pack('>I', len(d)) + t + d
        return c + struct.pack('>I', zlib.crc32(t + d) & 0xffffffff)
    raw = b''.join(b'\x00' + bytes(color) * w for _ in range(h))
    return (b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 2, 0, 0, 0))
            + chunk(b'IDAT', zlib.compress(raw)) + chunk(b'IEND', b''))


def gif_bytes(w, h):
    return b'GIF89a' + struct.pack('<HH', w, h) + b'\x00\x00\x00' + b';'


def jpeg_bytes(w, h, with_dht_first=True):
    """JPEG mínimo (no decodificable) con cabeceras válidas para leer el tamaño."""
    out = b'\xff\xd8' + b'\xff\xe0' + struct.pack('>H', 16) + b'JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00'
    if with_dht_first:
        out += b'\xff\xc4' + struct.pack('>H', 6) + b'\x00\x01\x02\x03'   # DHT con bytes parecidos a un SOF
    out += b'\xff\xc0' + struct.pack('>HBHHB', 11, 8, h, w, 1) + b'\x01\x11\x00'
    return out + b'\xff\xd9'


# ---------------------------------------------------------------- lectura
def run(*args):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        try:
            code = T.main([str(a) for a in args])
        except SystemExit as e:      # argparse
            code = e.code
    return code, out.getvalue(), err.getvalue()


def unesc(x):
    return T.unesc(x)


def zread(path, name):
    with zipfile.ZipFile(str(path)) as z:
        return z.read(name).decode('utf-8')


def doc_xml(path):
    return zread(path, 'word/document.xml')


def root_of(path):
    return ET.fromstring(doc_xml(path).encode('utf-8'))


def body_tables(root):
    return root.find(WN + 'body').findall(WN + 'tbl')


def trs(tbl):
    return tbl.findall(WN + 'tr')


def tcs(tr):
    return tr.findall(WN + 'tc')


def run_info(p):
    """[(texto, negrita)] de los runs con texto de un párrafo (ElementTree, independiente de la herramienta)."""
    out = []
    for r in p.iter(WN + 'r'):
        txt = ''
        for k in r:
            if k.tag == WN + 't':
                txt += k.text or ''
            elif k.tag == WN + 'tab':
                txt += '\t'
            elif k.tag == WN + 'br':
                txt += '\n'
        if txt:
            rpr = r.find(WN + 'rPr')
            b = rpr.find(WN + 'b') if rpr is not None else None
            bold = b is not None and b.get(WN + 'val', '1').lower() not in ('0', 'false', 'off')
            out.append((txt, bold))
    return out


def tags(el):
    return [k.tag.replace(WN, '') for k in el]


def cell_at(path, t, f, c):
    return tcs(trs(body_tables(root_of(path))[t])[f])[c]


class Base(unittest.TestCase):
    def setUp(self):
        self._td = tempfile.TemporaryDirectory()
        self.addCleanup(self._td.cleanup)
        self.dir = Path(self._td.name)

    def f(self, name):
        return self.dir / name

    def ok(self, *args):
        code, out, err = run(*args)
        self.assertEqual(code, 0, 'código %r\nstdout: %s\nstderr: %s' % (code, out, err))
        return out

    def fallo(self, code_expected, *args):
        code, out, err = run(*args)
        self.assertEqual(code, code_expected, 'código %r\nstdout: %s\nstderr: %s' % (code, out, err))
        return out, err

    def jsonf(self, name, obj):
        p = self.f(name)
        p.write_text(json.dumps(obj, ensure_ascii=False), encoding='utf-8')
        return p


# =========================================================== 1. negrita parcial
RPR_F = '<w:rFonts w:ascii="Arial" w:hAnsi="Arial"/><w:sz w:val="20"/>'


def doc_bold(path):
    """Tabla 1x2: celda 0 con el párrafo del caso de aceptación; celda 1 con un párrafo vacío."""
    p = p_(r_('Inicio. ', True, RPR_F), r_('Se verá el video (', False, RPR_F),
           r_('Anexo 7', True, RPR_F), r_(').', False, RPR_F))
    body = tbl_([4000, 4000], tr_(tc_(p, w=4000), tc_(p_(), w=4000)))
    return make_docx(path, body)


class NegritaParcial(Base):
    def edit(self, changes, body=None):
        src = self.f('a.docx')
        if body is None:
            doc_bold(src)
        else:
            make_docx(src, body)
        cj = self.jsonf('c.json', changes)
        return src, run('editar-celdas', src, cj, '-o', self.f('b.docx'))

    def test_caso_de_aceptacion(self):
        src, (code, out, err) = self.edit({'T0F0C0': '**Desarrollo.** Se leerá Identidad cultural (**Anexo 3**).'})
        self.assertEqual(code, 0, err)
        p = cell_at(self.f('b.docx'), 0, 0, 0).find(WN + 'p')
        self.assertEqual(run_info(p), [('Desarrollo.', True), (' Se leerá Identidad cultural (', False),
                                       ('Anexo 3', True), (').', False)])

    def test_rpr_base_y_posicion_de_negrita(self):
        self.edit({'T0F0C0': 'a **b** c'})
        p = cell_at(self.f('b.docx'), 0, 0, 0).find(WN + 'p')
        rprs = [tags(r.find(WN + 'rPr')) for r in p.iter(WN + 'r') if r.find(WN + 't') is not None]
        self.assertEqual(rprs, [['rFonts', 'sz'], ['rFonts', 'b', 'bCs', 'sz'], ['rFonts', 'sz']])

    def test_negrita_tras_rstyle_y_rfonts_o_al_inicio(self):
        rp = '<w:rStyle w:val="X"/><w:rFonts w:ascii="Arial"/><w:color w:val="FF0000"/>'
        body = tbl_([4000], tr_(tc_(p_(r_('hola', False, rp)), p_(r_('otro')))))
        self.edit({'T0F0C0': ['**a** b', '**c**']}, body)
        ps = cell_at(self.f('b.docx'), 0, 0, 0).findall(WN + 'p')
        self.assertEqual(tags(ps[0].findall(WN + 'r')[0].find(WN + 'rPr')), ['rStyle', 'rFonts', 'b', 'bCs', 'color'])
        # segundo párrafo: el run original no tiene rPr -> la negrita queda al inicio
        r2 = ps[1].findall(WN + 'r')[0]
        self.assertEqual(tags(r2.find(WN + 'rPr')), ['b', 'bCs'])

    def test_rpr_base_sin_negrita_aunque_el_run_original_la_tuviera(self):
        body = tbl_([4000], tr_(tc_(p_(r_('negro', True, RPR_F)))))
        self.edit({'T0F0C0': '**x** y'}, body)
        p = cell_at(self.f('b.docx'), 0, 0, 0).find(WN + 'p')
        self.assertEqual(run_info(p), [('x', True), (' y', False)])

    def test_asterisco_escapado_y_sin_marcas(self):
        self.edit({'T0F0C0': 'a \\* b **c\\*d** e', 'T0F0C1': 'precio 5\\*3'})
        d = self.f('b.docx')
        self.assertEqual(run_info(cell_at(d, 0, 0, 0).find(WN + 'p')),
                         [('a * b ', False), ('c*d', True), (' e', False)])
        self.assertEqual(run_info(cell_at(d, 0, 0, 1).find(WN + 'p')), [('precio 5*3', False)])

    def test_sin_cerrar_error_con_coordenada_y_sin_escribir(self):
        src = self.f('a.docx')
        doc_bold(src)
        cj = self.jsonf('c.json', {'T0F0C1': 'bien', 'T0F0C0': 'texto **sin cerrar'})
        out, err = self.fallo(2, 'editar-celdas', src, cj, '-o', self.f('b.docx'))
        self.assertIn('T0F0C0', err)
        self.assertIn('**', err)
        self.assertFalse(self.f('b.docx').exists())

    def test_sin_marcas_identico_al_comportamiento_actual(self):
        body = tbl_([4000], tr_(tc_(p_(r_('viejo', True, RPR_F), r_(' resto')))))
        self.edit({'T0F0C0': 'nuevo'}, body)
        x = doc_xml(self.f('b.docx'))
        self.assertIn('<w:p><w:r><w:rPr>%s<w:b/><w:bCs/></w:rPr><w:t>nuevo</w:t></w:r><w:r></w:r></w:p>' % RPR_F, x)

    def test_dibujos_y_campos_no_se_borran(self):
        dr = '<w:r><w:drawing><wp:inline/></w:drawing></w:r>'
        fl = '<w:r><w:fldChar w:fldCharType="begin"/></w:r><w:r><w:instrText> PAGE </w:instrText></w:r>'
        body = tbl_([4000], tr_(tc_(p_(dr, r_('viejo'), fl, r_('otro')))))
        src = self.f('a.docx')
        make_docx(src, body, ns=NS_BASE + NS_DRAW)
        cj = self.jsonf('c.json', {'T0F0C0': '**N** m'})
        self.ok('editar-celdas', src, cj, '-o', self.f('b.docx'))
        x = doc_xml(self.f('b.docx'))
        for frag in ('<w:drawing><wp:inline/></w:drawing>', '<w:fldChar w:fldCharType="begin"/>', '<w:instrText> PAGE </w:instrText>'):
            self.assertIn(frag, x)
        self.assertEqual(run_info(cell_at(self.f('b.docx'), 0, 0, 0).find(WN + 'p')), [('N', True), (' m', False)])

    def test_run_con_texto_y_dibujo_conserva_el_dibujo(self):
        mixed = '<w:r><w:t>viejo</w:t><w:drawing><wp:inline/></w:drawing></w:r>'
        body = tbl_([4000], tr_(tc_(p_(mixed))))
        src = self.f('a.docx')
        make_docx(src, body, ns=NS_BASE + NS_DRAW)
        cj = self.jsonf('c.json', {'T0F0C0': '**N** m'})
        self.ok('editar-celdas', src, cj, '-o', self.f('b.docx'))
        self.assertIn('<w:drawing><wp:inline/></w:drawing>', doc_xml(self.f('b.docx')))
        self.assertEqual(run_info(cell_at(self.f('b.docx'), 0, 0, 0).find(WN + 'p')), [('N', True), (' m', False)])

    def test_salto_y_tabulador_dentro_de_segmento(self):
        self.edit({'T0F0C0': '**a\nb** c\td'})
        p = cell_at(self.f('b.docx'), 0, 0, 0).find(WN + 'p')
        self.assertEqual(run_info(p), [('a\nb', True), (' c\td', False)])
        self.assertIn('<w:br/>', doc_xml(self.f('b.docx')))

    def test_parrafos_nuevos_y_celda_sin_runs(self):
        body = tbl_([4000], tr_(tc_(p_(r_('uno', False, RPR_F), ppr='<w:jc w:val="center"/>'))))
        self.edit({'T0F0C0': ['**a** x', 'y **b**']}, body)
        ps = cell_at(self.f('b.docx'), 0, 0, 0).findall(WN + 'p')
        self.assertEqual([run_info(p) for p in ps], [[('a', True), (' x', False)], [('y ', False), ('b', True)]])
        self.assertEqual(tags(ps[1].find(WN + 'pPr')), ['jc'])
        # párrafo vacío autocerrado
        body = tbl_([4000], tr_(tc_('<w:p w:rsidR="00AA"/>')))
        self.edit({'T0F0C0': '**solo**'}, body)
        self.assertEqual(run_info(cell_at(self.f('b.docx'), 0, 0, 0).find(WN + 'p')), [('solo', True)])

    def test_resultado_bien_formado_y_verificar_ok(self):
        self.edit({'T0F0C0': '**a** & <b> **c**'})
        ET.fromstring(doc_xml(self.f('b.docx')).encode('utf-8'))
        self.assertEqual(run_info(cell_at(self.f('b.docx'), 0, 0, 0).find(WN + 'p')),
                         [('a', True), (' & <b> ', False), ('c', True)])


# =============================================================== 2. leer-celdas
class LeerCeldas(Base):
    def build(self):
        nested = tbl_([1000, 1000], tr_(tc_(p_(r_('n1'))), tc_(p_(r_('n2')))))
        p1 = p_(r_('Inicio.', True), r_(' ', True), r_('Dos', True), r_(' normal ('), r_('Anexo 7', True), r_(').'))
        p2 = p_(r_('cero', False, '<w:b w:val="0"/>'), r_(' f', False, '<w:b w:val="false"/>'),
                r_(' o', False, '<w:b w:val="off"/>'), r_(' x*y', True, '<w:b w:val="1"/>'))
        body = (tbl_([3000, 3000], tr_(tc_(p1, p2, w=3000), tc_(p_(r_('B')), nested, p_(), w=3000)),
                     tr_(tc_(p_(r_('c0'))), tc_(p_(r_('c1'))))) +
                p_(r_('fuera')))
        return make_docx(self.f('a.docx'), body)

    def leer(self, *coords):
        out = self.ok('leer-celdas', self.f('a.docx'), *coords)
        return json.loads(out), out

    def test_negrita_union_de_runs_y_escape(self):
        self.build()
        d, raw = self.leer('T0F0C0')
        self.assertEqual(d['T0F0C0'], ['**Inicio. Dos** normal (**Anexo 7**).', 'cero f o** x\\*y**'])

    def test_forma_de_fila_y_json_sin_ascii_escapado(self):
        self.build()
        make_docx(self.f('a.docx'), tbl_([3000], tr_(tc_(p_(r_('Ñandú ✓'))), tc_(p_(r_('b'))))))
        d, raw = self.leer('T0F0')
        self.assertEqual(list(d), ['T0F0C0', 'T0F0C1'])
        self.assertIn('Ñandú ✓', raw)

    def test_tabla_anidada_se_anota_y_se_lee_por_coordenada(self):
        self.build()
        d, _ = self.leer('T0F0C1', 'T0F0C1.T0F0C1', 'T0F0C1.T0F0')
        self.assertEqual(d['T0F0C1.T0'], '(tabla anidada 1x2)')
        self.assertEqual(d['T0F0C1.T0F0C1'], ['n2'])
        self.assertEqual(d['T0F0C1.T0F0C0'], ['n1'])
        self.assertEqual(d['T0F0C1'][0], 'B')
        self.assertNotIn('n1', json.dumps(d['T0F0C1']))

    def test_coordenada_invalida_es_error_de_uso(self):
        self.build()
        out, err = self.fallo(2, 'leer-celdas', self.f('a.docx'), 'T9F0C0')
        self.assertIn('T9', err)
        self.fallo(2, 'leer-celdas', self.f('a.docx'), 'xx')

    def test_ida_y_vuelta_conserva_texto_y_negrita(self):
        self.build()
        d, _ = self.leer('T0F0C0', 'T0F0C1', 'T0F1')
        cj = self.jsonf('rt.json', d)
        self.ok('editar-celdas', self.f('a.docx'), cj, '-o', self.f('b.docx'))
        orig, new = root_of(self.f('a.docx')), root_of(self.f('b.docx'))

        def snap(root):
            out = []
            for tc in root.iter(WN + 'tc'):
                for p in tc.findall(WN + 'p'):
                    # une runs contiguos del mismo tipo
                    segs = []
                    for t, b in run_info(p):
                        if segs and segs[-1][1] == b:
                            segs[-1] = (segs[-1][0] + t, b)
                        else:
                            segs.append((t, b))
                    out.append(segs)
            return out
        self.assertEqual(snap(orig), snap(new))
        # y la segunda lectura es idéntica a la primera
        make_docx(self.f('a.docx'), '')   # sin efecto sobre b
        code, out, _ = run('leer-celdas', self.f('b.docx'), 'T0F0C0', 'T0F0C1', 'T0F1')
        self.assertEqual(json.loads(out), d)



# ================================================ 3. lectura más barata
def doc_rows(path, n=8):
    """T0 con 3 columnas y n filas: F0 encabezado; F1..F3 con C0 combinada (restart + 2 continue); resto normales."""
    rows = [tr_(tc_(p_(r_('H0')), w=1000), tc_(p_(r_('H1')), w=2000), tc_(p_(r_('H2')), w=3000))]
    for i in range(1, n):
        vm = 'restart' if i == 1 else ('continue' if i in (2, 3) else None)
        c0 = p_(r_('G')) if i == 1 else (p_() if i in (2, 3) else p_(r_('x%d' % i)))
        rows.append(tr_(tc_(c0, w=1000, vm=vm), tc_(p_(r_('a%d' % i)), w=2000), tc_(p_(r_('b%d' % i)), w=3000)))
    body = p_(r_('intro')) + tbl_([1000, 2000, 3000], *rows) + p_() + tbl_([500], tr_(tc_(p_(r_('otra'))))) + p_(r_('fin'))
    return make_docx(path, body)


class LecturaBarata(Base):
    def test_mapa_solo_tablas(self):
        doc_rows(self.f('a.docx'))
        out = self.ok('mapa', self.f('a.docx'), '--solo-tablas')
        lines = out.strip().splitlines()
        self.assertEqual(len(lines), 2)
        self.assertTrue(lines[0].startswith('B1 T0 8x3'))
        self.assertTrue(lines[1].startswith('B3 T1 1x1'))
        out = self.ok('mapa', self.f('a.docx'), '--solo-tablas', '--desde', '2')
        self.assertEqual(len(out.strip().splitlines()), 1)

    def test_mapa_sin_opcion_no_cambia(self):
        doc_rows(self.f('a.docx'))
        out = self.ok('mapa', self.f('a.docx'))
        self.assertEqual(len(out.strip().splitlines()), 6)   # 5 hijos + sectPr
        self.assertIn('B0 P "intro"', out)

    def test_tablas_filas_rango_inclusivo(self):
        doc_rows(self.f('a.docx'))
        out = self.ok('tablas', self.f('a.docx'), '--tabla', '0', '--filas', '2-3')
        lines = out.strip().splitlines()
        self.assertTrue(lines[0].startswith('# T0 8x3'))
        self.assertEqual([l.split()[0] for l in lines[1:]], ['T0F2C0', 'T0F2C1', 'T0F2C2', 'T0F3C0', 'T0F3C1', 'T0F3C2'])

    def test_tablas_una_fila_y_errores(self):
        doc_rows(self.f('a.docx'))
        out = self.ok('tablas', self.f('a.docx'), '--tabla', '0', '--filas', '5')
        self.assertEqual([l.split()[0] for l in out.strip().splitlines()[1:]], ['T0F5C0', 'T0F5C1', 'T0F5C2'])
        self.fallo(2, 'tablas', self.f('a.docx'), '--filas', '1-2')
        self.fallo(2, 'tablas', self.f('a.docx'), '--tabla', '0', '--filas', '9')
        self.fallo(2, 'tablas', self.f('a.docx'), '--tabla', '0', '--filas', '4-2')
        self.fallo(2, 'tablas', self.f('a.docx'), '--tabla', '0', '--filas', 'x')
        full = self.ok('tablas', self.f('a.docx'), '--tabla', '0')
        self.assertEqual(len(full.strip().splitlines()), 1 + 8 * 3)


# ============================================================ 4. duplicar-fila
def doc_dup(path):
    """F1 (restart) con paraId, dibujo con docPr y marcador; C2 con tabla anidada de 2 filas."""
    nested = tbl_([500, 500], tr_(tc_(p_(r_('n1'))), tc_(p_(r_('n2')))), tr_(tc_(p_(r_('m1'))), tc_(p_(r_('m2')))))
    dr = ('<w:r><w:drawing><wp:inline><wp:extent cx="10" cy="10"/><wp:docPr id="5" name="Imagen 5"/>'
          '</wp:inline></w:drawing></w:r>')
    para = ('<w:p w14:paraId="0000AAAA" w14:textId="0000BBBB"><w:pPr><w:jc w:val="center"/>'
            '<w:rPr><w:b/></w:rPr></w:pPr><w:bookmarkStart w:id="3" w:name="marca"/>'
            '<w:r><w:rPr><w:rFonts w:ascii="Arial"/><w:sz w:val="20"/></w:rPr><w:t>G</w:t></w:r><w:bookmarkEnd w:id="3"/></w:p>')
    rows = [
        tr_(tc_(p_(r_('H0')), w=1000), tc_(p_(r_('H1')), w=2000), tc_(p_(r_('H2')), w=3000)),
        tr_(tc_(para, w=1000, vm='restart'), tc_(p_(dr, r_('a1')), w=2000),
            tc_(p_(r_('b1')), nested, p_(), w=3000)),
        tr_(tc_(p_(), w=1000, vm='continue'), tc_(p_(r_('a2')), w=2000), tc_(p_(r_('b2')), w=3000)),
        tr_(tc_(p_(), w=1000, vm='continue'), tc_(p_(r_('a3')), w=2000), tc_(p_(r_('b3')), w=3000)),
        tr_(tc_(p_(r_('x4')), w=1000), tc_(p_(r_('a4')), w=2000), tc_(p_(r_('b4')), w=3000)),
    ]
    return make_docx(path, p_(r_('intro')) + tbl_([1000, 2000, 3000], *rows), ns=NS_BASE + NS_DRAW)


def vm_of(tc):
    vm = tc.find(WN + 'tcPr/' + WN + 'vMerge') if tc.find(WN + 'tcPr') is not None else None
    if vm is None:
        return None
    return vm.get(WN + 'val', 'continue')


def all_ids(path):
    x = doc_xml(path)
    return (re.findall(r'w14:paraId="([0-9A-F]+)"', x), re.findall(r'<wp:docPr id="(\d+)"', x),
            re.findall(r'<w:bookmarkStart w:id="(\d+)"', x), re.findall(r'<w:bookmarkStart[^>]*w:name="([^"]*)"', x))


class DuplicarFila(Base):
    def dup(self, *args, src=None):
        doc_dup(self.f('a.docx'))
        return self.ok('duplicar-fila', self.f('a.docx'), *args, '-o', self.f('b.docx'))

    def test_duplica_y_mensaje(self):
        out = self.dup('T0F1', '--veces', '2')
        self.assertEqual(out.strip(), 'OK: T0F1 duplicada ×2 -> %s; filas nuevas T0F2..T0F3' % self.f('b.docx'))
        rows = trs(body_tables(root_of(self.f('b.docx')))[0])
        self.assertEqual(len(rows), 7)
        txt = lambda tr: [''.join(t.text or '' for t in tc.iter(WN + 't')) for tc in tcs(tr)]
        self.assertEqual(txt(rows[2]), txt(rows[1]))
        self.assertEqual(txt(rows[3]), txt(rows[1]))
        self.assertEqual(txt(rows[4])[1], 'a2')

    def test_vmerge_restart_pasa_a_continue_en_clones(self):
        self.dup('T0F1', '--veces', '2')
        rows = trs(body_tables(root_of(self.f('b.docx')))[0])
        self.assertEqual([vm_of(tcs(r)[0]) for r in rows], [None, 'restart', 'continue', 'continue', 'continue', 'continue', None])

    def test_independientes_pierden_vmerge(self):
        self.dup('T0F1', '--veces', '1', '--independientes', 'C0')
        rows = trs(body_tables(root_of(self.f('b.docx')))[0])
        self.assertEqual([vm_of(tcs(r)[0]) for r in rows[:4]], [None, 'restart', None, 'continue'])
        self.dup('T0F2', '--veces', '1', '--independientes', 'C0,C1')
        rows = trs(body_tables(root_of(self.f('b.docx')))[0])
        self.assertEqual([vm_of(tcs(r)[0]) for r in rows[:5]], [None, 'restart', 'continue', None, 'continue'])

    def test_ids_nuevos_y_sin_duplicados(self):
        self.dup('T0F1', '--veces', '3')
        para, docpr, bm, names = all_ids(self.f('b.docx'))
        self.assertEqual(len(para), 4)           # original + 3 clones
        tid = re.findall(r'w14:textId="([0-9A-F]+)"', doc_xml(self.f('b.docx')))
        self.assertEqual((len(tid), len(set(tid))), (4, 4))
        self.assertEqual(len(set(para)), len(para))
        self.assertEqual(len(set(docpr)), len(docpr))
        self.assertEqual(len(docpr), 4)
        self.assertEqual(len(set(bm)), len(bm))
        self.assertEqual(len(set(names)), len(names))
        self.assertEqual(self.ok('verificar', self.f('b.docx')).splitlines()[0], 'OK')

    def test_vaciar(self):
        self.dup('T0F1', '--veces', '2', '--vaciar')
        root = root_of(self.f('b.docx'))
        rows = trs(body_tables(root)[0])
        self.assertEqual(len(rows), 7)
        for r in rows[2:4]:
            for tc in tcs(r):
                ps = tc.findall(WN + 'p')
                self.assertEqual(len(ps), 1)
                self.assertEqual(run_info(ps[0]), [])
                self.assertEqual(tc.findall(WN + 'tbl'), [])
                self.assertEqual(len(list(tc.iter(WN + 'drawing'))), 0)
        c0 = tcs(rows[2])[0].find(WN + 'p')
        self.assertEqual(tags(c0), ['pPr'])
        ppr = c0.find(WN + 'pPr')
        self.assertEqual(tags(ppr), ['jc', 'rPr'])
        self.assertEqual(tags(ppr.find(WN + 'rPr')), ['rFonts', 'sz'])     # rPr del primer run con texto
        self.assertEqual(len(rows[1].findall('.//' + WN + 'drawing')), 1)  # el original intacto
        self.assertEqual(len(re.findall('<w:drawing>', doc_xml(self.f('b.docx')))), 1)
        para, docpr, bm, names = all_ids(self.f('b.docx'))
        self.assertEqual((len(para), len(docpr), len(bm)), (1, 1, 1))

    def test_vaciar_conserva_vmerge_adaptado(self):
        self.dup('T0F1', '--veces', '1', '--vaciar')
        rows = trs(body_tables(root_of(self.f('b.docx')))[0])
        self.assertEqual([vm_of(tcs(r)[0]) for r in rows[:4]], [None, 'restart', 'continue', 'continue'])
        self.assertEqual(tcs(rows[2])[1].find(WN + 'tcPr/' + WN + 'tcW').get(WN + 'w'), '2000')

    def test_fila_anidada(self):
        doc_dup(self.f('a.docx'))
        out = self.ok('duplicar-fila', self.f('a.docx'), 'T0F1C2.T0F1', '--veces', '2', '-o', self.f('b.docx'))
        self.assertIn('filas nuevas T0F1C2.T0F2..T0F1C2.T0F3', out)
        nested = body_tables(root_of(self.f('b.docx')))[0].findall('.//' + WN + 'tbl')[0]
        self.assertEqual(len(trs(nested)), 4)

    def test_errores(self):
        doc_dup(self.f('a.docx'))
        for args in (('T0F9', '--veces', '1'), ('T7F0', '--veces', '1'), ('T0F1', '--veces', '0'),
                     ('T0F1C0', '--veces', '1'), ('T0F1', '--veces', '1', '--independientes', 'C7'),
                     ('T0F1', '--veces', '1', '--independientes', 'zz')):
            self.fallo(2, 'duplicar-fila', self.f('a.docx'), *args, '-o', self.f('b.docx'))
            self.assertFalse(self.f('b.docx').exists())
        self.fallo(2, 'duplicar-fila', self.f('a.docx'), 'T0F1', '--veces', '1')   # sin -o


# ============================================================== 5. borrar-filas
class BorrarFilas(Base):
    def borrar(self, *args, n=8, code=0):
        doc_rows(self.f('a.docx'), n)
        if self.f('b.docx').exists():
            self.f('b.docx').unlink()
        if code == 0:
            return self.ok('borrar-filas', self.f('a.docx'), *args, '-o', self.f('b.docx'))
        return self.fallo(code, 'borrar-filas', self.f('a.docx'), *args, '-o', self.f('b.docx'))

    def col0(self):
        return [''.join(t.text or '' for t in tcs(r)[0].iter(WN + 't')) for r in trs(body_tables(root_of(self.f('b.docx')))[0])]

    def test_una_fila_y_rango(self):
        out = self.borrar('T0F5')
        self.assertIn('OK:', out)
        self.assertEqual(self.col0(), ['H0', 'G', '', '', 'x4', 'x6', 'x7'])
        self.borrar('T0F5', '--hasta', 'F6')
        self.assertEqual(self.col0(), ['H0', 'G', '', '', 'x4', 'x7'])
        self.borrar('T0F5', '--hasta', '7')
        self.assertEqual(self.col0(), ['H0', 'G', '', '', 'x4'])

    def test_rechaza_borrar_todas(self):
        out, err = self.borrar('T0F0', '--hasta', 'F7', code=2)
        self.assertIn('todas las filas', err)
        self.assertFalse(self.f('b.docx').exists())

    def test_rechaza_vmerge_que_continua_y_nombra_la_celda(self):
        out, err = self.borrar('T0F1', code=2)
        self.assertIn('T0F1C0', err)
        self.assertFalse(self.f('b.docx').exists())
        out, err = self.borrar('T0F1', '--hasta', 'F2', code=2)
        self.assertIn('T0F1C0', err)

    def test_permite_si_la_combinacion_termina_en_el_rango(self):
        self.borrar('T0F1', '--hasta', 'F3')
        self.assertEqual(self.col0(), ['H0', 'x4', 'x5', 'x6', 'x7'])
        self.borrar('T0F2')                                    # solo una continue
        self.assertEqual(self.col0(), ['H0', 'G', '', 'x4', 'x5', 'x6', 'x7'])

    def test_forzar_promueve_la_primera_continue_y_avisa(self):
        out = self.borrar('T0F1', '--forzar')
        self.assertIn('AVISO', out)
        self.assertIn('se pierde', out)
        self.assertIn('T0F1C0', out)
        rows = trs(body_tables(root_of(self.f('b.docx')))[0])
        self.assertEqual([vm_of(tcs(r)[0]) for r in rows[:4]], [None, 'restart', 'continue', None])
        out = self.borrar('T0F1', '--hasta', 'F2', '--forzar')
        rows = trs(body_tables(root_of(self.f('b.docx')))[0])
        self.assertEqual([vm_of(tcs(r)[0]) for r in rows[:3]], [None, 'restart', None])

    def test_errores_de_uso(self):
        self.borrar('T0F9', code=2)
        self.borrar('T0F3', '--hasta', 'F2', code=2)
        self.borrar('T0F3', '--hasta', 'F20', code=2)
        self.borrar('T0F3C1', code=2)
        self.borrar('T5F0', code=2)

    def test_resultado_verifica_y_cuenta(self):
        self.borrar('T0F4', '--hasta', 'F5')
        self.assertEqual(self.ok('verificar', self.f('b.docx')).splitlines()[0], 'OK')
        self.assertEqual(len(trs(body_tables(root_of(self.f('b.docx')))[0])), 6)


# ================================================================= 6. vmerge
class VMerge(Base):
    def setUp(self):
        super().setUp()
        pr = lambda inner: '<w:tc>%s<w:p/></w:tc>' % inner
        cells = [
            '<w:tc><w:tcPr><w:tcW w:w="1000" w:type="dxa"/><w:gridSpan w:val="2"/><w:shd w:val="clear"/></w:tcPr><w:p/></w:tc>',   # C0 span
            '<w:tc><w:tcPr><w:tcW w:w="1000" w:type="dxa"/><w:shd w:val="clear"/></w:tcPr><w:p/></w:tc>',                          # C1 tcW
            '<w:tc><w:tcPr><w:shd w:val="clear"/></w:tcPr><w:p/></w:tc>',                                                           # C2 solo shd
            '<w:tc><w:p/></w:tc>',                                                                                                  # C3 sin tcPr
            '<w:tc><w:tcPr/><w:p/></w:tc>',                                                                                         # C4 tcPr vacío
            '<w:tc><w:tcPr><w:tcW w:w="9" w:type="dxa"/><w:vMerge w:val="restart"/></w:tcPr><w:p/></w:tc>',                         # C5 restart
        ]
        make_docx(self.f('a.docx'), '<w:tbl><w:tblPr/><w:tblGrid><w:gridCol w:w="1000"/></w:tblGrid><w:tr>%s</w:tr></w:tbl>' % ''.join(cells))

    def vm(self, coord, estado):
        self.ok('vmerge', self.f('a.docx'), coord, '--estado', estado, '-o', self.f('b.docx'))
        return cell_at(self.f('b.docx'), 0, 0, int(coord.split('C')[-1]))

    def test_posicion_tras_gridspan_tcw_o_inicio(self):
        self.assertEqual(tags(self.vm('T0F0C0', 'inicio').find(WN + 'tcPr')), ['tcW', 'gridSpan', 'vMerge', 'shd'])
        self.assertEqual(tags(self.vm('T0F0C1', 'continua').find(WN + 'tcPr')), ['tcW', 'vMerge', 'shd'])
        self.assertEqual(tags(self.vm('T0F0C2', 'continua').find(WN + 'tcPr')), ['vMerge', 'shd'])

    def test_valores(self):
        self.assertEqual(vm_of(self.vm('T0F0C1', 'inicio')), 'restart')
        self.assertIn('<w:vMerge w:val="restart"/>', doc_xml(self.f('b.docx')))
        self.assertEqual(vm_of(self.vm('T0F0C1', 'continua')), 'continue')
        self.assertIn('<w:tcW w:w="1000" w:type="dxa"/><w:vMerge/>', doc_xml(self.f('b.docx')))

    def test_crea_tcpr_como_primer_hijo(self):
        tc = self.vm('T0F0C3', 'inicio')
        self.assertEqual(tags(tc), ['tcPr', 'p'])
        self.assertEqual(vm_of(tc), 'restart')
        tc = self.vm('T0F0C4', 'continua')
        self.assertEqual(tags(tc), ['tcPr', 'p'])
        self.assertEqual(vm_of(tc), 'continue')

    def test_ninguno_quita_y_cambia(self):
        tc = self.vm('T0F0C5', 'ninguno')
        self.assertIsNone(vm_of(tc))
        self.assertEqual(tags(tc.find(WN + 'tcPr')), ['tcW'])
        self.assertEqual(vm_of(self.vm('T0F0C5', 'continua')), 'continue')
        self.assertEqual(len(doc_xml(self.f('b.docx')).split('vMerge')) - 1, 1)     # sin duplicar
        self.assertIsNone(vm_of(self.vm('T0F0C2', 'ninguno')))

    def test_errores(self):
        self.fallo(2, 'vmerge', self.f('a.docx'), 'T0F0C1', '--estado', 'otro', '-o', self.f('b.docx'))
        self.fallo(2, 'vmerge', self.f('a.docx'), 'T0F0C9', '--estado', 'inicio', '-o', self.f('b.docx'))
        self.fallo(2, 'vmerge', self.f('a.docx'), 'T0F0', '--estado', 'inicio', '-o', self.f('b.docx'))
        self.assertFalse(self.f('b.docx').exists())


# ========================================================== 7. tabla-en-celda
HOST_RPR = ('<w:rFonts w:ascii="Calibri" w:hAnsi="Calibri"/><w:b/><w:bCs/><w:color w:val="FF0000"/>'
            '<w:sz w:val="22"/><w:szCs w:val="22"/>')
BORDER_NAMES = ['top', 'left', 'bottom', 'right', 'insideH', 'insideV']


def doc_host(path):
    c0 = tc_(p_(r_('Anfitriona', False, HOST_RPR)), w=4000)
    c1 = tc_(p_(r_('Texto')), '<w:p w14:paraId="0000CCCC"/>', w=6000)
    spanned = tc_(p_(r_('Ancha')), span=2)
    body = tbl_([4000, 6000], tr_(c0, c1), tr_(spanned))
    return make_docx(path, body)


DATOS = {'encabezados': ['Fecha', 'Actividad'], 'filas': [['1', '**Leer** el texto'], ['2', 'Escribir']],
         'anchos': [1, 3], 'bordes': True}


class TablaEnCelda(Base):
    def ins(self, coord, datos, build=doc_host):
        build(self.f('a.docx'))
        dj = self.jsonf('d.json', datos)
        out = self.ok('tabla-en-celda', self.f('a.docx'), coord, dj, '-o', self.f('b.docx'))
        return out, root_of(self.f('b.docx'))

    def nested(self, root, t=0, f=0, c=0):
        return tcs(trs(body_tables(root)[t])[f])[c]

    def test_estructura_y_parrafo_final(self):
        out, root = self.ins('T0F0C0', DATOS)
        tc = self.nested(root)
        self.assertEqual(tags(tc), ['tcPr', 'p', 'tbl', 'p'])
        self.assertEqual(run_info(tc.findall(WN + 'p')[1]), [])
        self.assertIn('T0F0C0.T0', out)
        self.assertEqual(self.ok('verificar', self.f('b.docx')).splitlines()[0], 'OK')

    def test_si_el_ultimo_parrafo_esta_vacio_se_inserta_antes(self):
        out, root = self.ins('T0F0C1', DATOS)
        tc = self.nested(root, c=1)
        self.assertEqual(tags(tc), ['tcPr', 'p', 'tbl', 'p'])
        self.assertEqual(tc.findall(WN + 'p')[-1].get('{%s}paraId' % T.KNOWN_NS['w14']), '0000CCCC')
        self.assertEqual(len(tc.findall(WN + 'p')), 2)

    def test_ancho_proporciones_y_layout(self):
        out, root = self.ins('T0F0C0', DATOS)
        tbl = self.nested(root).find(WN + 'tbl')
        pr = tbl.find(WN + 'tblPr')
        self.assertEqual(tags(pr), ['tblW', 'tblBorders', 'tblLayout'])
        self.assertEqual((pr.find(WN + 'tblW').get(WN + 'w'), pr.find(WN + 'tblW').get(WN + 'type')), ('3800', 'dxa'))
        self.assertEqual(pr.find(WN + 'tblLayout').get(WN + 'type'), 'fixed')
        grid = [int(g.get(WN + 'w')) for g in tbl.find(WN + 'tblGrid')]
        self.assertEqual(grid, [950, 2850])
        for row in trs(tbl):
            self.assertEqual([int(tc.find(WN + 'tcPr/' + WN + 'tcW').get(WN + 'w')) for tc in tcs(row)], grid)

    def test_ancho_por_rejilla_y_columnas_iguales(self):
        datos = dict(DATOS)
        del datos['anchos']
        out, root = self.ins('T0F1C0', datos)
        tbl = self.nested(root, f=1).find(WN + 'tbl')
        self.assertEqual(tbl.find(WN + 'tblPr/' + WN + 'tblW').get(WN + 'w'), '9800')
        grid = [int(g.get(WN + 'w')) for g in tbl.find(WN + 'tblGrid')]
        self.assertEqual(grid, [4900, 4900])
        datos['encabezados'] = ['a', 'b', 'c']
        datos['filas'] = [['1', '2', '3']]
        out, root = self.ins('T0F0C0', datos)
        grid = [int(g.get(WN + 'w')) for g in self.nested(root).find(WN + 'tbl').find(WN + 'tblGrid')]
        self.assertEqual((sum(grid), grid[0], grid[1]), (3800, 1266, 1266))

    def test_bordes(self):
        out, root = self.ins('T0F0C0', DATOS)
        b = self.nested(root).find(WN + 'tbl/' + WN + 'tblPr/' + WN + 'tblBorders')
        self.assertEqual(tags(b), BORDER_NAMES)
        for k in b:
            self.assertEqual((k.get(WN + 'val'), k.get(WN + 'sz'), k.get(WN + 'color')), ('single', '4', 'auto'))
        d2 = dict(DATOS, bordes=False)
        out, root = self.ins('T0F0C0', d2)
        b = self.nested(root).find(WN + 'tbl/' + WN + 'tblPr/' + WN + 'tblBorders')
        self.assertEqual([k.get(WN + 'val') for k in b], ['nil'] * 6)

    def test_encabezado_en_negrita_y_tblheader_y_fuentes(self):
        out, root = self.ins('T0F0C0', DATOS)
        tbl = self.nested(root).find(WN + 'tbl')
        rows = trs(tbl)
        self.assertEqual(len(rows), 3)
        self.assertIsNotNone(rows[0].find(WN + 'trPr/' + WN + 'tblHeader'))
        self.assertIsNone(rows[1].find(WN + 'trPr'))
        self.assertEqual([run_info(tc.find(WN + 'p')) for tc in tcs(rows[0])], [[('Fecha', True)], [('Actividad', True)]])
        self.assertEqual(run_info(tcs(rows[1])[1].find(WN + 'p')), [('Leer', True), (' el texto', False)])
        self.assertEqual(run_info(tcs(rows[2])[1].find(WN + 'p')), [('Escribir', False)])
        r = tcs(rows[2])[1].find(WN + 'p/' + WN + 'r')
        self.assertEqual(tags(r.find(WN + 'rPr')), ['rFonts', 'sz', 'szCs'])      # sin negrita ni color
        r = tcs(rows[0])[0].find(WN + 'p/' + WN + 'r')
        self.assertEqual(tags(r.find(WN + 'rPr')), ['rFonts', 'b', 'bCs', 'sz', 'szCs'])
        self.assertEqual(r.find(WN + 'rPr/' + WN + 'rFonts').get(WN + 'ascii'), 'Calibri')

    def test_direccionable_con_comandos_existentes(self):
        out, root = self.ins('T0F0C0', DATOS)
        tl = self.ok('tablas', self.f('b.docx'), '--tabla', '0')
        self.assertIn('T0F0C0.T0F2C1 "Escribir"', tl)
        j = json.loads(self.ok('leer-celdas', self.f('b.docx'), 'T0F0C0.T0F1C1'))
        self.assertEqual(j['T0F0C0.T0F1C1'], ['**Leer** el texto'])
        cj = self.jsonf('c.json', {'T0F0C0.T0F2C1': 'Cambiado'})
        self.ok('editar-celdas', self.f('b.docx'), cj, '-o', self.f('c.docx'))
        self.assertIn('Cambiado', doc_xml(self.f('c.docx')))

    def test_segunda_tabla_en_la_misma_celda_es_t1(self):
        self.ins('T0F0C0', DATOS)
        dj = self.jsonf('d2.json', {'filas': [['solo']]})
        out = self.ok('tabla-en-celda', self.f('b.docx'), 'T0F0C0', dj, '-o', self.f('c.docx'))
        self.assertIn('T0F0C0.T1', out)
        tc = cell_at(self.f('c.docx'), 0, 0, 0)
        self.assertEqual(tags(tc), ['tcPr', 'p', 'tbl', 'tbl', 'p'])
        self.assertEqual(tags(tc)[-1], 'p')
        self.assertEqual(len(tc.findall(WN + 'tbl')), 2)
        self.assertEqual(len(trs(tc.findall(WN + 'tbl')[1])), 1)        # sin encabezados: solo la fila de datos
        self.assertIsNone(trs(tc.findall(WN + 'tbl')[1])[0].find(WN + 'trPr'))

    def test_errores(self):
        doc_host(self.f('a.docx'))
        malos = [{'filas': [['a', 'b'], ['c']]}, {'encabezados': ['a'], 'filas': [['a', 'b']]},
                 {'filas': [['a', 'b']], 'anchos': [1]}, {'filas': [['a']], 'anchos': [0]}, {'filas': []},
                 {'encabezados': [], 'filas': []}, [], {'filas': [['**sin cerrar']]}]
        for i, m in enumerate(malos):
            dj = self.jsonf('m%d.json' % i, m)
            self.fallo(2, 'tabla-en-celda', self.f('a.docx'), 'T0F0C0', dj, '-o', self.f('b.docx'))
            self.assertFalse(self.f('b.docx').exists())
        dj = self.jsonf('ok.json', DATOS)
        self.fallo(2, 'tabla-en-celda', self.f('a.docx'), 'T0F9C0', dj, '-o', self.f('b.docx'))


# ================================================================= 8. anexos
A_NS = T.KNOWN_NS['a']
R_ATTR = '{%s}' % T.R_NS
HLINK_TYPE = T.R_NS + '/hyperlink'
IMG_TYPE = T.R_NS + '/image'
EMU_TW = 635
CM04 = 144000


def rels_of(path):
    return {a['Id']: a for a in T.parse_rels(zread(path, 'word/_rels/document.xml.rels'))}


class ImagenYGeometria(unittest.TestCase):
    def test_png_gif_jpeg(self):
        self.assertEqual(T.image_info(png_bytes(7, 3))[:3], ('png', 7, 3))
        self.assertEqual(T.image_info(gif_bytes(40, 30))[:3], ('gif', 40, 30))
        self.assertEqual(T.image_info(jpeg_bytes(640, 480))[:3], ('jpeg', 640, 480))

    def test_jpeg_ignora_dht_jpg_dac_y_acepta_progresivo(self):
        app0 = b'\xff\xe0' + struct.pack('>H', 16) + b'JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00'
        trampa = lambda m: b'\xff' + bytes([m]) + struct.pack('>H', 8) + b'\xff\xc0\x00\x08'.ljust(6, b'\x00')
        sof2 = b'\xff\xc2' + struct.pack('>HBHHB', 11, 8, 333, 555, 1) + b'\x01\x11\x00'
        data = b'\xff\xd8' + app0 + trampa(0xC4) + trampa(0xC8) + trampa(0xCC) + sof2 + b'\xff\xd9'
        self.assertEqual(T.image_info(data)[:3], ('jpeg', 555, 333))

    def test_formatos_no_soportados_y_corruptos(self):
        for bad in (b'BM' + b'\x00' * 40, b'', b'hola', b'\xff\xd8\xff\xd9', b'\x89PNG\r\n\x1a\n\x00'):
            with self.assertRaises(T.ToolError):
                T.image_info(bad)

    def test_geometria_de_seccion(self):
        g = T.section_geometry('<w:sectPr><w:pgSz w:w="15840" w:h="12240" w:orient="landscape"/>'
                               '<w:pgMar w:top="720" w:right="1000" w:bottom="800" w:left="1100" w:header="1" w:footer="1" w:gutter="140"/></w:sectPr>')
        self.assertEqual((g['w'], g['h'], g['left'], g['right'], g['top'], g['bottom']), (15840, 12240, 1240, 1000, 720, 800))
        for none in (None, '<w:sectPr/>'):
            g = T.section_geometry(none)
            self.assertEqual((g['w'], g['h'], g['left'], g['right'], g['top'], g['bottom']), (12240, 15840, 1440, 1440, 1440, 1440))

    def test_layout_dos_filas_caben_en_la_pagina(self):
        lay = T.anexos_layout(T.section_geometry(None))
        self.assertEqual((lay['text_w'], lay['col_w']), (9360, 4680))
        self.assertEqual(lay['img_max_w_emu'], 4680 * EMU_TW - CM04)
        self.assertGreater(lay['img_max_h_emu'], 0)
        self.assertLess(2 * lay['img_max_h_emu'], (15840 - 2880) * EMU_TW)


def doc_anexos(path, ns=NS_BASE, body=None, **kw):
    body = body if body is not None else (p_(r_('uno')) + p_(r_('dos')) + p_(r_('tres')))
    return make_docx(path, body, ns=ns, **kw)


class Anexos(Base):
    def setUp(self):
        super().setUp()
        (self.dir / 'img').mkdir()
        (self.dir / 'img' / 'a.png').write_bytes(png_bytes(2000, 1000))
        (self.dir / 'img' / 'b.png').write_bytes(png_bytes(10, 10, (1, 2, 3)))
        (self.dir / 'img' / 'c.jpg').write_bytes(jpeg_bytes(300, 600))
        (self.dir / 'img' / 'same.png').write_bytes(png_bytes(10, 10, (1, 2, 3)))
        (self.dir / 'img' / 'g.gif').write_bytes(gif_bytes(50, 25))
        self.datos = {'titulo': 'ANEXOS', 'anexos': [
            {'n': 3, 'titulo': 'Video Qué es identidad', 'imagen': 'img/a.png', 'url': 'https://example.org/v?a=1&b=2'},
            {'n': 4, 'titulo': 'Lectura', 'imagen': 'img/b.png'},
            {'n': 5, 'titulo': 'Cartel', 'imagen': 'img/c.jpg', 'url': 'http://example.org/c'},
            {'n': 6, 'titulo': 'Solo texto'},
            {'n': 7, 'titulo': 'Gif', 'imagen': 'img/g.gif'}]}

    def go(self, datos=None, antes='B1', build=doc_anexos, code=0):
        build(self.f('a.docx'))
        aj = self.jsonf('anexos.json', datos if datos is not None else self.datos)
        if code == 0:
            return self.ok('anexos', self.f('a.docx'), aj, '--antes', antes, '-o', self.f('b.docx'))
        return self.fallo(code, 'anexos', self.f('a.docx'), aj, '--antes', antes, '-o', self.f('b.docx'))

    def body(self):
        return list(root_of(self.f('b.docx')).find(WN + 'body'))

    def test_mensaje_y_orden_del_body(self):
        out = self.go()
        self.assertEqual(out.strip(), 'OK: 5 anexos en 2 hojas antes de B1 -> %s' % self.f('b.docx'))
        self.assertEqual([k.tag.replace(WN, '') for k in self.body()],
                         ['p', 'p', 'tbl', 'p', 'p', 'tbl', 'p', 'p', 'p', 'sectPr'])
        self.assertEqual(self.ok('verificar', self.f('b.docx')).splitlines()[0], 'OK')

    def test_titulo_de_hoja(self):
        self.go()
        t = self.body()[1]
        self.assertEqual(run_info(t), [('ANEXOS', True)])
        ppr = t.find(WN + 'pPr')
        self.assertIsNotNone(ppr.find(WN + 'pageBreakBefore'))
        self.assertEqual(ppr.find(WN + 'jc').get(WN + 'val'), 'center')
        self.assertEqual(run_info(self.body()[4]), [('ANEXOS', True)])

    def test_tabla_2x2_sin_bordes_y_columnas_iguales(self):
        self.go()
        tbl = self.body()[2]
        pr = tbl.find(WN + 'tblPr')
        self.assertEqual([k.get(WN + 'val') for k in pr.find(WN + 'tblBorders')], ['nil'] * 6)
        self.assertEqual(pr.find(WN + 'tblLayout').get(WN + 'type'), 'fixed')
        self.assertEqual(pr.find(WN + 'tblW').get(WN + 'w'), '9360')
        self.assertEqual([g.get(WN + 'w') for g in tbl.find(WN + 'tblGrid')], ['4680', '4680'])
        rows = trs(tbl)
        self.assertEqual([len(tcs(r)) for r in rows], [2, 2])
        for r in rows:
            self.assertIsNotNone(r.find(WN + 'trPr/' + WN + 'cantSplit'))
        self.assertEqual(tags(self.body()[3]), [])       # párrafo vacío tras la tabla
        for tc in tbl.iter(WN + 'tc'):
            self.assertEqual(tags(tc)[-1], 'p')

    def test_celda_titulo_imagen_y_url(self):
        self.go()
        tc = tcs(trs(self.body()[2])[0])[0]
        ps = tc.findall(WN + 'p')
        self.assertEqual(run_info(ps[0]), [('Anexo 3', True), (' Video Qué es identidad', False)])
        self.assertEqual(ps[1].find(WN + 'pPr/' + WN + 'jc').get(WN + 'val'), 'center')
        self.assertEqual(len(ps), 3)
        h = ps[2].find(WN + 'hyperlink')
        self.assertIsNotNone(h)
        rid = h.get(R_ATTR + 'id')
        rel = rels_of(self.f('b.docx'))[rid]
        self.assertEqual((rel['Type'], rel['TargetMode'], unesc(rel['Target'])), (HLINK_TYPE, 'External', 'https://example.org/v?a=1&b=2'))
        r = h.find(WN + 'r')
        self.assertEqual(r.find(WN + 'rPr/' + WN + 'color').get(WN + 'val'), '0563C1')
        self.assertEqual(r.find(WN + 'rPr/' + WN + 'u').get(WN + 'val'), 'single')
        self.assertEqual(''.join(t.text for t in h.iter(WN + 't')), 'https://example.org/v?a=1&b=2')

    def test_imagen_en_linea_escalada_y_parte_media(self):
        self.go()
        lay = T.anexos_layout(T.section_geometry(None))
        root = root_of(self.f('b.docx'))
        inl = list(root.iter('{%s}inline' % T.KNOWN_NS['wp']))
        self.assertEqual(len(inl), 4)
        ext = inl[0].find('{%s}extent' % T.KNOWN_NS['wp'])
        cx, cy = int(ext.get('cx')), int(ext.get('cy'))
        self.assertLessEqual(cx, lay['img_max_w_emu'])
        self.assertLessEqual(cy, lay['img_max_h_emu'])
        self.assertLessEqual(abs(cx - 2 * cy), 2)                         # 2000x1000 conserva proporción
        self.assertEqual(max(cx, lay['img_max_w_emu']) , lay['img_max_w_emu'])
        ext2 = inl[1].find('{%s}extent' % T.KNOWN_NS['wp'])
        self.assertEqual((int(ext2.get('cx')), int(ext2.get('cy'))), (95250, 95250))     # 10 px a 96 ppp, sin ampliar
        blip = inl[0].find('.//{%s}blip' % A_NS)
        rel = rels_of(self.f('b.docx'))[blip.get(R_ATTR + 'embed')]
        self.assertEqual(rel['Type'], IMG_TYPE)
        self.assertTrue(rel['Target'].startswith('media/'))
        self.assertEqual(zipfile.ZipFile(str(self.f('b.docx'))).read('word/' + rel['Target']), (self.dir / 'img' / 'a.png').read_bytes())
        pic = inl[0].find('.//{%s}pic' % T.KNOWN_NS['pic'])
        self.assertIsNotNone(pic)
        self.assertEqual(inl[0].find('.//{%s}ext' % A_NS).get('cx'), str(cx))

    def test_content_types_y_namespaces_de_la_raiz(self):
        self.go()
        ct = zread(self.f('b.docx'), '[Content_Types].xml')
        for ext, mime in (('png', 'image/png'), ('jpeg', 'image/jpeg'), ('gif', 'image/gif')):
            self.assertEqual(len(re.findall(r'<Default Extension="%s" ContentType="%s"/>' % (ext, mime), ct)), 1, ext)
        head = doc_xml(self.f('b.docx')).split('>', 2)[1]
        for pfx in ('wp', 'a', 'pic', 'r'):
            self.assertIn('xmlns:%s=' % pfx, head)
        # si ya existe el Default no se duplica
        self.go(build=lambda p: doc_anexos(p, content_types=CT.replace('</Types>', '<Default Extension="png" ContentType="image/png"/></Types>')))
        ct = zread(self.f('b.docx'), '[Content_Types].xml')
        self.assertEqual(ct.count('Extension="png"'), 1)

    def test_docpr_unicos(self):
        pre = p_('<w:r><w:drawing><wp:inline><wp:docPr id="7" name="x"/></wp:inline></w:drawing></w:r>')
        self.go(build=lambda p: doc_anexos(p, ns=NS_BASE + NS_DRAW, body=pre + p_(r_('x'))))
        ids = re.findall(r'<wp:docPr id="(\d+)"', doc_xml(self.f('b.docx')))
        self.assertEqual(len(ids), 5)
        self.assertEqual(len(set(ids)), 5)
        self.assertEqual(self.ok('verificar', self.f('b.docx')).splitlines()[0], 'OK')

    def test_reutiliza_partes_y_relaciones_y_nombres_unicos(self):
        d = dict(self.datos)
        d['anexos'] = [{'n': 1, 'titulo': 'x', 'imagen': 'img/b.png', 'url': 'https://e.org/x'},
                       {'n': 2, 'titulo': 'y', 'imagen': 'img/same.png', 'url': 'https://e.org/x'},
                       {'n': 3, 'titulo': 'z', 'imagen': 'img/a.png'}]
        build = lambda p: doc_anexos(p, extra={'word/media/image1.png': png_bytes(4, 4, (9, 9, 9))})
        self.go(d, build=build)
        names = [n for n in zipfile.ZipFile(str(self.f('b.docx'))).namelist() if n.startswith('word/media/')]
        self.assertEqual(len(names), 3, names)                  # existente + b.png (reutilizada una vez) + a.png
        rels = rels_of(self.f('b.docx'))
        self.assertEqual(len([r for r in rels.values() if r['Type'] == IMG_TYPE]), 2)
        self.assertEqual(len([r for r in rels.values() if r['Type'] == HLINK_TYPE]), 1)
        # bytes idénticos ya presentes en el documento -> se reutiliza esa parte
        build2 = lambda p: doc_anexos(p, extra={'word/media/logo.png': png_bytes(10, 10, (1, 2, 3))})
        d['anexos'] = [{'n': 1, 'titulo': 'x', 'imagen': 'img/b.png'}]
        self.go(d, build=build2)
        names = [n for n in zipfile.ZipFile(str(self.f('b.docx'))).namelist() if n.startswith('word/media/')]
        self.assertEqual(names, ['word/media/logo.png'])

    def test_sin_archivo_de_relaciones_se_crea(self):
        d = {'anexos': [{'n': 1, 'titulo': 'x', 'imagen': 'img/b.png', 'url': 'https://e.org/'}]}
        self.go(d, build=lambda p: doc_anexos(p, docrels=None))
        self.assertEqual(len(rels_of(self.f('b.docx'))), 2)
        self.assertEqual(self.ok('verificar', self.f('b.docx')).splitlines()[0], 'OK')
        self.assertEqual(run_info(self.body()[1]), [('ANEXOS', True)])         # titulo por defecto

    def test_celdas_sobrantes_vacias(self):
        self.go()
        row = trs(self.body()[5])
        cells = [tc for r in row for tc in tcs(r)]
        self.assertEqual([len(tc.findall(WN + 'p')) for tc in cells], [2, 1, 1, 1])      # Gif / vacías
        for tc in cells[1:]:
            self.assertEqual(run_info(tc.find(WN + 'p')), [])
            self.assertEqual(tags(tc.find(WN + 'p')), [])
        self.assertEqual(run_info(cells[0].find(WN + 'p')), [('Anexo 7', True), (' Gif', False)])

    def test_geometria_de_la_seccion_que_gobierna_el_punto(self):
        land = ('<w:sectPr><w:pgSz w:w="15840" w:h="12240" w:orient="landscape"/>'
                '<w:pgMar w:top="720" w:right="720" w:bottom="720" w:left="720" w:header="0" w:footer="0" w:gutter="0"/></w:sectPr>')
        body = p_(r_('a')) + '<w:p><w:pPr>%s</w:pPr></w:p>' % land + p_(r_('b'))
        build = lambda p: doc_anexos(p, body=body)
        self.go(build=build, antes='B0')
        tbl = [k for k in self.body() if k.tag == WN + 'tbl'][0]
        self.assertEqual([g.get(WN + 'w') for g in tbl.find(WN + 'tblGrid')], ['7200', '7200'])
        self.go(build=build, antes='B2')
        tbl = [k for k in self.body() if k.tag == WN + 'tbl'][0]
        self.assertEqual([g.get(WN + 'w') for g in tbl.find(WN + 'tblGrid')], ['4680', '4680'])
        self.go(build=build, antes='B1')       # el párrafo con sectPr cierra la sección horizontal
        tbl = [k for k in self.body() if k.tag == WN + 'tbl'][0]
        self.assertEqual([g.get(WN + 'w') for g in tbl.find(WN + 'tblGrid')], ['7200', '7200'])

    def test_antes_del_sectpr_final_y_forma_numerica(self):
        self.go(antes='3')
        self.assertEqual(self.body()[-1].tag, WN + 'sectPr')
        self.assertEqual(self.body()[-2].tag, WN + 'p')
        self.go(antes='B3')
        self.assertEqual(self.body()[-1].tag, WN + 'sectPr')

    def test_errores(self):
        bad_n = [[{'n': 1, 'titulo': 'a'}, {'n': 3, 'titulo': 'b'}], [{'n': 1, 'titulo': 'a'}, {'n': 1, 'titulo': 'b'}],
                 [{'n': 2, 'titulo': 'a'}, {'n': 1, 'titulo': 'b'}], [{'titulo': 'sin n'}], [{'n': 'x', 'titulo': 'a'}], []]
        casos = [{'anexos': x} for x in bad_n]
        casos += [{'anexos': [{'n': 1, 'titulo': 'a', 'imagen': 'img/nada.png'}]},
                  {'anexos': [{'n': 1, 'titulo': 'a', 'imagen': 'img/bad.bmp'}]},
                  {'anexos': [{'n': 1, 'titulo': 'a', 'url': 'ftp://e.org/x'}]},
                  {'anexos': [{'n': 1, 'titulo': 'a', 'url': 'www.e.org'}]},
                  {'anexos': [{'n': 1, 'titulo': 'a', 'url': 'javascript:alert(1)'}]},
                  {'anexos': [{'n': 1, 'titulo': 'a', 'url': 'https://'}]}]
        (self.dir / 'img' / 'bad.bmp').write_bytes(b'BM' + b'\x00' * 40)
        for c in casos:
            self.go(c, code=2)
            self.assertFalse(self.f('b.docx').exists(), c)
        self.go(self.datos, antes='B99', code=2)
        self.assertFalse(self.f('b.docx').exists())

    def test_numeracion_continua_desde_cualquier_numero(self):
        d = {'anexos': [{'n': 12, 'titulo': 'a'}, {'n': 13, 'titulo': 'b'}, {'n': 14, 'titulo': 'c'},
                        {'n': 15, 'titulo': 'd'}, {'n': 16, 'titulo': 'e'}]}
        out = self.go(d)
        self.assertIn('5 anexos en 2 hojas', out)
        self.assertEqual(run_info(tcs(trs(self.body()[2])[1])[1].find(WN + 'p'))[0], ('Anexo 15', True))


# ============================================================== 9. conservado
class Conservado(Base):
    def build(self, dest_paras=None, orig_extra=None):
        orig = tbl_([3000, 3000],
                    tr_(tc_(p_(r_('Texto  intocable\u00a0uno')), w=3000),
                        tc_(p_(r_('Alfa beta')), p_(), p_(r_('Gamma delta')), w=3000)),
                    tr_(tc_(p_(r_('Re\u0301sumen final')), w=3000), tc_(p_(r_('Otra cosa')), w=3000)))
        make_docx(self.f('orig.docx'), orig)
        dest_paras = dest_paras or [
            p_(r_('Portada')), p_(r_('Texto intocable uno')), p_(r_('xx Alfa   beta yy')),
            p_(r_('Gamma')), p_(r_('delta')), p_(r_('R\u00e9sumen final')),
            tbl_([3000], tr_(tc_(p_(r_('Otra cosa')))))]
        make_docx(self.f('dest.docx'), ''.join(dest_paras))

    def con(self, celdas, *extra):
        return run('conservado', self.f('dest.docx'), self.f('orig.docx'), '--celdas', celdas, *extra)

    def test_todo_conservado(self):
        self.build()
        code, out, err = self.con('T0F0C0,T0F0C1,T0F1')
        self.assertEqual(code, 0, out + err)
        lines = out.strip().splitlines()
        self.assertEqual(lines[0], 'OK T0F0C0 (1 párrafo)')
        self.assertEqual(lines[1], 'OK T0F0C1 (2 párrafos)')
        self.assertEqual(lines[2:4], ['OK T0F1C0 (1 párrafo)', 'OK T0F1C1 (1 párrafo)'])
        self.assertIn('RESUMEN: 4 celdas OK, 0 con faltantes', lines[-1])

    def test_falta_con_indice_de_parrafo_y_codigo_1(self):
        self.build([p_(r_('Gamma')), p_(r_('OTRO')), p_(r_('delta')), p_(r_('Texto intocable uno')), p_(r_('Alfa beta'))])
        code, out, err = self.con('T0F0C0,T0F0C1')
        self.assertEqual(code, 1)
        self.assertIn('OK T0F0C0 (1 párrafo)', out)
        self.assertIn('FALTA T0F0C1/p2 "Gamma delta"', out)
        self.assertNotIn('OK T0F0C1', out)
        self.assertIn('RESUMEN: 1 celdas OK, 1 con faltantes (1 párrafos)', out)

    def test_distingue_mayusculas_y_normaliza_nfc(self):
        self.build([p_(r_('texto INTOCABLE uno')), p_(r_('R\u00e9sumen final'))])
        code, out, _ = self.con('T0F0C0,T0F1C0')
        self.assertEqual(code, 1)
        self.assertIn('FALTA T0F0C0/p0 "Texto intocable uno"', out)      # el origen se muestra normalizado
        self.assertIn('OK T0F1C0 (1 párrafo)', out)                      # NFD del origen == NFC del destino

    def test_rango_desde_hasta_en_el_destino(self):
        self.build()
        code, out, _ = self.con('T0F0C0', '--desde', 'B2', '--hasta', 'B5')
        self.assertEqual(code, 1)
        self.assertIn('FALTA T0F0C0/p0', out)
        code, out, _ = self.con('T0F0C0', '--desde', 'B1', '--hasta', 'B1')
        self.assertEqual(code, 0)
        code, out, _ = self.con('T0F1C1', '--desde', 'B6')
        self.assertEqual(code, 0)
        self.assertEqual(self.con('T0F0C0', '--desde', 'B1', '--hasta', 'B99')[0], 2)

    def test_celdas_desde_archivo(self):
        self.build()
        self.f('celdas.txt').write_text('T0F0C0\n\nT0F1\n', encoding='utf-8')
        code, out, _ = self.con('@' + str(self.f('celdas.txt')))
        self.assertEqual(code, 0)
        self.assertEqual(len([l for l in out.splitlines() if l.startswith('OK ')]), 3)

    def test_errores_de_uso(self):
        self.build()
        self.assertEqual(self.con('T9F0C0')[0], 2)
        self.assertEqual(self.con('xx')[0], 2)
        self.assertEqual(self.con('@' + str(self.f('no_existe.txt')))[0], 2)
        self.assertEqual(run('conservado', self.f('no.docx'), self.f('orig.docx'), '--celdas', 'T0F0C0')[0], 2)

    def test_no_modifica_ningun_archivo(self):
        self.build()
        antes = (self.f('dest.docx').read_bytes(), self.f('orig.docx').read_bytes())
        self.con('T0F0C0')
        self.assertEqual(antes, (self.f('dest.docx').read_bytes(), self.f('orig.docx').read_bytes()))


# ================================================================== 10. render
class Render(Base):
    def test_busca_soffice_en_path_y_rutas_habituales(self):
        which = lambda n: {'soffice': '/usr/bin/soffice'}.get(n)
        self.assertEqual(T.find_soffice(which, lambda p: False, 'linux'), '/usr/bin/soffice')
        which = lambda n: {'libreoffice': '/snap/bin/libreoffice'}.get(n)
        self.assertEqual(T.find_soffice(which, lambda p: False, 'linux'), '/snap/bin/libreoffice')
        win = 'C:\\Program Files\\LibreOffice\\program\\soffice.exe'
        self.assertEqual(T.find_soffice(lambda n: None, lambda p: p == win, 'win32'), win)
        mac = '/Applications/LibreOffice.app/Contents/MacOS/soffice'
        self.assertEqual(T.find_soffice(lambda n: None, lambda p: p == mac, 'darwin'), mac)
        self.assertIsNone(T.find_soffice(lambda n: None, lambda p: False, 'linux'))
        self.assertIsNone(T.find_soffice(lambda n: None, lambda p: p == win, 'linux'))

    def test_comando_soffice(self):
        cmd = T.soffice_command('/usr/bin/soffice', '/x/a b.docx', '/x/out', '/tmp/perfil 1')
        self.assertEqual(cmd, ['/usr/bin/soffice', '-env:UserInstallation=file:///tmp/perfil%201', '--headless',
                               '--convert-to', 'pdf', '--outdir', '/x/out', '/x/a b.docx'])

    def test_script_de_word(self):
        sc = T.word_script("C:\\d'ir\\a.docx", 'C:\\d\'ir\\a.pdf')
        for frag in ('Word.Application', 'Documents.Open', '$true', 'ExportAsFixedFormat', 'Quit()', "'C:\\d''ir\\a.docx'"):
            self.assertIn(frag, sc)

    def test_plan_ordena_libreoffice_antes_que_word(self):
        which = lambda n: {'soffice': 'S', 'powershell': 'PS'}.get(n)
        plan = T.render_plan('/a/b.docx', '/o', which, lambda p: False, 'win32', '/tmp/pf')
        self.assertEqual([k for k, _ in plan], ['libreoffice', 'word'])
        self.assertEqual(plan[1][1][:3], ['PS', '-NoProfile', '-Command'])
        self.assertEqual(T.render_plan('/a/b.docx', '/o', lambda n: 'PS' if n == 'powershell' else None,
                                       lambda p: False, 'win32', '/tmp/pf')[0][0], 'word')
        self.assertEqual(T.render_plan('/a/b.docx', '/o', lambda n: 'PS' if n == 'powershell' else None,
                                       lambda p: False, 'linux', '/tmp/pf'), [])

    def test_sin_renderizador_devuelve_3(self):
        make_docx(self.f('a.docx'), p_(r_('x')))
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = T.render_docx(self.f('a.docx'), self.f('o'), which=lambda n: None, exists=lambda p: False,
                                 platform='linux', runner=lambda *a, **k: self.fail('no debe ejecutar nada'))
        self.assertEqual(code, 3)
        self.assertIn('SIN RENDERIZADOR', out.getvalue() + err.getvalue())
        self.assertIn('revisión visual queda pendiente para el usuario en Word', out.getvalue() + err.getvalue())

    def test_exito_con_runner_falso_y_limite_de_tiempo(self):
        make_docx(self.f('a.docx'), p_(r_('x')))
        calls = []

        def runner(cmd, **kw):
            calls.append((cmd, kw))
            outdir = Path(cmd[cmd.index('--outdir') + 1])
            (outdir / 'a.pdf').write_bytes(b'%PDF-1.4')
            return type('R', (), {'returncode': 0, 'stdout': '', 'stderr': ''})()
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = T.render_docx(self.f('a.docx'), self.f('o'), which=lambda n: '/usr/bin/soffice' if n == 'soffice' else None,
                                 exists=lambda p: False, platform='linux', runner=runner)
        self.assertEqual(code, 0)
        self.assertEqual(out.getvalue().strip(), str(self.f('o') / 'a.pdf'))
        self.assertEqual(calls[0][1]['timeout'], 240)
        self.assertIn('--headless', calls[0][0])

    def test_si_libreoffice_falla_prueba_word_y_si_todo_falla_es_error(self):
        make_docx(self.f('a.docx'), p_(r_('x')))
        seen = []

        def runner(cmd, **kw):
            seen.append(cmd[0])
            return type('R', (), {'returncode': 1, 'stdout': '', 'stderr': 'falló'})()
        which = lambda n: {'soffice': 'S', 'powershell': 'PS'}.get(n)
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = T.render_docx(self.f('a.docx'), self.f('o'), which=which, exists=lambda p: False, platform='win32', runner=runner)
        self.assertEqual((code, seen), (2, ['S', 'PS']))
        self.assertIn('falló', err.getvalue() + out.getvalue())

    def test_cli_archivo_inexistente_es_error_de_uso(self):
        self.fallo(2, 'render', self.f('no.docx'))


# =================================================================== 11. verificar
class VerificarNuevo(Base):
    def verif(self, body):
        make_docx(self.f('a.docx'), body)
        return run('verificar', self.f('a.docx'))

    def test_celda_que_no_termina_en_parrafo(self):
        tbl_en_celda = tbl_([500], tr_(tc_(p_(r_('n')))))
        code, out, _ = self.verif(tbl_([3000, 3000], tr_(tc_(p_(r_('a')), tbl_en_celda), tc_(p_(r_('b'))))))
        self.assertEqual(code, 1)
        self.assertIn('PROBLEMAS', out)
        self.assertIn('T0F0C0', out)
        self.assertIn('w:p', out)
        self.assertNotIn('T0F0C1', out)

    def test_celda_vacia_sin_hijos_de_bloque(self):
        code, out, _ = self.verif(tbl_([3000], tr_('<w:tc><w:tcPr/></w:tc>')))
        self.assertEqual(code, 1)
        self.assertIn('T0F0C0', out)

    def test_celda_anidada(self):
        inner = tbl_([500], tr_('<w:tc><w:tcPr/><w:tbl><w:tblGrid/><w:tr><w:tc><w:p/></w:tc></w:tr></w:tbl></w:tc>'))
        code, out, _ = self.verif(tbl_([3000], tr_(tc_(p_(r_('a')), inner, p_()))))
        self.assertEqual(code, 1)
        self.assertIn('T0F0C0.T0F0C0', out)

    def test_tabla_sin_filas(self):
        code, out, _ = self.verif(p_(r_('x')) + '<w:tbl><w:tblPr/><w:tblGrid/></w:tbl>' + p_())
        self.assertEqual(code, 1)
        self.assertIn('T0', out)
        self.assertIn('no tiene filas', out)
        nested = tbl_([3000], tr_(tc_(p_(r_('a')), '<w:tbl><w:tblPr/><w:tblGrid/></w:tbl>', p_())))
        code, out, _ = self.verif(nested)
        self.assertIn('T0F0C0.T0', out)
        self.assertIn('no tiene filas', out)

    def test_documento_correcto_sigue_ok(self):
        code, out, _ = self.verif(tbl_([3000], tr_(tc_(p_(r_('a')), tbl_([500], tr_(tc_(p_(r_('n'))))), p_()))))
        self.assertEqual((code, out.splitlines()[0]), (0, 'OK'))


# ====================================== regresión: comandos que ya existían
class Regresion(Base):
    def test_lectura_formato_sin_cambios(self):
        doc_rows(self.f('a.docx'))
        a = self.f('a.docx')
        self.assertEqual(self.ok('mapa', a), 'B0 P "intro"\nB1 T0 8x3 "H0"\nB2 P ""\nB3 T1 1x1 "otra"\nB4 P "fin"\nB5 SECT\n')
        t = self.ok('tablas', a, '--tabla', '0').splitlines()
        self.assertEqual(t[0], '# T0 8x3 grid=1000,2000,3000')
        self.assertEqual(t[4:7], ['T0F1C0 [vmerge-ini] "G"', 'T0F1C1 "a1"', 'T0F1C2 "b1"'])
        self.assertEqual(t[7], 'T0F2C0 [vmerge] ""')
        self.assertEqual(len(t), 25)
        self.assertEqual(self.ok('texto', a, '--desde', '1').splitlines()[:3], ['B1 T0', '  F0: H0 | H1 | H2', '  F1: G | a1 | b1'])
        self.assertEqual(self.ok('buscar', a, 'a3'), 'T0F3C1 "a3"\n')
        self.assertEqual(self.ok('buscar', a, 'nada'), 'sin coincidencias\n')
        info = self.ok('info', a).splitlines()
        self.assertEqual(info[1], 'body: 6 hijos; párrafos 28; tablas 2 (primer nivel 2); secciones 1; imágenes 0 (media: 0 archivos, 0 bytes)')

    def test_reemplazar_y_borrar(self):
        doc_rows(self.f('a.docx'))
        out = self.ok('reemplazar', self.f('a.docx'), 'a3', 'ZZ', '-o', self.f('b.docx'))
        self.assertEqual(out, 'OK: 1 reemplazos -> %s\n' % self.f('b.docx'))
        self.assertIn('<w:t>ZZ</w:t>', doc_xml(self.f('b.docx')))
        out = self.ok('borrar', self.f('a.docx'), '--desde', '2', '--hasta', '3', '-o', self.f('c.docx'))
        self.assertEqual(out, 'OK: borrados B2..B3 (2 hijos) -> %s\n' % self.f('c.docx'))
        self.assertEqual(self.ok('mapa', self.f('c.docx')), 'B0 P "intro"\nB1 T0 8x3 "H0"\nB2 P "fin"\nB3 SECT\n')
        out, err = self.fallo(2, 'borrar', self.f('a.docx'), '--desde', '2')
        self.assertIn('falta -o', err)

    def test_editar_celdas_crece_y_encoge(self):
        body = tbl_([4000], tr_(tc_(p_(r_('uno', False, RPR_F), ppr='<w:jc w:val="center"/>'), p_(r_('dos')), p_(r_('tres')))))
        make_docx(self.f('a.docx'), body)
        cj = self.jsonf('c.json', {'T0F0C0': ['A', 'B']})
        self.assertEqual(self.ok('editar-celdas', self.f('a.docx'), cj, '-o', self.f('b.docx')),
                         'OK: 1 celdas editadas -> %s\n' % self.f('b.docx'))
        self.assertEqual([run_info(p) for p in cell_at(self.f('b.docx'), 0, 0, 0).findall(WN + 'p')], [[('A', False)], [('B', False)]])
        cj = self.jsonf('c.json', {'T0F0C0': ['1', '2', '3', '4']})
        self.ok('editar-celdas', self.f('a.docx'), cj, '-o', self.f('b.docx'))
        ps = cell_at(self.f('b.docx'), 0, 0, 0).findall(WN + 'p')
        self.assertEqual([run_info(p)[0][0] for p in ps], ['1', '2', '3', '4'])
        self.assertEqual(tags(ps[0].find(WN + 'pPr')), ['jc'])
        self.assertIsNone(ps[3].find(WN + 'pPr'))                  # el clon copia el pPr del último párrafo
        cj = self.jsonf('c.json', {'T0F0C0': 'T9'})
        self.assertEqual(self.ok('editar-celdas', self.f('a.docx'), cj, '-o', self.f('b.docx')).strip().split(' ')[0], 'OK:')
        self.fallo(2, 'editar-celdas', self.f('a.docx'), self.jsonf('x.json', {'T5F0C0': 'x'}), '-o', self.f('b.docx'))

    def test_copiar_con_imagen_comparar_y_verificar(self):
        dr = ('<w:p><w:r><w:drawing><wp:inline><wp:extent cx="10" cy="10"/><wp:docPr id="1" name="i"/>'
              '<a:graphic><a:graphicData><pic:pic><pic:blipFill><a:blip r:embed="rId9"/></pic:blipFill></pic:pic>'
              '</a:graphicData></a:graphic></wp:inline></w:drawing></w:r></w:p>')
        rel = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
               '<Relationship Id="rId9" Type="%s/image" Target="media/foto.png"/></Relationships>' % T.R_NS)
        ct = CT.replace('</Types>', '<Default Extension="png" ContentType="image/png"/></Types>')
        make_docx(self.f('o.docx'), p_(r_('x')) + dr, ns=NS_BASE + NS_DRAW, docrels=rel, content_types=ct,
                  extra={'word/media/foto.png': png_bytes(3, 3)})
        make_docx(self.f('d.docx'), p_(r_('d0')) + p_(r_('d1')))
        out = self.ok('copiar', self.f('d.docx'), self.f('o.docx'), '--desde', '1', '--antes', '1', '-o', self.f('e.docx'))
        self.assertTrue(out.startswith('OK: copiados B1..B1 de o.docx antes de B1 -> '))
        self.assertIn('word/media/foto.png', zipfile.ZipFile(str(self.f('e.docx'))).namelist())
        self.assertEqual(self.ok('verificar', self.f('e.docx')).splitlines()[0], 'OK')
        self.assertEqual(self.ok('comparar', self.f('d.docx'), self.f('d.docx')).split()[0], 'SIN')
        code, out, _ = run('comparar', self.f('d.docx'), self.f('e.docx'))
        self.assertEqual(code, 1)
        self.assertIn('imágenes: 0 -> 1', out)

    def test_extraer_e_insertar(self):
        doc_rows(self.f('a.docx'))
        self.ok('extraer', self.f('a.docx'), self.f('fr.xml'), '--desde', '3', '--hasta', '4')
        self.ok('insertar', self.f('a.docx'), self.f('fr.xml'), '--antes', '0', '-o', self.f('b.docx'))
        self.assertEqual(self.ok('mapa', self.f('b.docx')).splitlines()[0:3], ['B0 T0 1x1 "otra"', 'B1 P "fin"', 'B2 P "intro"'])

if __name__ == '__main__':
    unittest.main()

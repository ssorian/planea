#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""docx_tool: leer y editar DOCX con pocos tokens (solo biblioteca estándar).

Uso: python3 -I docx_tool.py <comando> archivo.docx [opciones]
     (Windows: py -I docx_tool.py ...  o  python -I docx_tool.py ...)

Diseño: document.xml NUNCA se reserializa. Se tokeniza para obtener los
desplazamientos (offsets) de los elementos y se edita por empalme de texto,
de modo que prefijos, mc:Ignorable y declaraciones de la raíz quedan intactos.
"""
import argparse
import hashlib
import html
import json
import os
import posixpath
import random
import re
import sys
import tempfile
import zipfile
from pathlib import Path
import xml.parsers.expat as expat

W_NS = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
R_NS = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
REL_MAIN = R_NS + '/officeDocument'

KNOWN_NS = {
    'w': W_NS, 'r': R_NS,
    'mc': 'http://schemas.openxmlformats.org/markup-compatibility/2006',
    'w14': 'http://schemas.microsoft.com/office/word/2010/wordml',
    'w15': 'http://schemas.microsoft.com/office/word/2012/wordml',
    'wp': 'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing',
    'wp14': 'http://schemas.microsoft.com/office/word/2010/wordprocessingDrawing',
    'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
    'pic': 'http://schemas.openxmlformats.org/drawingml/2006/picture',
    'wps': 'http://schemas.microsoft.com/office/word/2010/wordprocessingShape',
    'wpg': 'http://schemas.microsoft.com/office/word/2010/wordprocessingGroup',
    'v': 'urn:schemas-microsoft-com:vml', 'o': 'urn:schemas-microsoft-com:office:office',
    'w10': 'urn:schemas-microsoft-com:office:word',
    'm': 'http://schemas.openxmlformats.org/officeDocument/2006/math',
}


class ToolError(Exception):
    pass


# ----------------------------------------------------------------- utilidades
def esc(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def unesc(s):
    return html.unescape(s) if '&' in s else s


def trunc(s, n):
    s = re.sub(r'\s+', ' ', s).strip()
    return s if len(s) <= n else s[:max(1, n - 1)] + '…'


def q(s, n):
    return '"' + trunc(s, n) + '"'


def to_index(v):
    m = re.fullmatch(r'[BbTt]?(\d+)', str(v).strip())
    if not m:
        raise ToolError('índice no válido: %r' % (v,))
    return int(m.group(1))


def apply_splices(text, spl):
    spl = sorted(spl, key=lambda x: (x[0], x[1]))
    out, pos = [], 0
    for s, e, rep in spl:
        if s < pos:
            raise ToolError('ediciones solapadas en el documento (offset %d)' % s)
        out.append(text[pos:s])
        out.append(rep)
        pos = e
    out.append(text[pos:])
    return ''.join(out)


# ----------------------------------------------------------- tokenizador XML
TAG = re.compile(r'<(/?)([^\s/>!?]+)((?:"[^"]*"|\'[^\']*\'|[^>"\'])*)>')
# Elementos cuyo contenido no se desglosa (sus hijos no generan nodos).
OPAQUE = frozenset((
    'w:pPr', 'w:rPr', 'w:tcPr', 'w:tblPr', 'w:trPr', 'w:tblPrEx', 'w:sectPr',
    'w:tblGrid', 'w:drawing', 'w:pict', 'w:object', 'w:sdtPr', 'w:sdtEndPr'))


class Node:
    __slots__ = ('name', 's', 'oe', 'ce', 'e', 'kids', 'parent')

    def __init__(self, name, s, oe, parent):
        self.name, self.s, self.oe, self.parent = name, s, oe, parent
        self.ce = None   # inicio de la etiqueta de cierre (None si vacía)
        self.e = oe
        self.kids = []


def parse_tree(text):
    root = None
    stack = []   # (nodo|None, inc)
    skip = 0
    for m in TAG.finditer(text):
        closing, name, attrs = m.groups()
        if closing:
            if not stack:
                raise ToolError('XML mal formado (cierre inesperado) cerca de %d' % m.start())
            node, inc = stack.pop()
            if inc:
                skip -= 1
            if node is not None:
                node.ce = m.start()
                node.e = m.end()
            continue
        selfc = attrs.endswith('/')
        node = None
        if skip == 0:
            parent = stack[-1][0] if stack else None
            node = Node(name, m.start(), m.end(), parent)
            if parent is not None:
                parent.kids.append(node)
            elif root is None:
                root = node
        if selfc:
            continue
        inc = skip > 0 or name in OPAQUE
        if inc:
            skip += 1
        stack.append((node, inc))
    if stack:
        raise ToolError('XML mal formado (elementos sin cerrar)')
    return root


def kids_named(node, name, through=('w:sdt', 'w:sdtContent', 'w:customXml')):
    out = []
    for k in node.kids:
        if k.name == name:
            out.append(k)
        elif k.name in through:
            out.extend(kids_named(k, name, through))
    return out


def iter_paras(node):
    for k in node.kids:
        if k.name == 'w:p':
            yield k
        else:
            yield from iter_paras(k)


def ptext(p, text):
    out = []

    def rec(n):
        for k in n.kids:
            nm = k.name
            if nm == 'w:t':
                if k.ce is not None:
                    out.append(unesc(text[k.oe:k.ce]))
            elif nm == 'w:tab':
                out.append('\t')
            elif nm == 'w:br':
                if 'w:type="page"' not in text[k.s:k.oe] and 'w:type="column"' not in text[k.s:k.oe]:
                    out.append('\n')
            elif nm == 'w:noBreakHyphen':
                out.append('-')
            elif nm in OPAQUE:
                continue
            else:
                rec(k)
    rec(p)
    return ''.join(out)


def cell_paras(tc):
    return kids_named(tc, 'w:p')


def cell_tbls(tc):
    return kids_named(tc, 'w:tbl')


def cell_direct_text(tc, text):
    return ' / '.join(t for t in (ptext(p, text) for p in cell_paras(tc)) if t.strip())


def tbl_text_rows(tbl, text):
    rows = []
    for tr in kids_named(tbl, 'w:tr'):
        rows.append(' | '.join(cell_full_text(tc, text) for tc in kids_named(tr, 'w:tc')))
    return rows


def cell_full_text(tc, text):
    parts = []
    for k in tc.kids:
        if k.name == 'w:p':
            t = ptext(k, text)
            if t.strip():
                parts.append(t)
        elif k.name == 'w:tbl':
            parts.append('[' + '; '.join(tbl_text_rows(k, text)) + ']')
        elif k.name in ('w:sdt', 'w:sdtContent'):
            for p in iter_paras(k):
                t = ptext(p, text)
                if t.strip():
                    parts.append(t)
    return ' / '.join(parts)


def grid_widths(tbl, text):
    for k in tbl.kids:
        if k.name == 'w:tblGrid':
            seg = text[k.s:k.e]
            return [int(x) if x.isdigit() else x for x in re.findall(r'<w:gridCol\b[^>]*?\bw:w="(\d+)"', seg)] or \
                   [None] * len(re.findall(r'<w:gridCol\b', seg))
    return []


def tc_props(tc, text):
    span, vm = 1, None
    for k in tc.kids:
        if k.name == 'w:tcPr':
            seg = text[k.s:k.e]
            m = re.search(r'<w:gridSpan\b[^>]*?\bw:val="(\d+)"', seg)
            if m:
                span = int(m.group(1))
            m = re.search(r'<w:vMerge\b([^>]*)>', seg)
            if m:
                vm = 'restart' if 'restart' in m.group(1) else 'continue'
            break
    return span, vm


# -------------------------------------------------------------- paquete DOCX
def parse_rels(txt):
    out = []
    for m in re.finditer(r'<Relationship\b([^>]*?)/?>', txt):
        a = dict(re.findall(r'([\w:]+)="([^"]*)"', m.group(1)))
        out.append(a)
    return out


def resolve_target(source_dir, target):
    if target.startswith('/'):
        return posixpath.normpath(target[1:])
    return posixpath.normpath(posixpath.join(source_dir, target))


def ext_of(name):
    b = posixpath.basename(name)
    return b[1:] if b.startswith('.') and b.count('.') == 1 else posixpath.splitext(b)[1].lstrip('.')


def rels_name_for(part):
    d, b = posixpath.split(part)
    return posixpath.join(d, '_rels', b + '.rels')


class Docx:
    def __init__(self, path):
        self.path = Path(path)
        try:
            self.zf = zipfile.ZipFile(str(self.path))
        except FileNotFoundError:
            raise ToolError('no existe el archivo: %s' % path)
        except (zipfile.BadZipFile, IsADirectoryError, PermissionError) as e:
            raise ToolError('no es un ZIP/DOCX válido (%s): %s' % (e, path))
        self.infos = self.zf.infolist()
        self.names = [i.filename for i in self.infos]
        self.info_by = {i.filename: i for i in self.infos}
        self.texts = {}
        self.bom = {}
        self.modified = set()
        self.removed = set()
        self.added = []      # (nombre, bytes, compress_type)
        self._tree = None
        self.main = self._find_main()

    def _find_main(self):
        if '_rels/.rels' in self.info_by:
            for a in parse_rels(self.text('_rels/.rels')):
                if a.get('Type') == REL_MAIN:
                    return resolve_target('', a['Target'])
        return 'word/document.xml'

    def has(self, name):
        return name in self.info_by

    def bytes(self, name):
        if name not in self.info_by:
            raise ToolError('parte inexistente: %s' % name)
        return self.zf.read(name)

    def text(self, name):
        if name not in self.texts:
            b = self.bytes(name)
            self.bom[name] = b.startswith(b'\xef\xbb\xbf')
            try:
                self.texts[name] = b.decode('utf-8-sig')
            except UnicodeDecodeError:
                raise ToolError('%s no está en UTF-8' % name)
        return self.texts[name]

    def set_text(self, name, s):
        self.texts[name] = s
        self.modified.add(name)
        if name == self.main:
            self._tree = None

    @property
    def doc(self):
        return self.text(self.main)

    @property
    def tree(self):
        if self._tree is None:
            self._tree = parse_tree(self.doc)
        return self._tree

    @property
    def body(self):
        for k in self.tree.kids:
            if k.name == 'w:body':
                return k
        raise ToolError('document.xml sin w:body')

    @property
    def rels_name(self):
        return rels_name_for(self.main)

    def body_kids(self):
        return self.body.kids

    def table_index(self):
        """lista de (índice_body, nodo) de tablas de primer nivel."""
        return [(i, k) for i, k in enumerate(self.body_kids()) if k.name == 'w:tbl']

    def save(self, out, overwrite_ok=True):
        out = Path(out)
        names = list(self.names)
        ct = '[Content_Types].xml'
        order = ([ct] if ct in self.info_by else []) + [n for n in names if n != ct]
        fd, tmp = tempfile.mkstemp(prefix='.docx_tool_', suffix='.tmp', dir=str(out.resolve().parent))
        os.close(fd)
        try:
            with zipfile.ZipFile(tmp, 'w') as zo:
                for n in order:
                    if n in self.removed:
                        continue
                    src = self.info_by[n]
                    if n in self.texts and n in self.modified:
                        data = self.texts[n].encode('utf-8')
                        if self.bom.get(n):
                            data = b'\xef\xbb\xbf' + data
                    else:
                        data = self.zf.read(n)
                    zi = zipfile.ZipInfo(n, src.date_time)
                    zi.compress_type = src.compress_type
                    zi.external_attr = src.external_attr
                    zi.create_system = src.create_system
                    zo.writestr(zi, data, compress_type=src.compress_type)
                for n, data, ctype in self.added:
                    zi = zipfile.ZipInfo(n, (2024, 1, 1, 0, 0, 0))
                    zi.compress_type = ctype
                    zi.external_attr = 0o600 << 16
                    zo.writestr(zi, data, compress_type=ctype)
            try:
                um = os.umask(0)
                os.umask(um)
                os.chmod(tmp, 0o666 & ~um)
            except OSError:
                pass
            os.replace(tmp, str(out))
        except BaseException:
            try:
                os.unlink(tmp)
            except OSError:
                pass
            raise

    def all_names(self):
        return [n for n in self.names if n not in self.removed] + [a[0] for a in self.added]


def resolve_output(a, input_path):
    """Política de salida: nunca sobrescribe la entrada sin --sobrescribir."""
    inp = Path(input_path).resolve()
    if a.salida:
        out = Path(a.salida)
        if out.resolve() == inp and not a.sobrescribir:
            raise ToolError('la salida coincide con la entrada; usa otro -o o añade --sobrescribir')
    elif a.sobrescribir:
        out = Path(input_path)
    else:
        raise ToolError('falta -o salida.docx (o --sobrescribir para modificar el archivo de entrada)')
    d = out.resolve().parent
    for lock in ('.~lock.%s#' % out.name, '~$' + out.name[2:] if len(out.name) > 2 else '~$' + out.name):
        if (d / lock).exists():
            raise ToolError('el documento parece abierto en Word/LibreOffice (%s); ciérralo antes de escribir' % lock)
    if not d.is_dir():
        raise ToolError('no existe el directorio de salida: %s' % d)
    return out


# --------------------------------------------------------------- comandos
def body_range(doc, desde, hasta):
    kids = doc.body_kids()
    if desde is None:
        desde = 0
    if hasta is None:
        hasta = len(kids) - 1
    if not (0 <= desde <= hasta < len(kids)):
        raise ToolError('rango fuera de límites: %d..%d (el body tiene %d hijos, 0..%d)' % (desde, hasta, len(kids), len(kids) - 1))
    return desde, hasta


def cmd_info(a):
    d = Docx(a.archivo)
    size = Path(a.archivo).stat().st_size
    doc = d.doc
    names = d.names
    media = [n for n in names if '/media/' in n]
    media_size = sum(d.info_by[n].file_size for n in media)
    n_tbl_all = len(re.findall(r'<w:tbl[\s>]', doc))
    kids = d.body_kids()
    top = sum(1 for k in kids if k.name == 'w:tbl')
    n_p = len(re.findall(r'<w:p[\s>/]', doc))
    n_sect = len(re.findall(r'<w:sectPr[\s>/]', doc))
    n_img = len(re.findall(r'<a:blip\b', doc)) + len(re.findall(r'<v:imagedata\b', doc))
    ins = len(re.findall(r'<w:ins\s', doc))
    dele = len(re.findall(r'<w:del\s', doc))
    mov = len(re.findall(r'<w:move(?:From|To)\s', doc))
    print('%s  %d bytes, %d partes; %s %d bytes' % (Path(a.archivo).name, size, len(names), d.main, len(doc.encode('utf-8'))))
    print('body: %d hijos; párrafos %d; tablas %d (primer nivel %d); secciones %d; imágenes %d (media: %d archivos, %d bytes)'
          % (len(kids), n_p, n_tbl_all, top, n_sect, n_img, len(media), media_size))
    for pref, lab in (('header', 'encabezados'), ('footer', 'pies')):
        items = []
        for n in names:
            if re.fullmatch(r'word/%s\d*\.xml' % pref, n):
                t = d.text(n)
                tx = ' '.join(unesc(x) for x in re.findall(r'<w:t(?:\s[^>]*)?>([^<]*)</w:t>', t))
                items.append('%s %s' % (posixpath.basename(n), q(tx, a.ancho)))
        print('%s: %s' % (lab, '; '.join(items) if items else 'no'))
    com = 0
    if d.has('word/comments.xml'):
        com = len(re.findall(r'<w:comment\s', d.text('word/comments.xml')))
    print('comentarios: %d' % com)
    print('cambios controlados: ins=%d del=%d mov=%d' % (ins, dele, mov))
    macros = any(n.lower().endswith('vbaproject.bin') for n in names) or \
        ('macroEnabled' in d.text('[Content_Types].xml') if d.has('[Content_Types].xml') else False)
    sigs = [n for n in names if n.startswith('_xmlsignatures/')] or \
        (['signatureline'] if re.search(r'<o:signatureline\b|<w:signatureLine\b', doc) else [])
    print('macros: %s; firmas: %s' % ('sí' if macros else 'no', 'sí (%d)' % len(sigs) if sigs else 'no'))
    lock = Path(a.archivo).resolve()
    if (lock.parent / ('.~lock.%s#' % lock.name)).exists():
        print('AVISO: existe archivo de bloqueo; el documento puede estar abierto')
    return 0


def para_flags(p, text):
    seg = text[p.s:p.e]
    flags = []
    ppr = next((k for k in p.kids if k.name == 'w:pPr'), None)
    if ppr is not None:
        pseg = text[ppr.s:ppr.e]
        m = re.search(r'<w:pStyle\b[^>]*?\bw:val="([^"]*)"', pseg)
        if m and re.match(r'(?i)(heading|ttulo|titulo|title|subt)', m.group(1)):
            flags.append('est=' + m.group(1))
        if '<w:numPr>' in pseg or '<w:numPr ' in pseg:
            flags.append('LST')
        if '<w:pageBreakBefore' in pseg:
            flags.append('SALTO-PAG')
        m = re.search(r'<w:sectPr\b.*?</w:sectPr>', pseg, re.S)
        if m:
            t = re.search(r'<w:type\b[^>]*?\bw:val="([^"]*)"', m.group(0))
            flags.append('SALTO-SECC(%s)' % (t.group(1) if t else 'nextPage'))
    if re.search(r'<w:br\b[^>]*w:type="page"', seg):
        flags.append('SALTO-PAG')
    n = len(re.findall(r'<w:drawing[\s>]|<w:pict[\s>]', seg))
    if n:
        flags.append('IMG%d' % n)
    return flags


def cmd_mapa(a):
    d = Docx(a.archivo)
    text = d.doc
    kids = d.body_kids()
    lo, hi = body_range(d, a.desde, a.hasta)
    tn = {}
    c = 0
    for i, k in enumerate(kids):
        if k.name == 'w:tbl':
            tn[i] = c
            c += 1
    for i in range(lo, hi + 1):
        k = kids[i]
        if k.name == 'w:p':
            fl = para_flags(k, text)
            print('B%d P%s %s' % (i, (' [' + ' '.join(fl) + ']') if fl else '', q(ptext(k, text), a.ancho)))
        elif k.name == 'w:tbl':
            rows = kids_named(k, 'w:tr')
            cols = len(grid_widths(k, text)) or max([len(kids_named(r, 'w:tc')) for r in rows] or [0])
            first = ''
            for tr in rows:
                for tc in kids_named(tr, 'w:tc'):
                    first = cell_direct_text(tc, text)
                    if first:
                        break
                if first:
                    break
            n = len(re.findall(r'<w:drawing[\s>]|<w:pict[\s>]', text[k.s:k.e]))
            print('B%d T%d %dx%d%s %s' % (i, tn[i], len(rows), cols, (' [IMG%d]' % n) if n else '', q(first, a.ancho)))
        elif k.name == 'w:sectPr':
            t = re.search(r'<w:type\b[^>]*?\bw:val="([^"]*)"', text[k.s:k.e])
            print('B%d SECT%s' % (i, ' (%s)' % t.group(1) if t else ''))
        elif k.name == 'w:sdt':
            tx = ' / '.join(t for t in (ptext(p, text) for p in iter_paras(k)) if t.strip())
            print('B%d SDT %s' % (i, q(tx, a.ancho)))
        else:
            print('B%d X:%s' % (i, k.name))
    return 0


def list_table(tbl, path, text, ancho, out):
    rows = kids_named(tbl, 'w:tr')
    gw = grid_widths(tbl, text)
    out.append('# %s %dx%d grid=%s' % (path, len(rows), len(gw), ','.join(str(x) for x in gw)))
    for r, tr in enumerate(rows):
        for c, tc in enumerate(kids_named(tr, 'w:tc')):
            span, vm = tc_props(tc, text)
            tags = ''
            if span > 1:
                tags += ' [span=%d]' % span
            if vm == 'continue':
                tags += ' [vmerge]'
            elif vm == 'restart':
                tags += ' [vmerge-ini]'
            base = '%sF%dC%d' % (path, r, c)
            out.append('%s%s %s' % (base, tags, q(cell_direct_text(tc, text), ancho)))
            for n, t2 in enumerate(cell_tbls(tc)):
                list_table(t2, '%s.T%d' % (base, n), text, ancho, out)


def cmd_tablas(a):
    d = Docx(a.archivo)
    text = d.doc
    tbls = d.table_index()
    sel = range(len(tbls))
    if a.tabla is not None:
        t = to_index(a.tabla)
        if t >= len(tbls):
            raise ToolError('no existe T%d (hay %d tablas de primer nivel, T0..T%d)' % (t, len(tbls), len(tbls) - 1))
        sel = [t]
    out = []
    for t in sel:
        list_table(tbls[t][1], 'T%d' % t, text, a.ancho, out)
    print('\n'.join(out))
    return 0


def cmd_texto(a):
    d = Docx(a.archivo)
    text = d.doc
    kids = d.body_kids()
    lo, hi = body_range(d, a.desde, a.hasta if a.hasta is not None else a.desde)
    tn, c = {}, 0
    for i, k in enumerate(kids):
        if k.name == 'w:tbl':
            tn[i] = c
            c += 1
    for i in range(lo, hi + 1):
        k = kids[i]
        if k.name == 'w:p':
            print('B%d %s' % (i, ptext(k, text).replace('\n', ' ⏎ ')))
        elif k.name == 'w:tbl':
            print('B%d T%d' % (i, tn[i]))
            for r, row in enumerate(tbl_text_rows(k, text)):
                print('  F%d: %s' % (r, row.replace('\n', ' ⏎ ')))
        elif k.name in ('w:sdt',):
            for p in iter_paras(k):
                print('B%d %s' % (i, ptext(p, text).replace('\n', ' ⏎ ')))
        elif k.name == 'w:sectPr':
            print('B%d SECT' % i)
    return 0


def walk_tbl(tbl, prefix):
    for r, tr in enumerate(kids_named(tbl, 'w:tr')):
        for c, tc in enumerate(kids_named(tr, 'w:tc')):
            base = '%sF%dC%d' % (prefix, r, c)
            ps = cell_paras(tc)
            for k, p in enumerate(ps):
                yield base + ('/p%d' % k if len(ps) > 1 else ''), p
            for n, t2 in enumerate(cell_tbls(tc)):
                yield from walk_tbl(t2, '%s.T%d' % (base, n))


def iter_located(d, lo=0, hi=None):
    kids = d.body_kids()
    if hi is None:
        hi = len(kids) - 1
    tn, c = {}, 0
    for i, k in enumerate(kids):
        if k.name == 'w:tbl':
            tn[i] = c
            c += 1
    for i in range(lo, hi + 1):
        k = kids[i]
        if k.name == 'w:p':
            yield 'B%d' % i, k
        elif k.name == 'w:tbl':
            yield from walk_tbl(k, 'T%d' % tn[i])
        elif k.name != 'w:sectPr':
            for p in iter_paras(k):
                yield 'B%d' % i, p


def cmd_buscar(a):
    d = Docx(a.archivo)
    text = d.doc
    flags = 0 if a.sensible else re.I
    pat = re.compile(a.patron if a.regex else re.escape(a.patron), flags)
    n = 0
    for loc, p in iter_located(d):
        t = ptext(p, text)
        m = pat.search(t)
        if not m:
            continue
        cnt = len(pat.findall(t))
        s = max(0, m.start() - 20)
        ctx = t[s:m.end() + max(10, a.ancho - 20 - (m.end() - m.start()))]
        print('%s%s %s' % (loc, ' x%d' % cnt if cnt > 1 else '', q(('…' if s else '') + ctx, a.ancho + 20)))
        n += 1
        if a.max and n >= a.max:
            print('(límite --max %d alcanzado)' % a.max)
            break
    if n == 0:
        print('sin coincidencias')
    return 0


# ------------------------------------------------------------ edición de texto
def t_elem(seg):
    sp = ' xml:space="preserve"' if seg != seg.strip() else ''
    return '<w:t%s>%s</w:t>' % (sp, esc(seg))


def build_content(s):
    s = s.replace('\r\n', '\n').replace('\r', '\n')
    parts = []
    for li, line in enumerate(s.split('\n')):
        if li:
            parts.append('<w:br/>')
        for ti, seg in enumerate(line.split('\t')):
            if ti:
                parts.append('<w:tab/>')
            if seg:
                parts.append(t_elem(seg))
    return ''.join(parts)


def runs_of(n):
    out = []
    for k in n.kids:
        if k.name == 'w:r':
            out.append(k)
        elif k.name not in OPAQUE:
            out.extend(runs_of(k))
    return out


def run_text_kids(r, text):
    out = []
    for k in r.kids:
        if k.name in ('w:t', 'w:tab', 'w:noBreakHyphen'):
            out.append(k)
        elif k.name == 'w:br':
            tag = text[k.s:k.oe]
            if 'w:type="page"' not in tag and 'w:type="column"' not in tag:
                out.append(k)
    return out


def mark_rpr(p, text):
    ppr = next((k for k in p.kids if k.name == 'w:pPr'), None)
    if ppr is None:
        return ''
    m = re.search(r'<w:rPr>.*?</w:rPr>|<w:rPr/>', text[ppr.s:ppr.e], re.S)
    if not m:
        return ''
    return re.sub(r'<w:(?:ins|del|moveFrom|moveTo)\b[^>]*/>', '', m.group(0))


def run_rpr(r, text):
    for k in r.kids:
        if k.name == 'w:rPr':
            return text[k.s:k.e]
    return ''


def set_para_text(p, new, text):
    """Splices que dejan el párrafo con `new` conservando formato (primer run)."""
    spl = []
    content = build_content(new)
    if p.ce is None:
        run = '<w:r>%s%s</w:r>' % (mark_rpr(p, text), content) if content else ''
        head = text[p.s:p.e - 2].rstrip() + '>'
        # <w:p .../> -> <w:p ...>run</w:p>
        if run:
            spl.append((p.s, p.e, head + run + '</w:p>'))
        return spl
    runs = runs_of(p)
    target = None
    for r in runs:
        if any(k.name == 'w:t' for k in r.kids):
            target = r
            break
    placed = False
    for r in runs:
        tks = run_text_kids(r, text)
        if r is target:
            first_t = True
            for k in tks:
                if k.name == 'w:t' and first_t:
                    spl.append((k.s, k.e, content))
                    placed = True
                    first_t = False
                else:
                    spl.append((k.s, k.e, ''))
        else:
            for k in tks:
                spl.append((k.s, k.e, ''))
    if not placed and content:
        # sin w:t: usar un run textual sin objetos, o crear uno
        cand = None
        for r in runs:
            seg = text[r.s:r.e]
            if r.ce is not None and not re.search(r'<w:(?:drawing|pict|object|fldChar|instrText|footnoteReference|endnoteReference|commentReference)\b', seg):
                cand = r
                break
        if cand is not None:
            spl.append((cand.ce, cand.ce, content))
        else:
            spl.append((p.ce, p.ce, '<w:r>%s%s</w:r>' % (mark_rpr(p, text), content)))
    return spl


def clone_para(template, new, text):
    ppr = next((k for k in template.kids if k.name == 'w:pPr'), None)
    ppr_txt = ''
    if ppr is not None:
        ppr_txt = re.sub(r'<w:sectPr\b.*?</w:sectPr>|<w:sectPr\b[^>]*/>', '', text[ppr.s:ppr.e], flags=re.S)
    rpr = ''
    for r in runs_of(template):
        if any(k.name == 'w:t' for k in r.kids):
            rpr = run_rpr(r, text)
            break
    if not rpr:
        rpr = mark_rpr(template, text)
    content = build_content(new)
    run = '<w:r>%s%s</w:r>' % (rpr, content) if content else ''
    return '<w:p>%s%s</w:p>' % (ppr_txt, run)


def find_cell(d, coord):
    segs = coord.strip().split('.')
    tbls = d.table_index()
    cur_tc = None
    for depth, seg in enumerate(segs):
        m = re.fullmatch(r'T(\d+)F(\d+)C(\d+)', seg)
        if not m:
            raise ToolError('coordenada no válida: %r (formato T2F3C1 o T2F3C1.T0F0C0)' % coord)
        t, f, c = (int(x) for x in m.groups())
        if depth == 0:
            if t >= len(tbls):
                raise ToolError('%s: no existe T%d (hay %d)' % (coord, t, len(tbls)))
            tbl = tbls[t][1]
        else:
            nest = cell_tbls(cur_tc)
            if t >= len(nest):
                raise ToolError('%s: la celda no tiene tabla anidada T%d' % (coord, t))
            tbl = nest[t]
        rows = kids_named(tbl, 'w:tr')
        if f >= len(rows):
            raise ToolError('%s: no existe la fila F%d (hay %d)' % (coord, f, len(rows)))
        cells = kids_named(rows[f], 'w:tc')
        if c >= len(cells):
            raise ToolError('%s: no existe la celda C%d (la fila tiene %d)' % (coord, c, len(cells)))
        cur_tc = cells[c]
    return cur_tc


def edit_cell_splices(tc, value, text):
    new = [value] if isinstance(value, str) else list(value)
    if not new:
        new = ['']
    for v in new:
        if not isinstance(v, str):
            raise ToolError('los textos deben ser cadenas')
    ps = cell_paras(tc)
    spl = []
    if not ps:
        spl.append((tc.ce, tc.ce, ''.join('<w:p>%s</w:p>' % ('<w:r>%s</w:r>' % build_content(v) if v else '') for v in new)))
        return spl
    n = len(new)
    for i, p in enumerate(ps[:n]):
        spl.extend(set_para_text(p, new[i], text))
    if n > len(ps):
        tmpl = ps[-1]
        spl.append((tmpl.e, tmpl.e, ''.join(clone_para(tmpl, v, text) for v in new[len(ps):])))
    elif n < len(ps):
        extras = ps[n:]
        # no dejar la celda terminando en tabla
        last_kid = tc.kids[-1] if tc.kids else None
        keep_last = False
        remaining_last = None
        for k in reversed(tc.kids):
            if k.name in ('w:tcPr',):
                continue
            if k in extras:
                continue
            remaining_last = k
            break
        if remaining_last is not None and remaining_last.name == 'w:tbl':
            keep_last = True
        for j, p in enumerate(extras):
            seg = text[p.s:p.e]
            has_obj = re.search(r'<w:(?:drawing|pict|object)[\s>]', seg)
            if has_obj or (keep_last and j == len(extras) - 1):
                spl.extend(set_para_text(p, '', text))
            else:
                spl.append((p.s, p.e, ''))
    return spl


def cmd_editar_celdas(a):
    d = Docx(a.archivo)
    out = resolve_output(a, a.archivo)
    try:
        with open(a.cambios, 'r', encoding='utf-8') as fh:
            changes = json.load(fh)
    except (OSError, ValueError) as e:
        raise ToolError('no se pudo leer el JSON de cambios: %s' % e)
    if not isinstance(changes, dict) or not changes:
        raise ToolError('el JSON debe ser un objeto {"T2F3C1": "texto" | ["p1","p2"]}')
    text = d.doc
    spl, errs = [], []
    for coord, val in changes.items():
        try:
            if not isinstance(val, (str, list)):
                raise ToolError('%s: el valor debe ser texto o lista de textos' % coord)
            tc = find_cell(d, coord)
            spl.extend(edit_cell_splices(tc, val, text))
        except ToolError as e:
            errs.append(str(e))
    if errs:
        raise ToolError('sin cambios aplicados:\n  ' + '\n  '.join(errs))
    d.set_text(d.main, apply_splices(text, spl))
    d.save(out)
    print('OK: %d celdas editadas -> %s' % (len(changes), out))
    return 0


def fix_t_open(text, node, newtext):
    """Si el texto necesita xml:space=preserve y la etiqueta no lo tiene, devuelve la etiqueta nueva."""
    tag = text[node.s:node.oe]
    if newtext != newtext.strip() and 'xml:space' not in tag:
        return '<w:t xml:space="preserve"' + tag[len('<w:t'):]
    return None


def cmd_reemplazar(a):
    d = Docx(a.archivo)
    out = resolve_output(a, a.archivo)
    if not a.viejo:
        raise ToolError('el texto a buscar no puede estar vacío')
    text = d.doc
    lo, hi = body_range(d, a.desde, a.hasta)
    remaining = a.max if a.max else None
    spl = []
    total = 0
    cross_locs = []
    cross_n = 0
    for loc, p in iter_located(d, lo, hi):
        ts = []
        items = []
        for r in runs_of(p):
            for k in r.kids:
                if k.name == 'w:t' and k.ce is not None:
                    ts.append(k)
                    items.append(unesc(text[k.oe:k.ce]))
                elif k.name in ('w:tab', 'w:br'):
                    items.append('\x00')
        full = ''.join(items)
        tot = full.count(a.viejo)
        if not tot:
            continue
        within = sum(s.count(a.viejo) for s in items)
        cr = tot - within
        if cr > 0:
            cross_n += cr
            cross_locs.append(loc)
        for k in ts:
            if remaining is not None and remaining <= 0:
                break
            s = unesc(text[k.oe:k.ce])
            c = s.count(a.viejo)
            if not c:
                continue
            if remaining is not None:
                c = min(c, remaining)
                remaining -= c
            ns = s.replace(a.viejo, a.nuevo, c)
            newtag = fix_t_open(text, k, ns)
            if newtag:
                spl.append((k.s, k.oe, newtag))
            spl.append((k.oe, k.ce, esc(ns)))
            total += c
    if total:
        d.set_text(d.main, apply_splices(text, spl))
        d.save(out)
        print('OK: %d reemplazos -> %s' % (total, out))
    else:
        print('0 reemplazos; no se escribió salida')
    if cross_n:
        print('AVISO: %d coincidencias cruzan runs y NO se aplicaron en: %s' % (cross_n, ', '.join(cross_locs[:20])))
        print('       usa editar-celdas o texto/buscar para localizarlas y editarlas por coordenada')
    return 0


# -------------------------------------------------------- fragmentos (XML crudo)
def used_prefixes(frag):
    used = set(re.findall(r'<([A-Za-z_][\w.-]*):', frag))
    used |= set(re.findall(r'\s([A-Za-z_][\w.-]*):[\w.-]+\s*=', frag))
    for v in re.findall(r'\bRequires="([^"]*)"', frag):
        used |= set(v.split())
    local = set(re.findall(r'xmlns:([\w.-]+)\s*=', frag))
    used.discard('xml')
    used.discard('xmlns')
    return used - local


def root_decls(text):
    m = re.search(r'<[A-Za-z_][^>]*>', text)
    if not m:
        return {}, None
    return dict(re.findall(r'xmlns:([\w.-]+)\s*=\s*"([^"]*)"', m.group(0))), (m.start(), m.end())


def ensure_namespaces(d, frag, src_ns):
    decls, span = root_decls(d.doc)
    add = []
    for p in sorted(used_prefixes(frag)):
        uri = src_ns.get(p) or KNOWN_NS.get(p)
        if p in decls:
            if uri and decls[p] != uri:
                raise ToolError('el prefijo %s apunta a otro namespace en el destino (%s vs %s)' % (p, decls[p], uri))
            continue
        if not uri:
            raise ToolError('prefijo %s no declarado y desconocido; el fragmento debe incluir el comentario <!--ns ...--> o declararlo' % p)
        add.append((p, uri))
    return add, span


def fresh_ids(d, frag):
    """Reasigna paraId/textId/docPr/bookmark id duplicados. Devuelve (frag, cuenta)."""
    doc = d.doc
    rnd = random.Random(20260101)
    used_para = set(x.upper() for x in re.findall(r'w14:paraId="([0-9A-Fa-f]{8})"', doc))
    used_text = set(x.upper() for x in re.findall(r'w14:textId="([0-9A-Fa-f]{8})"', doc))
    used_doc = set(int(x) for x in re.findall(r'<wp:docPr\b[^>]*?\bid="(\d+)"', doc))
    used_bm = set(int(x) for x in re.findall(r'<w:bookmarkStart\b[^>]*?\bw:id="(\d+)"', doc))
    used_bm_names = set(re.findall(r'<w:bookmarkStart\b[^>]*?\bw:name="([^"]*)"', doc))
    cnt = {'paraId': 0, 'textId': 0, 'docPr': 0, 'bookmark': 0}

    def newhex(used):
        while True:
            v = '%08X' % rnd.randint(1, 0x7FFFFFFE)
            if v not in used:
                used.add(v)
                return v

    def sub_para(m):
        v = m.group(2).upper()
        if v in used_para:
            cnt['paraId'] += 1
            return m.group(1) + newhex(used_para) + m.group(3)
        used_para.add(v)
        return m.group(0)

    def sub_text(m):
        v = m.group(2).upper()
        if v == '77777777':
            return m.group(0)
        if v in used_text:
            cnt['textId'] += 1
            return m.group(1) + newhex(used_text) + m.group(3)
        used_text.add(v)
        return m.group(0)

    frag = re.sub(r'(w14:paraId=")([0-9A-Fa-f]{8})(")', sub_para, frag)
    frag = re.sub(r'(w14:textId=")([0-9A-Fa-f]{8})(")', sub_text, frag)

    def sub_doc(m):
        v = int(m.group(2))
        if v in used_doc:
            nv = max(used_doc) + 1
            used_doc.add(nv)
            cnt['docPr'] += 1
            return m.group(1) + str(nv) + m.group(3)
        used_doc.add(v)
        return m.group(0)

    frag = re.sub(r'(<wp:docPr\b[^>]*?\bid=")(\d+)(")', sub_doc, frag)

    bm_map = {}

    def sub_bm_start(m):
        tag = m.group(0)
        mid = re.search(r'\bw:id="(\d+)"', tag)
        if not mid:
            return tag
        old = int(mid.group(1))
        if old in used_bm or old in bm_map.values():
            nv = max(used_bm | set(bm_map.values()) | {0}) + 1
            bm_map[old] = nv
            used_bm.add(nv)
            cnt['bookmark'] += 1
            tag = tag.replace('w:id="%d"' % old, 'w:id="%d"' % nv, 1)
        else:
            bm_map.setdefault(old, old)
            used_bm.add(old)
        nm = re.search(r'\bw:name="([^"]*)"', tag)
        if nm and nm.group(1) in used_bm_names:
            k = 2
            while '%s_%d' % (nm.group(1), k) in used_bm_names:
                k += 1
            newn = '%s_%d' % (nm.group(1), k)
            tag = tag.replace('w:name="%s"' % nm.group(1), 'w:name="%s"' % newn, 1)
            used_bm_names.add(newn)
        elif nm:
            used_bm_names.add(nm.group(1))
        return tag

    frag = re.sub(r'<w:bookmarkStart\b[^>]*>', sub_bm_start, frag)

    def sub_bm_end(m):
        old = int(m.group(2))
        if old in bm_map and bm_map[old] != old:
            return m.group(1) + str(bm_map[old]) + m.group(3)
        return m.group(0)

    frag = re.sub(r'(<w:bookmarkEnd\b[^>]*?\bw:id=")(\d+)(")', sub_bm_end, frag)
    return frag, cnt


def style_warnings(d, frag):
    warns = []
    if d.has('word/styles.xml'):
        have = set(re.findall(r'w:styleId="([^"]*)"', d.text('word/styles.xml')))
        need = set(re.findall(r'<w:(?:pStyle|rStyle|tblStyle)\b[^>]*?\bw:val="([^"]*)"', frag))
        miss = sorted(need - have)
        if miss:
            warns.append('estilos ausentes en el destino (se verán con formato por defecto): ' + ', '.join(miss[:10]))
    if d.has('word/numbering.xml'):
        have = set(re.findall(r'<w:num\b[^>]*?\bw:numId="(\d+)"', d.text('word/numbering.xml')))
        need = set(re.findall(r'<w:numId\b[^>]*?\bw:val="(\d+)"', frag)) - {'0'}
        miss = sorted(need - have)
        if miss:
            warns.append('numId ausentes en el destino: ' + ', '.join(miss[:10]))
    return warns


class Importer:
    """Copia partes/relaciones/content types necesarias desde otro DOCX."""

    def __init__(self, dst, src):
        self.dst, self.src = dst, src
        self.map = {}          # parte origen -> parte destino
        self.rel_log = []
        self.reused = 0
        self.copied = 0
        self.dst_rels = dst.text(dst.rels_name) if dst.has(dst.rels_name) else \
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"></Relationships>'
        self.hash_idx = None

    def taken(self):
        s = set(n.lower() for n in self.dst.all_names())
        return s

    def uniq(self, name):
        taken = self.taken()
        if name.lower() not in taken:
            return name
        stem, ext = posixpath.splitext(name)
        k = 2
        while ('%s_%d%s' % (stem, k, ext)).lower() in taken:
            k += 1
        return '%s_%d%s' % (stem, k, ext)

    def find_same(self, data, name):
        d = self.dst
        if d.has(name) and name not in d.removed and d.bytes(name) == data:
            return name
        for n, b, _ in d.added:
            if b == data and n.startswith('word/media/'):
                return n
        for i in d.infos:
            if i.filename.startswith('word/media/') and i.file_size == len(data) and i.filename not in d.removed:
                if d.zf.read(i.filename) == data:
                    return i.filename
        return None

    def ensure_ct(self, src_part, dst_part):
        sct = self.src.text('[Content_Types].xml')
        dct = self.dst.text('[Content_Types].xml')
        ov = re.search(r'<Override\b[^>]*?\bPartName="/%s"[^>]*?/>' % re.escape(src_part), sct)
        add = ''
        if ov:
            ctype = re.search(r'ContentType="([^"]*)"', ov.group(0)).group(1)
            if not re.search(r'<Override\b[^>]*?\bPartName="/%s"' % re.escape(dst_part), dct):
                add = '<Override PartName="/%s" ContentType="%s"/>' % (dst_part, ctype)
        else:
            ext = ext_of(src_part)
            dm = None
            for m in re.finditer(r'<Default\b[^>]*/>', sct):
                e = re.search(r'Extension="([^"]*)"', m.group(0))
                if e and e.group(1).lower() == ext.lower():
                    dm = m.group(0)
                    break
            if dm is None:
                raise ToolError('sin tipo de contenido para %s en el origen' % src_part)
            ctype = re.search(r'ContentType="([^"]*)"', dm).group(1)
            dext = None
            for m in re.finditer(r'<Default\b[^>]*/>', dct):
                e = re.search(r'Extension="([^"]*)"', m.group(0))
                if e and e.group(1).lower() == ext.lower():
                    dext = re.search(r'ContentType="([^"]*)"', m.group(0)).group(1)
                    break
            if dext is None:
                add = '<Default Extension="%s" ContentType="%s"/>' % (ext, ctype)
            elif dext != ctype:
                if not re.search(r'<Override\b[^>]*?\bPartName="/%s"' % re.escape(dst_part), dct):
                    add = '<Override PartName="/%s" ContentType="%s"/>' % (dst_part, ctype)
        if add:
            dct = dct.replace('</Types>', add + '</Types>')
            self.dst.set_text('[Content_Types].xml', dct)

    def copy_part(self, sp):
        if sp in self.map:
            return self.map[sp]
        if not self.src.has(sp):
            raise ToolError('el origen referencia una parte inexistente: %s' % sp)
        data = self.src.bytes(sp)
        is_xml = sp.endswith('.xml') or sp.endswith('.rels')
        if not is_xml:
            same = self.find_same(data, sp)
            if same:
                self.map[sp] = same
                self.reused += 1
                return same
        newname = self.uniq(sp)
        self.map[sp] = newname
        ctype = self.src.info_by[sp].compress_type
        relsn = rels_name_for(sp)
        if self.src.has(relsn):
            rtxt = self.src.text(relsn)
            sdir = posixpath.dirname(sp)
            ndir = posixpath.dirname(newname)

            def fix(m):
                tag = m.group(0)
                if 'TargetMode="External"' in tag:
                    return tag
                tm = re.search(r'Target="([^"]*)"', tag)
                if not tm:
                    return tag
                tp = self.copy_part(resolve_target(sdir, unesc(tm.group(1))))
                rel = posixpath.relpath(tp, ndir or '.')
                return tag.replace(tm.group(0), 'Target="%s"' % esc(rel), 1)
            rtxt = re.sub(r'<Relationship\b[^>]*?/>', fix, rtxt)
            self.dst.added.append((rels_name_for(newname), rtxt.encode('utf-8'), zipfile.ZIP_DEFLATED))
        self.dst.added.append((newname, data, ctype))
        self.copied += 1
        self.ensure_ct(sp, newname)
        return newname

    def new_rel_id(self):
        ids = [int(x) for x in re.findall(r'\bId="rId(\d+)"', self.dst_rels)]
        return 'rId%d' % (max(ids or [0]) + 1)

    def map_rid(self, rid, src_rels):
        a = src_rels.get(rid)
        if a is None:
            return rid, False
        typ, tgt = a.get('Type', ''), a.get('Target', '')
        external = a.get('TargetMode') == 'External'
        if external:
            key_target = tgt
        else:
            sp = resolve_target(posixpath.dirname(self.src.main), unesc(tgt))
            np = self.copy_part(sp)
            key_target = esc(posixpath.relpath(np, posixpath.dirname(self.dst.main) or '.'))
        for m in re.finditer(r'<Relationship\b[^>]*?/>', self.dst_rels):
            b = dict(re.findall(r'([\w:]+)="([^"]*)"', m.group(0)))
            if b.get('Type') == typ and b.get('Target') == key_target and (b.get('TargetMode') == 'External') == external:
                return b['Id'], True
        nid = self.new_rel_id()
        rel = '<Relationship Id="%s" Type="%s" Target="%s"%s/>' % (nid, typ, key_target, ' TargetMode="External"' if external else '')
        self.dst_rels = self.dst_rels.replace('</Relationships>', rel + '</Relationships>')
        self.rel_log.append((rid, nid))
        return nid, True

    def remap_fragment(self, frag, rprefix):
        src_rels = {a['Id']: a for a in parse_rels(self.src.text(self.src.rels_name))} if self.src.has(self.src.rels_name) else {}
        ids = set(m.group(2) for m in re.finditer(r'(\s%s:[A-Za-z]+=")([^"]*)(")' % re.escape(rprefix), frag))
        mapping = {}
        for rid in sorted(ids):
            mapping[rid] = self.map_rid(rid, src_rels)[0]
        frag = re.sub(r'(\s%s:[A-Za-z]+=")([^"]*)(")' % re.escape(rprefix),
                      lambda m: m.group(1) + mapping.get(m.group(2), m.group(2)) + m.group(3), frag)
        self.dst.set_text(self.dst.rels_name, self.dst_rels)
        return frag


def parse_ns_comment(frag):
    m = re.match(r'\s*<!--ns (.*?)-->\s*', frag, re.S)
    if not m:
        return frag, {}
    return frag[m.end():], dict(re.findall(r'xmlns:([\w.-]+)="([^"]*)"', m.group(1)))


def splice_fragment(d, frag, src_ns, antes, importer=None, rprefix='r'):
    kids = d.body_kids()
    if not (0 <= antes <= len(kids)):
        raise ToolError('--antes fuera de rango (0..%d)' % len(kids))
    if antes == len(kids) or (antes == len(kids) - 1 and kids[antes].name == 'w:sectPr'):
        antes = len(kids) - 1 if kids[-1].name == 'w:sectPr' else len(kids)
    pos = kids[antes].s if antes < len(kids) else kids[-1].e
    info = {}
    if importer is not None:
        frag = importer.remap_fragment(frag, rprefix)
        info['rels'] = len(importer.rel_log)
        info['partes_copiadas'] = importer.copied
        info['partes_reutilizadas'] = importer.reused
    add, span = ensure_namespaces(d, frag, src_ns)
    frag, ids = fresh_ids(d, frag)
    info['ids_reasignados'] = ids
    text = d.doc
    new = text[:pos] + frag + text[pos:]
    if add:
        s, e = span
        close = new[e - 2:e] == '/>'
        ins_at = e - 2 if close else e - 1
        new = new[:ins_at] + ''.join(' xmlns:%s="%s"' % (p, u) for p, u in add) + new[ins_at:]
    info['ns_añadidos'] = [p for p, _ in add]
    d.set_text(d.main, new)
    return info


def fmt_info(info):
    parts = []
    for k, v in info.items():
        if isinstance(v, dict):
            v = ','.join('%s=%d' % (a, b) for a, b in v.items() if b) or '0'
        elif isinstance(v, list):
            v = ','.join(v) or '0'
        parts.append('%s=%s' % (k, v))
    return ' '.join(parts)


def cmd_extraer(a):
    d = Docx(a.archivo)
    kids = d.body_kids()
    lo, hi = body_range(d, a.desde, a.hasta if a.hasta is not None else a.desde)
    frag = d.doc[kids[lo].s:kids[hi].e]
    decls, _ = root_decls(d.doc)
    used = sorted(used_prefixes(frag))
    header = '<!--ns %s-->\n' % ' '.join('xmlns:%s="%s"' % (p, decls[p]) for p in used if p in decls)
    with open(a.fragmento, 'w', encoding='utf-8', newline='') as fh:
        fh.write(header + frag)
    rids = len(re.findall(r'\sr:[A-Za-z]+="', frag))
    print('OK: B%d..B%d (%d caracteres) -> %s' % (lo, hi, len(frag), a.fragmento))
    if rids:
        print('AVISO: el fragmento tiene %d referencias r:* (imágenes/enlaces); para reutilizarlas usa `copiar` en lugar de `insertar`' % rids)
    return 0


def cmd_insertar(a):
    d = Docx(a.archivo)
    out = resolve_output(a, a.archivo)
    try:
        raw = Path(a.fragmento).read_text(encoding='utf-8')
    except OSError as e:
        raise ToolError('no se pudo leer el fragmento: %s' % e)
    frag, ns = parse_ns_comment(raw)
    if not frag.strip():
        raise ToolError('fragmento vacío')
    if re.search(r'\sr:[A-Za-z]+="', frag):
        print('AVISO: el fragmento contiene referencias r:*; no se crean relaciones (usa `copiar` para imágenes)')
    info = splice_fragment(d, frag, ns, a.antes)
    for w in style_warnings(d, frag):
        print('AVISO: ' + w)
    d.save(out)
    print('OK: fragmento insertado antes de B%d -> %s (%s)' % (a.antes, out, fmt_info(info)))
    return 0


# ------------------------------------------------- estilos y numeración (copiar)
STYLE_RE = re.compile(r'<w:style\b[^>]*?\bw:styleId="([^"]*)"[^>]*?(?:/>|>.*?</w:style>)', re.S)
NUM_RE = re.compile(r'<w:num\b[^>]*?\bw:numId="(\d+)"[^>]*?>.*?</w:num>', re.S)
ABS_RE = re.compile(r'<w:abstractNum\b[^>]*?\bw:abstractNumId="(\d+)"[^>]*?>.*?</w:abstractNum>', re.S)
NUMID_RE = re.compile(r'(<w:numId\b[^>]*?\bw:val=")(\d+)(")')
NUMBERING_CT = 'application/vnd.openxmlformats-officedocument.wordprocessingml.numbering+xml'
NUMBERING_REL = R_NS + '/numbering'


def find_part(doc, suffix, default):
    if doc.has(doc.rels_name):
        for a in parse_rels(doc.text(doc.rels_name)):
            if a.get('Type', '').endswith('/' + suffix) and a.get('TargetMode') != 'External':
                return resolve_target(posixpath.dirname(doc.main), unesc(a['Target']))
    return default if doc.has(default) else None


def add_root_ns(text, snippet, src_text):
    sdecl, _ = root_decls(src_text)
    ddecl, span = root_decls(text)
    add = []
    for p in sorted(used_prefixes(snippet)):
        if p in ddecl:
            continue
        uri = sdecl.get(p) or KNOWN_NS.get(p)
        if not uri:
            raise ToolError('prefijo %s sin namespace conocido al copiar estilos/numeración' % p)
        add.append(' xmlns:%s="%s"' % (p, uri))
    if add:
        e = span[1]
        at = e - 2 if text[e - 2:e] == '/>' else e - 1
        text = text[:at] + ''.join(add) + text[at:]
    return text


def lst(items, n=12):
    items = list(items)
    return ','.join(items[:n]) + ('+%d' % (len(items) - n) if len(items) > n else '') if items else '-'


def import_styles_numbering(d, s, frag, imp):
    """Copia estilos y numeración que usa `frag`. Devuelve (frag, informe)."""
    copied_styles, kept_styles, nummap = [], [], []
    style_texts = {}
    sp_name = find_part(s, 'styles', 'word/styles.xml')
    dp_name = find_part(d, 'styles', 'word/styles.xml')
    if sp_name and dp_name:
        src_st = {m.group(1): m.group(0) for m in STYLE_RE.finditer(s.text(sp_name))}
        dst_ids = set(m.group(1) for m in STYLE_RE.finditer(d.text(dp_name)))
        queue = re.findall(r'<w:(?:pStyle|rStyle|tblStyle)\b[^>]*?\bw:val="([^"]*)"', frag)
        seen = set()
        while queue:
            sid = queue.pop(0)
            if sid in seen or sid not in src_st:
                continue
            seen.add(sid)
            if sid in dst_ids:
                kept_styles.append(sid)
                continue
            txt = re.sub(r'(<w:style\b[^>]*?)\s+w:default="(?:1|true|on)"', r'\1', src_st[sid], count=1)
            style_texts[sid] = txt
            copied_styles.append(sid)
            queue.extend(re.findall(r'<w:(?:basedOn|link|next)\b[^>]*?\bw:val="([^"]*)"', txt))
    else:
        if re.search(r'<w:(?:pStyle|rStyle|tblStyle)\b', frag):
            print('AVISO: falta styles.xml en origen o destino; no se copiaron estilos')
    # numeración
    ids = set(m.group(2) for m in NUMID_RE.finditer(frag)) - {'0'}
    for t in style_texts.values():
        ids |= set(m.group(2) for m in NUMID_RE.finditer(t)) - {'0'}
    sn_name = find_part(s, 'numbering', 'word/numbering.xml')
    mapping = {}
    if ids and sn_name:
        src_num = s.text(sn_name)
        nums = {m.group(1): m.group(0) for m in NUM_RE.finditer(src_num)}
        abss = {m.group(1): m.group(0) for m in ABS_RE.finditer(src_num)}
        dn_name = find_part(d, 'numbering', 'word/numbering.xml')
        create = dn_name is None
        if create:
            om = re.search(r'<w:numbering\b[^>]*>', src_num)
            dst_num = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n' + om.group(0) + '</w:numbering>'
        else:
            dst_num = d.text(dn_name)
        next_abs = max([int(x) for x in re.findall(r'<w:abstractNum\b[^>]*?\bw:abstractNumId="(\d+)"', dst_num)] or [-1]) + 1
        next_num = max([int(x) for x in re.findall(r'<w:num\b[^>]*?\bw:numId="(\d+)"', dst_num)] or [0]) + 1
        rnd = random.Random(20260102)
        absmap, new_abs, new_nums = {}, [], []
        for nid in sorted(ids, key=int):
            if nid not in nums:
                continue
            ntxt = nums[nid]
            am = re.search(r'<w:abstractNumId\b[^>]*?\bw:val="(\d+)"', ntxt)
            aid = am.group(1) if am else None
            if aid is not None and aid not in absmap:
                if aid not in abss:
                    continue
                atxt = abss[aid]
                if 'lvlPicBulletId' in atxt:
                    print('AVISO: la numeración %s usa viñetas de imagen (numPicBullet); no se copian las imágenes' % nid)
                atxt = re.sub(r'(<w:abstractNum\b[^>]*?\bw:abstractNumId=")\d+(")', lambda m: m.group(1) + str(next_abs) + m.group(2), atxt, count=1)
                atxt = re.sub(r'(<w:nsid\b[^>]*?\bw:val=")[0-9A-Fa-f]{8}(")', lambda m: m.group(1) + '%08X' % rnd.randint(1, 0x7FFFFFFE) + m.group(2), atxt, count=1)
                absmap[aid] = next_abs
                new_abs.append(atxt)
                next_abs += 1
            ntxt = re.sub(r'(<w:num\b[^>]*?\bw:numId=")\d+(")', lambda m: m.group(1) + str(next_num) + m.group(2), ntxt, count=1)
            if aid is not None:
                ntxt = re.sub(r'(<w:abstractNumId\b[^>]*?\bw:val=")\d+(")', lambda m: m.group(1) + str(absmap[aid]) + m.group(2), ntxt, count=1)
            mapping[nid] = str(next_num)
            nummap.append('%s→%d' % (nid, next_num))
            new_nums.append(ntxt)
            next_num += 1
        if new_nums:
            if new_abs:
                m = re.search(r'<w:num[\s>]', dst_num) or re.search(r'<w:numIdMacAtCleanup\b', dst_num) or re.search(r'</w:numbering>', dst_num)
                dst_num = dst_num[:m.start()] + ''.join(new_abs) + dst_num[m.start():]
            m = re.search(r'<w:numIdMacAtCleanup\b', dst_num) or re.search(r'</w:numbering>', dst_num)
            dst_num = dst_num[:m.start()] + ''.join(new_nums) + dst_num[m.start():]
            dst_num = add_root_ns(dst_num, ''.join(new_abs + new_nums), src_num)
            if create:
                base = posixpath.dirname(d.main)
                name = imp.uniq(posixpath.join(base, 'numbering.xml'))
                d.added.append((name, dst_num.encode('utf-8'), zipfile.ZIP_DEFLATED))
                rid = imp.new_rel_id()
                imp.dst_rels = imp.dst_rels.replace('</Relationships>', '<Relationship Id="%s" Type="%s" Target="%s"/></Relationships>' % (
                    rid, NUMBERING_REL, esc(posixpath.relpath(name, base or '.'))))
                ct = d.text('[Content_Types].xml')
                d.set_text('[Content_Types].xml', ct.replace('</Types>', '<Override PartName="/%s" ContentType="%s"/></Types>' % (name, NUMBERING_CT)))
            else:
                d.set_text(dn_name, dst_num)
    elif ids:
        print('AVISO: el origen no tiene numbering.xml; no se copiaron numeraciones')
    if mapping:
        sub = lambda m: m.group(1) + mapping.get(m.group(2), m.group(2)) + m.group(3)
        frag = NUMID_RE.sub(sub, frag)
        for k in style_texts:
            style_texts[k] = NUMID_RE.sub(sub, style_texts[k])
    if style_texts:
        st = d.text(dp_name)
        body = ''.join(style_texts[k] for k in copied_styles)
        st = st.replace('</w:styles>', body + '</w:styles>')
        st = add_root_ns(st, body, s.text(sp_name))
        d.set_text(dp_name, st)
    report = 'numeraciones: %s; estilos copiados: %s; estilos coincidentes conservados: %s' % (
        lst(nummap), lst(copied_styles), lst(kept_styles))
    return frag, report


def cmd_copiar(a):
    d = Docx(a.archivo)
    s = Docx(a.origen)
    out = resolve_output(a, a.archivo)
    skids = s.body_kids()
    lo, hi = body_range(s, a.desde, a.hasta if a.hasta is not None else a.desde)
    if any(k.name == 'w:sectPr' for k in skids[lo:hi + 1]):
        raise ToolError('el rango incluye el sectPr final del origen; excluye ese índice')
    frag = s.doc[skids[lo].s:skids[hi].e]
    sdecl, _ = root_decls(s.doc)
    rprefix = next((p for p, u in sdecl.items() if u == R_NS), 'r')
    imp = Importer(d, s)
    frag, rep = import_styles_numbering(d, s, frag, imp)
    info = splice_fragment(d, frag, sdecl, a.antes, importer=imp, rprefix=rprefix)
    d.save(out)
    print('OK: copiados B%d..B%d de %s antes de B%d -> %s' % (lo, hi, Path(a.origen).name, a.antes, out))
    print('    ' + fmt_info(info))
    print('    ' + rep)
    return 0


def rid_set(text, prefix='r'):
    return set(m.group(1) for m in re.finditer(r'\s%s:[A-Za-z]+="([^"]*)"' % re.escape(prefix), text))


def cmd_borrar(a):
    d = Docx(a.archivo)
    out = resolve_output(a, a.archivo)
    kids = d.body_kids()
    lo, hi = body_range(d, a.desde, a.hasta if a.hasta is not None else a.desde)
    if kids[hi].name == 'w:sectPr' and hi == len(kids) - 1:
        raise ToolError('no se puede borrar el sectPr final del body')
    text = d.doc
    new = text[:kids[lo].s] + text[kids[hi].e:]
    removed_parts = []
    if a.limpiar_media:
        before = rid_set(text)
        after = rid_set(new)
        gone = before - after
        rels_txt = d.text(d.rels_name)
        rels = parse_rels(rels_txt)
        byid = {r['Id']: r for r in rels}
        drop_ids = [i for i in gone if i in byid]
        for i in drop_ids:
            rels_txt = re.sub(r'<Relationship\b[^>]*?\bId="%s"[^>]*?/>' % re.escape(i), '', rels_txt)
        d.set_text(d.rels_name, rels_txt)
        removed_parts = gc_parts(d, [resolve_target(posixpath.dirname(d.main), unesc(byid[i]['Target']))
                                     for i in drop_ids if byid[i].get('TargetMode') != 'External'])
    d.set_text(d.main, new)
    d.save(out)
    print('OK: borrados B%d..B%d (%d hijos) -> %s%s' % (lo, hi, hi - lo + 1, out,
          ('; partes eliminadas: %d' % len(removed_parts)) if a.limpiar_media else ''))
    return 0


def all_rel_targets(d):
    refs = set()
    for n in d.all_names():
        if n.endswith('.rels'):
            if n in d.removed:
                continue
            txt = d.text(n) if (n in d.texts or d.has(n)) else None
            if txt is None:
                continue
            base = posixpath.dirname(posixpath.dirname(n))
            for a in parse_rels(txt):
                if a.get('TargetMode') != 'External' and 'Target' in a:
                    refs.add(resolve_target(base, unesc(a['Target'])).lower())
    return refs


def gc_parts(d, candidates):
    removed = []
    queue = list(candidates)
    while queue:
        part = queue.pop()
        if part in d.removed or not d.has(part):
            continue
        if part.lower() in all_rel_targets(d):
            continue
        d.removed.add(part)
        removed.append(part)
        rn = rels_name_for(part)
        if d.has(rn) and rn not in d.removed:
            base = posixpath.dirname(part)
            for a in parse_rels(d.text(rn)):
                if a.get('TargetMode') != 'External' and 'Target' in a:
                    queue.append(resolve_target(base, unesc(a['Target'])))
            d.removed.add(rn)
        ct = '[Content_Types].xml'
        txt = d.text(ct)
        nt = re.sub(r'<Override\b[^>]*?\bPartName="/%s"[^>]*?/>' % re.escape(part), '', txt)
        if nt != txt:
            d.set_text(ct, nt)
    return removed


# ---------------------------------------------------------------- verificar
def check_wellformed(data):
    p = expat.ParserCreate(namespace_separator=' ')
    p.Parse(data, True)


def dup_report(items):
    seen, dups = set(), set()
    for x in items:
        if x in seen:
            dups.add(x)
        seen.add(x)
    return sorted(dups)


def cmd_verificar(a):
    problems, avisos = [], []
    try:
        d = Docx(a.archivo)
    except ToolError as e:
        print('PROBLEMAS (1)\n- %s' % e)
        return 1
    bad = d.zf.testzip()
    if bad:
        problems.append('ZIP corrupto en la parte %s' % bad)
    dn = dup_report([n.lower() for n in d.names])
    if dn:
        problems.append('partes duplicadas en el ZIP: %s' % ', '.join(dn[:5]))
    if d.names and d.names[0] != '[Content_Types].xml':
        problems.append('[Content_Types].xml no es la primera entrada del ZIP')
    parts = set(d.names)
    xml_parts = [n for n in d.names if n.endswith('.xml') or n.endswith('.rels')]
    for n in xml_parts:
        try:
            check_wellformed(d.bytes(n))
        except expat.ExpatError as e:
            problems.append('%s: XML no parsea (%s)' % (n, e))
        except (zipfile.BadZipFile, ToolError) as e:
            problems.append('%s: %s' % (n, e))
    # content types
    ct = d.text('[Content_Types].xml') if d.has('[Content_Types].xml') else ''
    defaults = set(m.lower() for m in re.findall(r'<Default\b[^>]*?\bExtension="([^"]*)"', ct))
    overrides = set(m.lower() for m in re.findall(r'<Override\b[^>]*?\bPartName="/?([^"]*)"', ct))
    for n in d.names:
        if n == '[Content_Types].xml' or n.endswith('/'):
            continue
        ext = ext_of(n).lower()
        if n.lower() not in overrides and ext not in defaults:
            problems.append('sin tipo de contenido: %s' % n)
    for o in overrides:
        if o not in set(x.lower() for x in d.names):
            avisos.append('Override a parte inexistente: /%s' % o)
    # relaciones
    referenced = set()
    for n in d.names:
        if not n.endswith('.rels'):
            continue
        try:
            txt = d.text(n)
        except ToolError:
            continue
        base = posixpath.dirname(posixpath.dirname(n))
        ids = []
        for at in parse_rels(txt):
            ids.append(at.get('Id'))
            if at.get('TargetMode') == 'External' or 'Target' not in at:
                continue
            tp = resolve_target(base, unesc(at['Target']))
            referenced.add(tp.lower())
            if tp not in parts:
                problems.append('%s: Id=%s apunta a parte inexistente %s' % (n, at.get('Id'), tp))
        dd = dup_report(ids)
        if dd:
            problems.append('%s: Id de relación duplicado: %s' % (n, ', '.join(dd)))
    # r:id en cada parte
    for n in d.names:
        if not (n.endswith('.xml') and not n.endswith('.rels')) or n == '[Content_Types].xml':
            continue
        try:
            txt = d.text(n)
        except ToolError:
            continue
        m = re.search(r'xmlns:([\w.-]+)="%s"' % re.escape(R_NS), txt[:30000])
        if not m:
            continue
        used = rid_set(txt, m.group(1))
        if not used:
            continue
        rn = rels_name_for(n)
        have = set(a.get('Id') for a in parse_rels(d.text(rn))) if d.has(rn) else set()
        miss = sorted(used - have)
        if miss:
            problems.append('%s: r:id sin relación (%s%s)' % (n, ', '.join(miss[:5]), '…' if len(miss) > 5 else ''))
    orphans = [n for n in d.names if not n.endswith('.rels') and n != '[Content_Types].xml'
               and not n.endswith('/') and n.lower() not in referenced]
    if orphans:
        med = [n for n in orphans if '/media/' in n]
        avisos.append('partes huérfanas (sin relación): %d%s (media: %d) %s%s'
                      % (len(orphans), '', len(med), ', '.join(orphans[:6]), '…' if len(orphans) > 6 else ''))
    # relaciones de imagen sin uso en el cuerpo
    if d.has(d.rels_name) and d.has(d.main):
        mm = re.search(r'xmlns:([\w.-]+)="%s"' % re.escape(R_NS), d.doc[:30000])
        used_ids = rid_set(d.doc, mm.group(1)) if mm else set()
        unused = [x['Id'] for x in parse_rels(d.text(d.rels_name))
                  if x.get('Type', '').endswith('/image') and x.get('Id') not in used_ids]
        if unused:
            avisos.append('%s: %d relaciones de imagen sin uso en el cuerpo (¿borrar con --limpiar-media? solo si ningún encabezado las usa): %s'
                          % (d.rels_name, len(unused), ', '.join(unused[:5])))
    # ids duplicados
    for n in d.names:
        if not re.fullmatch(r'word/(document|header\d*|footer\d*|footnotes|endnotes|comments)\.xml', n):
            continue
        try:
            txt = d.text(n)
        except ToolError:
            continue
        dp = dup_report(x.upper() for x in re.findall(r'w14:paraId="([0-9A-Fa-f]{8})"', txt))
        if dp:
            (problems if n == d.main else avisos).append('%s: w14:paraId duplicado (%d): %s' % (n, len(dp), ', '.join(dp[:4])))
        dt = dup_report(x.upper() for x in re.findall(r'w14:textId="([0-9A-Fa-f]{8})"', txt) if x.upper() != '77777777')
        if dt:
            avisos.append('%s: w14:textId repetido (%d)' % (n, len(dt)))
        dd = dup_report(re.findall(r'<wp:docPr\b[^>]*?\bid="(\d+)"', txt))
        if dd:
            problems.append('%s: wp:docPr id duplicado (%d): %s' % (n, len(dd), ', '.join(dd[:6])))
        if n == d.main:
            bm = dup_report(re.findall(r'<w:bookmarkStart\b[^>]*?\bw:id="(\d+)"', txt))
            if bm:
                avisos.append('%s: bookmarkStart w:id repetido (%d)' % (n, len(bm)))
    # conteos
    cnt = ''
    try:
        doc = d.doc
        tree_ok = True
        try:
            body = d.body
            top = sum(1 for k in body.kids if k.name == 'w:tbl')
        except ToolError as e:
            problems.append(str(e))
            top = 0
        cnt = 'tablas=%d (total %d) filas=%d celdas=%d párrafos=%d secciones=%d imágenes=%d' % (
            top, len(re.findall(r'<w:tbl[\s>]', doc)), len(re.findall(r'<w:tr[\s>]', doc)),
            len(re.findall(r'<w:tc[\s>]', doc)), len(re.findall(r'<w:p[\s>/]', doc)),
            len(re.findall(r'<w:sectPr[\s>/]', doc)),
            len(re.findall(r'<a:blip\b', doc)) + len(re.findall(r'<v:imagedata\b', doc)))
        # estructura tbl/tr/tc coherente
        if len(re.findall(r'<w:tc[\s>]', doc)) != len(re.findall(r'</w:tc>', doc)):
            problems.append('w:tc sin cerrar o vacíos inconsistentes')
    except ToolError as e:
        problems.append(str(e))
    if problems:
        print('PROBLEMAS (%d)' % len(problems))
        for p in problems:
            print('- ' + p)
    else:
        print('OK' + (' (con %d avisos)' % len(avisos) if avisos else ''))
    for w in avisos:
        print('AVISO ' + w)
    if cnt:
        print('conteos: ' + cnt)
    return 1 if problems else 0


# ----------------------------------------------------------------- comparar
def table_sigs(d):
    text = d.doc
    sigs = {}

    def rec(tbl, path):
        rows = kids_named(tbl, 'w:tr')
        rsig = []
        for r, tr in enumerate(rows):
            cs = []
            for c, tc in enumerate(kids_named(tr, 'w:tc')):
                span, vm = tc_props(tc, text)
                cs.append((span, vm))
                for n, t2 in enumerate(cell_tbls(tc)):
                    rec(t2, '%sF%dC%d.T%d' % (path, r, c, n))
            rsig.append(cs)
        sigs[path] = (grid_widths(tbl, text), rsig)
    for t, (_, tbl) in enumerate(d.table_index()):
        rec(tbl, 'T%d' % t)
    return sigs


def counts(d):
    doc = d.doc
    return {
        'tablas': len(re.findall(r'<w:tbl[\s>]', doc)),
        'filas': len(re.findall(r'<w:tr[\s>]', doc)),
        'celdas': len(re.findall(r'<w:tc[\s>]', doc)),
        'imágenes': len(re.findall(r'<a:blip\b', doc)) + len(re.findall(r'<v:imagedata\b', doc)),
        'secciones': len(re.findall(r'<w:sectPr[\s>/]', doc)),
    }


def cmd_comparar(a):
    A, B = Docx(a.a), Docx(a.b)
    diffs = []
    ca, cb = counts(A), counts(B)
    for k in ca:
        if ca[k] != cb[k]:
            diffs.append('%s: %d -> %d' % (k, ca[k], cb[k]))
    sa, sb = table_sigs(A), table_sigs(B)
    for p in sorted(set(sa) | set(sb), key=lambda x: [int(n) for n in re.findall(r'\d+', x)]):
        if p not in sa:
            diffs.append('%s: solo en b' % p)
            continue
        if p not in sb:
            diffs.append('%s: solo en a' % p)
            continue
        ga, ra = sa[p]
        gb, rb = sb[p]
        if ga != gb:
            diffs.append('%s tblGrid: %s -> %s' % (p, ga, gb))
        if len(ra) != len(rb):
            diffs.append('%s filas: %d -> %d' % (p, len(ra), len(rb)))
        for r in range(min(len(ra), len(rb))):
            if ra[r] != rb[r]:
                if len(ra[r]) != len(rb[r]):
                    diffs.append('%sF%d celdas: %d -> %d' % (p, r, len(ra[r]), len(rb[r])))
                else:
                    for c, (x, y) in enumerate(zip(ra[r], rb[r])):
                        if x != y:
                            diffs.append('%sF%dC%d span/vmerge: %s -> %s' % (p, r, c, x, y))
    ra_, rb_ = root_decls(A.doc)[0], root_decls(B.doc)[0]
    if ra_ != rb_:
        diffs.append('declaraciones de namespace de la raíz difieren (%d vs %d)' % (len(ra_), len(rb_)))
    ia = re.search(r'mc:Ignorable="[^"]*"', A.doc[:30000])
    ib = re.search(r'mc:Ignorable="[^"]*"', B.doc[:30000])
    if (ia.group(0) if ia else None) != (ib.group(0) if ib else None):
        diffs.append('mc:Ignorable difiere')
    if diffs:
        print('DIFERENCIAS (%d)' % len(diffs))
        for x in diffs[:200]:
            print('- ' + x)
        return 1
    print('SIN DIFERENCIAS estructurales: ' + ' '.join('%s=%d' % kv for kv in ca.items()))
    return 0


# --------------------------------------------------------------------- CLI
def build_parser():
    ap = argparse.ArgumentParser(prog='docx_tool.py', description='Leer y editar DOCX con pocos tokens (solo biblioteca estándar).')
    sub = ap.add_subparsers(dest='cmd', required=True)
    com = argparse.ArgumentParser(add_help=False)
    com.add_argument('--ancho', type=int, default=60, help='caracteres máximos por texto (60)')
    wr = argparse.ArgumentParser(add_help=False)
    wr.add_argument('-o', '--salida', help='archivo .docx de salida')
    wr.add_argument('--sobrescribir', action='store_true', help='permite sobrescribir el archivo de entrada')

    def add(name, helptxt, *parents):
        sp = sub.add_parser(name, help=helptxt, parents=[com] + list(parents))
        return sp
    p = add('info', 'resumen del documento')
    p.add_argument('archivo')
    p.set_defaults(fn=cmd_info)
    p = add('mapa', 'hijos del body con índice')
    p.add_argument('archivo')
    p.add_argument('--desde', type=to_index)
    p.add_argument('--hasta', type=to_index)
    p.set_defaults(fn=cmd_mapa)
    p = add('tablas', 'celdas de tablas')
    p.add_argument('archivo')
    p.add_argument('--tabla')
    p.set_defaults(fn=cmd_tablas)
    p = add('texto', 'texto completo de un rango del body')
    p.add_argument('archivo')
    p.add_argument('--desde', type=to_index, required=True)
    p.add_argument('--hasta', type=to_index)
    p.set_defaults(fn=cmd_texto)
    p = add('buscar', 'buscar texto')
    p.add_argument('archivo')
    p.add_argument('patron')
    p.add_argument('--regex', action='store_true')
    p.add_argument('--sensible', action='store_true', help='distinguir mayúsculas')
    p.add_argument('--max', type=int, default=0, help='máximo de líneas')
    p.set_defaults(fn=cmd_buscar)
    p = add('editar-celdas', 'editar celdas por coordenada desde JSON', wr)
    p.add_argument('archivo')
    p.add_argument('cambios')
    p.set_defaults(fn=cmd_editar_celdas)
    p = add('reemplazar', 'reemplazar texto dentro de runs', wr)
    p.add_argument('archivo')
    p.add_argument('viejo')
    p.add_argument('nuevo')
    p.add_argument('--max', type=int, default=0)
    p.add_argument('--desde', type=to_index)
    p.add_argument('--hasta', type=to_index)
    p.set_defaults(fn=cmd_reemplazar)
    p = add('extraer', 'guardar XML crudo de hijos del body')
    p.add_argument('archivo')
    p.add_argument('fragmento')
    p.add_argument('--desde', type=to_index, required=True)
    p.add_argument('--hasta', type=to_index)
    p.set_defaults(fn=cmd_extraer)
    p = add('insertar', 'insertar un fragmento XML antes de un índice', wr)
    p.add_argument('archivo')
    p.add_argument('fragmento')
    p.add_argument('--antes', type=to_index, required=True)
    p.set_defaults(fn=cmd_insertar)
    p = add('copiar', 'copiar hijos del body de otro DOCX (con imágenes)', wr)
    p.add_argument('archivo', help='DOCX destino')
    p.add_argument('origen', help='DOCX origen')
    p.add_argument('--desde', type=to_index, required=True)
    p.add_argument('--hasta', type=to_index)
    p.add_argument('--antes', type=to_index, required=True)
    p.set_defaults(fn=cmd_copiar)
    p = add('borrar', 'borrar hijos del body', wr)
    p.add_argument('archivo')
    p.add_argument('--desde', type=to_index, required=True)
    p.add_argument('--hasta', type=to_index)
    p.add_argument('--limpiar-media', action='store_true', help='elimina relaciones y partes que queden huérfanas')
    p.set_defaults(fn=cmd_borrar)
    p = add('verificar', 'integridad del paquete')
    p.add_argument('archivo')
    p.set_defaults(fn=cmd_verificar)
    p = add('comparar', 'diferencias estructurales entre dos DOCX')
    p.add_argument('a')
    p.add_argument('b')
    p.set_defaults(fn=cmd_comparar)
    return ap


def main(argv=None):
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding='utf-8')
        except (AttributeError, ValueError):
            pass
    args = build_parser().parse_args(argv)
    try:
        return args.fn(args) or 0
    except ToolError as e:
        print('ERROR: %s' % e, file=sys.stderr)
        return 2
    except BrokenPipeError:
        return 0


if __name__ == '__main__':
    sys.exit(main())

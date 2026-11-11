# -*- coding: utf-8 -*-
"""Membangun proposal DOCX dari template resmi WIA. Jalankan dengan python venv yang memiliki python-docx dan Pillow."""
import copy, re, sys, importlib.util
from pathlib import Path
import docx
from docx.shared import Cm, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from PIL import Image

ROOT = Path("/Users/macbookpro/Projects/auditra-main")
WP = ROOT / "deliverables" / "wia-proposal"
TEMPLATE = ROOT / "[WIA] Template Proposal .docx"
OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else WP / "working" / "proposal_working.docx"

spec = importlib.util.spec_from_file_location("content", WP / "working" / "content.py")
C = importlib.util.module_from_spec(spec); spec.loader.exec_module(C)

FONT = "Plus Jakarta Sans"
doc = docx.Document(str(TEMPLATE))
body = doc.element.body
els = list(body)
sect = body.find(qn("w:sectPr"))

# ---------- bahan klon dari template ----------
H1_UNNUM = copy.deepcopy(els[26])
H1_BAB = copy.deepcopy(els[55])
H2 = copy.deepcopy(els[56])
for tpl in (H1_UNNUM, H1_BAB, H2):
    for bm in tpl.findall(qn("w:bookmarkStart")) + tpl.findall(qn("w:bookmarkEnd")):
        tpl.remove(bm)


def set_runs_text(p, texts):
    runs = p.findall(qn("w:r"))
    k = 0
    for r in runs:
        ts = r.findall(qn("w:t"))
        if not ts:
            continue
        for t in ts:
            t.text = texts[k] if k < len(texts) else ""
            t.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
            k += 1


def page_break_before(p):
    ppr = p.find(qn("w:pPr"))
    pb = OxmlElement("w:pageBreakBefore")
    ppr.insert(1 if ppr.find(qn("w:pStyle")) is not None else 0, pb)


# ---------- sampul ----------
def cover_set(idx, texts):
    set_runs_text(els[idx], texts)

cover_set(4, [C.TITLE])
# paragraf 5: tiga run teks pada template
r5 = [t.text for t in els[5].iter(qn("w:t"))]
cover_set(5, ["Disusun Oleh ", C.TEAM, " :"] if len(r5) >= 3 else ["Disusun Oleh " + C.TEAM + " :"])
for i, m in enumerate(C.MEMBERS):
    cover_set(6 + i, [m])
# pastikan seluruh sisa teks pada paragraf sampul bersih
for i in (4, 5, 6, 7, 8):
    txt = "".join(t.text or "" for t in els[i].iter(qn("w:t")))
    assert "[" not in txt and "Nama" not in txt, (i, txt)

# ---------- daftar isi: pertahankan sdt, hapus sisa paragraf kosong ----------
page_break_before(els[12])
for i in list(range(15, 26)):
    body.remove(els[i])
# hapus semuanya dari indeks 26 hingga sebelum sectPr
for e in els[26:]:
    if e is not sect:
        body.remove(e)


def add(el):
    sect.addprevious(el)
    return el


# ---------- helper pemformatan ----------
def font_run(run, size=10, bold=False, italic=False, color=None):
    run.font.name = FONT
    rpr = run._r.get_or_add_rPr()
    rf = rpr.find(qn("w:rFonts"))
    if rf is None:
        rf = OxmlElement("w:rFonts"); rpr.insert(0, rf)
    for a in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
        rf.set(qn(a), FONT)
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.italic = italic
    if color:
        run.font.color.rgb = RGBColor.from_string(color)


TOK = re.compile(r"(\*\*.+?\*\*|\*.+?\*)")


def add_inline(par, text, size=10, bold=False, italic=False):
    for part in TOK.split(text):
        if not part:
            continue
        b, i = bold, italic
        if part.startswith("**") and part.endswith("**"):
            part, b = part[2:-2], True
        elif part.startswith("*") and part.endswith("*") and len(part) > 2:
            part, i = part[1:-1], True
        r = par.add_run(part)
        font_run(r, size, b, i)


def new_par(align=WD_ALIGN_PARAGRAPH.JUSTIFY, before=0, after=6, line=1.5, keep_next=False, first_indent=None, left=None, hanging=None):
    p = doc.add_paragraph()
    sect.addprevious(p._p)
    pf = p.paragraph_format
    pf.alignment = align
    pf.space_before = Pt(before); pf.space_after = Pt(after)
    pf.line_spacing = line
    pf.keep_with_next = keep_next
    pf.widow_control = True
    if first_indent is not None:
        pf.first_line_indent = Cm(first_indent)
    if left is not None:
        pf.left_indent = Cm(left)
    if hanging is not None:
        pf.first_line_indent = Cm(-hanging)
    return p


# ---------- penomoran otomatis ----------
FIGN, TABN = {}, {}
nf = nt = 0
for section in (C.BAB1, C.BAB2, C.BAB3, C.BAB4, C.LAMPIRAN):
    for e in section:
        if e[0] in ("fig", "figrow"):
            nf += 1; FIGN[e[1]] = nf
        elif e[0] == "tab":
            nt += 1; TABN[e[1]] = nt


def resolve(s):
    s = re.sub(r"\{fig:(\w+)\}", lambda m: f"Gambar {FIGN[m.group(1)]}", s)
    s = re.sub(r"\{tab:(\w+)\}", lambda m: f"Tabel {TABN[m.group(1)]}", s)
    return s


def set_cell_borders(tbl):
    """Sisipkan tblBorders dan tblCellMar sesuai urutan skema OOXML."""
    tblPr = tbl._tbl.tblPr
    look = tblPr.find(qn("w:tblLook"))
    lay = tblPr.find(qn("w:tblLayout"))
    bd = OxmlElement("w:tblBorders")
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        el = OxmlElement(f"w:{edge}")
        el.set(qn("w:val"), "single"); el.set(qn("w:sz"), "4"); el.set(qn("w:space"), "0"); el.set(qn("w:color"), "9AA5B8")
        bd.append(el)
    mar = OxmlElement("w:tblCellMar")
    for edge, w in (("top", 40), ("left", 80), ("bottom", 40), ("right", 80)):
        el = OxmlElement(f"w:{edge}"); el.set(qn("w:w"), str(w)); el.set(qn("w:type"), "dxa"); mar.append(el)
    if lay is not None:
        lay.addprevious(bd); lay.addnext(mar)
    else:
        look.addprevious(bd); look.addprevious(mar)


def shade(cell, fill):
    tcPr = cell._tc.get_or_add_tcPr()
    sh = OxmlElement("w:shd"); sh.set(qn("w:val"), "clear"); sh.set(qn("w:color"), "auto"); sh.set(qn("w:fill"), fill)
    tcPr.append(sh)


def make_table(header, rows, widths, shade_rows=()):
    t = doc.add_table(rows=1 + len(rows), cols=len(header))
    sect.addprevious(t._tbl)
    t.autofit = False
    t.alignment = 1
    set_cell_borders(t)
    allrows = [header] + rows
    for ri, row in enumerate(allrows):
        tr = t.rows[ri]._tr
        trPr = tr.get_or_add_trPr()
        cs = OxmlElement("w:cantSplit"); trPr.append(cs)
        if ri == 0:
            th = OxmlElement("w:tblHeader"); trPr.append(th)
        for ci, val in enumerate(row):
            cell = t.cell(ri, ci)
            cell.width = Cm(widths[ci])
            hdr = ri == 0 or ri in shade_rows
            if hdr:
                shade(cell, "DCE6F2")
            p = cell.paragraphs[0]
            p.paragraph_format.space_after = Pt(0); p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.line_spacing = 1.1
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            add_inline(p, resolve(val), size=8.5, bold=hdr)
    return t


def add_caption_label(par, label, num, text, size=9):
    r = par.add_run(f"{label} {num}. "); font_run(r, size, True, False)
    add_inline(par, resolve(text), size=size)


def add_source(text, after=10):
    p = new_par(WD_ALIGN_PARAGRAPH.CENTER, 0, after, 1.0)
    add_inline(p, "Sumber: " + text.rstrip(".") + ".", size=8, italic=True)
    return p


def add_picture_par(path, width_cm):
    full = WP / path
    p = new_par(WD_ALIGN_PARAGRAPH.CENTER, 4, 2, 1.0, keep_next=True)
    p.add_run().add_picture(str(full), width=Cm(width_cm))
    return p


def render(elements):
    for e in elements:
        k = e[0]
        if k == "h2":
            h = copy.deepcopy(H2); set_runs_text(h, [e[1]]); add(h)
        elif k == "h3":
            p = new_par(WD_ALIGN_PARAGRAPH.LEFT, 6, 3, 1.15, keep_next=True)
            add_inline(p, e[1], size=10, bold=True)
        elif k == "p":
            p = new_par()
            add_inline(p, resolve(e[1]), size=10)
        elif k == "fig":
            _, key, path, w, cap, src = e
            add_picture_par(path, w)
            p = new_par(WD_ALIGN_PARAGRAPH.CENTER, 0, 2, 1.0)
            add_caption_label(p, "Gambar", FIGN[key], cap)
            add_source(src)
        elif k == "figrow":
            _, key, paths, w, cap, src = e
            t = doc.add_table(rows=1, cols=len(paths)); sect.addprevious(t._tbl); t.alignment = 1; t.autofit = False
            for i, pth in enumerate(paths):
                c = t.cell(0, i); c.width = Cm(w + 0.3)
                pp = c.paragraphs[0]; pp.alignment = WD_ALIGN_PARAGRAPH.CENTER
                pp.paragraph_format.keep_with_next = True
                pp.add_run().add_picture(str(WP / pth), width=Cm(w))
            p = new_par(WD_ALIGN_PARAGRAPH.CENTER, 2, 2, 1.0)
            add_caption_label(p, "Gambar", FIGN[key], cap)
            add_source(src)
        elif k == "tab":
            _, key, cap, header, rows, widths, src = e
            p = new_par(WD_ALIGN_PARAGRAPH.CENTER, 6, 3, 1.0, keep_next=True)
            add_caption_label(p, "Tabel", TABN[key], cap)
            shade_rows = [i + 1 for i, r in enumerate(rows) if r[0].startswith("Peluang (")]
            make_table(header, rows, widths, shade_rows)
            add_source(src, after=8).paragraph_format.space_before = Pt(3)


def bab_heading(num, title, bm=None):
    h = copy.deepcopy(H1_BAB)
    set_runs_text(h, [f"BAB {num}", title])
    page_break_before(h); add(h)


def plain_heading(title):
    h = copy.deepcopy(H1_UNNUM); set_runs_text(h, [title]); page_break_before(h); add(h)


# ---------- KATA PENGANTAR ----------
plain_heading("KATA PENGANTAR")
for e in C.KATA_PENGANTAR:
    p = new_par(); add_inline(p, e[1], size=10)
for txt, bold, before in (("Surabaya, 11 November 2026", False, 8), ("Ketua Tim", False, 0)):
    p = new_par(WD_ALIGN_PARAGRAPH.RIGHT, before, 0, 1.15); add_inline(p, txt, size=10)
for _ in range(2):
    new_par(WD_ALIGN_PARAGRAPH.RIGHT, 0, 0, 1.15)
p = new_par(WD_ALIGN_PARAGRAPH.RIGHT, 0, 0, 1.15); add_inline(p, "Galih Aji Pangestu", size=10, bold=True)

# ---------- BAB ----------
bab_heading("I", "PENDAHULUAN"); render(C.BAB1)
bab_heading("II", "RANCANGAN SISTEM"); render(C.BAB2)
bab_heading("III", "HASIL DAN PEMBAHASAN"); render(C.BAB3)
bab_heading("IV", "PENUTUP"); render(C.BAB4)
plain_heading("LAMPIRAN"); render(C.LAMPIRAN)
plain_heading("DAFTAR PUSTAKA")
for r in C.REFS:
    p = new_par(WD_ALIGN_PARAGRAPH.LEFT, 0, 6, 1.15, left=1.0, hanging=1.0)
    add_inline(p, r, size=10)

doc.save(str(OUT))
print("tersimpan", OUT, "gambar", nf, "tabel", nt)

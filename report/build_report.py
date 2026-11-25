"""Build the full project report from report_content.md on top of the course Word template.

    python report/build_report.py           -> report/out/FullReport.docx
    then report/lo_finalize.py (LibreOffice) refreshes the TOC / lists and exports the PDF.

The template's cover page, page border, header/footer, styles and caption style are kept;
everything after the "LIST OF FIGURES, TABLES" page is replaced by our content.
"""
import copy
import re
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK, WD_COLOR_INDEX
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor

ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / "report" / "template" / "Template_Do_An_Mon_Hoc_EN.docx"
CONTENT = ROOT / "report" / "report_content.md"
FIG = ROOT / "outputs" / "figures"
OUT = ROOT / "report" / "out"
EQ_DIR = OUT / "equations"

COVER = {
    "faculty": "FACULTY OF INFORMATION SYSTEMS",
    "topic": "STATISTICAL AND MACHINE LEARNING ANALYTICS FOR PATIENT VALUE, "
             "SATISFACTION AND RETENTION IN A PRIVATE OUTPATIENT CLINIC",
    "class_code": "STAT3013.R11.CTTT",
    "course_name": "Statistical Analysis (Phân tích thống kê)",
    "instructor": "Nguyen Minh Nhut",
    "group": "10",                                # TODO: confirm with class monitor
    "member": ("Ho Van Hieu", "19521497", "Leader"),
    "duration": "05/10/2026 - 28/11/2026",        # TODO: confirm dates
}
HIGHLIGHT = {"duration", "group"}  # values still to be confirmed


# ----------------------------------------------------------------- helpers
def set_runs(paragraph, parts):
    """Replace a paragraph's runs by (text, bold, highlight) parts, keeping paragraph style."""
    for r in list(paragraph.runs):
        r._r.getparent().remove(r._r)
    for text, bold, hl in parts:
        run = paragraph.add_run(text)
        run.bold = bold
        if hl:
            run.font.highlight_color = WD_COLOR_INDEX.YELLOW


def add_inline(paragraph, text, size=None, italic=False):
    """Add text with **bold**, *italic* and `code` markup as runs."""
    for tok in re.split(r"(\*\*[^*]+\*\*|\*[^*]+\*|`[^`]+`)", text):
        if not tok:
            continue
        if tok.startswith("**"):
            run = paragraph.add_run(tok[2:-2]); run.bold = True
        elif tok.startswith("*"):
            run = paragraph.add_run(tok[1:-1]); run.italic = True
        elif tok.startswith("`"):
            run = paragraph.add_run(tok[1:-1]); run.font.name = "Courier New"
            run.font.size = Pt(11)
        else:
            run = paragraph.add_run(tok)
        if italic:
            run.italic = True
        if size and not tok.startswith("`"):
            run.font.size = Pt(size)


def para_spacing(p, before=0, after=6, line=None):
    pf = p.paragraph_format
    pf.space_before, pf.space_after = Pt(before), Pt(after)
    if line:
        pf.line_spacing = line


def page_break(doc):
    doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)


def add_field(paragraph, instr, result):
    """Insert a Word field (e.g. SEQ, TOC) with a cached result."""
    def r(child):
        run = OxmlElement("w:r"); run.append(child); paragraph._p.append(run); return run
    b = OxmlElement("w:fldChar"); b.set(qn("w:fldCharType"), "begin"); r(b)
    it = OxmlElement("w:instrText"); it.set(qn("xml:space"), "preserve"); it.text = f" {instr} "; r(it)
    s = OxmlElement("w:fldChar"); s.set(qn("w:fldCharType"), "separate"); r(s)
    t = OxmlElement("w:t"); t.text = result; r(t)
    e = OxmlElement("w:fldChar"); e.set(qn("w:fldCharType"), "end"); r(e)


def caption(doc, kind, num, text):
    """Caption in the template's format: 'Figure 1. Text.' using SEQ Hình / SEQ Bảng."""
    p = doc.add_paragraph(style="Caption")
    p.add_run("Figure " if kind == "fig" else "Table ")
    add_field(p, "SEQ Hình \\* ARABIC" if kind == "fig" else "SEQ Bảng \\* ARABIC", str(num))
    p.add_run(". " + text.rstrip("."))
    p.add_run(".")
    return p


BULLET_NUM_ID = "90"


def add_bullet_numbering(doc):
    """Add a '•' bullet list definition (the template only defines numbered lists)."""
    numbering = doc.part.numbering_part.element
    absn = OxmlElement("w:abstractNum"); absn.set(qn("w:abstractNumId"), BULLET_NUM_ID)
    mlt = OxmlElement("w:multiLevelType"); mlt.set(qn("w:val"), "singleLevel"); absn.append(mlt)
    lvl = OxmlElement("w:lvl"); lvl.set(qn("w:ilvl"), "0")
    for tag, val in (("w:start", "1"), ("w:numFmt", "bullet"), ("w:lvlText", "\u2022"), ("w:lvlJc", "left")):
        e = OxmlElement(tag); e.set(qn("w:val"), val); lvl.append(e)
    ppr = OxmlElement("w:pPr"); ind = OxmlElement("w:ind")
    ind.set(qn("w:left"), "720"); ind.set(qn("w:hanging"), "360"); ppr.append(ind); lvl.append(ppr)
    rpr = OxmlElement("w:rPr"); rf = OxmlElement("w:rFonts")
    rf.set(qn("w:ascii"), "Times New Roman"); rf.set(qn("w:hAnsi"), "Times New Roman"); rpr.append(rf); lvl.append(rpr)
    absn.append(lvl)
    first_num = numbering.find(qn("w:num"))
    first_num.addprevious(absn)
    num = OxmlElement("w:num"); num.set(qn("w:numId"), BULLET_NUM_ID)
    an = OxmlElement("w:abstractNumId"); an.set(qn("w:val"), BULLET_NUM_ID); num.append(an)
    numbering.append(num)


def bullet(doc, text):
    p = doc.add_paragraph(style="List Paragraph")
    numpr = OxmlElement("w:numPr")
    il = OxmlElement("w:ilvl"); il.set(qn("w:val"), "0")
    ni = OxmlElement("w:numId"); ni.set(qn("w:val"), BULLET_NUM_ID)
    numpr.append(il); numpr.append(ni)
    p._p.get_or_add_pPr().append(numpr)
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    add_inline(p, text)
    para_spacing(p, after=3)


def equation(doc, latex, idx):
    EQ_DIR.mkdir(parents=True, exist_ok=True)
    path = EQ_DIR / f"eq{idx}.png"
    fig = plt.figure(figsize=(0.01, 0.01))
    fig.text(0, 0, f"${latex}$", fontsize=15, math_fontfamily="stix")
    fig.savefig(path, dpi=300, bbox_inches="tight", pad_inches=0.04, transparent=True)
    plt.close(fig)
    from PIL import Image
    w_px, _ = Image.open(path).size
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.add_run().add_picture(str(path), width=Inches(min(w_px / 300, 6.0)))
    para_spacing(p, before=2, after=6)


def code_block(doc, lines):
    p = doc.add_paragraph()
    pPr = p._p.get_or_add_pPr()
    shd = OxmlElement("w:shd"); shd.set(qn("w:val"), "clear"); shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), "F2F2F2"); pPr.append(shd)
    p.paragraph_format.left_indent = Inches(0.15)
    para_spacing(p, before=2, after=8, line=1.0)
    for k, line in enumerate(lines):
        run = p.add_run(line)
        run.font.name = "Courier New"; run.font.size = Pt(9)
        run._r.get_or_add_rPr().append(_rfonts("Courier New"))
        if k < len(lines) - 1:
            run.add_break()


def _rfonts(name):
    rf = OxmlElement("w:rFonts")
    for a in ("w:ascii", "w:hAnsi", "w:cs"):
        rf.set(qn(a), name)
    return rf


def table(doc, rows):
    ncol = max(len(r) for r in rows)
    t = doc.add_table(rows=len(rows), cols=ncol)
    t.style = "Table Grid"
    t.alignment = 1
    for i, row in enumerate(rows):
        for j in range(ncol):
            cell = t.cell(i, j)
            txt = row[j] if j < len(row) else ""
            p = cell.paragraphs[0]
            para_spacing(p, after=0, line=1.0)
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT if j == 0 else WD_ALIGN_PARAGRAPH.CENTER
            add_inline(p, txt, size=11)
            if i == 0:
                for r in p.runs:
                    r.bold = True
                shd = OxmlElement("w:shd"); shd.set(qn("w:val"), "clear"); shd.set(qn("w:fill"), "D9E2F3")
                cell._tc.get_or_add_tcPr().append(shd)
            cell.vertical_alignment = 1
    # column widths proportional to content length (page text width 6.27 in)
    lens = [max(min(len(r[j]) if j < len(r) else 0, 40) for r in rows) + 4 for j in range(ncol)]
    widths = [6.27 * l / sum(lens) for l in lens]
    t.autofit = False
    grid = t._tbl.tblGrid
    for j, (gc, w) in enumerate(zip(grid.findall(qn("w:gridCol")), widths)):
        gc.set(qn("w:w"), str(int(w * 1440)))
        for cell in t.columns[j].cells:
            cell.width = Inches(w)
    # keep rows whole and keep the table together with its caption
    for row in t.rows:
        trPr = row._tr.get_or_add_trPr()
        cs = OxmlElement("w:cantSplit"); cs.set(qn("w:val"), "true"); trPr.append(cs)
        if len(rows) <= 15:
            for cell in row.cells:
                for p in cell.paragraphs:
                    p.paragraph_format.keep_with_next = True
    # repeat header row on page breaks
    trPr = t.rows[0]._tr.get_or_add_trPr()
    th = OxmlElement("w:tblHeader"); th.set(qn("w:val"), "true"); trPr.append(th)
    return t


# ----------------------------------------------------------------- build
def edit_cover(doc):
    P = doc.paragraphs
    c = COVER
    set_runs(P[1], [(c["faculty"], True, False)])
    set_runs(P[6], [("TOPIC: " + c["topic"], None, False)])
    set_runs(P[10], [("Course: ", True, False), (c["class_code"] + " - ", None, False),
                     (c["course_name"], None, "course_name" in HIGHLIGHT)])
    set_runs(P[11], [("Instructor: ", True, False), (c["instructor"], None, "instructor" in HIGHLIGHT)])
    set_runs(P[12], [("Group ", True, False), (c["group"], True, "group" in HIGHLIGHT), (":", True, False)])
    name, sid, role = c["member"]
    set_runs(P[13], [(name, None, False), ("\t", None, False), (sid, None, False),
                     ("\t", None, False), ("\t", None, False), (role, None, False)])
    for k in (15, 14):
        P[k]._p.getparent().remove(P[k]._p)
    P = doc.paragraphs
    set_runs(P[14], [("Duration: ", True, False), (c["duration"], None, "duration" in HIGHLIGHT)])

    # Put the cover in its own section: the template's "border on first page only" setting is
    # ignored by LibreOffice/Pages, so the border lives in section 1 and section 2 has none.
    brk = P[15]
    for r in list(brk.runs):
        r._r.getparent().remove(r._r)
    final = doc.element.body.find(qn("w:sectPr"))
    cover_sect = copy.deepcopy(final)
    brk._p.get_or_add_pPr().append(cover_sect)
    for tag in ("w:pgBorders", "w:titlePg", "w:pgNumType"):
        el = final.find(qn(tag))
        if el is not None:
            final.remove(el)

    for p in doc.sections[0].header.paragraphs:
        if "Course name" in p.text:
            set_runs(p, [(f"Project Report for Statistical Analysis ({c['class_code']})", None, False), ("\t", None, False),
                         (f"Group {c['group']}", None, False)])


def trim_body(doc):
    """Keep cover + TOC + list-of-figures page; drop the template's sample content."""
    body = doc.element.body
    paras = doc.paragraphs
    lof = next(i for i, p in enumerate(paras) if p.text.strip() == "LIST OF FIGURES, TABLES")
    abstract = next(i for i, p in enumerate(paras) if p.text.strip() == "ABSTRACT")
    # replace the template's note on the list page by a list-of-tables field
    note = next(p for p in paras[lof:abstract] if p.text.startswith("Note:"))
    for r in list(note.runs):
        if not r._r.findall(qn("w:br")):
            r._r.getparent().remove(r._r)
    tbl_list = copy.deepcopy(note._p)
    note._p.addprevious(tbl_list)
    from docx.text.paragraph import Paragraph
    tp = Paragraph(tbl_list, note._parent)
    for r in list(tp.runs):
        r._r.getparent().remove(r._r)
    tp.style = doc.styles["table of figures"]
    add_field(tp, 'TOC \\h \\z \\c "Bảng"', "(list of tables – update field)")
    # remove everything from the ABSTRACT heading to the end (keep final sectPr)
    start = paras[abstract]._p
    el = start
    while el is not None:
        nxt = el.getnext()
        if el.tag != qn("w:sectPr"):
            body.remove(el)
        el = nxt


def build():
    doc = Document(TEMPLATE)
    edit_cover(doc)
    trim_body(doc)
    add_bullet_numbering(doc)

    lines = re.sub(r"<!--.*?-->", "", CONTENT.read_text(encoding="utf-8"), flags=re.S).splitlines()
    fig_n = tab_n = eq_n = ref_n = 0
    first_h1 = True
    i = 0
    while i < len(lines):
        line = lines[i].rstrip()
        if not line.strip():
            i += 1; continue
        if line.startswith("# "):
            h = doc.add_paragraph(line[2:].strip(), style="Heading 1")
            h.paragraph_format.page_break_before = not first_h1
            first_h1 = False
        elif line.startswith("## "):
            doc.add_paragraph(line[3:].strip(), style="Heading 2")
        elif line.startswith("### "):
            doc.add_paragraph(line[4:].strip(), style="Heading 3")
        elif line.startswith("- "):
            bullet(doc, line[2:])
        elif line.startswith("$$"):
            eq_n += 1
            equation(doc, line.strip("$ ").strip(), eq_n)
        elif line.startswith("```"):
            block = []
            i += 1
            while not lines[i].startswith("```"):
                block.append(lines[i]); i += 1
            code_block(doc, block)
        elif line.startswith("!["):
            m = re.match(r"!\[(.*)\]\((.*?)\)(\{([\d.]+)\})?", line)
            fig_n += 1
            p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.keep_with_next = True
            para_spacing(p, before=6, after=2, line=1.0)
            p.add_run().add_picture(str(FIG / m.group(2)), width=Inches(float(m.group(4) or 6.0)))
            caption(doc, "fig", fig_n, m.group(1))
        elif line.startswith("TABLE:"):
            cap = line[6:].strip()
            rows = []
            i += 1
            while i < len(lines) and lines[i].startswith("|"):
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
                i += 1
            tab_n += 1
            table(doc, rows)
            caption(doc, "tab", tab_n, cap)
            continue
        elif line.startswith("REF:"):
            ref_n += 1
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            p.paragraph_format.left_indent = Inches(0.45)
            p.paragraph_format.first_line_indent = Inches(-0.45)
            para_spacing(p, after=4)
            p.add_run(f"[{ref_n}]\t")
            add_inline(p, line[4:].strip())
        else:
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            if line.startswith("<") and line.endswith(">"):
                r = p.add_run(line); r.font.highlight_color = WD_COLOR_INDEX.YELLOW
            else:
                add_inline(p, line)
        i += 1

    OUT.mkdir(parents=True, exist_ok=True)
    out = OUT / "FullReport.docx"
    doc.save(out)
    print(f"saved {out}  figures={fig_n} tables={tab_n} equations={eq_n} references={ref_n}")


if __name__ == "__main__":
    build()

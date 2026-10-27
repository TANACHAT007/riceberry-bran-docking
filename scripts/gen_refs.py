"""Reference list: every number in the abstract/poster traced to a source or to our own data file."""
import json
from pathlib import Path
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.shared import Cm, Pt

ROOT = Path(__file__).resolve().parent.parent
META = json.loads((ROOT / "meta.json").read_text())
S = json.loads((ROOT / "summary.json").read_text())
F = "TH Sarabun New"

STRUCTURES = [
    ("2QMJ", "Human intestinal maltase-glucoamylase, N-terminal catalytic subunit, with acarbose. 1.9 Å.",
     "Sim L, Quezada-Calvillo R, Sterchi EE, Nichols BL, Rose DR. J Mol Biol. 2008;375:782.",
     "https://www.rcsb.org/structure/2QMJ"),
    ("3BAJ", "Human pancreatic α-amylase with nitrate and acarbose. 2.1 Å.",
     "Maurus R, Begum A, Williams LK, Fredriksen JR, Zhang R, Withers SG. Biochemistry. 2008;47:3332.",
     "https://www.rcsb.org/structure/3BAJ"),
]
SOFTWARE = [
    ("AutoDock Vina 1.2.7", "Docking engine. Built from source on this machine.",
     "Eberhardt J, Santos-Martins D, Tillack AF, Forli S. J Chem Inf Model. 2021;61:3891. · Trott O, Olson AJ. J Comput Chem. 2010;31:455."),
    ("Meeko 0.8.0", "Receptor and ligand PDBQT preparation.", "Forli Lab, Scripps Research. https://github.com/forlilab/Meeko"),
    ("RDKit 2026.09.1", "3D embedding (ETKDG), MMFF94 optimisation, descriptors.", "https://www.rdkit.org"),
    ("PDBFixer / OpenMM", "Missing atoms and hydrogens added at pH 7.4.", "Eastman P, et al. PLoS Comput Biol. 2017;13:e1005659."),
    ("PubChem", "Source of all ligand structures (CIDs listed below).", "Kim S, et al. Nucleic Acids Res. 2023;51:D1373."),
]
LITERATURE = [
    ("Anthocyanins from pigmented rice inhibit both enzymes in vitro",
     "Akkarachiyasit S, Charoenlertkul P, Yibchok-anun S, Adisakwattana S. Int J Mol Sci. 2010;11:3387. "
     "Chulalongkorn University. Cyanidin-3-glucoside IC50 0.97 mM (intestinal sucrase) and 0.30 mM (pancreatic α-amylase); "
     "synergy with low-dose acarbose.",
     "https://pmc.ncbi.nlm.nih.gov/articles/PMC2956102/"),
    ("Acarbose causes gastrointestinal effects",
     "US prescribing information, placebo-controlled trials: flatulence reported in 74% of 1,255 acarbose-treated patients "
     "versus 29% of 999 on placebo; diarrhoea 31%, abdominal pain 19%.",
     "https://www.accessdata.fda.gov/drugsatfda_docs/label/2011/020482s023lbl.pdf"),
    ("Rice bran is a low-value, rapidly spoiling by-product",
     "Endogenous lipase hydrolyses the oil within hours of milling, so most bran goes to animal feed. "
     "Fat content ~18–21%. Reviews of rice bran stabilisation.",
     "https://pmc.ncbi.nlm.nih.gov/articles/PMC10462582/"),
    ("Riceberry is a cross of Hom Nil and Khao Dawk Mali 105",
     "Rice Science Center, Kasetsart University.",
     "https://dna.kps.ku.ac.th/"),
    ("Docking scores predict binding, not inhibitory potency",
     "Standard limitation of empirical scoring functions; typical Vina scoring error is of the order of 1–2 kcal/mol. "
     "Stated explicitly in the abstract and on the poster.",
     "Trott O, Olson AJ. J Comput Chem. 2010;31:455."),
]


def style(d):
    st = d.styles["Normal"]; st.font.name = F; st.font.size = Pt(15)
    st.element.rPr.rFonts.set(qn("w:cs"), F); st.element.rPr.rFonts.set(qn("w:eastAsia"), F)
    st.element.rPr.append(st.element.rPr.makeelement(qn("w:szCs"), {qn("w:val"): "30"}))
    for s in d.sections:
        s.left_margin = s.right_margin = Cm(2.2); s.top_margin = s.bottom_margin = Cm(2.0)


def h(d, t, size=18):
    p = d.add_paragraph(); r = p.add_run(t); r.bold = True; r.font.size = Pt(size); r.font.name = F
    r._element.rPr.rFonts.set(qn("w:cs"), F)
    p.paragraph_format.space_before = Pt(12); p.paragraph_format.space_after = Pt(4)


def item(d, lead, body, url=None):
    p = d.add_paragraph(); p.paragraph_format.left_indent = Cm(0.7)
    p.paragraph_format.first_line_indent = Cm(-0.7); p.paragraph_format.space_after = Pt(5)
    r = p.add_run(lead + "  "); r.bold = True
    p.add_run(body)
    if url:
        r = p.add_run("  " + url); r.italic = True


def table(d, rows, widths):
    t = d.add_table(rows=len(rows), cols=len(rows[0]))
    borders = t._tbl.tblPr.makeelement(qn("w:tblBorders"), {})
    for e in ("top", "left", "bottom", "right", "insideH", "insideV"):
        borders.append(borders.makeelement(qn(f"w:{e}"), {qn("w:val"): "single", qn("w:sz"): "4", qn("w:color"): "8A93A8"}))
    t._tbl.tblPr.append(borders)
    for i, row in enumerate(rows):
        for j, val in enumerate(row):
            c = t.cell(i, j); c.width = Cm(widths[j]); c.text = ""
            r = c.paragraphs[0].add_run(str(val)); r.font.size = Pt(14); r.bold = i == 0
            c.paragraphs[0].paragraph_format.space_after = Pt(1)
    d.add_paragraph()


def main():
    d = Document(ROOT / "templates" / "th.docx")
    for el in list(d.element.body):
        if el.tag != qn("w:sectPr"):
            d.element.body.remove(el)
    style(d)
    p = d.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("เอกสารอ้างอิงและที่มาของข้อมูลทุกตัวเลข"); r.bold = True; r.font.size = Pt(22)
    p = d.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("Riceberry bran docking study — sources and reproducibility"); r.italic = True

    h(d, "1. โครงสร้างโปรตีน (Protein Data Bank)")
    for pdb, desc, cite, url in STRUCTURES:
        item(d, pdb, desc + " " + cite, url)

    h(d, "2. ซอฟต์แวร์และเวอร์ชัน")
    for name, desc, cite in SOFTWARE:
        item(d, name, desc + " " + cite)

    h(d, "3. สารที่ใช้ทดสอบ — PubChem CID (ตรวจสอบย้อนได้ทุกตัว)")
    rows = [["สาร", "PubChem CID", "สูตรโมเลกุล"]]
    for n, info in META["ligands"].items():
        rows.append([n, info["cid"], info["formula"]])
    table(d, rows, [8.2, 3.4, 4.4])

    h(d, "4. งานวิจัยที่อ้างอิง")
    for lead, body, url in LITERATURE:
        item(d, lead + ".", body, url)

    h(d, "5. ตัวเลขที่เป็นผลการคำนวณของโครงงานนี้เอง")
    d.add_paragraph("ตัวเลขทุกค่าด้านล่างมาจากการคำนวณบนเครื่องของเราเอง ไม่ได้คัดลอกจากงานใด และรันซ้ำได้ด้วยสคริปต์ในโฟลเดอร์ scripts/")
    v = S["validation"]
    rows = [["ค่าที่รายงาน", "ค่า", "ไฟล์ที่เก็บผลดิบ"]]
    rows.append(["Redock RMSD ของอะคาร์โบสบน MGAM (3 seed)",
                 " / ".join(f"{r['rmsd']}" for r in v["MGAM"]["redock"]) + " Å", "redock.json"])
    rows.append(["สัดส่วนอะตอมอะคาร์โบสที่ซ้อนทับผลึก HPA ภายใน 2 Å",
                 f"{round(v['HPA']['xtal_overlap_2A'] * 100)}%", "summary.json"])
    for lig in ("cycloartenyl ferulate", "cyanidin-3-O-glucoside", "peonidin-3-O-glucoside", "acarbose"):
        r = next(x for x in S["rows"] if x["ligand"] == lig)
        rows.append([f"พลังงานการจับ {lig} (MGAM / HPA)",
                     f"{r['MGAM']['mean']:.2f} ± {r['MGAM']['sd']:.2f} / {r['HPA']['mean']:.2f} ± {r['HPA']['sd']:.2f} kcal/mol",
                     "dock_results.json, summary.json"])
    rows.append(["ค่า logP, MW, Lipinski, Veber ของทุกสาร", "ดูตารางในโปสเตอร์", "summary.json (คำนวณด้วย RDKit)"])
    table(d, rows, [7.0, 5.4, 3.6])

    h(d, "6. การทำซ้ำ (reproducibility)")
    for line in [
        "scripts/prep.py — ดาวน์โหลดและเตรียมโปรตีนกับสาร",
        "scripts/dock.py — docking 2 เอนไซม์ × 12 สาร × 3 seed = 72 รอบ",
        "scripts/redock.py — ตรวจสอบความถูกต้องด้วยการ re-dock อะคาร์โบสจากผลึก 3 รอบ",
        "scripts/analyze.py — สรุปผล ค่าเฉลี่ย ± SD กรดอะมิโนที่สัมผัส และสมบัติทางเคมี",
        "scripts/figures.py, build_poster.py, gen_docx.py — สร้างรูป โปสเตอร์ และบทคัดย่อ",
    ]:
        p = d.add_paragraph(); p.paragraph_format.left_indent = Cm(0.8); p.paragraph_format.space_after = Pt(2)
        p.add_run("•  " + line)

    h(d, "7. ข้อจำกัดที่ระบุไว้ในผลงาน")
    for line in [
        "ค่า docking เป็นการทำนายการจับ ไม่ใช่ค่าความแรงในการยับยั้ง (IC50) จึงไม่สรุปว่าสารใดยับยั้งได้แรงกว่ากัน",
        "ค่า SD ที่ต่ำบอกว่าโปรแกรมให้ผลซ้ำได้ ไม่ได้บอกว่าค่านั้นถูกต้อง",
        "Redock RMSD 2.04–2.06 Å อยู่ที่ขอบเกณฑ์ 2 Å ที่ใช้กันทั่วไป รายงานตามจริง",
        "ยังไม่มีการทดสอบในหลอดทดลอง และไม่มีการกล่าวอ้างสรรพคุณทางสุขภาพ",
    ]:
        p = d.add_paragraph(); p.paragraph_format.left_indent = Cm(0.8); p.paragraph_format.space_after = Pt(2)
        p.add_run("•  " + line)

    out = ROOT / "submission" / "References_and_Data_Sources.docx"; d.save(out); print(out)


if __name__ == "__main__":
    main()

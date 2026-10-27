"""Supplementary figures and full data table — the detail that does not fit on the poster."""
import json
from pathlib import Path

import numpy as np
from docx import Document
from docx.enum.section import WD_ORIENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.shared import Cm, Pt
from scipy import stats as st

ROOT = Path(__file__).resolve().parent.parent
S = json.loads((ROOT / "summary.json").read_text())
OCC = json.loads((ROOT / "site_occupancy.json").read_text())
A = json.loads((ROOT / "abstract.json").read_text())
FIG = ROOT / "figures"
F = "Arial"   # the supplementary is English-only; TH Sarabun New is kept for the abstract
CATALYTIC = {"MGAM": {"ASP443", "ASP542", "ASP203"}, "HPA": {"ASP197", "GLU233", "ASP300"}}
NAME = {"acarbose": "Acarbose (reference drug)", "cyanidin-3-O-glucoside": "Cyanidin-3-O-glucoside",
        "peonidin-3-O-glucoside": "Peonidin-3-O-glucoside", "protocatechuic acid": "Protocatechuic acid",
        "ferulic acid": "Ferulic acid", "p-coumaric acid": "p-Coumaric acid", "vanillic acid": "Vanillic acid",
        "cycloartenyl ferulate": "Cycloartenyl ferulate",
        "24-methylenecycloartanyl ferulate": "24-Methylenecycloartanyl ferulate",
        "gamma-tocotrienol": "γ-Tocotrienol", "alpha-tocopherol": "α-Tocopherol", "quercetin": "Quercetin"}


def style(d):
    stn = d.styles["Normal"]; stn.font.name = F; stn.font.size = Pt(15)
    stn.element.rPr.rFonts.set(qn("w:cs"), F); stn.element.rPr.rFonts.set(qn("w:eastAsia"), F)
    rf = stn.element.rPr.rFonts
    for a in ("asciiTheme", "hAnsiTheme", "eastAsiaTheme", "cstheme"):   # theme fonts would win over ours
        rf.attrib.pop(qn("w:" + a), None)
    rf.set(qn("w:cs"), F)
    for s in d.sections:
        s.orientation = WD_ORIENT.LANDSCAPE
        s.page_width, s.page_height = Cm(29.7), Cm(21.0)
        s.left_margin = s.right_margin = Cm(1.6); s.top_margin = s.bottom_margin = Cm(1.4)


def h(d, t, size=19, space=14):
    p = d.add_paragraph(); r = p.add_run(t); r.bold = True; r.font.size = Pt(size); r.font.name = F
    r._element.rPr.rFonts.set(qn("w:cs"), F)
    p.paragraph_format.space_before = Pt(space); p.paragraph_format.space_after = Pt(4)


def para(d, t, size=15, italic=False):
    p = d.add_paragraph(); r = p.add_run(t); r.font.size = Pt(size); r.italic = italic
    r.font.name = F; r._element.rPr.rFonts.set(qn("w:cs"), F)
    p.paragraph_format.space_after = Pt(4)
    return p


def table(d, rows, widths, size=12):
    t = d.add_table(rows=len(rows), cols=len(rows[0])); t.autofit = False
    b = t._tbl.tblPr.makeelement(qn("w:tblBorders"), {})
    for e in ("top", "left", "bottom", "right", "insideH", "insideV"):
        b.append(b.makeelement(qn(f"w:{e}"), {qn("w:val"): "single", qn("w:sz"): "4", qn("w:color"): "8A93A8"}))
    t._tbl.tblPr.append(b)
    for m in ("left", "right"):
        t._tbl.tblPr.append(t._tbl.tblPr.makeelement(qn(f"w:tblCellMar"), {}))
        break
    for i, row in enumerate(rows):
        for j, val in enumerate(row):
            c = t.cell(i, j); c.width = Cm(widths[j]); c.text = ""
            t.columns[j].width = Cm(widths[j])
            p = c.paragraphs[0]; p.paragraph_format.space_after = Pt(0)
            if j: p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            r = p.add_run(str(val)); r.font.size = Pt(size); r.bold = i == 0
            r.font.name = F; r._element.rPr.rFonts.set(qn("w:cs"), F)
    return t


def figure(d, path, width, caption):
    p = d.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.add_run().add_picture(str(path), width=Cm(width))
    p.paragraph_format.space_after = Pt(3)
    c = para(d, caption, size=13)
    c.alignment = WD_ALIGN_PARAGRAPH.LEFT


def main():
    d = Document(); style(d)
    p = d.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("Supplementary figures and full data"); r.bold = True; r.font.size = Pt(24)
    para(d, A["en"]["title"], size=15, italic=True).alignment = WD_ALIGN_PARAGRAPH.CENTER
    para(d, f"{A['corresponding_name']} · {A['en']['affiliations'][0]} · {A['email']}",
         size=14).alignment = WD_ALIGN_PARAGRAPH.CENTER

    # ---- Table S1 -------------------------------------------------------
    h(d, "Table S1  Every compound, both enzymes, every number behind the poster", space=10)
    hdr = ["Compound", "MW", "logP", "Atoms",
           "MGAM ΔG ± SD", "LE", "H-bonds (cat.)", "Site %",
           "HPA ΔG ± SD", "LE", "H-bonds (cat.)", "Site %"]
    rows = [hdr]
    for r_ in sorted(S["rows"], key=lambda x: x["MGAM"]["mean"] + x["HPA"]["mean"]):
        lig = r_["ligand"]; cells = [NAME[lig], f"{r_['MW']:.0f}", f"{r_['logP']:.2f}".replace("-", "\u2212"), r_["HA"]]
        for t in ("MGAM", "HPA"):
            cat = sum(1 for x in r_[t]["hbond_res"] if x in CATALYTIC[t])
            cells += [f"{r_[t]['mean']:.2f} ± {r_[t]['sd']:.2f}".replace("-", "−"),
                      f"{r_[t]['LE']:.3f}", f"{len(r_[t]['hbond_res'])} ({cat})",
                      f"{OCC[lig][t]['occupancy_2A'] * 100:.0f}"]
        rows.append(cells)
    table(d, rows, [4.4, 1.6, 1.6, 1.5, 2.9, 1.4, 2.2, 1.4, 2.9, 1.4, 2.2, 1.4], size=11)
    para(d, "ΔG = Vina binding affinity in kcal/mol, mean ± SD of three independent seeds (11, 22, 33). "
            "LE = ligand efficiency, −ΔG divided by the number of heavy atoms. H-bonds = residues within 3.5 Å of a "
            "donor/acceptor in the best pose, with the number of catalytic residues among them in brackets "
            "(MGAM: Asp203, Asp443, Asp542; HPA: Asp197, Glu233, Asp300). Footprint % = pose atoms lying within 2 Å "
            "of an atom of the crystallographic acarbose in the same structure. logP and MW from RDKit.", size=12)

    # ---- validation -----------------------------------------------------
    v = S["validation"]
    h(d, "Table S2  Protocol validation")
    rows = [["Check", "Result", "Interpretation"]]
    rows.append(["Re-docking crystal acarbose into MGAM (2QMJ), 3 seeds from a randomised start",
                 " / ".join(f"{x['rmsd']} Å ({x['affinity']} kcal/mol)" for x in v["MGAM"]["redock"]),
                 "At the 2 Å threshold usually quoted; reported as measured, not rounded down"])
    rows.append(["Crystal acarbose pose atoms recovered inside the HPA site (3BAJ)",
                 f"{v['HPA']['xtal_overlap_2A'] * 100:.0f}%",
                 "The search box covers the catalytic site of the crystal complex"])
    rows.append(["Reproducibility across seeds, all 12 compounds",
                 f"SD ≤ {max(max(r['MGAM']['sd'], r['HPA']['sd']) for r in S['rows']):.2f} kcal/mol",
                 "The engine is repeatable; this says nothing about accuracy"])
    table(d, rows, [8.6, 6.4, 9.6], size=12)

    d.add_page_break()

    # ---- Figure S1 ------------------------------------------------------
    h(d, "Figure S1  Predicted binding affinity of all twelve compounds on both enzymes", space=0)
    figure(d, FIG / "affinity.png", 17.0,
           "Mean ± SD of three seeds. Solid bars α-glucosidase (MGAM), hatched bars α-amylase (HPA). "
           "Dashed and dotted lines mark acarbose on each enzyme. Colours group the compounds: purple = anthocyanins, "
           "gold = γ-oryzanol esters, green = vitamin E forms, orange = quercetin, pink = acarbose.")

    d.add_page_break()
    h(d, "Figure S2  Binding per atom, and the size bias in the scores", space=0)
    figure(d, FIG / "efficiency_size.png", 26.0,
           "(A) Ligand efficiency. The small phenolic acids bind far more efficiently per atom than any of the large "
           "molecules, and both anthocyanins beat acarbose (dotted line). (B) Predicted affinity against molecular size, "
           "with the least-squares fit for each enzyme. Empirical scoring functions reward added atoms, so a raw ranking "
           "favours the largest molecules; this is why solubility and efficiency were scored alongside the raw ΔG.")
    lines = []
    ha = np.array([r["HA"] for r in S["rows"]], float)
    for t in ("MGAM", "HPA"):
        lr = st.linregress(ha, np.array([-r[t]["mean"] for r in S["rows"]]))
        lines.append([t, f"{lr.slope:.3f}", f"{lr.rvalue:.3f}", f"{lr.rvalue ** 2:.3f}", f"{lr.pvalue:.2g}"])
    table(d, [["Enzyme", "Slope (kcal/mol per heavy atom)", "Pearson r", "r²", "p"]] + lines,
          [4.6, 7.4, 3.6, 3.6, 3.6], size=12)

    d.add_page_break()
    h(d, "Figure S3  Which active-site residues each compound touches", space=0)
    figure(d, FIG / "fingerprint.png", 26.0,
           "Contacts ≤ 4 Å in pale blue, hydrogen bonds ≤ 3.5 Å in dark blue, catalytic residues labelled in pink. "
           "Compounds are ordered by predicted affinity. Both anthocyanins hydrogen-bond the catalytic acids of both "
           "enzymes (Asp443 and Asp542 on MGAM; Asp197, Glu233 and Asp300 on HPA), the same residues acarbose engages, "
           "whereas the γ-oryzanol esters and the vitamin E forms make mostly hydrophobic contacts around them.")

    d.add_page_break()
    h(d, "Figure S4  All candidates occupy the acarbose site", space=0)
    figure(d, FIG / "occupancy.png", 16.0,
           "Percentage of each pose's heavy atoms lying within 2 Å of the crystallographic acarbose. Every compound "
           "sits inside that footprint, so the poses are competitive-site binders rather than surface artefacts. "
           "Small molecules reach 100% simply because they fit entirely inside the larger drug's envelope.")

    d.add_page_break()
    h(d, "Supplementary methods", space=0)
    for t in [
        "Ligand efficiency. LE = −ΔG ÷ number of heavy atoms, using the mean ΔG of three seeds. It removes the part of "
        "the score that comes only from molecular size.",
        "Score–size regression. Ordinary least squares of −ΔG on heavy-atom count across all twelve compounds, "
        "run separately for each enzyme (scipy.stats.linregress). Reported as slope, Pearson r, r² and p.",
        "Footprint occupancy. The crystallographic acarbose was taken from the same PDB entry used as the receptor "
        "(residues AC1 + GLC in 2QMJ, ARE in 3BAJ). For each docked pose, the fraction of heavy atoms within 2 Å of "
        "any crystal acarbose heavy atom was counted. Centroid shift (in site_occupancy.json) is the distance between "
        "the pose centroid and the crystal ligand centroid.",
        "Contacts and hydrogen bonds. A residue counts as a contact if any heavy atom lies within 4 Å of the ligand, "
        "and as a hydrogen bond if a donor/acceptor pair lies within 3.5 Å, measured on the best-scoring pose.",
        "Everything in this document is produced by scripts/analyze.py, scripts/extra_analysis.py and "
        "scripts/fig_extra.py from the raw docking output in dock_results.json and poses/. No value was transcribed "
        "by hand.",
    ]:
        para(d, "•  " + t, size=14)

    h(d, "What these numbers cannot show")
    for t in [
        "Docking ranks predicted binding, not inhibitory potency (IC₅₀) or selectivity between the two enzymes.",
        "Differences smaller than about 1 kcal/mol lie inside the scoring error of the function.",
        "A low SD shows the search is repeatable, not that the score is correct.",
        "No in vitro assay was run in this work, and no health claim is made.",
    ]:
        para(d, "•  " + t, size=14)

    out = ROOT / "submission" / "Supplementary_Figures_and_Data.docx"
    d.save(out); print(out)


if __name__ == "__main__":
    main()

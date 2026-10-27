"""Inject docking summary + pocket/pose structures into the 3D web template."""
import json
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
S = json.loads((ROOT / "summary.json").read_text())
META = json.loads((ROOT / "meta.json").read_text())


def slug(s):
    return "".join(c if c.isalnum() else "_" for c in s).strip("_")


def pocket(tgt, r=14.0):
    c = np.array(META["targets"][tgt]["center"])
    lines = [l for l in open(ROOT / "rec" / f"{tgt}_H.pdb") if l.startswith("ATOM")]
    keep = set()
    for l in lines:
        if np.linalg.norm(np.array([float(l[30:38]), float(l[38:46]), float(l[46:54])]) - c) <= r:
            keep.add(int(l[22:26]))
    return "".join(l for l in lines if int(l[22:26]) in keep and l[76:78].strip() != "H")


web = {t: {"pocket": pocket(t), "xtal": (ROOT / "rec" / f"{t}_xtal_lig.pdb").read_text()} for t in META["targets"]}
web["poses"] = {t: {l: (ROOT / "poses" / f"{t}__{slug(l)}__best.mol").read_text() for l in META["ligands"]} for t in META["targets"]}
methods = [
    ["เอนไซม์", "Human ntMGAM (PDB 2QMJ, 1.9 Å) และ human pancreatic α-amylase (PDB 3BAJ, 2.1 Å) ทั้งคู่มี acarbose ในผลึก"],
    ["เตรียมโปรตีน", "PDBFixer: ลบน้ำ/ไอออน/ลิแกนด์ เติมอะตอมที่ขาด และไฮโดรเจนที่ pH 7.4 → Meeko PDBQT"],
    ["เตรียมสาร", "โครงสร้างจาก PubChem → RDKit ETKDG + MMFF94 → Meeko"],
    ["Docking", "AutoDock Vina 1.2, กล่องครอบตำแหน่ง acarbose ในผลึก (≥ 22 Å), exhaustiveness 16, 3 seed"],
    ["วิเคราะห์", "ค่าเฉลี่ย ± SD, ligand efficiency, กรดอะมิโนในระยะ 4 Å, Lipinski/Veber"],
]
data = {"rows": S["rows"], "validation": S["validation"], "web": web, "methods": methods}
html = (ROOT / "web" / "template.html").read_text().replace("/*DATA*/null", json.dumps(data, separators=(",", ":")))
(ROOT / "web" / "riceberry-docking.html").write_text(html)
print("web size KB", len(html) // 1024)

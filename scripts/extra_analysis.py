"""Extra quantitative analyses for the poster: active-site occupancy, ligand efficiency,
and the score-vs-size relationship. All derived from the docking output already in poses/."""
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
META = json.loads((ROOT / "meta.json").read_text())
S = json.loads((ROOT / "summary.json").read_text())
XTAL_RES = {"MGAM": ("AC1", "GLC"), "HPA": ("ARE",)}


def xtal_atoms(target):
    pdb = ROOT / "data" / f"{META['targets'][target]['pdb']}.pdb"
    out = []
    for line in pdb.read_text().splitlines():
        if line.startswith("HETATM") and line[17:20].strip() in XTAL_RES[target] and line[76:78].strip() != "H":
            out.append((float(line[30:38]), float(line[38:46]), float(line[46:54])))
    return out


def pose_atoms(path):
    out = []
    for line in path.read_text().splitlines():
        if line.startswith(("ATOM", "HETATM")):
            t = line[77:79].strip()
            if t and t[0] != "H":
                out.append((float(line[30:38]), float(line[38:46]), float(line[46:54])))
    return out


def d2(a, b):
    return (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2 + (a[2] - b[2]) ** 2


def centroid(pts):
    n = len(pts)
    return tuple(sum(p[i] for p in pts) / n for i in range(3))


def main():
    xt = {t: xtal_atoms(t) for t in ("MGAM", "HPA")}
    for t, a in xt.items():
        print(t, "crystal acarbose heavy atoms:", len(a))
    out = {}
    for row in S["rows"]:
        lig = row["ligand"]
        rec = {}
        for t in ("MGAM", "HPA"):
            p = ROOT / "poses" / row[t]["pose"]
            atoms = pose_atoms(p)
            near = sum(1 for a in atoms if any(d2(a, b) <= 4.0 for b in xt[t]))   # within 2.0 A
            near3 = sum(1 for a in atoms if any(d2(a, b) <= 9.0 for b in xt[t]))  # within 3.0 A
            rec[t] = {
                "n_atoms": len(atoms),
                "occupancy_2A": round(near / len(atoms), 3),
                "occupancy_3A": round(near3 / len(atoms), 3),
                "centroid_shift": round(math.sqrt(d2(centroid(atoms), centroid(xt[t]))), 2),
                "n_catalytic": len(row[t]["catalytic_hits"]),
                "n_hbond": len(row[t]["hbond_res"]),
                "LE": row[t]["LE"],
            }
        out[lig] = rec
        print(f"{lig:36s} MGAM occ2 {rec['MGAM']['occupancy_2A']:.2f} shift {rec['MGAM']['centroid_shift']:5.2f} | "
              f"HPA occ2 {rec['HPA']['occupancy_2A']:.2f} shift {rec['HPA']['centroid_shift']:5.2f}")
    (ROOT / "site_occupancy.json").write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()

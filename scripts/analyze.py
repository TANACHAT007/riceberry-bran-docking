"""Summarise docking: mean±SD affinity, ligand efficiency, redock RMSD, contact residues, drug-likeness."""
import json, statistics as st
from pathlib import Path
import numpy as np
from rdkit import Chem
from rdkit.Chem import AllChem, Descriptors, Crippen, Lipinski, rdMolDescriptors, rdMolAlign
from meeko import PDBQTMolecule, RDKitMolCreate

ROOT = Path(__file__).resolve().parent.parent
META = json.loads((ROOT / "meta.json").read_text())
RES = json.loads((ROOT / "dock_results.json").read_text())
CATALYTIC = {"MGAM": {"ASP443", "ASP542", "ASP327", "ASP203", "TRP406", "PHE575"},
             "HPA": {"ASP197", "GLU233", "ASP300", "TRP59", "TYR62", "HIS305"}}


def slug(s):
    return "".join(c if c.isalnum() else "_" for c in s).strip("_")


def best_pose(tgt, lig):
    runs = sorted([r for r in RES if r["target"] == tgt and r["ligand"] == lig], key=lambda r: r["affinity"])
    pm = PDBQTMolecule.from_file(str(ROOT / "poses" / runs[0]["pose"]), skip_typing=True)
    return RDKitMolCreate.from_pdbqt_mol(pm)[0], runs


def receptor_atoms(tgt):
    out = []
    for l in open(ROOT / "rec" / f"{tgt}_H.pdb"):
        if l.startswith("ATOM"):
            out.append((l[17:20] + str(int(l[22:26])), l[12:16].strip(), np.array([float(l[30:38]), float(l[38:46]), float(l[46:54])])))
    return out


def contacts(mol, rec, cut=4.0):
    xyz = mol.GetConformer().GetPositions()
    heavy = [i for i, a in enumerate(mol.GetAtoms()) if a.GetAtomicNum() > 1]
    polar = [i for i in heavy if mol.GetAtomWithIdx(i).GetSymbol() in "NO"]
    near, hb = set(), set()
    for res, name, p in rec:
        if name.startswith("H"):
            continue
        d = np.linalg.norm(xyz[heavy] - p, axis=1)
        if d.min() <= cut:
            near.add(res)
        if name[0] in "NO" and polar and np.linalg.norm(xyz[polar] - p, axis=1).min() <= 3.5:
            hb.add(res)
    key = lambda r: int(r[3:])
    return sorted(near, key=key), sorted(hb, key=key)


def redock_rmsd(tgt, mol):
    xt = Chem.MolFromPDBFile(str(ROOT / "rec" / f"{tgt}_xtal_lig.pdb"), removeHs=True)
    tmpl = Chem.MolFromSmiles(META["ligands"]["acarbose"]["smiles"])
    xt = AllChem.AssignBondOrdersFromTemplate(tmpl, xt)
    return rdMolAlign.CalcRMS(Chem.RemoveHs(mol), xt)


def xtal_overlap(tgt, mol):
    xt = np.array([[float(l[30:38]), float(l[38:46]), float(l[46:54])] for l in open(ROOT / "rec" / f"{tgt}_xtal_lig.pdb") if l.startswith("HETATM")])
    p = Chem.RemoveHs(mol).GetConformer().GetPositions()
    return float(np.mean([np.linalg.norm(xt - a, axis=1).min() <= 2.0 for a in p]))


def druglike(smi):
    m = Chem.MolFromSmiles(smi)
    d = {"MW": Descriptors.MolWt(m), "logP": Crippen.MolLogP(m), "HBD": Lipinski.NumHDonors(m),
         "HBA": Lipinski.NumHAcceptors(m), "TPSA": rdMolDescriptors.CalcTPSA(m), "RotB": Lipinski.NumRotatableBonds(m),
         "HA": m.GetNumHeavyAtoms()}
    d["Lipinski_violations"] = sum([d["MW"] > 500, d["logP"] > 5, d["HBD"] > 5, d["HBA"] > 10])
    d["Veber_pass"] = d["TPSA"] <= 140 and d["RotB"] <= 10
    return {k: (round(v, 2) if isinstance(v, float) else v) for k, v in d.items()}


if __name__ == "__main__":
    rec = {t: receptor_atoms(t) for t in META["targets"]}
    summary, val = [], {}
    for lig, info in META["ligands"].items():
        dl = druglike(info["smiles"])
        row = {"ligand": lig, "cid": info["cid"], **dl}
        for t in META["targets"]:
            mol, runs = best_pose(t, lig)
            aff = [r["affinity"] for r in runs]
            near, hb = contacts(mol, rec[t])
            row[t] = {"mean": round(st.mean(aff), 2), "sd": round(st.stdev(aff), 2), "best": min(aff),
                      "LE": round(-min(aff) / dl["HA"], 3), "contacts": near, "hbond_res": hb,
                      "catalytic_hits": sorted(set(near) & CATALYTIC[t]), "pose": runs[0]["pose"]}
            Chem.MolToMolFile(mol, str(ROOT / "poses" / f"{t}__{slug(lig)}__best.mol"))
            if lig == "acarbose":
                val[t] = {"xtal_overlap_2A": round(xtal_overlap(t, mol), 2)}
        summary.append(row)
    rd = json.loads((ROOT / "redock.json").read_text())
    val["MGAM"]["redock"] = rd
    val["MGAM"]["rmsd"] = min(r["rmsd"] for r in rd)
    val["MGAM"]["rmsd_mean"] = round(st.mean(r["rmsd"] for r in rd), 2)
    for t in META["targets"]:
        ref = next(r for r in summary if r["ligand"] == "acarbose")[t]["mean"]
        print(f"\n== {t} (acarbose ref {ref}) validation {val[t]}")
        for r in sorted(summary, key=lambda r: r[t]["mean"]):
            x = r[t]
            print(f"{r['ligand']:34s} {x['mean']:6.2f}±{x['sd']:.2f}  LE {x['LE']:.3f}  cat {','.join(x['catalytic_hits'])}  HB {','.join(x['hbond_res'][:6])}")
    print("\n== drug-likeness")
    for r in summary:
        print(f"{r['ligand']:34s} MW {r['MW']:6.1f} logP {r['logP']:5.2f} HBD {r['HBD']} HBA {r['HBA']} TPSA {r['TPSA']:6.1f} Lip.viol {r['Lipinski_violations']} Veber {r['Veber_pass']}")
    (ROOT / "summary.json").write_text(json.dumps({"validation": val, "rows": summary}, indent=1))

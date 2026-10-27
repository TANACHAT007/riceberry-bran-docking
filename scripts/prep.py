"""Prepare receptors (PDBFixer, pH 7.4 -> Meeko PDBQT) and Riceberry bran ligands (PubChem -> RDKit -> Meeko)."""
import json, subprocess, sys, urllib.parse, urllib.request
from pathlib import Path
import numpy as np
from pdbfixer import PDBFixer
from openmm.app import PDBFile
from rdkit import Chem
from rdkit.Chem import AllChem
from meeko import MoleculePreparation, PDBQTWriterLegacy

ROOT = Path(__file__).resolve().parent.parent
D = ROOT / "data"; R = ROOT / "rec"; L = ROOT / "lig"
R.mkdir(exist_ok=True); L.mkdir(exist_ok=True)
BIN = Path(sys.executable).parent

# target -> (pdb, chain, crystal ligand residue selector)
TARGETS = {
    "MGAM": ("2QMJ", "A", lambda r: r[17:20] in ("AC1", "GLC") and r[21] == "B"),  # human ntMGAM + acarbose
    "HPA": ("3BAJ", "A", lambda r: r[17:20] == "ARE"),                           # human pancreatic a-amylase + acarbose
}

# Compounds reported in Riceberry / purple rice bran (anthocyanins, phenolic acids, gamma-oryzanol, vitamin E) + control
LIGANDS = {
    "acarbose": "cid/41774",  # cyclic acarbose; name lookup returns the open-chain CID 9811704
    "cyanidin-3-O-glucoside": "kuromanin",
    "peonidin-3-O-glucoside": "peonidin 3-glucoside",
    "protocatechuic acid": "protocatechuic acid",
    "ferulic acid": "ferulic acid",
    "p-coumaric acid": "p-coumaric acid",
    "vanillic acid": "vanillic acid",
    "cycloartenyl ferulate": "cycloartenyl ferulate",
    "24-methylenecycloartanyl ferulate": "24-methylenecycloartanyl ferulate",
    "gamma-tocotrienol": "gamma-tocotrienol",
    "alpha-tocopherol": "alpha-tocopherol",
    "quercetin": "quercetin",
}


def prep_receptor(name, pdb, chain, sel):
    src = D / f"{pdb}.pdb"
    lines = src.read_text().splitlines()
    lig = [l for l in lines if l.startswith("HETATM") and sel(l)]
    xyz = np.array([[float(l[30:38]), float(l[38:46]), float(l[46:54])] for l in lig])
    (R / f"{name}_xtal_lig.pdb").write_text("\n".join(lig) + "\nEND\n")
    f = PDBFixer(filename=str(src))
    f.removeChains([c.index for c in f.topology.chains() if c.id != chain])
    f.removeHeterogens(keepWater=False)
    f.findMissingResidues(); f.missingResidues = {}  # do not model missing loops
    f.findNonstandardResidues(); f.replaceNonstandardResidues()
    f.findMissingAtoms(); f.addMissingAtoms(); f.addMissingHydrogens(7.4)
    with open(R / f"{name}_H.pdb", "w") as fh:
        PDBFile.writeFile(f.topology, f.positions, fh, keepIds=True)
    subprocess.run([str(BIN / "mk_prepare_receptor.py"), "--read_pdb", str(R / f"{name}_H.pdb"),
                    "-o", str(R / name), "-p", "--forgive_extra_bonds", "-a"], check=True)
    return {"pdb": pdb, "center": xyz.mean(0).round(3).tolist(),
            "size": (np.ptp(xyz, 0) + 12).clip(min=22).round(1).tolist(), "n_xtal_atoms": len(lig)}


def pubchem(q):
    u = ("https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/" + (q if q.startswith("cid/") else "name/" + urllib.parse.quote(q))
         + "/property/IsomericSMILES,SMILES,MolecularFormula,MolecularWeight/JSON")
    p = json.load(urllib.request.urlopen(u, timeout=30))["PropertyTable"]["Properties"][0]
    return p["CID"], p.get("IsomericSMILES") or p.get("SMILES"), p["MolecularFormula"]


def prep_ligand(name, q):
    cid, smi, formula = pubchem(q)
    m = max(Chem.GetMolFrags(Chem.MolFromSmiles(smi), asMols=True), key=lambda f: f.GetNumAtoms())  # drop counter-ions
    smi = Chem.MolToSmiles(m)
    m = Chem.AddHs(m)
    AllChem.EmbedMolecule(m, randomSeed=42); AllChem.MMFFOptimizeMolecule(m)
    Chem.MolToMolFile(m, str(L / f"{slug(name)}.mol"))
    setup = MoleculePreparation().prepare(m)[0]
    pdbqt, ok, err = PDBQTWriterLegacy.write_string(setup)
    assert ok, err
    (L / f"{slug(name)}.pdbqt").write_text(pdbqt)
    return {"cid": cid, "smiles": smi, "formula": formula}


def slug(s):
    return "".join(c if c.isalnum() else "_" for c in s).strip("_")


if __name__ == "__main__":
    meta = {"targets": {}, "ligands": {}}
    for n, (pdb, ch, sel) in TARGETS.items():
        meta["targets"][n] = prep_receptor(n, pdb, ch, sel); print(n, meta["targets"][n])
    for n, q in LIGANDS.items():
        meta["ligands"][n] = prep_ligand(n, q); print(n, meta["ligands"][n]["cid"], meta["ligands"][n]["formula"])
    (ROOT / "meta.json").write_text(json.dumps(meta, indent=2))

"""Standard redocking control: crystal acarbose (crystal ring puckers, randomised torsions) -> Vina -> RMSD."""
import json, sys
from multiprocessing import Pool
from pathlib import Path
from rdkit import Chem
from rdkit.Chem import AllChem, rdMolAlign
from meeko import MoleculePreparation, PDBQTWriterLegacy, PDBQTMolecule, RDKitMolCreate
from vina import Vina

ROOT = Path(__file__).resolve().parent.parent
META = json.loads((ROOT / "meta.json").read_text())
SEEDS = (11, 22, 33)


def xtal(tgt):
    m = Chem.MolFromPDBFile(str(ROOT / "rec" / f"{tgt}_xtal_lig.pdb"), removeHs=True)
    m = AllChem.AssignBondOrdersFromTemplate(Chem.MolFromSmiles(META["ligands"]["acarbose"]["smiles"]), m)
    Chem.AssignStereochemistryFrom3D(m)
    return m


def run(seed, tgt="MGAM"):
    ref = xtal(tgt)
    m = Chem.AddHs(ref, addCoords=True)
    setup = MoleculePreparation().prepare(m)[0]
    pdbqt = PDBQTWriterLegacy.write_string(setup)[0]
    t = META["targets"][tgt]
    v = Vina(sf_name="vina", cpu=3, seed=seed, verbosity=0)
    v.set_receptor(str(ROOT / "rec" / f"{tgt}.pdbqt"))
    v.set_ligand_from_string(pdbqt)
    v.compute_vina_maps(center=t["center"], box_size=t["size"])
    v.randomize()  # start away from the crystal pose
    v.dock(exhaustiveness=16, n_poses=9)
    out = ROOT / "poses" / f"{tgt}__acarbose_xtal_redock__s{seed}.pdbqt"
    v.write_poses(str(out), n_poses=9, overwrite=True)
    pose = RDKitMolCreate.from_pdbqt_mol(PDBQTMolecule.from_file(str(out), skip_typing=True))[0]
    return {"seed": seed, "affinity": round(float(v.energies(n_poses=1)[0][0]), 2),
            "rmsd": round(rdMolAlign.CalcRMS(Chem.RemoveHs(pose), ref), 2)}


if __name__ == "__main__":
    with Pool(3) as p:
        res = p.map(run, SEEDS)
    print(res)
    (ROOT / "redock.json").write_text(json.dumps(res, indent=1))

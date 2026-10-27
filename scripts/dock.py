"""AutoDock Vina 1.2 docking: 2 targets x 12 ligands x 3 independent seeds (exhaustiveness 16)."""
import json, sys
from multiprocessing import Pool
from pathlib import Path
from vina import Vina

ROOT = Path(__file__).resolve().parent.parent
META = json.loads((ROOT / "meta.json").read_text())
OUT = ROOT / "poses"; OUT.mkdir(exist_ok=True)
SEEDS = (11, 22, 33)
EXH = 16


def slug(s):
    return "".join(c if c.isalnum() else "_" for c in s).strip("_")


def run(job):
    tgt, lig, seed = job
    t = META["targets"][tgt]
    v = Vina(sf_name="vina", cpu=1, seed=seed, verbosity=0)
    v.set_receptor(str(ROOT / "rec" / f"{tgt}.pdbqt"))
    v.set_ligand_from_file(str(ROOT / "lig" / f"{slug(lig)}.pdbqt"))
    v.compute_vina_maps(center=t["center"], box_size=t["size"])
    v.dock(exhaustiveness=EXH, n_poses=9)
    out = OUT / f"{tgt}__{slug(lig)}__s{seed}.pdbqt"
    v.write_poses(str(out), n_poses=9, overwrite=True)
    e = v.energies(n_poses=1)[0]
    return {"target": tgt, "ligand": lig, "seed": seed, "affinity": round(float(e[0]), 2), "pose": out.name}


if __name__ == "__main__":
    jobs = [(t, l, s) for t in META["targets"] for l in META["ligands"] for s in SEEDS]
    res = []
    with Pool(10) as p:
        for r in p.imap_unordered(run, jobs):
            res.append(r); print(len(res), "/", len(jobs), r["target"], r["ligand"], r["seed"], r["affinity"], flush=True)
    (ROOT / "dock_results.json").write_text(json.dumps(res, indent=1))

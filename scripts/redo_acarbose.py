"""Re-prepare acarbose from the cyclic PubChem record (CID 41774) and re-dock it on both targets."""
import json
from multiprocessing import Pool
from prep import prep_ligand, LIGANDS, ROOT
import dock

if __name__ == "__main__":
    meta = json.loads((ROOT / "meta.json").read_text())
    meta["ligands"]["acarbose"] = prep_ligand("acarbose", LIGANDS["acarbose"])
    (ROOT / "meta.json").write_text(json.dumps(meta, indent=2))
    dock.META = meta
    jobs = [(t, "acarbose", s) for t in meta["targets"] for s in dock.SEEDS]
    with Pool(6) as p:
        new = p.map(dock.run, jobs)
    print(new)
    res = [r for r in json.loads((ROOT / "dock_results.json").read_text()) if r["ligand"] != "acarbose"] + new
    (ROOT / "dock_results.json").write_text(json.dumps(res, indent=1))

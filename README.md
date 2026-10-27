# INMU 50th — Riceberry bran in silico abstract

Theme 1: Food Science and Food Chemistry (sub-theme: Bioactive Compounds / Functional Ingredients)
Abstract deadline 30 Oct 2026 (form checkbox says 30 Sep; confirm with LINE @inmu50th). Results 16 Nov 2026.

## Why this topic (maps to the 9 judging criteria)
- Relevance: bioactive compounds + functional ingredient, Thai crop, fits "Real World Impact".
- Impact: rice bran is a low-value milling by-product (BCG economy) and T2DM is a top Thai NCD.
- Novelty: published docking work covers black rice bran in general; no Riceberry-panel study found against
  the two *human* starch-digesting enzymes side by side.
- Method quality: validated redock (RMSD), 3 independent seeds (mean±SD), two crystal structures with acarbose,
  ligand efficiency + Lipinski/Veber, interaction residues. Fully reproducible scripts in scripts/.
- Honest conclusion: computational screening only; next step is in vitro IC50 of real bran extract.
- Presentation: interactive 3D web viewer (web/riceberry-docking.html) + QR on the poster.

## Pipeline
    .v11/bin/python scripts/prep.py      # PDBFixer + Meeko receptors, PubChem ligands
    .v11/bin/python scripts/dock.py      # Vina 1.2.7, 2 x 12 x 3 seeds
    .v11/bin/python scripts/analyze.py   # summary.json
    .v11/bin/python scripts/build_web.py # 3D page
    .v11/bin/python scripts/gen_docx.py  # submission/*.docx from abstract.json

Vina was built from source (setup.py patched: Homebrew boost path, -std=c++17).

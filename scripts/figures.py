"""Poster figures: affinity dumbbell/bar chart, compound structures, workflow."""
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from rdkit import Chem
from rdkit.Chem import Draw
from rdkit.Chem.Draw import rdMolDraw2D

ROOT = Path(__file__).resolve().parent.parent
S = json.loads((ROOT / "summary.json").read_text())
FIG = ROOT / "figures"; FIG.mkdir(exist_ok=True)
for f in ("Sarabun-Regular.ttf", "Sarabun-Bold.ttf", "Sarabun-SemiBold.ttf"):
    fm.fontManager.addfont(str(Path.home() / "Library/Fonts" / f))
plt.rcParams.update({"font.family": ["Sarabun", "DejaVu Sans"], "font.size": 20, "axes.spines.top": False, "axes.spines.right": False})
NAVY, BERRY, GOLD, PINK, GREY = "#1d3a8a", "#7a3fd1", "#e0a100", "#e0457b", "#9aa3b5"
LABEL = {"acarbose": "Acarbose (control)", "cyanidin-3-O-glucoside": "Cyanidin-3-O-glucoside",
         "peonidin-3-O-glucoside": "Peonidin-3-O-glucoside", "protocatechuic acid": "Protocatechuic acid",
         "ferulic acid": "Ferulic acid", "p-coumaric acid": "p-Coumaric acid", "vanillic acid": "Vanillic acid",
         "cycloartenyl ferulate": "Cycloartenyl ferulate", "24-methylenecycloartanyl ferulate": "24-Methylenecycloartanyl ferulate",
         "gamma-tocotrienol": "γ-Tocotrienol", "alpha-tocopherol": "α-Tocopherol", "quercetin": "Quercetin"}
GROUP = {"cyanidin-3-O-glucoside": BERRY, "peonidin-3-O-glucoside": BERRY, "cycloartenyl ferulate": GOLD,
         "24-methylenecycloartanyl ferulate": GOLD, "gamma-tocotrienol": "#2a9d6f", "alpha-tocopherol": "#2a9d6f",
         "quercetin": "#d9762b", "acarbose": PINK}


def affinity_chart():
    rows = sorted(S["rows"], key=lambda r: r["MGAM"]["mean"] + r["HPA"]["mean"], reverse=True)
    fig, ax = plt.subplots(figsize=(11, 8.2), dpi=220)
    y = range(len(rows)); h = 0.38
    for i, r in enumerate(rows):
        c = GROUP.get(r["ligand"], NAVY)
        ax.barh(i + h / 2, -r["MGAM"]["mean"], h, xerr=r["MGAM"]["sd"], color=c, alpha=.95, capsize=3, error_kw={"lw": 1})
        ax.barh(i - h / 2, -r["HPA"]["mean"], h, xerr=r["HPA"]["sd"], color=c, alpha=.45, capsize=3, hatch="//", edgecolor="white", error_kw={"lw": 1})
    ref = next(r for r in rows if r["ligand"] == "acarbose")
    ax.axvline(-ref["MGAM"]["mean"], color=PINK, ls="--", lw=1.4); ax.axvline(-ref["HPA"]["mean"], color=PINK, ls=":", lw=1.4)
    ax.set_yticks(list(y), [LABEL[r["ligand"]] for r in rows], fontsize=19)
    ax.set_xlabel("Binding affinity, −ΔG (kcal/mol), mean ± SD, n = 3")
    ax.set_xlim(4, 11.2)
    from matplotlib.patches import Patch
    from matplotlib.lines import Line2D
    ax.legend(handles=[Patch(color=GREY, label="α-Glucosidase (MGAM), solid"), Patch(facecolor=GREY, alpha=.45, hatch="//", edgecolor="white", label="α-Amylase (HPA), hatched"),
                       Line2D([], [], color=PINK, ls="--", label="Acarbose, MGAM"), Line2D([], [], color=PINK, ls=":", label="Acarbose, HPA")],
              loc="lower right", frameon=False, fontsize=17)
    ax.grid(axis="x", color="#e5e8f0"); ax.set_axisbelow(True)
    fig.tight_layout(); fig.savefig(FIG / "affinity.png", transparent=False, facecolor="white")


def selectivity_map():
    """ΔΔG vs acarbose on each enzyme (same protocol). Ideal food inhibitor: left half (≥ acarbose on α-glucosidase), top half (milder on α-amylase)."""
    rows = {r["ligand"]: r for r in S["rows"]}; a = rows.pop("acarbose")
    xt = min(r["affinity"] for r in S["validation"]["MGAM"]["redock"])
    fig, ax = plt.subplots(figsize=(11.5, 9.4), dpi=220)
    from matplotlib.patches import Rectangle
    ax.add_patch(Rectangle((-3.4, 0), 3.4, 3.5, color="#efe6ff", zorder=0))
    ax.axhline(0, color="#9aa3b5", lw=1); ax.axvline(0, color="#9aa3b5", lw=1)
    ax.axvline(xt - a["MGAM"]["mean"], color=PINK, ls=":", lw=1.4)
    ax.text(xt - a["MGAM"]["mean"] + 0.05, -2.25, "crystal-shape\nacarbose", color=PINK, fontsize=16, va="bottom")
    ax.text(-3.3, 3.35, "USABLE FOR FOOD:\nranks with acarbose on α-glucosidase\nand dissolves in water", color=BERRY, fontsize=19, fontweight="bold", va="top")
    for n, r in rows.items():
        dx = r["MGAM"]["mean"] - a["MGAM"]["mean"]; dy = r["HPA"]["mean"] - a["HPA"]["mean"]
        sol = r["logP"] < 3
        ax.errorbar(dx, dy, xerr=r["MGAM"]["sd"], yerr=r["HPA"]["sd"], fmt="none", ecolor="#555", lw=1, zorder=2)
        ax.scatter(dx, dy, s=330, color=GROUP.get(n, NAVY), marker="o" if sol else "s", edgecolor="white", lw=1.5, zorder=3)
        off = {"peonidin-3-O-glucoside": (0.08, -0.32), "cyanidin-3-O-glucoside": (0.08, 0.12), "p-coumaric acid": (0.08, -0.3),
               "ferulic acid": (0.08, 0.1), "24-methylenecycloartanyl ferulate": (0.08, 0.12), "quercetin": (0.08, -0.3), "gamma-tocotrienol": (-0.75, 0.1)}.get(n, (0.08, 0.08))
        ax.text(dx + off[0], dy + off[1], LABEL[n], fontsize=16, zorder=4)
    ax.scatter(0, 0, s=320, marker="*", color=PINK, zorder=4); ax.text(0.08, -0.3, "Acarbose", color=PINK, fontsize=17, fontweight="bold")
    ax.set_xlim(-3.4, 1.0); ax.set_ylim(-2.3, 3.5)
    ax.set_xlabel("ΔΔG vs acarbose, α-glucosidase (MGAM)  ←  binds tighter")
    ax.set_ylabel("ΔΔG vs acarbose, α-amylase (HPA)  →  milder")
    from matplotlib.lines import Line2D
    ax.legend(handles=[Line2D([], [], marker="o", ls="", color="#666", ms=14, label="water-soluble (logP < 3)"),
                       Line2D([], [], marker="s", ls="", color="#666", ms=14, label="lipophilic (logP > 8)")],
              loc="lower right", frameon=False, fontsize=17)
    ax.grid(color="#eef0f5"); ax.set_axisbelow(True)
    fig.tight_layout(); fig.savefig(FIG / "selectivity.png", facecolor="white")


def structures():
    names = ["cyanidin-3-O-glucoside", "peonidin-3-O-glucoside", "cycloartenyl ferulate", "gamma-tocotrienol",
             "quercetin", "acarbose"]
    rows = {r["ligand"]: r for r in S["rows"]}
    meta = json.loads((ROOT / "meta.json").read_text())["ligands"]
    mols = [Chem.MolFromSmiles(meta[n]["smiles"]) for n in names]
    opts = rdMolDraw2D.MolDrawOptions(); opts.legendFontSize = 34; opts.bondLineWidth = 2; opts.addStereoAnnotation = False
    img = Draw.MolsToGridImage(mols, molsPerRow=6, subImgSize=(560, 430), legends=[LABEL[n].replace("γ", "gamma-").replace("gamma--", "gamma-") for n in names], drawOptions=opts)
    img.save(FIG / "structures.png")


def qr(url):
    import qrcode
    q = qrcode.QRCode(border=1, box_size=20); q.add_data(url); q.make(fit=True)
    q.make_image(fill_color=NAVY, back_color="white").save(FIG / "qr.png")


if __name__ == "__main__":
    import sys
    affinity_chart(); selectivity_map(); structures()
    if len(sys.argv) > 1:
        qr(sys.argv[1])
    print("ok")

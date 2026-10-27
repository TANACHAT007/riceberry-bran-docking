"""Additional poster figures: ligand efficiency, score-versus-size bias, interaction fingerprint."""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import font_manager as fm
from scipy import stats

ROOT = Path(__file__).resolve().parent.parent
S = json.loads((ROOT / "summary.json").read_text())
OCC = json.loads((ROOT / "site_occupancy.json").read_text())
FIG = ROOT / "figures"
for f in ("Sarabun-Regular.ttf", "Sarabun-Bold.ttf", "Sarabun-SemiBold.ttf"):
    fm.fontManager.addfont(str(Path.home() / "Library/Fonts" / f))
plt.rcParams.update({"font.family": ["Sarabun", "DejaVu Sans"], "font.size": 20,
                     "axes.spines.top": False, "axes.spines.right": False})
NAVY, BERRY, GOLD, PINK, GREEN, ORANGE = "#1d3a8a", "#7a3fd1", "#e0a100", "#e0457b", "#2a9d6f", "#d9762b"
LABEL = {"acarbose": "Acarbose", "cyanidin-3-O-glucoside": "Cyanidin-3-O-glc",
         "peonidin-3-O-glucoside": "Peonidin-3-O-glc", "protocatechuic acid": "Protocatechuic acid",
         "ferulic acid": "Ferulic acid", "p-coumaric acid": "p-Coumaric acid", "vanillic acid": "Vanillic acid",
         "cycloartenyl ferulate": "Cycloartenyl ferulate",
         "24-methylenecycloartanyl ferulate": "24-Methylenecycloartanyl ferulate",
         "gamma-tocotrienol": "γ-Tocotrienol", "alpha-tocopherol": "α-Tocopherol", "quercetin": "Quercetin"}
GROUP = {"cyanidin-3-O-glucoside": BERRY, "peonidin-3-O-glucoside": BERRY, "cycloartenyl ferulate": GOLD,
         "24-methylenecycloartanyl ferulate": GOLD, "gamma-tocotrienol": GREEN, "alpha-tocopherol": GREEN,
         "quercetin": ORANGE, "acarbose": PINK}
ROWS = {r["ligand"]: r for r in S["rows"]}


def efficiency_and_size():
    """Left: ligand efficiency. Right: score against molecular size, with the fitted trend."""
    rows = sorted(S["rows"], key=lambda r: -(r["MGAM"]["LE"] + r["HPA"]["LE"]) / 2)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(21, 8.6), dpi=200, gridspec_kw={"width_ratios": [1.05, 1]})

    y = np.arange(len(rows)); h = 0.38
    for i, r in enumerate(rows):
        c = GROUP.get(r["ligand"], NAVY)
        ax1.barh(i + h / 2, r["MGAM"]["LE"], h, color=c, alpha=.95)
        ax1.barh(i - h / 2, r["HPA"]["LE"], h, color=c, alpha=.45, hatch="//", edgecolor="white")
    ax1.set_yticks(y, [LABEL[r["ligand"]] for r in rows], fontsize=18)
    ax1.invert_yaxis()
    ax1.axvline(ROWS["acarbose"]["HPA"]["LE"], color=PINK, ls=":", lw=1.6)
    ax1.set_xlabel("Ligand efficiency, −ΔG per heavy atom (kcal/mol/atom)", fontsize=19)
    ax1.set_title("A  Binding per atom, not per molecule", fontsize=22, fontweight="bold", loc="left", color=NAVY)
    from matplotlib.patches import Patch
    ax1.legend(handles=[Patch(color="#9aa3b5", label="α-glucosidase (MGAM), solid"),
                        Patch(facecolor="#9aa3b5", alpha=.45, hatch="//", edgecolor="white", label="α-amylase (HPA), hatched")],
               loc="lower right", frameon=False, fontsize=17)
    ax1.grid(axis="x", color="#e5e8f0"); ax1.set_axisbelow(True)

    for t, mk, lbl in (("MGAM", "o", "α-Glucosidase (MGAM)"), ("HPA", "^", "α-Amylase (HPA)")):
        x = np.array([r["HA"] for r in S["rows"]], float)
        yv = np.array([-r[t]["mean"] for r in S["rows"]], float)
        lr = stats.linregress(x, yv)
        xs = np.linspace(x.min() - 1, x.max() + 1, 20)
        ax2.plot(xs, lr.intercept + lr.slope * xs, color=NAVY if t == "MGAM" else GREEN, lw=1.6,
                 ls="-" if t == "MGAM" else "--",
                 label=f"{lbl}: r = {lr.rvalue:.2f}, p = {lr.pvalue:.1g}")
        for r in S["rows"]:
            ax2.scatter(r["HA"], -r[t]["mean"], s=190, marker=mk, color=GROUP.get(r["ligand"], NAVY),
                        edgecolor="white", lw=1.2, zorder=3)
    for n in ("cyanidin-3-O-glucoside", "cycloartenyl ferulate", "acarbose", "quercetin"):
        r = ROWS[n]
        ax2.annotate(LABEL[n], (r["HA"], -r["MGAM"]["mean"]), textcoords="offset points",
                     xytext=(8, -4), fontsize=17)
    ax2.set_xlabel("Heavy atoms in the molecule", fontsize=19)
    ax2.set_ylabel("Predicted binding, −ΔG (kcal/mol)", fontsize=19)
    ax2.set_title("B  Docking scores rise with molecular size", fontsize=22, fontweight="bold", loc="left", color=NAVY)
    ax2.legend(frameon=False, fontsize=17, loc="lower right")
    ax2.grid(color="#eef0f5"); ax2.set_axisbelow(True)
    fig.tight_layout(); fig.savefig(FIG / "efficiency_size.png", facecolor="white")


KEY = {"MGAM": ["ASP203", "ILE364", "TRP406", "ILE441", "ASP443", "MET444", "ARG526", "TRP539", "ASP542",
                "PHE575", "ALA576", "HIS600", "TYR605"],
       "HPA": ["TRP58", "TRP59", "TYR62", "HIS101", "TYR151", "LEU162", "ARG195", "ASP197", "ALA198",
               "LYS200", "HIS201", "GLU233", "HIS299", "ASP300"]}
CATALYTIC = {"MGAM": {"ASP443", "ASP542", "ASP203"}, "HPA": {"ASP197", "GLU233", "ASP300"}}


def fingerprint(wide=False):
    """Which active-site residues each compound touches, and where it hydrogen-bonds."""
    order = [r["ligand"] for r in sorted(S["rows"], key=lambda r: r["MGAM"]["mean"] + r["HPA"]["mean"])]
    size = (27, 7.6) if wide else (22, 9.4)
    fs = 20 if wide else 16
    fig, axes = plt.subplots(1, 2, figsize=size, dpi=200, gridspec_kw={"width_ratios": [1, 1.06]})
    cmap = matplotlib.colors.ListedColormap(["#f2f4f9", "#b9c6e8", NAVY])
    for ax, t in zip(axes, ("MGAM", "HPA")):
        res = KEY[t]
        M = np.zeros((len(order), len(res)))
        for i, lig in enumerate(order):
            row = ROWS[lig][t]
            for j, rr in enumerate(res):
                M[i, j] = 2 if rr in row["hbond_res"] else (1 if rr in row["contacts"] else 0)
        ax.imshow(M, cmap=cmap, vmin=0, vmax=2, aspect="auto")
        ax.set_xticks(range(len(res)), res, rotation=90, fontsize=fs)
        for j, rr in enumerate(res):
            if rr in CATALYTIC[t]:
                ax.get_xticklabels()[j].set_color(PINK)
                ax.get_xticklabels()[j].set_fontweight("bold")
        ax.set_yticks(range(len(order)), [LABEL[n] for n in order], fontsize=fs)
        ax.set_xticks(np.arange(-.5, len(res), 1), minor=True)
        ax.set_yticks(np.arange(-.5, len(order), 1), minor=True)
        ax.grid(which="minor", color="white", lw=2); ax.tick_params(which="minor", length=0)
        ax.set_title(("C  α-Glucosidase (MGAM)" if t == "MGAM" else "D  α-Amylase (HPA)"),
                     fontsize=22, fontweight="bold", loc="left", color=NAVY)
        for s in ax.spines.values():
            s.set_visible(False)
    axes[1].set_yticks([])
    from matplotlib.patches import Patch
    axes[1].legend(handles=[Patch(color=NAVY, label="hydrogen bond ≤ 3.5 Å"),
                            Patch(color="#b9c6e8", label="contact ≤ 4 Å"),
                            Patch(color="#f2f4f9", label="no contact"),
                            Patch(color="white", label="catalytic residues in pink")],
                   loc="upper left", bbox_to_anchor=(1.01, 1), frameon=False, fontsize=fs)
    fig.tight_layout()
    fig.savefig(FIG / ("fingerprint_wide.png" if wide else "fingerprint.png"), facecolor="white")


def occupancy():
    """Every candidate sits inside the footprint the crystal acarbose occupies."""
    order = [r["ligand"] for r in sorted(S["rows"], key=lambda r: r["MGAM"]["mean"] + r["HPA"]["mean"])]
    fig, ax = plt.subplots(figsize=(11, 8.0), dpi=200)
    y = np.arange(len(order)); h = 0.38
    for i, n in enumerate(order):
        c = GROUP.get(n, NAVY)
        ax.barh(i + h / 2, OCC[n]["MGAM"]["occupancy_2A"] * 100, h, color=c, alpha=.95)
        ax.barh(i - h / 2, OCC[n]["HPA"]["occupancy_2A"] * 100, h, color=c, alpha=.45, hatch="//", edgecolor="white")
    ax.set_yticks(y, [LABEL[n] for n in order], fontsize=18); ax.invert_yaxis()
    ax.set_xlabel("Pose atoms inside the crystal acarbose footprint (%)", fontsize=19)
    ax.set_xlim(0, 105)
    ax.grid(axis="x", color="#e5e8f0"); ax.set_axisbelow(True)
    fig.tight_layout(); fig.savefig(FIG / "occupancy.png", facecolor="white")


if __name__ == "__main__":
    efficiency_and_size(); fingerprint(); fingerprint(wide=True); occupancy()
    print("ok")

"""Forecast figure: what the bench assay should give, projected from the published literature.

Every value plotted here comes from a published paper (see SOURCES) or from an explicit
calculation on those values. Nothing is invented.
"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import font_manager as fm
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

ROOT = Path(__file__).resolve().parent.parent
FIG = ROOT / "figures"
for f in ("Sarabun-Regular.ttf", "Sarabun-Bold.ttf", "Sarabun-SemiBold.ttf"):
    fm.fontManager.addfont(str(Path.home() / "Library/Fonts" / f))
plt.rcParams.update({"font.family": ["Sarabun", "DejaVu Sans"], "font.size": 19,
                     "axes.spines.top": False, "axes.spines.right": False})
NAVY, BERRY, GOLD, PINK, GREEN, GREY = "#1d3a8a", "#7a3fd1", "#e0a100", "#e0457b", "#2a9d6f", "#9aa3b5"

MW_C3G = 449.4          # g/mol, cyanidin-3-O-glucoside

# ---- published IC50 of pure compounds, one study, one set of assays ------------------
# Akkarachiyasit S, Charoenlertkul P, Yibchok-anun S, Adisakwattana S.
# Int J Mol Sci. 2010;11:3387. Rat intestinal maltase and sucrase, porcine pancreatic
# alpha-amylase. Values in mM, mean +/- SEM, n = 3. ">" = not reached at that concentration.
PURE = {                                   # (maltase, sucrase, amylase), censored flag per enzyme
    "Cyanidin":                 ((3.00, True), (1.42, False), (0.38, False)),
    "Cyanidin-3-O-glucoside":   ((3.00, True), (0.97, False), (0.30, False)),
    "Cyanidin-3-O-galactoside": ((3.00, True), (0.50, False), (1.00, True)),
    "Cyanidin-3,5-diglucoside": ((3.00, True), (2.00, True),  (1.00, True)),
    "Acarbose":                 ((0.003, False), (0.09, False), (0.12, False)),
}
PURE_SD = {"Cyanidin": (None, 0.25, 0.01), "Cyanidin-3-O-glucoside": (None, 0.05, 0.01),
           "Cyanidin-3-O-galactoside": (None, 0.05, None), "Cyanidin-3,5-diglucoside": (None, None, None),
           "Acarbose": (0.001, 0.04, 0.04)}
ENZ = ["Intestinal maltase", "Intestinal sucrase", "Pancreatic α-amylase"]

# ---- published IC50 of pigmented-rice extracts --------------------------------------
# Settu R, Selvaraj D, Padikasan IA. Food Bioscience. 2021;42:101154. Pancreatic alpha-amylase.
EXTRACTS = [
    ("Mapillai Samba", 12.81, "amylase"),
    ("Karuppu Kavuni", 20.90, "amylase"),
    ("Elupaipoo Samba", 27.91, "amylase"),
    ("Karuthakar", 35.71, "amylase"),
    ("Kattuyanum", 37.02, "amylase"),
    ("Kodavazhai", 45.58, "amylase"),
    ("White Ponni (not pigmented)", 48.18, "amylase"),
    ("Acarbose, same assay", 13.52, "acarbose"),
]
BLACK_BRAN_GLU = 48.50   # ug/mL, black rice bran methanolic extract, alpha-glucosidase
RED_RICE_AMY = 144.46    # ug/mL, Indonesian red rice (whole grain), alpha-amylase

# ---- Riceberry bran composition ------------------------------------------------------
ANTHO_MIN, ANTHO_MAX = 2.0, 3.42     # mg total anthocyanin per g, Thai pigmented rice bran
C3G_RICEBERRY = 0.357                # mg C3G per g dry bran, Riceberry (Kasetsart)


def bottom_up(ic50_mM):
    """Extract concentration needed to deliver an inhibitory dose of anthocyanin, mg/mL.

    If the anthocyanins were the only active compounds, an extract carrying
    ANTHO mg of anthocyanin per g would have to reach this concentration.
    """
    mg_per_L = ic50_mM * MW_C3G       # mM -> mg of C3G per L
    # mg C3G per L  /  mg anthocyanin per g extract  =  g extract per L  =  mg extract per mL
    return mg_per_L / ANTHO_MAX, mg_per_L / ANTHO_MIN


def panel_pure(ax):
    names = list(PURE)
    y = np.arange(len(names))[::-1]
    off = {0: 0.26, 1: 0.0, 2: -0.26}
    colr = {0: NAVY, 1: BERRY, 2: GREEN}
    for j, enz in enumerate(ENZ):
        for i, n in enumerate(names):
            v, cens = PURE[n][j]
            sd = PURE_SD[n][j]
            yy = y[i] + off[j]
            if cens:
                ax.scatter(v, yy, marker=">", s=150, color=colr[j], zorder=3)
                ax.annotate("", xy=(v * 2.6, yy), xytext=(v, yy),
                            arrowprops=dict(arrowstyle="-|>", color=colr[j], lw=1.6))
            else:
                ax.scatter(v, yy, s=150, color=colr[j], zorder=3)
                if sd:
                    ax.plot([v - sd, v + sd], [yy, yy], color=colr[j], lw=2, zorder=2)
    ax.set_yticks(y, names, fontsize=18)
    ax.set_xscale("log")
    ax.set_xlim(8e-4, 6e1)
    ax.set_xlabel("Published IC₅₀ (mM, log scale) — further left = stronger", fontsize=18)
    ax.set_title("A  What the literature already measured, pure compounds",
                 fontsize=21, fontweight="bold", loc="left", color=NAVY)
    ax.legend(handles=[Line2D([], [], marker="o", ls="", color=colr[j], ms=11, label=ENZ[j]) for j in range(3)]
              + [Line2D([], [], marker=">", ls="", color=GREY, ms=11, label="not reached at the highest dose tested")],
              frameon=False, fontsize=15, loc="lower left", bbox_to_anchor=(0.0, -0.42), ncol=2)
    ax.grid(axis="x", color="#e8ebf2"); ax.set_axisbelow(True)


def panel_extracts(ax, pred):
    rows = [(n, v, k) for n, v, k in EXTRACTS]
    rows.append(("Black rice bran", BLACK_BRAN_GLU, "glucosidase"))
    rows.append(("Red rice, whole grain", RED_RICE_AMY, "amylase"))
    rows.sort(key=lambda r: r[1])
    y = np.arange(len(rows))[::-1]
    col = {"amylase": NAVY, "acarbose": PINK, "glucosidase": GREEN}
    for i, (n, v, k) in enumerate(rows):
        ax.barh(y[i], v, 0.6, color=col[k], alpha=.9 if k != "acarbose" else 1.0)
        ax.text(v * 0.95, y[i], f"{v:.1f}", va="center", ha="right", fontsize=15, color="white", fontweight="bold")
    ax.set_yticks(y, [r[0] for r in rows], fontsize=16)
    ax.set_xscale("log"); ax.set_xlim(5, 900)
    ax.set_xlabel("Published IC₅₀ of plant extracts (µg/mL, log scale)", fontsize=18)
    ax.set_title("B  …and for whole extracts of pigmented rice",
                 fontsize=21, fontweight="bold", loc="left", color=NAVY)
    ax.axvspan(pred["lit_lo"], pred["lit_hi"], color=BERRY, alpha=.10, zorder=0)
    ax.text(pred["lit_hi"] * 1.15, y[0] + 0.35, "where a Riceberry extract\nwould land if it behaves\nlike these",
            fontsize=15, color=BERRY, va="top")
    ax.legend(handles=[Patch(color=NAVY, label="α-amylase"), Patch(color=GREEN, label="α-glucosidase"),
                       Patch(color=PINK, label="acarbose reference")],
              frameon=False, fontsize=15, loc="lower right", bbox_to_anchor=(1.0, -0.42), ncol=3)
    ax.grid(axis="x", color="#e8ebf2"); ax.set_axisbelow(True)


def panel_prediction(ax, pred):
    c = np.logspace(-3, 3, 400)                       # mg extract / mL

    def curve(ic50):
        return 100 * c / (c + ic50)

    lit_lo, lit_hi = pred["lit_lo"] / 1000, pred["lit_hi"] / 1000      # µg/mL -> mg/mL
    ax.fill_between(c, curve(lit_hi), curve(lit_lo), color=BERRY, alpha=.22)
    ax.plot(c, curve((lit_lo * lit_hi) ** .5), color=BERRY, lw=2.6,
            label="Scenario 1 — behaves like published pigmented-rice extracts")
    amy_lo, amy_hi = pred["amy_lo"], pred["amy_hi"]
    ax.fill_between(c, curve(amy_hi), curve(amy_lo), color=GOLD, alpha=.22)
    ax.plot(c, curve((amy_lo * amy_hi) ** .5), color=GOLD, lw=2.6, ls="--",
            label="Scenario 2 — anthocyanin content alone explains the activity")
    ax.axhline(50, color=GREY, lw=1, ls=":")
    ax.axvspan(0.05, 10, color="#eef2fb", zorder=0)
    ax.text(0.33, 42, "concentration range a school-scale\nassay can actually test", fontsize=15, color=NAVY,
            ha="left")
    ax.set_xscale("log"); ax.set_xlim(1e-3, 1e3); ax.set_ylim(0, 102)
    ax.set_xlabel("Riceberry bran extract in the well (mg/mL, log scale)", fontsize=18)
    ax.set_ylabel("Predicted inhibition (%)", fontsize=18)
    ax.set_title("C  The two outcomes the experiment has to choose between",
                 fontsize=21, fontweight="bold", loc="left", color=NAVY)
    ax.legend(frameon=False, fontsize=16, loc="lower right")
    ax.grid(color="#eef0f5"); ax.set_axisbelow(True)


def main():
    amy_lo, amy_hi = bottom_up(0.30)       # C3G on pancreatic alpha-amylase
    suc_lo, suc_hi = bottom_up(0.97)       # C3G on intestinal sucrase
    mal_lo, mal_hi = bottom_up(3.00)       # C3G on intestinal maltase (lower bound only)
    pred = {"lit_lo": 12.81, "lit_hi": 48.50, "amy_lo": amy_lo, "amy_hi": amy_hi}

    fig = plt.figure(figsize=(23, 16), dpi=200)
    gs = fig.add_gridspec(2, 2, height_ratios=[1, 1.0], hspace=0.52, wspace=0.42)
    panel_pure(fig.add_subplot(gs[0, 0]))
    panel_extracts(fig.add_subplot(gs[0, 1]), pred)
    panel_prediction(fig.add_subplot(gs[1, :]), pred)
    fig.savefig(FIG / "forecast.png", facecolor="white", bbox_inches="tight")

    out = {
        "c3g_to_extract_mg_per_mL": {
            "pancreatic_alpha_amylase": [round(amy_lo, 1), round(amy_hi, 1)],
            "intestinal_sucrase": [round(suc_lo, 1), round(suc_hi, 1)],
            "intestinal_maltase_at_least": [round(mal_lo, 1), round(mal_hi, 1)],
        },
        "literature_extract_band_ug_per_mL": [12.81, 48.50],
        "ratio_scenario2_over_scenario1": round((amy_lo * 1000) / 48.50),
        "assumptions": {
            "anthocyanin_mg_per_g_extract": [ANTHO_MIN, ANTHO_MAX],
            "C3G_mg_per_g_dry_Riceberry_bran": C3G_RICEBERRY,
            "MW_C3G": MW_C3G,
        },
    }
    (ROOT / "forecast.json").write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()

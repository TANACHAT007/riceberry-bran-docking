"""Analyse 9-point hedonic data. Input sensory.csv columns: panelist,formula,appearance,color,aroma,taste,texture,overall
Usage: .v11/bin/python scripts/sensory.py [sensory.csv]"""
import csv, statistics as st, sys
from collections import defaultdict
from itertools import combinations
from pathlib import Path
from scipy import stats

ATTR = ["appearance", "color", "aroma", "taste", "texture", "overall"]
path = Path(sys.argv[1] if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent / "sensory.csv")
data = defaultdict(dict)  # attr -> formula -> {panelist: score}
for r in csv.DictReader(open(path, encoding="utf-8-sig")):
    for a in ATTR:
        data[a].setdefault(r["formula"], {})[r["panelist"]] = float(r[a])

for a in ATTR:
    forms = sorted(data[a])
    panel = sorted(set.intersection(*(set(data[a][f]) for f in forms)))
    cols = [[data[a][f][p] for p in panel] for f in forms]
    line = "  ".join(f"{f}: {st.mean(c):.2f}±{st.stdev(c):.2f}" for f, c in zip(forms, cols))
    chi, pv = stats.friedmanchisquare(*cols)
    print(f"{a:10s} n={len(panel)}  {line}  Friedman p={pv:.4f}")
    if pv < 0.05:
        k = len(list(combinations(range(len(forms)), 2)))
        for i, j in combinations(range(len(forms)), 2):
            p2 = stats.wilcoxon(cols[i], cols[j]).pvalue * k  # Bonferroni
            print(f"    {forms[i]} vs {forms[j]}: Wilcoxon p(adj)={min(p2, 1):.4f}")

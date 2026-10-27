"""Render docked poses to PNG with 3Dmol.js in headless Chrome (for the poster)."""
import json, subprocess, sys
from pathlib import Path
from build_web import pocket, slug, ROOT

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
OUT = ROOT / "figures"; TMP = ROOT / "build" / "render"; TMP.mkdir(parents=True, exist_ok=True)
S = json.loads((ROOT / "summary.json").read_text())

PAGE = """<!doctype html><html><body style="margin:0;background:#fff">
<div id="v" style="width:1600px;height:1200px;position:relative"></div>
<script src="https://cdn.jsdelivr.net/npm/3dmol@2.4.2/build/3Dmol-min.js"></script>
<script>
const D = %s;
const v = $3Dmol.createViewer("v", {backgroundColor: "white", antialias: true});
const p = v.addModel(D.pocket, "pdb");
p.setStyle({}, {cartoon: {color: "#c9d3ea", opacity: 0.9}});
const el = c => ({prop: "elem", map: {C: c, O: "#e23d3d", N: "#2f5bff", S: "#d7a800"}});
p.setStyle({resi: D.near}, {cartoon: {color: "#c9d3ea"}, stick: {radius: 0.14, colorscheme: el("#8a93a8")}});
p.setStyle({resi: D.hb}, {cartoon: {color: "#c9d3ea"}, stick: {radius: 0.18, colorscheme: el("#1fae6b")}});
p.setStyle({resi: D.cat}, {cartoon: {color: "#c9d3ea"}, stick: {radius: 0.2, colorscheme: el("#f0a400")}});
D.cat.concat(D.hb).forEach(r => { const a = p.selectedAtoms({resi: r, atom: "CA"})[0];
  if (a) v.addLabel(a.resn[0] + a.resn.slice(1).toLowerCase() + a.resi, {position: a, fontSize: 30, fontColor: "#1d3a8a", backgroundColor: "white", backgroundOpacity: 0.8, borderThickness: 0}); });
const L = v.addModel(D.pose, "mol");
L.setStyle({}, {stick: {radius: 0.3, colorscheme: el("#7a3fd1")}}); L.setStyle({elem: "H"}, {});
v.zoomTo({model: L}); v.zoom(0.72); v.render();
setTimeout(() => document.title = "ready", 1500);
</script></body></html>"""


def render(tgt, lig):
    row = next(r for r in S["rows"] if r["ligand"] == lig)[tgt]
    num = lambda xs: [int(x[3:]) for x in xs]
    d = {"pocket": pocket(tgt), "pose": (ROOT / "poses" / f"{tgt}__{slug(lig)}__best.mol").read_text(),
         "near": num(row["contacts"]), "hb": num(row["hbond_res"]), "cat": num(row["catalytic_hits"])}
    html = TMP / f"{tgt}_{slug(lig)}.html"; html.write_text(PAGE % json.dumps(d))
    png = OUT / f"pose_{tgt}_{slug(lig)}.png"
    subprocess.run([CHROME, "--headless=new", "--disable-gpu-sandbox", "--use-angle=swiftshader", "--enable-unsafe-swiftshader",
                    "--hide-scrollbars", "--window-size=1600,1200", "--virtual-time-budget=15000",
                    f"--screenshot={png}", html.as_uri()], check=True, capture_output=True, timeout=120)
    print(png.name)


if __name__ == "__main__":
    for t, l in [("MGAM", "cyanidin-3-O-glucoside"), ("HPA", "cyanidin-3-O-glucoside")]:
        render(t, l)

# Slice out/pluto_frame.stl with Bambu Studio's CLI (Bambu Lab A1 mini 0.4, Bambu PETG Basic) for a few profiles; write docs/slicer_estimates.json
import json, os, re, subprocess, sys, glob, time
import numpy as np
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = "/Applications/BambuStudio.app/Contents/Resources/profiles/BBL"
BS = "/Applications/BambuStudio.app/Contents/MacOS/BambuStudio"
WORK = sys.argv[1]
os.makedirs(WORK + "/bsdata", exist_ok=True)
PRINTER = os.environ.get("PF_PRINTER", "P1S")      # P1S (default) or A1M
if PRINTER == "P1S":
    m = json.load(open(P + "/machine/Bambu Lab P1S 0.4 nozzle.json"))
    m.update({"name": "P1S pf", "from": "user", "inherits": "Bambu Lab P1S 0.4 nozzle"})
else:
    m = json.load(open(P + "/machine/Bambu Lab A1 mini 0.4 nozzle.json"))
    m.update({"name": "A1mini pf", "from": "user", "printable_area": ["0x0", "180x0", "180x180", "0x180"], "printable_height": "180", "bed_exclude_area": [], "inherits": "Bambu Lab A1 mini 0.4 nozzle"})
MACHINE = WORK + "/machine.json"; json.dump(m, open(MACHINE, "w"))
if PRINTER == "P1S":
    base = json.load(open(P + "/process/0.16mm Optimal @BBL X1C.json"))         # Bambu's 0.16 profile for X1C / P1S
    FIL = P + "/filament/Bambu PETG Basic @BBL X1C.json"
else:
    base = json.load(open(P + "/process/0.16mm High Quality @BBL A1M.json"))
    FIL = P + "/filament/Bambu PETG Basic @BBL A1M 0.4 nozzle.json"
PETG_D = 1.27; FIL_D = 1.75
PROFILES_FRAME = {"recommended": dict(wall_loops="3", top_shell_layers="5", bottom_shell_layers="4", sparse_infill_density="40%", layer_height="0.16"),
            "light": dict(wall_loops="2", top_shell_layers="4", bottom_shell_layers="3", sparse_infill_density="15%", layer_height="0.16")}
PART = sys.argv[2] if len(sys.argv) > 2 else "pluto_frame"
stl = os.path.join(ROOT, "out", PART + ".stl")
PROFILES_COUPON = {"recommended": PROFILES_FRAME["recommended"],
                   "light_15pct_infill": dict(PROFILES_FRAME["recommended"], sparse_infill_density="15%"),
                   "lean": dict(wall_loops="2", top_shell_layers="3", bottom_shell_layers="3", sparse_infill_density="10%", layer_height="0.16"),
                   "lean_nobrim": dict(wall_loops="2", top_shell_layers="3", bottom_shell_layers="3", sparse_infill_density="10%", layer_height="0.16", brim_type="no_brim")}
PROFILES = PROFILES_FRAME if PART == "pluto_frame" else ({"recommended": PROFILES_COUPON["recommended"], "no_brim": dict(PROFILES_COUPON["recommended"], brim_type="no_brim")} if PART.startswith("sleeve") else PROFILES_COUPON)   # sleeves keep 2 perimeters (0.9 wall) in every profile
raw = open(stl, "rb").read(); n = int(np.frombuffer(raw[80:84], "<u4")[0])
dt = np.dtype([("n", "<f4", 3), ("v", "<f4", (3, 3)), ("a", "<u2")]); a = np.frombuffer(raw[84:84 + 50 * n], dtype=dt).copy()
mn = a["v"].reshape(-1, 3).min(0); mx = a["v"].reshape(-1, 3).max(0)
_c = 128 if PRINTER == "P1S" else 90
a["v"][:, :, 0] += _c - (mn[0] + mx[0]) / 2; a["v"][:, :, 1] += _c - (mn[1] + mx[1]) / 2; a["v"][:, :, 2] -= mn[2]
cen = WORK + "/%s_c.stl" % PART; open(cen, "wb").write(raw[:80] + np.uint32(n).tobytes() + a.tobytes())
res = {}
for name, ov in PROFILES.items():
    d = dict(base); d.update({"name": "pf_" + name, "from": "user", "inherits": base.get("name", ""), "enable_support": "0", "brim_type": "outer_only", "brim_width": "4",
                              "sparse_infill_pattern": "gyroid", "seam_position": "back"}); d.update(ov)
    if "brim_type" in ov: d["brim_type"] = ov["brim_type"]
    pj = f"{WORK}/{name}.json"; json.dump(d, open(pj, "w"))
    out = f"{WORK}/{PART}_{name}"; os.makedirs(out, exist_ok=True)
    t0 = time.time()
    r = subprocess.run([BS, "--datadir", WORK + "/bsdata", "--slice", "0", "--load-settings", f"{MACHINE};{pj}", "--load-filaments", FIL, "--outputdir", out, cen], capture_output=True, text=True, timeout=900)
    gc = glob.glob(out + "/plate_1.gcode")
    info = {"profile": ov, "return": r.returncode}
    if gc:
        txt = open(gc[0], errors="ignore").read()
        mm = re.search(r"total filament length \[mm\]\s*:\s*([\d.]+)", txt) or re.search(r"filament used \[mm\]\s*=\s*([\d.]+)", txt)
        tm = re.search(r"model printing time:\s*([^;\n]+)", txt) or re.search(r"estimated printing time[^=]*=\s*([^\n]+)", txt)
        if mm:
            L = float(mm.group(1)); info["filament_mm"] = L
            info["grams"] = round(L * 3.14159 * (FIL_D / 2) ** 2 / 1000 * PETG_D, 2)
        if tm: info["time"] = tm.group(1).strip()
        # brim mass is in the total; report it
        info["note"] = "includes a 4 mm outer brim"
    else:
        info["stderr"] = (r.stdout + r.stderr)[-800:]
    res[name] = info; print(name, info)
_f = os.path.join(ROOT, "docs", "slicer_estimates.json")
_all = json.load(open(_f)) if os.path.exists(_f) else {}
if "recommended" in _all: _all = {"pluto_frame": _all}      # old single-part format
_all[PART + ("" if PRINTER == "A1M" else "_" + PRINTER)] = res
json.dump(_all, open(_f, "w"), indent=1)

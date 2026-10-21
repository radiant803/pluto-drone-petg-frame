# local fast loop (Kerf venv): build the frame, report volume / mass / validity / bbox
import sys, os, time, math
from build123d import *
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for f in ("p_params.py", "p_parts.py"):
    exec(open(os.path.join(ROOT, "src", f), encoding="utf-8").read(), globals())
t = time.time()
fr = build_frame(with_labels="nolabel" not in sys.argv)
bb = fr.bounding_box()
print("build s %.1f" % (time.time() - t), "valid", fr.is_valid, "solids", len(fr.solids()))
print("bbox", [round(v, 2) for v in (bb.min.X, bb.min.Y, bb.min.Z, bb.max.X, bb.max.Y, bb.max.Z)])
print("volume mm3 %.0f  mass g %.2f" % (fr.volume, fr.volume / 1000 * PETG_DENSITY))
if "stl" in sys.argv:
    export_stl(fr, "/tmp/pf_test.stl")

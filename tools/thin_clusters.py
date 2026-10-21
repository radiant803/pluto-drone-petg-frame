# list thin-wall clusters (Kerf's own sampler) on the frame; arg 'labels' to include the engraving
import sys, os, math
import numpy as np
sys.path.insert(0, os.environ.get("KERF_SRC", os.path.expanduser("~/Kerf/src")))   # path to Kerf's src/ for its wall sampler
from build123d import *
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for f in ("p_params.py", "p_parts.py"): exec(open(os.path.join(ROOT, "src", f)).read(), globals())
from kerf.analysis import dfm
from kerf.worker.tessellate import tessellate
fr = build_frame(with_labels="labels" in sys.argv)
mesh = tessellate([("shape", fr.wrapped)])
cfg = dfm.THOROUGHNESS["thorough"]
th, pts, _ = dfm._sample_thickness(mesh, cfg["samples"], refine=cfg["refine"], dirs=cfg["dirs"])
ok = np.isfinite(th) & (th > 1e-9)
th, pts = th[ok], pts[ok]
thin = th < 0.8
print("samples", len(th), "thin", int(thin.sum()), "min %.4f" % th.min())
cells = {}
for t, p in zip(th[thin], pts[thin]):
    cells.setdefault(tuple(np.floor(p / 3).astype(int)), []).append((t, p))
for k, v in sorted(cells.items(), key=lambda kv: min(x[0] for x in kv[1]))[:25]:
    t, p = min(v, key=lambda x: x[0])
    print("%3d  %.3f  (%.2f, %.2f, %.2f)" % (len(v), t, *p))

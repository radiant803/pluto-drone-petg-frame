# printable-text check: rasterise the glyphs (0.01 mm), opening by the nozzle line (0.4) -> strokes thinner than 0.4 lose area;
# closing -> gaps narrower than 0.4 fill. Even-odd fill of all rings handles counters (A, B, 8, 6).
import json, numpy as np
from matplotlib.path import Path
from scipy import ndimage as nd
G = json.load(open("/tmp/pf_glyphs.json")); px = 0.01
for n, d in G.items():
    allp = np.vstack([np.array(r) for r in d["rings"]])
    x0, y0 = allp.min(0) - 0.6; x1, y1 = allp.max(0) + 0.6
    xs = np.arange(x0, x1, px); ys = np.arange(y0, y1, px)
    X, Y = np.meshgrid(xs, ys); P = np.c_[X.ravel(), Y.ravel()]
    m = np.zeros(len(P), bool)
    for r in d["rings"]:
        m ^= Path(np.array(r)).contains_points(P)
    m = m.reshape(X.shape)
    res = {}
    for w in (0.40, 0.45):
        rad = int(round(w / 2 / px)); yy, xx = np.ogrid[-rad:rad + 1, -rad:rad + 1]; disk = xx * xx + yy * yy <= rad * rad
        op = nd.binary_opening(m, disk); lost = (m & ~op).sum() * px * px
        cl = nd.binary_closing(m, disk); filled = (cl & ~m).sum() * px * px
        # ignore sub-0.002 mm2 corner rounding (opening always rounds sharp corners)
        res[w] = (round(lost, 4), round(filled, 4))
    edt = nd.distance_transform_edt(m) * px
    sk = (edt >= nd.maximum_filter(edt, 5)) & m & (edt > 0.05)
    thinnest = 2 * np.percentile(edt[sk], 1)
    # letter gaps and counters are measured exactly on the B-rep in kerf_scripts/frame.py (a raster gap metric picks up inside corners)
    print(n, repr(d["text"]), "area %.2f mm2" % (m.sum() * px * px), "thinnest stroke ~%.2f mm" % thinnest,
          "| opening/closing lost/filled mm2 at 0.40:", res[0.40], "at 0.45:", res[0.45])

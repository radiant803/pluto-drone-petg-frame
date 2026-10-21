# Regenerate the print files with plain build123d (no Kerf needed):
#   python tools/export.py            -> out/pluto_frame.{stl,step}, out/motor_fit_coupon.{stl,step}
#   python tools/export.py frame      -> just the frame
# Edit src/p_params.py first (MOTOR_D, SQUEEZE, HOLE_COMP, HOLE_SQ, PILOT_D ...).
import os, sys, math
from build123d import *
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for f in ("p_params.py", "p_parts.py", "p_coupon.py"):
    exec(open(os.path.join(ROOT, "src", f), encoding="utf-8").read(), globals())
os.makedirs(os.path.join(ROOT, "out"), exist_ok=True)
want = sys.argv[1:] or ["frame", "coupon"]
parts = {"frame": ("pluto_frame", lambda: build_frame(with_labels=True)), "coupon": ("motor_fit_coupon", lambda: build_coupon(with_labels=True))}
for key in want:
    name, fn = parts[key]
    shape = fn()
    bb = shape.bounding_box()
    print("%-18s valid=%s  %.1f x %.1f x %.1f mm  %.2f g (solid PETG)" % (name, shape.is_valid, bb.size.X, bb.size.Y, bb.size.Z, shape.volume / 1000 * PETG_DENSITY))
    export_stl(shape, os.path.join(ROOT, "out", name + ".stl"), tolerance=0.01, angular_tolerance=0.1)
    export_step(shape, os.path.join(ROOT, "out", name + ".step"))

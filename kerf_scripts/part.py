import os
SRC = os.environ.get("PLUTO_FRAME_SRC", os.path.join(os.getcwd(), "src")).rstrip("/") + "/"   # absolute path to src/ (set PLUTO_FRAME_SRC, or run from the repo root)
import math
for _n in ("p_params.py", "p_parts.py"):
    exec(open(SRC + _n, encoding="utf-8").read(), globals())
# the printable frame alone, in its print pose (z = 0 on the bed, +Y = drone front), for export
requirement("Printable Pluto 1.2 frame: single watertight solid, flat on the bed, fits the A1 mini")
frame = build_frame(with_labels=True)
require_watertight(frame)
require(len(frame.solids()) == 1 and len(frame.shells()) == 1, "one solid, one shell", name="single solid, no voids")
bb = frame.bounding_box()
require(abs(bb.min.Z) < 1e-6 and max(bb.max.X - bb.min.X, bb.max.Y - bb.min.Y) < 175, "flat base, %.1f x %.1f x %.1f" % (bb.max.X - bb.min.X, bb.max.Y - bb.min.Y, bb.max.Z), name="print pose / bed fit")
result = frame

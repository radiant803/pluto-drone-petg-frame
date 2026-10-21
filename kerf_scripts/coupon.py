import os
SRC = os.environ.get("PLUTO_FRAME_SRC", os.path.join(os.getcwd(), "src")).rstrip("/") + "/"   # absolute path to src/ (set PLUTO_FRAME_SRC, or run from the repo root)
import math
for _n in ("p_params.py", "p_coupon.py"):
    exec(open(SRC + _n, encoding="utf-8").read(), globals())
CP_DIAMETERS = globals().get("CP_ROWS_OVERRIDE", CP_DIAMETERS)
CP_SQUEEZE = globals().get("CP_COLS_OVERRIDE", CP_SQUEEZE)
CP_COMP = globals().get("CP_COMP_OVERRIDE", CP_COMP)
CP_CORNER = globals().get("CP_CORNER_OVERRIDE", CP_CORNER)    # single-row strips (e.g. kerf_scripts/coupon_7p5.py) set this before exec'ing this file

requirement("Motor fit-test coupon: every sleeve is the frame's motor tube (wall, height, lip, bore clearance, crush ribs) for one motor diameter and squeeze")
requirement("Covers the coreless sizes sold for nano quads: 6.0, 7.0, 8.0, 8.5, 10.0 mm, at squeeze 0 / 0.1 / 0.2 / 0.3 mm")
requirement("Prints flat, no supports, labels readable (raised), motors can be pushed out from below")
requirement("Every sleeve carries the printed-hole shrink allowance CP_COMP (= HOLE_COMP, +0.15 from the 0720 fit test) on bore and ribs; corner label shows it")
coupon = build_coupon(with_labels=True)
plain = build_coupon(with_labels=False)
require_watertight(coupon)
require(len(coupon.solids()) == 1 and len(coupon.shells()) == 1, "one solid, no voids", name="single solid")
bb = coupon.bounding_box()
require(abs(bb.min.Z) < 1e-6 and bb.size.X < 175 and bb.size.Y < 175, "flat base, %.1f x %.1f x %.1f" % (bb.size.X, bb.size.Y, bb.size.Z), name="print pose / bed fit")
require_min_wall(plain, 0.8, name="min wall >= 0.8 mm (coupon without the raised labels)")
# the sleeve geometry is the frame tube's, by construction - check the numbers against the frame parameters
s_f = cp_sizes(MOTOR_D, SQUEEZE)
ok_f = abs(s_f["bore"] - (TUBE_BORE - HOLE_COMP + CP_COMP)) < 1e-9 and abs(s_f["rib_d"] - (RIB_D - HOLE_COMP + CP_COMP)) < 1e-9 and abs(s_f["lip_id"] - LIP_ID) < 1e-9 and CP_PLATE_T == LIP_T
require(ok_f, "sleeves use the frame-tube formulas (frame D%.1f / sq%.1f -> bore %.2f, ribs %.2f, lip %.2f at comp %.2f)" % (MOTOR_D, SQUEEZE, s_f["bore"], s_f["rib_d"], s_f["lip_id"], CP_COMP), name="sleeve matches the frame tube")
for i, d in enumerate(CP_DIAMETERS):
    for j, sq in enumerate(CP_SQUEEZE):
        x, y = cp_tube_xy(i, j); s = cp_sizes(d, sq)
        core = _cyl(x, y, CP_PLATE_T, s["rib_d"] - 0.05, 20.0)
        require_no_interference(coupon, core, name="D%.1f sq%.1f: motor core passes down to the lip" % (d, sq))
        if sq - CP_COMP > 1e-9:
            can = _cyl(x, y, CP_PLATE_T + 0.5, d, TUBE_H - CP_PLATE_T - 1.5)
            v = (coupon & can).volume
            require(v > 0, "D%.1f sq%.1f: ribs bite the can (overlap %.2f mm3)" % (d, sq, v), name="D%.1f sq%.1f grips" % (d, sq))
        require(s["lip_id"] <= d - 1.8, "D%.1f: lip %.1f holds the can" % (d, s["lip_id"]), name="D%.1f lip" % d)
# neighbours stay apart (no merged sleeves)
odmax = cp_sizes(max(CP_DIAMETERS), 0)["od"]
require(CP_PITCH_X - odmax >= 2.0 and CP_PITCH_Y - odmax >= 2.0, "gap between the largest sleeves %.1f mm" % (CP_PITCH_X - odmax), name="sleeves separate")
for s_, sol, sk in cp_labels():
    fs = sk.faces()
    gap = min([fs[a].distance_to(fs[b]) for a in range(len(fs)) for b in range(a + 1, len(fs))] or [9])
    require(gap >= 0.45, "label '%s': letter gap %.2f" % (s_, gap), name="label %s printable" % s_)
for i, d in enumerate(CP_DIAMETERS):
    for j, sq in enumerate(CP_SQUEEZE):
        s_ = cp_sizes(d, sq)
        require(abs(s_["bore"] - (d + BORE_CLEAR + CP_COMP)) < 1e-9 and abs(s_["rib_d"] - (d - sq + CP_COMP)) < 1e-9, "D%.1f sq%.1f: bore %.2f, ribs %.2f (allowance %+.2f)" % (d, sq, s_["bore"], s_["rib_d"], CP_COMP), name="D%.1f sq%.1f allowance" % (d, sq))
require(_cp_corner() == ("D" if abs(CP_COMP) < 1e-9 else "+" + ("%.2f" % CP_COMP).lstrip("0")), "corner label '%s' marks the allowance" % _cp_corner(), name="allowance marked on the card")
result = coupon

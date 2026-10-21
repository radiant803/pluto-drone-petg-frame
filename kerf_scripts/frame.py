import os
SRC = os.environ.get("PLUTO_FRAME_SRC", os.path.join(os.getcwd(), "src")).rstrip("/") + "/"   # absolute path to src/ (set PLUTO_FRAME_SRC, or run from the repo root)
import math
for _n in ("p_params.py", "p_parts.py", "p_asm.py"):
    exec(open(SRC + _n, encoding="utf-8").read(), globals())

frame = build_frame(with_labels=True)
board = board_standin()
dampers = damper_standins()
bat = battery_standin()

requirement("Replacement Pluto 1.2 frame in PETG: one printable piece, flat on the bed, no supports, lighter than ~9 g")
requirement("Primus V5 mounts exactly like the stock frame: 41 x 41 mm posts -> stock rubber dampers -> board -> canopy tabs -> stock M2 screws")
requirement("The board touches only the dampers, never the plastic frame (manual FAQ)")
requirement("0720 motors (7 x 20, fit-tested) press into crush-ribbed tubes and seat on a lip; the motor plug threads down the tube and out through the lip slot")
requirement("Pluto 600 battery (37 x 24 x 8) slides in from the front under the deck")
requirement("55 mm props clear the frame, the board/canopy and each other")
requirement("Engraved labels on each arm: port, prop letter, spin direction; front arrow on the deck")

require_watertight(frame)
require(len(frame.solids()) == 1, "frame is a single solid", name="single solid")
bb = frame.bounding_box()
require(bb.max.X - bb.min.X <= 175 and bb.max.Y - bb.min.Y <= 175 and bb.max.Z - bb.min.Z <= 175,
        "print envelope %.1f x %.1f x %.1f within the A1 mini bed" % (bb.max.X - bb.min.X, bb.max.Y - bb.min.Y, bb.max.Z - bb.min.Z), name="bed fit")
require(abs(bb.min.Z) < 1e-6, "flat bottom on z = 0 (bed / landing plane)", name="flat base")
mass = frame.volume / 1000 * PETG_DENSITY
require(mass <= 9.0, "solid-model mass %.2f g <= 9.0 g (PETG 1.27 g/cm3)" % mass, name="mass budget")
# wall thickness is checked on the identical body without the 0.4 mm engraving: the ray sampler reads every glyph edge as a ~0 mm wall.
# The engraving is checked on its own below (floor under the letters, letter gaps, counters; stroke width by tools/text_check.py).
frame_plain = build_frame(with_labels=False)
require_min_wall(frame_plain, 0.8, name="min wall >= 0.8 mm (2 perimeters at 0.4), body without the engraving")
require(abs(frame_plain.volume - frame.volume - 0) < 80, "engraving removes %.1f mm3, only from the top skin" % (frame_plain.volume - frame.volume), name="engraving is shallow")
require(len(frame.shells()) == 1, "no hidden voids (single shell): every engraving opens to the top", name="no internal voids")
require(ARM_TOP - ENGRAVE >= 0.8 - 1e-9, "arm skin under the letters %.1f mm" % (ARM_TOP - ENGRAVE), name="floor under the letters")
for n in MOTORS:
    sk = Text(label_text(n), font_size=LABEL_SIZE, font=LABEL_FONT, font_style=FontStyle.BOLD, align=(Align.CENTER, Align.CENTER))
    fs = sk.faces(); bbl = sk.bounding_box()
    gap = min(fs[i].distance_to(fs[j]) for i in range(len(fs)) for j in range(i + 1, len(fs)))
    cnt = min([min(w.bounding_box().size.X, w.bounding_box().size.Y) for fc in fs for w in fc.inner_wires()] or [9])
    require(gap >= 0.45 and cnt >= 0.8, "%s '%s': letter gap %.2f, smallest counter %.2f mm" % (n, label_text(n), gap, cnt), name="%s label printable" % n)
    require(bbl.size.Y <= ARM_W - 2.0 and bbl.size.X <= (R_MOTOR - TUBE_OD / 2) - (R_POST + POST_D / 2 + 1.2) - 1.0,
            "%s label %.1f x %.1f fits the arm top %.1f wide between post and tube" % (n, bbl.size.X, bbl.size.Y, ARM_W), name="%s label fits" % n)

# board mounting
require_dimension(HOLE_SQ, 41.0, tol=0.01, name="post pattern 41.0 x 41.0 mm (Primus V5 holes)")
require(POST_D >= DAMPER_FLANGE_D - 0.3, "post top %.1f supports the %.1f damper flange" % (POST_D, DAMPER_FLANGE_D), name="damper seat")
require_clearance(board, frame, min=1.0, name="board clears the frame (touches only the dampers)")
require_no_interference(frame, *dampers, name="dampers sit on the posts without cutting into the frame")

# motors
for n in MOTORS:
    require_no_interference(frame, motor_standin(n, d=RIB_D - 0.05), name="%s: motor core passes the tube down to the lip" % n)
    require_no_interference(frame, connector_standin(n), name="%s: motor plug threads through the tube and lip" % n)
# the tube must be exactly the 7.0 / 0.2 / +0.15 sleeve that passed the fit test (docs/TOLERANCES.md)
TESTED = {"bore": 7.55, "rib_d": 6.95, "lip_id": 5.1, "wall": 0.9, "height": 8.5, "lip_t": 1.0, "rib_w": 0.9}
ours = {"bore": TUBE_BORE, "rib_d": RIB_D, "lip_id": LIP_ID, "wall": TUBE_WALL, "height": TUBE_H, "lip_t": LIP_T, "rib_w": RIB_W}
require(all(abs(ours[k] - TESTED[k]) < 1e-6 for k in TESTED), "motor tube = tested sleeve: " + ", ".join("%s %.2f" % (k, ours[k]) for k in TESTED), name="motor tube matches the fit-tested sleeve")
require(LIP_ID < MOTOR_D - 1.0, "lip ID %.1f holds the %.1f can" % (LIP_ID, MOTOR_D), name="motor seat lip")
require(PLUG_PASSES_LIP or WIRE_SLOT_W >= PLUG_W + 0.6, "plug %.1f x %.1f: %s" % (PLUG_L, PLUG_W, "passes the lip hole" if PLUG_PASSES_LIP else "drops through lip hole + %.1f mm slot to the tube centre" % WIRE_SLOT_W), name="plug exit")

# battery
require_no_interference(frame, bat, name="battery sits in the bay")
require_no_interference(frame, battery_path(), name="battery slides out through the open front")
require(DECK_Z0 - (RAIL_T + BAT_T) >= 0.4, "battery top gap %.2f mm under the deck" % (DECK_Z0 - RAIL_T - BAT_T), name="bay height")

# props
props = [prop_disc(n) for n in MOTORS]
for n, p in zip(MOTORS, props):
    require_clearance(p, frame, min=8.0, name="%s prop clears the frame" % n)
    require_clearance(p, board, min=3.0, name="%s prop clears the board" % n)
    require_clearance(p, canopy_envelope(), min=1.0, name="%s prop clears the canopy envelope" % n)
require_clearance(props[0], props[1], min=20.0, name="front props tip clearance")
require_clearance(props[0], props[2], min=20.0, name="left props tip clearance")

result = frame
show(frame, name="frame")
show(board, name="primus_v5"); [show(d, name="damper_%d" % i) for i, d in enumerate(dampers)]
show(bat, name="battery")
for n in MOTORS:
    show(motor_standin(n), name="motor_" + n)

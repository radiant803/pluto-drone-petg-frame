import math
# Pluto 1.2 replacement frame - every dimension in one place (mm, grams)
# World frame: +Y = drone FRONT (board arrow / Wi-Fi module end), +X = right, Z up, z = 0 = print bed / ground.
# Sources: Pluto 1.2 manual (DronaAviation/Resources, Feb 2026), dronaaviation.com/hardware/parts, top-view render in the manual
# (scaled with the 48 mm board, cross-checked with the 55 mm prop: 54.0 mm measured).

# ---- bought parts (confirmed) ----
BOARD = 48.0          # Primus V5 48 x 48 (manual spec page)
BOARD_T = 1.6         # PCB thickness (assumed standard)
BOARD_HOLE_D = 3.6    # damper holes in the board (manual)
BOARD_G = 10.4
HOLE_SQ = 41.0        # board hole pattern, square (measured from the render: 40.7-41.2)
MOTOR_D = 7.0         # 0720 coreless, 7 x 20 (fit test: the 7.0 / 0.2 / +0.15 sleeve fits; Drona lists 0720 for Primus)
MOTOR_L = 20.0
MOTOR_SHAFT_D, MOTOR_SHAFT_L = 1.0, 5.0
MOTOR_G = 3.2         # typical 0720 mass (not published by Drona; 8520 ~4.5)
MOTOR_R, MOTOR_I0, MOTOR_KV = 0.8, 0.18, 50000 / 3.7   # 0720 coil+brush ohm, no-load A, rpm/V (dronaaviation.com/hardware/parts)
PROP_D = 55.0         # bi-blade 55 mm (manual)
PROP_HUB_H = 4.5      # prop hub height above the can top
BAT_L, BAT_W, BAT_T, BAT_G = 37.0, 24.0, 8.0, 16.0   # Pluto 600 (parts page)
DAMPER_FLANGE_D, DAMPER_LOW_H, DAMPER_H = 5.6, 1.4, 4.6   # rubber FC grommet (kit part; flange under the PCB = 1.4)
SCREW_D = 2.0         # kit metal screw, M2 (self-taps into the post)

# ---- motor layout (measured from the manual's scaled top view) ----
MOTOR_XY = 46.5       # motor centres at (+-46.5, +-46.5): 93 x 93 square, 131.5 mm diagonal
# port silkscreen on the Primus V5 (read from the render) and the manual's prop figure
MOTORS = {            # name: (sx, sy, port, prop, spin)
    "FL": (-1, 1, "M5", "A", "CW"),
    "FR": (1, 1, "M8", "B", "CCW"),
    "RL": (-1, -1, "M6", "B", "CCW"),
    "RR": (1, -1, "M7", "A", "CW"),
}

# ---- frame ----
PETG_DENSITY = 1.27
# motor tube
TUBE_H = 8.5
TUBE_WALL = 0.9
# tube sizes follow the motor: set MOTOR_D, SQUEEZE and HOLE_COMP from the fit test (out/motor_fit_coupon.stl, docs/TOLERANCES.md)
SQUEEZE = 0.2         # crush-rib interference on the diameter (fit-test column that grips best)
BORE_CLEAR = 0.4      # bore between the ribs = motor + 0.4
HOLE_COMP = 0.15      # printed-hole shrink allowance on the bore and the rib circle (the bare 0720 test sleeve with +0.15 fits)
TUBE_BORE = MOTOR_D + BORE_CLEAR + HOLE_COMP   # 7.55 for the 0720
RIB_D = MOTOR_D - SQUEEZE + HOLE_COMP          # 6.95 for the 0720: diameter across the 4 crush ribs
RIB_W = 0.9
LIP_T = 1.0           # bottom lip the motor sits on
LIP_ID = min(6.6, MOTOR_D - 1.9)      # 5.1 for the 0720 (6.6 for an 8520, where the plug passes the lip on its own)
PLUG_L, PLUG_W = 5.0, 3.3             # motor plug housing (PicoBlade-style 2-pin)
PLUG_PASSES_LIP = math.hypot(PLUG_L, PLUG_W) < LIP_ID - 0.3
# side slot from the tube into the arm channel; when the plug can't pass the lip hole the slot runs to the tube centre and is plug-wide,
# so the plug drops through (lip hole + slot) and the lead leaves sideways; the can still sits on the rest of the lip ring
WIRE_SLOT_W = 2.6 if PLUG_PASSES_LIP else PLUG_W + 0.7   # 4.0: ~0.35 mm a side on the plug after print shrink
WIRE_SLOT_H = 2.6
TUBE_OD = TUBE_BORE + 2 * TUBE_WALL
# arms: Pi section (top plate for the engraved labels, wire channel underneath, open to the bed)
ARM_W = 6.2
ARM_H = 4.8
ARM_TOP = 1.2
ARM_WALL = 0.9
ENGRAVE = 0.4
LABEL_SIZE = 5.0      # font size -> cap height ~3.6 mm
LABEL_FONT, LABEL_BOLD = "Arial", True
# body / battery bay (battery slides in from the front, wires trail at the front)
BAY_W = 24.8
BAY_H = 8.6
BAY_REAR = -20.0      # inner face of the rear stop
BAY_FRONT = 21.5      # walls end here (open front)
BAY_WALL = 1.2
RAIL_W = 3.2          # floor rails under the battery edges
RAIL_T = 1.0
DECK_Z0 = RAIL_T + BAY_H          # 9.6
DECK_T = 1.6
DECK_TOP = DECK_Z0 + DECK_T       # 11.2
XBAR_W = 3.4
EDGEBAR_W = 3.0
HUB_D = 10.5
GUSSET = 4.0         # deck gusset leg (X bar / edge bar notch)
# damper posts (same scheme as the stock frame: post -> rubber damper -> board -> canopy tab -> screw)
POST_D = 5.4
POST_ABOVE_DECK = 3.0
POST_TOP = DECK_TOP + POST_ABOVE_DECK   # 14.2
PILOT_D = 1.8         # M2 self-tapping pilot (through)
BOARD_Z0 = POST_TOP + DAMPER_LOW_H      # board underside 15.6
# battery-lead holder: hook in front of the LEFT bay wall (the V5 battery plug sits on the board's left edge); press the two leads into the slot
HOLDER_X0, HOLDER_X1 = -17.0, -(BAY_W / 2) - 0.6
HOLDER_L, HOLDER_H, HOLDER_SLOT = 4.2, 7.0, 1.8   # slot runs across the hook (along X) so it never reaches the front-left arm

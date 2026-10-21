# Flat vented canopy for the Pluto frame (out/pluto_canopy_flat.stl). Needs p_params.py and p_asm.py exec'd first.
# Attaches to the stock screws and dampers; print roof-down, no supports, no brim. build_canopy() -> canopy_print_pose().
# Printed PETG canopy for the Pluto frame (needs p_params.py exec'd first)
# Attaches like the stock canopy: its 4 ears are clamped between the stock M2 screw heads and the top of the stock rubber
# dampers, so it uses only the hardware already on the drone and the board stays isolated on its dampers.
# Shape: a vented roof over the Primus V5 with a short stiffening rim, carried on 4 hollow towers (one per screw: the
# screwdriver reaches the screw through the tower). Left/right/front/rear stay open below the rim: motor plugs, battery
# plug, power switch, USB-C and the boot button are all on the board edges.
# Installed frame (same as the frame: +Y front, z up). Print pose = upside down (roof on the bed), see canopy_print_pose().

DAMPER_TOP = POST_TOP + DAMPER_H            # 18.8: top face of the damper's upper flange
BOARD_TOP = BOARD_Z0 + BOARD_T              # 17.2
CANOPY_CLEAR = 10.0       # free height above the board top (tallest part on the V5: a vertical 3-pin header, ~7-8 mm)
CANOPY_T = 0.9            # roof thickness
CANOPY_W, CANOPY_L = 46.0, 48.0             # roof footprint (x, y): covers the board, stays clear of the props
CANOPY_R = 4.0            # roof corner radius
RIM_H, RIM_T = 2.5, 0.9   # stiffening rim hanging under the roof edge
EAR_T = 1.0               # ear clamped between screw head and damper (like the stock canopy tab)
EAR_D = 7.0               # ear diameter (damper flange 5.6)
EAR_HOLE = 2.4            # M2 clearance
SCREW_HEAD_D = 4.0        # M2 pan/cross head (assumed; typical 3.8-4.0)
TOWER_ID = SCREW_HEAD_D + 1.2               # 5.2: head + screwdriver clearance
TOWER_WALL = 0.9
TOWER_OD = TOWER_ID + 2 * TOWER_WALL        # 7.0
VENT_D, VENT_PITCH = 5.6, 7.6               # roof vents (light + airflow + LEDs visible)
ROOF_BOT = BOARD_TOP + CANOPY_CLEAR         # 27.2
ROOF_TOP = ROOF_BOT + CANOPY_T              # 28.0

def _ccyl(x, y, z0, d, h):
    return Pos(x, y, z0) * Cylinder(d / 2, h, align=(Align.CENTER, Align.CENTER, Align.MIN))

def _rounded_rect(w, l, r, z0, h):
    b = Pos(0, 0, z0 + h / 2) * Box(w, l, h)
    return fillet(b.edges().filter_by(Axis.Z), radius=r)

def screw_xy():
    return [(sx * HOLE_SQ / 2, sy * HOLE_SQ / 2) for sx in (-1, 1) for sy in (-1, 1)]

def canopy_vents():
    """vent hole centres on a staggered grid, kept clear of the towers, the rim and the front arrow window"""
    pts = []
    ny = int(CANOPY_L / VENT_PITCH) + 2
    for j in range(-ny, ny + 1):
        y = j * VENT_PITCH * 0.866
        off = (VENT_PITCH / 2) if j % 2 else 0.0
        for i in range(-8, 9):
            x = i * VENT_PITCH + off
            if abs(x) > CANOPY_W / 2 - RIM_T - VENT_D / 2 - 1.6 or abs(y) > CANOPY_L / 2 - RIM_T - VENT_D / 2 - 1.6:
                continue
            if any(math.hypot(x - sx, y - sy) < TOWER_OD / 2 + VENT_D / 2 + 1.2 for sx, sy in screw_xy()):
                continue
            if abs(x) < 6.0 and y > 8.0:          # keep the front for the arrow window
                continue
            pts.append((x, y))
    return pts

def canopy_arrow_window():
    # through-cut arrow at the front of the roof (points to the front: line it up with the deck arrow)
    pts = [(0, 21.0), (-4.2, 15.5), (-1.5, 15.5), (-1.5, 10.0), (1.5, 10.0), (1.5, 15.5), (4.2, 15.5)]
    return Pos(0, 0, ROOF_BOT - 1) * extrude(Polygon(*pts, align=None), CANOPY_T + 2, dir=(0, 0, 1))

def build_canopy():
    roof = _rounded_rect(CANOPY_W, CANOPY_L, CANOPY_R, ROOF_BOT, CANOPY_T)
    rim_outer = _rounded_rect(CANOPY_W, CANOPY_L, CANOPY_R, ROOF_BOT - RIM_H, RIM_H + 0.1)
    rim_inner = _rounded_rect(CANOPY_W - 2 * RIM_T, CANOPY_L - 2 * RIM_T, CANOPY_R - RIM_T, ROOF_BOT - RIM_H - 1, RIM_H + 1.05)
    rim = rim_outer - rim_inner
    c = roof.fuse(rim).clean()
    towers = []
    for (x, y) in screw_xy():
        # tower from the ear bottom (on the damper) up through the roof
        towers.append(_ccyl(x, y, DAMPER_TOP, TOWER_OD, ROOF_TOP - DAMPER_TOP))
        towers.append(_ccyl(x, y, DAMPER_TOP, EAR_D, EAR_T))
    c = c.fuse(*towers).clean()
    for (x, y) in screw_xy():
        c = c - _ccyl(x, y, DAMPER_TOP + EAR_T, TOWER_ID, ROOF_TOP - DAMPER_TOP)   # screwdriver / head well, open through the roof
        c = c - _ccyl(x, y, DAMPER_TOP - 1, EAR_HOLE, EAR_T + 2)                     # M2 clearance through the ear
    # 45 deg chamfer ring where the well meets the ear: in the upside-down print pose the ear is printed over the well, so this
    # cuts its unsupported overhang from 1.4 mm to ~0.9 mm; it starts 0.15 mm outside the screw head, so the head still seats flat
    ch_r0 = SCREW_HEAD_D / 2 + 0.15
    ch_h = TOWER_ID / 2 - ch_r0
    fills = []
    for (x, y) in screw_xy():
        ring = _ccyl(x, y, DAMPER_TOP + EAR_T - 0.01, TOWER_ID + 0.02, ch_h + 0.01)
        cone = Pos(x, y, DAMPER_TOP + EAR_T - 0.02) * Cone(ch_r0, TOWER_ID / 2 + 0.02, ch_h + 0.04, align=(Align.CENTER, Align.CENTER, Align.MIN))
        fills.append(ring - cone)
    c = c.fuse(*fills).clean()
    for (x, y) in canopy_vents():
        c = c - _ccyl(x, y, ROOF_BOT - 1, VENT_D, CANOPY_T + 2)
    c = c - canopy_arrow_window()
    return c

def canopy_print_pose(c):
    """upside down: roof face on the bed (z = 0), towers and ears pointing up"""
    flipped = Rot(180, 0, 0) * c
    return Pos(0, 0, -flipped.bounding_box().min.Z) * flipped

# --- keep-out volumes on the board that the canopy must not touch -------------------------------------------------
EDGE_PART_H = 6.0         # edge band: side-entry motor connectors (~4-5 mm), switch, Wi-Fi module (~3-4 mm)
TALL_PART_H = 8.5         # board body: allows for the vertical 3-pin header (~7-8 mm, rear right, ~16 mm in from the edge)
def board_component_envelope():
    """conservative keep-out for the board's top-side parts: TALL_PART_H over the board body (|x|,|y| < 20), EDGE_PART_H
    out to the board edge; the four screw corners (mounting ears, no parts) excluded"""
    env = Pos(0, 0, BOARD_TOP + TALL_PART_H / 2) * Box(40.0, 40.0, TALL_PART_H)
    env = env.fuse(Pos(0, 0, BOARD_TOP + EDGE_PART_H / 2) * Box(BOARD, BOARD, EDGE_PART_H)).clean()
    for (x, y) in screw_xy():
        env = env - Pos(x, y, BOARD_TOP + CANOPY_CLEAR / 2) * Box(9.0, 9.0, CANOPY_CLEAR + 2)
    return env

def edge_access_keepouts():
    """side-entry motor plugs, battery plug, switch, USB-C plug and boot button: reachable from outside, nothing in the way"""
    h = 6.0                                       # plug / button height above the board top
    k = []
    for sx in (-1, 1):                            # left / right edges: motor plugs + battery plug + switch, plugs stick out ~6 mm
        k.append(Pos(sx * (BOARD / 2 + 3.0), 0, BOARD_TOP + h / 2) * Box(12.0, 32.0, h))   # connectors at y ~ +-13
    k.append(Pos(0, -(BOARD / 2 + 4.0), BOARD_TOP + h / 2) * Box(12.0, 12.0, h))     # USB-C plug at the rear
    k.append(Pos(0, (BOARD / 2 + 4.0), BOARD_TOP + h / 2) * Box(20.0, 12.0, h))      # boot button / Wi-Fi end at the front
    return k

def screw_head_standins():
    # M2 head 4.0 x 1.4 on top of each ear
    return [_ccyl(x, y, DAMPER_TOP + EAR_T, SCREW_HEAD_D, 1.4) for (x, y) in screw_xy()]

def screwdriver_standins():
    # a 3 mm cross-point driver straight down onto each screw, from well above the roof
    return [_ccyl(x, y, DAMPER_TOP + EAR_T + 1.4, 3.0, 40.0) for (x, y) in screw_xy()]

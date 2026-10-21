# Pluto 1.2 frame - printed part (single piece, prints in this pose: z = 0 on the bed, no supports)
# needs p_params.py exec'd first

def _arm_loc(theta, r):
    return Pos(r * math.cos(math.radians(theta)), r * math.sin(math.radians(theta)), 0) * Rot(0, 0, theta)

def _radial_box(theta, r0, r1, w, z0, z1):
    """box along the radial direction theta from radius r0 to r1, width w, z0..z1"""
    return _arm_loc(theta, (r0 + r1) / 2) * Pos(0, 0, (z0 + z1) / 2) * Box(r1 - r0, w, z1 - z0)

def motor_xy(name):
    sx, sy = MOTORS[name][0], MOTORS[name][1]
    return sx * MOTOR_XY, sy * MOTOR_XY

def theta_of(name):
    sx, sy = MOTORS[name][0], MOTORS[name][1]
    return math.degrees(math.atan2(sy, sx))

R_MOTOR = MOTOR_XY * math.sqrt(2)
R_POST = HOLE_SQ / 2 * math.sqrt(2)
WX = BAY_W / 2 + BAY_WALL            # outer face of a bay wall

def deck_gussets(g=GUSSET):
    # fill the 45 deg notch between each X bar and the front/rear edge bar (a knife edge otherwise) with a triangle;
    # both legs end 0.3 mm inside the bars so every new edge crosses a bar edge transversally (no tangent slivers)
    out = []
    ye = HOLE_SQ / 2 - EDGEBAR_W / 2                 # inner edge of the edge bar
    c = XBAR_W / 2 * math.sqrt(2)                     # FL X-bar edge line: x + y = c
    r2 = math.sqrt(2)
    for n in MOTORS:
        sx, sy = MOTORS[n][0], MOTORS[n][1]
        ax, ay = sx * (ye - c), sy * ye               # notch apex
        d1 = (-sx, 0.0); d2 = (-sx / r2, -sy / r2)    # along the edge bar / along the X bar, into the air wedge
        n1 = (0.0, sy); n2 = (sx / r2, -sy / r2)      # into the edge bar / into the X bar
        bx, by = d1[0] + d2[0], d1[1] + d2[1]; bl = math.hypot(bx, by); bx, by = bx / bl, by / bl
        pts = [(ax - 1.0 * bx, ay - 1.0 * by),
               (ax + g * d1[0] + 0.3 * n1[0], ay + g * d1[1] + 0.3 * n1[1]),
               (ax + g * d2[0] + 0.3 * n2[0], ay + g * d2[1] + 0.3 * n2[1])]
        out.append(Pos(0, 0, DECK_Z0) * extrude(Polygon(*pts, align=None), DECK_T, dir=(0, 0, 1)))   # explicit dir: mirrored corners wind clockwise
    return out

def body_blank():
    parts = []
    # bay side walls (up through the deck) and rear stop
    for sx in (-1, 1):
        parts.append(Pos(sx * (BAY_W / 2 + BAY_WALL / 2), (BAY_REAR - BAY_WALL + BAY_FRONT) / 2, DECK_TOP / 2)
                     * Box(BAY_WALL, BAY_FRONT - BAY_REAR + BAY_WALL, DECK_TOP))
    parts.append(Pos(0, BAY_REAR - BAY_WALL / 2, DECK_TOP / 2) * Box(2 * WX, BAY_WALL, DECK_TOP))
    # deck: X bars post to post, front/rear edge bars (they rest on the bay walls), centre hub
    for th in (45, 135):
        parts.append(Pos(0, 0, DECK_Z0 + DECK_T / 2) * Rot(0, 0, th) * Box(2 * R_POST, XBAR_W, DECK_T))
    for sy in (-1, 1):
        parts.append(Pos(0, sy * HOLE_SQ / 2, DECK_Z0 + DECK_T / 2) * Box(HOLE_SQ, EDGEBAR_W, DECK_T))
    parts.append(Pos(0, 0, DECK_Z0) * Cylinder(HUB_D / 2, DECK_T, align=(Align.CENTER, Align.CENTER, Align.MIN)))
    parts += deck_gussets()
    # damper posts, full height so they also stand on the bed
    for n in MOTORS:
        sx, sy = MOTORS[n][0], MOTORS[n][1]
        parts.append(Pos(sx * HOLE_SQ / 2, sy * HOLE_SQ / 2, 0) * Cylinder(POST_D / 2, POST_TOP, align=(Align.CENTER, Align.CENTER, Align.MIN)))
    # battery-lead holder at the front of the LEFT wall (the Primus V5 battery plug is on the board's left edge)
    parts.append(Pos((HOLDER_X0 + HOLDER_X1) / 2, BAY_FRONT + HOLDER_L / 2 - 0.3, HOLDER_H / 2) * Box(HOLDER_X1 - HOLDER_X0, HOLDER_L + 0.3, HOLDER_H))
    return parts

def arm_blank(n):
    th = theta_of(n)
    mx, my = motor_xy(n)
    arm = _radial_box(th, 16.0, R_MOTOR, ARM_W, 0, ARM_H)
    tube = Pos(mx, my, 0) * Cylinder(TUBE_OD / 2, TUBE_H, align=(Align.CENTER, Align.CENTER, Align.MIN))
    return [arm, tube]

def arm_cuts(n):
    th = theta_of(n)
    mx, my = motor_xy(n)
    ch_w = ARM_W - 2 * ARM_WALL
    ch_h = ARM_H - ARM_TOP
    cuts = []
    # wire channel under the arm (open to the bed): outer segment tube -> post, and a short root pocket that stops 0.5 mm clear of the bay wall
    r_root0 = (BAY_W / 2 + BAY_WALL + 0.5) * math.sqrt(2) + ch_w / 2
    cuts.append(_radial_box(th, r_root0, R_POST - POST_D / 2 - 1.2, ch_w, -1.0, ch_h))
    cuts.append(_radial_box(th, R_POST + POST_D / 2 + 1.2, R_MOTOR - TUBE_OD / 2 + 0.05, ch_w, -1.0, ch_h))
    # motor bore above the lip, lip hole, wire slot from the bore into the channel
    cuts.append(Pos(mx, my, LIP_T) * Cylinder(TUBE_BORE / 2, TUBE_H, align=(Align.CENTER, Align.CENTER, Align.MIN)))
    cuts.append(Pos(mx, my, -1) * Cylinder(LIP_ID / 2, TUBE_H + 2, align=(Align.CENTER, Align.CENTER, Align.MIN)))
    cuts.append(_radial_box(th, R_MOTOR - TUBE_OD / 2 - 1.0, (R_MOTOR - LIP_ID / 2 + 0.5) if PLUG_PASSES_LIP else (R_MOTOR + 0.3), WIRE_SLOT_W, -1.0, WIRE_SLOT_H))
    return cuts

def ribs(n):
    mx, my = motor_xy(n)
    out = []
    for k in range(4):
        a = 45 + 90 * k + theta_of(n)
        r0, r1 = RIB_D / 2, TUBE_BORE / 2 + 0.3
        out.append(Pos(mx, my, 0) * Rot(0, 0, a) * Pos((r0 + r1) / 2, 0, (LIP_T + TUBE_H - 0.8) / 2) * Box(r1 - r0, RIB_W, TUBE_H - 0.8 - LIP_T + 0.02))
    return out

def label_text(n):
    port, prop, spin = MOTORS[n][2], MOTORS[n][3], MOTORS[n][4]
    return f"{port} {prop} {spin}"

def label_cut(n):
    th = theta_of(n)
    sx = MOTORS[n][0]
    ang = th if sx > 0 else th + 180          # every label reads with its top towards the front
    r_mid = (R_POST + POST_D / 2 + R_MOTOR - TUBE_OD / 2) / 2
    sk = Text(label_text(n), font_size=LABEL_SIZE, font=LABEL_FONT, font_style=FontStyle.BOLD if LABEL_BOLD else FontStyle.REGULAR, align=(Align.CENTER, Align.CENTER))
    txt = extrude(sk, ENGRAVE + 0.5, dir=(0, 0, 1))
    return Pos(r_mid * math.cos(math.radians(th)), r_mid * math.sin(math.radians(th)), ARM_H - ENGRAVE) * Rot(0, 0, ang) * txt

def hub_arrow_cut():
    # board-arrow match mark: arrow pointing to the FRONT (+Y) on the deck hub
    pts = [(0, 5.0), (-3.4, 0.6), (-1.3, 0.6), (-1.3, -4.6), (1.3, -4.6), (1.3, 0.6), (3.4, 0.6)]
    sk = Polygon(*pts, align=None)
    return Pos(0, 0, DECK_TOP - ENGRAVE) * extrude(sk, ENGRAVE + 0.5, dir=(0, 0, 1))

def build_frame(with_labels=True):
    blank = body_blank()
    for n in MOTORS:
        blank += arm_blank(n)
    f = blank[0]
    f = f.fuse(*blank[1:]).clean()
    # battery bay cavity (also trims the arm roots flush with the walls)
    cav = Pos(0, (BAY_REAR + 40) / 2, DECK_Z0 / 2 - 0.5) * Box(BAY_W, 40 - BAY_REAR, DECK_Z0 + 1)
    cuts = [cav]
    for n in MOTORS:
        cuts += arm_cuts(n)
    # damper-post pilot holes (through) and the battery-lead slot in the holder
    for n in MOTORS:
        sx, sy = MOTORS[n][0], MOTORS[n][1]
        cuts.append(Pos(sx * HOLE_SQ / 2, sy * HOLE_SQ / 2, -1) * Cylinder(PILOT_D / 2, POST_TOP + 2, align=(Align.CENTER, Align.CENTER, Align.MIN)))
    y_slot = BAY_FRONT - 0.3 + HOLDER_L / 2 + 0.3          # slot centre: 1.2 mm walls front and back
    cuts.append(Pos((HOLDER_X0 - 0.5 + HOLDER_X1 + 0.5) / 2, y_slot, HOLDER_H) * Box(HOLDER_X1 - HOLDER_X0 + 1.0, HOLDER_SLOT, 2 * (HOLDER_H - 2.0)))
    # lightening windows in the bay walls, between the arm roots
    for sx in (-1, 1):
        cuts.append(Pos(sx * (BAY_W / 2 + BAY_WALL / 2), 0, (2.0 + 7.6) / 2) * Box(BAY_WALL + 2, 16.0, 7.6 - 2.0))
    cuts.append(Pos(0, BAY_REAR - BAY_WALL / 2, (2.0 + 7.6) / 2) * Box(BAY_W - 6.0, BAY_WALL + 2, 7.6 - 2.0))   # rear-stop window
    for c in cuts:
        f = f - c
    # battery floor rails and the crush ribs go back in after the cavity / bores
    adds = []
    for sx in (-1, 1):
        adds.append(Pos(sx * (BAY_W / 2 - RAIL_W / 2 + 0.1), (BAY_REAR + BAY_FRONT) / 2, RAIL_T / 2) * Box(RAIL_W + 0.2, BAY_FRONT - BAY_REAR, RAIL_T))
    for n in MOTORS:
        adds += ribs(n)
    f = f.fuse(*adds).clean()
    if with_labels:
        for n in MOTORS:
            f = f - label_cut(n)
        f = f - hub_arrow_cut()
    return f

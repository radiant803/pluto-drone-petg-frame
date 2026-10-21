# Motor fit-test coupon: one sleeve per (motor diameter, squeeze), each a copy of the frame's motor tube
# (same wall, height, lip, bore clearance and crush ribs, printed upright the same way), so the sleeve that grips
# best gives MOTOR_D and SQUEEZE for p_params.py directly.  Needs p_params.py exec'd first.

CP_DIAMETERS = [6.0, 7.0, 8.0, 8.5, 10.0]       # 0615, 0716/0720, 0820, 8520, 1020 coreless motors (all sold for nano quads)
CP_SQUEEZE = [0.0, 0.1, 0.2, 0.3]               # crush-rib interference on the diameter; 0.0 = slip-fit reference
CP_PITCH_X, CP_PITCH_Y = 15.0, 15.0
CP_LABEL_W, CP_LABEL_H = 14.0, 9.0              # left column (diameters) / top row (squeeze) for the raised labels
CP_MARGIN = 2.5
CP_PLATE_T = LIP_T                              # the plate is the lip, exactly as in the frame tube
CP_TEXT = 5.0
CP_TEXT_H = 0.6                                 # raised text height
CP_COMP = HOLE_COMP                             # shrink allowance on bore + ribs (a test piece can override it)
CP_CORNER = None                                # corner header text (default "D")
CP_LATTICE = True                               # open base: bars through the rows/columns + rim + label pads (the sleeves are unchanged)
CP_BAR_W = 3.0
CP_RIM_W = 2.5
CP_PAD_MARGIN = 1.2

def cp_tube_xy(i, j):
    """centre of the sleeve for diameter row i (0 = top) and squeeze column j"""
    ox = -_cp_w() / 2 + CP_MARGIN + CP_LABEL_W + CP_PITCH_X / 2
    oy = _cp_h() / 2 - CP_MARGIN - CP_LABEL_H - CP_PITCH_Y / 2
    return ox + j * CP_PITCH_X, oy - i * CP_PITCH_Y

def _cp_w():
    return 2 * CP_MARGIN + CP_LABEL_W + len(CP_SQUEEZE) * CP_PITCH_X

def _cp_h():
    return 2 * CP_MARGIN + CP_LABEL_H + len(CP_DIAMETERS) * CP_PITCH_Y

def cp_sizes(d, sq):
    bore = d + BORE_CLEAR + CP_COMP
    return {"bore": bore, "od": bore + 2 * TUBE_WALL, "rib_d": d - sq + CP_COMP, "lip_id": min(6.6, d - 1.9)}

def _cyl(x, y, z0, dia, h):
    return Pos(x, y, z0) * Cylinder(dia / 2, h, align=(Align.CENTER, Align.CENTER, Align.MIN))

def _cp_corner():
    """corner header: "D" for an uncompensated card, "+.15" style when a shrink allowance is built in"""
    if CP_CORNER: return CP_CORNER
    return "D" if abs(CP_COMP) < 1e-9 else "+" + ("%.2f" % CP_COMP).lstrip("0")

def cp_labels():
    out = []
    def txt(s, x, y, size=CP_TEXT):
        sk = Text(s, font_size=size, font=LABEL_FONT, font_style=FontStyle.BOLD, align=(Align.CENTER, Align.CENTER))
        out.append((s, Pos(x, y, CP_PLATE_T - 0.01) * extrude(sk, CP_TEXT_H + 0.01, dir=(0, 0, 1)), sk))
    xl = -_cp_w() / 2 + CP_MARGIN + CP_LABEL_W / 2
    for i, d in enumerate(CP_DIAMETERS):
        txt("%.1f" % d, xl, cp_tube_xy(i, 0)[1])
    yt = _cp_h() / 2 - CP_MARGIN - CP_LABEL_H / 2
    for j, sq in enumerate(CP_SQUEEZE):
        txt("%.1f" % sq if sq else "0", cp_tube_xy(0, j)[0], yt)
    txt(_cp_corner(), xl, yt)
    return out

def build_coupon(with_labels=True):
    w, h = _cp_w(), _cp_h()
    plate = Pos(0, 0, CP_PLATE_T / 2) * Box(w, h, CP_PLATE_T)
    plate = fillet(plate.edges().filter_by(Axis.Z), radius=3.0)
    if CP_LATTICE:
        plate = plate - Pos(0, 0, CP_PLATE_T / 2) * Box(w - 2 * CP_RIM_W, h - 2 * CP_RIM_W, CP_PLATE_T + 2)
        web = []
        for i in range(len(CP_DIAMETERS)):          # row bars, rim to rim (pass under the diameter labels)
            web.append(Pos(0, cp_tube_xy(i, 0)[1], CP_PLATE_T / 2) * Box(w - CP_RIM_W, CP_BAR_W, CP_PLATE_T))
        for j in range(len(CP_SQUEEZE)):            # column bars, rim to rim (pass under the squeeze labels)
            web.append(Pos(cp_tube_xy(0, j)[0], 0, CP_PLATE_T / 2) * Box(CP_BAR_W, h - CP_RIM_W, CP_PLATE_T))
        for s_, sol, sk in cp_labels():             # a pad under every label
            bb = sol.bounding_box()
            x0, x1, y0, y1 = bb.min.X - CP_PAD_MARGIN, bb.max.X + CP_PAD_MARGIN, bb.min.Y - CP_PAD_MARGIN, bb.max.Y + CP_PAD_MARGIN
            if s_ == _cp_corner():                            # corner header: run its pad out to the rim corner
                x0, y1 = -w / 2 + CP_RIM_W / 2, h / 2 - CP_RIM_W / 2
            web.append(Pos((x0 + x1) / 2, (y0 + y1) / 2, CP_PLATE_T / 2) * Box(x1 - x0, y1 - y0, CP_PLATE_T))
        plate = plate.fuse(*web).clean()
    adds, cuts, ribs_ = [], [], []
    for i, d in enumerate(CP_DIAMETERS):
        for j, sq in enumerate(CP_SQUEEZE):
            x, y = cp_tube_xy(i, j)
            s = cp_sizes(d, sq)
            adds.append(_cyl(x, y, 0, s["od"], TUBE_H))
            cuts.append(_cyl(x, y, CP_PLATE_T, s["bore"], TUBE_H))
            cuts.append(_cyl(x, y, -1, s["lip_id"], TUBE_H + 2))      # push-out hole: poke the motor out from below
            for k in range(4):
                a = 45 + 90 * k
                r0, r1 = s["rib_d"] / 2, s["bore"] / 2 + 0.3
                ribs_.append(Pos(x, y, 0) * Rot(0, 0, a) * Pos((r0 + r1) / 2, 0, (CP_PLATE_T + TUBE_H - 0.8) / 2)
                             * Box(r1 - r0, RIB_W, TUBE_H - 0.8 - CP_PLATE_T + 0.02))
    c = plate.fuse(*adds).clean()
    for t in cuts:                       # one tool at a time (touching tools in one Compound cut can collapse)
        c = c - t
    c = c.fuse(*ribs_).clean()
    if with_labels:
        c = c.fuse(*[l[1] for l in cp_labels()]).clean()
    return c

def build_single_sleeve(d, sq):
    """one bare sleeve (no plate, no labels): the frame tube for motor d at squeeze sq, with CP_COMP shrink allowance; base on z = 0"""
    s = cp_sizes(d, sq)
    c = _cyl(0, 0, 0, s["od"], TUBE_H)
    c = c - _cyl(0, 0, LIP_T, s["bore"], TUBE_H)
    c = c - _cyl(0, 0, -1, s["lip_id"], TUBE_H + 2)
    ribs_ = []
    for k in range(4):
        r0, r1 = s["rib_d"] / 2, s["bore"] / 2 + 0.3
        ribs_.append(Rot(0, 0, 45 + 90 * k) * Pos((r0 + r1) / 2, 0, (LIP_T + TUBE_H - 0.8) / 2) * Box(r1 - r0, RIB_W, TUBE_H - 0.8 - LIP_T + 0.02))
    return c.fuse(*ribs_).clean()

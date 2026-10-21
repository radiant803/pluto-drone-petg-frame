# Pluto 1.2 frame - stand-ins for the bought parts and the contracts (needs p_params.py + p_parts.py)

def _cyl(x, y, z0, d, h):
    return Pos(x, y, z0) * Cylinder(d / 2, h, align=(Align.CENTER, Align.CENTER, Align.MIN))

def board_standin():
    # 48 x 48 x 1.6 PCB on the dampers, with its 3.6 mm damper holes (outline taken as the full square: conservative)
    b = Pos(0, 0, BOARD_Z0 + BOARD_T / 2) * Box(BOARD, BOARD, BOARD_T)
    for n in MOTORS:
        sx, sy = MOTORS[n][0], MOTORS[n][1]
        b = b - _cyl(sx * HOLE_SQ / 2, sy * HOLE_SQ / 2, BOARD_Z0 - 1, BOARD_HOLE_D, BOARD_T + 2)
    return b

def damper_standins():
    out = []
    for n in MOTORS:
        sx, sy = MOTORS[n][0], MOTORS[n][1]
        x, y = sx * HOLE_SQ / 2, sy * HOLE_SQ / 2
        d = _cyl(x, y, POST_TOP, DAMPER_FLANGE_D, DAMPER_LOW_H) + _cyl(x, y, POST_TOP, BOARD_HOLE_D - 0.1, DAMPER_H) \
            + _cyl(x, y, POST_TOP + DAMPER_LOW_H + BOARD_T, DAMPER_FLANGE_D, DAMPER_H - DAMPER_LOW_H - BOARD_T)
        out.append(d - _cyl(x, y, POST_TOP - 1, SCREW_D + 0.1, DAMPER_H + 2))
    return out

def motor_standin(n, d=MOTOR_D):
    mx, my = motor_xy(n)
    return _cyl(mx, my, LIP_T, d, MOTOR_L) + _cyl(mx, my, LIP_T + MOTOR_L, MOTOR_SHAFT_D, MOTOR_SHAFT_L)

PROP_Z = LIP_T + MOTOR_L + 1.0          # underside of the prop blades (hub pressed on the shaft just above the can)

def prop_disc(n):
    mx, my = motor_xy(n)
    return _cyl(mx, my, PROP_Z, PROP_D, 3.0)

def connector_standin(n):
    # Molex PicoBlade-style 2-pin housing 5.0 x 3.3 x 6, threaded down the bore and out through the lip
    # small motors: the plug drops through lip hole + slot, shifted 0.8 mm into the slot (towards the drone centre)
    mx, my = motor_xy(n)
    off = 0.0 if PLUG_PASSES_LIP else -0.8
    return Pos(mx, my, -0.5) * Rot(0, 0, theta_of(n)) * Pos(off, 0, 3) * Box(PLUG_L, PLUG_W, 6.0)

BAT_Y0 = BAY_REAR + 0.5                 # battery pushed in until 0.5 mm from the rear stop
def battery_standin():
    return Pos(0, BAT_Y0 + BAT_L / 2, RAIL_T + 0.05 + BAT_T / 2) * Box(BAT_W, BAT_L, BAT_T)

def battery_path():
    # the battery's swept path from its seat out through the open front
    return Pos(0, BAT_Y0 + 60, RAIL_T + 0.05 + BAT_T / 2) * Box(BAT_W, 120, BAT_T)

def canopy_envelope():
    # stock canopy sits above the board between the screws and dampers; take a 46 x 50 x 30 envelope above the board
    return Pos(0, 0, BOARD_Z0 + BOARD_T + 15) * Box(46, 50, 30)

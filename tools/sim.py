# Engineering checks for the Pluto 1.2 frame (Kerf venv python):
#  1 mass budget + thrust/weight     2 inertia from the CAD + parts      3 arm beam model (stiffness, first mode, crash load)
#  4 closed-loop attitude simulation (QuadX mixer, motor lag, rate+angle PID) - new frame vs. stock-geometry estimate
# writes docs/sim_results.json and docs/sim_attitude.png
import os, sys, json, math
import numpy as np
from build123d import *
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for f in ("p_params.py", "p_parts.py"):
    exec(open(os.path.join(ROOT, "src", f), encoding="utf-8").read(), globals())

out = {}
g = 9.81
fr = build_frame(with_labels=True)
frame_g = fr.volume / 1000 * PETG_DENSITY
sliced_g = float(sys.argv[1]) if len(sys.argv) > 1 else frame_g     # pass the slicer mass when known
out["frame_cad_g"] = round(frame_g, 2)
out["frame_printed_g"] = round(sliced_g, 2)

# ---------------- 1 mass budget ----------------
parts = {   # grams; sources in docs/RESEARCH.md
    "Primus V5 board": BOARD_G, "Pluto 600 battery": BAT_G, "4 x motor (%g x %g)" % (MOTOR_D, MOTOR_L): 4 * MOTOR_G, "4 x 55 mm prop": 4 * 0.6,
    "4 dampers + 4 M2 screws": 4 * 0.35, "canopy (stock)": 3.0, "frame (this design)": sliced_g,
}
auw = sum(parts.values())
out["mass_budget_g"] = {k: round(v, 2) for k, v in parts.items()}
out["auw_g"] = round(auw, 1)
out["auw_with_stock_propguards_g"] = round(auw + 4 * 1.2, 1)
# static thrust, T = C_T rho n^2 D^4 ; C_T 0.10 typical for a 55 mm 2-blade micro prop; 8520 under load ~30-35 krpm at 3.7 V
rho, D = 1.2, PROP_D / 1000
def thrust_g(rpm, ct=0.10):
    return ct * rho * (rpm / 60) ** 2 * D ** 4 / g * 1000
# full-throttle operating point from a brushed DC motor model (Drona's published R, I0, no-load rpm) driving the 55 mm prop:
#   V_motor = V_batt - 4 I R_batt - I R_fet ;  V_motor = I R + rpm / Kv ;  I = I0 + Q / Kt ;  Q = C_Q rho n^2 D^5 (C_Q = C_P / 2 pi, C_P 0.05)
def full_throttle(R, I0, Kv, v_batt=3.7, r_batt=0.07, r_fet=0.03, cp=0.05):
    Kt = 60 / (2 * math.pi * Kv)
    rpm = 30000.0
    for _ in range(200):
        n = rpm / 60
        Q = cp / (2 * math.pi) * rho * n ** 2 * D ** 5
        I = I0 + Q / Kt
        v = v_batt - 4 * I * r_batt - I * r_fet - I * R
        rpm = 0.5 * rpm + 0.5 * max(v, 0) * Kv
    return rpm, I
rpm_max, i_max = full_throttle(MOTOR_R, MOTOR_I0, MOTOR_KV)
rpm_8520, _ = full_throttle(0.5, 0.22, 50000 / 3.7)
out["motor"] = {"type": "%g x %g" % (MOTOR_D, MOTOR_L), "full_throttle_rpm": round(rpm_max), "current_per_motor_A": round(i_max, 2),
                "thrust_per_motor_g": round(thrust_g(rpm_max), 1), "for_comparison_8520_rpm": round(rpm_8520), "for_comparison_8520_thrust_g": round(thrust_g(rpm_8520), 1)}
out["thrust_per_motor_g"] = round(thrust_g(rpm_max), 1)
tmax = 4 * thrust_g(rpm_max)
out["thrust_to_weight"] = round(tmax / auw, 2)
out["hover_throttle_fraction_of_max_thrust"] = round(auw / tmax, 2)
rpm_hover = rpm_max * math.sqrt(auw / tmax)
out["hover_rpm_est"] = round(rpm_hover)

# ---------------- 2 inertia ----------------
com = fr.center(CenterOf.MASS)
rho_frame = sliced_g / 1000 / (fr.volume * 1e-9)      # kg/m3 so the frame matches the printed mass
from OCP.GProp import GProp_GProps
from OCP.BRepGProp import BRepGProp
gp = GProp_GProps(); BRepGProp.VolumeProperties_s(fr.wrapped, gp)
M = gp.MatrixOfInertia()
I_frame = np.array([[M.Value(i, j) for j in (1, 2, 3)] for i in (1, 2, 3)]) * 1e-15 * rho_frame   # mm^5 -> m^5 * kg/m3, about the frame COM
c = np.array([com.X, com.Y, com.Z]) / 1000
pts = []  # point / box masses (kg, position m, half-sizes m)
for n in MOTORS:
    mx, my = motor_xy(n)
    pts.append((MOTOR_G / 1000, (mx / 1000, my / 1000, (LIP_T + MOTOR_L / 2) / 1000), (MOTOR_D / 2000,) * 3))
    pts.append((0.6 / 1000, (mx / 1000, my / 1000, (LIP_T + MOTOR_L + 2) / 1000), (PROP_D / 4000, PROP_D / 4000, 0.001)))
pts.append((BAT_G / 1000, (0, (BAY_FRONT - 2 - BAT_L / 2) / 1000, (RAIL_T + BAT_T / 2) / 1000), (BAT_W / 2000, BAT_L / 2000, BAT_T / 2000)))
pts.append((BOARD_G / 1000, (0, 0, (BOARD_Z0 + 1.5) / 1000), (BOARD / 2000, BOARD / 2000, 0.0015)))
pts.append((3.0 / 1000, (0, 0, (BOARD_Z0 + 12) / 1000), (0.022, 0.022, 0.01)))     # canopy
pts.append((1.4 / 1000, (0, 0, (POST_TOP + 2) / 1000), (HOLE_SQ / 2000, HOLE_SQ / 2000, 0.001)))
def assemble(frame_kg, I_fr, c_fr, extra):
    m_tot = frame_kg + sum(p[0] for p in extra)
    cg = (frame_kg * c_fr + sum(p[0] * np.array(p[1]) for p in extra)) / m_tot
    I = np.zeros((3, 3))
    def shift(m, r):
        r = np.asarray(r); return m * (np.dot(r, r) * np.eye(3) - np.outer(r, r))
    I += I_fr + shift(frame_kg, c_fr - cg)
    for m, pos, h in extra:
        a, b, cc = 2 * np.array(h)
        Ib = m / 12 * np.diag([b * b + cc * cc, a * a + cc * cc, a * a + b * b])
        I += Ib + shift(m, np.array(pos) - cg)
    return m_tot, cg, I
m_new, cg_new, I_new = assemble(sliced_g / 1000, I_frame, c, pts)
# stock-geometry estimate: same motor positions and parts, stock frame assumed 8 g spread like ours (frame shape unknown)
m_st, cg_st, I_st = assemble(0.008, I_frame * 0.008 / (sliced_g / 1000), c, pts)
out["cg_mm"] = [round(v * 1000, 2) for v in cg_new]
out["inertia_kgm2_diag"] = [float("%.3e" % v) for v in np.diag(I_new)]
out["inertia_stock_estimate_kgm2_diag"] = [float("%.3e" % v) for v in np.diag(I_st)]
out["cg_offset_from_thrust_centre_mm"] = round(math.hypot(cg_new[0], cg_new[1]) * 1000, 2)

# ---------------- 3 arm beam model ----------------
th = theta_of("FR")
r_root = R_POST + POST_D / 2               # cantilever from the post (conservative: ignores the inner arm into the bay wall)
r_tip = R_MOTOR
L = (r_tip - r_root) / 1000
# real section from the CAD at mid-span, in the arm frame (u across, v up)
r_mid = (r_root + r_tip) / 2
plane = Plane(origin=(r_mid * math.cos(math.radians(th)), r_mid * math.sin(math.radians(th)), 0),
              x_dir=(-math.sin(math.radians(th)), math.cos(math.radians(th)), 0), z_dir=(math.cos(math.radians(th)), math.sin(math.radians(th)), 0))
fr_no_lbl = build_frame(with_labels=False)       # section between the labels' letters is the weakest -> use the label-free section and subtract the engraving depth
slab = plane.location * Box(200, 200, 0.02)
s3 = fr_no_lbl & slab
A = s3.volume / 0.02                               # mm^2
# second moments from a fine grid of the section
bbx = s3.bounding_box()
ys_ = np.linspace(-ARM_W / 2, ARM_W / 2, 113); zs_ = np.linspace(0, ARM_H, 97)
cell = (ys_[1] - ys_[0]) * (zs_[1] - zs_[0])
ch_w = ARM_W - 2 * ARM_WALL; ch_h = ARM_H - ARM_TOP
Y, Z = np.meshgrid((ys_[:-1] + ys_[1:]) / 2, (zs_[:-1] + zs_[1:]) / 2)
inside = ~((np.abs(Y) < ch_w / 2) & (Z < ch_h))
inside &= ~((Z > ARM_H - ENGRAVE) & (np.abs(Y) < 1.6))            # engraving removes up to ~3.2 mm of the top skin
Ag = inside.sum() * cell
zc = (Z[inside]).mean(); Iv = ((Z[inside] - zc) ** 2).sum() * cell + Ag * 0     # about horizontal axis (vertical bending, thrust)
Ih = ((Y[inside]) ** 2).sum() * cell                                             # lateral bending (yaw / side hits)
E = 1.8e9   # printed PETG, along the print lines
sig_y = 40e6  # printed PETG tensile, conservative
out["arm"] = {"cantilever_mm": round(L * 1000, 1), "section_area_cad_mm2": round(A, 2), "section_area_grid_mm2": round(Ag, 2),
              "I_vertical_mm4": round(Iv, 1), "I_lateral_mm4": round(Ih, 1), "neutral_axis_z_mm": round(zc, 2)}
F_thr = thrust_g(rpm_max) * 1.15 / 1000 * g      # +15 % margin on max thrust
defl = F_thr * L ** 3 / (3 * E * Iv * 1e-12)
out["arm"]["tip_deflection_at_max_thrust_mm"] = round(defl * 1000, 4)
c_far = max(zc, ARM_H - zc) / 1000
stress = F_thr * L * c_far / (Iv * 1e-12)
out["arm"]["root_stress_at_max_thrust_MPa"] = round(stress / 1e6, 2)
# first bending mode with the motor + prop + tube as tip mass
m_beam = Ag * 1e-6 * L * 1270
m_tip = (MOTOR_G + 0.6) / 1000 + 0.35 / 1000
k_v = 3 * E * Iv * 1e-12 / L ** 3; k_h = 3 * E * Ih * 1e-12 / L ** 3
f_v = math.sqrt(k_v / (m_tip + 0.24 * m_beam)) / (2 * math.pi)
f_h = math.sqrt(k_h / (m_tip + 0.24 * m_beam)) / (2 * math.pi)
out["arm"]["first_mode_vertical_Hz"] = round(f_v)
out["arm"]["first_mode_lateral_Hz"] = round(f_h)
out["arm"]["rotor_rate_at_hover_Hz"] = round(rpm_hover / 60)
out["arm"]["blade_pass_at_hover_Hz"] = round(2 * rpm_hover / 60)
# crash: tip load that first yields the root (static), and in g of the motor+tube mass
for nm, I_, cf in (("vertical", Iv, c_far), ("lateral", Ih, ARM_W / 2000)):
    F_y = sig_y * I_ * 1e-12 / (L * cf)
    out["arm"]["tip_load_to_yield_%s_N" % nm] = round(F_y, 2)
    out["arm"]["equiv_g_on_motor_%s" % nm] = round(F_y / (m_tip * g))

# ---------------- 4 closed-loop attitude simulation ----------------
# rigid body (Euler, small coupling kept), QuadX mixer from MagisV2 flight/mixer.cpp, first-order motor lag, angle P -> rate PID
def simulate(m, I, tau=0.035, T=1.6, dt=1e-4, noise=0.0, seed=1):
    rng = np.random.default_rng(seed)
    Ix, Iy, Iz = np.diag(I)
    arm_xy = MOTOR_XY / 1000
    tmax_m = thrust_g(rpm_max) / 1000 * g
    kq = 0.012 * PROP_D / 1000      # yaw torque / thrust ratio (m), ~ 0.012 D
    mix = np.array([[1, -1, 1, -1], [1, -1, -1, 1], [1, 1, 1, 1], [1, 1, -1, -1]], float)  # REAR_R, FRONT_R, REAR_L, FRONT_L : thr, roll, pitch, yaw
    pos = np.array([[1, -1], [1, 1], [-1, -1], [-1, 1]], float) * arm_xy                     # x right, y front
    spin = np.array([1, -1, -1, 1], float)     # CW = +1 (RR, FL CW ; FR, RL CCW) -> reaction torque sign
    att = np.zeros(3); w = np.zeros(3); thrust = np.full(4, m * g / 4)
    hover = m * g / 4 / tmax_m
    kp_ang = np.array([12.0, 12.0, 6.0]); kp_r = np.array([0.14, 0.14, 0.12]); ki_r = np.array([0.8, 0.8, 0.5]); kd_r = np.array([0.0015, 0.0015, 0.0])   # generic Betaflight-like structure, not the Magis numbers
    integ = np.zeros(3); w_prev = np.zeros(3)
    log = []
    for k in range(int(T / dt)):
        t = k * dt
        sp = np.array([math.radians(15) if 0.2 <= t < 0.9 else 0.0, 0.0, 0.0])    # 15 deg roll step, then back
        dist = np.array([0.0012 if 1.2 <= t < 1.25 else 0.0, 0, 0])               # 1.2 mN.m kick (a bump)
        rate_sp = kp_ang * (sp - att)
        err = rate_sp - w
        integ += err * dt
        dw = (w - w_prev) / dt; w_prev = w.copy()
        u = kp_r * err + ki_r * integ - kd_r * dw            # normalised commands
        cmd = np.clip(hover + mix[:, 1] * u[0] + mix[:, 2] * u[1] + mix[:, 3] * u[2], 0.05, 1.0)
        thrust += (cmd * tmax_m - thrust) * dt / tau
        # states: roll = rotation about +Y (front axis, + = right wing down), pitch = nose-down rotation (= -rotation about +X), yaw = about +Z
        # r x F with F = (0, 0, T) at (x, y): tau_Y = -x T, tau_X = y T ; CW prop reaction torque on the frame is +Z (CCW)
        roll_tq = np.sum(-pos[:, 0] * thrust)
        pitch_tq = -np.sum(pos[:, 1] * thrust)
        yaw_tq = -np.sum(spin * kq * thrust)     # Magis yaw + raises the CCW motors -> frame turns CW (seen from above) = yaw state +
        tq = np.array([roll_tq, pitch_tq, yaw_tq]) + dist
        if noise: tq += rng.normal(0, noise, 3)
        wd = tq / np.array([Iy, Ix, Iz])      # small-angle, gyroscopic coupling negligible at these rates
        w = w + wd * dt; att = att + w * dt
        if k % 20 == 0: log.append((t, math.degrees(att[0]), math.degrees(sp[0]), *(thrust / tmax_m)))
    return np.array(log)
log_new = simulate(m_new, I_new); log_st = simulate(m_st, I_st)
def metrics(lg):
    t, a, sp = lg[:, 0], lg[:, 1], lg[:, 2]
    seg = (t >= 0.2) & (t < 0.9)
    over = a[seg].max() - 15
    t90 = (t[seg][np.argmax(a[seg] >= 13.5)] - 0.2) if (a[seg] >= 13.5).any() else float("nan")
    band = np.abs(a[seg] - 15) > 0.75; ts = (t[seg][np.nonzero(band)[0][-1]] - 0.2) if band.any() else 0
    kick = np.abs(a[t >= 1.2]).max()
    sat = (lg[:, 3:] >= 0.999).mean()
    return {"rise_to_90pct_s": round(float(t90), 3), "overshoot_deg": round(float(over), 2), "settle_2pt5pct_s": round(float(ts), 3),
            "peak_after_bump_deg": round(float(kick), 2), "time_motor_saturated_frac": round(float(sat), 3)}
out["attitude_sim_new"] = metrics(log_new); out["attitude_sim_stock_estimate"] = metrics(log_st)
try:
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    fig, ax = plt.subplots(1, 2, figsize=(10, 3.6))
    ax[0].plot(log_new[:, 0], log_new[:, 2], "k--", lw=1, label="setpoint")
    ax[0].plot(log_new[:, 0], log_new[:, 1], lw=1.6, label="new PETG frame")
    ax[0].plot(log_st[:, 0], log_st[:, 1], lw=1.2, alpha=.8, label="stock-geometry estimate")
    ax[0].set_xlabel("time (s)"); ax[0].set_ylabel("roll (deg)"); ax[0].legend(frameon=False, fontsize=8); ax[0].set_title("15 deg roll step + bump at 1.2 s", fontsize=9)
    for i, nm in enumerate(["RR M7", "FR M8", "RL M6", "FL M5"]):
        ax[1].plot(log_new[:, 0], log_new[:, 3 + i], lw=1, label=nm)
    ax[1].set_xlabel("time (s)"); ax[1].set_ylabel("thrust / max"); ax[1].legend(frameon=False, fontsize=8, ncol=2); ax[1].set_ylim(0, 1.05); ax[1].set_title("motor commands (new frame)", fontsize=9)
    for a_ in ax: a_.spines[["top", "right"]].set_visible(False)
    fig.tight_layout(); fig.savefig(os.path.join(ROOT, "docs", "images", "sim_attitude.png"), dpi=130)
except Exception as e:
    out["plot_error"] = str(e)
np.savez(os.path.join(ROOT, 'docs', 'sim_logs.npz'), new=log_new, stock=log_st)
json.dump(out, open(os.path.join(ROOT, "docs", "sim_results.json"), "w"), indent=1)
print(json.dumps(out, indent=1))

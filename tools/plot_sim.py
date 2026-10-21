# plot docs/sim_logs.npz (system python with matplotlib)
import os, numpy as np, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
d = np.load(os.path.join(ROOT, "docs", "sim_logs.npz")); n, s = d["new"], d["stock"]
fig, ax = plt.subplots(1, 2, figsize=(10, 3.6))
ax[0].plot(n[:, 0], n[:, 2], "k--", lw=1, label="setpoint")
ax[0].plot(n[:, 0], n[:, 1], lw=2.0, label="new PETG frame")
ax[0].plot(s[:, 0], s[:, 1], ":", lw=1.6, label="stock-geometry estimate")
ax[0].set_xlabel("time (s)"); ax[0].set_ylabel("roll (deg)"); ax[0].legend(frameon=False, fontsize=8); ax[0].set_title("15 deg roll step, 1.2 mN.m bump at 1.2 s", fontsize=9)
for i, nm in enumerate(["RR M7", "FR M8", "RL M6", "FL M5"]):
    ax[1].plot(n[:, 0], n[:, 3 + i], lw=1.2, label=nm)
ax[1].set_xlabel("time (s)"); ax[1].set_ylabel("thrust / max"); ax[1].legend(frameon=False, fontsize=8, ncol=2); ax[1].set_ylim(0, 1.05)
ax[1].set_title("motor commands, new frame", fontsize=9)
for a in ax: a.spines[["top", "right"]].set_visible(False)
fig.tight_layout(); fig.savefig(os.path.join(ROOT, "docs", "images", "sim_attitude.png"), dpi=130); print("ok")

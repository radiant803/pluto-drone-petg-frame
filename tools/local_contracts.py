# run kerf_scripts/frame.py locally with stand-in contract functions (fast pre-check before kerf_build)
import sys, math
from build123d import *
def requirement(s): pass
def require(c, msg, name=""): print("OK  " if c else "FAIL", name, "|", msg)
def require_watertight(s, name="watertight"): print("..  ", name, s.is_valid)
def require_min_wall(s, t, name=""): print("..  ", name, "(kerf only)")
def require_dimension(a, b, tol=0.1, name=""): print("OK  " if abs(a-b) <= tol else "FAIL", name, a)
def require_clearance(a, b, min=0, name=""):
    d = a.distance_to(b); print("OK  " if d >= min else "FAIL", name, "%.2f" % d)
def require_no_interference(*s, name=""):
    v = 0
    for i in range(len(s)):
        for j in range(i+1, len(s)):
            x = s[i] & s[j]; v = max(v, x.volume if x is not None else 0)
    print("OK  " if v < 1e-3 else "FAIL", name, "%.4f" % v)
def show(*a, **k): pass
exec(open(sys.argv[1]).read(), globals())

# dump the label glyph outlines (Kerf venv) for tools/text_check.py
import json, math, os
from build123d import *
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for f in ("p_params.py", "p_parts.py"): exec(open(os.path.join(ROOT, "src", f)).read(), globals())
import sys
if len(sys.argv) > 3: LABEL_FONT, LABEL_BOLD, LABEL_SIZE = sys.argv[1], sys.argv[2] == "1", float(sys.argv[3])
out = {}
for n in MOTORS:
    sk = Text(label_text(n), font_size=LABEL_SIZE, font=LABEL_FONT, font_style=FontStyle.BOLD if LABEL_BOLD else FontStyle.REGULAR, align=(Align.CENTER, Align.CENTER))
    rings = []
    for fc in sk.faces():
        for w in fc.wires():
            pts = []
            for e in w.edges():
                k = max(8, int(e.length / 0.02))
                pts += [(p.X, p.Y) for p in e.positions([i / k for i in range(k + 1)])]
            rings.append(pts)
    out[n] = {"text": label_text(n), "rings": rings}
json.dump(out, open("/tmp/pf_glyphs.json", "w"))
print("ok", {k: len(v["rings"]) for k, v in out.items()})

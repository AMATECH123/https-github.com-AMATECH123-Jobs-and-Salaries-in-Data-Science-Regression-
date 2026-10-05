import itertools
from sweep import *
hbs = {"base": HOURS, "lowZ": {"zapier": (0.6, 0.12), "make": (2.0, 0.40), "n8n": (3.0, 0.55)},
       "midZ": {"zapier": (0.8, 0.16), "make": (2.0, 0.40), "n8n": (3.0, 0.55)}}
rows = []
for rate, mk, zp, cb, hbn in itertools.product([25, 30, 36, 42], [4, 5, 6, 7], [1.5, 2, 2.5], [4, 6, 8, 10], hbs):
    r = evaluate(rate, mk, zp, 1, cb, hbs[hbn]); t = r["TRUTH"]
    w = min(t, key=t.get); srt = sorted(t.values()); margin = (srt[1] - srt[0]) / srt[0]
    flips = [k for k in r if k != "TRUTH" and min(r[k], key=r[k].get) != w]
    # robustness: second best stays second best, truth margin ok
    rows.append((len(flips), round(margin, 3), rate, mk, zp, cb, hbn, w, flips))
rows = [x for x in rows if 0.08 <= x[1] <= 0.16 and x[7] == "zapier"]
rows.sort(key=lambda x: (-x[0], -x[1]))
for x in rows[:12]: print(x)

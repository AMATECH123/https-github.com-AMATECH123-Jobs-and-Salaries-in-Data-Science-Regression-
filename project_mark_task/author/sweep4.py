import itertools
import sweep_core as S
from params import *
hbs = {"cur": HOURS,
       "z+": {"zapier": (1.0, 0.20), "make": (2.0, 0.40), "n8n": (3.0, 0.55)},
       "n-": {"zapier": (0.6, 0.12), "make": (2.0, 0.40), "n8n": (2.0, 0.40)},
       "n--": {"zapier": (0.6, 0.12), "make": (2.0, 0.40), "n8n": (1.2, 0.25)},
       "m-": {"zapier": (0.6, 0.12), "make": (1.2, 0.25), "n8n": (3.0, 0.55)}}
rows = []
for rate, mk, zp, n8, cb, hn in itertools.product([30, 45, 60, 80], [0.6, 0.8, 1.0, 1.3], [0.6, 0.8, 1.0, 1.3], [1, 2, 4], [4, 8, 14], hbs):
    r = S.evaluate(rate, mk, zp, n8, cb, hbs[hn]); t = r["TRUTH"]
    w = min(t, key=t.get); srt = sorted(t.values()); mg = (srt[1] - srt[0]) / srt[0]
    fl = [k for k in r if k != "TRUTH" and min(r[k], key=r[k].get) != w]
    rows.append((len(fl), round(mg, 3), rate, mk, zp, n8, cb, hn, w, fl))
rows = [x for x in rows if 0.07 <= x[1] <= 0.14]
rows.sort(key=lambda x: (-x[0], -x[1]))
for x in rows[:12]: print(x)

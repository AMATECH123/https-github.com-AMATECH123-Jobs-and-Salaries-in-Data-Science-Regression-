import itertools
import sweep_core as S
from params import *
hbs = {"cur": HOURS,
       "z-": {"zapier": (0.8, 0.16), "make": (2.0, 0.40), "n8n": (2.0, 0.40)},
       "m+": {"zapier": (1.4, 0.28), "make": (3.0, 0.60), "n8n": (2.0, 0.40)},
       "m++": {"zapier": (1.4, 0.28), "make": (4.0, 0.80), "n8n": (2.0, 0.40)},
       "n-": {"zapier": (1.4, 0.28), "make": (2.0, 0.40), "n8n": (1.2, 0.25)}}
rows = []
for rate, mk, zp, n8, cb, hn in itertools.product([30, 45, 60], [1.0, 1.3, 1.6, 2.0], [0.7, 0.85, 1.0], [0.6, 0.8, 1.0], [4, 8], hbs):
    r = S.evaluate(rate, mk, zp, n8, cb, hbs[hn]); t = r["TRUTH"]
    w = min(t, key=t.get); srt = sorted(t.values()); mg = (srt[1] - srt[0]) / srt[0]
    fl = [k for k in r if k != "TRUTH" and min(r[k], key=r[k].get) != w]
    rows.append((len(fl), round(mg, 3), rate, mk, zp, n8, cb, hn, w, fl))
rows = [x for x in rows if 0.06 <= x[1] <= 0.12 and "lazy churn (all 4 flagged excluded)" in x[9]]
rows.sort(key=lambda x: (-x[0], -x[1]))
for x in rows[:10]: print(x)

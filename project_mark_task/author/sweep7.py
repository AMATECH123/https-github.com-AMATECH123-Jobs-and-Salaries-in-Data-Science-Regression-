import itertools
import sweep_core as S
from params import *
hbs = {"cur": HOURS,
       "z-": {"zapier": (0.8, 0.16), "make": (2.0, 0.40), "n8n": (2.0, 0.40)},
       "z--": {"zapier": (0.6, 0.12), "make": (2.0, 0.40), "n8n": (2.0, 0.40)},
       "n-": {"zapier": (1.4, 0.28), "make": (2.0, 0.40), "n8n": (1.2, 0.25)},
       "m+": {"zapier": (1.4, 0.28), "make": (3.0, 0.60), "n8n": (2.0, 0.40)}}
rows = []
for rate, mk, zp, n8, cb, hn in itertools.product([30, 36, 45], [0.9, 1.0, 1.1, 1.2, 1.3], [0.7, 0.8, 0.9, 1.0], [0.8, 1.0, 1.2, 1.5], [4, 8], hbs):
    r = S.evaluate(rate, mk, zp, n8, cb, hbs[hn]); t = r["TRUTH"]
    w = min(t, key=t.get); srt = sorted(t.values()); mg = (srt[1] - srt[0]) / srt[0]
    fl = [k for k in r if k != "TRUTH" and min(r[k], key=r[k].get) != w]
    rows.append((len(fl), round(mg, 3), rate, mk, zp, n8, cb, hn, w, fl))
rows = [x for x in rows if 0.05 <= x[1] <= 0.12 and "sub only" in x[9] and "lazy churn (all 4 flagged excluded)" in x[9]]
rows.sort(key=lambda x: (-x[0], -x[1]))
for x in rows[:10]: print(x)

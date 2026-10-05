import itertools
import sweep_core as S
from params import *
hbs = {"cur": HOURS,
       "n-": {"zapier": (0.6, 0.12), "make": (2.0, 0.40), "n8n": (1.4, 0.30)},
       "n--": {"zapier": (0.6, 0.12), "make": (2.0, 0.40), "n8n": (1.0, 0.22)},
       "z+": {"zapier": (1.0, 0.20), "make": (2.0, 0.40), "n8n": (2.0, 0.40)},
       "z++": {"zapier": (1.4, 0.28), "make": (2.0, 0.40), "n8n": (2.0, 0.40)}}
rows = []
for rate, mk, zp, n8, cb, hn in itertools.product([30, 40, 55], [0.8, 1.0, 1.2], [0.8, 1.0, 1.2], [0.8, 1.0, 1.3], [4, 8], hbs):
    r = S.evaluate(rate, mk, zp, n8, cb, hbs[hn]); t = r["TRUTH"]
    w = min(t, key=t.get); srt = sorted(t.values()); mg = (srt[1] - srt[0]) / srt[0]
    fl = [k for k in r if k != "TRUTH" and min(r[k], key=r[k].get) != w]
    rows.append((len(fl), round(mg, 3), rate, mk, zp, n8, cb, hn, w, fl))
rows = [x for x in rows if 0.07 <= x[1] <= 0.15 and "no Zapier upgrade clause" in x[9]]
rows.sort(key=lambda x: (-x[0], -x[1]))
for x in rows[:12]: print(x)

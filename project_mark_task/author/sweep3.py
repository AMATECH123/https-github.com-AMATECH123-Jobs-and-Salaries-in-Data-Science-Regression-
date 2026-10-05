import io, contextlib, itertools
with contextlib.redirect_stdout(io.StringIO()):
    import sweep as S
    import reference_solution as R
import pandas as pd
from params import *
known_z = {k[1] for k in R.xwin if k[0]=="zapier"}; known_m = {k[1] for k in R.xwin if k[0]=="make"}
za = R.z[(~R.z.native.isin(known_z)) & R.z.workflow_id.notna()][["workflow_id","date","runs"]]
ma = R.m[(~R.m.native.isin(known_m)) & R.m.workflow_id.notna()][["workflow_id","date","runs"]]
lost = pd.concat([za, ma]); ca = R.conf.merge(lost, on=["workflow_id","date"], how="left"); ca["business_runs"] -= ca.runs.fillna(0)
S.CASES["dropped unmapped ids"] = dict(vo=S.vols(S.rm_of(ca, R.active.workflow_id), S.latest()), wfs=R.active, cur=R.cur)
hbs = {"cur": HOURS,
       "z+": {"zapier": (1.0, 0.20), "make": (2.0, 0.40), "n8n": (3.0, 0.55)},
       "n-": {"zapier": (0.6, 0.12), "make": (2.0, 0.40), "n8n": (2.0, 0.40)},
       "m-": {"zapier": (0.6, 0.12), "make": (1.2, 0.25), "n8n": (3.0, 0.55)}}
rows = []
for rate, mk, zp, n8, cb, hn in itertools.product([30, 36, 45, 55], [0.6, 0.8, 1.0, 1.3], [0.6, 0.8, 1.0, 1.3], [1, 3, 6], [4, 8, 12], hbs):
    r = S.evaluate(rate, mk, zp, n8, cb, hbs[hn]); t = r["TRUTH"]
    w = min(t, key=t.get); srt = sorted(t.values()); mg = (srt[1] - srt[0]) / srt[0]
    fl = [k for k in r if k != "TRUTH" and min(r[k], key=r[k].get) != w]
    rows.append((len(fl), round(mg, 3), rate, mk, zp, n8, cb, hn, w, fl))
rows = [x for x in rows if 0.07 <= x[1] <= 0.14]
rows.sort(key=lambda x: (-x[0], -x[1]))
for x in rows[:14]: print(x)

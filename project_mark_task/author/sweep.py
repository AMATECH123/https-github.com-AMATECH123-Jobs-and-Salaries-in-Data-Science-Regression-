import io, contextlib, math, itertools, json
import numpy as np, pandas as pd
with contextlib.redirect_stdout(io.StringIO()):
    import reference_solution as R
from params import *
import params as PR

wf, ver, conf, active, cur, sup = R.wf, R.ver, R.conf, R.active, R.cur, R.sup
stale = {r.workflow_id: r.platform_last_reviewed.lower() for r in wf.itertuples()}
def latest(draft=False):
    v = ver if draft else ver[ver.status == "deployed"]
    return v.sort_values(["workflow_id", "version"]).groupby("workflow_id").tail(1).set_index("workflow_id")
def rm_of(c, wids):
    return c[c.workflow_id.isin(wids)].groupby(["workflow_id", "billing_month"]).business_runs.sum().unstack(fill_value=0)
def vols(rm, v):
    u = {"make": v["make_modules_per_run"], "zapier": v["zapier_billable_steps"], "n8n": pd.Series(1, index=v.index)}
    return {p: [float((rm[R.src_month[ym]] * u[p].reindex(rm.index).fillna(1)).sum()) for ym in R.fwd_months] for p in u}

# naive (no dedupe / mirror / incident) conformed volumes
z = pd.read_csv(R.P("zapier_usage_daily.csv"), dtype={"zap_id": str})
z["workflow_id"] = z.zap_id.map(lambda n: R.xmap.get(("zapier", n))); z["bm"] = z.usage_date.str[:7]
m = pd.read_csv(R.P("make_operations_daily.csv"), sep=";", encoding="utf-8-sig", dtype=str); m = m[m["Scenario name"] != "TOTAL"].copy()
m["workflow_id"] = m["Scenario ID"].map(lambda n: R.xmap.get(("make", n)))
m["bm"] = pd.to_datetime(m["Date"], format="%d.%m.%Y").dt.strftime("%Y-%m"); m["runs"] = m["Executions"].str.replace(".", "", regex=False).astype(int)
n = pd.DataFrame(R.j); n["workflow_id"] = n.workflowId.map(lambda x: R.xmap.get(("n8n", x))); n["bm"] = pd.to_datetime(n.startedAt, utc=True).dt.strftime("%Y-%m")
raw = pd.concat([z[["workflow_id", "bm"]].assign(r=z.runs_success), m[["workflow_id", "bm"]].assign(r=m.runs), n[["workflow_id", "bm"]].assign(r=1)])
raw = raw[raw.workflow_id.notna() & (raw.workflow_id != "")]
naive = raw.groupby(["workflow_id", "bm"]).r.sum().reset_index().rename(columns={"bm": "billing_month", "r": "business_runs"})

def labour_h(wfset, curmap, p, conn=True, cb=CUSTOM_BUILD_HOURS, hb=None):
    b, per = (hb or HOURS)[p]; h = 0
    for r in wfset.itertuples():
        if curmap[r.workflow_id] == p: continue
        hh = b + per * r.nodes
        if conn:
            for c in r.required_connectors.split(";"):
                if sup.loc[c, p] == "N": hh += cb
        h += hh
    return h

def subs(vo, mk_mult, zp_mult, n8_mult, incr=True, usd_eur=False):
    out = {}
    best = None
    for a, f, o in MAKE_TIERS:
        t = o_ = 0
        for ym, u in zip(R.fwd_months, vo["make"]):
            k = (1.14 if (incr and ym >= (2026, 1)) else 1.0) * mk_mult
            t += f * k; o_ += math.ceil(max(0, u - a) / 1000) * o * k
        if best is None or t + o_ < best: best = t + o_
    out["make"] = best
    best = None
    for a, f in ZAP_TIERS:
        f2 = f * zp_mult; t = f2 * 0.8 * 12; rate = 1.25 * f2 / (a / 1000)
        o_ = sum(math.ceil(max(0, u - a) / 1000) * rate for u in vo["zapier"])
        c = (t + o_) / (1 if usd_eur else R.EURUSD)
        if best is None or c < best: best = c
    out["zapier"] = best
    out["n8n"] = next((f * n8_mult * 12 for a, f in N8N_TIERS if max(vo["n8n"]) <= a), 1e9)
    return out

CASES = {}
def build_cases():
    rm = rm_of(conf, active.workflow_id); v = latest()
    CASES["TRUTH"] = dict(vo=vols(rm, v), wfs=active, cur=cur)
    CASES["stale platform"] = dict(vo=CASES["TRUTH"]["vo"], wfs=active, cur=stale)
    rma = rm_of(conf, wf.workflow_id); CASES["incl churned"] = dict(vo=vols(rma, v), wfs=wf, cur=cur)
    a2 = active[active.client_id != "INTERNAL"]; rm2 = rm_of(conf, a2.workflow_id)
    CASES["drop internal"] = dict(vo=vols(rm2, v), wfs=a2, cur=cur)
    CASES["draft versions"] = dict(vo=vols(rm, latest(True)), wfs=active, cur=cur)
    rmn = rm_of(naive, active.workflow_id); CASES["no dedupe/mirror/incident"] = dict(vo=vols(rmn, v), wfs=active, cur=cur)
    CASES["no connector gaps"] = dict(vo=CASES["TRUTH"]["vo"], wfs=active, cur=cur, conn=False)
    CASES["USD as EUR"] = dict(vo=CASES["TRUTH"]["vo"], wfs=active, cur=cur, usd_eur=True)
    CASES["no Make +14%"] = dict(vo=CASES["TRUTH"]["vo"], wfs=active, cur=cur, incr=False)
    CASES["sub only"] = dict(vo=CASES["TRUTH"]["vo"], wfs=active, cur=cur, nolab=True)
build_cases()

def evaluate(rate, mk, zp, n8, cb, hb):
    res = {}
    for k, c in CASES.items():
        s = subs(c["vo"], mk, zp, n8, c.get("incr", True), c.get("usd_eur", False))
        tot = {}
        for p in s:
            lab = 0 if c.get("nolab") else labour_h(c["wfs"], c["cur"], p, c.get("conn", True), cb, hb) * rate
            tot[p] = s[p] + lab
        res[k] = tot
    return res

if __name__ == "__main__":
    hbs = {"base": HOURS, "lowZ": {"zapier": (0.6, 0.12), "make": (2.0, 0.40), "n8n": (3.0, 0.55)}}
    rows = []
    for rate, mk, zp, n8, cb, hbn in itertools.product([30, 45, 68], [1, 3, 6], [0.5, 1, 2], [1, 4, 8], [4, 8, 14], hbs):
        r = evaluate(rate, mk, zp, n8, cb, hbs[hbn]); t = r["TRUTH"]
        w = min(t, key=t.get); srt = sorted(t.values()); margin = (srt[1] - srt[0]) / srt[0]
        flips = [k for k in r if k != "TRUTH" and min(r[k], key=r[k].get) != w]
        rows.append((len(flips), margin, rate, mk, zp, n8, cb, hbn, w, flips))
    rows = [x for x in rows if 0.04 <= x[1] <= 0.18]
    rows.sort(key=lambda x: -x[0])
    for x in rows[:15]: print(x)

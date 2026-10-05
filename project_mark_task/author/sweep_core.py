import io, contextlib, math
with contextlib.redirect_stdout(io.StringIO()):
    import reference_solution as R
import pandas as pd, numpy as np
from params import *
wf, ver, conf, active, cur, sup = R.wf, R.ver, R.conf, R.active, R.cur, R.sup
H = R.helper_of
stale = {r.workflow_id: r.platform_last_reviewed.lower() for r in wf.itertuples()}
def latest(draft=False):
    v = ver if draft else ver[ver.status == "deployed"]
    return v.sort_values(["workflow_id", "version"]).groupby("workflow_id").tail(1).set_index("workflow_id")
def rm_of(c, wids):
    return c[c.workflow_id.isin(wids)].groupby(["workflow_id", "billing_month"]).business_runs.sum().unstack(fill_value=0)
def units(v, merge=True):
    u = {"make": v["make_modules_per_run"].copy(), "zapier": v["zapier_billable_steps"].copy(), "n8n": pd.Series(1, index=v.index)}
    if merge:
        base = {k: x.copy() for k, x in u.items()}
        for h, p in H.items():
            for k in u: u[k][p] = u[k][p] + base[k][h]
    return u
def vols(rm, u):
    return {p: [float((rm[R.src_month[ym]] * u[p].reindex(rm.index).fillna(1)).sum()) for ym in R.fwd_months] for p in u}
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
def subs(vo, mk, zp, n8, incr=True, usd_eur=False, clause=True):
    out = {}; best = None
    for a, f, o in MAKE_TIERS:
        t = o_ = 0
        for ym, u in zip(R.fwd_months, vo["make"]):
            k = (1.14 if (incr and ym >= (2026, 1)) else 1.0) * mk
            t += f * k; o_ += math.ceil(max(0, u - a) / 1000) * o * k
        if best is None or t + o_ < best: best = t + o_
    out["make"] = best; best = None
    for start in range(len(ZAP_TIERS)):
        i = start; fees = over = 0.0
        for u in vo["zapier"]:
            a, f = ZAP_TIERS[i]; f2 = f * zp
            fees += f2 * 0.8; over += math.ceil(max(0, u - a) / 1000) * 1.25 * f2 / (a / 1000)
            if clause and u > 1.25 * a and i < len(ZAP_TIERS) - 1: i += 1
        c = (fees + over) / (1 if usd_eur else R.EURUSD)
        if best is None or c < best: best = c
    out["zapier"] = best
    out["n8n"] = next((f * n8 * 12 for a, f in N8N_TIERS if max(vo["n8n"]) <= a), 1e9)
    return out

CASES = {}
def build():
    rm = R.rm.copy(); v = latest()
    T = vols(rm, units(v)); CASES["TRUTH"] = dict(vo=T, wfs=active, cur=cur)
    CASES["stale platform"] = dict(vo=T, wfs=active, cur=stale)
    CASES["no Zapier upgrade clause"] = dict(vo=T, wfs=active, cur=cur, clause=False)
    CASES["backfill bursts left in"] = dict(vo=vols(rm_of(conf, active.workflow_id), units(v)), wfs=active, cur=cur)
    CASES["incl churned"] = dict(vo=vols(rm_of(conf, wf.workflow_id), units(v)), wfs=wf, cur=cur)
    a2 = active[active.client_id != "INTERNAL"]; CASES["drop internal"] = dict(vo=vols(rm_of(conf, a2.workflow_id), units(v)), wfs=a2, cur=cur)
    CASES["draft versions"] = dict(vo=vols(rm, units(latest(True))), wfs=active, cur=cur)
    CASES["no connector gaps"] = dict(vo=T, wfs=active, cur=cur, conn=False)
    CASES["USD as EUR"] = dict(vo=T, wfs=active, cur=cur, usd_eur=True)
    CASES["no Make +14%"] = dict(vo=T, wfs=active, cur=cur, incr=False)
    CASES["sub only"] = dict(vo=T, wfs=active, cur=cur, nolab=True)
    # helpers
    CASES["helper units ignored"] = dict(vo=vols(rm, units(v, merge=False)), wfs=active, cur=cur)
    rmh = rm.copy()
    for h, p in H.items():
        if h in set(active.workflow_id) and p in rmh.index: rmh.loc[h] = rmh.loc[p]
    CASES["helper runs counted, no merge"] = dict(vo=vols(rmh, units(v, merge=False)), wfs=active, cur=cur)
    CASES["helper runs counted + merged"] = dict(vo=vols(rmh, units(v, merge=True)), wfs=active, cur=cur)
build()
def evaluate(rate, mk, zp, n8, cb, hb):
    res = {}
    for k, c in CASES.items():
        s = subs(c["vo"], mk, zp, n8, c.get("incr", True), c.get("usd_eur", False), c.get("clause", True))
        res[k] = {p: s[p] + (0 if c.get("nolab") else labour_h(c["wfs"], c["cur"], p, c.get("conn", True), cb, hb) * rate) for p in s}
    return res

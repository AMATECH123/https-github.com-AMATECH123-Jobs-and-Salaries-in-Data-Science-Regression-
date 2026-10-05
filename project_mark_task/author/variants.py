"""Scores plausible WRONG pipelines to see which platform each would recommend. Author-only."""
import os, json, math, datetime as dt, itertools
import numpy as np, pandas as pd
import reference_solution as R   # reuses parsed inputs + truth (re-runs, prints)
from params import *

wf, ver, conf, active, vv, cur, sup = R.wf, R.ver, R.conf, R.active, R.vv, R.cur, R.sup
EUR = R.EURUSD

def fwd_vols(rm, units, ym_map=R.src_month):
    return {p: [float((rm[ym_map[ym]] * units[p].reindex(rm.index).fillna(1)).sum()) for ym in R.fwd_months] for p in units}

def total(vols, wfset, curmap, make_incr=True, usd_as_eur=False, conn=True, hours_scale=1.0):
    mk = R.cost_make(vols["make"]) if make_incr else None
    # recompute make without increase if asked
    if not make_incr:
        best = None
        for allow, fee, ov in MAKE_TIERS:
            t = 12 * fee; o = sum(math.ceil(max(0, u - allow) / 1000) * ov for u in vols["make"])
            if best is None or t + o < best[1] + best[2]: best = (allow, t, o)
        mk = best
    zp = R.cost_zap(vols["zapier"])
    if usd_as_eur:
        zp = (zp[0], zp[1] * EUR, zp[2] * EUR)
    try: nn = R.cost_n8n(vols["n8n"])
    except RuntimeError: nn = (None, 1e9, 0)
    subs = {"make": mk, "zapier": zp, "n8n": nn}
    lab = {}
    for p in ("zapier", "make", "n8n"):
        h = 0
        for r in wfset.itertuples():
            if curmap[r.workflow_id] == p: continue
            b, per = HOURS[p]; hh = b + per * r.nodes
            if conn:
                for c in r.required_connectors.split(";"):
                    if sup.loc[c, p] == "N": hh += CUSTOM_BUILD_HOURS
            h += hh
        lab[p] = h * RATE_EUR_PER_HOUR * hours_scale
    return {p: round(subs[p][1] + subs[p][2] + lab[p]) for p in subs}, {p: round(subs[p][1] + subs[p][2]) for p in subs}

def rm_of(c, wids):
    return c[c.workflow_id.isin(wids)].groupby(["workflow_id", "billing_month"]).business_runs.sum().unstack(fill_value=0)

def units_latest(index, draft=False):
    v = ver if draft else ver[ver.status == "deployed"]
    v = v.sort_values(["workflow_id", "version"]).groupby("workflow_id").tail(1).set_index("workflow_id")
    return {"make": v["make_modules_per_run"].reindex(index).fillna(1), "zapier": v["zapier_billable_steps"].reindex(index).fillna(1), "n8n": pd.Series(1, index=index)}

stale = {r.workflow_id: r.platform_last_reviewed.lower() for r in wf.itertuples()}
out = {}
# TRUTH
rm = rm_of(conf, active.workflow_id)
t, s = total(fwd_vols(rm, units_latest(rm.index)), active, cur)
out["TRUTH"] = (t, s)
# V1 stale catalog platform
out["stale catalog platform"] = total(fwd_vols(rm, units_latest(rm.index)), active, stale)
# V2 include churned clients
rm_all = rm_of(conf, wf.workflow_id)
out["include churned clients"] = total(fwd_vols(rm_all, units_latest(rm_all.index)), wf, cur)
# V3 drop internal (inner join to client master)
act2 = active[active.client_id != "INTERNAL"]
rm2 = rm_of(conf, act2.workflow_id)
out["drop INTERNAL workflows"] = total(fwd_vols(rm2, units_latest(rm2.index)), act2, cur)
# V4 use draft versions
out["use draft versions"] = total(fwd_vols(rm, units_latest(rm.index, draft=True)), active, cur)
# V5 no make price increase
out["no Make +14%"] = total(fwd_vols(rm, units_latest(rm.index)), active, cur, make_incr=False)
# V6 USD treated as EUR
out["USD as EUR"] = total(fwd_vols(rm, units_latest(rm.index)), active, cur, usd_as_eur=True)
# V7 ignore connector gaps
out["ignore connector gaps"] = total(fwd_vols(rm, units_latest(rm.index)), active, cur, conn=False)
# V8 naive raw volumes: sum billed units per platform, no dedupe, as-billed, no labour considered
z = pd.read_csv(R.P("zapier_usage_daily.csv")); m = pd.read_csv(R.P("make_operations_daily.csv"), sep=";", encoding="utf-8-sig", dtype=str)
m = m[m["Scenario name"] != "TOTAL"]
raw_zap = z.tasks_billed.sum(); raw_make = m["Operations"].str.replace(".", "", regex=False).astype(int).sum(); raw_n8n = R.pd.DataFrame(R.j).shape[0]
print("raw billed: zapier tasks", raw_zap, "make ops", raw_make, "n8n execs", raw_n8n)
# raw runs naive (no dedup/mirror/incident), with latest units, flat monthly
raw_runs = (z.runs_success.sum() + m["Executions"].str.replace(".", "", regex=False).astype(int).sum() + raw_n8n)
print("raw run rows total", raw_runs, "vs conformed", R.conf.business_runs.sum())
flat = {p: [x / 12 for x in [sum(vv_)]] * 12 for p, vv_ in {}.items()}
# V9 conformed volumes but flat 12-month average (ignore seasonality / peak)
fv = fwd_vols(rm, units_latest(rm.index))
flatv = {p: [sum(v) / 12] * 12 for p, v in fv.items()}
out["flat monthly avg (no peaks)"] = total(flatv, active, cur)
# V10 no labour (conformed, subscription only)
out["subscription only"] = (out["TRUTH"][1], out["TRUTH"][1])
for k, (t, s) in out.items():
    w = min(t, key=t.get)
    print(f"{k:32s} -> {w:7s} {t}")

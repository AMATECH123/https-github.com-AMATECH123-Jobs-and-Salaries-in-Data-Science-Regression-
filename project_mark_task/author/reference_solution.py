"""Reference solution. Reads ONLY ../inputs. Writes ../author/reference_outputs/*"""
import os, re, json, math, datetime as dt
import numpy as np, pandas as pd
from params import *

HERE = os.path.dirname(os.path.abspath(__file__))
IN = os.path.join(HERE, "..", "inputs")
OUTD = os.path.join(HERE, "reference_outputs"); os.makedirs(OUTD, exist_ok=True)
P = lambda f: os.path.join(IN, f)

# --- crosswalk
xw = pd.read_csv(P("id_crosswalk.csv"), dtype=str).fillna("")
xmap = {(r.platform, r.native_id): r.workflow_id for r in xw.itertuples()}

# --- workflows, versions, clients
wf = pd.read_excel(P("workflow_catalog.xlsx"), sheet_name="workflows")
ver = pd.read_excel(P("workflow_catalog.xlsx"), sheet_name="versions")
cm = pd.read_excel(P("client_master.xlsx"))
cm["status_n"] = cm["status"].str.strip().str.lower()
def parse_any(s):
    if pd.isna(s): return None
    for f in ("%d/%m/%Y", "%Y-%m-%d", "%b %d, %Y"):
        try: return dt.datetime.strptime(str(s).strip()[:10] if f == "%Y-%m-%d" else str(s).strip(), f).date()
        except ValueError: pass
    return pd.to_datetime(s).date()
cm["end"] = cm["end_date"].map(parse_any)
churned = set(cm[(cm.status_n.isin(["churned", "inactive"])) | (cm.end.notna() & (cm.end <= dt.date(2025, 9, 30)))].client_id)

# --- change log
mig = {}
for line in open(P("change_log.txt")):
    if line.startswith("#"): continue
    p = [x.strip() for x in line.split("|")]
    if len(p) < 4 or not p[1].startswith("W"): continue
    wid = p[1]
    if "parallel run started" in p[3]:
        a, b = [x.strip() for x in p[2].split("->")]
        mig.setdefault(wid, {}).update(frm=a, to=b, pf=dt.date.fromisoformat(p[0]))
    elif "cutover" in p[2]:
        mig.setdefault(wid, {})["cut"] = dt.datetime.strptime(p[0], "%d %b %Y").date()

# --- incidents
inc = pd.read_csv(P("incident_log.csv"), dtype=str).fillna("")

def inc_rate(platform, native, d):
    for r in inc.itertuples():
        if r.platform != platform or r.duplicate_delivery_rate == "": continue
        if dt.date.fromisoformat(r.start_date_utc) <= d <= dt.date.fromisoformat(r.end_date_utc):
            if r.scope == "ALL" or native in r.scoped_native_ids.split(";"):
                return float(r.duplicate_delivery_rate)
    return 0.0

frames = []
# --- Zapier
z = pd.read_csv(P("zapier_usage_daily.csv"), dtype={"zap_id": str})
z = z.sort_values("exported_at").drop_duplicates(["zap_id", "usage_date"], keep="last")
z["date"] = pd.to_datetime(z["usage_date"]).dt.date
z["rate"] = [inc_rate("zapier", n, d) for n, d in zip(z.zap_id, z.date)]
z["runs"] = np.rint(z.runs_success / (1 + z.rate)).astype(int)
z["native"] = z.zap_id; z["platform"] = "zapier"
frames.append(z[["platform", "native", "date", "runs"]])
# --- Make
m = pd.read_csv(P("make_operations_daily.csv"), sep=";", encoding="utf-8-sig", dtype=str)
m = m[m["Scenario name"] != "TOTAL"].copy()
num = lambda s: s.str.replace(".", "", regex=False).astype(int)
m["date"] = pd.to_datetime(m["Date"], format="%d.%m.%Y").dt.date
m["rep"] = num(m["Executions"]) - num(m["Failed"]) - num(m["Retries"]) - num(m["Manual runs"])
m["rate"] = [inc_rate("make", n, d) for n, d in zip(m["Scenario ID"], m.date)]
m["runs"] = np.rint(m.rep / (1 + m.rate)).astype(int)
m["native"] = m["Scenario ID"]; m["platform"] = "make"
frames.append(m[["platform", "native", "date", "runs"]])
# --- n8n
j = json.load(open(P("n8n_executions.json")))["executions"]
n = pd.DataFrame(j)
n = n[(n.status == "success") & (n["mode"].isin(["trigger", "webhook"])) & (n.retryOf.isna())].copy()
n["k"] = np.where(n.eventId.notna(), n.workflowId + "|" + n.eventId.fillna(""), n.id)
n = n.drop_duplicates("k")
n["date"] = pd.to_datetime(n.startedAt, utc=True).dt.date
g = n.groupby(["workflowId", "date"]).size().reset_index(name="runs").rename(columns={"workflowId": "native"})
g["platform"] = "n8n"
frames.append(g[["platform", "native", "date", "runs"]])

allr = pd.concat(frames, ignore_index=True)
allr["workflow_id"] = [xmap.get((p, nv), None) for p, nv in zip(allr.platform, allr.native)]
allr = allr[allr.workflow_id.notna() & (allr.workflow_id != "")]
# parallel-run handling
keep = np.ones(len(allr), bool)
for wid, mg in mig.items():
    sel = allr.workflow_id == wid
    mirror = sel & (allr.platform == mg["to"]) & (allr.date >= mg["pf"]) & (allr.date < mg["cut"])
    stale = sel & (allr.platform == mg["frm"]) & (allr.date >= mg["cut"])
    keep &= ~(mirror | stale).values
allr = allr[keep]
allr = allr[allr.runs > 0]
assert not allr.duplicated(["workflow_id", "date"]).any(), "workflow-day collision"
allr = allr.merge(wf[["workflow_id", "client_id"]], on="workflow_id", how="left")
allr["billing_month"] = pd.to_datetime(allr.date).dt.strftime("%Y-%m")
conf = allr.rename(columns={"platform": "source_platform", "runs": "business_runs"})[
    ["workflow_id", "client_id", "date", "billing_month", "source_platform", "business_runs"]].sort_values(["date", "workflow_id"])
conf.to_csv(os.path.join(OUTD, "conformed_runs_reference.csv"), index=False)

# ---------------- forward cost
active = wf[~wf.client_id.isin(churned)].copy()
vv = ver[(ver.status == "deployed") & (pd.to_datetime(ver.effective_from) <= "2025-09-30")]
vv = vv.sort_values(["workflow_id", "effective_from"]).groupby("workflow_id").tail(1).set_index("workflow_id")
cur = {}
for r in wf.itertuples():
    cur[r.workflow_id] = mig[r.workflow_id]["to"] if r.workflow_id in mig else r.platform_last_reviewed.lower()
fwd_months = [(2025, 11), (2025, 12)] + [(2026, k) for k in range(1, 11)]
src_month = {(2025, 11): "2024-11", (2025, 12): "2024-12"}
for k in range(1, 10): src_month[(2026, k)] = f"2025-{k:02d}"
src_month[(2026, 10)] = "2024-10"
rm = conf[conf.workflow_id.isin(active.workflow_id)].groupby(["workflow_id", "billing_month"]).business_runs.sum().unstack(fill_value=0)
units = {"make": vv.loc[rm.index, "make_modules_per_run"], "zapier": vv.loc[rm.index, "zapier_billable_steps"],
         "n8n": pd.Series(1, index=rm.index)}
vol = {}
for p in units:
    mv = []
    for ym in fwd_months:
        mv.append(float((rm[src_month[ym]] * units[p]).sum()))
    vol[p] = mv

# fx
fx = pd.read_csv(P("fx_rates.csv"))
f = fx[(fx.pair == "EURUSD") & (fx.month == "2025-09")].sort_values("published").iloc[-1]
EURUSD = float(f.rate)

def cost_make(vols):
    best = None
    for allow, fee, ov in MAKE_TIERS:
        tot = 0; over_t = 0
        for ym, u in zip(fwd_months, vols):
            k = 1.14 if ym >= (2026, 1) else 1.0
            blocks = math.ceil(max(0, u - allow) / 1000)
            tot += fee * k; over_t += blocks * ov * k
        if best is None or tot + over_t < best[1] + best[2]: best = (allow, tot, over_t)
    return best
def cost_zap(vols):
    best = None
    for allow, fee in ZAP_TIERS:
        tot = fee * (1 - ZAP_ANNUAL_DISCOUNT) * 12; over_t = 0
        rate = ZAP_OVERAGE_MULT * fee / (allow / 1000)
        for u in vols: over_t += math.ceil(max(0, u - allow) / 1000) * rate
        tot_e, over_e = tot / EURUSD, over_t / EURUSD
        if best is None or tot_e + over_e < best[1] + best[2]: best = (allow, tot_e, over_e)
    return best
def cost_n8n(vols):
    for allow, fee in N8N_TIERS:
        if max(vols) <= allow: return (allow, fee * 12, 0.0)
    raise RuntimeError("no plan")

sub = {"make": cost_make(vol["make"]), "zapier": cost_zap(vol["zapier"]), "n8n": cost_n8n(vol["n8n"])}
sup = pd.read_csv(P("connector_support.csv")).set_index("connector")
labour = {}
for p in ("zapier", "make", "n8n"):
    h = 0; cnt = 0
    for r in active.itertuples():
        if cur[r.workflow_id] == p: continue
        base, per = HOURS[p]
        hh = base + per * r.nodes
        for c in r.required_connectors.split(";"):
            if sup.loc[c, p] == "N": hh += CUSTOM_BUILD_HOURS
        h += hh; cnt += 1
    labour[p] = dict(hours=h, workflows=cnt, eur=h * RATE_EUR_PER_HOUR)
res = {}
for p in sub:
    res[p] = dict(plan_allowance=sub[p][0], subscription_eur=sub[p][1], overage_eur=sub[p][2],
                  migration_hours=labour[p]["hours"], migration_workflows=labour[p]["workflows"], migration_eur=labour[p]["eur"],
                  total_eur=sub[p][1] + sub[p][2] + labour[p]["eur"], peak_month_units=max(vol[p]), annual_units=sum(vol[p]))
out = dict(results=res, eurusd=EURUSD, conformed_rows=len(conf), conformed_total_runs=int(conf.business_runs.sum()),
           churned_clients=sorted(churned), active_workflows=len(active),
           trailing_runs_by_month=conf.groupby("billing_month").business_runs.sum().to_dict(),
           winner=min(res, key=lambda k: res[k]["total_eur"]))
json.dump(out, open(os.path.join(OUTD, "ground_truth.json"), "w"), indent=1, default=str)
print(json.dumps({k: out[k] for k in ("eurusd", "conformed_rows", "conformed_total_runs", "active_workflows", "winner")}, indent=1))
for p, r in res.items(): print(p, {k: round(v, 1) if isinstance(v, float) else v for k, v in r.items()})

# --- verification against hidden generator truth
wt = json.load(open(os.path.join(HERE, "world_truth.json")))
days = [dt.date(2024, 10, 1) + dt.timedelta(days=i) for i in range(365)]
mism = 0; tot_true = 0
cd = conf.groupby("workflow_id").apply(lambda d: d.set_index("date").business_runs.to_dict(), include_groups=False)
for wid, arr in wt["B_by_wid"].items():
    got = cd.get(wid, {})
    for d, v in zip(days, arr):
        tot_true += v
        if got.get(d, 0) != v: mism += 1
print("workflow-days mismatching hidden truth:", mism, "| true total", tot_true, "| conformed total", int(conf.business_runs.sum()))

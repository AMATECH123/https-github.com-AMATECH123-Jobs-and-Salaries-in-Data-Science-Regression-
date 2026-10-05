"""
Generates the synthetic input package for the "Automation platform consolidation" task.
Everything is synthetic. Vendor names are real products but ALL prices, limits and
connector-support flags are invented for this exercise.
Run:  python3 generate_data.py   (writes ../inputs/*)
"""
import json, os, math, random, datetime as dt
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "inputs")
os.makedirs(OUT, exist_ok=True)
SEED = 20251005
rng = np.random.default_rng(SEED)
rnd = random.Random(SEED)

START = dt.date(2024, 10, 1)
END = dt.date(2025, 9, 30)
DAYS = [START + dt.timedelta(days=i) for i in range((END - START).days + 1)]
ND = len(DAYS)
DIDX = {d: i for i, d in enumerate(DAYS)}

# ------------------------------------------------------------------ clients
client_names = [
    "Brightpath Dental", "Calder & Voss Legal", "Harbor Lane Realty", "Nimbus Cloud Print", "Orchard Row Bakery",
    "Pinecrest Physio", "Quarry Street Cycles", "Redwood HVAC", "Summit Ridge Solar", "Tidewater Marine Supply",
    "Umber & Oak Interiors", "Vantage Freight Co", "Willow Creek Vets", "Xenon Fitness", "Yarrow Health Foods",
    "Zephyr Travel Group", "Alder Point Accounting", "Birchwood Schools Trust", "Cobalt Roofing", "Dunmore Logistics",
    "Eastgate Motors", "Fernhill Garden Centre", "Granite Peak Mortgage", "Hollis & Reed Architects", "Ivory Coast Catering",
    "Juniper Learning", "Kestrel Drones", "Lumen Optical",
]
clients = []
churned_idx = {3, 9, 14, 21}  # four churned clients
for i, nm in enumerate(client_names):
    cid = f"CL-{i+1:03d}"
    churn = None
    if i in churned_idx:
        churn = dt.date(2025, rnd.choice([2, 3, 4, 6, 7]), rnd.randint(3, 25))
    clients.append(dict(client_id=cid, client_name=nm, churn_date=churn,
                        onboarded=dt.date(2022 + rnd.randint(0, 2), rnd.randint(1, 12), rnd.randint(1, 28))))
cl_by_id = {c["client_id"]: c for c in clients}
for _i in (3, 9):   # churn flag in the CRM, but the business re-signed under a new contract id and usage never stopped
    clients[_i]["resigned"] = True

# ---------------------------------------------------------------- workflows
FAMILIES = ["Lead intake to CRM", "Invoice reminder", "Client onboarding", "Weekly KPI report", "Booking confirmation",
            "Support ticket triage", "Order sync", "Review request", "Document e-sign", "Payment reconciliation",
            "Inventory alert", "Email enrichment"]
CONNECTORS = ["crm_core", "ledger_sync", "sms_gateway", "esign", "helpdesk", "ecom_orders", "calendar_booking",
              "forms", "warehouse_api", "ai_extract", "chat_ops", "sheet_store"]
NW = 120
workflows = []
active_cids = [c["client_id"] for c in clients]
for i in range(NW):
    wid = f"W{i+1:03d}"
    if i < 12:
        cid = "INTERNAL"
    else:
        cid = active_cids[(i - 12) % len(active_cids)] if i - 12 < len(active_cids) else rnd.choice(active_cids)
    fam = rnd.choice(FAMILIES)
    nodes = int(np.clip(round(rng.lognormal(2.15, 0.45)), 3, 34))
    ncon = rnd.choice([1, 1, 2, 2, 3])
    cons = rnd.sample(CONNECTORS, ncon)
    base_rate = float(rng.lognormal(2.35, 0.85))
    workflows.append(dict(workflow_id=wid, client_id=cid, family=fam, nodes=nodes, connectors=cons,
                          base_rate=base_rate, weekday_only=rnd.random() < 0.42,
                          trend=float(rng.uniform(-0.05, 0.45))))
wf_by_id = {w["workflow_id"]: w for w in workflows}
for w in workflows:
    cname = "Internal" if w["client_id"] == "INTERNAL" else cl_by_id[w["client_id"]]["client_name"]
    w["name"] = f"{cname} | {w['family']}"
_seen = {}
for w in workflows:
    k = _seen.get(w["name"], 0); _seen[w["name"]] = k + 1
    if k:
        w["name"] = f"{w['name']} - {['EU', 'Phase 2', 'Backup', 'Retail', 'Internal', 'Legacy', 'Pilot'][(k - 1) % 7]}{'' if k < 8 else ' ' + str(k)}"
assert len({w["name"] for w in workflows}) == len(workflows)

# ------------------------------------------------------- platform timelines
# initial platform; then pick migrations
init_plat = {}
ids = [w["workflow_id"] for w in workflows]
order = ids[:]
rnd.shuffle(order)
for k, wid in enumerate(order):
    init_plat[wid] = "zapier" if k < 57 else ("make" if k < 57 + 44 else "n8n")
# n8n-resident workflows are low-volume
for wid, p in init_plat.items():
    if p == "n8n":
        wf_by_id[wid]["base_rate"] *= 0.30

active_wids = [w["workflow_id"] for w in workflows
               if w["client_id"] == "INTERNAL" or cl_by_id[w["client_id"]]["churn_date"] is None or cl_by_id[w["client_id"]].get("resigned")]
migrations = []  # dict(workflow_id, from, to, parallel_from, cutover)
def pick(plat, n, lowvol=False):
    pool = [w for w in active_wids if init_plat[w] == plat and w not in {m["workflow_id"] for m in migrations}]
    if lowvol:
        pool = sorted(pool, key=lambda x: wf_by_id[x]["base_rate"])[: max(n * 3, 10)]
    return rnd.sample(pool, n)
plan = [("zapier", "make", 8, False), ("make", "n8n", 3, True), ("zapier", "n8n", 3, True)]
for f, t, n, lv in plan:
    for wid in pick(f, n, lv):
        pf = dt.date(2025, 1, 6) + dt.timedelta(days=rnd.randint(0, 200))
        migrations.append(dict(workflow_id=wid, frm=f, to=t, parallel_from=pf,
                               cutover=pf + dt.timedelta(days=14)))
mig_by_wid = {m["workflow_id"]: m for m in migrations}
cur_plat = {wid: (mig_by_wid[wid]["to"] if wid in mig_by_wid else init_plat[wid]) for wid in ids}

# --------------------------------------------------------------- versions
versions = []  # workflow_id, version, effective_from, status, make_modules, zap_steps, note
for w in workflows:
    mm = max(2, int(round(w["nodes"] * rng.uniform(0.55, 0.85))))
    zs = max(1, int(round(mm * rng.uniform(0.45, 0.65))))
    versions.append(dict(workflow_id=w["workflow_id"], version=1, effective_from=dt.date(2024, 1, 1),
                         status="deployed", make_modules=mm, zap_steps=zs, note="initial build"))
    w["v"] = [(dt.date(2024, 1, 1), mm, zs)]
    if rnd.random() < 0.35:
        eff = dt.date(2024, 11, 1) + dt.timedelta(days=rnd.randint(0, 270))
        mm2 = mm + rnd.randint(2, 6)
        zs2 = zs + rnd.randint(1, 3)
        versions.append(dict(workflow_id=w["workflow_id"], version=2, effective_from=eff, status="deployed",
                             make_modules=mm2, zap_steps=zs2, note=rnd.choice(
                                 ["added error branch", "added CRM dedupe lookup", "added Slack notification", "added enrichment step"])))
        w["v"].append((eff, mm2, zs2))
        if rnd.random() < 0.4:
            versions.append(dict(workflow_id=w["workflow_id"], version=3, effective_from=dt.date(2025, 10, 15),
                                 status="draft", make_modules=mm2 + rnd.randint(3, 8), zap_steps=zs2 + rnd.randint(2, 4),
                                 note="rework in progress - not deployed"))
    elif rnd.random() < 0.12:
        versions.append(dict(workflow_id=w["workflow_id"], version=2, effective_from=dt.date(2025, 10, 20),
                             status="draft", make_modules=mm + rnd.randint(3, 7), zap_steps=zs + rnd.randint(2, 4),
                             note="rework in progress - not deployed"))

def vals_on(w, d):
    cur = w["v"][0]
    for v in w["v"]:
        if v[0] <= d:
            cur = v
    return cur[1], cur[2]

# ------------------------------------------------------------ daily volumes
MONTH_F = {1: 0.95, 2: 0.92, 3: 1.00, 4: 1.02, 5: 1.05, 6: 0.98, 7: 0.90, 8: 0.88, 9: 1.04, 10: 1.12, 11: 1.28, 12: 1.38}
dow = np.array([d.weekday() for d in DAYS])
mf = np.array([MONTH_F[d.month] for d in DAYS])
B = {}  # workflow_id -> int array ND of true first-attempt successful business runs
for w in workflows:
    wid = w["workflow_id"]
    tr = 1 + w["trend"] * (np.arange(ND) / ND)
    wk = np.where(dow >= 5, 0.05 if w["weekday_only"] else 0.75, 1.0)
    lam = w["base_rate"] * tr * wk * mf
    arr = rng.poisson(lam)
    c = cl_by_id.get(w["client_id"])
    if c and c["churn_date"] and not c.get("resigned"):
        arr = np.where(np.array(DAYS) >= c["churn_date"], 0, arr)
    B[wid] = arr.astype(int)

# --------------------------------------------------------------- incidents
incidents = [
    dict(incident_id="INC-101", platform="zapier", start=dt.date(2025, 2, 11), end=dt.date(2025, 2, 11), scope="ALL", rate=0.40,
         note="webhook redelivery storm after vendor-side queue stall; source systems re-sent events"),
    dict(incident_id="INC-102", platform="make", start=dt.date(2024, 12, 17), end=dt.date(2024, 12, 17), scope="ALL", rate=0.25,
         note="scheduler replayed triggers after datastore lock"),
    dict(incident_id="INC-103", platform="zapier", start=dt.date(2025, 6, 3), end=dt.date(2025, 6, 4), scope="LISTED", rate=0.30,
         note="duplicate deliveries on CRM-triggered zaps only"),
    dict(incident_id="INC-104", platform="make", start=dt.date(2025, 5, 20), end=dt.date(2025, 5, 20), scope="LISTED", rate=0.35,
         note="scenarios on the shared ledger webhook delivered twice"),
    dict(incident_id="INC-106", platform="zapier", start=dt.date(2025, 8, 12), end=dt.date(2025, 8, 13), scope="ALL", rate=0.50,
         note="duplicate deliveries after vendor-side retry loop"),
    dict(incident_id="INC-107", platform="make", start=dt.date(2025, 3, 4), end=dt.date(2025, 3, 4), scope="ALL", rate=0.45,
         note="scheduler double-fired webhook queue"),
    dict(incident_id="INC-108", platform="zapier", start=dt.date(2024, 11, 26), end=dt.date(2024, 11, 26), scope="ALL", rate=0.35,
         note="source CRM re-sent events after outage"),
    dict(incident_id="INC-105", platform="n8n", start=dt.date(2025, 4, 8), end=dt.date(2025, 4, 9), scope="ALL", rate=None,
         note="duplicate webhook deliveries; executions carry eventId, deduplicate on it"),
]

# native ids
def zid(): return f"zap_{rnd.randint(10_000_000, 99_999_999)}"
def mid(): return str(rnd.randint(3_000_000, 4_999_999))
def nid(): return "".join(rnd.choice("abcdefghjkmnpqrstuvwxyz23456789") for _ in range(16))
native = {}  # (wid, platform) -> id
for wid in ids:
    for p in ("zapier", "make", "n8n"):
        native[(wid, p)] = {"zapier": zid, "make": mid, "n8n": nid}[p]()

def platform_spans(wid):
    """returns list of (platform, first_day, last_day, role) role in {'main','mirror'}"""
    if wid in mig_by_wid:
        m = mig_by_wid[wid]
        return [(m["frm"], START, m["cutover"] - dt.timedelta(days=1), "main"),
                (m["to"], m["parallel_from"], m["cutover"] - dt.timedelta(days=1), "mirror"),
                (m["to"], m["cutover"], END, "main")]
    return [(init_plat[wid], START, END, "main")]

# choose incident scopes
zap_listed = set(rnd.sample([w for w in ids if init_plat[w] == "zapier" and w not in mig_by_wid], 14))
make_listed = set(rnd.sample([w for w in ids if init_plat[w] == "make" and w not in mig_by_wid], 12))
# scenarios/zaps that were re-created (new id, NOT in crosswalk) or rebuilt (new id in crosswalk, old id keeps firing 10 days)
recreated, rebuilt = {}, {}
_cz = rnd.sample([w for w in ids if init_plat[w] == "zapier" and w not in mig_by_wid], 12)
_cm = rnd.sample([w for w in ids if init_plat[w] == "make" and w not in mig_by_wid], 8)
for plat_, lst in (("zapier", _cz), ("make", _cm)):
    half = len(lst) // 2 + (1 if plat_ == "zapier" else 0)
    for k, wid_ in enumerate(lst):
        sw = dt.date(2025, 1, 15) + dt.timedelta(days=rnd.randint(0, 190))
        new_id = zid() if plat_ == "zapier" else mid()
        (recreated if k < half else rebuilt)[wid_] = (plat_, sw, new_id)

# helper (sub-)workflows: invoked once per parent run, no trigger events of their own
helper_of = {}
_excl = set(mig_by_wid) | set(recreated) | set(rebuilt)
_by_client = {}
for w_ in workflows:
    _by_client.setdefault(w_["client_id"], []).append(w_["workflow_id"])
_cands = [w_["workflow_id"] for w_ in workflows if w_["workflow_id"] not in _excl and w_["client_id"] != "INTERNAL"]
rnd.shuffle(_cands)
for h_ in _cands:
    if len(helper_of) >= 11:
        break
    sib = [x for x in _by_client[wf_by_id[h_]["client_id"]] if x != h_ and x not in _excl and x not in helper_of and x not in helper_of.values()]
    if h_ in helper_of.values() or not sib:
        continue
    helper_of[h_] = max(sib, key=lambda x: wf_by_id[x]["base_rate"])
for h_, p_ in helper_of.items():
    B[h_] = B[p_].copy()
B_biz = {k: (np.zeros_like(v) if k in helper_of else v) for k, v in B.items()}

# one-off bulk backfills (real runs, but not recurring usage)
_busy = set(helper_of) | set(helper_of.values()) | set(mig_by_wid) | set(recreated) | set(rebuilt)
def _pick_burst(plat):
    pool = [w_ for w_ in ids if init_plat[w_] == plat and w_ not in _busy and w_ in set(active_wids)]
    return max(pool, key=lambda x: wf_by_id[x]["base_rate"])
bursts = []
for plat_, d0_, d1_, lam_ in (("zapier", dt.date(2024, 11, 12), dt.date(2024, 11, 21), 1100), ("make", dt.date(2025, 3, 10), dt.date(2025, 3, 14), 1700)):
    w_ = _pick_burst(plat_); _busy.add(w_)
    for d_ in DAYS:
        if d0_ <= d_ <= d1_:
            B[w_][DIDX[d_]] += int(rng.poisson(lam_)); B_biz[w_][DIDX[d_]] = B[w_][DIDX[d_]]
    bursts.append(dict(workflow_id=w_, start=d0_, end=d1_))

def ids_for(wid, plat, d):
    base_id = native[(wid, plat)]
    for tbl in (recreated, rebuilt):
        if wid in tbl and tbl[wid][0] == plat:
            _, sw, new_id = tbl[wid]
            if d < sw:
                return [base_id]
            if tbl is rebuilt and d < sw + dt.timedelta(days=10):
                return [base_id, new_id]   # old build still firing (zombie duplicate)
            return [new_id]
    return [base_id]

def incident_rate(platform, wid, d):
    for inc in incidents:
        if inc["platform"] != platform or inc["rate"] is None:
            continue
        if inc["start"] <= d <= inc["end"]:
            if inc["scope"] == "ALL":
                return inc["rate"]
            lst = zap_listed if platform == "zapier" else make_listed
            if wid in lst:
                return inc["rate"]
    return 0.0

# ---------------------------------------------------------- build exports
zap_rows, make_rows, n8n_rows = [], [], []
ev_counter = [0]
# sandbox ids
sandbox = {"zapier": [zid() for _ in range(3)], "make": [mid() for _ in range(2)], "n8n": [nid() for _ in range(2)]}

def tz_offset(d):  # Europe/Berlin for n8n instance
    # DST 2025-03-30 .. 2025-10-26 ; 2024-10-27 end
    if dt.date(2024, 10, 27) <= d < dt.date(2025, 3, 30) or d >= dt.date(2025, 10, 26):
        return 1
    if d < dt.date(2024, 10, 27):
        return 2
    return 2

def n8n_events_for_day(wid, d, count):
    """generate execution records whose UTC instant falls on UTC day d"""
    recs = []
    for _ in range(count):
        sec = rnd.randint(0, 86399)
        inst = dt.datetime(d.year, d.month, d.day) + dt.timedelta(seconds=sec)
        # offset for that instant (approx by UTC date adjusted)
        off = 2 if dt.datetime(2025, 3, 30, 1) <= inst < dt.datetime(2025, 10, 26, 1) else 1
        local = inst + dt.timedelta(hours=off)
        recs.append((inst, local, off))
    return recs

n8n_id_ctr = [100000]
def add_n8n(wid, name, inst, off, mode, status, retry_of=None, event_id=None):
    n8n_id_ctr[0] += rnd.randint(1, 4)
    local = inst + dt.timedelta(hours=off)
    sign = "+" if off >= 0 else "-"
    st = local.strftime("%Y-%m-%dT%H:%M:%S") + f".{rnd.randint(0,999):03d}{sign}{abs(off):02d}:00"
    stop_local = local + dt.timedelta(seconds=rnd.randint(1, 40))
    sp = stop_local.strftime("%Y-%m-%dT%H:%M:%S") + f".{rnd.randint(0,999):03d}{sign}{abs(off):02d}:00"
    rec = dict(id=str(n8n_id_ctr[0]), workflowId=native[(wid, "n8n")], workflowName=name, mode=mode, status=status,
               startedAt=st, stoppedAt=sp, retryOf=retry_of, eventId=event_id)
    n8n_rows.append(rec)
    return rec["id"]

zap_batches = [("EXP-A", dt.date(2025, 3, 31), dt.date(2024, 10, 1), dt.date(2025, 3, 31)),
               ("EXP-B", dt.date(2025, 7, 2), dt.date(2025, 2, 1), dt.date(2025, 6, 30)),
               ("EXP-C", dt.date(2025, 10, 2), dt.date(2025, 6, 1), dt.date(2025, 9, 30))]
def batches_for(d):
    return [b for b in zap_batches if b[2] <= d <= b[3]]
LATEST_BATCH_RANK = {b[0]: i for i, b in enumerate(zap_batches)}

def fmt_eu_int(n):
    s = f"{int(n):,}".replace(",", ".")
    return s

for w in workflows:
    wid = w["workflow_id"]
    for (plat, d0, d1, role) in platform_spans(wid):
        for d in DAYS:
            if d < d0 or d > d1:
                continue
            b = int(B[wid][DIDX[d]])
            # business-run "true" for the span; mirrors copy the same events
            if b == 0 and rnd.random() < 0.85:
                continue
            mm, zs = vals_on(w, d)
            if plat == "zapier":
                rate = incident_rate("zapier", wid, d)
                rep = int(round(b * (1 + rate)))
                err = int(rng.binomial(max(b, 0), 0.06))
                repl = int(rng.binomial(err, 0.8)) if err else 0
                test = int(rng.integers(1, 4)) if rnd.random() < 0.05 else 0
                tasks = zs * (rep + repl + test) + err * max(1, zs // 2)
                for nid_ in ids_for(wid, "zapier", d):
                    for (bid, exp_at, b0, b1) in batches_for(d):
                        val = rep
                        if bid == "EXP-A" and len(batches_for(d)) > 1:   # late-arriving runs missing from the oldest export
                            val = int(math.floor(rep * rnd.uniform(0.94, 0.985)))
                        # newest export (EXP-C) renamed the column to runs_completed, which also counts replayed runs
                        zap_rows.append(dict(export_batch=bid, exported_at=exp_at.isoformat(), zap_id=nid_,
                                             zap_title=w["name"] if rnd.random() > 0.15 else w["name"].upper(),
                                             usage_date=d.isoformat(), runs_success=(None if bid == "EXP-C" else val),
                                             runs_completed=((val + repl) if bid == "EXP-C" else None),
                                             runs_errored=err, runs_replayed=repl, test_runs=test, tasks_billed=tasks))
            elif plat == "make":
                rate = incident_rate("make", wid, d)
                rep = int(round(b * (1 + rate)))
                fail = int(rng.binomial(max(b, 0), 0.03))
                retry = int(fail * rng.integers(1, 3)) if fail else 0
                manual = int(rng.integers(1, 5)) if rnd.random() < 0.06 else 0
                total = rep + fail + retry + manual
                ops = mm * (rep + retry + manual) + fail * max(1, mm // 2)
                for nid_ in ids_for(wid, "make", d):
                    make_rows.append(dict(sid=nid_, sname=w["name"] + (" " if rnd.random() < .1 else ""),
                                          d=d, total=total, fail=fail, retry=retry, manual=manual, ops=ops,
                                          mb=round(float(rng.uniform(0.2, 9.0)) * (1 + b / 40), 1)))
            else:  # n8n event level
                events = b
                # events are on this UTC day (we store UTC instant)
                for k in range(events):
                    sec = rnd.randint(0, 86399)
                    inst = dt.datetime(d.year, d.month, d.day) + dt.timedelta(seconds=sec)
                    off = 2 if dt.datetime(2025, 3, 30, 1) <= inst < dt.datetime(2025, 10, 26, 1) else 1
                    ev = None
                    mode = "webhook" if rnd.random() < 0.55 else "trigger"
                    if mode == "webhook":
                        ev_counter[0] += 1
                        ev = f"evt-{ev_counter[0]:08d}"
                    add_n8n(wid, w["name"], inst, off, mode, "success", None, ev)
                    in_inc = any(i["platform"] == "n8n" and i["start"] <= d <= i["end"] for i in incidents)
                    if in_inc and mode == "webhook" and rnd.random() < 0.3:
                        add_n8n(wid, w["name"], inst + dt.timedelta(seconds=rnd.randint(1, 5)), off, "webhook", "success", None, ev)
                # additional events whose first attempt failed, then succeeded on retry (not business runs)
                for _ in range(int(rng.binomial(max(b, 0), 0.03))):
                    sec = rnd.randint(0, 86399)
                    inst = dt.datetime(d.year, d.month, d.day) + dt.timedelta(seconds=sec)
                    off = 2 if dt.datetime(2025, 3, 30, 1) <= inst < dt.datetime(2025, 10, 26, 1) else 1
                    ev = None
                    orig = add_n8n(wid, w["name"], inst, off, "trigger", "error", None, ev)
                    add_n8n(wid, w["name"], inst + dt.timedelta(seconds=rnd.randint(60, 900)), off, "retry", "success", orig, ev)
                if rnd.random() < 0.04:
                    inst = dt.datetime(d.year, d.month, d.day, rnd.randint(8, 17), rnd.randint(0, 59))
                    off = 2 if dt.datetime(2025, 3, 30, 1) <= inst < dt.datetime(2025, 10, 26, 1) else 1
                    add_n8n(wid, w["name"], inst, off, "manual", "success", None, None)

# sandbox rows
for zsb in sandbox["zapier"]:
    for d in DAYS:
        if rnd.random() < 0.3:
            for (bid, exp_at, b0, b1) in [batches_for(d)[-1]]:
                n = int(rng.integers(1, 15))
                zap_rows.append(dict(export_batch=bid, exported_at=exp_at.isoformat(), zap_id=zsb,
                                     zap_title="[sandbox] scratch zap", usage_date=d.isoformat(), runs_success=n,
                                     runs_errored=0, runs_replayed=0, test_runs=0, tasks_billed=n * 2))
for msb in sandbox["make"]:
    for d in DAYS:
        if rnd.random() < 0.3:
            n = int(rng.integers(1, 15))
            make_rows.append(dict(sid=msb, sname="Sandbox - tmp", d=d, total=n, fail=0, retry=0, manual=0, ops=n * 4, mb=0.1))
for nsb in sandbox["n8n"]:
    for d in DAYS:
        if rnd.random() < 0.1:
            inst = dt.datetime(d.year, d.month, d.day, 10, 0)
            n8n_id_ctr[0] += 2
            n8n_rows.append(dict(id=str(n8n_id_ctr[0]), workflowId=nsb, workflowName="sandbox", mode="trigger", status="success",
                                 startedAt=inst.strftime("%Y-%m-%dT%H:%M:%S.000+02:00"), stoppedAt=inst.strftime("%Y-%m-%dT%H:%M:%S.100+02:00"),
                                 retryOf=None, eventId=None))

# ---------------------------------------------------------------- write logs
zdf = pd.DataFrame(zap_rows)
zdf = zdf.sample(frac=1.0, random_state=1).sort_values(["export_batch", "usage_date"]).reset_index(drop=True)
zdf.to_csv(os.path.join(OUT, "zapier_usage_daily.csv"), index=False)

mrows = []
for r in make_rows:
    mrows.append({"Scenario ID": r["sid"], "Scenario name": r["sname"], "Date": r["d"].strftime("%d.%m.%Y"),
                  "Executions": fmt_eu_int(r["total"]), "Failed": fmt_eu_int(r["fail"]), "Retries": fmt_eu_int(r["retry"]),
                  "Manual runs": fmt_eu_int(r["manual"]), "Operations": fmt_eu_int(r["ops"]),
                  "Data transfer (MB)": f"{r['mb']:.1f}".replace(".", ",")})
mdf = pd.DataFrame(mrows)
mdf["_k"] = pd.to_datetime(mdf["Date"], format="%d.%m.%Y")
mdf = mdf.sort_values(["_k", "Scenario ID"]).drop(columns="_k")
total_row = {"Scenario ID": "", "Scenario name": "TOTAL", "Date": "", "Executions": fmt_eu_int(sum(r["total"] for r in make_rows)),
             "Failed": fmt_eu_int(sum(r["fail"] for r in make_rows)), "Retries": fmt_eu_int(sum(r["retry"] for r in make_rows)),
             "Manual runs": fmt_eu_int(sum(r["manual"] for r in make_rows)), "Operations": fmt_eu_int(sum(r["ops"] for r in make_rows)),
             "Data transfer (MB)": ""}
mdf = pd.concat([mdf, pd.DataFrame([total_row])], ignore_index=True)
mdf.to_csv(os.path.join(OUT, "make_operations_daily.csv"), index=False, sep=";", encoding="utf-8-sig")

rnd.shuffle(n8n_rows)
n8n_rows.sort(key=lambda r: int(r["id"]))
with open(os.path.join(OUT, "n8n_executions.json"), "w") as f:
    json.dump({"instance": "n8n.northgate-auto.example", "exportedAt": "2025-10-02T06:15:00Z", "count": len(n8n_rows),
               "executions": n8n_rows}, f)

# ------------------------------------------------------------- reference xlsx
def fmt_status(c):
    if c["churn_date"] is None:
        return rnd.choice(["Active", "Active", "active", "Active "])
    return rnd.choice(["Churned", "churned", "CHURNED", "Inactive"])
crows = []
for c in clients:
    cd = c["churn_date"]
    crows.append(dict(client_id=c["client_id"], client_name=c["client_name"], status=fmt_status(c),
                      onboarded=c["onboarded"].isoformat(),
                      end_date=(cd.strftime(rnd.choice(["%d/%m/%Y", "%Y-%m-%d", "%b %d, %Y"])) if cd else None),
                      billing_entity=rnd.choice(["Northgate Automations Ltd", "Northgate Automations Ltd", "Northgate Labs GmbH"])))
_nxt = 29
for c in clients:
    if c.get("resigned"):
        crows.append(dict(client_id=f"CL-{_nxt:03d}", client_name=c["client_name"] + " (2025 contract)", status="Active",
                          onboarded=(c["churn_date"] + dt.timedelta(days=1)).isoformat(), end_date=None,
                          billing_entity="Northgate Automations Ltd"))
        _nxt += 1
with pd.ExcelWriter(os.path.join(OUT, "client_master.xlsx")) as xw:
    pd.DataFrame(crows).to_excel(xw, sheet_name="clients", index=False)

_decoys = ["owner: MK", "owner: JL", "client asked for weekday-only handling", "triggered by account manager from the CRM button",
           "paused over the August holiday", "pilot for the Q2 upsell", "uses client's own API key", "reviewed with client in June"]
def notes_for(wid):
    if wid in helper_of:
        p_ = helper_of[wid]
        return rnd.choice([f"sub-flow, called by {p_} via webhook for every run",
                           f"helper scenario invoked by {p_}; no trigger of its own",
                           f"called from {p_} (one call per run)"])
    return rnd.choice(_decoys) if rnd.random() < 0.18 else ""
wrows = []
for w in workflows:
    wrows.append(dict(workflow_id=w["workflow_id"], workflow_name=w["name"], client_id=w["client_id"],
                      platform_last_reviewed=init_plat[w["workflow_id"]].capitalize() if init_plat[w["workflow_id"]] != "n8n" else "n8n",
                      nodes=w["nodes"], required_connectors=";".join(w["connectors"]),
                      notes=notes_for(w["workflow_id"])))
vdf = pd.DataFrame(versions).sort_values(["workflow_id", "version"])
vdf["effective_from"] = vdf["effective_from"].astype(str)
with pd.ExcelWriter(os.path.join(OUT, "workflow_catalog.xlsx")) as xw:
    pd.DataFrame(wrows).to_excel(xw, sheet_name="workflows", index=False)
    vdf.rename(columns={"zap_steps": "zapier_billable_steps", "make_modules": "make_modules_per_run"}).to_excel(
        xw, sheet_name="versions", index=False)

# crosswalk
xrows = []
for w in workflows:
    wid = w["workflow_id"]
    for plat, d0, d1, role in platform_spans(wid):
        pass
    if wid in mig_by_wid:
        m = mig_by_wid[wid]
        xrows.append(dict(platform=m["frm"], native_id=native[(wid, m["frm"])], native_name=w["name"], workflow_id=wid,
                          valid_from="", valid_to=(m["cutover"] - dt.timedelta(days=1)).isoformat()))
        xrows.append(dict(platform=m["to"], native_id=native[(wid, m["to"])], native_name=w["name"], workflow_id=wid,
                          valid_from=m["parallel_from"].isoformat(), valid_to=""))
    else:
        if wid in recreated:
            p_, sw, _n = recreated[wid]
            xrows.append(dict(platform=p_, native_id=native[(wid, p_)], native_name=w["name"], workflow_id=wid,
                              valid_from="", valid_to=(sw - dt.timedelta(days=1)).isoformat()))
        elif wid in rebuilt:
            p_, sw, nn_ = rebuilt[wid]
            xrows.append(dict(platform=p_, native_id=native[(wid, p_)], native_name=w["name"], workflow_id=wid,
                              valid_from="", valid_to=(sw - dt.timedelta(days=1)).isoformat()))
            xrows.append(dict(platform=p_, native_id=nn_, native_name=w["name"], workflow_id=wid,
                              valid_from=sw.isoformat(), valid_to=""))
        else:
            xrows.append(dict(platform=init_plat[wid], native_id=native[(wid, init_plat[wid])], native_name=w["name"],
                              workflow_id=wid, valid_from="", valid_to=""))
for p, lst in sandbox.items():
    for s in lst:
        xrows.append(dict(platform=p, native_id=s, native_name="sandbox / scratch", workflow_id="", valid_from="", valid_to=""))
pd.DataFrame(xrows).sample(frac=1.0, random_state=3).to_csv(os.path.join(OUT, "id_crosswalk.csv"), index=False)

# connector support (invented)
sup = []
for c in CONNECTORS:
    sup.append(dict(connector=c, make="Y" if rnd.random() < 0.88 else "N", zapier="Y" if rnd.random() < 0.78 else "N",
                    n8n="Y" if rnd.random() < 0.70 else "N"))
pd.DataFrame(sup).to_csv(os.path.join(OUT, "connector_support.csv"), index=False)

# fx
fx = []
base = 1.07
for i in range(12):
    mth = (dt.date(2024, 10, 1) + dt.timedelta(days=31 * i)).replace(day=1)
    r = round(base + 0.012 * math.sin(i / 2) + 0.004 * i, 4)
    fx.append(dict(month=mth.strftime("%Y-%m"), pair="EURUSD", rate=r, published=(mth + dt.timedelta(days=27)).isoformat()))
    fx.append(dict(month=mth.strftime("%Y-%m"), pair="USDEUR", rate=round(1 / r, 4), published=(mth + dt.timedelta(days=27)).isoformat()))
fx_df = pd.DataFrame(fx)
# revision for the final month
last_m = fx_df[fx_df.pair == "EURUSD"].iloc[-1]
fx_df = pd.concat([fx_df, pd.DataFrame([dict(month=last_m.month, pair="EURUSD", rate=round(float(last_m.rate) + 0.0185, 4),
                                             published="2025-10-02"),
                                        dict(month=last_m.month, pair="USDEUR", rate=round(1 / (float(last_m.rate) + 0.0185), 4),
                                             published="2025-10-02")])])
fx_df.to_csv(os.path.join(OUT, "fx_rates.csv"), index=False)

# incidents
inc_rows = []
for i in incidents:
    inc_rows.append(dict(incident_id=i["incident_id"], platform=i["platform"], start_date_utc=i["start"].isoformat(),
                         end_date_utc=i["end"].isoformat(), scope=i["scope"],
                         scoped_native_ids=(";".join(x for w in sorted(zap_listed if i["platform"] == "zapier" else make_listed)
                                                    for x in [native[(w, i["platform"])]] + [t_[w][2] for t_ in (recreated, rebuilt) if w in t_ and t_[w][0] == i["platform"]])
                                            if i["scope"] == "LISTED" else ""),
                         duplicate_delivery_rate=("" if i["rate"] is None else i["rate"]), note=i["note"]))
pd.DataFrame(inc_rows).to_csv(os.path.join(OUT, "incident_log.csv"), index=False)

# change log
lines = []
noise = ["rotated shared API credentials", "renewed agency domain", "retired unused Slack app", "moved docs to new drive",
         "added second approver for invoices", "updated brand footer on report emails", "onboarded intern to Airtable base"]
events = []
for m in migrations:
    w = wf_by_id[m["workflow_id"]]
    events.append((m["parallel_from"], f"{m['parallel_from']} | {m['workflow_id']} | {m['frm']} -> {m['to']} | parallel run started (new build live, old build still primary) | JL"))
    events.append((m["cutover"], f"{m['cutover'].strftime('%d %b %Y')} | {m['workflow_id']} | cutover to {m['to']} done, old build switched off | JL"))
for k in range(9):
    d = dt.date(2024, 10, 3) + dt.timedelta(days=rnd.randint(0, 360))
    events.append((d, f"{d} | - | misc | {rnd.choice(noise)} | MK"))
for b_ in bursts:
    events.append((b_["start"], f"{b_['start']} | {b_['workflow_id']} | one-off bulk backfill of historic records, runs {b_['start']} to {b_['end']} on this workflow only; not recurring usage, leave out of capacity planning for those dates | JL"))
events.sort(key=lambda x: x[0])
with open(os.path.join(OUT, "change_log.txt"), "w") as f:
    f.write("# Northgate ops change log (append-only, informal)\n")
    for _, l in events:
        f.write(l + "\n")

# stash truth-side helper for the author (NOT shipped)
with open(os.path.join(HERE, "world_truth.json"), "w") as f:
    json.dump(dict(cur_plat=cur_plat, migrations=[{**m, "parallel_from": str(m["parallel_from"]), "cutover": str(m["cutover"])} for m in migrations],
                   B_total=int(sum(B_biz[w].sum() for w in ids)),
                   helpers=helper_of, B_by_wid={w: B_biz[w].tolist() for w in ids}), f)
print("zapier rows", len(zdf), "make rows", len(mdf), "n8n execs", len(n8n_rows))
print("current platform counts", pd.Series(cur_plat).value_counts().to_dict())
print("true business runs", int(sum(B_biz[w].sum() for w in ids)), "| helpers", len(helper_of))

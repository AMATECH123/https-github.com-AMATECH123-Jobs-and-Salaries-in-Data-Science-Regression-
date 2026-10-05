"""Reference solution. Reads ONLY ../inputs. Estimates each channel's marginal incremental contribution per dollar."""
import os, re, json, math, datetime as dt
import numpy as np, pandas as pd
from zoneinfo import ZoneInfo
HERE = os.path.dirname(os.path.abspath(__file__)); IN = os.path.join(HERE, "..", "inputs"); OUTD = os.path.join(HERE, "reference_outputs"); os.makedirs(OUTD, exist_ok=True)
P = lambda f: os.path.join(IN, f)
CHI = ZoneInfo("America/Chicago"); UTC = dt.timezone.utc
CUT = dt.date(2025, 9, 30); WIN0 = dt.date(2025, 7, 1)
CH = ["brand", "nonbrand", "meta", "lsa", "retarget"]

def norm_phone(x): d = re.sub(r"\D", "", str(x or "")); return d[-10:] if len(d) >= 10 else ""
def norm_email(x): x = str(x or "").strip().lower(); return x if "@" in x else ""
def parse_ts(s):
    s = str(s).strip()
    if "T" in s: return dt.datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=UTC)
    return dt.datetime.strptime(s, "%m/%d/%Y %H:%M").replace(tzinfo=CHI).astimezone(UTC)

# ---------------------------------------------------------------- channel mapping
cm = pd.read_csv(P("channel_map.csv"))
lab_map = {r.value.strip().lower(): r.channel for r in cm.itertuples() if r.kind == "source_label"}
trk_map = {str(r.value): r.channel for r in cm.itertuples() if r.kind == "tracking_number"}
def label_channel(lbl):
    l = str(lbl).strip().lower()
    if l in lab_map and not lab_map[l].startswith("("): return lab_map[l]
    if l in ("phone call", "website"): return None
    if "retarget" in l or "remarket" in l: return "retarget"
    if "lsa" in l or "guaranteed" in l or "local services" in l: return "lsa"
    if "brand" in l and not re.search(r"non[\s_-]?brand|\bnb\b", l): return "brand"
    if re.search(r"non[\s_-]?brand|\bnb\b|generic", l): return "nonbrand"
    if "facebook" in l or "fb" in l or "meta" in l: return "meta"
    return "organic"

# ---------------------------------------------------------------- records
ct = pd.read_csv(P("ghl_contacts.csv"), dtype=str).fillna("")
ct["ts"] = ct.created_at.map(parse_ts); ct["email_n"] = ct.email.map(norm_email); ct["phone_n"] = ct.phone.map(norm_phone); ct["last_n"] = ct.last_name.str.strip().str.lower()
ct["chan"] = ct.source.map(label_channel)
calls = pd.DataFrame(json.load(open(P("call_tracking.json")))["calls"])
calls["ts"] = pd.to_datetime(calls.started_at, unit="ms", utc=True).dt.to_pydatetime()
calls["phone_n"] = calls.caller_number.map(norm_phone); calls["chan"] = calls.tracking_number.astype(str).map(trk_map)
calls = calls[(calls.answered) & (calls.duration_sec >= 30)].copy()          # short / unanswered calls are not leads

# ---------------------------------------------------------------- identity resolution
parent = {}
def find(x):
    while parent.setdefault(x, x) != x:
        parent[x] = parent[parent[x]]; x = parent[x]
    return x
def union(a, b):
    ra, rb = find(a), find(b)
    if ra != rb: parent[rb] = ra
key_first = {}
for r in ct.itertuples():
    n = ("c", r.contact_id); find(n)
    if r.email_n: union(n, ("e", r.email_n))
    if r.phone_n and r.last_n: union(n, ("p", r.phone_n, r.last_n))
# phone numbers: a phone seen with a single surname group links contacts that lack email/surname match
ph_groups = {}
for r in ct.itertuples():
    if r.phone_n: ph_groups.setdefault(r.phone_n, set()).add(find(("c", r.contact_id)))
# calls attach to a person by phone when exactly one person holds that phone; otherwise they are their own lead
call_node = {}
for r in calls.itertuples():
    n = ("call", r.call_id); find(n); call_node[r.call_id] = n
    g = ph_groups.get(r.phone_n, set()); g = {find(x) for x in g}
    if len(g) == 1: union(n, next(iter(g)))
    else: union(n, ("callphone", r.phone_n)) if not g else None
# repeat calls from the same unmatched phone belong together (handled by the callphone node)
recs = [("contact", r.contact_id, r.ts, r.chan, r.postal_code) for r in ct.itertuples()] + [("call", r.call_id, r.ts, r.chan, None) for r in calls.itertuples()]
df = pd.DataFrame(recs, columns=["kind", "rid", "ts", "chan", "zip"])
df["node"] = [("c", rid) if k == "contact" else ("call", rid) for k, rid in zip(df.kind, df.rid)]
df["person"] = [find(n) for n in df.node]
df["person"] = df.person.map(lambda x: str(x))
codes = {p: i for i, p in enumerate(df.person.unique())}; df["pid"] = df.person.map(codes)
df = df.sort_values("ts")
# first touch: earliest record whose channel is informative (generic labels are skipped)
first_any = df.groupby("pid").first()
info = df[df.chan.notna()].groupby("pid").first()
led = first_any[["ts"]].rename(columns={"ts": "first_touch_ts"}).join(info[["chan"]].rename(columns={"chan": "channel"}))
led["channel"] = led.channel.fillna("organic")
zips = df[df.zip.notna() & (df.zip != "")].groupby("pid").zip.first(); led = led.join(zips.rename("zip"))
led["n_records"] = df.groupby("pid").size()
led["first_touch_date"] = led.first_touch_ts.map(lambda t: t.date())
geo = pd.read_csv(P("geo_map.csv"), dtype=str); gmap = dict(zip(geo.zip, geo.cluster)); led["cluster"] = led.zip.map(gmap)
print("unique persons", len(led)); print(led.channel.value_counts().to_dict())

# ---------------------------------------------------------------- deals -> persons
deals = json.load(open(P("airtable_deals.json")))["records"]
contact_pid = {}
for r in df[df.kind == "contact"].itertuples(): contact_pid[r.rid] = r.pid
email_pid = {}; phone_pid = {}
for r in ct.itertuples():
    pid = contact_pid.get(r.contact_id)
    if pid is None: continue
    if r.email_n: email_pid.setdefault(r.email_n, set()).add(pid)
    if r.phone_n: phone_pid.setdefault(r.phone_n, set()).add(pid)
for r in calls.itertuples():
    pid = df[(df.kind == "call") & (df.rid == r.call_id)].pid.iloc[0] if False else None
call_pid = {r.rid: r.pid for r in df[df.kind == "call"].itertuples()}
for r in calls.itertuples():
    if r.phone_n: phone_pid.setdefault(r.phone_n, set()).add(call_pid[r.call_id])
drows = []
for d in deals:
    f = d["fields"]; cands = set()
    if f.get("GHL Contact ID") in contact_pid: cands.add(contact_pid[f["GHL Contact ID"]])
    e = norm_email(f.get("Contact Email"))
    if e and e in email_pid: cands |= email_pid[e]
    if not cands:
        ph = norm_phone(f.get("Contact Phone"))
        if ph in phone_pid: cands |= phone_pid[ph]
    if len(cands) > 1:   # shared line: pick the person whose first touch is closest to the deal's lead date
        lc = dt.date.fromisoformat(f["Lead Created"]); cands = {min(cands, key=lambda p: abs((led.loc[p, "first_touch_date"] - lc).days))}
    pid = next(iter(cands)) if cands else None
    drows.append(dict(deal_id=f["Deal ID"], pid=pid, stage=f.get("Stage"), won=f.get("Won Date"), lost=f.get("Lost Date"), quote=f.get("Quote Amount"), svc=f.get("Service Type")))
dd = pd.DataFrame(drows); print("deals", len(dd), "unmatched deals", int(dd.pid.isna().sum()), "| persons with >1 deal", int(dd.pid.dropna().duplicated().sum()))
dd = dd.dropna(subset=["pid"]); dd["pid"] = dd.pid.astype(int)
led = led.join(dd.set_index("pid")[["deal_id", "stage", "won", "lost", "quote", "svc"]])

# ---------------------------------------------------------------- jobs and payments
sheets = pd.read_excel(P("jobs_completed.xlsx"), sheet_name=None); jobs = pd.concat(sheets.values(), ignore_index=True)
pay = pd.read_csv(P("payments.csv"))
jobs["phone_n"] = jobs.phone.map(norm_phone)
miss = jobs.deal_id.isna() | (jobs.deal_id.astype(str).str.strip() == "")
# fallback link: phone + surname + service type
dname = led.reset_index()
jobs["surname"] = jobs.customer.str.split().str[-1].str.lower()
for i in jobs[miss].index:
    ph = jobs.at[i, "phone_n"]; cand = phone_pid.get(ph, set())
    cand = [p for p in cand if str(led.loc[p, "stage"]) == "Won"]
    if len(cand) > 1: cand = [p for p in cand if str(led.loc[p, "svc"]).lower() == str(jobs.at[i, "service_type"]).lower()] or cand
    if len(cand) >= 1: jobs.at[i, "deal_id"] = led.loc[cand[0], "deal_id"]
jobs = jobs.dropna(subset=["deal_id"]); jobs = jobs[jobs.deal_id.astype(str).str.strip() != ""]
refs = pay[pay.type != "payment"].groupby("job_id").agg(refund=("amount", "sum"), refund_date=("posted_at", "max"))
jobs = jobs.merge(refs, on="job_id", how="left"); jobs["refund"] = jobs.refund.fillna(0.0)
def commission(rev): return 0.05 * min(rev, 1000) + 0.08 * max(0.0, min(rev, 3000) - 1000) + 0.12 * max(0.0, rev - 3000)
jobs["commission"] = jobs.revenue.map(commission); jobs["fee"] = 0.029 * jobs.revenue + 0.30
jobs["labor"] = jobs.labor_hours * 48.0
jobs["net_to_date"] = jobs.revenue - jobs.materials - jobs.labor - jobs.commission - jobs.fee - jobs.refund
led = led.reset_index().merge(jobs[["deal_id", "job_id", "completed_on", "revenue", "materials", "labor", "commission", "fee", "refund", "net_to_date"]], on="deal_id", how="left").set_index("pid")
led["won_date"] = pd.to_datetime(led.won)
print("jobs linked", int(led.job_id.notna().sum()), "of", len(jobs))

# ---------------------------------------------------------------- maturity (win-lag completion by channel)
led["age"] = [(CUT - d).days for d in led.first_touch_date]
led["win_lag"] = (led.won_date - pd.to_datetime(led.first_touch_ts.map(lambda t: t.date()))).dt.days
mature = led[led.first_touch_date <= dt.date(2024, 12, 31)]
F = {}
for c in CH + ["organic"]:
    m = mature[mature.channel == c]; wins = m.win_lag.dropna().clip(lower=0).values
    grid = np.arange(0, 400); F[c] = np.array([(wins <= a).mean() for a in grid]) if len(wins) else np.ones(400)
    if len(wins) == 0: continue
win = led[(led.first_touch_date >= WIN0)].copy()
res = {}
for c in CH:
    w = win[win.channel == c]; n = len(w); wins = int((w.stage == "Won").sum())
    comp = float(np.mean([F[c][min(a, 399)] for a in w.age])); p_hat = wins / (n * comp)
    # per-job economics: ticket size and costs did not change with the April process change, so pool the channel's full job history
    j = led[(led.channel == c) & led.job_id.notna()]
    mj = led[(led.first_touch_date <= dt.date(2024, 12, 31)) & (led.channel == c) & led.job_id.notna()]
    refund_ratio = mj.refund.sum() / mj.revenue.sum()
    rev = j.revenue.mean(); contrib = (j.revenue - j.materials - j.labor - j.commission - j.fee).mean() - refund_ratio * rev
    res[c] = dict(persons_window=n, wins_window=wins, completion=comp, p_hat=p_hat, rev_per_job=rev, contrib_per_win=contrib, refund_ratio=refund_ratio, u_per_person=p_hat * contrib, p_naive=wins / n)

# ---------------------------------------------------------------- incrementality (geo holdout)
import pdfplumber
txt = " ".join((pg.extract_text() or "") for pg in pdfplumber.open(P("holdout_test_design.pdf")).pages).replace("\n", " ")
get = lambda key: re.findall(r"G\d{2}", re.search(key + r"[^:]*:\s*([^.]*)\.", txt).group(1))
T_brand = get("Brand search ads were switched off in clusters"); T_ret = get("Retargeting was switched off in clusters"); CTRL = get("Control: all other clusters")
TEST0, TEST1 = dt.date(2025, 2, 3), dt.date(2025, 4, 27); PRE0 = dt.date(2024, 11, 11)
led["week"] = led.first_touch_date.map(lambda d: d - dt.timedelta(days=d.weekday()))
def cnt(chan, clusters, d0, d1):
    m = led[(led.channel == chan) & led.cluster.isin(clusters) & (led.week >= d0) & (led.week <= d1)]; return len(m)
PRE1 = TEST0 - dt.timedelta(days=7)
inc = {}
for chan, T in (("brand", T_brand), ("retarget", T_ret)):
    # organic arrivals in paused clusters rise by the people who would have come anyway; ratio-DiD against control clusters
    org_T_pre, org_T_test = cnt("organic", T, PRE0, PRE1), cnt("organic", T, TEST0, TEST1)
    org_C_pre, org_C_test = cnt("organic", CTRL, PRE0, PRE1), cnt("organic", CTRL, TEST0, TEST1)
    gain = org_T_test - org_T_pre * org_C_test / org_C_pre
    ch_T_pre = cnt(chan, T, PRE0, PRE1); ch_C_pre, ch_C_test = cnt(chan, CTRL, PRE0, PRE1), cnt(chan, CTRL, TEST0, TEST1)
    expected_attr_test = ch_T_pre * ch_C_test / ch_C_pre
    rho = float(np.clip(gain / expected_attr_test, 0, 1))
    # cross-check with total leads
    tot = lambda clusters, a, b: len(led[led.cluster.isin(clusters) & (led.week >= a) & (led.week <= b)])
    lost = tot(T, PRE0, PRE1) * tot(CTRL, TEST0, TEST1) / tot(CTRL, PRE0, PRE1) - tot(T, TEST0, TEST1)
    inc[chan] = dict(rho_organic_uplift=rho, incremental_share=1 - rho, incremental_share_total_leads=float(np.clip(lost / expected_attr_test, 0, 1)), pre_attr_in_T=ch_T_pre)
print("incrementality", {k: {a: round(b, 3) for a, b in v.items()} for k, v in inc.items()})

# ---------------------------------------------------------------- response curves
sp = pd.read_csv(P("ad_spend_daily.csv")); sp["date"] = pd.to_datetime(sp.date)
name2ch = {"Google Search - Brand": "brand", "Google Search - Non-brand": "nonbrand", "Meta Lead Ads": "meta", "Google Local Services Ads": "lsa", "Retargeting (Display/Meta)": "retarget"}
sp["ch"] = sp.channel.map(name2ch); sp["week"] = sp.date.dt.to_period("W-SUN").dt.start_time.dt.date
wk_sp = sp.groupby(["ch", "week"]).spend_usd.sum().unstack(0)
season = pd.read_csv(P("season_index.csv")); season["week"] = pd.to_datetime(season.week_start).dt.date; season = season.set_index("week").demand_index
wk_att = led.groupby(["channel", "week"]).size().unstack(0).reindex(wk_sp.index).fillna(0)
weeks_all = list(wk_sp.index); last8 = weeks_all[-8:]
resp = {}
for c in CH:
    ok = [w for w in weeks_all if not (c in ("brand", "retarget") and TEST0 <= w <= TEST1)]
    y = np.log(wk_att.loc[ok, c].clip(lower=1).values); x1 = np.log(wk_sp.loc[ok, c].values); x2 = np.log(season.loc[ok].values)
    X = np.column_stack([np.ones(len(ok)), x1, x2]); b = np.linalg.lstsq(X, y, rcond=None)[0]
    X0 = np.column_stack([np.ones(len(ok)), x1]); b0 = np.linalg.lstsq(X0, y, rcond=None)[0]
    s_run = float(wk_sp.loc[last8, c].mean()); A0 = float(wk_att.loc[last8, c].mean())
    resp[c] = dict(beta=float(b[1]), beta_no_season=float(b0[1]), season_elasticity=float(b[2]), run_rate_spend=s_run, attr_persons_per_week=A0, marginal_attr_persons_per_usd=float(b[1]) * A0 / s_run)
print("response", {c: (round(v["beta"], 2), round(v["beta_no_season"], 2)) for c, v in resp.items()})

# ---------------------------------------------------------------- put it together
out = {}
for c in CH:
    inc_share = inc[c]["incremental_share"] if c in inc else 1.0
    out[c] = dict(**res[c], **resp[c], incremental_share=inc_share,
                  marginal_incremental_contribution_per_usd=inc_share * resp[c]["marginal_attr_persons_per_usd"] * res[c]["u_per_person"],
                  avg_attributed_roas_platform=float(sp[sp.ch == c].platform_reported_conversions.sum() / sp[sp.ch == c].spend_usd.sum()))
rank = sorted(CH, key=lambda c: -out[c]["marginal_incremental_contribution_per_usd"])
final = dict(channels=out, ranking=rank, top=rank[0], unique_persons=len(led), persons_by_channel=led.channel.value_counts().to_dict(), incrementality=inc)
json.dump(final, open(os.path.join(OUTD, "estimates.json"), "w"), indent=1, default=float)
led_out = led.reset_index(drop=True)
led_out.insert(0, "person_id", range(1, len(led_out) + 1))
led_out[["person_id", "first_touch_ts", "first_touch_date", "week", "channel", "cluster", "n_records", "deal_id", "stage", "won", "job_id", "revenue", "materials", "labor", "commission", "fee", "refund", "net_to_date"]].to_csv(os.path.join(OUTD, "lead_ledger_reference.csv"), index=False)
print("RANK", [(c, round(out[c]["marginal_incremental_contribution_per_usd"], 3)) for c in rank])
tr = json.load(open(os.path.join(HERE, "world_truth.json")))
print("TRUTH", {c: round(tr["channels"][c]["marginal_incremental_contribution_per_usd"], 3) for c in CH}, "| persons", tr["persons"], "vs", len(led))
print("truth persons by channel", tr["persons_by_channel"])

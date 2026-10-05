"""Generates the synthetic input package for the home-services channel-budget task. All data is synthetic."""
import os, json, math, random, datetime as dt, string
from zoneinfo import ZoneInfo
import numpy as np, pandas as pd
from model import *

HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, "..", "inputs"); os.makedirs(OUT, exist_ok=True)
SEED = int(os.environ.get("TASK_SEED", 20251101))
rng = np.random.default_rng(SEED); rnd = random.Random(SEED)
W0 = dt.date(2024, 1, 1); NW = 91; CUT = dt.date(2025, 9, 30)
weeks = [W0 + dt.timedelta(days=7 * i) for i in range(NW)]
NEW_FLOW = dt.date(2025, 4, 14)
CHI = ZoneInfo("America/Chicago"); UTC = dt.timezone.utc

# ----------------------------------------------------------------- season, spend, expected volumes
season = 1 + 0.22 * np.sin(2 * np.pi * (np.arange(NW) - 8) / 52) + rng.normal(0, 0.04, NW); season = season / season.mean()
planned = {}; mu = {}
for c in CH:
    p = P[c]; sp = p["s0"] * season ** p["season_delta"] * np.exp(rng.normal(0, 0.25, NW) - 0.5 * 0.25 ** 2)
    planned[c] = sp; mu[c] = p["a0"] * (sp / p["s0"]) ** p["beta"] * season ** SEASON_GAMMA
mu_org = ORGANIC_A0 * season ** 0.6

# ----------------------------------------------------------------- geography and holdout design
G = 24; share = rng.lognormal(0, 0.7, G); share = share / share.sum()
order = np.argsort(-share); top10 = list(order[:10]); top12 = list(order[:12])
T_brand = sorted(rnd.sample(top10, 7)); rest = [g for g in order[:14] if g not in T_brand]; T_ret = sorted(rnd.sample(rest, 7))
control = [g for g in range(G) if g not in T_brand and g not in T_ret]
TEST_START = dt.date(2025, 2, 3); TEST_END = dt.date(2025, 4, 27); PRE_START = dt.date(2024, 11, 11)
in_test = np.array([TEST_START <= w <= TEST_END for w in weeks])
zips = {g: [60000 + g * 10 + k for k in range(8)] for g in range(G)}
frac_paused = {"brand": float(share[T_brand].sum()), "retarget": float(share[T_ret].sum())}
spend = {c: planned[c].copy() for c in CH}
for c in ("brand", "retarget"):
    spend[c] = np.where(in_test, planned[c] * (1 - frac_paused[c]), planned[c])

# ----------------------------------------------------------------- persons
FIRST = "James Mary Robert Patricia John Jennifer Michael Linda David Elizabeth William Barbara Richard Susan Joseph Jessica Thomas Sarah Charles Karen Chris Nancy Daniel Lisa Matthew Betty Anthony Sandra Mark Ashley Donald Emily Steven Kimberly Paul Donna Andrew Michelle Joshua Carol Kenneth Amanda Kevin Melissa Brian Deborah George Stephanie Edward Rebecca Ronald Laura Timothy Sharon Jason Cynthia Jeffrey Kathleen Ryan Amy Gary Angela Nicholas Shirley Eric Anna Jonathan Brenda Stephen Pamela Larry Emma Justin Nicole Scott Helen Brandon Samantha Benjamin Katherine Samuel Christine Gregory Debra Frank Rachel Alexander Carolyn Raymond Janet Patrick Maria".split()
LAST = "Smith Johnson Williams Brown Jones Garcia Miller Davis Rodriguez Martinez Hernandez Lopez Gonzalez Wilson Anderson Thomas Taylor Moore Jackson Martin Lee Perez Thompson White Harris Sanchez Clark Ramirez Lewis Robinson Walker Young Allen King Wright Scott Torres Nguyen Hill Flores Green Adams Nelson Baker Hall Rivera Campbell Mitchell Carter Roberts Gomez Phillips Evans Turner Diaz Parker Cruz Edwards Collins Reyes Stewart Morris Morales Murphy Cook Rogers Gutierrez Ortiz Morgan Cooper Peterson Bailey Reed Kelly Howard Ramos Kim Cox Ward Richardson Watson Brooks Chavez Wood James Bennett Gray Mendoza Ruiz Hughes Price Alvarez Castillo Sanders Patel Myers Long Ross Foster Jimenez".split()
DOM = ["gmail.com", "gmail.com", "gmail.com", "yahoo.com", "outlook.com", "hotmail.com", "icloud.com", "aol.com", "comcast.net", "att.net"]
AREA = [312, 773, 630, 708, 847, 224, 331, 815]
used_phone = {}; used_email = set()
def new_phone():
    while True:
        ph = f"{rnd.choice(AREA)}{rnd.randint(200, 999)}{rnd.randint(1000, 9999)}"
        if ph not in used_phone: used_phone[ph] = 1; return ph
persons = []
pid = 0
wkday_w = np.array([1, 1, 1, 1, 1, 0.7, 0.7]); wkday_w = wkday_w / wkday_w.sum()
def make_person(w_idx, ch, cannibal, g):
    global pid
    pid += 1
    day = int(rng.choice(7, p=wkday_w)); sec = int(rng.integers(0, 86400))
    t = dt.datetime.combine(weeks[w_idx] + dt.timedelta(days=day), dt.time(0, 0), tzinfo=UTC) + dt.timedelta(seconds=sec)
    last = rnd.choice(LAST); first = rnd.choice(FIRST)
    ph = new_phone()
    if persons and rnd.random() < 0.015:   # shared line (household/office phone) with a different person
        other = rnd.choice(persons[-4000:]);
        if other["last"] != last: ph = other["phone"]
    em = None
    if rnd.random() < 0.82:
        while True:
            em = f"{first.lower()}.{last.lower()}{rnd.choice(['', '', str(rnd.randint(1, 999))])}@{rnd.choice(DOM)}"
            if em not in used_email: used_email.add(em); break
            em = f"{first.lower()}{rnd.randint(1, 9999)}@{rnd.choice(DOM)}"
            if em not in used_email: used_email.add(em); break
    mix = P[ch]["mix"] if ch in P else (0.5, 0.3, 0.2)
    jt = JT[int(rng.choice(3, p=mix))]
    return dict(pid=pid, week=w_idx, t=t, channel=ch, cannibal=cannibal, cluster=g, first=first, last=last, phone=ph, email=em, jt=jt,
                zip=rnd.choice(zips[g]))
for w in range(NW):
    for c in CH:
        p = P[c]
        for g in range(G):
            m = mu[c][w] * share[g]
            paused = in_test[w] and ((c == "brand" and g in T_brand) or (c == "retarget" and g in T_ret))
            ni = 0 if paused else rng.poisson((1 - p["rho"]) * m); nk = rng.poisson(p["rho"] * m)
            for _ in range(ni): persons.append(make_person(w, c, False, g))
            for _ in range(nk): persons.append(make_person(w, "organic" if paused else c, True, g))
    for g in range(G):
        for _ in range(rng.poisson(mu_org[w] * share[g])): persons.append(make_person(w, "organic", False, g))
print("persons", len(persons))

# ----------------------------------------------------------------- outcomes
def lognorm(med, sig): return float(rnd.lognormvariate(math.log(med), sig))
ORG = dict(p=0.33, lag_med=6, lag_sig=0.9, q_form=0.80, dup=0.05, ref_mult=1.0, ref_med=45)
jobs = []; 
for pr in persons:
    c = pr["channel"]; p = P.get(c) or ORG
    d0 = pr["t"].date()
    pw = p["p_new"] if (c in P and d0 >= NEW_FLOW) else (p["p_old"] if c in P else ORG["p"])
    pr["won"] = rnd.random() < pw
    if pr["won"]:
        pr["won_at"] = pr["t"] + dt.timedelta(days=lognorm(p["lag_med"], p["lag_sig"]))
    else:
        pr["lost_at"] = pr["t"] + dt.timedelta(days=lognorm(p["lag_med"] * 0.8, p["lag_sig"]))
    if pr["won"]:
        t = pr["jt"]
        rev = float(rnd.lognormvariate(math.log(REV_MU[t]) - REV_SIG[t] ** 2 / 2, REV_SIG[t]))
        mat = rev * MAT_FRAC[t] * rnd.uniform(0.85, 1.15)
        hrs = float(rng.gamma(6, LAB_HRS[t] / 6))
        pr["job"] = dict(rev=rev, mat=mat, hrs=hrs, done=pr["won_at"] + dt.timedelta(days=1 + float(rng.gamma(2, 2.0))))
        pr["quote"] = rev * rnd.uniform(0.97, 1.03)
        refund = rnd.random() < REF_P[t] * p["ref_mult"]
        pr["refund"] = (rev * rnd.uniform(0.3, 1.0), pr["job"]["done"] + dt.timedelta(days=lognorm(p["ref_med"], REF_SIG)), rnd.random() < 0.2) if refund else None
print("won", sum(p["won"] for p in persons))

# ----------------------------------------------------------------- records: contacts, calls
LABELS = {
 "brand": ["Google Ads - Brand", "google brand search", "GAds BRAND", "Brand Search (Google)", "google_ads_brand", "Google Brand"],
 "nonbrand": ["Google Ads - Non-Brand", "google nonbrand", "GAds NB", "Search - Generic", "google_ads_nonbrand", "Google Search (non brand)"],
 "meta": ["Facebook Lead Form", "Meta Lead Ads", "FB Instant Form", "fb_leadform", "Meta Instant Form", "Facebook Ads"],
 "lsa": ["Google LSA", "Local Services Ad", "Google Guaranteed", "LSA", "google_lsa"],
 "retarget": ["Retargeting", "FB Retargeting", "Display Remarketing", "remarketing_display", "Meta Retargeting"],
 "organic": ["Organic Search", "Direct", "Website", "Referral", "Google Organic", "Walk-in/Referral"]}
MAPPED_LABELS = {k: v[:-1] if k != "organic" else v for k, v in LABELS.items()}   # last variant per channel is deliberately unmapped
TRACK = {"brand": "3125550101", "nonbrand": "3125550102", "meta": "3125550103", "lsa": "3125550104", "retarget": "3125550105", "organic": "3125550100"}
def phone_fmt(ph):
    s = rnd.choice([0, 0, 1, 2, 3, 4])
    return [ph, f"({ph[:3]}) {ph[3:6]}-{ph[6:]}", f"{ph[:3]}-{ph[3:6]}-{ph[6:]}", f"+1 {ph[:3]} {ph[3:6]} {ph[6:]}", f"{ph[:3]}.{ph[3:6]}.{ph[6:]}"][s]
def email_fmt(e):
    if not e: return ""
    return rnd.choice([e, e, e.upper(), e.title(), " " + e, e + " "])
def ts_fmt(t):
    if t.date() < dt.date(2024, 7, 1):
        loc = t.astimezone(CHI); return loc.strftime("%m/%d/%Y %H:%M")
    return t.strftime("%Y-%m-%dT%H:%M:%SZ")
contacts = []; calls = []; cid = 0; callid = 0
def add_contact(pr, t, label, with_email=True, with_phone=True, source_override=None):
    global cid
    cid += 1
    pr.setdefault("ghl_ids", []).append(f"GHL-{cid:06d}")
    contacts.append(dict(contact_id=f"GHL-{cid:06d}", created_at=ts_fmt(t), first_name=pr["first"], last_name=pr["last"] if rnd.random() > 0.03 else pr["last"].upper(),
                         email=email_fmt(pr["email"]) if with_email else "", phone=phone_fmt(pr["phone"]) if with_phone else "",
                         postal_code=pr["zip"], source=source_override or rnd.choice(LABELS[pr["channel"]]),
                         utm_campaign=(rnd.choice(["spring_promo", "always_on", "hvac_tuneup", "plumbing_q3"]) if rnd.random() < 0.35 else ""),
                         _t=t))
def add_call(pr, t, track_ch, answered=True, dur=None):
    global callid
    callid += 1
    if pr is not None: pr.setdefault("call_ids", []).append(f"CALL-{callid:06d}")
    calls.append(dict(call_id=f"CALL-{callid:06d}", started_at=int(t.timestamp() * 1000), tracking_number=TRACK[track_ch], caller_number=phone_fmt(pr["phone"]) if pr else phone_fmt(new_phone()),
                      duration_sec=dur if dur is not None else int(rng.integers(30, 900)), answered=bool(answered), _pid=pr["pid"] if pr else None))
for pr in persons:
    c = pr["channel"]; p = P.get(c) or ORG; t = pr["t"]
    has_form = rnd.random() < p["q_form"]
    if has_form:
        add_contact(pr, t, None, with_email=pr["email"] is not None, with_phone=rnd.random() < 0.95)
        if rnd.random() < 0.15: add_call(pr, t + dt.timedelta(hours=rnd.uniform(1, 40)), "organic")
        if rnd.random() < p["dup"] + 0.0:
            for _ in range(1 + (rnd.random() < 0.25)):
                tt = t + dt.timedelta(days=rnd.uniform(0, 6))
                keep_email = (rnd.random() < 0.8) and pr["email"] is not None; keep_phone = (rnd.random() < 0.8) or not keep_email
                add_contact(pr, tt, None, with_email=keep_email and pr["email"] is not None, with_phone=keep_phone,
                            source_override=("Website" if rnd.random() < 0.4 else None))
        pr["has_record"] = True
    else:
        add_call(pr, t, c if c in TRACK else "organic")
        if rnd.random() < 0.08: add_call(pr, t + dt.timedelta(days=rnd.uniform(0.5, 9)), "organic")
        if rnd.random() < 0.6:
            add_contact(pr, t + dt.timedelta(days=rnd.uniform(0, 3)), None, with_email=False, with_phone=True, source_override="Phone Call")
        pr["has_record"] = True
# unanswered / short / spam calls
for c in TRACK:
    for _ in range(int(0.12 * sum(1 for x in calls if x["tracking_number"] == TRACK[c]))):
        w = rnd.randrange(NW); t = dt.datetime.combine(weeks[w] + dt.timedelta(days=rnd.randrange(7)), dt.time(0), tzinfo=UTC) + dt.timedelta(seconds=rnd.randrange(86400))
        add_call(None, t, c, answered=rnd.random() < 0.5, dur=rnd.randint(2, 28))
print("contacts", len(contacts), "calls", len(calls))

# ----------------------------------------------------------------- deals (Airtable), jobs, payments
deals = []; jobrows = []; pay = []
did = 0; jid = 0; invid = 0
def person_ident(pr):
    refs = {}
    cand = []
    if pr["email"]: cand.append("email")
    cand.append("phone")
    if pr.get("ghl_ids"): cand.append("ghl")
    k = rnd.sample(cand, k=min(len(cand), rnd.choice([1, 2, 2, 3])))
    if not pr.get("ghl_ids") and "phone" not in k: k.append("phone")   # call-only people can only be linked by phone
    if "email" in k: refs["Contact Email"] = email_fmt(pr["email"]).lower().strip() if rnd.random() < 0.9 else email_fmt(pr["email"])
    if "phone" in k: refs["Contact Phone"] = phone_fmt(pr["phone"])
    if "ghl" in k: refs["GHL Contact ID"] = rnd.choice(pr["ghl_ids"])
    return refs
for pr in persons:
    did += 1
    t0 = pr["t"] + dt.timedelta(days=rnd.uniform(0, 2))
    f = dict(person_ident(pr)); f["Deal ID"] = f"D-{did:06d}"; f["Lead Created"] = t0.strftime("%Y-%m-%d"); f["Service Type"] = pr["jt"].capitalize(); f["Owner"] = rnd.choice(["Ava", "Ben", "Cara", "Dev"])
    status = "Open"
    if pr["won"] and pr["won_at"].date() <= CUT:
        status = "Won"; f["Won Date"] = pr["won_at"].strftime("%Y-%m-%d"); f["Quote Amount"] = round(pr["quote"], 2)
    elif (not pr["won"]) and pr["lost_at"].date() <= CUT:
        status = "Lost"; f["Lost Date"] = pr["lost_at"].strftime("%Y-%m-%d")
    f["Stage"] = status
    pr["deal_id"] = f["Deal ID"]
    deals.append(dict(id="rec" + "".join(rnd.choice(string.ascii_letters + string.digits) for _ in range(14)), createdTime=t0.strftime("%Y-%m-%dT%H:%M:%S.000Z"), fields=f))
    if pr["won"] and pr["job"]["done"].date() <= CUT:
        jid += 1; j = pr["job"]
        row = dict(job_id=f"J-{jid:06d}", deal_id=(f["Deal ID"] if rnd.random() < 0.92 else ""), customer=f"{pr['first']} {pr['last']}", phone=phone_fmt(pr["phone"]),
                   service_type=pr["jt"], completed_on=j["done"].strftime("%Y-%m-%d"), revenue=round(j["rev"], 2), materials=round(j["mat"], 2),
                   labor_hours=round(j["hrs"], 2), callback=("Y" if rnd.random() < 0.05 else "N"))
        jobrows.append((j["done"].date(), row))
        invid += 1
        pay.append(dict(invoice_id=f"INV-{invid:06d}", job_id=row["job_id"], posted_at=j["done"].strftime("%Y-%m-%d"), type="payment", amount=round(j["rev"], 2), method=rnd.choice(["card", "card", "ach", "check", "financing"])))
        if pr["refund"] and pr["refund"][1].date() <= CUT:
            amt, rt, cb = pr["refund"]
            pay.append(dict(invoice_id=f"INV-{invid:06d}", job_id=row["job_id"], posted_at=rt.strftime("%Y-%m-%d"), type=("chargeback" if cb else "refund"), amount=round(amt, 2), method="card"))
print("deals", len(deals), "jobs", len(jobrows), "payments", len(pay))

# ----------------------------------------------------------------- write files
cdf = pd.DataFrame([{k: v for k, v in c.items() if not k.startswith("_")} for c in contacts]).sample(frac=1.0, random_state=2)
cdf.to_csv(os.path.join(OUT, "ghl_contacts.csv"), index=False)
json.dump({"exported_at": "2025-10-01T05:00:00Z", "calls": [{k: v for k, v in c.items() if not k.startswith("_")} for c in calls]}, open(os.path.join(OUT, "call_tracking.json"), "w"))
json.dump({"base": "appHarborPineDeals", "table": "Deals", "records": deals}, open(os.path.join(OUT, "airtable_deals.json"), "w"))
with pd.ExcelWriter(os.path.join(OUT, "jobs_completed.xlsx")) as xw:
    df = pd.DataFrame([dict(_d=d, **r) for d, r in jobrows]); df["_q"] = pd.to_datetime(df["_d"]).dt.to_period("Q").astype(str)
    for q, g in df.groupby("_q"):
        g.drop(columns=["_d", "_q"]).to_excel(xw, sheet_name=q.replace("Q", "-Q"), index=False)
pd.DataFrame(pay).to_csv(os.path.join(OUT, "payments.csv"), index=False)
rows = []
for c in CH:
    for w in range(NW):
        for d in range(7):
            wt = wkday_w[d]
            sp = spend[c][w] * wt; day = weeks[w] + dt.timedelta(days=d)
            rows.append(dict(date=day.isoformat(), channel=LABEL[c], spend_usd=round(float(sp), 2), impressions=int(sp * rnd.uniform(70, 110)), clicks=int(sp * rnd.uniform(0.35, 0.6)),
                             platform_reported_conversions=round(float(mu[c][w] * wt * rnd.uniform(1.25, 1.7)), 1)))
pd.DataFrame(rows).to_csv(os.path.join(OUT, "ad_spend_daily.csv"), index=False)
pd.DataFrame(dict(week_start=[w.isoformat() for w in weeks], demand_index=np.round(season, 4))).to_csv(os.path.join(OUT, "season_index.csv"), index=False)
pd.DataFrame([dict(zip=z, cluster=f"G{g+1:02d}") for g in range(G) for z in zips[g]]).to_csv(os.path.join(OUT, "geo_map.csv"), index=False)
cm = [dict(kind="source_label", value=v, channel=ch) for ch, vs in MAPPED_LABELS.items() for v in vs] + [dict(kind="tracking_number", value=n, channel=ch) for ch, n in TRACK.items()] + [dict(kind="source_label", value="Phone Call", channel="(generic - use call tracking)"), dict(kind="source_label", value="Website", channel="(generic)")]
pd.DataFrame(cm).to_csv(os.path.join(OUT, "channel_map.csv"), index=False)

# ----------------------------------------------------------------- hidden truth
last8 = slice(NW - 8, NW)
truth = {"persons": len(persons), "persons_by_channel": pd.Series([p["channel"] for p in persons]).value_counts().to_dict(),
         "T_brand": [f"G{g+1:02d}" for g in T_brand], "T_retarget": [f"G{g+1:02d}" for g in T_ret], "control": [f"G{g+1:02d}" for g in control]}
tab = truth_table(); tr = {}
for c in CH:
    p = P[c]; s_run = float(spend[c][last8].mean())
    a0 = float(p["a0"] * np.mean((spend[c][last8] / p["s0"]) ** p["beta"] * season[last8] ** SEASON_GAMMA))   # expected attributed persons/week at run-rate
    a_at_run = float(p["a0"] * (s_run / p["s0"]) ** p["beta"] * np.mean(season[last8] ** SEASON_GAMMA))
    mar = p["beta"] * a_at_run / s_run
    tr[c] = dict(run_rate_spend=s_run, attr_persons_per_week=a_at_run, beta=p["beta"], rho=p["rho"], incremental_share=1 - p["rho"], p_win_current=p["p_new"],
                 contrib_per_win=float(tab[c]["contrib_per_win"]), u_per_person=float(tab[c]["u"]), completion_window=window_completion(c),
                 marginal_attr_persons_per_usd=mar, marginal_incremental_contribution_per_usd=(1 - p["rho"]) * mar * float(tab[c]["u"]),
                 attributed_roas_platform=None)
truth["channels"] = tr; truth["season_last8"] = float(season[last8].mean())
json.dump(truth, open(os.path.join(HERE, "world_truth.json"), "w"), indent=1, default=float)
print({c: round(tr[c]["marginal_incremental_contribution_per_usd"], 3) for c in CH}); print(truth["persons_by_channel"])

import pickle
pickle.dump([dict(pid=p["pid"], channel=p["channel"], cannibal=p["cannibal"], cluster=int(p["cluster"]), t=p["t"], deal_id=p["deal_id"], won=p["won"], rev=(p["job"]["rev"] if p["won"] else None),
                  done=(p["job"]["done"] if p["won"] else None), ghl_ids=p.get("ghl_ids", []), call_ids=p.get("call_ids", []), phone=p["phone"], email=p["email"], last=p["last"]) for p in persons], open(os.path.join(HERE, "persons_truth.pkl"), "wb"))

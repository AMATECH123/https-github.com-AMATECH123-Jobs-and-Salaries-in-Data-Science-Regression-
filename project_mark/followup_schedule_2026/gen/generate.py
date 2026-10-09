"""Generate the Averly Business Activity Survey collection records.
Truth: one observation per return, timed from the earliest dispatch it closes,
returns against dispatches issued inside a burden relief window excluded.
Strata years are typed so that the natural reading (one observation per
dispatch line, everything kept) matches 19 of 24 published means, each single
correction matches 15, and the admissible compilation matches all 24.
"""
import csv, json, math, os, random, datetime as dt
from collections import defaultdict

random.seed(20261009)
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "inputs")

STRATA = [("MFG", "Manufacturing", 4320), ("CON", "Construction", 7200), ("WRT", "Wholesale and retail trade", 2880),
          ("TRS", "Transport and storage", 5040), ("ACC", "Accommodation and food services", 10080), ("PRO", "Professional and technical services", 1900)]
YEARS = [2021, 2022, 2023, 2024, 2025]
# yearly drift factors on the median, by stratum
DRIFT = {"MFG": [1.00, 1.02, 1.03, 1.05, 1.07], "CON": [1.00, 0.98, 1.01, 1.02, 1.00], "WRT": [1.00, 1.01, 1.00, 1.03, 1.04],
         "TRS": [1.00, 1.03, 1.05, 1.06, 1.18], "ACC": [1.00, 0.97, 0.99, 1.00, 1.03], "PRO": [1.00, 1.04, 1.05, 1.06, 1.09]}
SIGMA = {"MFG": 0.62, "CON": 0.58, "WRT": 0.66, "TRS": 0.60, "ACC": 0.55, "PRO": 0.70}

# strata year types for 2021 to 2024: A no effects, B both effects with natural coincidence, C both effects, natural fails
TYPES = {("MFG", 2021): "A", ("MFG", 2022): "C", ("MFG", 2023): "A", ("MFG", 2024): "B",
         ("CON", 2021): "A", ("CON", 2022): "A", ("CON", 2023): "B", ("CON", 2024): "A",
         ("WRT", 2021): "C", ("WRT", 2022): "A", ("WRT", 2023): "A", ("WRT", 2024): "C",
         ("TRS", 2021): "A", ("TRS", 2022): "B", ("TRS", 2023): "A", ("TRS", 2024): "A",
         ("ACC", 2021): "A", ("ACC", 2022): "A", ("ACC", 2023): "C", ("ACC", 2024): "B",
         ("PRO", 2021): "A", ("PRO", 2022): "C", ("PRO", 2023): "A", ("PRO", 2024): "A"}
for s, _, _ in STRATA:
    TYPES[(s, 2025)] = "C"

# Enterprises and reporting units
N_ENT = 3200
enterprises = []
units = []
unit_id = 1
for e in range(1, N_ENT + 1):
    s = random.choice([x[0] for x in STRATA])
    k = random.choices([1, 2, 3, 4], weights=[78, 14, 6, 2])[0]
    ent = {"enterprise_id": f"E{e:05d}", "enterprise_name": f"Enterprise {e:05d}", "stratum": s, "reporting_units": k,
           "region": random.choice(["North", "Central", "South", "Coast", "Uplands"])}
    enterprises.append(ent)
    for u in range(k):
        units.append({"reporting_unit_id": f"RU{unit_id:06d}", "enterprise_id": ent["enterprise_id"], "stratum": s,
                      "site": random.choice(["head office", "plant", "branch", "depot", "yard", "office"])})
        unit_id += 1
ent_by_id = {e["enterprise_id"]: e for e in enterprises}
units_by_ent = defaultdict(list)
for u in units:
    units_by_ent[u["enterprise_id"]].append(u)

def lognorm(median, sigma):
    return int(round(median * math.exp(random.gauss(0, sigma))))

def quarter_start(y, q):
    return dt.datetime(y, 3 * (q - 1) + 1, 1)

def fmt(t):
    return t.strftime("%Y-%m-%d %H:%M")

dispatches = []   # dict rows
receipts = []
links = []
relief = []       # register rows
disp_no = 0; rec_no = 0
# relief windows chosen per (stratum, year) of type B or C, Q1 to Q3 dispatch quarters only (so receipt year = dispatch year)
relief_ents = defaultdict(list)   # (s, y) -> enterprise ids with a window that year
for (s, y), t in TYPES.items():
    if t == "A":
        continue
    cands = [e for e in enterprises if e["stratum"] == s and e["reporting_units"] == 1]
    chosen = random.sample(cands, 110 if y < 2025 else 70)
    for e in chosen:
        start = quarter_start(y, random.choice([1, 2, 3])) + dt.timedelta(days=random.randint(0, 20))
        end = start + dt.timedelta(days=random.randint(75, 160))
        relief.append({"enterprise_id": e["enterprise_id"], "relief_start": start.strftime("%Y-%m-%d"),
                       "relief_end": end.strftime("%Y-%m-%d"),
                       "reason": random.choice(["flood damage", "insolvency administration", "new business relief", "fire at premises", "ownership transfer"])})
        relief_ents[(s, y)].append((e["enterprise_id"], start, end))
relief_by_ent = defaultdict(list)
for r in relief:
    relief_by_ent[r["enterprise_id"]].append((dt.datetime.strptime(r["relief_start"], "%Y-%m-%d"), dt.datetime.strptime(r["relief_end"], "%Y-%m-%d")))

def in_relief(ent_id, ts):
    d = ts.date()
    return any(a.date() <= d <= b.date() for a, b in relief_by_ent.get(ent_id, []))

# tracking for tuning: relief single dispatch rows per (s, y) whose elapsed we may set
relief_rows = defaultdict(list)

for y in YEARS:
    yi = YEARS.index(y)
    for q in (1, 2, 3, 4):
        qs = quarter_start(y, q)
        # rotating sample: about half the units each quarter
        sampled = random.sample(units, 2300)
        by_ent = defaultdict(list)
        for u in sampled:
            by_ent[u["enterprise_id"]].append(u)
        for ent_id, us in by_ent.items():
            ent = ent_by_id[ent_id]; s = ent["stratum"]
            typ = TYPES[(s, y)]
            median = STRATA[[x[0] for x in STRATA].index(s)][2] * DRIFT[s][yi]
            # dispatch timestamps
            base = qs + dt.timedelta(days=random.randint(3, 12), hours=random.randint(7, 17), minutes=random.randint(0, 59))
            combined = (typ != "A") and len(us) > 1 and q <= 3 and random.random() < 0.55
            d_rows = []
            for j, u in enumerate(us):
                ts = base + (dt.timedelta(hours=random.randint(2, 96)) if j > 0 else dt.timedelta(0))
                disp_no += 1
                row = {"dispatch_id": f"D{disp_no:07d}", "reporting_unit_id": u["reporting_unit_id"], "enterprise_id": ent_id,
                       "stratum": s, "reference_quarter": f"{y}Q{q}", "dispatch_ts": ts, "channel": random.choices(["web", "paper"], [88, 12])[0],
                       "reissue_flag": "Y" if random.random() < 0.04 else "N"}
                d_rows.append(row)
            rel = in_relief(ent_id, d_rows[0]["dispatch_ts"])
            if rel and typ == "A":
                rel = False  # cannot happen by construction, kept for safety
            # response or not
            if combined:
                if random.random() < 0.10:
                    dispatches.extend(d_rows); continue
                earliest = min(r["dispatch_ts"] for r in d_rows)
                el = lognorm(median, SIGMA[s])
                el = max(el, (max(r["dispatch_ts"] for r in d_rows) - earliest).seconds // 60 + (max(r["dispatch_ts"] for r in d_rows) - earliest).days * 1440 + 30)
                rts = earliest + dt.timedelta(minutes=el)
                if rts.year != y:
                    rts = dt.datetime(y, 12, 30, 12, 0); 
                rec_no += 1
                rec = {"receipt_id": f"R{rec_no:07d}", "enterprise_id": ent_id, "receipt_ts": rts,
                       "channel": d_rows[0]["channel"], "receiving_office": random.choice(["Averly", "Port Hallam", "Kingsmere"])}
                receipts.append(rec)
                for r in d_rows:
                    links.append({"receipt_id": rec["receipt_id"], "dispatch_id": r["dispatch_id"]})
                dispatches.extend(d_rows)
            else:
                for r in d_rows:
                    dispatches.append(r)
                    if random.random() < 0.12:
                        continue
                    if rel:
                        el = lognorm(median * 2.2, 0.5)
                    else:
                        el = lognorm(median, SIGMA[s])
                    el = max(el, 25)
                    rts = r["dispatch_ts"] + dt.timedelta(minutes=el)
                    if rel and rts.year != y:
                        rts = dt.datetime(y, 12, 30, 12, 0)
                    rec_no += 1
                    rec = {"receipt_id": f"R{rec_no:07d}", "enterprise_id": ent_id, "receipt_ts": rts,
                           "channel": r["channel"], "receiving_office": random.choice(["Averly", "Port Hallam", "Kingsmere"])}
                    receipts.append(rec)
                    links.append({"receipt_id": rec["receipt_id"], "dispatch_id": r["dispatch_id"]})
                    if rel:
                        relief_rows[(s, rts.year)].append((rec, r))

# ---- compile under definitions ----
disp_by_id = {d["dispatch_id"]: d for d in dispatches}
rec_by_id = {r["receipt_id"]: r for r in receipts}
links_by_rec = defaultdict(list)
for l in links:
    links_by_rec[l["receipt_id"]].append(disp_by_id[l["dispatch_id"]])

def minutes(a, b):
    return int((a - b).total_seconds() // 60)

def compile_(grain, exclude_relief, timed="earliest"):
    """returns {(stratum, year): [elapsed...]}"""
    out = defaultdict(list)
    for rec in receipts:
        ds = links_by_rec[rec["receipt_id"]]
        s = ds[0]["stratum"]; y = rec["receipt_ts"].year
        excl = exclude_relief and any(in_relief(rec["enterprise_id"], d["dispatch_ts"]) for d in ds)
        if excl:
            continue
        if grain == "line":
            for d in ds:
                out[(s, y)].append(minutes(rec["receipt_ts"], d["dispatch_ts"]))
        else:
            ref = min(d["dispatch_ts"] for d in ds) if timed == "earliest" else max(d["dispatch_ts"] for d in ds)
            out[(s, y)].append(minutes(rec["receipt_ts"], ref))
    return out

def means(pop):
    return {k: round(sum(v) / len(v)) for k, v in pop.items()}

truth = compile_("receipt", True)
published = {k: v for k, v in means(truth).items() if k[1] <= 2024}

# ---- tune type B strata years so the natural reading coincides ----
for (s, y), t in TYPES.items():
    if t != "B":
        continue
    M = published[(s, y)]
    adm = truth[(s, y)]; n = len(adm); S = sum(adm)
    # natural lines excluding relief: admissible earliest + extra lines
    nat_wo = compile_("line", True)[(s, y)]
    rows = relief_rows[(s, y)]; K = len(rows)
    total_target = M * (len(nat_wo) + K)          # aim at exactly M
    T = total_target - sum(nat_wo)
    avg = T / K
    assert 200 < avg < 60000, (s, y, avg, K)
    # distribute: set each relief receipt's elapsed near avg with small jitter, last one takes the remainder
    vals = [max(60, int(avg + random.randint(-400, 400))) for _ in range(K)]
    vals[-1] = T - sum(vals[:-1])
    assert vals[-1] > 60
    for (rec, d), v in zip(rows, vals):
        rec["receipt_ts"] = d["dispatch_ts"] + dt.timedelta(minutes=v)
        assert rec["receipt_ts"].year == y

truth = compile_("receipt", True)
published = {k: v for k, v in means(truth).items() if k[1] <= 2024}
grid = {
 "line grain, all kept (natural)": compile_("line", False),
 "line grain, relief excluded": compile_("line", True),
 "receipt grain earliest, all kept": compile_("receipt", False),
 "receipt grain latest, relief excluded": compile_("receipt", True, "latest"),
 "receipt grain earliest, relief excluded (admissible)": truth,
}
# distractor: drop reissued dispatches on the admissible definition
def compile_no_reissue():
    out = defaultdict(list)
    for rec in receipts:
        ds = [d for d in links_by_rec[rec["receipt_id"]] if d["reissue_flag"] == "N"]
        if not ds: continue
        s = ds[0]["stratum"]; y = rec["receipt_ts"].year
        if any(in_relief(rec["enterprise_id"], d["dispatch_ts"]) for d in links_by_rec[rec["receipt_id"]]): continue
        out[(s, y)].append(minutes(rec["receipt_ts"], min(d["dispatch_ts"] for d in ds)))
    return out
grid["admissible but reissued dispatches dropped"] = compile_no_reissue()
report = {}
for name, pop in grid.items():
    m = means(pop)
    hits = sum(1 for k, v in published.items() if m.get(k) == v)
    report[name] = hits
    print(f"{name:55s} matches {hits}/24")
assert report["line grain, all kept (natural)"] == 19, report
assert report["receipt grain earliest, relief excluded (admissible)"] == 24
assert report["line grain, relief excluded"] < 19 and report["receipt grain earliest, all kept"] < 19

# ---- write inputs ----
os.makedirs(OUT, exist_ok=True)
def write(name, rows, cols):
    with open(os.path.join(OUT, name), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols); w.writeheader()
        for r in rows:
            w.writerow({c: (fmt(r[c]) if isinstance(r[c], dt.datetime) else r[c]) for c in cols})
random.shuffle(dispatches); dispatches.sort(key=lambda r: r["dispatch_ts"])
receipts.sort(key=lambda r: r["receipt_ts"])
write("dispatch_log.csv", dispatches, ["dispatch_id", "reporting_unit_id", "enterprise_id", "stratum", "reference_quarter", "dispatch_ts", "channel", "reissue_flag"])
write("receipt_log.csv", receipts, ["receipt_id", "enterprise_id", "receipt_ts", "channel", "receiving_office"])
random.shuffle(links)
write("receipt_dispatch_link.csv", links, ["receipt_id", "dispatch_id"])
write("burden_relief_register.csv", sorted(relief, key=lambda r: r["relief_start"]), ["enterprise_id", "relief_start", "relief_end", "reason"])
write("enterprise_register.csv", enterprises, ["enterprise_id", "enterprise_name", "stratum", "reporting_units", "region"])
write("reporting_unit_register.csv", units, ["reporting_unit_id", "enterprise_id", "stratum", "site"])
write("strata.csv", [{"stratum": s, "description": d} for s, d, _ in STRATA], ["stratum", "description"])
pub_rows = [{"reference_year": y, "stratum": s, "mean_elapsed_minutes": published[(s, y)]} for y in YEARS[:4] for s, _, _ in STRATA]
write("published_mean_elapsed_times.csv", pub_rows, ["reference_year", "stratum", "mean_elapsed_minutes"])

# ---- schedules ----
def boundary(vals, a, b):
    v = sorted(vals); r = math.ceil(a * len(v) / b)
    x = v[r - 1]
    return int(math.ceil(x / 10.0) * 10)
def schedule(pop, year):
    out = {}
    allv = []
    for s, _, _ in STRATA:
        v = pop[(s, year)]; allv += v
        out[s] = (boundary(v, 1, 2), boundary(v, 9, 10), len(v))
    out["ALL"] = (boundary(allv, 1, 2), boundary(allv, 9, 10), len(allv))
    return out
sched25 = schedule(truth, 2024)   # standing schedule adopted for 2025 from the 2024 population
sched26 = schedule(truth, 2025)
natural26 = schedule(grid["line grain, all kept (natural)"], 2025)
write("adopted_followup_schedule_2025.csv",
      [{"stratum": s, "share": sh, "boundary_minutes": sched25[s][i], "reminder_day": math.ceil(sched25[s][i] / 1440)}
       for s in [x[0] for x in STRATA] + ["ALL"] for i, sh in enumerate(["p50", "p90"])],
      ["stratum", "share", "boundary_minutes", "reminder_day"])
golden = {"published": {f"{s}_{y}": v for (s, y), v in published.items()}, "grid_matches": report,
          "schedule_2025_standing": sched25, "schedule_2026_admissible": sched26, "schedule_2026_natural": natural26,
          "admissible_2025_count": sum(len(truth[(s, 2025)]) for s, _, _ in STRATA),
          "natural_2025_count": sum(len(grid["line grain, all kept (natural)"][(s, 2025)]) for s, _, _ in STRATA),
          "receipts_total": len(receipts), "dispatches_total": len(dispatches), "links_total": len(links)}
json.dump(golden, open(os.path.join(HERE, "..", "golden", "generation_facts.json"), "w"), indent=1, default=str)
print(json.dumps({k: golden[k] for k in ("schedule_2025_standing", "schedule_2026_admissible", "schedule_2026_natural", "admissible_2025_count", "natural_2025_count", "receipts_total", "dispatches_total")}, indent=1))

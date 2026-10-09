"""Golden solution for the 2026 follow up schedule, working only from inputs/."""
import csv, json, math, os, datetime as dt
from collections import defaultdict
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__)); INP = os.path.join(HERE, "..", "inputs")
P = lambda n: os.path.join(INP, n)
ts = lambda s: dt.datetime.strptime(s, "%Y-%m-%d %H:%M")
disp = {r["dispatch_id"]: r for r in csv.DictReader(open(P("dispatch_log.csv")))}
for d in disp.values(): d["t"] = ts(d["dispatch_ts"])
recs = {r["receipt_id"]: r for r in csv.DictReader(open(P("receipt_log.csv")))}
for r in recs.values(): r["t"] = ts(r["receipt_ts"])
links = defaultdict(list)
for l in csv.DictReader(open(P("receipt_dispatch_link.csv"))): links[l["receipt_id"]].append(disp[l["dispatch_id"]])
relief = defaultdict(list)
for r in csv.DictReader(open(P("burden_relief_register.csv"))): relief[r["enterprise_id"]].append((r["relief_start"], r["relief_end"]))
published = {(r["stratum"], int(r["reference_year"])): int(r["mean_elapsed_minutes"]) for r in csv.DictReader(open(P("published_mean_elapsed_times.csv")))}
standing = {(r["stratum"], r["share"]): int(r["boundary_minutes"]) for r in csv.DictReader(open(P("adopted_followup_schedule_2025.csv")))}
strata = [r["stratum"] for r in csv.DictReader(open(P("strata.csv")))]

def in_relief(ent, t):
    d = t.strftime("%Y-%m-%d"); return any(a <= d <= b for a, b in relief.get(ent, []))
mins = lambda a, b: int((a - b).total_seconds() // 60)

def compile_(grain="receipt", exclude_relief=True, timed="earliest", drop_reissue=False):
    out = defaultdict(list)
    for rid, r in recs.items():
        ds = links[rid]
        if drop_reissue: ds = [d for d in ds if d["reissue_flag"] == "N"]
        if not ds: continue
        if exclude_relief and any(in_relief(r["enterprise_id"], d["t"]) for d in links[rid]): continue
        s, y = ds[0]["stratum"], r["t"].year
        if grain == "line":
            for d in ds: out[(s, y)].append(mins(r["t"], d["t"]))
        else:
            ref = min(d["t"] for d in ds) if timed == "earliest" else max(d["t"] for d in ds)
            out[(s, y)].append(mins(r["t"], ref))
    return out
means = lambda pop: {k: round(sum(v) / len(v)) for k, v in pop.items()}
def matches(pop):
    m = means(pop); return sum(1 for k, v in published.items() if m.get(k) == v), m

candidates = {
 "one observation per dispatch line, every return kept": dict(grain="line", exclude_relief=False),
 "one observation per dispatch line, relief returns excluded": dict(grain="line", exclude_relief=True),
 "one observation per form, timed from the earliest dispatch, every return kept": dict(grain="receipt", exclude_relief=False),
 "one observation per form, timed from the latest dispatch, relief returns excluded": dict(grain="receipt", exclude_relief=True, timed="latest"),
 "one observation per form, timed from the earliest dispatch, reissued dispatches dropped, relief excluded": dict(grain="receipt", exclude_relief=True, drop_reissue=True),
 "one observation per form, timed from the earliest dispatch, relief returns excluded": dict(grain="receipt", exclude_relief=True),
}
results = {}
for name, kw in candidates.items():
    pop = compile_(**kw); n, m = matches(pop); results[name] = (n, pop, m)
    print(f"{n:2d}/24  {name}")
admissible = [n for n, v in results.items() if v[0] == 24]; assert len(admissible) == 1
ADOPT = admissible[0]; pop = results[ADOPT][1]; comp_means = results[ADOPT][2]
rejected = max((n for n in results if results[n][0] < 24), key=lambda n: results[n][0]); rpop = results[rejected][1]

def boundary(vals, a, b):
    v = sorted(vals); return int(math.ceil(v[math.ceil(a * len(v) / b) - 1] / 10.0) * 10)
def schedule(pop):
    out = {}; allv = []
    for s in strata:
        v = pop[(s, 2025)]; allv += v; out[s] = {"p50": boundary(v, 1, 2), "p90": boundary(v, 9, 10)}
    out["ALL"] = {"p50": boundary(allv, 1, 2), "p90": boundary(allv, 9, 10)}; return out
sched = schedule(pop); rsched = schedule(rpop)
rows = []
for s in strata + ["ALL"]:
    for sh in ("p50", "p90"):
        b = sched[s][sh]; st = standing[(s, sh)]
        rows.append({"stratum": s, "share": sh, "boundary_minutes": b, "reminder_day": math.ceil(b / 1440),
                     "standing_2025_boundary_minutes": st, "movement_vs_2025_pct": f"{100 * (b - st) / st:.1f}"})
with open(os.path.join(HERE, "followup_schedule_2026.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
mover = max((r for r in rows if r["stratum"] != "ALL"), key=lambda r: abs(float(r["movement_vs_2025_pct"])))
mb = mover["boundary_minutes"]; day = math.ceil(mb / 1440)
threshold = {"reminder_day": day, "day_holds_up_to_and_including": day * 1440, "previous_day_up_to_and_including": (day - 1) * 1440}
diverg = {f"{s} {sh}": rsched[s][sh] - sched[s][sh] for s in strata + ["ALL"] for sh in ("p50", "p90")}
worst = max(diverg, key=lambda k: abs(diverg[k]))
kept_2025 = sum(len(pop[(s, 2025)]) for s in strata); total_forms_2025 = sum(1 for r in recs.values() if r["t"].year == 2025)
figures = {"adopted_compilation": ADOPT, "matches": {n: v[0] for n, v in results.items()}, "schedule_2026": sched,
           "rejected_closest": rejected, "rejected_schedule": rsched, "divergence_minutes": diverg, "largest_divergence": [worst, diverg[worst]],
           "furthest_mover": mover, "reminder_day_threshold": threshold, "forms_2025_total": total_forms_2025, "forms_2025_kept": kept_2025,
           "published_vs_compiled": {f"{s}_{y}": [published[(s, y)], comp_means[(s, y)]] for (s, y) in sorted(published)},
           "legacy_sheet": "superseded parameter sheet (p60 and p95, 15 minute rounding, pooled two years, questionnaire unit); no use under COS 2019"}
json.dump(figures, open(os.path.join(HERE, "figures.json"), "w"), indent=1)
# chart
allv = [x for s in strata for x in pop[(s, 2025)]]
fig, ax = plt.subplots(figsize=(8, 4.5))
ax.hist([v / 1440 for v in allv], bins=120, range=(0, 30), color="#9ecae1", edgecolor="none")
for sh, c in (("p50", "#d62728"), ("p90", "#ff7f0e")):
    ax.axvline(sched["ALL"][sh] / 1440, color=c, lw=1.8, label=f"survey wide {sh}: {sched['ALL'][sh]:,} minutes (day {math.ceil(sched['ALL'][sh] / 1440)})")
ax.set_xlabel("elapsed time from dispatch to receipt, days"); ax.set_ylabel("forms received in 2025")
ax.set_title("Business Activity Survey, elapsed time of admissible 2025 returns, all strata"); ax.legend(); ax.grid(axis="y", alpha=0.3); plt.tight_layout()
fig.savefig(os.path.join(HERE, "elapsed_time_2025.png"), dpi=150); plt.close(fig)
# note
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
ss = getSampleStyleSheet(); body = ss["BodyText"]; body.fontSize = 9.5; body.leading = 12.5
doc = SimpleDocTemplate(os.path.join(HERE, "followup_note_2026.pdf"), pagesize=letter, leftMargin=50, rightMargin=50, topMargin=48, bottomMargin=48)
Pg = lambda s: Paragraph(s, body)
def tbl(data, widths=None):
    t = Table(data, hAlign="LEFT", colWidths=widths); t.setStyle(TableStyle([("FONTSIZE", (0, 0), (-1, -1), 8.2), ("LINEBELOW", (0, 0), (-1, 0), 0.6, colors.black), ("ALIGN", (1, 1), (-1, -1), "RIGHT"), ("BOTTOMPADDING", (0, 0), (-1, -1), 2), ("TOPPADDING", (0, 0), (-1, -1), 2)])); return t
story = [Paragraph("Business Activity Survey: follow up schedule for 2026", ss["Heading2"]),
 Pg(f"<b>Schedule adopted.</b> Table 1 is the schedule put to the Board, compiled under COS 2019 from the returns received in 2025 on the only compilation that reproduces all 24 published means: {ADOPT}. It keeps {kept_2025:,} of the {total_forms_2025:,} forms received in 2025."),
 Spacer(1, 4), tbl([["Stratum", "p50 boundary", "day", "p90 boundary", "day", "2025 p50", "2025 p90", "move p50", "move p90"]] +
   [[s, f"{sched[s]['p50']:,}", math.ceil(sched[s]['p50'] / 1440), f"{sched[s]['p90']:,}", math.ceil(sched[s]['p90'] / 1440), f"{standing[(s, 'p50')]:,}", f"{standing[(s, 'p90')]:,}",
     f"{100 * (sched[s]['p50'] - standing[(s, 'p50')]) / standing[(s, 'p50')]:+.1f}%", f"{100 * (sched[s]['p90'] - standing[(s, 'p90')]) / standing[(s, 'p90')]:+.1f}%"] for s in strata + ["ALL"]]),
 Spacer(1, 6),
 Pg("<b>Compilation basis.</b> Elapsed time is whole minutes from dispatch to receipt, counted in the year of receipt (clause 2). The standard does not say what the observation is or which returns count, so both were settled by clause 6: each reading of the records was run back over 2021 to 2024 and compared with the Bulletin. "
    "One observation per form received, timed from the earliest dispatch the form closes (enterprises with several reporting units return one combined form), with forms excluded where the dispatch fell inside the enterprise's burden relief window (register dates, both ends inclusive), reproduces every published mean to the minute. "
    f"The reading the record layout invites, one observation per dispatch line with every return kept, reproduces {results[rejected][0]} of 24; correcting either the unit or the population alone reproduces {results['one observation per dispatch line, relief returns excluded'][0]} and {results['one observation per form, timed from the earliest dispatch, every return kept'][0]}, so neither correction can be tested on its own. Dropping reissued dispatches reproduces {results['one observation per form, timed from the earliest dispatch, reissued dispatches dropped, relief excluded'][0]}. Boundaries follow clause 4: rank ceiling of a times n over b, no interpolation, rounded up to the next 10 minutes; reminder day is the boundary over 1,440 rounded up."),
 Spacer(1, 4), Pg("<b>Annex A. Published means beside the compiled means, minutes.</b>"),
 tbl([["Stratum", "2021 pub.", "2021 comp.", "diff", "2022 pub.", "2022 comp.", "diff", "2023 pub.", "2023 comp.", "diff", "2024 pub.", "2024 comp.", "diff"]] +
     [[s] + sum([[f"{published[(s, y)]:,}", f"{comp_means[(s, y)]:,}", comp_means[(s, y)] - published[(s, y)]] for y in (2021, 2022, 2023, 2024)], []) for s in strata]),
 Spacer(1, 6),
 Pg(f"<b>Closest reading that does not stand.</b> One observation per dispatch line with every return kept misses five published means (differences of {', '.join(str(results[rejected][2][k] - published[k]) for k in sorted(published) if results[rejected][2][k] != published[k])} minutes) and cannot reach the Board under clause 6.2. Its 2025 schedule parts from the adopted one by: "
    + "; ".join(f"{k} {v:+,}" for k, v in diverg.items()) + f" minutes. The widest gap is {worst}, {diverg[worst]:+,} minutes."),
 Pg(f"<b>Furthest movement.</b> {mover['stratum']} moves furthest against the standing schedule, {mover['movement_vs_2025_pct']} per cent at {mover['share']} ({mover['standing_2025_boundary_minutes']:,} to {mb:,} minutes). Its reminder day is {day}; day {day} holds for any boundary above {threshold['previous_day_up_to_and_including']:,} minutes up to and including {threshold['day_holds_up_to_and_including']:,}, so the boundary would have to fall to {threshold['previous_day_up_to_and_including']:,} or below to come forward a day, or rise above {threshold['day_holds_up_to_and_including']:,} to move out a day."),
 Pg("The 2018 parameter sheet predates the standard (p60 and p95 shares, 15 minute rounding, two pooled years, questionnaire unit) and has no use under COS 2019; the standing schedule is not carried forward by default (clause 6.3), and is not needed, since an admissible compilation exists."),
 Spacer(1, 4), Image(os.path.join(HERE, "elapsed_time_2025.png"), width=440, height=247)]
doc.build(story)
print(json.dumps({k: figures[k] for k in ("schedule_2026", "furthest_mover", "largest_divergence", "reminder_day_threshold", "forms_2025_kept", "forms_2025_total")}, indent=1))

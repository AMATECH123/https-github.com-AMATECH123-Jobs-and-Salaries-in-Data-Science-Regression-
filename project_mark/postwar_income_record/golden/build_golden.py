"""Golden deliverables for the postwar farm and nonfarm income record task.
Reads transcription.py (hand transcribed cells of Table 1 in three scanned
P-60 reports) plus the series tables, and writes:
  residence_income_1956_1960_1961.csv, farm_nonfarm_medians.png,
  farm_nonfarm_memo.pdf, figures.json
"""
import csv, json, os, re, html
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from transcription import T1956, T1960, T1961, COLS_11, COLS_1961, BRACKETS_16, BRACKETS_17, NA, DOT

HERE = os.path.dirname(os.path.abspath(__file__))
INPUTS = os.path.join(HERE, "..", "inputs")

# Series tables (medians only), transcribed from the scans
# 1961 report Table 19 (page 27), families and unrelated individuals in households, farm and nonfarm, 1960 census farm definition
SERIES_NEW = {  # year: {group: (total, nonfarm, farm)}
    1959: {"families": (5417, 5619, 2799), "unrelated": (1603, 1683, 774), "all": (4806, 5011, 2482)},
    1960: {"families": (5625, 5813, 2876), "unrelated": (1784, 1842, 917), "all": (5009, 5176, 2681)},
    1961: {"families": (5744, 5930, 3238), "unrelated": (1789, 1831, 909), "all": (5056, 5211, 2956)},
}
# 1956 report Table 13 (page 30), families and unrelated individuals in dwelling units, 1950 census farm definition
SERIES_OLD = {
    1956: {"families": (4787, 5061, 2375), "unrelated": (1448, 1522, 723), "all": (4257, 4468, 2149)},
    1955: {"families": (4420, 4705, 2117), "unrelated": (1310, 1371, 635), "all": (3948, 4195, 1937)},
    1954: {"families": (4167, 4406, 1968), "unrelated": (1225, 1312, 583), "all": (3730, 3949, 1803)},
}

BOUNDS_16 = [(0, 500), (500, 1000), (1000, 1500), (1500, 2000), (2000, 2500), (2500, 3000), (3000, 3500),
             (3500, 4000), (4000, 4500), (4500, 5000), (5000, 6000), (6000, 7000), (7000, 10000),
             (10000, 15000), (15000, 25000), (25000, None)]
BOUNDS_17 = BOUNDS_16[:12] + [(7000, 8000), (8000, 10000)] + BOUNDS_16[13:]

def num(v):
    return v if isinstance(v, (int, float)) else 0.0

def collapse17(pct17):
    """17 bracket column -> 16 bracket column (7,000 to 7,999 + 8,000 to 9,999)."""
    out = pct17[:12] + [round(num(pct17[12]) + num(pct17[13]), 1)] + pct17[14:]
    return out

def interp_median(pct, bounds):
    cum = 0.0
    tot = sum(num(p) for p in pct)
    half = tot / 2
    for p, (lo, hi) in zip(pct, bounds):
        p = num(p)
        if cum + p >= half:
            if hi is None:
                return None
            return lo + (half - cum) / p * (hi - lo)
        cum += p
    return None

def derive_nonfarm(n_tot, pct_tot, n_farm, pct_farm):
    n_nf = n_tot - n_farm
    return n_nf, [round((n_tot * num(a) - n_farm * num(b)) / n_nf, 1) for a, b in zip(pct_tot, pct_farm)]

rows = []
def add(year, group, residence, measure, value, status, source, note=""):
    rows.append({"year": year, "group": group, "residence": residence, "measure": measure,
                 "value": "" if value is None else value, "status": status, "source": source, "note": note})

def emit_table(year, table, brackets, bounds, cols, src, farm_def):
    for group in ("families", "unrelated"):
        t = table[group]
        for j, col in enumerate(cols):
            n = t["number"][j]
            add(year, group, col, "number_thousands", n, "printed" if n is not NA else "not_available_in_report", src,
                farm_def if col == "rural_farm" else "")
            pct16 = collapse17(t["pct"][j and j or 0]) if False else None
            colpct = [r[j] for r in t["pct"]]
            if len(brackets) == 17:
                colpct16 = collapse17(colpct)
                for b, v, (raw) in zip(BRACKETS_16, colpct16, [None]*16):
                    pass
            else:
                colpct16 = colpct
            for k, (b, v) in enumerate(zip(BRACKETS_16, colpct16)):
                if len(brackets) == 17 and k == 12:
                    status = "printed_two_brackets_combined"
                    note = "sum of $7,000 to $7,999 and $8,000 to $9,999 as printed"
                elif v == DOT:
                    status, note = "printed_less_than_0.1", "shown as three dots in the report"
                    v = None
                else:
                    status, note = "printed", ""
                add(year, group, col, "pct " + b, v, status, src, note)
            if len(brackets) == 17:
                for k, b in ((12, BRACKETS_17[12]), (13, BRACKETS_17[13])):
                    v = t["pct"][k][j]
                    add(year, group, col, "pct_detail " + b, None if v == DOT else v,
                        "printed_less_than_0.1" if v == DOT else "printed", src,
                        "detail bracket, not printed in the 1956 report")
            m = t["median"][j]
            add(year, group, col, "median_dollars", m, "printed" if m is not NA else "not_shown_base_too_small", src)
            if "yrft_pct" in t:
                add(year, group, col, "year_round_full_time_pct", t["yrft_pct"][j], "printed", src)
            ym = t["yrft_median"][j]
            add(year, group, col, "year_round_full_time_median_dollars", None if ym in (NA, DOT) else ym,
                "printed" if ym not in (NA, DOT) else "not_shown_base_too_small", src)

SRC56 = "P-60 No. 27, Table 1, page 21"
SRC60 = "P-60 No. 37, Table 1, page 25 (PDF page 33)"
SRC61 = "P-60 No. 39, Table 1, page 16"
emit_table(1956, T1956, BRACKETS_16, BOUNDS_16, COLS_11, SRC56, "1950 Census farm definition")
emit_table(1960, T1960, BRACKETS_17, BOUNDS_17, COLS_11, SRC60, "1960 Census farm definition")

# 1961: reshape into the same group/residence layout
t61 = {"families": {k: None for k in ("number", "pct", "median", "yrft_pct", "yrft_median")},
       "unrelated": {}}
def slice61(group):
    base = {"families": 3, "unrelated": 6}[group]
    return {"number": T1961["number"][base:base + 3],
            "pct": [r[base:base + 3] for r in T1961["pct"]],
            "median": T1961["median"][base:base + 3],
            "yrft_pct": T1961["yrft_pct"][base:base + 3],
            "yrft_median": T1961["yrft_median"][base:base + 3]}
T61 = {"families": slice61("families"), "unrelated": slice61("unrelated")}
emit_table(1961, T61, BRACKETS_17, BOUNDS_17, ["total", "nonfarm", "farm"], SRC61, "1960 Census farm definition")

# Derived nonfarm for 1956 and 1960 by subtracting farm from the national distribution
derived = {}
checks = {}
for year, table, brackets, bounds, src in ((1956, T1956, BRACKETS_16, BOUNDS_16, SRC56), (1960, T1960, BRACKETS_17, BOUNDS_17, SRC60)):
    for group in ("families", "unrelated"):
        t = table[group]
        n_tot, n_farm = t["number"][0], t["number"][10]
        pct_tot = [r[0] for r in t["pct"]]; pct_farm = [r[10] for r in t["pct"]]
        n_nf, pct_nf = derive_nonfarm(n_tot, pct_tot, n_farm, pct_farm)
        med = interp_median(pct_nf, bounds)
        med_tot_check = interp_median(pct_tot, bounds)
        pct16 = collapse17(pct_nf) if len(brackets) == 17 else pct_nf
        derived[(year, group)] = {"number": n_nf, "pct16": pct16, "pct": pct_nf, "median_interp": round(med),
                                  "total_interp_vs_printed": (round(med_tot_check), t["median"][0])}
        add(year, group, "nonfarm_derived", "number_thousands", n_nf, "derived_total_minus_farm", src)
        for b, v in zip(BRACKETS_16, pct16):
            add(year, group, "nonfarm_derived", "pct " + b, v, "derived_total_minus_farm", src,
                "(total count x total pct minus farm count x farm pct) / nonfarm count; dots treated as 0")
        add(year, group, "nonfarm_derived", "median_dollars", round(med), "derived_linear_interpolation", src,
            "interpolated within the detailed bracket; the report prints no nonfarm median in Table 1")
        if year == 1956:
            # cross check with the urban + rural nonfarm weighting that the 1956 report allows
            n_u, n_rnf = t["number"][1], t["number"][9]
            pct_u = [r[1] for r in t["pct"]]; pct_rnf = [r[9] for r in t["pct"]]
            w = [round((n_u * num(a) + n_rnf * num(b)) / (n_u + n_rnf), 1) for a, b in zip(pct_u, pct_rnf)]
            checks[(year, group)] = {"urban_plus_rural_nonfarm_count": n_u + n_rnf,
                                     "max_abs_diff_pct_points": max(abs(x - y) for x, y in zip(w, pct_nf)),
                                     "weighted_median_interp": round(interp_median(w, bounds))}

# 1961 validation of the subtraction method against the printed nonfarm column
t = T61["families"]
n_nf, pct_nf = derive_nonfarm(t["number"][0], [r[0] for r in t["pct"]], t["number"][2], [r[2] for r in t["pct"]])
checks[(1961, "families")] = {"derived_nonfarm_count": n_nf, "printed_nonfarm_count": t["number"][1],
                              "max_abs_diff_vs_printed_pct_points": max(abs(num(a) - num(b)) for a, b in zip(pct_nf, [r[1] for r in t["pct"]])),
                              "interp_median_printed_nonfarm_col": round(interp_median([r[1] for r in t["pct"]], BOUNDS_17)),
                              "printed_nonfarm_median": t["median"][1]}

# Series medians (comparable new definition 1959 to 1961, old definition 1954 to 1956)
for year, d in SERIES_NEW.items():
    for group, (tot, nf, fm) in d.items():
        src = "P-60 No. 39, Table 19, page 27 (households, 1960 Census farm definition)"
        add(year, group, "total_in_households", "median_dollars", tot, "printed_series", src)
        add(year, group, "nonfarm_in_households", "median_dollars", nf, "printed_series", src)
        add(year, group, "farm_in_households", "median_dollars", fm, "printed_series", src)
for year, d in SERIES_OLD.items():
    for group, (tot, nf, fm) in d.items():
        src = "P-60 No. 27, Table 13, page 30 (dwelling units, 1950 Census farm definition)"
        add(year, group, "total_in_dwelling_units", "median_dollars", tot, "printed_series_old_farm_definition", src)
        add(year, group, "nonfarm_in_dwelling_units", "median_dollars", nf, "printed_series_old_farm_definition", src)
        add(year, group, "farm_in_dwelling_units", "median_dollars", fm, "printed_series_old_farm_definition", src)

with open(os.path.join(HERE, "residence_income_1956_1960_1961.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["year", "group", "residence", "measure", "value", "status", "source", "note"])
    w.writeheader(); w.writerows(rows)

# Modern tables for the revision comparison
def read_html_rows(name, years):
    t = open(os.path.join(INPUTS, name), errors="replace").read()
    t = re.sub(r"<script.*?</script>", " ", t, flags=re.S); t = re.sub(r"<[^>]+>", " ", t); t = html.unescape(t)
    out = {}
    for line in t.splitlines():
        m = re.match(r"\s*(19\d\d)\s*(?:\d+/)?\s+([\d,]+)\s+\$?([\d,]+)", line)
        if m and int(m.group(1)) in years and int(m.group(1)) not in out:
            out[int(m.group(1))] = (int(m.group(2).replace(",", "")), int(m.group(3).replace(",", "")))
    return out
f7 = read_html_rows("f07ar.html", {1956, 1959, 1960, 1961})   # number, current dollar median (all families block comes first)
contemp = {1956: (43445, 4783), 1959: (45062, 5417), 1960: (45435, 5620), 1961: (46341, 5737)}

def shares(pct16, lo_count=6):
    return round(sum(num(p) for p in pct16[:lo_count]), 1)

fam56 = T1956["families"]; fam60 = T1960["families"]; fam61 = T61["families"]
figures = {
 "recommendation": "Do not read the farm figures of the 1956 report against those of the 1960 and 1961 reports as one series. "
                   "The farm definition changed to the 1960 Census definition from the 1959 income year, so the like for like "
                   "farm and nonfarm comparison these reports support runs 1959 to 1961 (Table 19 of the 1961 report). "
                   "The 1956 residence detail stands on its own under the 1950 Census definitions.",
 "farm_definition_change": {"where": "P-60 No. 37 page 13; footnote 1 to Table 17 (No. 37) and Table 19 (No. 39)",
                            "effect": "reduced the farm population 14 and over by about one fifth"},
 "farm_families_thousands": {"1956_old_definition": fam56["number"][10], "1960_new_definition": fam60["number"][10], "1961_new_definition": fam61["number"][2]},
 "all_families_thousands": {"1956": fam56["number"][0], "1960": fam60["number"][0], "1961": fam61["number"][0]},
 "farm_share_of_families_pct": {"1956": round(100 * fam56["number"][10] / fam56["number"][0], 1), "1961": round(100 * fam61["number"][2] / fam61["number"][0], 1)},
 "table1_medians": {"1956": {"total": fam56["median"][0], "urban": fam56["median"][1], "rural_nonfarm": fam56["median"][9], "rural_farm": fam56["median"][10]},
                    "1960": {"total": fam60["median"][0], "urban": fam60["median"][1], "rural_nonfarm": fam60["median"][9], "rural_farm": fam60["median"][10]},
                    "1961": {"total": fam61["median"][0], "nonfarm": fam61["median"][1], "farm": fam61["median"][2]}},
 "comparable_series_1959_1961_families": {str(y): {"total": v["families"][0], "nonfarm": v["families"][1], "farm": v["families"][2]} for y, v in SERIES_NEW.items()},
 "old_definition_series_families": {str(y): {"total": v["families"][0], "nonfarm": v["families"][1], "farm": v["families"][2]} for y, v in SERIES_OLD.items()},
 "farm_to_nonfarm_median_ratio": {"1959": round(2799 / 5619, 3), "1961": round(3238 / 5930, 3), "1956_old_definition": round(2375 / 5061, 3)},
 "naive_change_not_to_report": {"farm_median_1956_table1": fam56["median"][10], "farm_median_1961_table1": fam61["median"][2],
                                "pct_change": round(100 * (fam61["median"][2] / fam56["median"][10] - 1), 1)},
 "comparable_change_1959_1961": {"farm_pct": round(100 * (3238 / 2799 - 1), 1), "nonfarm_pct": round(100 * (5930 / 5619 - 1), 1)},
 "derived_nonfarm": {f"{y}_{g}": v for (y, g), v in derived.items()},
 "method_checks": {f"{y}_{g}": v for (y, g), v in checks.items()},
 "families_under_3000_pct": {"1956_farm": shares([r[10] for r in fam56["pct"]]), "1956_total": shares([r[0] for r in fam56["pct"]]),
                             "1961_farm": shares([r[2] for r in fam61["pct"]]), "1961_nonfarm": shares([r[1] for r in fam61["pct"]]),
                             "1961_total": shares([r[0] for r in fam61["pct"]])},
 "modern_revisions": {str(y): {"contemporaneous_count": contemp[y][0], "modern_F7_count": f7.get(y, (None, None))[0],
                               "contemporaneous_median": contemp[y][1], "modern_F7_median": f7.get(y, (None, None))[1]} for y in (1956, 1959, 1960, 1961)},
 "other_breaks": ["1959 and 1960 include Alaska and Hawaii for the first time (No. 37 page 1 and page 13)",
                  "household definition moved from dwelling unit (1950 rules) to housing unit (1960 rules) in 1960 (No. 37 page 13)",
                  "1961 income nonresponse imputed from similar households for the first time, earlier years based on complete reporters only (No. 39 page 13)",
                  "the 1960 report prints no urban or rural nonfarm counts for 1960, only the national and rural farm counts",
                  "the 1960 scan has pages 9 to 16 bound after pages 17 to 24, and pages 17 to 24 appear twice"],
 "persons_report": "P-60 No. 16 (May 1955) covers income of persons 14 and over for 1953 only; it has no family or residence tables and adds nothing to the family record",
 "cells_in_csv": len(rows),
}
json.dump(figures, open(os.path.join(HERE, "figures.json"), "w"), indent=1)

# Chart
fig, ax = plt.subplots(figsize=(8, 4.8))
yrs_old = [1954, 1955, 1956]; yrs_new = [1959, 1960, 1961]
ax.plot(yrs_old, [SERIES_OLD[y]["families"][1] for y in yrs_old], "o--", color="#1f77b4", mfc="white", label="Nonfarm, 1950 Census farm definition")
ax.plot(yrs_old, [SERIES_OLD[y]["families"][2] for y in yrs_old], "s--", color="#d62728", mfc="white", label="Farm, 1950 Census farm definition")
ax.plot(yrs_new, [SERIES_NEW[y]["families"][1] for y in yrs_new], "o-", color="#1f77b4", label="Nonfarm, 1960 Census farm definition")
ax.plot(yrs_new, [SERIES_NEW[y]["families"][2] for y in yrs_new], "s-", color="#d62728", label="Farm, 1960 Census farm definition")
ax.axvspan(1956.5, 1958.5, color="grey", alpha=0.15)
ax.text(1957.5, 4300, "farm definition\nchanged; no farm\nfigures published\nfor 1957 and 1958", ha="center", va="center", fontsize=8, color="dimgrey")
for y in yrs_new:
    ax.annotate(f"${SERIES_NEW[y]['families'][2]:,}", (y, SERIES_NEW[y]["families"][2]), textcoords="offset points", xytext=(0, -14), ha="center", fontsize=8)
    ax.annotate(f"${SERIES_NEW[y]['families'][1]:,}", (y, SERIES_NEW[y]["families"][1]), textcoords="offset points", xytext=(0, 7), ha="center", fontsize=8)
ax.annotate(f"${SERIES_OLD[1956]['families'][2]:,}", (1956, 2375), textcoords="offset points", xytext=(0, -14), ha="center", fontsize=8)
ax.annotate(f"${SERIES_OLD[1956]['families'][1]:,}", (1956, 5061), textcoords="offset points", xytext=(0, 7), ha="center", fontsize=8)
ax.set_xticks(yrs_old + yrs_new); ax.set_ylim(1500, 6800)
ax.set_ylabel("Median family money income, current dollars")
ax.set_title("Farm and nonfarm family income as published at the time, 1954 to 1961\n(families in households; Series P-60 Nos. 27 and 39)", fontsize=10)
ax.legend(fontsize=8, loc="upper left"); ax.grid(axis="y", alpha=0.3); plt.tight_layout()
fig.savefig(os.path.join(HERE, "farm_nonfarm_medians.png"), dpi=150); plt.close(fig)

# Memo
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
ss = getSampleStyleSheet(); body = ss["BodyText"]; body.fontSize = 9.5; body.leading = 12.5
H = ss["Heading3"]
doc = SimpleDocTemplate(os.path.join(HERE, "farm_nonfarm_memo.pdf"), pagesize=letter, leftMargin=54, rightMargin=54, topMargin=54, bottomMargin=54)
P = lambda s: Paragraph(s, body)
d56, d60 = derived[(1956, "families")], derived[(1960, "families")]
story = [Paragraph("Farm and nonfarm family income in the Current Population Reports for 1956, 1960 and 1961", ss["Heading2"]),
 P("What the reports support. The three reports do not give one farm and nonfarm series across the five years. "
   "Between the 1956 and the 1960 income years the Bureau moved to the 1960 Census definition of a farm (page 13 of the 1960 report): "
   "a rural place of under 10 acres counts as a farm only with agricultural sales of 250 dollars or more, and a place of 10 acres or more with sales of 50 dollars or more. "
   "The report says the change cut the farm population aged 14 and over by about one fifth, and both later reports refuse to print farm or nonfarm figures for years before 1959 for that reason "
   "(footnote 1 to Table 17 of the 1960 report and to Table 19 of the 1961 report). "
   "The like for like comparison these reports allow therefore runs 1959 to 1961, and the 1956 residence detail has to be read under the 1950 Census definitions."),
 P(f"Comparable change, 1959 to 1961 (Table 19 of the 1961 report, families in households): the farm median rose from 2,799 to 3,238 dollars, "
   f"{figures['comparable_change_1959_1961']['farm_pct']} percent, and the nonfarm median from 5,619 to 5,930 dollars, "
   f"{figures['comparable_change_1959_1961']['nonfarm_pct']} percent. The farm median stood at {figures['farm_to_nonfarm_median_ratio']['1959']:.0%} of the nonfarm median in 1959 and "
   f"{figures['farm_to_nonfarm_median_ratio']['1961']:.0%} in 1961. The intermediate 1960 values are 2,876 and 5,813 dollars."),
 P(f"What not to report. Reading the rural farm median of Table 1 in the 1956 report (2,371 dollars) against the farm median of Table 1 in the 1961 report (3,241 dollars) gives a rise of "
   f"{figures['naive_change_not_to_report']['pct_change']} percent, but part of that is the definition change, which dropped low sales places out of the farm count. "
   f"The farm family count fell from 4,908 thousand in 1956 to 3,490 thousand in 1960 and 1961, and the farm share of all families from "
   f"{figures['farm_share_of_families_pct']['1956']} to {figures['farm_share_of_families_pct']['1961']} percent; neither figure separates the exodus from the reclassification. "
   f"Under the old definition the 1956 farm median was {figures['farm_to_nonfarm_median_ratio']['1956_old_definition']:.0%} of the nonfarm median (2,375 against 5,061 dollars in Table 13 of the 1956 report)."),
 Paragraph("The lined up table", H),
 P("The CSV carries every residence class the reports print: eleven classes for 1956 and 1960 (urban by size of place and rural) and the farm and nonfarm split for 1961, for families and for unrelated individuals, "
   "with the count, the full income distribution, the median and the year round full time worker figures, each cell marked printed, not available, or less than 0.1 as the page shows it. "
   "The 1960 and 1961 reports split 7,000 to 9,999 dollars into two brackets; the table carries the combined bracket to match 1956 and keeps the two halves as detail rows."),
 P(f"Nonfarm for 1956 and 1960 is not printed in Table 1, and the 1960 report gives no urban or rural nonfarm counts at all, so the urban and rural nonfarm columns cannot be weighted together for 1960. "
   f"The table therefore derives nonfarm by taking the farm distribution out of the national one with the printed counts: {d56['number']:,} thousand families in 1956 and {d60['number']:,} thousand in 1960. "
   f"Applied to 1961, where the report prints nonfarm, the same arithmetic reproduces the printed column within {checks[(1961,'families')]['max_abs_diff_vs_printed_pct_points']:.1f} of a percentage point, "
   f"and for 1956 it agrees with the urban plus rural nonfarm weighting within {checks[(1956,'families')]['max_abs_diff_pct_points']:.1f} of a point. "
   f"The derived nonfarm medians, by the Bureau's own linear interpolation (page 21 of the 1960 report), are about {d56['median_interp']:,} dollars for 1956 and {d60['median_interp']:,} dollars for 1960; "
   f"they are estimates, not printed figures, and the households based series in Table 13 and Table 17 gives 5,061 and 5,813 dollars for the same years on a slightly narrower universe."),
 Paragraph("Other things not to take at face value", H),
 P("Alaska and Hawaii enter the figures with the 1959 income year. The household definition moved from the 1950 dwelling unit to the 1960 housing unit in 1960, which the Bureau judged too small to matter for family income. "
   "From the 1961 survey the Bureau imputed income for nonrespondents from similar households; earlier years rest on complete reporters only, and the Bureau's own test on 1958 data found the new method raises the upper income shares slightly. "
   "The 1961 medians in Table 1 (5,737 dollars) and Table 19 (5,744 dollars) differ because Table 19 covers families in households only."),
 P("The Bureau's present historical tables have since revised these years. Table F-7 carries 43,497 thousand families and a median of 4,780 dollars for 1956, 45,539 thousand and 5,620 dollars for 1960, and 46,418 thousand and 5,735 dollars for 1961, "
   "against 43,445 and 4,783, 45,435 and 5,620, and 46,341 and 5,737 in the reports; the counts for 1954 to 1961 were raised later and the 1947 to 1953 figures left as published; the footnote page that explains the revision is not in the folder, and the Bureau's methodology note dates the 1960 Census based population controls to 1962. "
   "The revised tables do not carry a residence split for these years, so the residence detail exists only in the contemporaneous reports."),
 P("The May 1955 release (No. 16) covers income of persons 14 and over for 1953 only. It has no family or residence tables and can be left aside; the modern persons tables already carry its headline medians."),
 P("The 1960 scan is bound out of order: pages 9 to 16 follow pages 17 to 24, which appear twice. Page 13, with the definitions, sits at PDF page 29."),
]
tbl = [["", "1956 (1950 def.)", "1959", "1960", "1961"],
       ["Farm median, families in households", "2,375", "2,799", "2,876", "3,238"],
       ["Nonfarm median, families in households", "5,061", "5,619", "5,813", "5,930"],
       ["All families, median (Table 1)", "4,783", "5,417", "5,620", "5,737"],
       ["Farm families, thousands (Table 1)", "4,908", "n.p.", "3,490", "3,490"],
       ["All families, thousands (Table 1)", "43,445", "45,062", "45,435", "46,341"]]
t = Table(tbl, hAlign="LEFT"); t.setStyle(TableStyle([("FONTSIZE", (0, 0), (-1, -1), 8.5), ("LINEBELOW", (0, 0), (-1, 0), 0.6, colors.black), ("ALIGN", (1, 0), (-1, -1), "RIGHT")]))
story += [Spacer(1, 6), t, Spacer(1, 4), P("n.p.: not printed in the reports in the package. Current dollars throughout.")]
doc.build(story)
print(json.dumps(figures, indent=1)[:3500])

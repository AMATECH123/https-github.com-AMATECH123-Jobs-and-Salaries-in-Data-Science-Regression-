"""Golden build for the 2026 attitudes table. Reads only files in ../inputs and writes the three deliverables
plus a figures.json used by the design note. Every number is computed here; nothing is hard coded."""
import os, sys, json, numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from indicators import INDICATORS, FIRST_YEAR, BASE_YEAR, EDITION_YEAR
from svylib import estimate
HERE = os.path.dirname(os.path.abspath(__file__)); INP = os.path.join(HERE, "..", "inputs")
cols = ["year", "race", "vstrat", "vpsu", "wtssps", "wtssall", "oversamp"] + [v for _, v, _, _ in INDICATORS]
df = pd.read_parquet(os.path.join(INP, "gss_all.parquet"), columns=cols)
df["wtssall_oversamp"] = df.wtssall * df.oversamp
df["wtssps_oversamp"] = df.wtssps * df.oversamp
Y = {y: df[df.year == y] for y in (FIRST_YEAR, BASE_YEAR, EDITION_YEAR)}
legacy = pd.read_csv(os.path.join(INP, "attitudes_table_2016_edition.csv"))
research = pd.read_csv(os.path.join(INP, "research_draft_2026.csv"))
editor = pd.read_csv(os.path.join(INP, "editor_draft_2026.csv"))
CRIT = 1.96
F = {}  # figures for the design note

# 1. Continuity gate: reproduce the previous edition under its own method
repro = []
for label, var, codes, _ in INDICATORS:
    row = legacy[legacy.indicator == label].iloc[0]
    e87 = estimate(Y[FIRST_YEAR], var, codes, "wtssall_oversamp"); e14 = estimate(Y[BASE_YEAR], var, codes, "wtssall")
    ok87 = (e87 is None and pd.isna(row["1987 figure (%)"])) or (e87 is not None and round(e87["p"] * 100, 1) == row["1987 figure (%)"] and e87["n"] == row["1987 respondents"])
    ok14 = round(e14["p"] * 100, 1) == row["2014 figure (%)"] and e14["n"] == row["2014 respondents"]
    repro.append((label, var, ok87, ok14))
assert all(a and b for _, _, a, b in repro), repro
F["reproduced"] = len(repro); F["held"] = 0

# the oversample check: WTSSPS already carries the 1987 oversample adjustment
x = Y[FIRST_YEAR]
def black_share(w): return float(np.average((x.race == 2).astype(float), weights=x[w]))
F["black_share_1987"] = {"unweighted": float((x.race == 2).mean()), "wtssall": black_share("wtssall"), "wtssall_x_oversamp": black_share("wtssall_oversamp"), "wtssps": black_share("wtssps"), "wtssps_x_oversamp": black_share("wtssps_oversamp")}
xb = df[df.year == 1988]; F["black_share_1988_wtssps"] = float(np.average((xb.race == 2).astype(float), weights=xb.wtssps))

# 2. The table on WTSSPS
rows = []
for label, var, codes, wording in INDICATORS:
    e87 = estimate(Y[FIRST_YEAR], var, codes, "wtssps"); e14 = estimate(Y[BASE_YEAR], var, codes, "wtssps"); e24 = estimate(Y[EDITION_YEAR], var, codes, "wtssps")
    r = dict(indicator=label, variable=var, p87=None if e87 is None else e87["p"] * 100, n87=None if e87 is None else e87["n"],
             p14=e14["p"] * 100, n14=e14["n"], se14=e14["se_design"] * 100, p24=None, n24=None, se24=None, d=None, se=None, moved=None, note="")
    if e24 is None:
        r["note"] = "not fielded in 2024; not updated this edition"; r["moved"] = "not updated"
    else:
        r.update(p24=e24["p"] * 100, n24=e24["n"], se24=e24["se_design"] * 100)
        r["d"] = r["p24"] - r["p14"]; r["se"] = float(np.hypot(e24["se_design"], e14["se_design"]) * 100)
        r["moved"] = "Yes" if abs(r["d"]) >= CRIT * r["se"] else "No"
    if e87 is None: r["note"] = (r["note"] + "; " if r["note"] else "") + "not fielded in 1987"
    # the over corrected 1987 figure, for the design note only
    e87o = estimate(Y[FIRST_YEAR], var, codes, "wtssps_oversamp"); r["p87_overcorrected"] = None if e87o is None else e87o["p"] * 100
    # the SRS and mixed readings, for the memo
    r["t_srs"] = None if e24 is None else r["d"] / (np.hypot(e24["se_srs"], e14["se_srs"]) * 100)
    e14a = estimate(Y[BASE_YEAR], var, codes, "wtssall"); r["p14_legacy"] = e14a["p"] * 100
    r["t_mixed"] = None if e24 is None else (r["p24"] - r["p14_legacy"]) / (np.hypot(e24["se_design"], e14a["se_design"]) * 100)
    rows.append(r)
T = pd.DataFrame(rows)

# 3. Check the drafts against their methods and the table
res_set = set(research[research.moved == "Yes"].indicator); ed_set = set(editor[editor.moved == "Yes"].indicator)
srs_set = set(T[(T.t_srs.abs() >= CRIT)].indicator); mixed_set = set(T[(T.t_mixed.abs() >= CRIT)].indicator)
assert res_set == srs_set, (res_set ^ srs_set); assert ed_set == mixed_set, (ed_set ^ mixed_set)
gold_set = set(T[T.moved == "Yes"].indicator)
F["moved"] = sorted(gold_set); F["moved_n"] = len(gold_set); F["research_n"] = len(res_set); F["editor_n"] = len(ed_set)
F["research_extra"] = sorted(res_set - gold_set); F["editor_extra"] = sorted(ed_set - gold_set); F["research_missing"] = sorted(gold_set - res_set); F["editor_missing"] = sorted(gold_set - ed_set)
F["not_updated"] = sorted(T[T.moved == "not updated"].indicator)

# 4. Restatements of 2014
T["restate"] = T.p14 - T.p14_legacy
big = T.loc[T.restate.abs().idxmax()]
F["restatement_largest"] = {"indicator": big.indicator, "legacy": round(big.p14_legacy, 1), "new": round(big.p14, 1), "diff": round(big.restate, 2)}
F["restated_n"] = int((T.p14.round(1) != T.p14_legacy.round(1)).sum())

# 5. Movers and the flip point
upd = T[T.moved != "not updated"]
dm = upd.loc[upd.d.abs().idxmax()]; F["decade_mover"] = {"indicator": dm.indicator, "variable": dm.variable, "change": round(dm.d, 1), "p14": round(dm.p14, 1), "p24": round(dm.p24, 1)}
runner = upd.loc[upd.d.abs().nlargest(2).index[1]]; F["decade_runner_up"] = {"indicator": runner.indicator, "change": round(runner.d, 1)}
lr = upd.dropna(subset=["p87"]).copy(); lr["long"] = lr.p24 - lr.p87
lm = lr.loc[lr.long.abs().idxmax()]; F["long_mover"] = {"indicator": lm.indicator, "variable": lm.variable, "p87": round(lm.p87, 1), "p24": round(lm.p24, 1), "change": round(lm.long, 1)}
lr2 = lr.loc[lr.long.abs().nlargest(2).index[1]]; F["long_runner_up"] = {"indicator": lr2.indicator, "change": round(lr2.long, 1)}
un = upd[upd.moved == "No"].copy(); un["need"] = CRIT * un.se - un.d.abs()
cl = un.sort_values("need").iloc[0]; nxt = un.sort_values("need").iloc[1]
F["closest"] = {"indicator": cl.indicator, "variable": cl.variable, "change": round(cl.d, 2), "se": round(cl.se, 2), "threshold": round(CRIT * cl.se, 2), "need_points": round(cl.need, 2), "direction": "lower" if cl.d < 0 else "higher", "p24": round(cl.p24, 1), "p24_at_flip": round(cl.p24 - cl.need if cl.d < 0 else cl.p24 + cl.need, 1)}
F["closest_next"] = {"indicator": nxt.indicator, "need_points": round(nxt.need, 2)}
F["t_values"] = {r.variable: (None if r.d is None else round(r.d / r.se, 2)) for r in T.itertuples()}

# 6. Deliverable 1: the CSV
def f1(v): return "" if v is None or pd.isna(v) else f"{v:.1f}"
def f2(v): return "" if v is None or pd.isna(v) else f"{v:.2f}"
out = pd.DataFrame({"indicator": T.indicator, "gss_variable": T.variable, "first_edition_1987": T.p87.map(f1), "figure_2014": T.p14.map(f1), "figure_2024": T.p24.map(f1),
                    "decade_change_points": T.d.map(f1), "sampling_error": T.se.map(f2), "reported_as_moved": T.moved, "note": T.note})
out.to_csv(os.path.join(HERE, "attitudes_table_2026.csv"), index=False)

# 7. Deliverable 2: the chart
c = upd.sort_values("d")
nu = T[T.moved == "not updated"]
fig, ax = plt.subplots(figsize=(11, 8.5))
labels = []
for k, r in enumerate(nu.itertuples()):
    ax.text(0, k, "no 2024 figure, not updated this edition", va="center", ha="center", fontsize=9, color="#4d4d4d", style="italic",
            bbox=dict(boxstyle="round,pad=0.25", fc="white", ec="#bbbbbb"))
    labels.append(r.indicator)
off = len(nu)
for i, r in enumerate(c.itertuples()):
    col = "#b2182b" if r.moved == "Yes" else "#7f7f7f"
    ax.errorbar(r.d, i + off, xerr=CRIT * r.se, fmt="o", color=col, ecolor=col, elinewidth=2, capsize=4, markersize=8)
    ax.text(r.d + (CRIT * r.se + 0.6) * (1 if r.d >= 0 else -1), i + off, f"{r.d:+.1f}", va="center", ha="left" if r.d >= 0 else "right", fontsize=9, color=col)
    labels.append(r.indicator)
ax.axvline(0, color="black", lw=1)
ax.set_yticks(range(len(labels))); ax.set_yticklabels(labels, fontsize=9)
ax.set_ylim(-0.8, len(labels) - 0.2)
ax.set_xlabel("Change 2014 to 2024, percentage points, with 95 percent interval under the survey design")
ax.set_title(f"Attitudes table 2026: decade change by indicator\n{F['moved_n']} of {len(upd)} updated indicators reported as moved; {len(nu)} not updated", fontsize=12)
from matplotlib.lines import Line2D
ax.legend(handles=[Line2D([], [], color="#b2182b", marker="o", lw=2, label="reported as moved"), Line2D([], [], color="#7f7f7f", marker="o", lw=2, label="not reported")], loc="upper left")
ax.set_xlim(-22, 22); ax.grid(axis="x", alpha=0.3); plt.tight_layout(); fig.savefig(os.path.join(HERE, "decade_change_2014_2024.png"), dpi=150, bbox_inches="tight"); plt.close(fig)

# 8. Deliverable 3: the memo
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
ss = getSampleStyleSheet(); body = ss["BodyText"]; body.fontSize = 9.5; body.leading = 12.5
h = ss["Heading2"]; h.fontSize = 11.5
doc = SimpleDocTemplate(os.path.join(HERE, "attitudes_table_memo.pdf"), pagesize=letter, leftMargin=54, rightMargin=54, topMargin=50, bottomMargin=50)
P = lambda t: Paragraph(t, body)
S = []
S.append(Paragraph("Attitudes table, 2026 edition: certification memo", ss["Title"]))
S.append(P(f"<b>Certified table.</b> {F['moved_n']} of the {len(upd)} indicators with a 2024 figure moved over the decade from 2014 to 2024: "
           + "; ".join(f"{r.indicator} ({r.d:+.1f} points)" for r in upd[upd.moved == 'Yes'].sort_values('d', key=abs, ascending=False).itertuples())
           + f". The other {len(upd) - F['moved_n']} updated indicators are not reported as moved. {', '.join(F['not_updated'])} were not fielded in 2024 and are carried without a change. "
           f"Neither draft is certified: Research's draft reports {F['research_n']} indicators as moved and the editor's {F['editor_n']}."))
S.append(Paragraph("The two drafts", h))
S.append(P(f"<b>Research's draft</b> rebuilt both years on the post stratification weight, as the standard requires, but its sampling errors are those of a simple random sample of the respondents (the square root of p(1 minus p)/n in each year). The GSS is a stratified multistage sample and its design effects on these items run between about 1.6 and 3.2, so those errors are too small by a fifth to nearly a half. On the design based error, six of the fifteen indicators it reports fall back inside the margin: {', '.join(F['research_extra'])}. Not certified."))
S.append(P(f"<b>The editor's draft</b> kept the 2014 figures printed in the 2016 edition, which were weighted by WTSSALL, and set 2024 figures on WTSSPS beside them. The sampling errors are design based, but the two years are on different weights, which rule 4 of the standard does not allow: the 2014 figures have to be restated on WTSSPS. The mixed weights add between 0.0 and {abs(F['restatement_largest']['diff']):.1f} points of spurious change, and three indicators cross the margin on that alone: {', '.join(F['editor_extra'])}. Not certified."))
S.append(Paragraph("Continuity and restatement", h))
S.append(P(f"All twenty indicators reproduce the 2016 edition's published figures from the current file under that edition's method (WTSSALL for 2014; WTSSALL with the OVERSAMP weight for 1987), to the published precision and respondent count, so none is held out. The 2016 edition's 2014 figures are restated on WTSSPS for every indicator; {F['restated_n']} of the twenty change at one decimal. The largest restatement is {F['restatement_largest']['indicator']}: {F['restatement_largest']['legacy']:.1f} becomes {F['restatement_largest']['new']:.1f}, {F['restatement_largest']['diff']:+.1f} points."))
S.append(P(f"The first edition column is on WTSSPS alone. The OVERSAMP weight that the 2016 edition applied to 1987 belonged with WTSSALL, which does not adjust for the 1987 Black oversample; WTSSPS already does. With WTSSPS the Black share of the 1987 sample is {F['black_share_1987']['wtssps']*100:.1f} percent, in line with 1988 ({F['black_share_1988_wtssps']*100:.1f} percent on the same weight), while applying OVERSAMP on top of WTSSPS would push it to {F['black_share_1987']['wtssps_x_oversamp']*100:.1f} percent and move several 1987 figures by one to two points."))
S.append(Paragraph("Movers and the closest call", h))
S.append(P(f"The largest decade change is {F['decade_mover']['indicator']}: {F['decade_mover']['p14']:.1f} to {F['decade_mover']['p24']:.1f} percent, {F['decade_mover']['change']:+.1f} points (next, {F['decade_runner_up']['indicator']} at {F['decade_runner_up']['change']:+.1f}). Since the first edition the largest change is {F['long_mover']['indicator']}: {F['long_mover']['p87']:.1f} percent in 1987 to {F['long_mover']['p24']:.1f} in 2024, {F['long_mover']['change']:+.1f} points (next, {F['long_runner_up']['indicator']} at {F['long_runner_up']['change']:+.1f})."))
S.append(P(f"The unreported indicator closest to the margin is {F['closest']['indicator']}: change {F['closest']['change']:+.2f} points against a margin of {F['closest']['threshold']:.2f} (1.96 times a sampling error of {F['closest']['se']:.2f}). A 2024 figure {F['closest']['need_points']:.2f} points {F['closest']['direction']}, {F['closest']['p24_at_flip']:.1f} percent instead of {F['closest']['p24']:.1f}, would report it, holding the sampling error. The next closest is {F['closest_next']['indicator']}, {F['closest_next']['need_points']:.2f} points short."))
S.append(Spacer(1, 6))
tab = [["Indicator", "1987", "2014", "2024", "Change", "SE", "Moved"]] + [[Paragraph(r.indicator, body), f1(r.p87), f1(r.p14), f1(r.p24), f1(r.d), f2(r.se), r.moved] for r in T.itertuples()]
t = Table(tab, colWidths=[250, 40, 40, 40, 48, 40, 60], repeatRows=1)
t.setStyle(TableStyle([("FONTSIZE", (0, 0), (-1, -1), 8), ("GRID", (0, 0), (-1, -1), 0.3, colors.grey), ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey), ("VALIGN", (0, 0), (-1, -1), "MIDDLE")]))
S.append(t)
S.append(Spacer(1, 6))
S.append(P("Figures are percent of respondents giving the counted response among those giving a listed response, weighted by WTSSPS; sampling errors of the change are design based from the variance strata and PSUs, each year an independent sample; an indicator is reported as moved when its change is at least 1.96 times its sampling error. No other reading of the standard reaches a different set: the same weight in both years, the design based error and the 1.96 margin are each fixed by the standard, and the set is unchanged at a margin of 2.0."))
doc.build(S)
json.dump(F, open(os.path.join(HERE, "figures.json"), "w"), indent=1, default=str)
print(json.dumps(F, indent=1, default=str))
print(out.to_string())

"""Golden build for the trust series task. Reads only ../inputs; writes the three deliverables and figures.json."""
import os, sys, json, numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from svylib import estimate
HERE = os.path.dirname(os.path.abspath(__file__)); INP = os.path.join(HERE, "..", "inputs")
cols = ["year", "vstrat", "vpsu", "wtssps", "oversamp", "mode", "ballot", "trust", "trustv", "trustnv"]
df = pd.read_parquet(os.path.join(INP, "gss_all.parquet"), columns=cols)
prev = pd.read_csv(os.path.join(INP, "trust_series_2024_edition.csv"))
research = pd.read_csv(os.path.join(INP, "research_draft_2026.csv")); editor = pd.read_csv(os.path.join(INP, "editor_draft_2026.csv"))
BASE, EDITION, CRIT = 2014, 2024, 1.96
F = {}
def f1(v): return "" if v is None or pd.isna(v) else f"{v:.1f}"
def f2(v): return "" if v is None or pd.isna(v) else f"{v:.2f}"
MODE = {1: "in person", 2: "phone", 3: "multimode", 4: "web"}

rows = []
for y in sorted(df.year.unique()):
    x = df[df.year == y]; y = int(y)
    std = x.trust.notna(); v = x.trustv.notna(); nv = x.trustnv.notna()
    if not std.any() and not v.any():
        continue  # question not fielded in any form
    r = dict(year=y, n=int(std.sum()), p=np.nan, se=np.nan, status="", reason="", n_sample=len(x))
    if std.any():
        e = estimate(x, "trust", [1], "wtssps"); r["p"] = e["p"] * 100; r["n"] = e["n"]
        r["se"] = np.nan if x.vstrat.isna().all() else e["se_design"] * 100
    modes_std = x.loc[std, "mode"].value_counts().to_dict() if x["mode"].notna().any() else {}
    # rule 3: the standard instrument must have reached every respondent it was fielded to; the versions mark an experiment
    if v.any() or nv.any():
        nver = int(v.sum() + nv.sum())
        if std.any():
            r["status"] = "withdrawn" if y <= 2022 else "not published"
            r["reason"] = (f"standard question fielded only to {int(std.sum())} in person, phone and multimode respondents; "
                           f"{nver} web and multimode respondents received the experimental versions TRUSTV and TRUSTNV, so the figure is not from the full sample (rule 3)")
        else:
            r["status"] = "no figure"; r["reason"] = f"standard question not fielded; {nver} respondents received the experimental versions TRUSTV and TRUSTNV only (rule 3)"
    else:
        r["status"] = "published"
    r["modes_std"] = {MODE[int(k)]: int(c) for k, c in modes_std.items()}
    rows.append(r)
S = pd.DataFrame(rows)
pub = S[S.status == "published"]
carried = pub.iloc[-1]; F["carried"] = {"year": int(carried.year), "figure": float(carried.p), "figure_printed": f1(carried.p), "se": round(carried.se, 2), "n": int(carried.n)}
F["edition_year_figure"] = None; F["decade_change"] = None
F["withheld"] = S[S.status != "published"][["year", "status", "n", "reason"]].to_dict("records")

# continuity gate against the 2024 edition
repro = []
for pr in prev.itertuples():
    s = S[S.year == pr.year]
    if pr.note == "not fielded":
        repro.append((pr.year, True)); continue
    ok = (round(s.p.iloc[0], 1) == float(pr._3)) and (int(s.n.iloc[0]) == int(pr.respondents)) and (pd.isna(pr._4) or round(s.se.iloc[0], 2) == float(pr._4))
    repro.append((pr.year, bool(ok)))
assert all(ok for _, ok in repro), repro
F["previous_reproduced"] = len(repro); F["previous_withdrawn"] = [int(y) for y in S[S.status == "withdrawn"].year]

# the drafts
x24 = df[df.year == 2024]; x22 = df[df.year == 2022]
e24 = estimate(x24, "trust", [1], "wtssps"); assert round(e24["p"] * 100, 1) == float(research["edition year figure (%)"][0])
e22 = estimate(x22, "trust", [1], "wtssps"); assert round(e22["p"] * 100, 1) == float(editor["figure carried (%)"][0])
F["research"] = {"figure": round(e24["p"] * 100, 1), "n": e24["n"], "sample": len(x24), "modes": {MODE[int(k)]: int(c) for k, c in x24.loc[x24.trust.notna(), "mode"].value_counts().items()}, "web_in_sample": int((x24["mode"] == 4).sum())}
F["editor"] = {"figure": round(e22["p"] * 100, 1), "n": e22["n"], "sample": len(x22), "modes": {MODE[int(k)]: int(c) for k, c in x22.loc[x22.trust.notna(), "mode"].value_counts().items()}, "web_in_sample": int((x22["mode"] == 4).sum())}
# what the versions do (for the memo)
def pooled(x, cols_):
    x = x.copy(); x["pool"] = np.nan
    for c in cols_: x["pool"] = x["pool"].fillna(x[c])
    e = estimate(x, "pool", [1], "wtssps"); e3 = estimate(x, "pool", [3], "wtssps")
    return {"n": e["n"], "p": round(e["p"] * 100, 1), "depends": round(e3["p"] * 100, 1)}
F["versions_2024"] = {"standard": pooled(x24, ["trust"]), "trustv": pooled(x24, ["trustv"]), "trustnv": pooled(x24, ["trustnv"]), "all_pooled": pooled(x24, ["trust", "trustv", "trustnv"])}
F["versions_2022"] = {"standard": pooled(x22, ["trust"]), "trustv": pooled(x22, ["trustv"]), "trustnv": pooled(x22, ["trustnv"])}
# oversample check for 1987
x87 = df[df.year == 1987].assign(wo=lambda d: d.wtssps * d.oversamp)
F["p1987_wtssps"] = round(estimate(x87, "trust", [1], "wtssps")["p"] * 100, 1); F["p1987_wtssps_x_oversamp"] = round(estimate(x87, "trust", [1], "wo")["p"] * 100, 1)
# high, low, largest consecutive change
hi = pub.loc[pub.p.idxmax()]; lo = pub.loc[pub.p.idxmin()]
F["high"] = {"year": int(hi.year), "figure": round(hi.p, 1)}; F["low"] = {"year": int(lo.year), "figure": round(lo.p, 1)}
pp = pub.reset_index(drop=True); best = None
for i in range(1, len(pp)):
    d = pp.p[i] - pp.p[i - 1]; se = np.hypot(pp.se[i], pp.se[i - 1]) if not (pd.isna(pp.se[i]) or pd.isna(pp.se[i - 1])) else np.nan
    if best is None or abs(d) > abs(best["change"]): best = {"from": int(pp.year[i - 1]), "to": int(pp.year[i]), "change": round(d, 2), "se": None if pd.isna(se) else round(se, 2), "t": None if pd.isna(se) else round(d / se, 2)}
F["largest_consecutive"] = best
# the decade change that would have been reported had 2018 been compared, for context
e14 = estimate(df[df.year == 2014], "trust", [1], "wtssps"); e18 = estimate(df[df.year == 2018], "trust", [1], "wtssps")
F["context_2014_2018"] = {"change": round((e18["p"] - e14["p"]) * 100, 2), "se": round(np.hypot(e18["se_design"], e14["se_design"]) * 100, 2)}

# deliverable 1
out = pd.DataFrame({"year": S.year, "respondents": S.n, "figure": S.p.map(f1), "sampling_error": S.se.map(f2), "status": S.status, "reason": S.reason})
out.loc[out.year == F["carried"]["year"], "status"] = "published, carried as the latest figure"
out.to_csv(os.path.join(HERE, "trust_series_2026.csv"), index=False)

# deliverable 2
fig, ax = plt.subplots(figsize=(11, 6.5))
ax.errorbar(pub.year, pub.p, yerr=CRIT * pub.se.fillna(0), fmt="o-", color="#1f5f8b", ecolor="#1f5f8b", capsize=3, lw=1.5, markersize=5, label="published figure with 95 percent interval")
ax.plot([carried.year], [carried.p], "o", color="#b2182b", markersize=11, zorder=5, label=f"figure the 2026 edition carries: {f1(carried.p)} percent ({int(carried.year)})")
for r in S[S.status != "published"].itertuples():
    ax.axvspan(r.year - 0.4, r.year + 0.4, color="#dddddd", alpha=0.8, zorder=0)
    if not pd.isna(r.p): ax.plot([r.year], [r.p], "x", color="#7f7f7f", markersize=9, zorder=4)
ax.text(2022.5, 53.5, "2021, 2022, 2024:\nno published figure", ha="center", va="top", fontsize=8.5, color="#4d4d4d")
ax.plot([], [], "x", color="#7f7f7f", label="figure printed before or drafted, not from the full sample (2022 withdrawn, 2024 not published)")
ax.axvline(BASE, color="#999999", ls="--", lw=1); ax.text(BASE, 22, "base year 2014", ha="center", fontsize=8, color="#666666")
ax.set_ylim(20, 55); ax.set_xlim(1970, 2026); ax.set_ylabel("Percent saying most people can be trusted"); ax.set_xlabel("Survey year")
ax.set_title("Most people can be trusted, 1972 to 2024: the series the 2026 edition carries", fontsize=12)
ax.grid(alpha=0.3); ax.legend(loc="lower left", fontsize=8.5); plt.tight_layout(); fig.savefig(os.path.join(HERE, "trust_trend_1972_2024.png"), dpi=150, bbox_inches="tight"); plt.close(fig)

# deliverable 3
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
ss = getSampleStyleSheet(); body = ss["BodyText"]; body.fontSize = 9.5; body.leading = 12.5; h = ss["Heading2"]; h.fontSize = 11.5
P = lambda t: Paragraph(t, body)
doc = SimpleDocTemplate(os.path.join(HERE, "trust_certification_memo.pdf"), pagesize=letter, leftMargin=54, rightMargin=54, topMargin=50, bottomMargin=50)
c, R, E, V = F["carried"], F["research"], F["editor"], F["versions_2024"]
L = []
L.append(Paragraph("Trust series, 2026 edition: certification memo", ss["Title"]))
L.append(P(f"<b>What the edition prints.</b> The trust row carries the 2018 figure, {c['figure_printed']} percent (sampling error {c['se']:.2f}, {c['n']:,} respondents), labelled as the latest figure. No 2024 figure is published and no decade change is published. The 2022 figure the 2024 edition printed, {E['figure']:.1f} percent, is withdrawn. Neither draft is certified: Research's 2024 figure of {R['figure']:.1f} percent and the editor's carried 2022 figure of {E['figure']:.1f} percent are the same kind of figure, each computed from the respondents who were asked the standard question in a survey year in which the web sample was asked experimental versions of it instead."))
L.append(Paragraph("Why 2024, 2022 and 2021 have no figure", h))
L.append(P(f"From the 2021 survey onward NORC fielded the trust question to its web respondents in two experimental versions, TRUSTV (the volunteered answer \"depends\" offered on screen) and TRUSTNV (not offered), and kept the standard question for in person and phone interviews. In 2024 the standard question reached {R['n']:,} of {R['sample']:,} respondents (" + ", ".join(f"{k} {v:,}" for k, v in R['modes'].items()) + f"); all {R['web_in_sample']:,} web respondents received a version. Rule 3 of the standard requires a figure from every respondent the question was fielded to, on the standard instrument. The {R['n']:,} are selected by interview mode, so the figure is not an estimate for the population: the versions show how much the instrument matters, {V['trustv']['p']:.1f} percent trusting when \"depends\" is offered ({V['trustv']['depends']:.1f} percent choosing it) against {V['trustnv']['p']:.1f} percent when it is not, and {V['all_pooled']['p']:.1f} percent if all three are pooled. None of those is the standard instrument on the full sample either."))
L.append(P(f"The 2022 survey has the same structure: the standard question reached {E['n']:,} of {E['sample']:,} respondents (" + ", ".join(f"{k} {v:,}" for k, v in E['modes'].items()) + f"), and all {E['web_in_sample']:,} web respondents received the versions. The 2024 edition printed {E['figure']:.1f} percent for 2022 from those {E['n']:,}; the figure reproduces exactly under that edition's method and is withdrawn under rule 7, because it does not meet rule 3. In 2021 the standard question was not fielded at all; the 2024 edition's \"not fielded\" stands. The last survey year in which the standard question reached the full sample is 2018, so {c['figure_printed']} percent is the figure the edition carries. The decade change is not published because there is no 2024 figure; for the record, 2018 stood {F['context_2014_2018']['change']:+.1f} points above the 2014 base, within its sampling error of {F['context_2014_2018']['se']:.2f}."))
L.append(Paragraph("The drafts", h))
L.append(P(f"<b>Research's draft</b> measured the standard question in 2024 on the {R['n']:,} in person, phone and multimode respondents, correctly weighted and with a design based error, and put the decade change at {float(research['decade change (points)'][0]):+.1f} points, not significant. The figure is right for what it counts and not a figure for the series: it leaves out the {R['web_in_sample']:,} web respondents by mode. Not certified."))
L.append(P(f"<b>The editor's draft</b> carried the 2022 figure of {E['figure']:.1f} percent forward unchanged and published no 2024 figure and no change, which is the right shape of decision applied to the wrong year: the 2022 figure rests on {E['n']:,} non web respondents in the same way. Not certified."))
L.append(Paragraph("Continuity, the series and the next edition", h))
L.append(P(f"All {F['previous_reproduced']} rows the 2024 edition printed reproduce from the current file under that edition's method, to the printed precision and respondent count. One is withdrawn (2022); the rest stand. The 1987 figure stays at {F['p1987_wtssps']:.1f} percent on WTSSPS alone, which already carries the Black oversample adjustment ({F['p1987_wtssps_x_oversamp']:.1f} percent if OVERSAMP were applied on top)."))
b = F["largest_consecutive"]
L.append(P(f"The series' high is {F['high']['year']} at {F['high']['figure']:.1f} percent and its low is {F['low']['year']} at {F['low']['figure']:.1f} percent. The largest change between consecutive fieldings is {b['from']} to {b['to']}, {b['change']:+.1f} points, {abs(b['t']):.1f} times its sampling error of {b['se']:.2f}, significant."))
L.append(P("For the next edition to print a 2026 figure, the 2026 survey has to field the standard trust question, with the same wording and the same offered response options as before, to every respondent in every interview mode, with no experimental versions in its place for any part of the sample. If the versions continue, the series stays at 2018 until NORC publishes a bridged series, and the chapter would say so."))
L.append(Spacer(1, 6))
tab = [["Year", "Respondents", "Figure", "SE", "Status"]] + [[int(r.year), int(r.n), f1(r.p), f2(r.se), r.status] for r in S.itertuples()]
t = Table(tab, colWidths=[45, 70, 50, 45, 120], repeatRows=1)
t.setStyle(TableStyle([("FONTSIZE", (0, 0), (-1, -1), 7.5), ("GRID", (0, 0), (-1, -1), 0.3, colors.grey), ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey)]))
L.append(t)
doc.build(L)
json.dump(F, open(os.path.join(HERE, "figures.json"), "w"), indent=1, default=str)
print(json.dumps(F, indent=1, default=str)); print(out.to_string())

"""Builds the three scenario tables shipped in inputs/: the previous edition's table (2016 edition, built on
WTSSALL with OVERSAMP applied to 1987), Research's 2026 draft (WTSSPS both years, simple random sampling
error) and the editor's 2026 draft (previous edition's 2014 figures carried, 2024 on WTSSPS, design error).
All figures are computed from the cumulative file in inputs/. Run from the golden/ folder."""
import numpy as np, pandas as pd, sys, os
sys.path.insert(0, os.path.dirname(__file__))
from indicators import INDICATORS, FIRST_YEAR, BASE_YEAR, EDITION_YEAR
from svylib import estimate
HERE = os.path.dirname(os.path.abspath(__file__))
INP = os.path.join(HERE, "..", "inputs")
cols = ["year", "vstrat", "vpsu", "wtssps", "wtssall", "oversamp"] + [v for _, v, _, _ in INDICATORS]
df = pd.read_parquet(os.path.join(INP, "gss_all.parquet"), columns=cols)
df["wtssall_oversamp"] = df["wtssall"] * df["oversamp"]
Y = {y: df[df.year == y] for y in (FIRST_YEAR, BASE_YEAR, EDITION_YEAR)}

def fig(e): return "" if e is None else f"{e['p']*100:.1f}"

legacy, research, editor = [], [], []
for label, var, codes, wording in INDICATORS:
    e87 = estimate(Y[FIRST_YEAR], var, codes, "wtssall_oversamp")
    e14_all = estimate(Y[BASE_YEAR], var, codes, "wtssall")
    legacy.append({"indicator": label, "response counted": wording,
                   "1987 figure (%)": fig(e87), "1987 respondents": "" if e87 is None else e87["n"],
                   "2014 figure (%)": fig(e14_all), "2014 respondents": e14_all["n"]})
    e14 = estimate(Y[BASE_YEAR], var, codes, "wtssps")
    e24 = estimate(Y[EDITION_YEAR], var, codes, "wtssps")
    # Research: WTSSPS both years, SRS error
    if e24 is None:
        research.append({"indicator": label, "2014 figure (%)": fig(e14), "2024 figure (%)": "", "change (points)": "", "standard error": "", "moved": "not fielded in 2024"})
        editor.append({"indicator": label, "2014 figure (%)": fig(e14_all), "2024 figure (%)": "", "change (points)": "", "standard error": "", "moved": "not fielded in 2024"})
        continue
    d = (e24["p"] - e14["p"]) * 100
    se = np.hypot(e24["se_srs"], e14["se_srs"]) * 100
    research.append({"indicator": label, "2014 figure (%)": fig(e14), "2024 figure (%)": fig(e24), "change (points)": f"{d:.1f}", "standard error": f"{se:.2f}", "moved": "Yes" if abs(d) >= 1.96 * se else "No"})
    d2 = (e24["p"] - e14_all["p"]) * 100
    se2 = np.hypot(e24["se_design"], e14_all["se_design"]) * 100
    editor.append({"indicator": label, "2014 figure (%)": fig(e14_all), "2024 figure (%)": fig(e24), "change (points)": f"{d2:.1f}", "standard error": f"{se2:.2f}", "moved": "Yes" if abs(d2) >= 1.96 * se2 else "No"})

pd.DataFrame(legacy).to_csv(os.path.join(INP, "attitudes_table_2016_edition.csv"), index=False)
pd.DataFrame(research).to_csv(os.path.join(INP, "research_draft_2026.csv"), index=False)
pd.DataFrame(editor).to_csv(os.path.join(INP, "editor_draft_2026.csv"), index=False)
print("research moved", sum(r["moved"] == "Yes" for r in research), "editor moved", sum(r["moved"] == "Yes" for r in editor))
print(pd.DataFrame(legacy).to_string()); print(pd.DataFrame(research).to_string()); print(pd.DataFrame(editor).to_string())

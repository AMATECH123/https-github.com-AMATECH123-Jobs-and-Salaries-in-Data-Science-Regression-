"""Builds the scenario tables in inputs/: the trust series as the 2024 edition printed it (every fielded year
1972 to 2022 from the TRUST variable on WTSSPS), Research's 2026 draft (2024 from TRUST alone) and the editor's
2026 draft (2022 carried forward). Run from golden/."""
import os, sys, numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from svylib import estimate
HERE = os.path.dirname(os.path.abspath(__file__)); INP = os.path.join(HERE, "..", "inputs")
df = pd.read_parquet(os.path.join(INP, "gss_all.parquet"), columns=["year", "vstrat", "vpsu", "wtssps", "trust"])
rows = []
for y in sorted(df.year.unique()):
    x = df[df.year == y]
    if y > 2022: continue
    e = estimate(x, "trust", [1], "wtssps") if x.trust.notna().any() else None
    if e is None:
        if y == 2021: rows.append({"year": int(y), "respondents": "", "figure (%)": "", "sampling error": "", "note": "not fielded"})
        continue
    se = "" if x.vstrat.isna().all() else f"{e['se_design']*100:.2f}"
    rows.append({"year": int(y), "respondents": e["n"], "figure (%)": f"{e['p']*100:.1f}", "sampling error": se, "note": ""})
pd.DataFrame(rows).to_csv(os.path.join(INP, "trust_series_2024_edition.csv"), index=False)
x14 = df[df.year == 2014]; x24 = df[df.year == 2024]; x22 = df[df.year == 2022]
e14 = estimate(x14, "trust", [1], "wtssps"); e24 = estimate(x24, "trust", [1], "wtssps"); e22 = estimate(x22, "trust", [1], "wtssps")
d = (e24["p"] - e14["p"]) * 100; se = np.hypot(e24["se_design"], e14["se_design"]) * 100
pd.DataFrame([{"edition year figure (%)": f"{e24['p']*100:.1f}", "figure year": 2024, "respondents": e24["n"], "sampling error": f"{e24['se_design']*100:.2f}",
               "2014 figure (%)": f"{e14['p']*100:.1f}", "decade change (points)": f"{d:.1f}", "change sampling error": f"{se:.2f}", "change significant": "Yes" if abs(d) >= 1.96 * se else "No"}]).to_csv(os.path.join(INP, "research_draft_2026.csv"), index=False)
pd.DataFrame([{"figure carried (%)": f"{e22['p']*100:.1f}", "figure year": 2022, "respondents": e22["n"], "sampling error": f"{e22['se_design']*100:.2f}",
               "2024 figure": "none, carried from 2022", "decade change": "none published"}]).to_csv(os.path.join(INP, "editor_draft_2026.csv"), index=False)
print(open(os.path.join(INP, "trust_series_2024_edition.csv")).read()); print(open(os.path.join(INP, "research_draft_2026.csv")).read()); print(open(os.path.join(INP, "editor_draft_2026.csv")).read())

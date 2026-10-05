import json, os, pandas as pd
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt, textwrap
HERE = os.path.dirname(os.path.abspath(__file__)); OUTD = os.path.join(HERE, "reference_outputs")
T = pd.DataFrame(json.load(open(os.path.join(HERE, "world_truth.json")))["truth"])
NAME = {"S1": "Duplicate payment", "S2": "Employee-linked vendor", "S3": "Split approvals", "S4": "Receipts shortfall", "S5": "Bank change diversion", "S6": "Shell vendor", "S7": "Contract overrun", "S8": "Blocked vendor"}
FREEZE = {"S2", "S4", "S5", "S6"}
reg = pd.DataFrame(dict(case_id=[f"CASE-{i+1:03d}" for i in range(len(T))], vendor_id=T.vendor, scheme=T.scheme.map(NAME), document_ids=T.docs.map(lambda d: ";".join(d)), exposure_usd=T.exposure, action=T.scheme.map(lambda s: "freeze vendor" if s in FREEZE else "recover and fix control")))
reg.to_csv(os.path.join(OUTD, "reference_register.csv"), index=False)
tot = T.exposure.sum(); by = T.groupby("scheme").exposure.sum()
fig = plt.figure(figsize=(8.27, 11.69)); fig.text(0.07, 0.95, "AP forensic review: USD %s confirmed exposure" % f"{tot:,.0f}", fontsize=16, weight="bold")
top = T.sort_values("exposure", ascending=False).head(3); fz = sorted(set(T[T.scheme.isin(FREEZE)].vendor))
y = 0.91
for line in [f"{len(T)} confirmed cases across 8 tests. Freeze {len(fz)} vendors today: " + ", ".join(fz) + ".",
             "Deal with first: " + "; ".join(f"{r.vendor} ({NAME[r.scheme]}, USD {r.exposure:,.0f})" for r in top.itertuples()) + ".",
             "Cleared as not exposure: disclosed related-party vendors, voided or refunded duplicate payments, short shipments fully credited, verified bank changes, amended contracts, block overrides, near-limit invoices that are single or approved at a higher limit."]:
    for l in textwrap.wrap(line, 105): fig.text(0.07, y, l, fontsize=9.5); y -= 0.018
    y -= 0.008
ax = fig.add_axes([0.1, 0.45, 0.8, 0.3]); ax.barh([NAME[s] for s in by.index][::-1], by.values[::-1], color="#3b6ea5"); ax.set_xlabel("Confirmed exposure (USD)"); ax.spines[["top", "right"]].set_visible(False)
for i, v in enumerate(by.values[::-1]): ax.text(v, i, f" {v:,.0f}", va="center", fontsize=8)
fig.savefig(os.path.join(OUTD, "reference_memo.pdf")); print("ok", round(tot, 2))

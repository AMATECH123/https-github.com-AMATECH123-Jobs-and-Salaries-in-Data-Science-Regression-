import sys, re, json, os, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); IN = os.path.join(HERE, "..", "inputs")
T = json.load(open(os.path.join(HERE, "world_truth.json")))["truth"]
vm = pd.read_excel(os.path.join(IN, "vendor_master.xlsx"), sheet_name="vendors"); leg = {}
for r in vm.itertuples(): leg[r.vendor_id] = r.legacy_vendor_id; leg[r.legacy_vendor_id] = r.legacy_vendor_id
W = {"S1": 6, "S2": 6, "S3": 6, "S4": 6, "S5": 6, "S6": 5, "S7": 5, "S8": 5}
def score(path):
    d = pd.read_csv(path, dtype=str).fillna(""); rows = []
    for r in d.to_dict("records"):
        txt = " ".join(str(v) for v in r.values())
        ids = set(re.findall(r"\b(?:AP|PM)\d{7}\b", txt)); vend = {leg[x] for x in re.findall(r"\b(?:VN-\d{6}|V\d{5})\b", txt) if x in leg}
        amt = None
        for c in d.columns:
            if re.search(r"exposure|amount|risk|dollar|usd", c, re.I):
                try: amt = float(re.sub(r"[^0-9.\-]", "", r[c])); break
                except ValueError: pass
        rows.append((ids, vend, amt))
    out = {}; matched_rows = set()
    for s in W:
        ts = [t for t in T if t["scheme"] == s]; got = 0.0
        for t in ts:
            tid = set(t["docs"]) | {t["key"]}
            hit = [i for i, (ids, vend, amt) in enumerate(rows) if (s in ("S1", "S3") and (ids & tid)) or (s not in ("S1", "S3") and t["vendor"] in vend)]
            if hit:
                matched_rows |= set(hit); a = sum((rows[i][2] or 0) for i in hit)
                got += 1.0 if abs(a - t["exposure"]) <= 0.10 * t["exposure"] else 0.5
        out[s] = (got, len(ts))
    tv = {t["vendor"] for t in T}; td = {x for t in T for x in t["docs"]}
    fp = [i for i, (ids, vend, amt) in enumerate(rows) if i not in matched_rows and not (vend & tv) and not (ids & td)]
    prec = 1 - len(fp) / max(1, len(rows)); pts = {s: round(W[s] * out[s][0] / out[s][1], 2) for s in W}; ppts = 5 if prec >= 0.9 else 3 if prec >= 0.8 else 1 if prec >= 0.6 else 0
    print("recall by scheme:", {s: f"{out[s][0]:.1f}/{out[s][1]}" for s in W}); print("rows", len(rows), "false-positive rows", len(fp), "precision", round(prec, 3))
    print("D1 points:", pts, "precision pts", ppts, "TOTAL", round(sum(pts.values()) + ppts, 1), "/ 50")
if __name__ == "__main__":
    for p in sys.argv[1:]: score(p)

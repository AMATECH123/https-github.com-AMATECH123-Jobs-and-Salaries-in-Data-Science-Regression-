"""Scores a tax workpaper CSV + memo PDF text against world_truth.json by searching for the key amounts."""
import sys, re, json, os, pandas as pd, pdfplumber
HERE = os.path.dirname(os.path.abspath(__file__)); T = json.load(open(os.path.join(HERE, "world_truth.json"))); A = T["adjustments"]
def nums(text):
    out = []
    for m in re.findall(r"\(?-?\$?\s?\d[\d,]*\.?\d*\)?", text):
        s = re.sub(r"[^\d.]", "", m)
        if s.count(".") > 1 or not s: continue
        try: out.append(float(s))
        except ValueError: pass
    return out
def has(pool, v, tol=0.0025, floor=500.0):
    v = abs(v); t = max(v * tol, 1.0) if v > floor else max(v * 0.02, 1.0)
    return any(abs(x - v) <= t for x in pool)
def score(csv_path, pdf_path):
    c = pd.read_csv(csv_path, dtype=str).fillna(""); ctext = " ".join(" ".join(r) for r in c.values.tolist()); cp = nums(ctext)
    ptext = " ".join((pg.extract_text() or "") for pg in pdfplumber.open(pdf_path).pages); pp = nums(ptext); both = cp + pp
    perm = A["meals_50pct"] + A["entertainment"] + A["fines_penalties"] + A["lobbying"] + A["key_man_life"] + A["gifts_over_25"] + A["transit_passes"]
    dep = T["depreciation"]
    items = [
     ("final: balance due", 30, has(both, T["balance_due"])), ("book pre-tax income", 6, has(both, T["book_pretax"])),
     ("taxable income before NOL", 6, has(both, T["ti_after_163j"])), ("taxable income", 4, has(both, T["taxable_income"])),
     ("permanent items total (or each item present)", 4, has(both, perm) or sum(has(both, A[k]) for k in ("meals_50pct", "entertainment", "fines_penalties", "lobbying", "key_man_life", "gifts_over_25", "transit_passes")) >= 6),
     ("bad debt adjustment", 3, has(both, A["bad_debts"])), ("accrual adjustment (2.5 month rule, owner bonus)", 5, has(both, A["accruals"])),
     ("depreciation adjustment", 7, has(both, A["depreciation"])), ("section 179 deduction 812,454", 2, has(both, dep["s179_taken"], 0.001)),
     ("section 1245 gain adjustment", 3, has(both, A["disposals"])), ("section 174 net adjustment", 6, has(both, A["sec174"])),
     ("163(j) deductible interest or disallowed amount", 5, has(both, T["sec163j"]["limit"]) or has(both, T["sec163j"]["disallowed_added_back"])), ("NOL deduction", 5, has(both, T["nol_deduction"])),
     ("tax before payments", 2, has(both, T["tax"])), ("tax payments 185,000", 1, has(both, T["payments"], 0.001)), ("mid-quarter convention stated", 1, bool(re.search(r"mid[- ]?quarter", ptext + ctext, re.I)))]
    got = 0
    for n, w, ok in items: print(f"  {'OK ' if ok else 'MISS'} {w:2d}  {n}"); got += w if ok else 0
    print("TOTAL (auto items)", got, "/ 90   (+10 for memo form/chart, graded by reading)")
if __name__ == "__main__": score(sys.argv[1], sys.argv[2])

"""Reference solution: reads ONLY ../inputs and reproduces the 2024 federal computation."""
import os, re, json, datetime as dt
import pandas as pd, pdfplumber
from docx import Document
import taxlaw as T
HERE = os.path.dirname(os.path.abspath(__file__)); IN = os.path.join(HERE, "..", "inputs"); OUTD = os.path.join(HERE, "reference_outputs"); os.makedirs(OUTD, exist_ok=True)
P = lambda f: os.path.join(IN, f)
gl = pd.read_csv(P("gl_transactions.csv"), dtype=str); gl["debit"] = gl.debit.astype(float); gl["credit"] = gl.credit.astype(float)
coa = pd.read_excel(P("chart_of_accounts.xlsx"), dtype=str); typ = dict(zip(coa.account_code, coa.account_type)); gl["type"] = gl.account_code.map(typ)
pl = gl[gl.type.isin(["revenue", "cogs", "opex", "other", "tax"]) & (gl.account_code != "8100")]
book_pretax = float((pl.credit - pl.debit).sum())
desc = gl.description.str.lower()
# permanent items
m = gl[gl.account_code == "6400"]; md = m.description.str.lower()
meals50 = float(m[md.str.startswith("client dinner") | md.str.startswith("meals - travel per diem")].debit.sum())
ent0 = float(m[md.str.startswith("client entertainment") | md.str.startswith("suite rental")].debit.sum())
party = float(m[md.str.startswith("holiday party") | md.str.contains("summer picnic")].debit.sum()); assert abs(meals50 + ent0 + party - m.debit.sum()) < 0.01
fines = float(gl[gl.account_code == "6720"].debit.sum())
lob = 0.0
for r in gl[gl.account_code == "6710"].itertuples():
    mt = re.search(r"notice: (\d+)% of dues used for lobbying", r.description); lob += r.debit * int(mt.group(1)) / 100.0
keyman = float(gl[desc.str.contains("key-man life")].debit.sum())
gifts = {}
for x in gl[gl.account_code == "6420"].itertuples():
    nm = re.match(r"Client gift - (.+?) \(", x.description).group(1); gifts[nm] = gifts.get(nm, 0.0) + x.debit
gift_excess = sum(max(0.0, v - T.GIFT_LIMIT_PER_RECIPIENT) for v in gifts.values()); transit = float(gl[gl.account_code == "6210"].debit.sum())
bad_prov = float(gl[gl.account_code == "6810"].debit.sum()); writeoffs = float(gl[(gl.account_code == "1210") & desc.str.contains("write-off")].debit.sum())
# accruals
acc = pd.read_excel(P("accrual_schedule.xlsx"), dtype=str); acc["accrued_amount"] = acc.accrued_amount.astype(float); acc["paid"] = pd.to_datetime(acc.paid_date, errors="coerce")
book_acc = tax_acc = 0.0
for r in acc.itertuples():
    owner = r.payee_is_majority_shareholder == "Y"; paid = r.paid
    if r.accrued_year == "2024":
        book_acc += r.accrued_amount
        if (not owner) and pd.notna(paid) and paid <= pd.Timestamp(T.ACCRUAL_DEADLINE): tax_acc += r.accrued_amount
        elif owner and pd.notna(paid) and paid.year == 2024: tax_acc += r.accrued_amount
    elif r.accrued_year == "2023" and pd.notna(paid) and paid.year == 2024:
        deducted_2023 = (not owner) and paid <= pd.Timestamp("2024-03-15")
        if not deducted_2023: tax_acc += r.accrued_amount
# fixed assets
fa = pd.read_excel(P("fixed_assets.xlsx"), sheet_name=None); assets = fa["assets"]; disp = fa["disposals_2024"]
assets["in_service"] = pd.to_datetime(assets.in_service_date); book_depr = float(gl[gl.account_code == "6900"].debit.sum())
exist = float(assets[assets.in_service.dt.year < 2024].tax_depreciation_2024_prior_workpapers.fillna(0).sum())
new = assets[assets.in_service.dt.year == 2024].copy()
book_threshold = float(re.search(r"capitalise purchases of USD ([\d,]+) and above", " ".join(p.text for p in Document(P("cfo_election_memo.docx")).paragraphs)).group(1).replace(",", ""))
small = new[(new.cost < book_threshold) & (new.cost <= T.DE_MINIMIS_AFS)]; big = new[~new.index.isin(small.index)]   # safe harbor only for items expensed on the books
adds = []
for r in big.itertuples():
    d = r.description.lower()
    kind = "building" if str(r.tax_class_years) == "39" else "li" if "land improvements" in d else "auto" if (pd.notna(r.gvwr_lbs) and r.gvwr_lbs <= 6000) else "suv" if (pd.notna(r.gvwr_lbs) and r.gvwr_lbs > 6000) else "std"
    adds.append(dict(id=r.asset_id, cls=str(r.tax_class_years), cost=float(r.cost), date=r.in_service.date(), kind=kind, name=r.description))
memo = " ".join(p.text for p in Document(P("cfo_election_memo.docx")).paragraphs)
order = []
for k in range(1, 5):
    mt = re.search(rf"\({k}\) ([^,]+?)(?: \(|,| up)", memo)
    if mt:
        nm = mt.group(1).strip(); hit = [a for a in adds if a["name"].lower().startswith(nm.lower())]
        if hit: order.append((hit[0]["id"], hit[0]["cost"]))
per, summ = T.depreciation_additions(adds, order); tax_depr = exist + sum(v["total"] for v in per.values()) + float(small.cost.sum())
disp["tax_gain"] = disp.proceeds - disp.adjusted_tax_basis; disp["book_gain"] = disp.proceeds - disp.book_net_value
# section 174
pay = pd.read_csv(P("payroll_register.csv")); pay["q"] = pay.annual_wages_2024 * pay.pct_time_qualified_research
dom_w = float(pay[pay.location == "US"].q.sum()); for_w = float(pay[pay.location == "IN"].q.sum())
ctr = pd.DataFrame(json.load(open(P("contractor_invoices.json")))["invoices"]); dl = ctr.description.str.lower()
isre = dl.str.contains("software development|prototype engineering|development of|design and build") & ~dl.str.contains("quality control|routine inspection|market research|efficiency survey")
dom_c = float(ctr[isre & (ctr.vendor_country == "US")].amount.sum()); for_c = float(ctr[isre & (ctr.vendor_country == "IN")].amount.sum())
proto = float(gl[gl.account_code == "6510"].debit.sum())
dom_re = dom_w + dom_c + proto; for_re = for_w + for_c
txt = " ".join((pg.extract_text() or "") for pg in pdfplumber.open(P("prior_year_workpapers.pdf")).pages).replace("\n", " ")
num = lambda s: float(s.replace(",", ""))
r22 = re.search(r"2022 ([\d,]+) ([\d,]+)", txt); r23 = re.search(r"2023 ([\d,]+) ([\d,]+)", txt)
nol_bal = num(re.search(r"1 January 2024: USD ([\d,]+)", txt).group(1)); cf = num(re.search(r"2024: USD ([\d,]+)\.", txt).group(1)) if re.search(r"carried forward from 2023 to 2024: USD ([\d,]+)", txt) is None else num(re.search(r"carried forward from 2023 to 2024: USD ([\d,]+)", txt).group(1))
amort_dom, amort_for = T.re_amortization(dom_re, for_re, num(r23.group(1)), num(r23.group(2)), num(r22.group(1)), num(r22.group(2)))
adj = dict(meals_50pct=0.5 * meals50, entertainment=ent0, fines_penalties=fines, lobbying=lob, key_man_life=keyman, gifts_over_25=gift_excess, transit_passes=transit, bad_debts=bad_prov - writeoffs, accruals=book_acc - tax_acc, depreciation=book_depr - tax_depr,
           disposals=float(disp.tax_gain.sum() - disp.book_gain.sum()), sec174=(dom_re + for_re) - (amort_dom + amort_for))
ti0 = book_pretax + sum(adj.values())
bie = float(gl[gl.account_code == "7000"].debit.sum()); bii = float(gl[gl.account_code == "7100"].credit.sum())
j = T.sec163j(ti0, bie, bii, cf); ti1 = ti0 + bie - j["deductible"]; n = T.nol(ti1, nol_bal); taxable = ti1 - n["deduction"]; tax = taxable * T.RATE
paid = float(pd.read_csv(P("tax_payments.csv")).amount.sum()); balance = tax - paid
res = dict(book_pretax=book_pretax, adjustments=adj, ti_before_163j=ti0, sec163j=j, ti_after_163j=ti1, nol_balance=nol_bal, nol_deduction=n["deduction"], taxable_income=taxable, tax=tax, payments=paid, balance_due=balance,
           depreciation=dict(summ=summ, new_total=sum(v["total"] for v in per.values()), existing=exist, de_minimis=float(small.cost.sum())), re=dict(dom=dom_re, foreign=for_re, amort_dom=amort_dom, amort_for=amort_for))
json.dump(res, open(os.path.join(OUTD, "reference_result.json"), "w"), indent=1, default=str)
T0 = json.load(open(os.path.join(HERE, "world_truth.json")))
print("balance due: reference", round(balance, 2), "truth", T0["balance_due"], "| taxable", round(taxable, 2), T0["taxable_income"], "| book pretax", round(book_pretax, 2), T0["book_pretax"])
for k, v in adj.items(): print(f"  {k:18s} ref {v:14,.2f} truth {T0['adjustments'][k]:14,.2f} diff {v - T0['adjustments'][k]:10.2f}")
print("MQ", summ["mid_quarter"], "179", summ["s179_taken"], "limit", summ["s179_limit"], "| CF", cf, "NOL", nol_bal)

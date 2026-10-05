"""Reference detectors. Reads ONLY ../inputs."""
import os, re, json, datetime as dt
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); IN = os.path.join(HERE, "..", "inputs"); OUTD = os.path.join(HERE, "reference_outputs"); os.makedirs(OUTD, exist_ok=True)
P = lambda f: os.path.join(IN, f)
digits = lambda s: re.sub(r"\D", "", str(s))
def nodigits0(s): d = digits(s); return d.lstrip("0")
inv = pd.read_csv(P("ap_invoices.csv"), dtype={"invoice_no": str}); inv["invoice_date"] = pd.to_datetime(inv.invoice_date)
pay = pd.read_csv(P("payments.csv"), dtype={"invoice_ref": str}); pay["pay_date"] = pd.to_datetime(pay.pay_date, format="%m/%d/%Y")
po = pd.read_csv(P("purchase_orders.csv")); gr = pd.read_csv(P("goods_receipts.csv"))
hr = pd.read_csv(P("hr_employees.csv")); pay_acct = {r["emp_id"]: digits(r["bank_account"]) for r in json.load(open(P("hr_payroll_accounts.json")))["accounts"]}
x = pd.read_excel(P("vendor_master.xlsx"), sheet_name=None); vm = x["vendors"]; st = x["status_history"]; rp = x["related_party_register"]; ov = x["block_overrides"]
bc = pd.DataFrame(json.load(open(P("bank_change_requests.json")))["changes"])
cx = pd.read_excel(P("contracts_register.xlsx"), sheet_name=None); contracts = cx["contracts"]; amend = cx["amendments"]
# canonical vendor = legacy id
to_leg = {}
for r in vm.itertuples(): to_leg[r.vendor_id] = r.legacy_vendor_id; to_leg[r.legacy_vendor_id] = r.legacy_vendor_id
inv["v"] = inv.vendor_id.map(to_leg); pay["v"] = pay.vendor_id.map(to_leg); po["v"] = po.vendor_id.map(to_leg)
cases = []
def add(scheme, vendor, docs, exposure, key): cases.append(dict(scheme=scheme, vendor=vendor, docs=docs, exposure=round(float(exposure), 2), key=key))

# 1 duplicates
p1 = pay[(pay.payment_type == "PAYMENT") & (pay.status == "cleared")].copy(); p1["num"] = p1.invoice_ref.map(nodigits0)
refund = pay[pay.payment_type == "REFUND_IN"].copy(); refund["num"] = refund.invoice_ref.map(nodigits0); refset = set(zip(refund.v, refund.num))
for (v, num, amt), g in p1.groupby(["v", "num", "amount"]):
    if len(g) >= 2 and num != "":
        g = g.sort_values("pay_date")
        for r in g.iloc[1:].itertuples():
            if (v, num) in refset: continue
            add("S1", v, [r.payment_id], r.amount, r.payment_id)
# 2 employee-linked
rpset = set(rp.vendor_id)
hr["addr_n"] = hr.home_address.map(lambda s: re.sub(r"[^a-z0-9]", "", str(s).lower().replace("street", "st").replace("avenue", "ave").replace("road", "rd").replace("drive", "dr").replace("lane", "ln").replace("boulevard", "blvd").replace("court", "ct").replace("way", "wy").replace("apt", "").replace("unit", "").replace("suite", "").replace("#", "")))
hr["ph"] = hr.phone.map(lambda s: digits(s)[-10:])
vm["addr_n"] = vm.address.map(lambda s: re.sub(r"[^a-z0-9]", "", str(s).lower().replace("street", "st").replace("avenue", "ave").replace("road", "rd").replace("drive", "dr").replace("lane", "ln").replace("boulevard", "blvd").replace("court", "ct").replace("way", "wy").replace("apt", "").replace("unit", "").replace("suite", "").replace("#", "")))
vm["ph"] = vm.phone.map(lambda s: digits(s)[-10:]); vm["acct"] = vm.bank_account_on_file.map(digits)
acct_emp = {a: e for e, a in pay_acct.items()}
vacct = {}
for r in pay.itertuples(): vacct.setdefault(r.v, set()).add(digits(r.bank_acct_to))
for r in vm.itertuples():
    hit = [acct_emp[a] for a in (vacct.get(r.legacy_vendor_id, set()) | {r.acct}) if a in acct_emp]
    hit2 = hr[(hr.addr_n == r.addr_n) & (hr.ph == r.ph)].emp_id.tolist()
    if (hit or hit2) and r.legacy_vendor_id not in rpset:
        pp = pay[(pay.v == r.legacy_vendor_id) & (pay.status == "cleared") & (pay.payment_type == "PAYMENT")]
        add("S2", r.legacy_vendor_id, [r.legacy_vendor_id], pp.amount.sum(), r.legacy_vendor_id)
# 3 split approvals
role = dict(zip(hr.emp_id, hr.role)); LIM = {"Approver L1": 10000, "Approver L2": 50000, "Approver L3": 250000}
iv = inv[inv.doc_type == "INVOICE"].copy(); iv["lim"] = iv.approver_id.map(lambda e: LIM.get(role.get(e), np.nan)); iv = iv[(iv.amount >= 0.9 * iv.lim) & (iv.amount < iv.lim)]
for (ap, v), g in iv.groupby(["approver_id", "v"]):
    g = g.sort_values("invoice_date"); used = set(); rows = g.to_dict("records")
    for i, a in enumerate(rows):
        grp = [b for b in rows if 0 <= (b["invoice_date"] - a["invoice_date"]).days <= 5]
        if len(grp) >= 2 and a["invoice_id"] not in used:
            for b in grp: used.add(b["invoice_id"])
            add("S3", v, [b["invoice_id"] for b in grp], sum(b["amount"] for b in grp), "|".join(b["invoice_id"] for b in grp))
# 4 receipts shortfall
gsum = gr.groupby("po_number").received_value.sum(); cm = inv[inv.doc_type == "CREDIT_MEMO"].groupby("po_number").amount.sum()
poi = inv[(inv.doc_type == "INVOICE") & (inv.po_number.notna())].merge(po[["po_number", "po_type"]], on="po_number")
poi = poi[poi.po_type == "GOODS"].copy(); poi["gr"] = poi.po_number.map(gsum).fillna(0.0); poi["cm"] = -poi.po_number.map(cm).fillna(0.0)
poi["short"] = poi.amount - poi.gr - poi.cm
bad = poi[(poi.gr < 0.8 * poi.amount) & (poi.short > 1)]
for v, g in bad.groupby("v"): add("S4", v, g.invoice_id.tolist(), g.short.sum(), v)
# 5 bank change diversion
unv = bc[bc.callback_verified == "N"].copy(); unv["eff"] = pd.to_datetime(unv.effective_from); unv["leg"] = unv.legacy_vendor_id
for r in unv.itertuples():
    na = digits(r.new_account); nxt = bc[(bc.legacy_vendor_id == r.leg) & (pd.to_datetime(bc.effective_from) > r.eff)]
    end = pd.to_datetime(nxt.effective_from).min() if len(nxt) else r.eff + pd.Timedelta(days=14)
    pp = pay[(pay.v == r.leg) & (pay.status == "cleared") & (pay.pay_date >= r.eff) & (pay.pay_date <= min(r.eff + pd.Timedelta(days=14), end)) & (pay.bank_acct_to.map(digits) == na) & (pay.amount >= 25000)]
    if len(pp): add("S5", r.leg, pp.payment_id.tolist(), pp.amount.sum(), r.leg)
# 6 shell vendors
ent = inv[inv.doc_type == "INVOICE"].groupby(["v", "entered_by"]).size().reset_index(name="n"); tot = ent.groupby("v").n.sum()
cre = dict(zip(vm.legacy_vendor_id, vm.created_by)); tin_ok = dict(zip(vm.legacy_vendor_id, vm.tin_status))
for r in ent.itertuples():
    if cre.get(r.v) == r.entered_by and r.n >= 0.8 * tot[r.v] and tin_ok.get(r.v) != "matched":
        pp = pay[(pay.v == r.v) & (pay.status == "cleared") & (pay.payment_type == "PAYMENT")]; add("S6", r.v, [r.v], pp.amount.sum(), r.v)
# 7 contract overrun
paid_inv = inv[(inv.doc_type == "INVOICE") & inv.contract_ref.notna()].copy(); paid_inv["num"] = paid_inv.invoice_no.map(nodigits0)
pm = p1.merge(paid_inv[["v", "num", "amount", "contract_ref"]], on=["v", "num", "amount"], how="inner")
eff_cap = contracts.set_index("contract_id").cap_value.copy()
for r in amend.sort_values("effective_date").itertuples(): eff_cap[r.contract_id] = r.new_cap_value
for cid, g in pm.groupby("contract_ref"):
    tot_paid = g.amount.sum()
    if tot_paid > 1.10 * eff_cap[cid]:
        v = contracts.set_index("contract_id").loc[cid, "vendor_id"]; add("S7", v, [cid], tot_paid - eff_cap[cid], cid)
# 8 blocked vendors
ovset = set(ov.payment_id); sth = st.sort_values("effective_from"); sth["effective_from"] = pd.to_datetime(sth.effective_from)
for v, g in sth.groupby("vendor_id"):
    g = g.sort_values("effective_from"); periods = []; start = None
    for r in g.itertuples():
        if r.status != "active" and start is None: start = r.effective_from
        elif r.status == "active" and start is not None: periods.append((start, r.effective_from)); start = None
    if start is not None: periods.append((start, pd.Timestamp("2100-01-01")))
    for a, b in periods:
        pp = pay[(pay.v == v) & (pay.status == "cleared") & (pay.payment_type == "PAYMENT") & (pay.pay_date >= a) & (pay.pay_date < b) & (~pay.payment_id.isin(ovset))]
        if len(pp): add("S8", v, pp.payment_id.tolist(), pp.amount.sum(), v)
C = pd.DataFrame(cases); C.to_csv(os.path.join(OUTD, "reference_cases.csv"), index=False)
truth = pd.DataFrame(json.load(open(os.path.join(HERE, "world_truth.json")))["truth"])
print("found", len(C), "truth", len(truth)); print(C.groupby("scheme").agg(n=("exposure", "size"), exposure=("exposure", "sum")))
print(truth.groupby("scheme").agg(n=("exposure", "size"), exposure=("exposure", "sum")))
tk = set(zip(truth.scheme, truth.vendor)); fk = set(zip(C.scheme, C.vendor))
print("missing from detectors:", sorted(tk - fk)[:10], "| extra flagged:", sorted(fk - tk)[:15])
tc = set(zip(truth.scheme, truth.key)); fc = set(zip(C.scheme, C.key)); print("S1/S3 key mismatch: missing", len([k for k in tc - fc if k[0] in ('S1', 'S3')]), "extra", len([k for k in fc - tc if k[0] in ('S1', 'S3')]))

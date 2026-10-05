"""Synthetic AP forensic dataset for Calloway Industrial. All data is synthetic."""
import os, json, math, random, datetime as dt, string
import numpy as np, pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, "..", "inputs"); os.makedirs(OUT, exist_ok=True)
SEED = int(os.environ.get("TASK_SEED", 20251105)); rng = np.random.default_rng(SEED); rnd = random.Random(SEED)
START = dt.date(2024, 1, 1); END = dt.date(2025, 9, 30); MIG = dt.date(2025, 3, 1); INV_END = dt.date(2025, 8, 20)
def D(d): return d.isoformat()
def addd(d, n): return d + dt.timedelta(days=int(n))
def rdate(a, b): return addd(a, rnd.randint(0, (b - a).days))
def wk(d):
    while d.weekday() >= 5: d = addd(d, 1)
    return d

FIRST = "James Mary Robert Patricia John Jennifer Michael Linda David Elizabeth William Barbara Richard Susan Joseph Jessica Thomas Sarah Charles Karen Chris Nancy Daniel Lisa Matthew Betty Anthony Sandra Mark Ashley Donald Emily Steven Kimberly Paul Donna Andrew Michelle Joshua Carol Kenneth Amanda Kevin Melissa Brian Deborah George Stephanie Edward Rebecca Ronald Laura Timothy Sharon Jason Cynthia Jeffrey Kathleen Ryan Amy Gary Angela Nicholas Shirley Eric Anna Jonathan Brenda Stephen Pamela Larry Emma Justin Nicole Scott Helen Brandon Samantha Benjamin Katherine Samuel Christine Gregory Debra Frank Rachel Alexander Carolyn Raymond Janet Patrick Maria".split()
LAST = "Smith Johnson Williams Brown Jones Garcia Miller Davis Rodriguez Martinez Hernandez Lopez Gonzalez Wilson Anderson Thomas Taylor Moore Jackson Martin Lee Perez Thompson White Harris Sanchez Clark Ramirez Lewis Robinson Walker Young Allen King Wright Scott Torres Nguyen Hill Flores Green Adams Nelson Baker Hall Rivera Campbell Mitchell Carter Roberts Gomez Phillips Evans Turner Diaz Parker Cruz Edwards Collins Reyes Stewart Morris Morales Murphy Cook Rogers Gutierrez Ortiz Morgan Cooper Peterson Bailey Reed Kelly Howard Ramos Kim Cox Ward Richardson Watson Brooks Chavez Wood James Bennett Gray Mendoza Ruiz Hughes Price Alvarez Castillo Sanders Patel Myers Long Ross Foster Jimenez Kowalski Novak Petrov Schmidt Fischer".split()
STREETS = "Maple Oak Pine Cedar Elm Washington Lake Hill Park Sunset Highland Church Mill Spring River Forest Meadow Ridge Union Franklin Jefferson Lincoln Madison Jackson Adams Cherry Walnut Chestnut Dogwood Birch Willow".split()
SUFFIX = ["Street", "Avenue", "Road", "Drive", "Lane", "Boulevard", "Court", "Way"]
ABBR = {"Street": "St", "Avenue": "Ave", "Road": "Rd", "Drive": "Dr", "Lane": "Ln", "Boulevard": "Blvd", "Court": "Ct", "Way": "Wy"}
CITIES = [("Aurora", "IL", "60502"), ("Naperville", "IL", "60540"), ("Joliet", "IL", "60435"), ("Elgin", "IL", "60120"), ("Oak Brook", "IL", "60523"), ("Schaumburg", "IL", "60173"), ("Bolingbrook", "IL", "60440"), ("Wheaton", "IL", "60187")]
ADJ = "Apex Summit Pioneer Liberty Heritage Precision Reliable Superior Midwest Prairie Lakeshore Keystone Cornerstone Anchor Beacon Crescent Dynamic Evergreen Frontier Granite Horizon Ironwood Landmark Meridian Northstar Pinnacle Quality Redline Sterling Titan United Vanguard Westfield Allied Premier Standard Regal Atlas Delta Omega".split()
NOUN = "Industrial Supply;Fasteners;Packaging;Electric;Hydraulics;Logistics;Maintenance Services;Safety Equipment;Tooling;Metals;Plastics;Cleaning Services;Staffing;IT Services;Consulting;Chemicals;Pumps;Bearings;Controls;Calibration;Freight;Fabrication;Machining;Coatings;Lubricants;Filtration;Abrasives;Valves;Printing;Uniforms".split(";")
LEGAL = ["LLC", "Inc", "Co", "Corp", "LP", "Group"]

def mk_addr():
    c = rnd.choice(CITIES); sfx = rnd.choice(SUFFIX)
    return dict(num=rnd.randint(10, 9999), street=rnd.choice(STREETS), sfx=sfx, unit=(rnd.choice(["Apt ", "Unit ", "Suite "]) + str(rnd.randint(1, 40)) + rnd.choice(["", "A", "B"])) if rnd.random() < 0.35 else "", city=c[0], st=c[1], zip=c[2])
def fmt_addr(a, style):
    sfx = a["sfx"] if style == 0 else ABBR[a["sfx"]]
    unit = a["unit"] if style != 2 else a["unit"].replace("Apt ", "#").replace("Unit ", "#").replace("Suite ", "#")
    s = f"{a['num']} {a['street']} {sfx}"
    if unit: s += (", " if style == 0 else " ") + unit
    return f"{s}, {a['city']}, {a['st']} {a['zip']}" if style != 1 else f"{s} {a['city']} {a['st']} {a['zip']}".upper()
def phone(): return f"{rnd.choice([312,630,708,847,331,224])}{rnd.randint(200,999)}{rnd.randint(1000,9999)}"
def acct(): return f"{rnd.choice(['021000021','071000013','026009593','111000025','122000247'])}{rnd.randint(1000000000, 9999999999)}"
def fmt_phone(p, s): return [p, f"({p[:3]}) {p[3:6]}-{p[6:]}", f"{p[:3]}-{p[3:6]}-{p[6:]}", f"+1{p}"][s]
def fmt_acct(a, s): return [a, f"{a[:9]}-{a[9:]}", f"{a[:9]} {a[9:]}", f"{a[:9]}/{a[9:]}"][s]
def tin(): return f"{rnd.randint(10, 98)}-{rnd.randint(1000000, 9999999)}"

# ----------------------------------------------------------------------------- employees
ROLES = [("Buyer", 60), ("AP Clerk", 12), ("Approver L1", 45), ("Approver L2", 16), ("Approver L3", 6), ("Receiver", 24), ("Other", 640)]
emps = []; eid = 0
used_names = set()
for role, n in ROLES:
    for _ in range(n):
        eid += 1
        while True:
            nm = (rnd.choice(FIRST), rnd.choice(LAST))
            if nm not in used_names: used_names.add(nm); break
        emps.append(dict(emp_id=f"E{eid:04d}", first=nm[0], last=nm[1], role=role, addr=mk_addr(), phone=phone(), payroll_acct=acct(),
                         hire=rdate(dt.date(2008, 1, 1), dt.date(2023, 6, 1)), term=None, dept=rnd.choice(["Plant", "Procurement", "Finance", "Logistics", "Quality", "Maintenance", "IT", "HR"])))
for e in rnd.sample([e for e in emps if e["role"] == "Other"], 70): e["term"] = rdate(dt.date(2023, 3, 1), dt.date(2025, 6, 30))
by_role = lambda r: [e for e in emps if e["role"] == r]
BUY, CLERK, L1, L2, L3, RECV = by_role("Buyer"), by_role("AP Clerk"), by_role("Approver L1"), by_role("Approver L2"), by_role("Approver L3"), by_role("Receiver")
LIMIT = {"L1": 10000, "L2": 50000, "L3": 250000}
for e in emps: e["manager"] = rnd.choice(L2)["emp_id"] if e["role"] not in ("Approver L3",) else None
emp_by_id = {e["emp_id"]: e for e in emps}

# ----------------------------------------------------------------------------- vendors
vendors = []; NV = 740
used_vname = set()
def vname():
    while True:
        n = f"{rnd.choice(ADJ)} {rnd.choice(NOUN)} {rnd.choice(LEGAL)}"
        if n not in used_vname: used_vname.add(n); return n
for i in range(NV):
    cat = rnd.choices(["goods", "services", "recurring"], [0.55, 0.33, 0.12])[0]
    mig = rnd.random() < 0.38
    v = dict(idx=i, legacy=f"V{10000+i}", current=(f"VN-{500000+i}" if mig else f"V{10000+i}"), name=vname(), cat=cat, tin=tin(), tin_status=rnd.choices(["matched", "not_checked"], [0.97, 0.03])[0],
             addr=mk_addr(), phone=phone(), domain=f"{rnd.choice(ADJ).lower()}{rnd.choice(NOUN).split()[0].lower()}.com", created=rdate(dt.date(2016, 1, 1), dt.date(2023, 10, 1)),
             created_by=rnd.choice(BUY)["emp_id"], scale=float(rnd.lognormvariate(0, 0.6)), kind="legit")
    v["acct"] = acct(); v["bank_hist"] = [dict(acct=v["acct"], frm=v["created"], to=None, verified="Y", by=None, ticket=None, ts=None)]
    vendors.append(v)
v_by_leg = {v["legacy"]: v for v in vendors}
def vid_at(v, d): return v["current"] if d >= MIG else v["legacy"]
def acct_at(v, d):
    for h in v["bank_hist"]:
        if h["frm"] <= d and (h["to"] is None or d < h["to"]): return h["acct"]
    return v["bank_hist"][-1]["acct"]
goods_v = [v for v in vendors if v["cat"] == "goods"]; svc_v = [v for v in vendors if v["cat"] == "services"]; rec_v = [v for v in vendors if v["cat"] == "recurring"]

# legit bank changes (verified) and a few unverified small
def add_bank_change(v, d, verified, by, revert_to=None):
    new = acct(); last = v["bank_hist"][-1]; last["to"] = d
    v["bank_hist"].append(dict(acct=new, frm=d, to=None, verified=verified, by=by["emp_id"], ticket=(f"TKT-{rnd.randint(100000,999999)}" if verified == "Y" else ""), ts=None))
    return new
bank_legit = rnd.sample(vendors, 60)
for v in bank_legit: add_bank_change(v, rdate(dt.date(2024, 2, 1), dt.date(2025, 7, 15)), "Y", rnd.choice(CLERK))
bank_unv_small = rnd.sample([v for v in vendors if v not in bank_legit and v["cat"] != "recurring"], 12)
for v in bank_unv_small: add_bank_change(v, rdate(dt.date(2024, 2, 1), dt.date(2025, 7, 15)), "N", rnd.choice(CLERK))

# ----------------------------------------------------------------------------- core ledger
invoices = []; payments = []; pos = []; grs = []
inv_ctr = {}; po_ctr = [0]; inv_id = [0]; pay_id = [0]; gr_id = [0]
PREFIX = {v["legacy"]: rnd.choice(["INV-", "", "I", "BILL-", "#", "INV"]) for v in vendors}
VBASE = {v["legacy"]: rnd.randint(1000, 90000) for v in vendors}
def next_inv_no(v):
    inv_ctr[v["legacy"]] = inv_ctr.get(v["legacy"], 0) + rnd.randint(1, 4)
    n = VBASE[v["legacy"]] + inv_ctr[v["legacy"]]; return f"{PREFIX[v['legacy']]}{n}", n
def pick_approver(amount):
    if amount < 9000: return rnd.choices([rnd.choice(L1), rnd.choice(L2)], [0.8, 0.2])[0]
    if amount < 48000: return rnd.choice(L2) if rnd.random() < 0.8 else rnd.choice(L3)
    return rnd.choice(L3)
def new_invoice(v, d, amount, po=None, approver=None, entered_by=None, contract=None, desc="", doc="INVOICE", inv_no=None, entered_on=None, kind="bg"):
    inv_id[0] += 1
    no = inv_no or next_inv_no(v)[0]
    appr = approver or pick_approver(abs(amount))
    row = dict(invoice_id=f"AP{inv_id[0]:07d}", vendor_id=vid_at(v, d), invoice_no=no, invoice_date=d, entered_on=entered_on or addd(d, rnd.randint(0, 4)), amount=round(float(amount), 2),
               po_number=po or "", approver_id=appr["emp_id"], entered_by=(entered_by or rnd.choice(CLERK))["emp_id"], contract_ref=contract or "", doc_type=doc, description=desc, _v=v["legacy"], _kind=kind)
    invoices.append(row); return row
def new_payment(inv, pay_date, amount=None, acct_to=None, status="cleared", method=None, ptype="PAYMENT", ref=None, vendor=None):
    pay_id[0] += 1
    v = vendor or v_by_leg[inv["_v"]]
    row = dict(payment_id=f"PM{pay_id[0]:07d}", invoice_ref=ref if ref is not None else inv["invoice_no"], vendor_id=vid_at(v, pay_date), pay_date=pay_date, amount=round(float(inv["amount"] if amount is None else amount), 2),
               method=method or rnd.choices(["ACH", "CHECK", "WIRE"], [0.72, 0.25, 0.03])[0], bank_acct_to=acct_to if acct_to is not None else acct_at(v, pay_date), batch_id=f"B{pay_date.isocalendar()[0]}{pay_date.isocalendar()[1]:02d}",
               status=status, ptype=ptype, _inv=inv["invoice_id"], _v=v["legacy"])
    payments.append(row); return row
def new_po(v, d, amount, typ, requester=None):
    po_ctr[0] += 1; r = requester or rnd.choice(BUY); n = f"PO-{d.year}-{po_ctr[0]:06d}"
    row = dict(po_number=n, vendor_id=vid_at(v, d), po_date=d, amount=round(float(amount), 2), po_type=typ, requester=r["emp_id"], approver_id=pick_approver(amount)["emp_id"], _v=v["legacy"])
    pos.append(row); return row
def new_gr(po, d, value, receiver=None):
    gr_id[0] += 1
    grs.append(dict(gr_id=f"GR{gr_id[0]:07d}", po_number=po["po_number"], received_date=d, value=round(float(value), 2), receiver_id=(receiver or rnd.choice(RECV))["emp_id"], _v=po["_v"]))
def pay_after(inv, term=None):
    d = wk(addd(inv["invoice_date"], term or rnd.choice([30, 30, 45, 45, 60, 15])))
    return d
def bg_amount(v): return float(np.clip(rnd.lognormvariate(math.log(2600), 1.05) * v["scale"], 120, 238000))

# contracts: services vendors with a contract and a monthly stream
contract_vendors = rnd.sample(svc_v, 70); contracts = []
for k, v in enumerate(contract_vendors):
    start = rdate(dt.date(2023, 10, 1), dt.date(2024, 3, 1)); months = rnd.choice([24, 30, 36]); end = addd(start, months * 30)
    cap = float(rnd.choice([180000, 250000, 320000, 400000, 520000, 650000, 800000]))
    contracts.append(dict(contract_id=f"C-{1000+k}", _v=v["legacy"], start=start, end=end, cap=cap, kind="legit"))
c_by_v = {c["_v"]: c for c in contracts}

# background POs / invoices
for v in vendors:
    if v["cat"] == "recurring":
        amt0 = float(round(rnd.choice([1800, 4200, 6500, 12500, 24000]) * rnd.uniform(0.9, 1.4), 2)); varying = rnd.random() < 0.5
        d = dt.date(2024, rnd.randint(1, 3), rnd.randint(1, 25)); m = 0
        while d <= INV_END:
            a = amt0 * (rnd.uniform(0.85, 1.2) if varying else 1.0)
            inv = new_invoice(v, d, a, desc="monthly service/utility", entered_by=rnd.choice(CLERK), approver=pick_approver(a))
            new_payment(inv, pay_after(inv, 30))
            m += 1; d = addd(dt.date(2024, 1, 1), 31 * m + rnd.randint(-2, 2)); d = d.replace(day=min(d.day, 28)) if d else d
        continue
    npo = int(np.clip(rnd.lognormvariate(math.log(32), 0.85), 3, 380)) if v["legacy"] not in c_by_v else 0
    for _ in range(npo):
        d = rdate(START, addd(INV_END, -45)); amt = bg_amount(v)
        typ = "GOODS" if v["cat"] == "goods" else "SVC"
        po = new_po(v, d, amt, typ)
        inv_d = addd(d, rnd.randint(4, 28))
        # partial deliveries
        if typ == "GOODS":
            if rnd.random() < 0.10:      # two shipments
                f = rnd.uniform(0.4, 0.7); new_gr(po, addd(d, rnd.randint(3, 10)), amt * f); new_gr(po, addd(d, rnd.randint(12, 24)), amt * (1 - f) * rnd.uniform(0.97, 1.0))
            elif rnd.random() < 0.04:    # genuine short ship, between 80% and 95%
                new_gr(po, addd(d, rnd.randint(3, 15)), amt * rnd.uniform(0.82, 0.93))
            else: new_gr(po, addd(d, rnd.randint(3, 15)), amt * rnd.uniform(0.97, 1.0))
        a = amt
        inv = new_invoice(v, inv_d, a, po=po["po_number"], desc=f"{typ.lower()} invoice")
        po["approver_id"] = inv["approver_id"]
        new_payment(inv, pay_after(inv))
# contract streams (legit): cumulative stays under cap, some with amendments
for c in contracts:
    v = v_by_leg[c["_v"]]; n_m = max(6, int((min(c["end"], INV_END) - c["start"]).days / 30))
    target = c["cap"] * rnd.uniform(0.62, 0.92); per = target / n_m; d = c["start"]
    for m in range(n_m):
        dd = addd(c["start"], 30 * m + rnd.randint(0, 6))
        if dd > INV_END: break
        a = per * rnd.uniform(0.8, 1.2); po = new_po(v, dd, a, "SVC")
        inv = new_invoice(v, addd(dd, rnd.randint(10, 25)), a, po=po["po_number"], contract=c["contract_id"], desc="contract services", approver=rnd.choice(L3))
        po["approver_id"] = inv["approver_id"]; new_payment(inv, pay_after(inv))

def drop_bg_invoices(pred):
    """Remove background invoices (and their payments, POs, GRs) matching pred, to avoid accidental rule hits."""
    global invoices, payments, pos, grs
    kill = {i["invoice_id"] for i in invoices if i["_kind"] in ("bg", "lookalike") and pred(i)}
    kpo = {i["po_number"] for i in invoices if i["invoice_id"] in kill and i["po_number"]}
    invoices = [i for i in invoices if i["invoice_id"] not in kill]; payments = [p for p in payments if p["_inv"] not in kill]
    pos = [p for p in pos if p["po_number"] not in kpo]; grs = [g for g in grs if g["po_number"] not in kpo]
TRUTH = []     # truth cases
DECOYS = []    # documented lookalikes (for the author)
used = set(c["_v"] for c in contracts)
def free_vendor(pool, k=1):
    c = [v for v in pool if v["legacy"] not in used and v["kind"] == "legit"]; ch = rnd.sample(c, k)
    for v in ch: used.add(v["legacy"])
    return ch
def dig(s): return "".join(ch for ch in str(s) if ch.isdigit())
def variant_no(no):
    n = dig(no); return rnd.choice([n, f"INV-{n}", f"0{n}", f"INV {n}", f"{n}-A", f"I{n}"])
def make_vendor(kind, cat="services", created=None, created_by=None, tin_status="matched", addr_fn=None):
    i = len(vendors); mig = rnd.random() < 0.3
    v = dict(idx=i, legacy=f"V{10000+i}", current=(f"VN-{500000+i}" if mig else f"V{10000+i}"), name=vname(), cat=cat, tin=tin(), tin_status=tin_status, addr=mk_addr(), phone=phone(),
             domain=f"{rnd.choice(ADJ).lower()}{rnd.choice(NOUN).split()[0].lower()}.com", created=created or rdate(dt.date(2016, 1, 1), dt.date(2023, 10, 1)), created_by=created_by or rnd.choice(BUY)["emp_id"],
             scale=1.0, kind=kind, po_box=False)
    v["acct"] = acct(); v["bank_hist"] = [dict(acct=v["acct"], frm=v["created"], to=None, verified="Y", by=None, ticket=None, ts=None)]
    vendors.append(v); v_by_leg[v["legacy"]] = v; used.add(v["legacy"]); PREFIX[v["legacy"]] = rnd.choice(["INV-", "", "I"]); VBASE[v["legacy"]] = rnd.randint(1000, 9000); return v
def stream(v, n, d0, d1, lo, hi, po_type="SVC", approver=None, entered_by=None, no_po=False, seq=False, ratio=None, receiver=None, desc=""):
    out = []
    for k in range(n):
        d = rdate(d0, d1); a = round(rnd.uniform(lo, hi), 2)
        po = None
        if not no_po:
            po = new_po(v, addd(d, -rnd.randint(5, 20)), a, po_type)
            if po_type == "GOODS":
                new_gr(po, addd(d, -rnd.randint(1, 4)), a * (ratio() if ratio else rnd.uniform(0.97, 1.0)), receiver)
        inv = new_invoice(v, d, a, po=(po["po_number"] if po else None), approver=approver, entered_by=entered_by, desc=desc or "invoice", kind="planted")
        if po: po["approver_id"] = inv["approver_id"]
        out.append(inv)
    return out

# ---------- S1 duplicate payments across the re-key
pay_by_inv = {}
for p in payments: pay_by_inv.setdefault(p["_inv"], []).append(p)
cand = [i for i in invoices if i["_kind"] == "bg" and i["doc_type"] == "INVOICE" and v_by_leg[i["_v"]]["current"] != i["_v"] and dt.date(2024, 9, 1) <= i["invoice_date"] <= dt.date(2025, 1, 31)
        and 1500 <= i["amount"] <= 45000 and i["_v"] not in used and pay_by_inv.get(i["invoice_id"]) and pay_by_inv[i["invoice_id"]][0]["pay_date"] < MIG]
sel = rnd.sample(cand, 52); modes = ["true"] * 28 + ["voided"] * 12 + ["recovered"] * 12
rnd.shuffle(modes)
for orig, mode in zip(sel, modes):
    used.add(orig["_v"]); v = v_by_leg[orig["_v"]]; eo = rdate(dt.date(2025, 3, 5), dt.date(2025, 5, 20))
    dup = new_invoice(v, orig["invoice_date"], orig["amount"], po=(orig["po_number"] if rnd.random() < 0.6 else None), inv_no=variant_no(orig["invoice_no"]), entered_on=eo, kind="dup")
    dup["vendor_id"] = v["current"]
    pd_ = wk(addd(eo, rnd.randint(28, 45)))
    pm = new_payment(dup, pd_, status=("voided" if mode == "voided" else "cleared"))
    if mode == "recovered": new_payment(dup, wk(addd(pd_, rnd.randint(18, 55))), amount=-dup["amount"], ptype="REFUND_IN", method="ACH")
    DECOYS.append(dict(scheme="S1", mode=mode, invoice=dup["invoice_id"]))
    if mode == "true": TRUTH.append(dict(scheme="S1", vendor=v["legacy"], docs=[dup["invoice_id"], pm["payment_id"]], exposure=dup["amount"], key=pm["payment_id"]))
# legit lookalikes: same vendor, same amount, different invoice number, close in time
for v in rnd.sample([v for v in goods_v + svc_v if v["legacy"] not in used], 60):
    used.add(v["legacy"]); d = rdate(dt.date(2024, 3, 1), dt.date(2025, 6, 1)); a = round(rnd.uniform(1800, 9000), 2)
    for k in range(2):
        po = new_po(v, addd(d, 30 * k - 5), a, "SVC"); inv = new_invoice(v, addd(d, 30 * k + rnd.randint(0, 3)), a, po=po["po_number"], kind="lookalike"); po["approver_id"] = inv["approver_id"]; new_payment(inv, pay_after(inv))
# ---------- S2 ghost / related-party vendors
ghosts = []
e_a = rnd.choice(BUY); e_b = rnd.choice([e for e in emps if e["role"] == "Other" and e["term"] is None]); e_c = rnd.choice([e for e in emps if e["role"] == "Other" and e["term"] is None and e is not e_b])
for tag, e, how, tinst in (("g1", e_a, "acct", "not_checked"), ("g2", e_b, "addr", "matched"), ("g3", e_c, "acct", "not_checked")):
    v = make_vendor("ghost", created=rdate(dt.date(2023, 11, 1), dt.date(2024, 3, 1)), created_by=rnd.choice(BUY)["emp_id"], tin_status=tinst)
    if how == "acct":
        v["acct"] = e["payroll_acct"]; v["bank_hist"] = [dict(acct=e["payroll_acct"], frm=v["created"], to=None, verified="Y", by=None, ticket=None, ts=None)]
    else:
        v["addr"] = dict(e["addr"]); v["phone"] = e["phone"]
    mgr = emp_by_id[e["manager"]]
    inv_list = stream(v, rnd.randint(32, 44), dt.date(2024, 3, 1), dt.date(2025, 7, 20), 3500, 9400, approver=mgr, desc="professional services")
    pays = [new_payment(i, pay_after(i)) for i in inv_list]
    ghosts.append(v); TRUTH.append(dict(scheme="S2", vendor=v["legacy"], docs=[i["invoice_id"] for i in inv_list], exposure=round(sum(p["amount"] for p in pays), 2), key=v["legacy"]))
related = []
for k, how in enumerate(("addr", "acct")):
    e = rnd.choice([e for e in emps if e["role"] == "Other" and e["term"] is None and e not in (e_b, e_c)])
    v = make_vendor("related_disclosed", created=rdate(dt.date(2018, 1, 1), dt.date(2022, 1, 1)))
    if how == "acct": v["acct"] = e["payroll_acct"]; v["bank_hist"] = [dict(acct=e["payroll_acct"], frm=v["created"], to=None, verified="Y", by=None, ticket=None, ts=None)]
    else: v["addr"] = dict(e["addr"]); v["phone"] = e["phone"]
    stream(v, rnd.randint(20, 30), dt.date(2024, 1, 5), dt.date(2025, 7, 20), 2500, 8000, desc="services")
    related.append(dict(v=v, emp=e))
for r in related:
    for i in [i for i in invoices if i["_v"] == r["v"]["legacy"] and i["_kind"] == "planted" and "paid" not in i]:
        new_payment(i, pay_after(i)); i["paid"] = 1
for tag in range(3):   # name-only coincidences
    e = rnd.choice(emps); v = make_vendor("name_coincidence"); v["name"] = f"{e['last']} {rnd.choice(NOUN)} {rnd.choice(LEGAL)}"
    for i in stream(v, rnd.randint(15, 25), dt.date(2024, 1, 5), dt.date(2025, 7, 20), 1500, 7000, desc="services"): new_payment(i, pay_after(i))
# ---------- S3 split approvals
splitters = rnd.sample(L1, 3)
def sp_vendor(): return rnd.choice([v for v in goods_v if v["legacy"] not in used and v["cat"] == "goods"])
for k in range(9):
    appr = splitters[k % 3]; v = sp_vendor(); used.add(v["legacy"]); d0 = wk(rdate(dt.date(2024, 3, 1), dt.date(2025, 6, 20))); n = rnd.choice([2, 3, 3, 4]); items = []
    for j in range(n):
        a = round(rnd.uniform(9050, 9985), 2); dd = addd(d0, j + rnd.randint(0, 1))
        po = new_po(v, addd(dd, -8), a, "GOODS"); new_gr(po, addd(dd, -3), a * rnd.uniform(0.98, 1.0))
        inv = new_invoice(v, dd, a, po=po["po_number"], approver=appr, kind="planted"); po["approver_id"] = appr["emp_id"]; items.append(inv)
    pays = [new_payment(i, pay_after(i)) for i in items]
    TRUTH.append(dict(scheme="S3", vendor=v["legacy"], docs=[i["invoice_id"] for i in items], exposure=round(sum(i["amount"] for i in items), 2), key="|".join(i["invoice_id"] for i in items)))
for k in range(12):   # near-limit pairs far apart in time (decoy)
    appr = rnd.choice(L1); v = sp_vendor(); used.add(v["legacy"]); d0 = rdate(dt.date(2024, 2, 1), dt.date(2025, 5, 1))
    for j in range(2):
        a = round(rnd.uniform(9050, 9985), 2); dd = addd(d0, j * rnd.randint(9, 25)); po = new_po(v, addd(dd, -8), a, "GOODS"); new_gr(po, addd(dd, -3), a * 0.99)
        inv = new_invoice(v, dd, a, po=po["po_number"], approver=appr, kind="decoy_s3"); po["approver_id"] = appr["emp_id"]; new_payment(inv, pay_after(inv))
for k in range(10):   # near-limit, same approver, same week, DIFFERENT vendors (decoy)
    appr = rnd.choice(L1); d0 = rdate(dt.date(2024, 2, 1), dt.date(2025, 5, 1))
    for j in range(2):
        v = sp_vendor(); used.add(v["legacy"]); a = round(rnd.uniform(9050, 9985), 2); dd = addd(d0, j); po = new_po(v, addd(dd, -8), a, "GOODS"); new_gr(po, addd(dd, -3), a * 0.99)
        inv = new_invoice(v, dd, a, po=po["po_number"], approver=appr, kind="decoy_s3"); po["approver_id"] = appr["emp_id"]; new_payment(inv, pay_after(inv))
for k in range(10):   # just-under-10k invoices clustered, but approved by an L2 (limit 50k) -> not near THEIR limit
    appr = rnd.choice(L2); v = sp_vendor(); used.add(v["legacy"]); d0 = wk(rdate(dt.date(2024, 3, 1), dt.date(2025, 6, 20)))
    for j in range(rnd.choice([2, 3])):
        a = round(rnd.uniform(9050, 9985), 2); dd = addd(d0, j); po = new_po(v, addd(dd, -8), a, "GOODS"); new_gr(po, addd(dd, -3), a * 0.99)
        inv = new_invoice(v, dd, a, po=po["po_number"], approver=appr, kind="decoy_s3"); po["approver_id"] = appr["emp_id"]; new_payment(inv, pay_after(inv))
# ---------- S4 fictitious receipts
recv_bad = rnd.sample(RECV, 2)
for k in range(2):
    v = make_vendor("fict_receipt", cat="goods", created=rdate(dt.date(2019, 1, 1), dt.date(2023, 6, 1)))
    invs = stream(v, 28, dt.date(2024, 2, 1), dt.date(2025, 7, 15), 6000, 38000, po_type="GOODS", ratio=lambda: rnd.uniform(0.06, 0.14), receiver=recv_bad[k], desc="goods invoice")
    pays = [new_payment(i, pay_after(i)) for i in invs]
    po_gr = {}
    for g in grs:
        if g["_v"] == v["legacy"]: po_gr[g["po_number"]] = po_gr.get(g["po_number"], 0) + g["value"]
    ex = sum(i["amount"] - po_gr.get(i["po_number"], 0) for i in invs)
    TRUTH.append(dict(scheme="S4", vendor=v["legacy"], docs=[i["invoice_id"] for i in invs], exposure=round(ex, 2), key=v["legacy"]))
for k in range(3):   # short receipts fully credited (decoy): credit memo removes the exposure
    v = make_vendor("short_credited", cat="goods", created=rdate(dt.date(2019, 1, 1), dt.date(2023, 6, 1)))
    invs = stream(v, 8, dt.date(2024, 2, 1), dt.date(2025, 7, 15), 6000, 30000, po_type="GOODS", ratio=lambda: rnd.uniform(0.45, 0.65), desc="goods invoice")
    for i in invs:
        gv = sum(g["value"] for g in grs if g["po_number"] == i["po_number"]); cr = round(i["amount"] - gv, 2)
        cm = new_invoice(v, addd(i["invoice_date"], rnd.randint(3, 12)), -cr, po=i["po_number"], desc=f"credit for short shipment on {i['invoice_no']}", doc="CREDIT_MEMO", kind="credit_decoy")
        new_payment(i, pay_after(i), amount=round(i["amount"] - cr, 2))
        cm["_paid"] = 1
# ---------- S5 bank-account diversion
for v in bank_unv_small:
    chg = v["bank_hist"][-1]["frm"]
    drop_bg_invoices(lambda i, v=v, chg=chg: i["_v"] == v["legacy"] and i["amount"] >= 20000 and chg - dt.timedelta(days=60) <= i["invoice_date"] <= chg + dt.timedelta(days=30))
bec_pool = [v for v in goods_v if v["legacy"] not in used and len(v["bank_hist"]) == 1]
bec = rnd.sample(bec_pool, 5); clerk_y = rnd.choice(CLERK)
BANKREQ = []
for v in bec:
    used.add(v["legacy"]); d0 = wk(rdate(dt.date(2024, 6, 1), dt.date(2025, 6, 1))); a = round(rnd.uniform(62000, 138000), 2)
    po = new_po(v, addd(d0, -12), a, "GOODS"); new_gr(po, addd(d0, -5), a * 0.99)
    inv = new_invoice(v, d0, a, po=po["po_number"], approver=rnd.choice(L3), desc="goods invoice", kind="planted"); po["approver_id"] = inv["approver_id"]
    chg = addd(d0, 2); mule = acct(); old = v["bank_hist"][-1]["acct"]; v["bank_hist"][-1]["to"] = chg
    v["bank_hist"].append(dict(acct=mule, frm=chg, to=addd(d0, 12), verified="N", by=clerk_y["emp_id"], ticket="", ts=f"{D(chg)}T23:{rnd.randint(10,50)}:00"))
    v["bank_hist"].append(dict(acct=old, frm=addd(d0, 12), to=None, verified="Y", by=rnd.choice(CLERK[1:])["emp_id"], ticket=f"TKT-{rnd.randint(100000,999999)}", ts=f"{D(addd(d0,12))}T10:{rnd.randint(10,50)}:00"))
    pm = new_payment(inv, wk(addd(d0, rnd.randint(4, 8))))
    assert pm["bank_acct_to"] == mule
    TRUTH.append(dict(scheme="S5", vendor=v["legacy"], docs=[inv["invoice_id"], pm["payment_id"]], exposure=pm["amount"], key=v["legacy"]))
# legit verified changes followed by large payments (decoy)
for v in rnd.sample([v for v in bank_legit if v["legacy"] not in used and v["cat"] == "goods"], 10):
    used.add(v["legacy"]); chg = v["bank_hist"][-1]["frm"]; d0 = addd(chg, rnd.randint(-2, 3)); a = round(rnd.uniform(30000, 95000), 2)
    po = new_po(v, addd(d0, -12), a, "GOODS"); new_gr(po, addd(d0, -5), a * 0.99); inv = new_invoice(v, d0, a, po=po["po_number"], approver=rnd.choice(L3), kind="decoy_s5"); po["approver_id"] = inv["approver_id"]
    new_payment(inv, wk(addd(chg, rnd.randint(2, 6))))
# ---------- S6 shell vendors with SoD
clerk_z = CLERK[0]; friend = rnd.choice(L1)
for k in range(2):
    v = make_vendor("shell", created=rdate(dt.date(2023, 12, 1), dt.date(2024, 6, 1)), created_by=clerk_z["emp_id"], tin_status=rnd.choice(["not_checked", "unmatched"])); v["po_box"] = True
    n = rnd.randint(48, 60); d = v["created"] + dt.timedelta(days=20); items = []; ctr = rnd.randint(1000, 1100)
    for j in range(n):
        d = wk(addd(d, rnd.randint(5, 12)))
        if d > INV_END: break
        ctr += 1; items.append(new_invoice(v, d, round(rnd.uniform(4600, 4990), 2), inv_no=f"{ctr}", approver=friend, entered_by=clerk_z, desc="consulting services", kind="planted"))
    pays = [new_payment(i, pay_after(i)) for i in items]
    TRUTH.append(dict(scheme="S6", vendor=v["legacy"], docs=[i["invoice_id"] for i in items], exposure=round(sum(p["amount"] for p in pays), 2), key=v["legacy"]))
for k in range(4):   # sequential small legit vendors (decoy)
    v = make_vendor("seq_legit", created=rdate(dt.date(2020, 1, 1), dt.date(2023, 6, 1)), tin_status="matched"); ctr = rnd.randint(100, 900); d = dt.date(2024, 1, 10)
    while d < INV_END:
        d = addd(d, rnd.randint(14, 35)); ctr += 1; i = new_invoice(v, d, round(rnd.uniform(1200, 4800), 2), inv_no=f"{ctr}", desc="supplies", kind="decoy_s6"); new_payment(i, pay_after(i))
for k in range(3):   # created by clerk Z but invoices entered by others, TIN matched, with POs (decoy)
    v = make_vendor("created_by_z", created=rdate(dt.date(2021, 1, 1), dt.date(2023, 6, 1)), created_by=clerk_z["emp_id"], tin_status="matched")
    for i in stream(v, 14, dt.date(2024, 2, 1), dt.date(2025, 7, 15), 2000, 9000, entered_by=rnd.choice(CLERK[1:]), desc="services"): new_payment(i, pay_after(i))
# ---------- S7 contract cap overruns
AMEND = []
free_c = [c for c in contracts if c["kind"] == "legit"]
def cum(c): return sum(i["amount"] for i in invoices if i["contract_ref"] == c["contract_id"] and i["doc_type"] == "INVOICE")
def push_to(c, target):
    v = v_by_leg[c["_v"]]; need = target - cum(c); k = 0; appr = rnd.choice(L3)
    while need > 500:
        a = round(min(need, rnd.uniform(20000, 45000)), 2); d = rdate(addd(INV_END, -240), INV_END); po = new_po(v, addd(d, -10), a, "SVC")
        inv = new_invoice(v, d, a, po=po["po_number"], contract=c["contract_id"], approver=appr, desc="contract services", kind="planted"); po["approver_id"] = appr["emp_id"]; new_payment(inv, pay_after(inv)); need -= a
for c in rnd.sample(free_c, 4):
    c["kind"] = "overrun"; push_to(c, c["cap"] * rnd.uniform(1.18, 1.45))
    paid = sum(i["amount"] for i in invoices if i["contract_ref"] == c["contract_id"] and i["doc_type"] == "INVOICE")
    TRUTH.append(dict(scheme="S7", vendor=c["_v"], docs=[c["contract_id"]], exposure=round(paid - c["cap"], 2), key=c["contract_id"]))
free_c = [c for c in contracts if c["kind"] == "legit"]
for c in rnd.sample(free_c, 4):   # amended (decoy)
    c["kind"] = "amended"; push_to(c, c["cap"] * rnd.uniform(1.15, 1.4)); paid = cum(c)
    AMEND.append(dict(contract_id=c["contract_id"], effective=rdate(addd(c["start"], 200), addd(INV_END, -300)) if False else addd(c["start"], 300), new_cap=round(math.ceil(paid * 1.06 / 10000) * 10000, 0), reason="scope extension"))
free_c = [c for c in contracts if c["kind"] == "legit"]
for c in rnd.sample(free_c, 3):   # within 10% tolerance (decoy)
    c["kind"] = "tolerance"; push_to(c, c["cap"] * rnd.uniform(1.02, 1.085))
# ---------- S8 payments to blocked vendors
STATUS = []; OVERRIDE = []
blk_pool = [v for v in goods_v + svc_v if v["legacy"] not in used and v["kind"] == "legit"]
bl = rnd.sample(blk_pool, 14)
for v in bl: used.add(v["legacy"])
for v in bl[:6]:   # blocked, then paid without override
    b = rdate(dt.date(2024, 6, 1), dt.date(2025, 4, 1)); STATUS.append(dict(v=v, status="blocked", eff=b, reason="compliance hold", by="E0007")); n = rnd.randint(2, 3); ex = 0; items = []
    drop_bg_invoices(lambda i, v=v, b=b: i["_v"] == v["legacy"] and i["invoice_date"] >= addd(b, -70))
    for j in range(n):
        d = addd(b, rnd.randint(10, 120)); d = min(d, INV_END); a = round(rnd.uniform(3000, 22000), 2); po = new_po(v, addd(d, -8), a, "SVC")
        inv = new_invoice(v, d, a, po=po["po_number"], desc="services", kind="planted"); po["approver_id"] = inv["approver_id"]; pm = new_payment(inv, pay_after(inv)); items.append((inv, pm))
    ex = round(sum(pm["amount"] for inv, pm in items if pm["pay_date"] >= b), 2)
    TRUTH.append(dict(scheme="S8", vendor=v["legacy"], docs=[pm["payment_id"] for inv, pm in items if pm["pay_date"] >= b], exposure=ex, key=v["legacy"]))
for v in bl[6:10]:   # blocked, paid WITH override (decoy)
    b = rdate(dt.date(2024, 6, 1), dt.date(2025, 4, 1)); STATUS.append(dict(v=v, status="blocked", eff=b, reason="insurance certificate expired", by="E0007"))
    drop_bg_invoices(lambda i, v=v, b=b: i["_v"] == v["legacy"] and i["invoice_date"] >= addd(b, -70))
    for j in range(rnd.randint(2, 3)):
        d = min(addd(b, rnd.randint(10, 120)), INV_END); a = round(rnd.uniform(3000, 22000), 2); po = new_po(v, addd(d, -8), a, "SVC"); inv = new_invoice(v, d, a, po=po["po_number"], kind="decoy_s8"); po["approver_id"] = inv["approver_id"]
        pm = new_payment(inv, pay_after(inv)); OVERRIDE.append(dict(v=v, payment=pm["payment_id"], approved_by="E0003", ticket=f"OVR-{rnd.randint(1000,9999)}", approved_on=addd(pm["pay_date"], -rnd.randint(1, 4))))
for v in bl[10:]:    # blocked then reactivated before payments (decoy)
    b = rdate(dt.date(2024, 5, 1), dt.date(2024, 10, 1)); STATUS.append(dict(v=v, status="blocked", eff=b, reason="tax form missing", by="E0007")); r = addd(b, rnd.randint(20, 60)); STATUS.append(dict(v=v, status="active", eff=r, reason="cleared", by="E0007"))
    drop_bg_invoices(lambda i, v=v, b=b, r=r: i["_v"] == v["legacy"] and addd(b, -70) <= i["invoice_date"] < r)
    for j in range(2):
        d = min(addd(r, rnd.randint(10, 150)), INV_END); a = round(rnd.uniform(3000, 22000), 2); po = new_po(v, addd(d, -8), a, "SVC"); inv = new_invoice(v, d, a, po=po["po_number"], kind="decoy_s8"); po["approver_id"] = inv["approver_id"]; new_payment(inv, pay_after(inv))
print("after injection:", len(invoices), "invoices", len(payments), "payments", len(pos), "POs", len(grs), "GRs", "| truth cases", len(TRUTH))
print(pd.DataFrame(TRUTH).groupby("scheme").agg(n=("exposure", "size"), exposure=("exposure", "sum")))

# ============================================================================ export
def asd(d): return D(d) if d else ""
# invoices
inv_rows = []
for i in sorted(invoices, key=lambda r: (r["invoice_date"], r["invoice_id"])):
    inv_rows.append(dict(invoice_id=i["invoice_id"], vendor_id=i["vendor_id"], invoice_no=i["invoice_no"], invoice_date=D(i["invoice_date"]), entered_on=D(i["entered_on"]), amount=i["amount"],
                         po_number=i["po_number"], approver_id=i["approver_id"], entered_by=i["entered_by"], contract_ref=i["contract_ref"], doc_type=i["doc_type"], description=i["description"],
                         cost_center=f"CC{rnd.randint(100, 480)}"))
pd.DataFrame(inv_rows).to_csv(os.path.join(OUT, "ap_invoices.csv"), index=False)
pay_rows = []
for p in sorted(payments, key=lambda r: (r["pay_date"], r["payment_id"])):
    pay_rows.append(dict(payment_id=p["payment_id"], invoice_ref=p["invoice_ref"], vendor_id=p["vendor_id"], pay_date=p["pay_date"].strftime("%m/%d/%Y"), amount=p["amount"], method=p["method"],
                         bank_acct_to=fmt_acct(p["bank_acct_to"], rnd.choice([0, 1, 2, 3])), batch_id=p["batch_id"], status=p["status"], payment_type=p["ptype"]))
pd.DataFrame(pay_rows).to_csv(os.path.join(OUT, "payments.csv"), index=False)
pd.DataFrame([dict(po_number=p["po_number"], vendor_id=p["vendor_id"], po_date=D(p["po_date"]), amount=p["amount"], po_type=p["po_type"], requester_id=p["requester"], approver_id=p["approver_id"]) for p in pos]).to_csv(os.path.join(OUT, "purchase_orders.csv"), index=False)
pd.DataFrame([dict(gr_id=g["gr_id"], po_number=g["po_number"], received_date=D(g["received_date"]), received_value=g["value"], receiver_id=g["receiver_id"]) for g in grs]).to_csv(os.path.join(OUT, "goods_receipts.csv"), index=False)
# employees / HR
pd.DataFrame([dict(emp_id=e["emp_id"], first_name=e["first"], last_name=e["last"], role=e["role"], department=e["dept"], home_address=fmt_addr(e["addr"], rnd.choice([0, 1, 2])),
                   phone=fmt_phone(e["phone"], rnd.choice([0, 1, 2, 3])), hire_date=D(e["hire"]), termination_date=asd(e["term"]), manager_id=e["manager"] or "") for e in emps]).to_csv(os.path.join(OUT, "hr_employees.csv"), index=False)
json.dump({"as_of": "2025-09-30", "accounts": [dict(emp_id=e["emp_id"], bank_account=f"ACH {fmt_acct(e['payroll_acct'], rnd.choice([1, 2, 3]))}") for e in emps]}, open(os.path.join(OUT, "hr_payroll_accounts.json"), "w"), indent=0)
# vendor master
blocked_now = {}
for s in sorted(STATUS, key=lambda s: s["eff"]): blocked_now[s["v"]["legacy"]] = s["status"]
vm = []
for v in vendors:
    a = v["addr"]; addr = f"PO Box {rnd.randint(1000, 9999)}, {a['city']}, {a['st']} {a['zip']}" if v.get("po_box") else fmt_addr(a, rnd.choice([0, 1, 2]))
    t = v["tin"]; t = t if rnd.random() < 0.7 else t.replace("-", "")
    vm.append(dict(vendor_id=v["current"], legacy_vendor_id=v["legacy"], vendor_name=v["name"], tax_id=t, tin_status=v["tin_status"], address=addr, phone=fmt_phone(v["phone"], rnd.choice([0, 1, 2, 3])),
                   email_domain=v["domain"], created_date=D(v["created"]), created_by=v["created_by"], category=v["cat"], status=blocked_now.get(v["legacy"], "active"),
                   bank_account_on_file=fmt_acct(v["bank_hist"][-1]["acct"], rnd.choice([1, 2, 3]))))
status_rows = []
for v in vendors: status_rows.append(dict(vendor_id=v["legacy"], status="active", effective_from=D(v["created"]), reason="onboarded", set_by=v["created_by"]))
for s in STATUS: status_rows.append(dict(vendor_id=s["v"]["legacy"], status=s["status"], effective_from=D(s["eff"]), reason=s["reason"], set_by=s["by"]))
rel_rows = [dict(vendor_id=r["v"]["legacy"], employee_id=r["emp"]["emp_id"], relationship=rnd.choice(["spouse-owned", "family-owned"]), disclosed_on=D(rdate(dt.date(2018, 1, 1), dt.date(2023, 6, 1))), approved_by="E0003", board_minute_ref=f"BM-{rnd.randint(10,99)}-{rnd.randint(1,12)}") for r in related]
ov_rows = [dict(payment_id=o["payment"], override_ticket=o["ticket"], approved_by=o["approved_by"], approved_on=D(o["approved_on"])) for o in OVERRIDE]
with pd.ExcelWriter(os.path.join(OUT, "vendor_master.xlsx")) as xw:
    pd.DataFrame(vm).to_excel(xw, sheet_name="vendors", index=False); pd.DataFrame(status_rows).to_excel(xw, sheet_name="status_history", index=False)
    pd.DataFrame(rel_rows).to_excel(xw, sheet_name="related_party_register", index=False); pd.DataFrame(ov_rows).to_excel(xw, sheet_name="block_overrides", index=False)
# bank change requests
BR = []
for v in vendors:
    for k in range(1, len(v["bank_hist"])):
        h, prev = v["bank_hist"][k], v["bank_hist"][k - 1]
        ts = h["ts"] or f"{D(h['frm'])}T{rnd.randint(9, 16)}:{rnd.randint(0, 59):02d}:00"
        BR.append(dict(vendor_id=vid_at(v, h["frm"]), legacy_vendor_id=v["legacy"], old_account=fmt_acct(prev["acct"], 1), new_account=fmt_acct(h["acct"], 1), requested_at=ts, requested_by=h["by"],
                       callback_verified=h["verified"], ticket_ref=h["ticket"], effective_from=D(h["frm"])))
json.dump({"exported": "2025-10-01", "changes": sorted(BR, key=lambda r: r["requested_at"])}, open(os.path.join(OUT, "bank_change_requests.json"), "w"), indent=0)
# contracts
vn = {v["legacy"]: v["name"] for v in vendors}
with pd.ExcelWriter(os.path.join(OUT, "contracts_register.xlsx")) as xw:
    pd.DataFrame([dict(contract_id=c["contract_id"], vendor_id=c["_v"], vendor_name=vn[c["_v"]], start_date=D(c["start"]), end_date=D(c["end"]), cap_value=c["cap"]) for c in contracts]).to_excel(xw, sheet_name="contracts", index=False)
    pd.DataFrame([dict(contract_id=a["contract_id"], effective_date=D(a["effective"]), new_cap_value=a["new_cap"], reason=a["reason"]) for a in AMEND]).to_excel(xw, sheet_name="amendments", index=False)
json.dump(dict(truth=[{k: (v if not isinstance(v, float) else round(v, 2)) for k, v in t.items()} for t in TRUTH], ghosts=[v["legacy"] for v in ghosts], related=[r["v"]["legacy"] for r in related], bec=[v["legacy"] for v in bec],
               clerk_y=clerk_y["emp_id"], clerk_z=clerk_z["emp_id"], contracts_overrun=[c["contract_id"] for c in contracts if c["kind"] == "overrun"], amended=[c["contract_id"] for c in contracts if c["kind"] == "amended"]),
          open(os.path.join(HERE, "world_truth.json"), "w"), indent=1)
print("exported", len(inv_rows), len(pay_rows))

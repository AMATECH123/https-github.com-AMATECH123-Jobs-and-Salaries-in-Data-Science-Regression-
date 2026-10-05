"""Brightwater Precision Components, Inc. tax year 2024 dataset. All data is synthetic."""
import os, json, math, random, datetime as dt
import numpy as np, pandas as pd
import taxlaw as T
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, "..", "inputs"); os.makedirs(OUT, exist_ok=True)
SEED = int(os.environ.get("TASK_SEED", 20251110)); rng = np.random.default_rng(SEED); rnd = random.Random(SEED)
Y0, Y1 = dt.date(2024, 1, 1), dt.date(2024, 12, 31)
def D(d): return d.isoformat()
def rdate(a, b): return a + dt.timedelta(days=rnd.randint(0, (b - a).days))
FIRST = "James Mary Robert Patricia John Jennifer Michael Linda David Elizabeth William Barbara Richard Susan Joseph Jessica Thomas Sarah Charles Karen Chris Nancy Daniel Lisa Matthew Betty Anthony Sandra Mark Ashley Donald Emily Steven Kimberly Paul Donna Andrew Michelle Joshua Carol Kenneth Amanda Kevin Melissa Brian Deborah George Stephanie Edward Rebecca Ronald Laura Timothy Sharon Jason Cynthia Priya Arjun Ananya Rohan Neha Vikram".split()
LAST = "Smith Johnson Williams Brown Jones Garcia Miller Davis Rodriguez Martinez Hernandez Lopez Gonzalez Wilson Anderson Thomas Taylor Moore Jackson Martin Lee Perez Thompson White Harris Sanchez Clark Ramirez Lewis Robinson Walker Young Allen King Wright Scott Torres Nguyen Hill Flores Green Adams Nelson Baker Hall Sharma Patel Iyer Rao Gupta Nair".split()

# ============================================================================ employees / payroll
DEPTS = [  # dept, n, avg annual wage, location, pct range of time on qualified R&E
    ("R&D Engineering", 52, 128000, "US", (0.55, 1.00)), ("Software Development", 18, 142000, "US", (1.00, 1.00)), ("R&D Engineering India", 14, 52000, "IN", (0.70, 1.00)),
    ("Quality Lab", 22, 78000, "US", (0.0, 0.0)), ("Production", 240, 56000, "US", (0.0, 0.0)), ("Administration", 55, 84000, "US", (0.0, 0.0)), ("Sales & Marketing", 42, 96000, "US", (0.0, 0.0))]
emps = []; eid = 0
for dept, n, wage, loc, (lo, hi) in DEPTS:
    for _ in range(n):
        eid += 1; w = round(float(rng.lognormal(math.log(wage), 0.22)), -2)
        emps.append(dict(emp_id=f"EMP{eid:04d}", name=f"{rnd.choice(FIRST)} {rnd.choice(LAST)}", dept=dept, location=loc, annual_wages_2024=w, pct_time_qualified_research=round(rnd.uniform(lo, hi), 2) if hi > 0 else 0.0))
dept_wages = {d[0]: sum(e["annual_wages_2024"] for e in emps if e["dept"] == d[0]) for d in DEPTS}
rd_dom_wages = sum(e["annual_wages_2024"] * e["pct_time_qualified_research"] for e in emps if e["location"] == "US")
rd_for_wages = sum(e["annual_wages_2024"] * e["pct_time_qualified_research"] for e in emps if e["location"] == "IN")

# ============================================================================ contractors (R&E) / supplies
contr = []
VENDORS_US = ["Northgate Engineering LLC", "Summit Prototyping Inc", "Lakeshore Software Partners", "Ironwood Test Labs", "Meridian Design Group"]
VENDORS_IN = ["Pune Embedded Systems Pvt Ltd", "Chennai Software Works Pvt Ltd", "Bengaluru Simulation Labs Pvt Ltd"]
RE_DESC = ["Software development - controller firmware", "Prototype engineering - new actuator design", "Development of simulation models for new alloy process", "Software development - MES integration module", "Design and build of pre-production tooling prototype"]
NON_DESC = ["Metallurgical testing for product quality control", "Routine inspection and calibration testing", "Market research study - customer survey", "Production-line efficiency survey"]
for i in range(88):
    us = rnd.random() < 0.78; v = rnd.choice(VENDORS_US if us else VENDORS_IN); re = rnd.random() < 0.82
    contr.append(dict(invoice_id=f"CTR-{i+1:04d}", vendor=v, vendor_country=("US" if us else "IN"), invoice_date=D(rdate(Y0, Y1)), description=rnd.choice(RE_DESC if re else NON_DESC), amount=round(float(rng.lognormal(math.log(21000 if us else 13000), 0.5)), 2), _re=re))
rd_dom_contr = sum(c["amount"] for c in contr if c["_re"] and c["vendor_country"] == "US"); rd_for_contr = sum(c["amount"] for c in contr if c["_re"] and c["vendor_country"] == "IN")

# ============================================================================ fixed assets
assets = []; aid = [0]
def add_asset(desc, cls, cost, date, kind="std", prior=False, **kw):
    aid[0] += 1; a = dict(asset_id=f"FA{aid[0]:04d}", description=desc, tax_class=cls, cost=round(cost, 2), in_service=date, kind=kind, prior=prior); a.update(kw); assets.append(a); return a
# prior-year assets (tax depreciation for 2024 already computed in prior workpapers)
for i in range(78):
    cls = rnd.choice(["5", "7", "7", "7", "15", "39"]); cost = float(rng.lognormal(math.log(180000 if cls != "39" else 900000), 0.8)); d = rdate(dt.date(2016, 1, 1), dt.date(2023, 12, 20))
    life = {"5": 5, "7": 10, "15": 15, "39": 39}[cls]; yrs_in = (2024 - d.year)
    tax24 = cost * rnd.uniform(0.02, 0.14) if yrs_in < 8 and cls != "39" else (cost / 39 if cls == "39" else cost * 0.01)
    add_asset(f"{rnd.choice(['CNC lathe','Stamping press','Forklift','Compressor','Server rack','Paint booth','Warehouse racking','Welding cell','Inspection CMM','Conveyor system','HVAC chiller','Dock levelers'])} #{i+1}", cls, cost, d, "std" if cls != "39" else "building", prior=True,
              book_life_years=life + 2, book_depr_2024=round(cost / (life + 2) if yrs_in < life + 2 else 0.0, 2), tax_depr_2024_existing=round(tax24, 2))
# 2024 additions (kind drives the tax treatment; sizes tuned below)
ADD = []
ADD.append(add_asset("CNC machining center (Haas VF-10)", "7", 1180000, dt.date(2024, 2, 20), "std"))
ADD.append(add_asset("Fiber laser cutting system", "7", 760000, dt.date(2024, 5, 14), "std"))
ADD.append(add_asset("Automated packaging line", "7", 320000, dt.date(2024, 8, 12), "std"))
ADD.append(add_asset("Furniture, fixtures - new offices", "7", 150000, dt.date(2024, 3, 8), "std"))
ADD.append(add_asset("Forklift fleet (3 units)", "5", 90000, dt.date(2024, 7, 9), "std"))
ADD.append(add_asset("Sedan - executive pool (GVWR 4,100 lbs)", "5", 52000, dt.date(2024, 8, 5), "auto", gvwr_lbs=4100, business_use_pct=100))
ADD.append(add_asset("Press brake", "7", 460000, dt.date(2024, 11, 6), "std"))
ADD.append(add_asset("Server and network refresh", "5", 330000, dt.date(2024, 10, 21), "std"))
ADD.append(add_asset("SUV - sales fleet (GVWR 6,400 lbs)", "5", 68000, dt.date(2024, 10, 28), "suv", gvwr_lbs=6400, business_use_pct=100))
ADD.append(add_asset("Parking lot and drainage (land improvements)", "15", 480000, dt.date(2024, 11, 18), "li"))
ADD.append(add_asset("Robot welding cell", "7", 0, dt.date(2024, 12, 3), "std"))      # cost tuned below
ADD.append(add_asset("Warehouse addition (nonresidential real property)", "39", 2400000, dt.date(2024, 9, 12), "building"))
SMALL = []
for i in range(16):
    SMALL.append(add_asset(rnd.choice(["Standing desks (set of 4)", "Label printer", "Conference room displays", "Handheld scanners (set)", "Workbench set", "Test bench PC", "Air compressor (portable)", "Office copier"]) + f" #{i+1}", "5" if rnd.random() < 0.5 else "7",
                           round(rnd.uniform(1800, 4900), 2), rdate(dt.date(2024, 1, 15), dt.date(2024, 12, 15)), "std", small=True))
ELECTION = [("CNC machining center (Haas VF-10)", 1180000), ("Fiber laser cutting system", 760000)]      # CFO memo order of preference
def build_adds():
    return [dict(id=a["asset_id"], cls=a["tax_class"], cost=a["cost"], date=a["in_service"], kind=a["kind"], _name=a["description"]) for a in assets if not a["prior"]]   # book policy capitalises >= 1,800, so no item qualifies for the de minimis safe harbor
adds = build_adds(); id_by_name = {x["_name"]: x["id"] for x in adds}; order = [(id_by_name[n], amt) for n, amt in ELECTION]
per, summ = T.depreciation_additions(adds, order)
gross_q4 = sum(x["cost"] for x in adds if x["cls"] != "39" and T.quarter(x["date"]) == 4) / sum(x["cost"] for x in adds if x["cls"] != "39")
print("179 limit", summ["s179_limit"], "| Q4 share after 179", round(summ["q4_share"], 4), "| gross Q4 share", round(gross_q4, 4), "| mid-quarter", summ["mid_quarter"])
for a in assets:
    if not a["prior"]:
        a["book_life_years"] = {"5": 7, "7": 10, "15": 15, "39": 39}[a["tax_class"]] if not a.get("small") else 5
        a["book_depr_2024"] = round(a["cost"] / a["book_life_years"] * ((12 - a["in_service"].month + 0.5) / 12), 2)
        a["tax_depr_2024_existing"] = None
# disposals
dispos = []
for k, (cls, cost, yr) in enumerate([("7", 410000, 2018), ("5", 155000, 2021)]):
    a = add_asset(f"Disposed: {rnd.choice(['Stamping press','Injection molder'])} #D{k+1}", cls, cost, dt.date(yr, 6, 15), "std", prior=True, book_life_years=10, book_depr_2024=0.0, tax_depr_2024_existing=0.0)
    proceeds = round(cost * rnd.uniform(0.22, 0.33), 2); tax_basis = round(cost * rnd.uniform(0.04, 0.12), 2); book_nbv = round(cost * rnd.uniform(0.35, 0.5), 2)
    dispos.append(dict(asset_id=a["asset_id"], disposal_date=D(rdate(dt.date(2024, 3, 1), dt.date(2024, 11, 30))), proceeds=proceeds, adjusted_tax_basis=tax_basis, book_net_value=book_nbv))
book_depr_total = sum(a["book_depr_2024"] for a in assets)

# ============================================================================ accruals schedule
accr = []
def acr(kind, year, payee, owner, amt, paid):
    accr.append(dict(item=f"ACR{len(accr)+1:04d}", type=kind, accrued_year=year, payee=payee, payee_is_majority_shareholder=owner, accrued_amount=round(amt, 2), paid_date=D(paid) if paid else ""))
for i in range(125): acr("bonus", 2024, f"EMP{rnd.randint(1, 440):04d}", "N", float(rng.lognormal(math.log(9500), 0.5)), rdate(dt.date(2025, 2, 10), dt.date(2025, 3, 14)))
for i in range(6): acr("bonus", 2024, f"EMP{rnd.randint(1, 440):04d}", "N", float(rng.lognormal(math.log(14000), 0.4)), rdate(dt.date(2025, 3, 18), dt.date(2025, 4, 10)))       # paid late
acr("bonus", 2024, "CEO R. Hale (owns 60%)", "Y", 450000, dt.date(2025, 4, 11))
acr("vacation", 2024, "All employees (accrued PTO)", "N", 418000, None)
acr("bonus", 2023, "CEO R. Hale (owns 60%)", "Y", 350000, dt.date(2024, 1, 19))
for i in range(60): acr("bonus", 2023, f"EMP{rnd.randint(1, 440):04d}", "N", float(rng.lognormal(math.log(8800), 0.5)), rdate(dt.date(2024, 2, 5), dt.date(2024, 3, 12)))          # paid in time: deducted in 2023
for i in range(4): acr("bonus", 2023, f"EMP{rnd.randint(1, 440):04d}", "N", float(rng.lognormal(math.log(12000), 0.4)), rdate(dt.date(2024, 3, 25), dt.date(2024, 5, 3)))             # paid late: deductible 2024
acr("vacation", 2023, "All employees (accrued PTO)", "N", 391000, dt.date(2024, 9, 30))   # taken/paid during 2024 (after the 2.5 month window)
def accrual_tax_2024(rows):
    book = tax = 0.0
    for r in rows:
        paid = dt.date.fromisoformat(r["paid_date"]) if r["paid_date"] else None; amt = r["accrued_amount"]; owner = r["payee_is_majority_shareholder"] == "Y"
        if r["accrued_year"] == 2024:
            book += amt
            if (not owner) and paid and paid <= T.ACCRUAL_DEADLINE: tax += amt
            elif owner and paid and paid.year == 2024: tax += amt
        elif r["accrued_year"] == 2023 and paid and paid.year == 2024:
            deducted_2023 = (not owner) and paid <= dt.date(2024, 3, 15)
            if not deducted_2023: tax += amt
    return book, tax
acc_book, acc_tax = accrual_tax_2024(accr)

print("people", len(emps), "dept wages", {k: round(v) for k, v in dept_wages.items()}); print("R&E wages dom", round(rd_dom_wages), "for", round(rd_for_wages), "| contractors dom", round(rd_dom_contr), "for", round(rd_for_contr))
print("book depreciation", round(book_depr_total), "| accrual book/tax", round(acc_book), round(acc_tax))
import pickle; pickle.dump(dict(emps=emps, contr=contr, assets=assets, dispos=dispos, accr=accr, adds=adds, order=order, per=per, summ=summ, rd_dom_wages=rd_dom_wages, rd_for_wages=rd_for_wages,
                               rd_dom_contr=rd_dom_contr, rd_for_contr=rd_for_contr, dept_wages=dept_wages, book_depr_total=book_depr_total, acc_book=acc_book, acc_tax=acc_tax, SMALL=[a["asset_id"] for a in SMALL]), open(os.path.join(HERE, "stage1.pkl"), "wb"))

# ============================================================================ GL
ACCTS = {  # code: (name, type)
 "1210": ("Allowance for doubtful accounts", "balance sheet"), "4000": ("Product sales", "revenue"), "5000": ("Materials purchased", "cogs"), "5100": ("Direct labor", "cogs"), "5200": ("Manufacturing overhead", "cogs"),
 "5300": ("Quality control labor", "cogs"), "6000": ("Administrative salaries", "opex"), "6010": ("Sales salaries", "opex"), "6100": ("Bonus expense", "opex"), "6110": ("Accrued vacation expense", "opex"),
 "6200": ("Payroll taxes and benefits", "opex"), "6300": ("Rent and utilities", "opex"), "6400": ("Meals and entertainment", "opex"), "6410": ("Travel", "opex"), "6420": ("Client gifts", "opex"), "6210": ("Employee transportation benefits", "opex"), "6500": ("R&D payroll", "opex"),
 "6510": ("R&D materials and prototypes", "opex"), "6520": ("Quality test materials", "opex"), "6530": ("Contract engineering and studies", "opex"), "6600": ("Professional fees", "opex"), "6700": ("Insurance", "opex"),
 "6710": ("Dues and subscriptions", "opex"), "6720": ("Penalties and fines", "opex"), "6730": ("Late fees and finance charges", "opex"), "6800": ("Advertising and marketing", "opex"), "6810": ("Bad debt expense", "opex"),
 "6900": ("Depreciation expense", "opex"), "6950": ("Other general and administrative", "opex"), "7000": ("Interest expense", "other"), "7100": ("Interest income", "other"), "7200": ("Gain or loss on sale of equipment", "other"),
 "8000": ("State income tax expense", "tax"), "8100": ("Federal income tax expense (book provision)", "tax")}
GL = []; je = [0]
CC = ["CC100", "CC200", "CC300", "CC400", "CC500", "CC600"]
def gl(date, code, memo, vendor, amount, cc=None):
    """amount > 0 = debit, < 0 = credit"""
    je[0] += 1; GL.append(dict(je_id=f"JE{je[0]:06d}", post_date=date, account_code=code, account_name=ACCTS[code][0], description=memo, vendor=vendor, debit=round(max(amount, 0), 2), credit=round(max(-amount, 0), 2), cost_center=cc or rnd.choice(CC)))
CLIENTS = ["Allied Aerospace", "Northwind Energy", "Cardinal Medical", "Summit Rail", "Ironclad Tools", "Granite Hydraulics", "Pioneer Automotive", "Keystone Defense"]
CITIES = ["Detroit", "Houston", "Phoenix", "Atlanta", "Denver", "Seattle", "Boston", "Dallas", "Chicago", "Charlotte"]
MATV = ["Apex Steel Service", "Midwest Alloys", "Precision Bearings Inc", "Lakeshore Fasteners", "Titan Castings", "Everest Polymers", "Granite Coatings", "Allied Wire & Cable", "Northstar Forgings", "Ridgeline Plastics"]
tr = dict(meals50=0.0, ent0=0.0, party100=0.0, fines=0.0, lobby=0.0, keyman=0.0, bad_prov=0.0, writeoffs=0.0, proto=0.0, qc_supplies=0.0, contr_all=0.0, interest=0.0, int_income=0.0)
# payroll summaries (semi-monthly) by department
PP = [dt.date(2024, m, d) for m in range(1, 13) for d in (15, 28)]
dept_acct = {"R&D Engineering": "6500", "Software Development": "6500", "R&D Engineering India": "6500", "Quality Lab": "5300", "Production": "5100", "Administration": "6000", "Sales & Marketing": "6010"}
for dept, tot in dept_wages.items():
    parts = np.array(rng.uniform(0.9, 1.1, 24)); parts = parts / parts.sum() * tot; parts = np.round(parts, 2); parts[-1] = round(tot - parts[:-1].sum(), 2)
    for k, d in enumerate(PP): gl(d, dept_acct[dept], f"Payroll - {dept} - pay period {k+1}", "ADP Payroll", float(parts[k]), "CC300")
tot_wages = sum(dept_wages.values())
for k, d in enumerate(PP): gl(d, "6200", f"Payroll taxes and benefits - pay period {k+1}", "ADP Payroll", round(tot_wages * 0.215 / 24, 2), "CC300")
# bonus and vacation accruals (2024)
bon = sum(r["accrued_amount"] for r in accr if r["accrued_year"] == 2024 and r["type"] == "bonus"); vac = sum(r["accrued_amount"] for r in accr if r["accrued_year"] == 2024 and r["type"] == "vacation")
for m in range(1, 13): gl(dt.date(2024, m, 28), "6100", f"Accrued bonus - 2024 plan - month {m}", "Accrual", round(bon / 12, 2))
GL[-1]["debit"] = round(bon - round(bon / 12, 2) * 11, 2)
gl(Y1, "6110", "Year-end accrual of unused vacation (PTO)", "Accrual", vac)
# materials and overhead
for i in range(9000): gl(rdate(Y0, Y1), "5000", f"Materials - PO {rnd.randint(100000, 999999)} - {rnd.choice(['bar stock','sheet','castings','fasteners','coatings','resin','wire','bearings'])}", rnd.choice(MATV), float(rng.lognormal(math.log(3300), 0.9)))
for i in range(3800): gl(rdate(Y0, Y1), "5200", rnd.choice(["Factory utilities", "Tooling consumables", "Equipment repair", "Safety supplies", "Freight in", "Plant maintenance", "Cutting fluids"]) + f" inv {rnd.randint(10000, 99999)}", rnd.choice(["Grainger", "MSC Industrial", "ComEd", "Nicor Gas", "FedEx Freight", "Uline"]), float(rng.lognormal(math.log(1500), 0.8)))
for i in range(2400): gl(rdate(Y0, Y1), "6950", rnd.choice(["Office supplies", "Software subscription", "Telecom", "Printing", "Courier", "Training course", "Recruiting fee", "IT support"]) + f" inv {rnd.randint(10000, 99999)}", rnd.choice(["Staples", "Microsoft", "AT&T", "Indeed", "Dell", "Zoom"]), float(rng.lognormal(math.log(700), 0.9)))
for m in range(1, 13): gl(dt.date(2024, m, 1), "6300", "Rent and utilities - HQ and plant", "Lakeshore Properties", round(float(rng.uniform(150000, 175000)), 2))
for i in range(180): gl(rdate(Y0, Y1), "6600", rnd.choice(["Legal fees", "Audit fees", "Tax advisory", "Consulting"]) + f" inv {rnd.randint(1000, 9999)}", rnd.choice(["Hale & Dorr LLP", "BDO", "Marsh", "KPMG"]), float(rng.lognormal(math.log(4200), 0.8)))
for i in range(400): gl(rdate(Y0, Y1), "6800", rnd.choice(["Trade show booth", "Digital advertising", "Catalog printing", "Sponsorship", "Website"]) + f" inv {rnd.randint(1000, 9999)}", rnd.choice(["Thomasnet", "Google Ads", "LinkedIn", "ProPrint"]), float(rng.lognormal(math.log(1400), 0.8)))
# travel and meals
for i in range(1300): gl(rdate(Y0, Y1), "6410", rnd.choice(["Airfare", "Hotel", "Rental car", "Ground transport"]) + f" - {rnd.choice(CITIES)} trip {rnd.randint(1000, 9999)}", rnd.choice(["Delta", "Marriott", "Hertz", "Uber"]), float(rng.lognormal(math.log(650), 0.6)))
for i in range(900):
    a = float(rng.lognormal(math.log(165), 0.5)); gl(rdate(Y0, Y1), "6400", f"Client dinner - {rnd.choice(CLIENTS)} (taxpayer present)", rnd.choice(["Morton's", "Capital Grille", "Ruth's Chris", "Local restaurant"]), a); tr["meals50"] += a
for i in range(600):
    a = float(rng.uniform(40, 95)); gl(rdate(Y0, Y1), "6400", f"Meals - travel per diem {rnd.choice(CITIES)}", "Employee reimbursement", a); tr["meals50"] += a
for nm, a in (("Holiday party - all employees: venue", 41200), ("Holiday party - all employees: catering", 28750), ("Holiday party - all employees: band and entertainment", 8900), ("Employee summer picnic - all employees", 21400)):
    gl(rdate(dt.date(2024, 6, 1) if "picnic" in nm else dt.date(2024, 12, 1), dt.date(2024, 6, 28) if "picnic" in nm else dt.date(2024, 12, 20)), "6400", nm, "Event vendor", a); tr["party100"] += a
for i in range(40):
    a = float(rng.uniform(450, 1500)); gl(rdate(Y0, Y1), "6400", f"Client entertainment - {rnd.choice(['Bulls','Bears','Cubs','Blackhawks'])} tickets - {rnd.choice(CLIENTS)}", "Ticketmaster", a); tr["ent0"] += a
for q, a in enumerate((11800, 12400, 11200, 12600)): gl(dt.date(2024, 3 * q + 3, 15), "6400", "Suite rental - client entertainment", "United Center Suites", a); tr["ent0"] += a
# client gifts ($25 per recipient limit) and employee transit passes (nondeductible)
RECIP = [(f"{rnd.choice(FIRST)} {rnd.choice(LAST)}", rnd.choice(CLIENTS)) for _ in range(70)]   # each recipient belongs to one client company
gift_by = {}
for i in range(190):
    r, co = rnd.choice(RECIP); a = round(float(rng.choice([45, 60, 75, 90, 120, 185, 240])), 2); gift_by[r] = gift_by.get(r, 0.0) + a
    gl(rdate(Y0, Y1), "6420", f"Client gift - {r} ({co}) - {rnd.choice(['gift basket','wine','gift card','steak set'])}", "Gift vendor", a)
tr["gift_excess"] = sum(max(0.0, v - T.GIFT_LIMIT_PER_RECIPIENT) for v in gift_by.values())
for m in range(1, 13):
    gl(dt.date(2024, m, 3), "6210", "Employee transit pass subsidy - qualified transportation fringe", "Commuter benefits provider", 17800.0); tr["transit"] = tr.get("transit", 0.0) + 17800.0
# dues with lobbying notices
ASSOC = [("Industrial Manufacturers Association", 38000, 15), ("State Chamber of Commerce", 12000, 22), ("Precision Metalforming Association", 15000, 0), ("Aerospace Suppliers Forum", 9000, 8), ("Local Business Council", 6000, 0)]
for nm, qa, pct in ASSOC:
    for q in range(4):
        gl(dt.date(2024, 3 * q + 2, 10), "6710", f"{nm} dues Q{q+1} - notice: {pct}% of dues used for lobbying", nm, qa); tr["lobby"] += qa * pct / 100.0
# insurance
for m in range(1, 13):
    gl(dt.date(2024, m, 5), "6700", "Key-man life insurance premium - CEO policy - beneficiary: Company", "Northwestern Mutual", 5200); tr["keyman"] += 5200
    gl(dt.date(2024, m, 5), "6700", "Group term life insurance premium - employees", "Prudential", 11000)
    gl(dt.date(2024, m, 6), "6700", "Property and casualty insurance premium", "Travelers", float(rng.uniform(52000, 61000)))
# penalties
for nm, a, pen in (("OSHA citation - penalty paid (Docket 2024-0412)", 28000, 1), ("EPA consent order - civil penalty", 41000, 1), ("State annual report late filing penalty", 1200, 1), ("Parking violation fines", 760, 1), ("Late payment fee - Grainger invoice", 1400, 0), ("Customs duty and broker fees", 18600, 0)):
    gl(rdate(Y0, Y1), "6720" if pen else "6730", nm, "Agency/vendor", a)
    if pen: tr["fines"] += a
# bad debts
prov = 312000
for m in range(1, 13): gl(dt.date(2024, m, 28), "6810", f"Provision for doubtful accounts - month {m}", "Allowance JE", round(prov / 12, 2))
wo = []
for i in range(38):
    a = float(rng.lognormal(math.log(6200), 0.6)); wo.append(a); gl(rdate(Y0, Y1), "1210", f"Write-off of uncollectible receivable - invoice {rnd.randint(20000, 99999)} - customer bankrupt/uncollectible", "AR", a)
tr["bad_prov"] = prov; tr["writeoffs"] = sum(wo)
# R&D supplies and contractors
for i in range(320):
    a = float(rng.lognormal(math.log(1900), 0.6)); gl(rdate(Y0, Y1), "6510", f"Prototype materials - project {rnd.choice(['Atlas','Boreal','Cobalt','Dune','Ember','Fjord'])}", rnd.choice(MATV), a); tr["proto"] += a
for i in range(150):
    a = float(rng.lognormal(math.log(1100), 0.6)); gl(rdate(Y0, Y1), "6520", f"Quality test materials - lot {rnd.randint(1000, 9999)}", rnd.choice(MATV), a); tr["qc_supplies"] += a
for c in contr: gl(dt.date.fromisoformat(c["invoice_date"]), "6530", f"{c['description']} - {c['vendor']} - {c['invoice_id']}", c["vendor"], c["amount"]); tr["contr_all"] += c["amount"]
# depreciation, interest, disposals, state tax
bd = round(book_depr_total / 12, 2)
for m in range(1, 13): gl(dt.date(2024, m, 28), "6900", f"Monthly depreciation - book basis - {m}", "Fixed asset subledger", bd)
GL[-1]["debit"] = round(book_depr_total - bd * 11, 2)
BIE_TOTAL = 7400000.0; BII_TOTAL = 112000.0
for m in range(1, 13):
    gl(dt.date(2024, m, 30) if m != 2 else dt.date(2024, 2, 29), "7000", f"Interest expense - term loan and revolver - month {m}", "First National Bank", round(BIE_TOTAL / 12, 2)); tr["interest"] += round(BIE_TOTAL / 12, 2)
    gl(dt.date(2024, m, 28), "7100", f"Interest income - operating accounts - month {m}", "First National Bank", -round(BII_TOTAL / 12, 2)); tr["int_income"] += round(BII_TOTAL / 12, 2)
book_gain = 0.0
for d_ in dispos:
    g = d_["proceeds"] - d_["book_net_value"]; book_gain += g; nm = next(a["description"] for a in assets if a["asset_id"] == d_["asset_id"])
    gl(dt.date.fromisoformat(d_["disposal_date"]), "7200", f"{'Gain' if g >= 0 else 'Loss'} on sale of equipment - {nm} - proceeds {d_['proceeds']:,.2f}", "Equipment buyer", -g)
for q in range(4): gl(dt.date(2024, 3 * q + 3, 20), "8000", f"State income tax - installment {q+1}", "State DOR", 56000)
state_tax = 224000

# ============================================================================ truth (Schedule M-1 style) and revenue plug
exp = sum(g["debit"] - g["credit"] for g in GL if ACCTS[g["account_code"]][1] in ("cogs", "opex", "other", "tax") and g["account_code"] != "8100")
prior = dict(re_dom_2022=0.0, re_dom_2023=0.0, re_for_2022=0.0, re_for_2023=0.0)
dom_re = rd_dom_wages + rd_dom_contr + tr["proto"]; for_re = rd_for_wages + rd_for_contr
prior["re_dom_2023"] = round(dom_re * 0.93, -3); prior["re_dom_2022"] = round(dom_re * 0.84, -3); prior["re_for_2023"] = round(for_re * 0.88, -3); prior["re_for_2022"] = round(for_re * 0.71, -3)
amort_dom, amort_for = T.re_amortization(dom_re, for_re, prior["re_dom_2023"], prior["re_for_2023"], prior["re_dom_2022"], prior["re_for_2022"])
small_cost = 0.0   # de minimis safe harbor: nothing expensed on the books below the 5,000 ceiling
tax_depr_new = sum(v["total"] for v in per.values()); tax_depr_exist = sum(a["tax_depr_2024_existing"] for a in assets if a["prior"])
tax_depr_total = tax_depr_new + tax_depr_exist + small_cost
tax_gain = sum(d_["proceeds"] - d_["adjusted_tax_basis"] for d_ in dispos)
adj = dict(meals_50pct=0.5 * tr["meals50"], entertainment=tr["ent0"], fines_penalties=tr["fines"], lobbying=tr["lobby"], key_man_life=tr["keyman"], gifts_over_25=tr["gift_excess"], transit_passes=tr["transit"],
           bad_debts=tr["bad_prov"] - tr["writeoffs"], accruals=acc_book - acc_tax, depreciation=book_depr_total - tax_depr_total, disposals=tax_gain - book_gain, sec174=(dom_re + for_re) - (amort_dom + amort_for))
TARGET_TI0 = 14_200_000.0
pretax = TARGET_TI0 - sum(adj.values()); revenue_total = exp + pretax
ndays = (Y1 - Y0).days + 1; dayw = rng.uniform(0.7, 1.3, ndays); dayw = dayw / dayw.sum() * revenue_total
for k in range(ndays): gl(Y0 + dt.timedelta(days=k), "4000", "Daily product sales summary", "Customers", -round(float(dayw[k]), 2), "CC100")
gl(Y1, "8100", "Provision for federal income taxes - book (current)", "Tax provision JE", 1_050_000.0)
# recompute exact totals from the final GL
revenue = -sum(g["debit"] - g["credit"] for g in GL if g["account_code"] == "4000")
book_pretax = sum(-(g["debit"] - g["credit"]) for g in GL if ACCTS[g["account_code"]][1] in ("revenue", "cogs", "opex", "other", "tax") and g["account_code"] != "8100")
ti0 = book_pretax + sum(adj.values())
j = T.sec163j(ti0, BIE_TOTAL, BII_TOTAL, 450000.0)
ti1 = ti0 + BIE_TOTAL - j["deductible"]
NOL_BAL = round(ti1 * 0.8 * 1.12, -3)
n = T.nol(ti1, NOL_BAL); taxable = ti1 - n["deduction"]; tax = taxable * T.RATE
payments = [dict(payment_date="2024-04-15", description="Estimated tax - Q1", amount=40000.0), dict(payment_date="2024-06-17", description="Estimated tax - Q2", amount=40000.0),
            dict(payment_date="2024-09-16", description="Estimated tax - Q3", amount=40000.0), dict(payment_date="2024-12-16", description="Estimated tax - Q4", amount=40000.0), dict(payment_date="2025-04-15", description="Extension payment (Form 7004)", amount=25000.0)]
paid = sum(p["amount"] for p in payments); balance = tax - paid
TRUTH = dict(book_pretax=book_pretax, adjustments=adj, ti_before_163j=ti0, sec163j=j, ti_after_163j=ti1, nol_balance=NOL_BAL, nol=n, taxable_income=taxable, tax=tax, payments=paid, balance_due=balance,
             depreciation=dict(summ=summ, new_total=tax_depr_new, existing=tax_depr_exist, de_minimis=small_cost, per=per), re=dict(dom_2024=dom_re, for_2024=for_re, **prior, amort_dom=amort_dom, amort_for=amort_for),
             accruals=dict(book=acc_book, tax=acc_tax), meals=dict(meals_lines=tr["meals50"], entertainment=tr["ent0"], party100=tr["party100"]), lobby=tr["lobby"], keyman=tr["keyman"], fines=tr["fines"], bad=dict(prov=tr["bad_prov"], writeoffs=tr["writeoffs"]),
             disposals=dict(tax_gain=tax_gain, book_gain=book_gain), bie=BIE_TOTAL, bii=BII_TOTAL, carryforward_in=450000.0, revenue=revenue)
print(json.dumps({k: (round(v, 0) if isinstance(v, float) else v) for k, v in TRUTH.items() if k in ("book_pretax", "ti_before_163j", "ti_after_163j", "nol_balance", "taxable_income", "tax", "payments", "balance_due")}, indent=1))
print({k: round(v) for k, v in adj.items()}); print("163j", {k: round(v) for k, v in j.items()}, "| nol", {k: round(v) for k, v in n.items()}); print("GL rows", len(GL), "| revenue", round(revenue))
pickle.dump(dict(GL=GL, TRUTH=TRUTH, payments=payments, prior=prior, ASSOC=ASSOC), open(os.path.join(HERE, "stage2.pkl"), "wb"))

# ============================================================================ export
gldf = pd.DataFrame(GL).sort_values(["post_date", "je_id"])
gldf["post_date"] = [d.strftime("%m/%d/%Y") if d >= dt.date(2024, 7, 1) else d.isoformat() for d in gldf.post_date]   # the ERP changed the date format on 1 Jul 2024
gldf.loc[gldf.account_code == "6400", "account_name"] = [("Meals & Ent." if d[2] == "/" or d[:2] in ("07", "08", "09", "10", "11", "12") else "Meals and entertainment") for d in gldf[gldf.account_code == "6400"].post_date]
gldf.to_csv(os.path.join(OUT, "gl_transactions.csv"), index=False)
pd.DataFrame([dict(account_code=k, account_name=v[0], account_type=v[1]) for k, v in ACCTS.items()]).to_excel(os.path.join(OUT, "chart_of_accounts.xlsx"), index=False)
arows = []
for a in assets:
    arows.append(dict(asset_id=a["asset_id"], description=a["description"], tax_class_years=a["tax_class"], cost=a["cost"], in_service_date=D(a["in_service"]), book_life_years=a["book_life_years"], book_depreciation_2024=a["book_depr_2024"],
                      tax_depreciation_2024_prior_workpapers=a["tax_depr_2024_existing"], gvwr_lbs=a.get("gvwr_lbs"), business_use_pct=a.get("business_use_pct")))
with pd.ExcelWriter(os.path.join(OUT, "fixed_assets.xlsx")) as xw:
    pd.DataFrame(arows).to_excel(xw, sheet_name="assets", index=False); pd.DataFrame(dispos).to_excel(xw, sheet_name="disposals_2024", index=False)
pd.DataFrame([{k: v for k, v in e.items()} for e in emps]).to_csv(os.path.join(OUT, "payroll_register.csv"), index=False)
json.dump({"year": 2024, "invoices": [{k: v for k, v in c.items() if not k.startswith("_")} for c in contr]}, open(os.path.join(OUT, "contractor_invoices.json"), "w"), indent=0)
pd.DataFrame(accr).to_excel(os.path.join(OUT, "accrual_schedule.xlsx"), index=False)
pd.DataFrame(payments).to_csv(os.path.join(OUT, "tax_payments.csv"), index=False)
pickle.dump(dict(TRUTH=TRUTH, ELECTION=ELECTION, prior=prior, NOL_BAL=NOL_BAL), open(os.path.join(HERE, "truth.pkl"), "wb"))
json.dump(dict(book_pretax=round(book_pretax, 2), adjustments={k: round(v, 2) for k, v in adj.items()}, ti_before_163j=round(ti0, 2), sec163j={k: round(v, 2) for k, v in j.items()}, ti_after_163j=round(ti1, 2), nol_balance=NOL_BAL, nol_deduction=round(n["deduction"], 2),
               taxable_income=round(taxable, 2), tax=round(tax, 2), payments=paid, balance_due=round(balance, 2), depreciation=dict(s179_limit=summ["s179_limit"], s179_taken=summ["s179_taken"], mid_quarter=summ["mid_quarter"], q4_share=round(summ["q4_share"], 4),
               new_assets_total=round(tax_depr_new, 2), existing=round(tax_depr_exist, 2), de_minimis=round(small_cost, 2)), re=dict(dom_2024=round(dom_re, 2), for_2024=round(for_re, 2), amort_dom=round(amort_dom, 2), amort_for=round(amort_for, 2), **prior)),
          open(os.path.join(HERE, "world_truth.json"), "w"), indent=1)
print("exported", len(gldf), "GL rows")

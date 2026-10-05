"""US federal income tax rules for TAX YEAR 2024, calendar-year C corporation (pre-2025-legislation law).
Every constant carries its authority. This module is the single source of truth for the ground truth and for the reference solution."""
import datetime as dt

RATE = 0.21                                           # IRC 11(b)
# --- depreciation (IRC 168, 179, 280F) ---------------------------------------------------------------------------------
BONUS_2024 = 0.60                                     # IRC 168(k)(6)(A)(iii): 60% for property placed in service in 2024 (acquired after 9/27/2017)
S179_LIMIT_2024 = 1_220_000                           # Rev. Proc. 2023-34
S179_PHASEOUT_2024 = 3_050_000                        # Rev. Proc. 2023-34 (dollar-for-dollar reduction above this)
SUV_179_CAP_2024 = 30_500                             # IRC 179(b)(5) as indexed, Rev. Proc. 2023-34 (SUVs 6,001-14,000 lbs GVWR)
AUTO_CAP_Y1_BONUS_2024 = 20_400                       # IRC 280F(a), Rev. Proc. 2024-13: 12,400 + 8,000 when bonus is claimed (passenger auto <= 6,000 lbs)
MQ_THRESHOLD = 0.40                                   # IRC 168(d)(3): mid-quarter if > 40% of depreciable basis placed in service in Q4
HY = {"3": 33.33, "5": 20.00, "7": 14.29, "15": 5.00}   # Rev. Proc. 87-57 Table 1 first-year, half-year convention
MQ = {"3": [58.33, 41.67, 25.00, 8.33], "5": [35.00, 25.00, 15.00, 5.00], "7": [25.00, 17.85, 10.71, 3.57], "15": [8.75, 6.25, 3.75, 1.25]}  # Table 2-5, first-year, by quarter placed in service
RE39_FIRST = {1: 2.461, 2: 2.247, 3: 2.033, 4: 1.819, 5: 1.605, 6: 1.391, 7: 1.177, 8: 0.963, 9: 0.749, 10: 0.535, 11: 0.321, 12: 0.107}  # 39-year nonresidential real property, mid-month
DE_MINIMIS_AFS = 5_000                                # Treas. Reg. 1.263(a)-1(f)(1)(i): taxpayers with an AFS, per invoice/item, with annual election
GIFT_LIMIT_PER_RECIPIENT = 25.0                       # IRC 274(b)(1): business gifts deductible only up to $25 per recipient per year
TRANSIT_NONDEDUCTIBLE = True                          # IRC 274(a)(4): qualified transportation fringe (transit passes) not deductible by the employer
MEALS_PCT = 0.50                                      # IRC 274(n)(1)
LOBBY_NONDEDUCTIBLE = True                            # IRC 162(e); association dues disallowed in the notified lobbying percentage
SEC163J_PCT = 0.30                                    # IRC 163(j)(1)
NOL_PCT = 0.80                                        # IRC 172(a)(2) for NOLs arising in tax years beginning after 2017
RE_DOM_YEARS, RE_FOR_YEARS = 5, 15                    # IRC 174(a)(2)(B), mid-year convention IRC 174(a)(2)(B)(ii)
ACCRUAL_DEADLINE = dt.date(2025, 3, 15)               # Treas. Reg. 1.404(b)-1T Q&A-2: 2 1/2 months after year end (calendar year)

def quarter(d): return (d.month - 1) // 3 + 1

def depreciation_additions(adds, election_order):
    """adds: list of dict(id, cls, cost, date, kind in std|auto|suv|li|building). election_order: list of (id, requested_179).
    Returns (per_asset dict, summary dict)."""
    by = {a["id"]: a for a in adds}
    s179_prop = sum(a["cost"] for a in adds if a["kind"] not in ("building", "li"))   # 179 property cost (full cost counts toward the phase-out)
    limit = max(0.0, S179_LIMIT_2024 - max(0.0, s179_prop - S179_PHASEOUT_2024))
    remaining = limit; s179 = {a["id"]: 0.0 for a in adds}
    for aid, req in election_order:
        a = by[aid]; cap = 0.0 if a["kind"] in ("building", "li") else min(req, a["cost"], SUV_179_CAP_2024 if a["kind"] == "suv" else a["cost"])
        take = min(cap, remaining); s179[aid] = take; remaining -= take
    basis = {a["id"]: a["cost"] - s179[a["id"]] for a in adds if a["cls"] != "39"}
    tot = sum(basis.values()); q4 = sum(b for k, b in basis.items() if quarter(by[k]["date"]) == 4)
    mq = tot > 0 and q4 / tot > MQ_THRESHOLD
    per = {}
    for a in adds:
        i = a["id"]
        if a["cls"] == "39":
            per[i] = dict(s179=0.0, bonus=0.0, macrs=a["cost"] * RE39_FIRST[a["date"].month] / 100.0, total=a["cost"] * RE39_FIRST[a["date"].month] / 100.0); continue
        rem = a["cost"] - s179[i]; bonus = BONUS_2024 * rem; rem2 = rem - bonus
        rate = MQ[a["cls"]][quarter(a["date"]) - 1] if mq else HY[a["cls"]]
        macrs = rem2 * rate / 100.0; total = s179[i] + bonus + macrs
        if a["kind"] == "auto": total = min(total, AUTO_CAP_Y1_BONUS_2024)
        per[i] = dict(s179=s179[i], bonus=bonus, macrs=macrs, total=total)
    return per, dict(s179_limit=limit, s179_property_cost=s179_prop, s179_taken=sum(s179.values()), mid_quarter=mq, q4_share=(q4 / tot if tot else 0.0), basis_for_test=tot)

def re_amortization(dom24, for24, dom23, for23, dom22, for22):
    dom = 0.10 * dom24 + 0.20 * dom23 + 0.20 * dom22      # 5-year, midpoint: 10%, 20%, 20%, 20%, 20%, 10%
    fr = (1 / 30) * for24 + (2 / 30) * for23 + (2 / 30) * for22   # 15-year, midpoint: 1/30 first year, 2/30 thereafter
    return dom, fr

def sec163j(ti_before, bie, bii, carryforward):
    """ti_before = taxable income after deducting current business interest expense and including business interest income, before NOL.
    ATI for tax years beginning 2022-2024 is NOT increased by depreciation/amortization."""
    ati = ti_before + bie - bii
    limit = bii + SEC163J_PCT * max(0.0, ati)
    deductible = min(bie + carryforward, limit)
    return dict(ati=ati, limit=limit, deductible=deductible, disallowed_added_back=bie - deductible, carryforward_out=bie + carryforward - deductible)

def nol(ti, balance):
    ded = min(balance, NOL_PCT * max(0.0, ti)); return dict(deduction=ded, carryforward_out=balance - ded)

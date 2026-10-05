"""Data-generating model for the channel-budget task. Shared by the generator and the truth calculation."""
import numpy as np

CH = ["brand", "nonbrand", "meta", "lsa", "retarget"]
LABEL = {"brand": "Google Search - Brand", "nonbrand": "Google Search - Non-brand", "meta": "Meta Lead Ads",
         "lsa": "Google Local Services Ads", "retarget": "Retargeting (Display/Meta)"}
# weekly run-rate spend s0 (USD), expected attributed persons/week at s0 (average season), response exponent beta,
# cannibalised share rho (share of attributed persons who would have arrived anyway)
P = {
 "brand":    dict(s0=1333, a0=130, beta=0.30, rho=0.70, p_old=0.40, p_new=0.40, lag_med=3,  lag_sig=0.9, q_form=0.80, dup=0.05, mix=(0.65, 0.25, 0.10), ref_mult=0.8, ref_med=40, season_delta=0.10),
 "nonbrand": dict(s0=4500, a0=69, beta=0.70, rho=0.00, p_old=0.30, p_new=0.30, lag_med=7,  lag_sig=0.9, q_form=0.75, dup=0.06, mix=(0.50, 0.20, 0.30), ref_mult=1.0, ref_med=45, season_delta=0.10),
 "meta":     dict(s0=6700, a0=130, beta=0.75, rho=0.00, p_old=0.15, p_new=0.22, lag_med=42, lag_sig=0.9, q_form=0.95, dup=0.24, mix=(0.15, 0.15, 0.70), ref_mult=1.3, ref_med=70, season_delta=0.00),
 "lsa":      dict(s0=3000, a0=105, beta=0.40, rho=0.00, p_old=0.42, p_new=0.42, lag_med=2,  lag_sig=0.8, q_form=0.25, dup=0.03, mix=(0.80, 0.15, 0.05), ref_mult=0.9, ref_med=35, season_delta=1.00),
 "retarget": dict(s0=1950, a0=45,  beta=0.45, rho=0.55, p_old=0.22, p_new=0.22, lag_med=10, lag_sig=0.9, q_form=0.85, dup=0.10, mix=(0.35, 0.15, 0.50), ref_mult=1.0, ref_med=45, season_delta=0.00),
}
SEASON_GAMMA = 0.9      # elasticity of attributed persons to the seasonal demand index
ORGANIC_A0 = 130        # organic persons per week at season = 1
# job economics
JT = ["repair", "maint", "install"]
REV_MU = {"repair": 450, "maint": 220, "install": 4200}
REV_SIG = {"repair": 0.45, "maint": 0.30, "install": 0.25}
MAT_FRAC = {"repair": 0.28, "maint": 0.12, "install": 0.46}
LAB_HRS = {"repair": 2.2, "maint": 1.2, "install": 16.0}
REF_P = {"repair": 0.03, "maint": 0.01, "install": 0.09}
LAB_RATE = 48.0
FEE_PCT, FEE_FIX = 0.029, 0.30
def commission(rev):
    return 0.05 * min(rev, 1000) + 0.08 * max(0.0, min(rev, 3000) - 1000) + 0.12 * max(0.0, rev - 3000)
REF_SIG = 0.6

def job_stats(ch, n=400000, seed=1):
    """Monte-Carlo expected economics per WON job for a channel (fully matured)."""
    r = np.random.default_rng(seed); p = P.get(ch) or dict(mix=(0.5, 0.3, 0.2), ref_mult=1.0)
    jt = r.choice(3, size=n, p=p["mix"]); out = np.zeros(n); rev_a = np.zeros(n)
    for k, t in enumerate(JT):
        m = jt == k; nk = m.sum()
        rev = r.lognormal(np.log(REV_MU[t]) - REV_SIG[t] ** 2 / 2, REV_SIG[t], nk)
        mat = rev * MAT_FRAC[t] * r.uniform(0.85, 1.15, nk)
        hrs = r.gamma(6, LAB_HRS[t] / 6, nk)
        com = np.array([commission(x) for x in rev]) if nk < 200000 else (0.05 * np.minimum(rev, 1000) + 0.08 * np.maximum(0, np.minimum(rev, 3000) - 1000) + 0.12 * np.maximum(0, rev - 3000))
        fee = FEE_PCT * rev + FEE_FIX
        refund = (r.random(nk) < REF_P[t] * p["ref_mult"]) * rev * r.uniform(0.3, 1.0, nk)
        out[m] = rev - mat - hrs * LAB_RATE - com - fee - refund; rev_a[m] = rev
    return out.mean(), rev_a.mean()

def truth_table():
    rows = {}
    for c in CH:
        p = P[c]; contrib, rev = job_stats(c)
        u = p["p_new"] * contrib                      # expected matured contribution per attributed person
        mar_attr = p["beta"] * p["a0"] / p["s0"]      # marginal attributed persons per $
        mar_inc = (1 - p["rho"]) * mar_attr
        rows[c] = dict(contrib_per_win=contrib, rev_per_win=rev, u=u, avg_attr_roas=p["a0"] * p["p_new"] * rev / p["s0"],
                       avg_inc_contrib_per_usd=(1 - p["rho"]) * p["a0"] * u / p["s0"], mar_attr_contrib_per_usd=mar_attr * u,
                       mar_inc_contrib_per_usd=mar_inc * u)
    return rows


import math
def lag_cdf(t, med, sig):
    return 0.0 if t <= 0 else 0.5 * (1 + math.erf((math.log(t) - math.log(med)) / (sig * math.sqrt(2))))
def window_completion(c, window_days=91):
    p = P[c]; return float(np.mean([lag_cdf(a + 0.5, p["lag_med"], p["lag_sig"]) for a in range(window_days)]))
def season_bias_beta(c, var_ls_noise=0.0625, var_season=0.04):
    p = P[c]; d = p["season_delta"]; v = d * d * var_season + var_ls_noise
    return p["beta"] + SEASON_GAMMA * d * var_season / v

def variants():
    t = truth_table(); out = {}
    comp = {c: window_completion(c) for c in CH}
    out["TRUTH marginal incremental"] = {c: t[c]["mar_inc_contrib_per_usd"] for c in CH}
    out["naive attributed ROAS (platform view)"] = {c: t[c]["avg_attr_roas"] * comp[c] for c in CH}
    out["no maturity adjustment"] = {c: t[c]["mar_inc_contrib_per_usd"] * comp[c] for c in CH}
    out["no incrementality"] = {c: t[c]["mar_attr_contrib_per_usd"] for c in CH}
    out["average not marginal"] = {c: t[c]["avg_inc_contrib_per_usd"] for c in CH}
    out["no season control"] = {c: t[c]["mar_inc_contrib_per_usd"] * season_bias_beta(c) / P[c]["beta"] for c in CH}
    return out, comp


if __name__ == "__main__":
    t = truth_table()
    v, comp = variants()
    print("completion", {c: round(x, 2) for c, x in comp.items()})
    for k, d in v.items():
        top = max(d, key=d.get); srt = sorted(d.values(), reverse=True)
        print(f"{k:42s} top={top:9s} margin={(srt[0]/srt[1]-1):.0%}", {c: round(x, 2) for c, x in d.items()})
    import json
    for k in ("avg_attr_roas", "mar_attr_contrib_per_usd", "avg_inc_contrib_per_usd", "mar_inc_contrib_per_usd"):
        print(k, {c: round(t[c][k], 3) for c in CH})
    print({c: (round(t[c]["contrib_per_win"]), round(t[c]["u"], 1)) for c in CH})


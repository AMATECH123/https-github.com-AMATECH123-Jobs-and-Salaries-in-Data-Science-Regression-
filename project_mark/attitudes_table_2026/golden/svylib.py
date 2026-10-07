import numpy as np, pandas as pd

def estimate(x, var, codes, weight):
    """Share of respondents with a listed response who gave one of `codes`, in one survey year.
    x: every record of that year. Returns dict(p, n, se_design, se_srs). Missing values are excluded
    from the denominator. Sampling error by Taylor linearisation over the variance strata and PSUs of the
    full year sample (domain estimation), each stratum with its PSUs as sampled."""
    v = x[var]
    insub = v.notna().values
    if insub.sum() == 0:
        return None
    y = np.where(insub, v.isin(codes).astype(float), 0.0)
    w = x[weight].values
    W = w[insub].sum()
    p = (w * y)[insub].sum() / W
    n = int(insub.sum())
    se_srs = float(np.sqrt(p * (1 - p) / n))
    z = np.where(insub, w * (y - p) / W, 0.0)
    t = pd.DataFrame({"h": x["vstrat"].values, "j": x["vpsu"].values, "z": z}).groupby(["h", "j"])["z"].sum().reset_index()
    var_ = 0.0
    for _, g in t.groupby("h"):
        nh = len(g)
        if nh > 1:
            var_ += nh / (nh - 1) * ((g.z - g.z.mean()) ** 2).sum()
    return dict(p=float(p), n=n, se_design=float(np.sqrt(var_)), se_srs=se_srs)

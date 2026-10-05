import itertools
from sweep import *
import sweep
r = evaluate(PR.RATE_EUR_PER_HOUR, 1, 1, 1, PR.CUSTOM_BUILD_HOURS, PR.HOURS)
for k, t in r.items():
    print(f"{k:28s} -> {min(t, key=t.get):7s}", {p: round(v) for p, v in t.items()})

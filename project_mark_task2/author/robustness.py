import subprocess, os, json, sys
res = []
for seed in (11, 22, 33, 44, 55, 66):
    env = dict(os.environ, TASK_SEED=str(seed))
    subprocess.run(["python3", "generate.py"], env=env, capture_output=True, check=True); subprocess.run(["python3", "make_docs.py"], env=env, capture_output=True, check=True)
    r = subprocess.run(["python3", "reference_solution.py"], env=env, capture_output=True, text=True, check=True)
    e = json.load(open("reference_outputs/estimates.json")); t = json.load(open("world_truth.json"))["channels"]
    est = {c: round(e["channels"][c]["marginal_incremental_contribution_per_usd"], 2) for c in e["channels"]}
    tru = {c: round(t[c]["marginal_incremental_contribution_per_usd"], 2) for c in t}
    print(seed, "top", e["top"], "| est", est, "| truth", tru, flush=True)

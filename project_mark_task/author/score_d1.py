import json, sys, io, contextlib, pandas as pd
with contextlib.redirect_stdout(io.StringIO()):
    import reference_solution as R
gt = json.load(open("reference_outputs/ground_truth_checks.json")); tw = R.conf.groupby("workflow_id").business_runs.sum()
t = lambda a,b,tol: abs(a-b)/b <= tol
def score(path):
    d = pd.read_csv(path); sc = {}
    cols = {c.lower(): c for c in d.columns}
    pc = cols.get("platform") or cols.get("source_platform") or cols.get("recording_platform"); dc = [c for c in d.columns if "date" in c.lower()][0]
    mc = [c for c in d.columns if c.lower() in ("month", "billing_month")][0]
    d["_p"] = d[pc].astype(str).str.lower(); d["_d"] = d[dc].astype(str).str[:10]
    sc[1] = 2
    tot = d.business_runs.sum(); sc[2] = 6 if t(tot, gt["total_runs"], .005) else 0
    mt = d.groupby(mc).business_runs.sum(); ok = sum(t(mt.get(m,0), v, .01) for m, v in gt["monthly_totals"].items()); sc[3] = 6 if ok >= 10 else 0
    sc[4] = 3 if t(d[d.workflow_id.isin(gt["migrated_workflows"])].business_runs.sum(), gt["migrated_runs"], .01) else 0
    inc = {("2025-02-11","zapier"): gt["incident_zap_2025-02-11"], ("2024-12-17","make"): gt["incident_make_2024-12-17"],
           ("2025-08-12","zapier"): gt["incident_zap_2025-08-12"], ("2025-03-04","make"): gt["incident_make_2025-03-04"]}
    iok = sum(t(d[(d._d==dd)&(d._p==pp)].business_runs.sum(), v, .03) for (dd, pp), v in inc.items()); sc[5] = 4 if iok >= 3 else 0
    sc[6] = 2 if t(d[d.client_id=="INTERNAL"].business_runs.sum(), gt["internal_runs"], .01) else 0
    ps = d.groupby("_p").business_runs.sum().to_dict()
    zjs = d[(d._p=="zapier") & (d[mc].astype(str) >= "2025-06")].business_runs.sum()
    sc[7] = 3 if t(zjs, gt["zapier_runs_jun_sep_2025"], .01) and all(t(ps.get(k,0), v, .01) for k, v in gt["runs_by_source_platform"].items()) else 0
    rc = d[d.workflow_id.isin(gt["recreated_workflows"])].groupby("workflow_id").business_runs.sum()
    rok = sum(t(rc.get(w,0), tw[w], .02) for w in gt["recreated_workflows"]); sc[8] = 2 if rok == 11 else (1 if rok >= 8 else 0)
    hz = d[d.workflow_id.isin(gt["helpers_to_parent"])].business_runs.sum(); ps_ = set(gt["helpers_to_parent"].values())
    pok = sum(t(d[d.workflow_id==p].business_runs.sum(), tw[p], .01) for p in ps_); sc[9] = 2 if hz == 0 and pok == len(ps_) else (1 if hz == 0 else 0)
    print(path.split("/")[-3], "total", int(tot), "vs", gt["total_runs"], "| months ok", ok, "/12 | platform", ps, "| internal", int(d[d.client_id=="INTERNAL"].business_runs.sum()), "| recreated ok", rok, "| helper runs", int(hz), "| parents ok", pok, "/", len(ps_), "| migrated", int(d[d.workflow_id.isin(gt["migrated_workflows"])].business_runs.sum()), "| incidents ok", iok, "| zapier Jun-Sep", int(zjs), "vs", gt["zapier_runs_jun_sep_2025"])
    return sc
if __name__ == "__main__":
    for p in sys.argv[1:]:
        sc = score(p); print("D1", sum(sc.values()), "/30", sc)

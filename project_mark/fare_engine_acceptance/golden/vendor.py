"""The vendor's engine as delivered: base fare per leg by route class, zone fare by the farther zone, transfer
discounts without time, media or product conditions, cash and every medium accepted everywhere."""
import pandas as pd, re
plan=pd.read_csv('test_plan.csv',dtype=str); routes=pd.read_csv('feed/routes.txt',dtype=str).fillna(''); sa=pd.read_csv('feed/stop_areas.txt',dtype=str)
cls=dict(zip(routes.route_id,routes.route_fare_class)); net=dict(zip(routes.route_id,routes.network_id))
zone={}
for r in sa.itertuples():
    m=re.search(r'zone_(\d+a?)$',r.area_id)
    if m and 'commuter_rail' in r.area_id: zone.setdefault(r.stop_id,set()).add(m.group(1))
zp={'1a':2.40,'1':6.50,'2':7.00,'3':8.00,'4':8.75,'5':9.75,'6':10.50,'7':11.00,'8':12.25,'9':12.75,'10':13.25}
ferry={'ferry_f1f2h':9.75,'ferry_east_boston':2.40,'ferry_f4':2.40,'ferry_f6':6.50,'ferry_f7':6.50,'ferry_f8':6.50,'ferry_f10':2.40,'ferry_lynn':7.00}
def legfare(r):
    c=cls[r.route_id]; n=net[r.route_id]
    if c in ('Local Bus','Free'): return 1.70,'bus'
    if c=='Rapid Transit': return 2.40,'subway'
    if c=='Commuter Rail':
        zs=zone.get(r.board_stop_id,set())|zone.get(r.alight_stop_id,set())
        far=max(zs,key=lambda z: 0 if z=='1a' else int(z)) if zs else '1a'; return zp[far],'cr'
    if c=='Ferry': return ferry.get(n,2.40),'ferry'
    return 2.40,'other'
out=[]
for jid,g in plan.groupby('journey_id',sort=False):
    g=g.sort_values('leg',key=lambda s:s.astype(int)); total=0; prev=None
    for r in g.itertuples():
        f,kind=legfare(r)
        if prev=='bus' and kind=='subway': f=0.70
        elif prev=='subway' and kind=='bus': f=0.0
        elif prev=='bus' and kind=='bus': f=0.0
        elif prev=='subway' and kind=='subway': f=0.0
        total+=f; prev=kind
    out.append(dict(journey_id=jid,vendor_fare=f"{total:.2f}"))
pd.DataFrame(out).to_csv('vendor_results.csv',index=False)
g=pd.read_csv('golden_fares.csv',dtype=str).merge(pd.DataFrame(out),on='journey_id')
g['match']=g.apply(lambda r: r.fare!='' and not pd.isna(r.fare) and abs(float(r.fare)-float(r.vendor_fare))<0.005,axis=1)
print(g[['journey_id','fare_medium','fare','vendor_fare','match']].to_string()); print('mismatches',(~g.match).sum(),'of',len(g))

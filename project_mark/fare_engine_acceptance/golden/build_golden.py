"""Golden build: prices every journey of the acceptance test plan with the Fares v2 engine, compares with the
vendor's results and writes the three deliverables plus figures.json. Run from golden/ after unpacking
../inputs/MBTA_GTFS.zip into golden/feed (see unpack step in README)."""
import os, sys, json, zipfile, pandas as pd, numpy as np
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
HERE=os.path.dirname(os.path.abspath(__file__)); INP=os.path.join(HERE,'..','inputs'); sys.path.insert(0,HERE)
if not os.path.exists(os.path.join(HERE,'feed','fare_leg_rules.txt')):
    zipfile.ZipFile(os.path.join(INP,'MBTA_GTFS.zip')).extractall(os.path.join(HERE,'feed'))
from fare_engine import Feed, sec
F=Feed(os.path.join(HERE,'feed')); D='20261015'
plan=pd.read_csv(os.path.join(INP,'acceptance_test_plan.csv'),dtype=str); vend=pd.read_csv(os.path.join(INP,'vendor_results.csv'),dtype=str).set_index('journey_id').vendor_fare.astype(float)
rows=[]; FIG={}
for jid,g in plan.groupby('journey_id',sort=False):
    g=g.sort_values('leg',key=lambda s:s.astype(int)); media=g.fare_medium.iloc[0]
    legs=[dict(route=r.route_id,from_stop=r.board_stop_id,to_stop=r.alight_stop_id,dep=sec(r.scheduled_departure),arr=sec(r.scheduled_arrival)) for r in g.itertuples()]
    tot,det=F.price(legs,media,D)
    # products per leg in leg order (a transfer entry means the leg is covered by the from-leg product)
    prods=[]
    if det:
        for d in det: prods.append(d[4] if d[3]=='leg' else f"covered by transfer ({d[4]})")
    v=vend[jid]
    rows.append(dict(journey_id=jid,description=g.description.iloc[0],fare_medium=media,legs=len(legs),certified_fare=('no fare on this medium' if tot is None else f"{tot:.2f}"),
                     products_by_leg=' | '.join(prods) if prods else 'none on this medium',vendor_fare=f"{v:.2f}",difference=('n/a' if tot is None else f"{v-tot:+.2f}"),vendor_matches=('No' if tot is None or abs(v-tot)>0.005 else 'Yes'),tot_=tot,v_=v,
                     legs_=legs))
T=pd.DataFrame(rows)
mis=T[T.vendor_matches=='No']; FIG['journeys']=len(T); FIG['mispriced']=len(mis); FIG['verdict']='fails acceptance'
priced=mis[mis.tot_.notna()]; FIG['net_difference']=round(float((priced.v_-priced.tot_).sum()),2); FIG['over']=round(float((priced.v_-priced.tot_).clip(lower=0).sum()),2); FIG['under']=round(float((priced.v_-priced.tot_).clip(upper=0).sum()),2)
FIG['no_fare_journeys']=T[T.tot_.isna()].journey_id.tolist()
big=priced.loc[(priced.v_-priced.tot_).abs().idxmax()]; FIG['largest_error']={'journey':big.journey_id,'certified':big.tot_,'vendor':big.v_,'error':round(big.v_-big.tot_,2)}
# the ninety minute window journey
chg=[]
for r in T.itertuples():
    if r.tot_ is None or np.isnan(r.tot_): continue
    F.tr.loc[F.tr.duration_limit=='7200','duration_limit']='5400'
    t2,_=F.price(r.legs_,r.fare_medium,D)
    F.tr.loc[F.tr.duration_limit=='5400','duration_limit']='7200'
    if t2 is None or abs(t2-r.tot_)>0.005: chg.append((r.journey_id,r.tot_,t2))
FIG['ninety_minute_changes']=chg
# groups
groups={'cash or medium not valid for a leg (no fare on the medium)':T[T.tot_.isna()].journey_id.tolist(),
        'CharlieTicket priced as a local bus fare':[j for j in ['J03'] if j in mis.journey_id.values],
        'transfer applied outside the two hour window or beyond the allowed count':[j for j in ['J13','J16','J38'] if j in mis.journey_id.values],
        'transfer discount given to a medium or product that has none':[j for j in ['J11','J15'] if j in mis.journey_id.values],
        'free Silver Line from the airport terminals charged':[j for j in ['J20','J21'] if j in mis.journey_id.values],
        'commuter rail interzone fare priced as a zone fare from Boston':[j for j in ['J27','J28'] if j in mis.journey_id.values]}
FIG['groups']=groups; assert sorted(sum(groups.values(),[]))==sorted(mis.journey_id.tolist()), (sorted(sum(groups.values(),[])), sorted(mis.journey_id.tolist()))
out=T[['journey_id','description','fare_medium','legs','certified_fare','products_by_leg','vendor_fare','difference','vendor_matches']]
out.to_csv(os.path.join(HERE,'journey_fares.csv'),index=False)
# chart
fig,ax=plt.subplots(figsize=(11,7))
x=np.arange(len(T)); cert=np.array([0 if (t is None or np.isnan(t)) else t for t in T.tot_]); v=T.v_.values; m=(T.vendor_matches=='No').values; nofare=T.tot_.isna().values
ax.bar(x-0.2,cert,0.4,color=np.where(nofare,'#dddddd','#1f5f8b'),label='certified fare (grey: no fare on the medium)')
ax.bar(x+0.2,v,0.4,color=np.where(m,'#b2182b','#9ecae1'),label='vendor fare (red: mismatch)')
for i in np.where(nofare)[0]: ax.text(i-0.2,0.15,'no\nfare',ha='center',fontsize=7,color='#4d4d4d')
ax.set_xticks(x); ax.set_xticklabels(T.journey_id,rotation=90,fontsize=8); ax.set_ylabel('US dollars')
ax.set_title(f"Fare engine acceptance: FAILS. {FIG['mispriced']} of {FIG['journeys']} journeys mispriced; vendor net {FIG['net_difference']:+.2f} USD across the plan",fontsize=12)
ax.legend(loc='upper left'); ax.grid(axis='y',alpha=0.3); plt.tight_layout(); fig.savefig(os.path.join(HERE,'fare_differences.png'),dpi=150,bbox_inches='tight'); plt.close(fig)
# memo
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
ss=getSampleStyleSheet(); body=ss['BodyText']; body.fontSize=9; body.leading=12; h=ss['Heading2']; h.fontSize=11
P=lambda t: Paragraph(t,body)
doc=SimpleDocTemplate(os.path.join(HERE,'acceptance_memo.pdf'),pagesize=letter,leftMargin=50,rightMargin=50,topMargin=46,bottomMargin=46)
L=[Paragraph('Fare engine acceptance: memo',ss['Title'])]
L.append(P(f"<b>Verdict: the engine fails acceptance.</b> It priced {FIG['mispriced']} of the {FIG['journeys']} journeys in the plan wrongly. Across the plan its prices come to {FIG['net_difference']:+.2f} USD against the certified fares of the journeys that have a fare ({FIG['over']:+.2f} overcharged, {FIG['under']:+.2f} undercharged), and it returned a price for {len(FIG['no_fare_journeys'])} journeys that have no fare on their medium at all."))
L.append(Paragraph('What the vendor got wrong, by rule',h))
expl={'cash or medium not valid for a leg (no fare on the medium)':'the engine prices every leg on every medium. Under the feed, cash has no product at a subway fare gate (the cash rule for rapid transit is transfer only, so it can never start a journey), the mTicket app has no bus or subway product, and the CharlieCard and contactless products do not exist for commuter rail. Each of these journeys has no fare on its medium and the engine must say so.',
      'CharlieTicket priced as a local bus fare':'the only product a CharlieTicket holds for a local bus leg is the subway quick ticket at 2.40, not the 1.70 bus fare.',
      'transfer applied outside the two hour window or beyond the allowed count':'the bus to bus rule allows one transfer within two hours of the first departure, measured departure to departure; the subway to bus rule allows one; a third bus, or a bus boarded more than two hours after the first departure, is a new fare.',
      'transfer discount given to a medium or product that has none':'cash carries no transfer rules between buses or onto the subway, and the quick ticket product has no transfer onto the subway from a bus.',
      'free Silver Line from the airport terminals charged':'the SL1 leg from the airport terminals is a free fare product and its transfer to the Red Line at South Station is free as well.',
      'commuter rail interzone fare priced as a zone fare from Boston':'a journey between two stations outside Zone 1A is priced by the interzone product for the number of zones crossed, not by the zone fare from Boston.'}
for gname,js in groups.items():
    if js: L.append(P(f"<b>{gname.capitalize()}</b> ({', '.join(js)}): {expl[gname]}"))
L.append(Paragraph('Largest error and the window',h))
le=FIG['largest_error']; L.append(P(f"The largest error in dollars is {le['journey']}: certified {le['certified']:.2f}, vendor {le['vendor']:.2f}, {le['error']:+.2f}."))
if chg:
    j,t1,t2=chg[0]; L.append(P(f"If the transfer window were cut to ninety minutes, exactly one journey's correct fare would change: {j}, from {t1:.2f} to {t2:.2f}, because its second leg departs {int((T[T.journey_id==j].legs_.iloc[0][1]['dep']-T[T.journey_id==j].legs_.iloc[0][0]['dep'])/60)} minutes after the first and so falls inside two hours but outside ninety minutes. Every other transfer in the plan is made within 45 minutes or already falls outside two hours."))
L.append(Spacer(1,4))
tab=[['Journey','Medium','Legs','Certified','Vendor','Match']]+[[r.journey_id,r.fare_medium,r.legs,r.certified_fare,r.vendor_fare,r.vendor_matches] for r in out.itertuples()]
t=Table(tab,colWidths=[50,120,35,130,50,40],repeatRows=1); t.setStyle(TableStyle([('FONTSIZE',(0,0),(-1,-1),7),('GRID',(0,0),(-1,-1),0.3,colors.grey),('BACKGROUND',(0,0),(-1,0),colors.lightgrey)]))
L.append(t); doc.build(L)
json.dump(FIG,open(os.path.join(HERE,'figures.json'),'w'),indent=1,default=str); print(json.dumps(FIG,indent=1,default=str))

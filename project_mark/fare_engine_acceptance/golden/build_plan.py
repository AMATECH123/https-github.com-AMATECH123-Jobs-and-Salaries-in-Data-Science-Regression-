import sys, pandas as pd, numpy as np
sys.path.insert(0,'.')
from fare_engine import Feed, sec; from trips import Trips
F=Feed('feed'); T=Trips('feed'); D='20261015'
def J(specs, after='09:00:00'):
    legs=[]; t=after
    for spec in specs:
        route,a,b=spec[:3]; gap=spec[3] if len(spec)>3 else None
        if gap: t=f"{(sec(t)+gap)//3600:02d}:{((sec(t)+gap)%3600)//60:02d}:00"
        l=T.find(route,a,b,D,after=t)
        if not l: raise SystemExit(f'NOT FOUND {spec} after {t}')
        legs.append(l); t=l['arr_t']
    return legs
plan=[
 ("J01","CharlieCard, one bus",'charliecard',[('1','Nubian','Holyoke')]),
 ("J02","Cash, one bus",'cash',[('1','Nubian','Holyoke')]),
 ("J03","CharlieTicket on a bus",'charlieticket',[('66','Nubian','Fenwood')]),
 ("J04","mTicket on a bus",'mticket',[('66','Nubian','Fenwood')]),
 ("J05","Contactless, subway",'contactless_credit_debit',[('Red','place-alfcl','place-sstat')]),
 ("J06","Cash at a subway fare gate",'cash',[('Red','place-alfcl','place-sstat')]),
 ("J07","Cash boarding a surface Green Line stop",'cash',[('Green-B','place-lake','place-pktrm')]),
 ("J08","Cash boarding Green Line underground",'cash',[('Green-B','place-pktrm','place-lake')]),
 ("J09","CharlieCard bus then subway within window",'charliecard',[('39','Myrtle','Forest Hills'),('Orange','place-forhl','place-dwnxg')]),
 ("J10","Cash bus then subway",'cash',[('39','Myrtle','Forest Hills'),('Orange','place-forhl','place-dwnxg')]),
 ("J11","CharlieTicket bus then subway",'charlieticket',[('39','Myrtle','Forest Hills'),('Orange','place-forhl','place-dwnxg')]),
 ("J12","CharlieCard subway then bus",'charliecard',[('Orange','place-dwnxg','place-forhl'),('39','Forest Hills','Perkins')]),
 ("J13","CharlieCard subway then bus after the window",'charliecard',[('Orange','place-dwnxg','place-forhl'),('39','Forest Hills','Perkins',8100)]),
 ("J14","CharlieCard bus then bus",'charliecard',[('66','Nubian','Fenwood'),('39','Fenwood','Forest Hills')]),
 ("J15","Cash bus then bus",'cash',[('66','Nubian','Fenwood'),('39','Fenwood','Forest Hills')]),
 ("J16","CharlieCard three buses",'charliecard',[('66','Nubian','Fenwood'),('39','Fenwood','Forest Hills'),('32','Forest Hills','Cummins')]),
 ("J17","CharlieCard bus, subway, bus",'charliecard',[('39','Myrtle','Forest Hills'),('Orange','place-forhl','place-rugg'),('15','Ruggles','Nubian')]),
 ("J18","CharlieCard subway then subway",'charliecard',[('Orange','place-forhl','place-dwnxg'),('Red','place-dwnxg','place-alfcl')]),
 ("J19","Contactless bus then subway just inside the window",'contactless_credit_debit',[('39','Myrtle','Forest Hills'),('Orange','place-forhl','place-dwnxg',6000)]),
 ("J20","Cash SL1 from Terminal A",'cash',[('741','17091','place-sstat')]),
 ("J21","CharlieCard SL1 from Terminal A then Red Line",'charliecard',[('741','17091','place-sstat'),('Red','place-sstat','place-alfcl')]),
 ("J22","CharlieCard SL1 toward the airport",'charliecard',[('741','place-sstat','17091')]),
 ("J23","CharlieCard Blue Line from Airport",'charliecard',[('Blue','place-aport','place-gover')]),
 ("J24","CharlieCard SL3 Chelsea to South Station",'charliecard',[('743','place-chels','place-sstat')]),
 ("J25","Cash Mattapan trolley",'cash',[('Mattapan','place-asmnl','place-matt')]),
 ("J26","mTicket North Station to Salem",'mticket',[('CR-Newburyport','place-north','place-ER-0168')]),
 ("J27","Cash Lynn to Salem",'cash',[('CR-Newburyport','place-ER-0117','place-ER-0168')]),
 ("J28","mTicket Beverly to Newburyport",'mticket',[('CR-Newburyport','place-ER-0183','place-ER-0362')]),
 ("J29","mTicket Four Corners to South Station",'mticket',[('CR-Fairmount','place-DB-2249','place-sstat')]),
 ("J30","mTicket Readville to South Station",'mticket',[('CR-Fairmount','place-DB-0095','place-sstat')]),
 ("J31","CharlieCard North Station to Chelsea",'charliecard',[('CR-Newburyport','place-north','place-chels')]),
 ("J32","Contactless North Station to Chelsea",'contactless_credit_debit',[('CR-Newburyport','place-north','place-chels')]),
 ("J33","mTicket Porter to Waltham",'mticket',[('CR-Fitchburg','place-portr','place-FR-0098')]),
 ("J34","Cash Hingham ferry to Long Wharf",'cash',[('Boat-F1','Hingham','Rowes')]),
 ("J35","Cash East Boston ferry",'cash',[('Boat-EastBoston','Lewis','Long Wharf')]),
 ("J36","Contactless Winthrop ferry to Boston",'contactless_credit_debit',[('Boat-F6','Winthrop','Central Wharf')]),
 ("J37","mTicket Hingham ferry then Blue Line",'mticket',[('Boat-F1','Hingham','Rowes'),('Blue','place-aqucl','place-aport')]),
 ("J38","Contactless subway, bus, bus",'contactless_credit_debit',[('Orange','place-dwnxg','place-forhl'),('39','Forest Hills','Perkins'),('39','Perkins','Forest Hills')]),
]
rows=[]; gold=[]
for jid,desc,media,specs in plan:
    try: legs=J(specs)
    except SystemExit as e: print(jid, e); continue
    tot,det=F.price(legs,media,D)
    for i,l in enumerate(legs,1):
        rows.append(dict(journey_id=jid,description=desc,fare_medium=media,leg=i,route_id=l['route'],trip_id=l['trip'],board_stop_id=l['from_stop'],board_stop=T.name[l['from_stop']],scheduled_departure=l['dep_t'],alight_stop_id=l['to_stop'],alight_stop=T.name[l['to_stop']],scheduled_arrival=l['arr_t']))
    gold.append(dict(journey_id=jid,description=desc,fare_medium=media,legs=len(legs),fare=tot,detail=str([(d[1],d[3],d[4],d[5]) for d in (det or [])])))
    print(jid, desc, media, '->', tot)
pd.DataFrame(rows).to_csv('test_plan.csv',index=False); pd.DataFrame(gold).to_csv('golden_fares.csv',index=False)
print(len(gold),'journeys')

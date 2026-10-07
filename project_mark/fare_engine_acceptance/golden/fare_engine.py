"""GTFS Fares v2 engine following the specification's empty entry semantics, with the MBTA extensions
(transfer_only, filter_fare_product_id, fare_media_behavior, fare_product_behavior)."""
import pandas as pd, itertools, functools
from collections import defaultdict

def sec(x):
    h, m, s = x.split(':'); return int(h) * 3600 + int(m) * 60 + int(s)

class Feed:
    def __init__(self, d):
        rd = lambda f, **k: pd.read_csv(f"{d}/{f}.txt", dtype=str, **k).fillna('')
        self.routes = rd('routes'); self.stops = rd('stops'); self.lr = rd('fare_leg_rules'); self.tr = rd('fare_transfer_rules')
        self.fp = rd('fare_products'); self.sa = rd('stop_areas'); self.tf = rd('timeframes'); self.jr = rd('fare_leg_join_rules')
        self.cal = rd('calendar'); self.cald = rd('calendar_dates')
        self.net = dict(zip(self.routes.route_id, self.routes.network_id))
        self.stop_areas = defaultdict(set)
        for r in self.sa.itertuples(): self.stop_areas[r.stop_id].add(r.area_id)
        parent = dict(zip(self.stops.stop_id, self.stops.parent_station))
        for s, p in parent.items():
            if p and p in self.stop_areas and s not in self.stop_areas: self.stop_areas[s] = set(self.stop_areas[p])
        self.listed_net = set(self.lr.network_id) - {''}; self.listed_from = set(self.lr.from_area_id) - {''}; self.listed_to = set(self.lr.to_area_id) - {''}
        self.listed_tfrom = set(self.tr.from_leg_group_id) - {''}; self.listed_tto = set(self.tr.to_leg_group_id) - {''}
        self.products = defaultdict(dict)  # product -> media -> amount
        for r in self.fp.itertuples(): self.products[r.fare_product_id][r.fare_media_id] = float(r.amount)
        self.lr['tonly'] = self.lr.transfer_only == '1'
        self.sid_dates = {}
    def service_active(self, sid, date):
        c = self.cal[self.cal.service_id == sid]
        dow = ['monday','tuesday','wednesday','thursday','friday','saturday','sunday'][pd.Timestamp(date).dayofweek]
        ok = False
        for r in c.itertuples():
            if r.start_date <= date <= r.end_date and getattr(r, dow) == '1': ok = True
        for r in self.cald[(self.cald.service_id == sid) & (self.cald.date == date)].itertuples():
            ok = r.exception_type == '1'
        return ok
    def timeframe_ok(self, group, date, t):
        if group == '': return True
        tod = t % 86400; day = date if t < 86400 else (pd.Timestamp(date) + pd.Timedelta(days=t // 86400)).strftime('%Y%m%d')
        for r in self.tf[self.tf.timeframe_group_id == group].itertuples():
            st = sec(r.start_time) if r.start_time else 0; en = sec(r.end_time) if r.end_time else 86400
            if self.service_active(r.service_id, day) and st <= tod < en: return True
        return False
    def amount(self, product, media):
        pm = self.products.get(product, {})
        if media in pm: return pm[media]
        if '' in pm: return pm['']
        return None
    def leg_rules(self, leg, date, as_transfer):
        """All leg rule records matching a leg (dict with network, from_stop, to_stop, dep, arr)."""
        fa = self.stop_areas.get(leg['from_stop'], set()); ta = self.stop_areas.get(leg['to_stop'], set())
        out = []
        for r in self.lr.itertuples():
            if r.tonly and not as_transfer: continue
            # network
            if r.network_id: 
                if r.network_id != leg['network']: continue
            elif leg['network'] in self.listed_net: continue
            if r.from_area_id:
                if r.from_area_id not in fa: continue
            elif fa & self.listed_from: continue
            if r.to_area_id:
                if r.to_area_id not in ta: continue
            elif ta & self.listed_to: continue
            if not self.timeframe_ok(r.from_timeframe_group_id, date, leg['dep']): continue
            if not self.timeframe_ok(r.to_timeframe_group_id, date, leg['arr']): continue
            out.append(r)
        # spec step 2 then 3: exact matches (all three characteristic fields specified) take precedence over empty entries
        exact = [r for r in out if r.network_id and r.from_area_id and r.to_area_id]
        return exact if exact else out
    def transfer_rules(self, g1, g2):
        ex = self.tr[(self.tr.from_leg_group_id == g1) & (self.tr.to_leg_group_id == g2)]
        if len(ex): return list(ex.itertuples())
        out = []
        for r in self.tr.itertuples():
            if r.from_leg_group_id:
                if r.from_leg_group_id != g1: continue
            elif g1 in self.listed_tfrom: continue
            if r.to_leg_group_id:
                if r.to_leg_group_id != g2: continue
            elif g2 in self.listed_tto: continue
            out.append(r)
        return out
    def price(self, legs, media, date):
        """legs: list of dicts (route, from_stop, to_stop, dep, arr). Returns (total or None, detail list) for the
        cheapest valid combination of products and transfers under the medium."""
        legs = [dict(l, network=self.net[l['route']]) for l in legs]
        # join rules: merge consecutive legs matching a join rule into one effective leg
        eff = []; i = 0
        while i < len(legs):
            cur = dict(legs[i]); j = i
            while j + 1 < len(legs):
                a, b = legs[j], legs[j + 1]
                m = self.jr[(self.jr.from_network_id == a['network']) & (self.jr.to_network_id == b['network'])]
                ok = False
                for r in m.itertuples():
                    if r.from_stop_id or r.to_stop_id:
                        if r.from_stop_id == a['to_stop'] and r.to_stop_id == b['from_stop']: ok = True
                    elif a['to_stop'] == b['from_stop'] or self.stops.set_index('stop_id').parent_station.get(a['to_stop'], 'x') == self.stops.set_index('stop_id').parent_station.get(b['from_stop'], 'y'): ok = True
                if ok and a['network'] == b['network']:
                    cur['to_stop'] = b['to_stop']; cur['arr'] = b['arr']; cur['joined'] = cur.get('joined', [a.get('route')]) + [b['route']]; j += 1
                else: break
            eff.append(cur); i = j + 1
        best = (None, None)
        def options(k, as_transfer):
            rules = self.leg_rules(eff[k], date, as_transfer)
            opts = []
            for r in rules:
                amt = self.amount(r.fare_product_id, media)
                if amt is None: continue
                opts.append((r.leg_group_id, r.fare_product_id, amt, r.tonly))
            return opts
        def rec(k, prev, total, detail, chain):
            nonlocal best
            # prev: (group, product) of previous effective leg, chain: (rule_key, count, chain_start_dep, chain_start_arr)
            if k == len(eff):
                if best[0] is None or total < best[0]: best = (total, detail)
                return
            leg = eff[k]
            cand = options(k, as_transfer=prev is not None)
            if not cand: return
            for g, p, amt, tonly in cand:
                applied = False
                if prev is not None:
                    for tr in self.transfer_rules(prev[0], g):
                        # media behaviour: same media always true here; product behaviour / filter
                        if tr.filter_fare_product_id and tr.filter_fare_product_id != prev[1]: continue
                        if tr.fare_product_behavior == '1' and tr.filter_fare_product_id and p != tr.filter_fare_product_id and tr.filter_fare_product_id not in self.products: continue
                        key = (tr.from_leg_group_id, tr.to_leg_group_id, tr.fare_product_id)
                        count = chain[1] + 1 if chain and chain[0] == key else 1
                        tc = tr.transfer_count
                        if tc not in ('', '-1') and count > int(tc): continue
                        if tc == '' and chain and chain[0] == key: continue
                        start_dep, start_arr = (chain[2], chain[3]) if chain and chain[0] == key else (eff[k - 1]['dep'], eff[k - 1]['arr'])
                        if tr.duration_limit:
                            lim = int(tr.duration_limit); t = tr.duration_limit_type
                            span = {'0': leg['arr'] - start_dep, '1': leg['dep'] - start_dep, '2': leg['dep'] - start_arr, '3': leg['arr'] - start_arr}[t]
                            if span > lim: continue
                        tamt = self.amount(tr.fare_product_id, media) if tr.fare_product_id else 0.0
                        if tamt is None: continue
                        applied = True
                        # fare_transfer_type 0: S + AB; the to-leg keeps the from-leg's product when behaviour 1
                        newp = tr.filter_fare_product_id if (tr.fare_product_behavior == '1' and tr.filter_fare_product_id) else p
                        rec(k + 1, (g, newp), round(total + tamt, 2), detail + [(k, g, p, 'transfer', tr.fare_product_id or 'none', tamt)], (key, count, start_dep, start_arr))
                if tonly: continue  # transfer only rules need a transfer
                rec(k + 1, (g, p), round(total + amt, 2), detail + [(k, g, p, 'leg', p, amt)], None)
        rec(0, None, 0.0, [], None)
        return best

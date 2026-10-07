import pandas as pd
from fare_engine import sec
class Trips:
    def __init__(self, d):
        self.trips = pd.read_csv(f'{d}/trips.txt', dtype=str).fillna('')
        st = pd.read_csv(f'{d}/stop_times.txt', dtype=str, usecols=['trip_id','arrival_time','departure_time','stop_id','stop_sequence']).fillna('')
        st['seq'] = st.stop_sequence.astype(int); self.st = st
        self.stops = pd.read_csv(f'{d}/stops.txt', dtype=str).fillna('')
        self.cal = pd.read_csv(f'{d}/calendar.txt', dtype=str); self.cald = pd.read_csv(f'{d}/calendar_dates.txt', dtype=str)
        self.parent = dict(zip(self.stops.stop_id, self.stops.parent_station)); self.name = dict(zip(self.stops.stop_id, self.stops.stop_name))
    def services(self, date):
        dow = ['monday','tuesday','wednesday','thursday','friday','saturday','sunday'][pd.Timestamp(date).dayofweek]
        s = set(self.cal[(self.cal.start_date <= date) & (self.cal.end_date >= date) & (self.cal[dow] == '1')].service_id)
        for r in self.cald[self.cald.date == date].itertuples():
            if r.exception_type == '1': s.add(r.service_id)
            else: s.discard(r.service_id)
        return s
    def find(self, route, from_place, to_place, date, after='09:00:00', direction=None):
        """first trip of route on date departing from_place (stop id or parent station) after the time, that later serves to_place"""
        svc = self.services(date)
        t = self.trips[(self.trips.route_id == route) & (self.trips.service_id.isin(svc))]
        if direction is not None: t = t[t.direction_id == str(direction)]
        st = self.st[self.st.trip_id.isin(t.trip_id)].copy()
        def match(sid, place): return sid == place or self.parent.get(sid, '') == place or (not place.startswith('place-') and not place.isdigit() and place in self.name.get(sid, ''))
        best = None
        for tid, g in st.groupby('trip_id'):
            g = g.sort_values('seq')
            a = g[g.stop_id.map(lambda s: match(s, from_place))]; 
            if a.empty: continue
            a = a.iloc[0]
            if sec(a.departure_time) < sec(after): continue
            b = g[(g.seq > a.seq) & g.stop_id.map(lambda s: match(s, to_place))]
            if b.empty: continue
            b = b.iloc[0]
            if best is None or sec(a.departure_time) < best['dep']:
                best = dict(route=route, trip=tid, from_stop=a.stop_id, to_stop=b.stop_id, dep=sec(a.departure_time), arr=sec(b.arrival_time), dep_t=a.departure_time, arr_t=b.arrival_time)
        return best

"""Builds the three golden deliverables for version 5 from the shipped input package.

Count: the latest season (Fall 2024) of the MBTA Commuter Rail ridership count by trip, season, line and stop.
Schedule: the weekday Commuter Rail schedule in effect on most Monday to Friday dates of the Fall 2026 rating
(28 September to 11 December 2026), taken by date from MBTA_GTFS.zip.
Control: the Fall 2024 archived feed (20241014.zip) shows the count's train numbers and departures were valid in
Fall 2024 and were reassigned by Fall 2026; the Spring 2018 count reproduces the previous certification.
Every figure printed or written here is asserted stable under the determinism checks below.
"""
import csv, io, os, json, zipfile, collections, datetime as dt, struct

HERE = os.path.dirname(os.path.abspath(__file__))
INPUTS = os.path.join(HERE, '..', 'inputs')
COUNT = 'MBTA_Commuter_Rail_Ridership_by_Trip2C_Season2C_Route_Line2C_and_Stop..'
RATING_START, RATING_END = dt.date(2026, 9, 28), dt.date(2026, 12, 11)
TOLERANCE = 10  # minutes, convention rule 5
FINANCE_TRAIN, FINANCE_LOAD = '827', 896
PLANNING_TRAIN, PLANNING_FIGURE = '723', 1036
CONTROL = ('CR-Worcester', '508', '1', 1384, 'West Natick')
# Count station names that the feed spells differently (convention rule 6). Verified below against both feeds:
# the 2024 feed carries 'Dedham Corp Center' as a child stop of place-FB-0118 and 'Lynn' and 'Middleborough/Lakeville' as
# stations; the 2026 feed spells them 'Dedham Corporate Center', keeps 'Lynn' as an unserved station, and has
# no Middleborough/Lakeville station at all (the new 'Middleborough' station is a different stop id).
RENAMES = {'Littleton/Rte 495': 'Littleton/Route 495', 'Dedham Corp Center': 'Dedham Corporate Center',
           'Porter Square': 'Porter', 'Lynn': 'Lynn', 'Middleborough/Lakeville': None}


def table(z, name):
    with z.open(name) as f:
        return list(csv.DictReader(io.TextIOWrapper(f, encoding='utf-8-sig')))


def mins(t):
    h, m, s = t.split(':')
    return int(h) * 60 + int(m) + int(s) / 60


def hhmm(m):
    m = int(round(m))
    return f"{(m // 60) % 24:02d}:{m % 60:02d}"


def clock_gap(a, b):
    d = abs(a - b) % 1440
    return min(d, 1440 - d)


# ---------------------------------------------------------------- the count
def load_count():
    rows = list(csv.DictReader(open(os.path.join(INPUTS, COUNT + 'csv'), encoding='utf-8-sig')))
    for r in rows:
        for k in ('average_ons', 'average_offs', 'average_load'):
            r[k] = int(r[k])
    # determinism: the four export formats hold the same rows
    geo = [f['properties'] for f in json.load(open(os.path.join(INPUTS, COUNT + 'geojson')))['features']]
    assert len(geo) == len(rows) == 15761
    for a, b in zip(rows, geo):
        assert all(str(b[k]) == a[k] if k not in ('average_ons', 'average_offs', 'average_load') else b[k] == a[k] for k in b)
    with zipfile.ZipFile(os.path.join(INPUTS, COUNT + 'zip')) as z:
        dbf = [n for n in z.namelist() if n.endswith('.dbf')][0]
        hdr = z.open(dbf).read(8)
        assert struct.unpack('<I', hdr[4:8])[0] == len(rows)
    kml = open(os.path.join(INPUTS, COUNT + 'kml'), encoding='utf-8').read()
    assert kml.count('<Placemark>') == len(rows)
    return rows


def seqkey(r):
    return int(r['stopsequence']) if r['stopsequence'].isdigit() else 10 ** 6


def clock(stop_time):
    """Clock minutes of a count stop_time ('1/1/2024 17:40'); None when the row carries no time."""
    if ' ' not in stop_time:
        return None
    h, m = stop_time.split(' ')[1].split(':')[:2]
    return int(h) * 60 + int(m)


def trains(rows, season):
    by = collections.defaultdict(list)
    for r in rows:
        if r['season'] == season:
            by[(r['route_id'], r['train'], r['direction_id'])].append(r)
    out = {}
    for k, rs in by.items():
        rs.sort(key=seqkey)
        peak = max(rs, key=lambda r: r['average_load'])  # first occurrence wins a tie
        out[k] = dict(rows=rs, line=k[0], train=k[1], direction=k[2], first=rs[0]['stop_id'],
                      departure=clock(rs[0]['stop_time']), last=rs[-1]['stop_id'],
                      peak=peak['average_load'], peak_stop=peak['stop_id'], peak_time=clock(peak['stop_time']),
                      boardings=sum(r['average_ons'] for r in rs), alightings=sum(r['average_offs'] for r in rs))
    return out


# ---------------------------------------------------------------- the schedule
def load_feed(path):
    z = zipfile.ZipFile(path)
    d = dict(zip=z, routes={r['route_id']: r for r in table(z, 'routes.txt')}, calendar=table(z, 'calendar.txt'),
             cal_dates=collections.defaultdict(list), trips=table(z, 'trips.txt'),
             stops={r['stop_id']: r for r in table(z, 'stops.txt')})
    for r in table(z, 'calendar_dates.txt'):
        d['cal_dates'][r['date']].append((r['service_id'], r['exception_type']))
    d['cr'] = {k for k, v in d['routes'].items() if v['route_fare_class'] == 'Commuter Rail'}
    return d


def active_services(d, date):
    ds = date.strftime('%Y%m%d')
    dow = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'][date.weekday()]
    s = {r['service_id'] for r in d['calendar'] if r['start_date'] <= ds <= r['end_date'] and r[dow] == '1'}
    for sid, et in d['cal_dates'].get(ds, []):
        (s.add if et == '1' else s.discard)(sid)
    return s


def station(d, stop_id):
    s = d['stops'][stop_id]
    return d['stops'][s['parent_station']]['stop_name'] if s['parent_station'] else s['stop_name']


def rating_schedule(d, start, end):
    """The set of Commuter Rail trips run on the greatest number of Monday to Friday dates in [start, end]."""
    tally = collections.Counter()
    day = start
    while day <= end:
        if day.weekday() < 5:
            s = active_services(d, day)
            tally[frozenset(t['trip_id'] for t in d['trips'] if t['service_id'] in s and t['route_id'] in d['cr'])] += 1
        day += dt.timedelta(days=1)
    (trip_ids, days), = tally.most_common(1)
    return trip_ids, days, sum(tally.values())


def schedule_trains(d, trip_ids):
    tr = {t['trip_id']: t for t in d['trips'] if t['trip_id'] in trip_ids}
    st = collections.defaultdict(list)
    with d['zip'].open('stop_times.txt') as f:
        for r in csv.DictReader(io.TextIOWrapper(f, encoding='utf-8-sig')):
            if r['trip_id'] in tr:
                st[r['trip_id']].append(r)
    out = {}
    for tid, t in tr.items():
        s = sorted(st[tid], key=lambda r: int(r['stop_sequence']))
        out[tid] = dict(line=t['route_id'], train=t['trip_short_name'], direction=t['direction_id'],
                        first=station(d, s[0]['stop_id']), departure=mins(s[0]['departure_time']),
                        last=station(d, s[-1]['stop_id']), arrival=mins(s[-1]['arrival_time']),
                        stops=[station(d, r['stop_id']) for r in s], service=t['service_id'])
    return out


def resolve(name, feed_names):
    """Count station name to feed station name (convention rule 6)."""
    if name in feed_names and name not in RENAMES:
        return name
    assert name in RENAMES, name
    return RENAMES[name]


def operate(counted, sched, tolerance=TOLERANCE):
    """Convention rule 5: the scheduled train operating a counted train, or None."""
    idx = collections.defaultdict(list)
    for tid, s in sched.items():
        idx[(s['line'], s['direction'], s['first'])].append((s['departure'] % 1440, s['train'], tid))
    feed_names = {s['first'] for s in sched.values()} | {n for s in sched.values() for n in s['stops']}
    result = {}
    for k, c in counted.items():
        origin = resolve(c['first'], feed_names)
        cands = idx.get((c['line'], c['direction'], origin), []) if origin and c['departure'] is not None else []
        best = None
        for dep, train, tid in cands:
            gap = clock_gap(dep, c['departure'])
            if gap <= tolerance and (best is None or (gap, dep) < (best[0], best[1])):
                best = (gap, dep, train, tid)
        result[k] = best
    return result


def main():
    rows = load_count()
    seasons = sorted({r['season'] for r in rows}, key=lambda s: int(s.split()[1]))
    latest = seasons[-1]
    assert latest == 'Fall 2024'
    counted = trains(rows, latest)
    assert len(counted) == 514 and all(seqkey(c['rows'][0]) == 1 for c in counted.values())

    fall = load_feed(os.path.join(INPUTS, 'MBTA_GTFS.zip'))
    trip_ids, days, weekdays = rating_schedule(fall, RATING_START, RATING_END)
    sched = schedule_trains(fall, trip_ids)
    assert len(sched) == 547 and days >= 50, (len(sched), days, weekdays)
    old = load_feed(os.path.join(INPUTS, '20241014.zip'))
    lines = dict(old['routes']); lines.update(fall['routes'])  # Middleborough/Lakeville exists only in the 2024 feed
    assert 'CR-Middleborough' not in fall['routes'] and 'CR-NewBedford' not in old['routes']
    name = lambda l: lines[l]['route_long_name']
    order = lambda l: int(lines[l]['route_sort_order'])

    # ---- rule 6 check: every count station resolves to a feed station or is documented as gone
    feed_names = {n for s in sched.values() for n in s['stops']}
    count_names = {r['stop_id'] for c in counted.values() for r in c['rows']}
    unresolved = sorted(n for n in count_names if n not in feed_names)
    assert unresolved == sorted(n for n in RENAMES if n != 'Lynn') or unresolved == sorted(RENAMES), unresolved
    assert all(v is None or v in {s['stop_name'] for s in fall['stops'].values()} for v in RENAMES.values())
    assert 'Middleborough/Lakeville' not in {s['stop_name'] for s in fall['stops'].values()}
    old_names = {s['stop_name'] for s in old['stops'].values()}
    assert {'Lynn', 'Middleborough/Lakeville', 'Littleton/Route 495', 'Porter', 'Dedham Corp Center'} <= old_names
    assert old['stops']['Dedham Corp Center-S']['parent_station'] == 'place-FB-0118' and fall['stops']['place-FB-0118']['stop_name'] == 'Dedham Corporate Center'

    # ---- control 1: the count's numbers and departures were valid on the Fall 2024 feed
    old_ids, old_days, _ = rating_schedule(old, dt.date(2024, 10, 14), dt.date(2024, 10, 17))
    old_sched = schedule_trains(old, old_ids)
    old_by_key = {(s['line'], s['train'], s['direction']): s for s in old_sched.values()}
    same_number = [k for k in counted if k in old_by_key]
    exact = sum(1 for k in same_number if counted[k]['departure'] is not None
                and clock_gap(old_by_key[k]['departure'] % 1440, counted[k]['departure']) == 0)
    assert len(same_number) == 434 and exact >= 400, (len(same_number), exact)
    fall_by_key = {(s['line'], s['train'], s['direction']): s for s in sched.values()}
    same_number_2026 = [k for k in counted if k in fall_by_key]
    same_slot_2026 = [k for k in same_number_2026 if counted[k]['departure'] is not None
                      and clock_gap(fall_by_key[k]['departure'] % 1440, counted[k]['departure']) <= TOLERANCE]
    assert len(same_number_2026) == 132 and len(same_slot_2026) <= 3, (len(same_number_2026), len(same_slot_2026))

    # ---- rule 5: which counted trains the Fall 2026 schedule operates
    op = operate(counted, sched)
    ranked = sorted(counted, key=lambda k: (-counted[k]['peak'], order(counted[k]['line']), int(counted[k]['train'])))
    operated = [k for k in ranked if op[k]]
    winner, runner = operated[0], operated[1]
    w, r_ = counted[winner], counted[runner]
    assert w['peak'] > r_['peak'] and winner == ('CR-Providence', '829', '0') and w['peak'] == 1064
    flip = w['peak'] - r_['peak'] + 1
    # determinism: the same winner and runner up under every tolerance from 5 to 30 minutes
    for tol in (5, 15, 20, 30):
        o2 = operate(counted, sched, tol)
        top2 = [k for k in ranked if o2[k]][:2]
        assert top2 == [winner, runner], tol
    # determinism: the result does not depend on which 2026 weekday is read, nor on the two other feeds' calendars
    for day in (dt.date(2026, 9, 30), dt.date(2026, 10, 21), dt.date(2026, 12, 9)):
        s = active_services(fall, day)
        assert frozenset(t['trip_id'] for t in fall['trips'] if t['service_id'] in s and t['route_id'] in fall['cr']) == trip_ids, day
    w_slot = op[winner]
    r_slot = op[runner]
    w_train, r_train = sched[w_slot[3]], sched[r_slot[3]]
    assert w_train['train'] == '867' and w_train['stops'] == [resolve(x['stop_id'], feed_names) for x in w['rows']]

    # ---- the office figures
    fin = [k for k in counted if k[1] == FINANCE_TRAIN and k[0] == 'CR-Providence'][0]
    assert counted[fin]['peak'] == FINANCE_LOAD
    fin_2026 = fall_by_key[fin]
    fin_slot = sched[op[fin][3]]
    fin_rank = 1 + sum(1 for k in counted if counted[k]['peak'] > counted[fin]['peak'])
    fin_tied = [k for k in counted if counted[k]['peak'] == counted[fin]['peak'] and k != fin]
    assert r_['train'] == PLANNING_TRAIN and r_['peak'] == PLANNING_FIGURE and w['rows'][-1]['average_load'] != 0 and r_['rows'][-1]['average_load'] == 0
    assert not any(k[1] in (PLANNING_TRAIN, w['train']) for k in fall_by_key)  # neither number exists in Fall 2026
    assert [k for k in ranked if counted[k]['peak'] > PLANNING_FIGURE] == [winner]
    ctrl = trains(rows, 'Spring 2018')[CONTROL[:3]]
    assert ctrl['peak'] == CONTROL[3] and ctrl['peak_stop'] == CONTROL[4]
    assert max(trains(rows, 'Spring 2018').values(), key=lambda c: c['peak'])['peak'] == CONTROL[3]
    raw_max = max(counted.values(), key=lambda c: c['peak'])
    assert raw_max is w  # the raw maximum is the certified train; the traps are in its identity and its measure
    byn = [k for k in ranked if k[0] == 'CR-Providence' and k[1] == '829']
    assert not any(k[1] == '829' for k in fall_by_key)

    # ---- coverage both ways
    cov_c = collections.Counter(); tot_c = collections.Counter()
    for k in counted:
        tot_c[k[0]] += 1
        cov_c[k[0]] += bool(op[k])
    n_op = sum(cov_c.values()); n_not = len(counted) - n_op
    # a Fall 2026 train has a counted train behind it when it operates at least one counted train (rule 5)
    operating = {o[3] for o in op.values() if o}
    cov_s = collections.Counter(); tot_s = collections.Counter()
    for tid, s in sched.items():
        tot_s[s['line']] += 1
        cov_s[s['line']] += tid in operating
    assert len(operating) == 408 and n_op == 411
    all_lines = sorted(set(tot_c) | set(tot_s), key=order)
    n_uncovered = len(sched) - sum(cov_s.values())
    south_mod = sum(1 for s in sched.values() if s['service'] == 'Spring/SummerWeekday')
    typ = {a['service_id']: a['service_schedule_typicality'] for a in table(fall['zip'], 'calendar_attributes.txt')}
    assert typ['Spring/SummerWeekday'] == '4' and w_train['service'] == 'Spring/SummerWeekday'

    # ---------- 1. CSV register ----------
    dirname = {'0': 'Outbound', '1': 'Inbound'}
    with open(os.path.join(HERE, 'crowding_priority_register.csv'), 'w', newline='') as f:
        wr = csv.writer(f)
        wr.writerow(['rank', 'line_id', 'line_name', 'train', 'direction', 'first_stop', 'counted_departure', 'peak_load',
                     'peak_load_stop', 'peak_load_time', 'weekday_boardings', 'fall_2026_status', 'fall_2026_train',
                     'fall_2026_departure', 'departure_difference_minutes'])
        rank, prev = 0, None
        for i, k in enumerate(ranked, 1):
            c = counted[k]
            if c['peak'] != prev:
                rank, prev = i, c['peak']
            o = op[k]
            wr.writerow([rank, c['line'], name(c['line']), c['train'], dirname[c['direction']], c['first'],
                         hhmm(c['departure']) if c['departure'] is not None else '', c['peak'], c['peak_stop'],
                         hhmm(c['peak_time']) if c['peak_time'] is not None else '', c['boardings'],
                         'operated' if o else 'not operated', o[2] if o else '', hhmm(o[1]) if o else '',
                         int(o[0]) if o else ''])

    # ---------- 2. PNG ----------
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.patches import Patch
    INK, INK2, SURF, GRID = '#0b0b0b', '#52514e', '#fcfcfb', '#e6e5e0'
    C_OP, C_NOT = '#2a78d6', '#eb6834'
    top = ranked[:15]
    fig, ax = plt.subplots(figsize=(13, 8), dpi=200)
    fig.patch.set_facecolor(SURF); ax.set_facecolor(SURF)
    ys = list(range(len(top)))[::-1]
    for y, k in zip(ys, top):
        c = counted[k]; o = op[k]
        ax.barh(y, c['peak'], color=C_OP if o else C_NOT, height=0.62, edgecolor=SURF, linewidth=1)
        lab = f"{c['peak']:,} leaving {c['peak_stop']}"
        lab += f"; Fall 2026 train {o[2]} at {hhmm(o[1])}" if o else '; not operated in Fall 2026'
        if k == winner:
            lab = 'Certified crowding priority\n' + lab
        ax.text(c['peak'] + 12, y, lab, va='center', fontsize=8.4, color=INK, fontweight='bold' if k == winner else 'normal')
    ax.set_yticks(ys)
    ax.set_yticklabels([f"{name(counted[k]['line']).replace(' Line', '')} {counted[k]['train']} {dirname[counted[k]['direction']].lower()}, "
                        f"{hhmm(counted[k]['departure'])} from {counted[k]['first']}" for k in top], fontsize=8.4, color=INK2)
    ax.set_xlim(0, 1950); ax.set_ylim(-0.7, len(top) - 0.3)
    ax.xaxis.grid(True, color=GRID, lw=0.6); ax.set_axisbelow(True)
    for side in ['top', 'right', 'left']:
        ax.spines[side].set_visible(False)
    ax.spines['bottom'].set_color('#d6d5d0')
    ax.set_xticks(range(0, 1601, 200))
    ax.tick_params(colors=INK2, length=0, labelsize=8.4)
    ax.set_xlabel('Peak load in the Fall 2024 count: average riders on board on leaving the busiest stop', fontsize=9, color=INK2)
    fig.text(0.01, 0.975, 'Fifteen highest weekday peak loads in the Fall 2024 count', fontsize=11, color=INK, fontweight='bold')
    fig.text(0.01, 0.948, f"Certified Fall 2026 crowding priority: {name(w['line']).replace(' Line', '')} train {w['train']}, "
             f"{w['peak']:,} riders leaving {w['peak_stop']}, operated in Fall 2026 as train {w_train['train']}", fontsize=9.6, color=INK2)
    ax.legend(handles=[Patch(color=C_OP, label='Operated by the Fall 2026 weekday schedule (same line, direction and first stop, departure within 10 minutes)'),
                       Patch(color=C_NOT, label='Not operated in Fall 2026')],
              loc='upper center', bbox_to_anchor=(0.5, -0.09), ncol=1, frameon=False, fontsize=8.2, labelcolor=INK2)
    fig.text(0.01, 0.012, 'Source: MBTA Commuter Rail Ridership by Trip, Season, Route/Line, and Stop (Fall 2024 season) and the '
             'MBTA GTFS feed published 2 October 2026 (weekday schedule running 28 September to 11 December 2026).',
             fontsize=7.4, color=INK2)
    fig.tight_layout(rect=(0, 0.04, 1, 0.935))
    fig.savefig(os.path.join(HERE, 'top_trains_by_peak_load.png'), facecolor=SURF)

    # ---------- 3. PDF ----------
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    ss = getSampleStyleSheet()
    body = ParagraphStyle('body', parent=ss['Normal'], fontName='Helvetica', fontSize=9.4, leading=12.3, spaceAfter=5)
    h = ParagraphStyle('h', parent=body, fontName='Helvetica-Bold', fontSize=10.4, spaceBefore=6, spaceAfter=3)
    title = ParagraphStyle('t', parent=body, fontName='Helvetica-Bold', fontSize=13.5, leading=17, spaceAfter=4)
    small = ParagraphStyle('s', parent=body, fontSize=8.4, leading=10.8)
    wl, rl = name(w['line']), name(r_['line'])
    w_board_stop = max(w['rows'], key=lambda x: x['average_ons'])
    not_op_lines = {l: tot_c[l] - cov_c[l] for l in all_lines if tot_c[l] - cov_c[l]}
    unc_lines = {l: tot_s[l] - cov_s[l] for l in all_lines if tot_s[l] - cov_s[l]}
    story = [
        Paragraph('Fall 2026 weekday crowding priority: certification', title),
        Paragraph('To: MBTA Board of Directors &nbsp;&nbsp; From: Commuter Rail service planning &nbsp;&nbsp; Date: 6 October 2026', small),
        Spacer(1, 4),
        Paragraph('Certified priority', h),
        Paragraph(f"The Board should certify the Fall 2026 weekday crowding priority as <b>{wl} train {w['train']}</b> of the "
                  f"Fall 2024 count, outbound from {w['first']} at {hhmm(w['departure'])}, with a certified peak load of "
                  f"<b>{w['peak']:,} riders leaving {w['peak_stop']} at {hhmm(w['peak_time'])}</b>. The Fall 2026 weekday "
                  f"schedule operates that train as <b>train {w_train['train']}</b>, leaving {w_train['first']} at "
                  f"{hhmm(w_train['departure'])} and arriving {w_train['last']} at {hhmm(w_train['arrival'])}, the same "
                  f"{len(w_train['stops'])} stops the count recorded. The added coach set goes to train {w_train['train']}. "
                  f"Finance's draft (train {FINANCE_TRAIN}, {FINANCE_LOAD}) and Planning's draft (train {PLANNING_TRAIN}, "
                  f"{PLANNING_FIGURE:,}) are not certified; the certified train's weekday boardings are {w['boardings']:,}, "
                  f"which is not a load.", body),
        Paragraph('The two draft figures: what each measured', h),
        Paragraph(f"<b>Finance, train {FINANCE_TRAIN} at {FINANCE_LOAD}: not certified.</b> Finance took the highest load "
                  f"among counted trains whose number also appears in the Fall 2026 schedule. The number is the only thing "
                  f"the two trains share. In the count, {FINANCE_TRAIN} leaves {counted[fin]['first']} at "
                  f"{hhmm(counted[fin]['departure'])} with {FINANCE_LOAD} riders leaving {counted[fin]['peak_stop']}; in the "
                  f"Fall 2026 schedule, {FINANCE_TRAIN} is an off peak train leaving {fin_2026['first']} at "
                  f"{hhmm(fin_2026['departure'])}. Train numbers were reassigned between the two schedules: of the "
                  f"{len(counted)} counted trains, {len(same_number_2026)} share a number with a Fall 2026 train on the same "
                  f"line and direction and only {len(same_slot_2026)} of those still leave within ten minutes of the counted "
                  f"departure. The counted {FINANCE_TRAIN} is operated in Fall 2026 as train {fin_slot['train']} at "
                  f"{hhmm(fin_slot['departure'])}, and its {FINANCE_LOAD} is only the sixth highest load in the count, shared with "
                  f"{name(fin_tied[0][0])} train {fin_tied[0][1]}.", body),
        Paragraph(f"<b>Planning, train {PLANNING_TRAIN} at {PLANNING_FIGURE:,}: not certified.</b> Train {PLANNING_TRAIN} is the "
                  f"runner up, and {PLANNING_FIGURE:,} is its correct peak load. It can only rank first if train {w['train']} is "
                  f"set aside, and the one thing that distinguishes {w['train']}'s count is that it does not reconcile to zero: "
                  f"the published load on leaving its last stop is {w['rows'][-1]['average_load']}, a rounding residue of averaged "
                  f"boardings ({w['boardings']:,}) and alightings ({w['alightings']:,}), where {PLANNING_TRAIN}'s count ends at "
                  f"{r_['rows'][-1]['average_load']}. The convention certifies counts as published and adjusts none, and 57 of the "
                  f"{len(counted)} counted trains carry the same kind of residue; setting them aside is not a rule the Board "
                  f"applies. Neither {w['train']} nor {PLANNING_TRAIN} appears as a number in the Fall 2026 feed, so Planning's "
                  f"figure is not a number match either.", body),
        Paragraph('How the count was conformed to the Fall 2026 schedule', h),
        Paragraph(f"The latest published count is the Fall 2024 season ({len(counted)} weekday trains, every one listed from "
                  f"its first stop). The Fall 2026 weekday schedule was taken by date from the feed: the same {len(sched)} "
                  f"Commuter Rail trains run on {days} of the rating's {weekdays} Monday to Friday dates, the north side on "
                  f"typical weekday services and the south side ({south_mod} trains, the certified train among them) on the "
                  f"service the feed labels a modified weekday schedule, which is the schedule in effect for the whole "
                  f"rating. Every counted train was matched to the schedule by line, direction and first stop with the "
                  f"departure within ten minutes, after resolving the count's station spellings to the feed's "
                  f"(Littleton/Rte 495, Dedham Corp Center and Porter Square are feed stations under other names; Lynn is "
                  f"a feed station the Fall 2026 schedule no longer serves; Middleborough/Lakeville is no longer a feed "
                  f"station). The Fall 2024 archived feed confirms the method: {len(same_number)} of the {len(counted)} "
                  f"counted trains carry their number in that feed and {exact} of them leave at exactly the counted minute, "
                  f"so the count's numbers and times were right when taken and the numbers moved afterwards.", body),
        Paragraph(f"<b>{n_op} counted trains are operated in Fall 2026 and {n_not} are not.</b> The trains not operated are "
                  + ', '.join(f"{name(l).replace(' Line', '')} {n}" for l, n in not_op_lines.items()) + '. '
                  f"The Middleborough/Lakeville Line ran no Fall 2026 weekday service (the Fall River/New Bedford Line replaced "
                  f"it); Worcester and Franklin run fewer weekday trains than the count covered ({tot_s['CR-Worcester']} and "
                  f"{tot_s['CR-Franklin']} scheduled against {tot_c['CR-Worcester']} and {tot_c['CR-Franklin']} counted); and the "
                  f"Kingston, Greenbush and Haverhill schedules were retimed so that many counted departures have no train "
                  f"within ten minutes. <b>{n_uncovered} of the {len(sched)} Fall 2026 weekday trains have no counted train "
                  f"behind them</b>, meaning they operate no counted train: " + ', '.join(f"{name(l).replace(' Line', '')} {n} of {tot_s[l]}" for l, n in unc_lines.items())
                  + f" (three Fall 2026 trains each operate two counted trains, so {n_op} operated counted trains map to "
                  f"{len(operating)} Fall 2026 trains). The Fall River/New Bedford Line has never been counted; Haverhill and Lowell run more weekday trains "
                  f"than the count covered ({tot_c['CR-Haverhill']} and {tot_c['CR-Lowell']} counted against {tot_s['CR-Haverhill']} "
                  f"and {tot_s['CR-Lowell']} scheduled); Kingston and Greenbush were retimed.", body),
        Paragraph('Runner up and flip point', h),
        Paragraph(f"The runner up is <b>{rl} train {r_['train']}</b>, outbound from {r_['first']} at {hhmm(r_['departure'])}, "
                  f"peak load {r_['peak']:,} leaving {r_['peak_stop']} at {hhmm(r_['peak_time'])}, operated in Fall 2026 as "
                  f"train {r_train['train']} at {hhmm(r_train['departure'])}. The certified train leads by "
                  f"{w['peak'] - r_['peak']} riders, so a fall of <b>{flip} riders</b> in its peak load (to {w['peak'] - flip:,}) "
                  f"would hand the priority to train {r_['train']}. The third operated train is "
                  f"{name(counted[operated[2]]['line'])} {counted[operated[2]]['train']} at {counted[operated[2]]['peak']:,}.", body),
        Paragraph(f"Train {w['train']} stop by stop", h),
    ]
    rows_t = [['Stop', 'Time', 'Boardings', 'Alightings', 'Load leaving']]
    for x in w['rows']:
        rows_t.append([x['stop_id'], hhmm(clock(x['stop_time'])), f"{x['average_ons']:,}", f"{x['average_offs']:,}", f"{x['average_load']:,}"])
    rows_t.append(['Total', '', f"{w['boardings']:,}", f"{w['alightings']:,}", ''])
    t = Table(rows_t, colWidths=[1.9 * inch, 0.7 * inch, 0.9 * inch, 0.9 * inch, 1.0 * inch], repeatRows=1)
    t.setStyle(TableStyle([
        ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold', 8.2), ('FONT', (0, 1), (-1, -1), 'Helvetica', 8.2),
        ('FONT', (0, -1), (-1, -1), 'Helvetica-Bold', 8.2), ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
        ('LINEBELOW', (0, 0), (-1, 0), 0.6, colors.black), ('LINEABOVE', (0, -1), (-1, -1), 0.6, colors.black),
        ('TOPPADDING', (0, 0), (-1, -1), 0.8), ('BOTTOMPADDING', (0, 0), (-1, -1), 0.8),
        ('BACKGROUND', (0, 3), (-1, 3), colors.HexColor('#dbe8f8')),
    ]))
    story += [t, Spacer(1, 5),
        Paragraph(f"Most riders board at <b>{w_board_stop['stop_id']}</b> ({w_board_stop['average_ons']:,} of the "
                  f"{w['boardings']:,} boardings), then Back Bay and Ruggles. The published count ends the run with a load of "
                  f"{w['rows'][-1]['average_load']} at {w['last']}, a rounding residue of the averaged boardings and alightings; "
                  f"under the convention the count is certified as published and is not adjusted for it.", body),
        Paragraph('Previous certification reproduced', h),
        Paragraph(f"The Spring 2018 priority reproduces from the Spring 2018 season of the same file: {name(CONTROL[0])} train "
                  f"{CONTROL[1]} inbound, peak load {CONTROL[3]:,} leaving {CONTROL[4]}, the highest load of that season. The "
                  f"Fall 2026 certified load of {w['peak']:,} is {CONTROL[3] - w['peak']} riders, {(1 - w['peak'] / CONTROL[3]) * 100:.0f} percent, "
                  f"below it, and the highest load has moved from an inbound Worcester train to an outbound Providence train "
                  f"in the evening peak.", body),
        Paragraph('Why no other train survives', h),
        Paragraph(f"The convention fixes the count (latest season, as published), the measure (peak load, not boardings), the "
                  f"identity of a train across schedules (line, direction, first stop and departure, not number) and the "
                  f"schedule (the weekday service the feed runs on most dates of the rating). Applied together they give one "
                  f"ranked register in which train {w['train']} holds the highest load and is operated, and the ranking is the "
                  f"same whether the departure window is five, ten or thirty minutes. Every other candidate relaxes one fixed "
                  f"point: a shared number instead of a shared slot, a count set aside for a rounding residue, boardings instead "
                  f"of load, or a train the rating no longer runs.", body),
    ]
    doc = SimpleDocTemplate(os.path.join(HERE, 'crowding_priority_memo.pdf'), pagesize=letter,
                            leftMargin=0.8 * inch, rightMargin=0.8 * inch, topMargin=0.7 * inch, bottomMargin=0.7 * inch,
                            title='Fall 2026 weekday crowding priority: certification', author='Commuter Rail service planning')
    doc.build(story)

    print(f"certified: {wl} {w['train']} {dirname[w['direction']]} dep {hhmm(w['departure'])} from {w['first']}; peak {w['peak']} leaving {w['peak_stop']} at {hhmm(w['peak_time'])}; boardings {w['boardings']}; operated as {w_train['train']} at {hhmm(w_train['departure'])} ({w_slot[0]} min)")
    print(f"runner up: {rl} {r_['train']} peak {r_['peak']} at {r_['peak_stop']} operated as {r_train['train']} at {hhmm(r_train['departure'])}; flip {flip}; third {counted[operated[2]]['line']} {counted[operated[2]]['train']} {counted[operated[2]]['peak']}")
    print(f"finance {FINANCE_TRAIN}: count dep {hhmm(counted[fin]['departure'])} peak {counted[fin]['peak']} rank {ranked.index(fin)+1}; 2026 train {FINANCE_TRAIN} dep {hhmm(fin_2026['departure'])}; counted 827 operated as {fin_slot['train']} {hhmm(fin_slot['departure'])}")
    print(f"schedule: {len(sched)} trains on {days} of {weekdays} weekdays; south side modified {south_mod}; same number 2026 {len(same_number_2026)} same slot {len(same_slot_2026)}; 2024 feed same number {len(same_number)} exact minute {exact}")
    print(f"coverage: operated {n_op} not {n_not}; not operated by line {not_op_lines}; 2026 trains uncovered {n_uncovered}: {unc_lines}")
    print('operated by line:', [(l, cov_c[l], tot_c[l]) for l in all_lines if tot_c[l]])
    print('control:', CONTROL, 'raw max is winner:', raw_max is w)


if __name__ == '__main__':
    main()

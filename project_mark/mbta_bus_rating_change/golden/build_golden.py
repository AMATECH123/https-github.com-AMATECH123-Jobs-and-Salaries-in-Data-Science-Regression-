"""Builds the three golden deliverables for version 6 from the shipped input package.

Count: the MBTA Commuter Rail ridership count by trip, season, line and stop; the Fall 2024 season (latest) and
the Spring 2018 season (previous certification).
Schedules: the archived feed in effect on Wednesday 16 October 2024 (20241014.zip) and on Wednesday 23 May 2018
(20180516.zip), which fix each counted train's scheduled departure and so its period; the published Fall 2026
feed (MBTA_GTFS.zip) for the rating's weekday supply by period.
Every figure printed or written here is asserted stable under the determinism checks below.
"""
import csv, io, os, json, math, zipfile, collections, datetime as dt, struct

HERE = os.path.dirname(os.path.abspath(__file__))
INPUTS = os.path.join(HERE, '..', 'inputs')
COUNT = 'MBTA_Commuter_Rail_Ridership_by_Trip2C_Season2C_Route_Line2C_and_Stop..'
SEASONS = {'Spring 2018': ('20180516.zip', dt.date(2018, 5, 23)), 'Fall 2024': ('20241014.zip', dt.date(2024, 10, 16))}
PREVIOUS, LATEST = 'Spring 2018', 'Fall 2024'
AM, PM = (5 * 60 + 30, 8 * 60 + 29), (15 * 60 + 30, 18 * 60 + 29)   # convention rule 4, inclusive minutes
RATING_START, RATING_END = dt.date(2026, 9, 28), dt.date(2026, 12, 11)
FINANCE_SHARE = 59.9


def table(z, name):
    with z.open(name) as f:
        return list(csv.DictReader(io.TextIOWrapper(f, encoding='utf-8-sig')))


def mins(t):
    h, m, s = t.split(':')
    return int(h) * 60 + int(m)


def hhmm(m):
    return f"{(m // 60) % 24:02d}:{m % 60:02d}"


# ---------------------------------------------------------------- the count
def load_count():
    rows = list(csv.DictReader(open(os.path.join(INPUTS, COUNT + 'csv'), encoding='utf-8-sig')))
    for r in rows:
        for k in ('average_ons', 'average_offs', 'average_load'):
            r[k] = int(r[k])
    geo = [f['properties'] for f in json.load(open(os.path.join(INPUTS, COUNT + 'geojson')))['features']]
    assert len(geo) == len(rows) == 15761
    for a, b in zip(rows, geo):
        assert all(str(b[k]) == a[k] if k not in ('average_ons', 'average_offs', 'average_load') else b[k] == a[k] for k in b)
    with zipfile.ZipFile(os.path.join(INPUTS, COUNT + 'zip')) as z:
        dbf = [n for n in z.namelist() if n.endswith('.dbf')][0]
        assert struct.unpack('<I', z.open(dbf).read(8)[4:8])[0] == len(rows)
    assert open(os.path.join(INPUTS, COUNT + 'kml'), encoding='utf-8').read().count('<Placemark>') == len(rows)
    return rows


def seqkey(r):
    return int(r['stopsequence']) if r['stopsequence'].isdigit() else 10 ** 6


def count_clock(stop_time):
    """Minutes on the count's own clock, next day placeholder dates counted past 24:00; None when no time."""
    if ' ' not in stop_time:
        return None
    d, t = stop_time.split(' ')
    h, m = t.split(':')[:2]
    return (int(d.split('/')[1]) - 1) * 1440 + int(h) * 60 + int(m)


def trains(rows, season):
    by = collections.defaultdict(list)
    for r in rows:
        if r['season'] == season:
            by[(r['route_id'], r['train'], r['direction_id'])].append(r)
    out = {}
    for k, rs in by.items():
        rs.sort(key=seqkey)
        out[k] = dict(rows=rs, line=k[0], train=k[1], direction=k[2], first=rs[0]['stop_id'],
                      counted=count_clock(rs[0]['stop_time']), boardings=sum(r['average_ons'] for r in rs))
    return out


# ---------------------------------------------------------------- the schedules
def load_feed(name):
    z = zipfile.ZipFile(os.path.join(INPUTS, name))
    d = dict(zip=z, routes={r['route_id']: r for r in table(z, 'routes.txt')}, calendar=table(z, 'calendar.txt'),
             cal_dates=collections.defaultdict(list), trips=table(z, 'trips.txt'),
             stops={r['stop_id']: r for r in table(z, 'stops.txt')})
    for r in table(z, 'calendar_dates.txt'):
        d['cal_dates'][r['date']].append((r['service_id'], r['exception_type']))
    d['cr'] = {k for k, v in d['routes'].items() if v['route_type'] == '2'}
    return d


def active_services(d, date):
    ds = date.strftime('%Y%m%d')
    dow = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'][date.weekday()]
    s = {r['service_id'] for r in d['calendar'] if r['start_date'] <= ds <= r['end_date'] and r[dow] == '1'}
    for sid, et in d['cal_dates'].get(ds, []):
        (s.add if et == '1' else s.discard)(sid)
    return s


def schedule(d, trip_ids):
    tr = {t['trip_id']: t for t in d['trips'] if t['trip_id'] in trip_ids}
    first = {}
    with d['zip'].open('stop_times.txt') as f:
        for r in csv.DictReader(io.TextIOWrapper(f, encoding='utf-8-sig')):
            k = r['trip_id']
            if k in tr:
                seq = int(r['stop_sequence'])
                if k not in first or seq < first[k][0]:
                    first[k] = (seq, mins(r['departure_time']), r['stop_id'])
    out = {}
    for k, t in tr.items():
        out[k] = dict(line=t['route_id'], number=t['trip_short_name'], direction=t['direction_id'],
                      departure=first[k][1], first_stop=first[k][2])
    return out


def day_schedule(d, date):
    s = active_services(d, date)
    return schedule(d, {t['trip_id'] for t in d['trips'] if t['service_id'] in s and t['route_id'] in d['cr']})


def rating_schedule(d, start, end):
    tally = collections.Counter()
    day = start
    while day <= end:
        if day.weekday() < 5:
            s = active_services(d, day)
            tally[frozenset(t['trip_id'] for t in d['trips'] if t['service_id'] in s and t['route_id'] in d['cr'])] += 1
        day += dt.timedelta(days=1)
    (ids, days), = tally.most_common(1)
    return schedule(d, ids), days, sum(tally.values())


def period(departure, direction, am=AM, pm=PM):
    """Convention rule 4: inbound trains leaving 05:30 to 08:29 and outbound trains leaving 15:30 to 18:29 are peak."""
    m = departure % 1440
    if direction == '1' and am[0] <= m <= am[1]:
        return 'peak'
    if direction == '0' and pm[0] <= m <= pm[1]:
        return 'peak'
    return 'off peak'


def key(number, direction):
    """Convention rule 5: train numbers are compared by their digits (the feeds pad with zeros and prefix a few with B)."""
    return (''.join(ch for ch in number if ch.isdigit()).lstrip('0'), direction)


def place(counted, sched, am=AM, pm=PM, use_count_clock=False, strip=True):
    """Convention rule 5: a counted train is the scheduled train of the same number and direction."""
    idx = {}
    for s in sched.values():
        k = key(s['number'], s['direction']) if strip else (s['number'], s['direction'])
        assert k not in idx, k
        idx[k] = s
    out = {}
    for k, c in counted.items():
        s = idx.get(key(c['train'], c['direction']) if strip else (c['train'], c['direction']))
        if use_count_clock:
            dep = c['counted']
            out[k] = (period(dep, c['direction'], am, pm), dep, s) if dep is not None else (None, None, s)
        else:
            out[k] = (period(s['departure'], c['direction'], am, pm), s['departure'], s) if s else (None, None, None)
    return out


def totals(counted, placed):
    t = collections.Counter(); byline = collections.defaultdict(collections.Counter); unplaced = []
    for k, c in counted.items():
        p = placed[k][0]
        if p is None:
            unplaced.append(k); continue
        t[p] += c['boardings']; byline[c['line']][p] += c['boardings']
    return t, byline, unplaced


def share(t):
    return 100.0 * t['peak'] / (t['peak'] + t['off peak'])


def main():
    rows = load_count()
    counted = {s: trains(rows, s) for s in SEASONS}
    assert len(counted[PREVIOUS]) == 516 and len(counted[LATEST]) == 514
    feeds = {s: load_feed(f) for s, (f, _) in SEASONS.items()}
    sched = {s: day_schedule(feeds[s], SEASONS[s][1]) for s in SEASONS}
    assert len(sched[PREVIOUS]) == 511 and len(sched[LATEST]) == 524
    placed = {s: place(counted[s], sched[s]) for s in SEASONS}
    tot, byline, unplaced = {}, {}, {}
    for s in SEASONS:
        tot[s], byline[s], unplaced[s] = totals(counted[s], placed[s])
    s18, s24 = share(tot[PREVIOUS]), share(tot[LATEST])
    change = s24 - s18
    placement = 'peak' if change >= 0 else 'off peak'
    assert placement == 'off peak' and round(s18, 1) == 71.9 and round(s24, 1) == 59.9 and round(change, 1) == -12.0
    assert len(unplaced[PREVIOUS]) == 1 and len(unplaced[LATEST]) == 0
    assert all(placed[LATEST][k][2]['line'] == counted[LATEST][k]['line'] for k in counted[LATEST])

    # ---- determinism: boundaries, the other 2018 schedule, and the count's own clock
    for am, pm in [((300, 479), (900, 1079)), ((360, 539), (960, 1139)), ((330, 539), (930, 1139)), ((300, 509), (900, 1109))]:
        a = share(totals(counted[PREVIOUS], place(counted[PREVIOUS], sched[PREVIOUS], am, pm))[0])
        b = share(totals(counted[LATEST], place(counted[LATEST], sched[LATEST], am, pm))[0])
        assert b - a < -10, (am, pm, a, b)
    alt18 = day_schedule(feeds[PREVIOUS], dt.date(2018, 5, 16))
    alt = share(totals(counted[PREVIOUS], place(counted[PREVIOUS], alt18))[0])
    assert round(alt, 1) == round(s18, 1)
    for day in (dt.date(2024, 10, 15), dt.date(2024, 10, 17)):
        assert round(share(totals(counted[LATEST], place(counted[LATEST], day_schedule(feeds[LATEST], day)))[0]), 1) == round(s24, 1)
    # the count's own clock: Fall 2024 agrees with the schedule, Spring 2018 runs five hours ahead of it
    offsets = {}
    for s in SEASONS:
        o = collections.Counter()
        for k, c in counted[s].items():
            p = placed[s][k]
            if p[2] and c['counted'] is not None:
                o[c['counted'] - p[2]['departure']] += 1
        offsets[s] = o
    assert offsets[LATEST][0] >= 400 and offsets[PREVIOUS][300] >= 400
    clock = {s: totals(counted[s], place(counted[s], sched[s], use_count_clock=True))[0] for s in SEASONS}
    clock_change = share(clock[LATEST]) - share(clock[PREVIOUS])
    assert clock_change > 50 and round(share(clock[LATEST]), 1) == 59.8  # the trap flips the sign
    # the raw string join: Old Colony trains carry a leading zero in the feeds and none in the count
    raw = {s: totals(counted[s], place(counted[s], sched[s], strip=False)) for s in SEASONS}
    raw_un = {s: len(raw[s][2]) for s in SEASONS}
    raw_change = share(raw[LATEST][0]) - share(raw[PREVIOUS][0])
    assert raw_un[LATEST] == 80 and raw_change < 0
    letters = [s_['number'] for s_ in sched[PREVIOUS].values() if not s_['number'].isdigit()]
    assert sorted(letters) == ['B787', 'B789', 'B910', 'B912']

    # ---- recovery, lines, flip, Fall 2026 supply
    rec = {p: 100.0 * tot[LATEST][p] / tot[PREVIOUS][p] for p in ('peak', 'off peak')}
    lines = dict(feeds[PREVIOUS]['routes']); lines.update(feeds[LATEST]['routes'])
    name = lambda l: lines[l]['route_long_name']
    order = lambda l: int(lines[l]['route_sort_order'])
    line_rows = []
    for l in sorted(byline[PREVIOUS], key=order):
        a, b = byline[PREVIOUS][l], byline[LATEST][l]
        line_rows.append(dict(line=l, s18=share(a), s24=share(b), change=share(b) - share(a),
                              b18=sum(a.values()), b24=sum(b.values()),
                              rp=100.0 * b['peak'] / a['peak'], ro=100.0 * b['off peak'] / a['off peak'],
                              peak18=a['peak'], off18=a['off peak'], peak24=b['peak'], off24=b['off peak']))
    assert all(r['change'] < 0 for r in line_rows)
    ranked = sorted(line_rows, key=lambda r: r['change'])
    fell_most, held_best = ranked[0], ranked[-1]
    assert fell_most['line'] == 'CR-Fitchburg' and held_best['line'] == 'CR-Haverhill'
    above = [r for r in line_rows if r['off24'] > r['off18']]
    T24, P24 = sum(tot[LATEST].values()), tot[LATEST]['peak']
    flip = math.ceil(s18 / 100.0 * T24 - P24)
    assert 100.0 * (P24 + flip) / T24 >= s18 > 100.0 * (P24 + flip - 1) / T24
    fall = load_feed('MBTA_GTFS.zip')
    fall['cr'] = {k for k, v in fall['routes'].items() if v['route_fare_class'] == 'Commuter Rail'}
    lines.update(fall['routes'])
    fsched, fdays, fweekdays = rating_schedule(fall, RATING_START, RATING_END)
    assert len(fsched) == 547 and fdays >= 50
    supply = collections.Counter(period(s['departure'], s['direction']) for s in fsched.values())
    supply_line = collections.defaultdict(collections.Counter)
    for s in fsched.values():
        supply_line[s['line']][period(s['departure'], s['direction'])] += 1
    dirname = {'0': 'Outbound', '1': 'Inbound'}
    stopname = lambda d, sid: d['stops'][sid]['stop_name'] if sid in d['stops'] else sid

    # ---------- 1. CSV register ----------
    with open(os.path.join(HERE, 'period_register.csv'), 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['season', 'line_id', 'line_name', 'train', 'direction', 'first_stop', 'counted_time', 'scheduled_departure',
                    'period', 'weekday_boardings', 'placed'])
        for s in (PREVIOUS, LATEST):
            for k in sorted(counted[s], key=lambda k: (order(counted[s][k]['line']), int(counted[s][k]['train']), k[2])):
                c = counted[s][k]; p = placed[s][k]
                w.writerow([s, c['line'], name(c['line']), c['train'], dirname[c['direction']], c['first'],
                            hhmm(c['counted']) if c['counted'] is not None else '',
                            hhmm(p[1]) if p[1] is not None else '', p[0] or '', c['boardings'], 'yes' if p[0] else 'no'])

    # ---------- 2. PNG ----------
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    INK, INK2, SURF, GRID = '#0b0b0b', '#52514e', '#fcfcfb', '#e6e5e0'
    C18, C24 = '#eb6834', '#2a78d6'
    items = ranked + [dict(line='SYSTEM', s18=s18, s24=s24, change=change)]
    fig, ax = plt.subplots(figsize=(12, 7.6), dpi=200)
    fig.patch.set_facecolor(SURF); ax.set_facecolor(SURF)
    ys = list(range(len(items)))[::-1]
    for y, r in zip(ys, items):
        ax.plot([r['s24'], r['s18']], [y, y], color='#c9c8c2', lw=2.2, zorder=1, solid_capstyle='round')
        ax.plot(r['s18'], y, 'o', color=C18, ms=9, markeredgecolor=SURF, markeredgewidth=1.5, zorder=3)
        ax.plot(r['s24'], y, 'o', color=C24, ms=9, markeredgecolor=SURF, markeredgewidth=1.5, zorder=3)
        ax.text(r['s24'] - 1.2, y, f"{r['s24']:.1f}", ha='right', va='center', fontsize=8.6, color=INK)
        ax.text(r['s18'] + 1.2, y, f"{r['s18']:.1f}", ha='left', va='center', fontsize=8.6, color=INK)
        ax.text(96, y, f"{r['change']:+.1f} pts", ha='right', va='center', fontsize=8.6, color=INK,
                fontweight='bold' if r['line'] == 'SYSTEM' else 'normal')
    ax.set_yticks(ys)
    ax.set_yticklabels(['All lines (certified)' if r['line'] == 'SYSTEM' else name(r['line']) for r in items], fontsize=9,
                       color=INK2)
    ax.axhline(0.5, color='#d6d5d0', lw=0.8)
    ax.set_xlim(35, 97); ax.set_ylim(-0.7, len(items) - 0.3)
    ax.set_xticks(range(40, 91, 10)); ax.set_xticklabels([f"{t}%" for t in range(40, 91, 10)], fontsize=8.6, color=INK2)
    ax.xaxis.grid(True, color=GRID, lw=0.6); ax.set_axisbelow(True)
    for side in ['top', 'right', 'left']:
        ax.spines[side].set_visible(False)
    ax.spines['bottom'].set_color('#d6d5d0'); ax.tick_params(colors=INK2, length=0)
    ax.set_xlabel('Share of weekday boardings on peak trains (inbound leaving 05:30 to 08:29, outbound leaving 15:30 to 18:29)',
                  fontsize=9, color=INK2)
    fig.text(0.01, 0.975, 'Peak share of weekday Commuter Rail boardings, Spring 2018 certification to Fall 2024 count', fontsize=11,
             color=INK, fontweight='bold')
    fig.text(0.01, 0.948, f"Every line fell. System share {s18:.1f}% to {s24:.1f}% ({change:+.1f} points): the Fall 2026 added "
             f"weekday round trip is placed in the {placement}.", fontsize=9.6, color=INK2)
    from matplotlib.lines import Line2D
    ax.legend(handles=[Line2D([], [], marker='o', color=C18, lw=0, ms=8, label='Spring 2018'),
                       Line2D([], [], marker='o', color=C24, lw=0, ms=8, label='Fall 2024')],
              loc='lower left', frameon=False, fontsize=8.6, labelcolor=INK2)
    fig.text(0.01, 0.012, 'Source: MBTA Commuter Rail Ridership by Trip, Season, Route/Line, and Stop; periods from the scheduled '
             'departure in the MBTA GTFS feeds of 23 May 2018 and 16 October 2024. Lines ordered by the change in share.',
             fontsize=7.4, color=INK2)
    fig.tight_layout(rect=(0, 0.03, 1, 0.935))
    fig.savefig(os.path.join(HERE, 'peak_share_by_line.png'), facecolor=SURF)

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
    T18 = sum(tot[PREVIOUS].values())
    un18 = ', '.join(f"{name(k[0]).replace(' Line', '')} {k[1]} {dirname[k[2]].lower()}" for k in unplaced[PREVIOUS])
    oc = {s: sum(1 for k in counted[s] if k[0] in ('CR-Greenbush', 'CR-Kingston', 'CR-Middleborough')) for s in SEASONS}
    story = [
        Paragraph('Fall 2026 added weekday round trip: service allocation certification', title),
        Paragraph('To: MBTA Board of Directors &nbsp;&nbsp; From: Commuter Rail service planning &nbsp;&nbsp; Date: 6 October 2026', small),
        Spacer(1, 4),
        Paragraph('Placement', h),
        Paragraph(f"The Board should place the Fall 2026 added weekday round trip in the <b>off peak</b>. The certified peak share of "
                  f"weekday Commuter Rail boardings is <b>{s24:.1f} percent</b> in the Fall 2024 count ({tot[LATEST]['peak']:,} of "
                  f"{T24:,} placed boardings) against <b>{s18:.1f} percent</b> at the Spring 2018 certification "
                  f"({tot[PREVIOUS]['peak']:,} of {T18:,}), a fall of <b>{-change:.1f} points</b>. The convention places the round "
                  f"trip in the peak only when the share has held or risen; it has fallen on every line. Finance's draft and "
                  f"Planning's draft, which both place the round trip in the peak, are not certified.", body),
        Paragraph('The two drafts: what each measured', h),
        Paragraph(f"<b>Finance, peak share {FINANCE_SHARE} percent, round trip to the peak: not certified.</b> The share is right and "
                  f"it is the Fall 2024 figure alone. The convention does not ask whether the peak still carries most riders (it does, "
                  f"three in five); it asks whether the peak's share has held since the previous certification, and that needs the "
                  f"Spring 2018 count placed on the same rule. Against {s18:.1f} percent, {s24:.1f} percent is a fall.", body),
        Paragraph(f"<b>Planning, the peak's share has risen since Spring 2018, round trip to the peak: not certified.</b> Planning read "
                  f"the Spring 2018 trains' periods from the count's own stop time field. In the Spring 2018 season that field runs "
                  f"five hours ahead of the schedule on every train ({offsets[PREVIOUS][300]} of the {sum(offsets[PREVIOUS].values())} "
                  f"matched trains sit at exactly 300 minutes; the 06:57 from Worcester is written 11:57, and evening trains carry "
                  f"the next day's placeholder date), so morning peak trains land in the midday and evening peak trains land after "
                  f"20:00. Read that way the Spring 2018 peak share is {share(clock[PREVIOUS]):.1f} percent and the change is "
                  f"{clock_change:+.1f} points. In the Fall 2024 season the same field agrees with the schedule to the minute on "
                  f"{offsets[LATEST][0]} of {sum(offsets[LATEST].values())} matched trains, which is why the error only shows in the "
                  f"comparison. The convention places trains by their scheduled departure, and the Spring 2018 feed gives it.", body),
        Paragraph('Peak and off peak boardings, and what each has recovered to', h),
    ]
    rows_t = [['', 'Spring 2018', 'Fall 2024', 'Fall 2024 as % of 2018'],
              ['Peak boardings', f"{tot[PREVIOUS]['peak']:,}", f"{tot[LATEST]['peak']:,}", f"{rec['peak']:.1f}%"],
              ['Off peak boardings', f"{tot[PREVIOUS]['off peak']:,}", f"{tot[LATEST]['off peak']:,}", f"{rec['off peak']:.1f}%"],
              ['Placed boardings', f"{T18:,}", f"{T24:,}", f"{100.0 * T24 / T18:.1f}%"],
              ['Peak share', f"{s18:.1f}%", f"{s24:.1f}%", f"{change:+.1f} pts"]]
    t = Table(rows_t, colWidths=[1.6 * inch, 1.1 * inch, 1.1 * inch, 1.6 * inch])
    t.setStyle(TableStyle([('FONT', (0, 0), (-1, 0), 'Helvetica-Bold', 8.4), ('FONT', (0, 1), (-1, -1), 'Helvetica', 8.4),
                           ('FONT', (0, -1), (-1, -1), 'Helvetica-Bold', 8.4), ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
                           ('LINEBELOW', (0, 0), (-1, 0), 0.6, colors.black), ('LINEABOVE', (0, -1), (-1, -1), 0.6, colors.black),
                           ('TOPPADDING', (0, 0), (-1, -1), 0.9), ('BOTTOMPADDING', (0, 0), (-1, -1), 0.9)]))
    story += [t, Spacer(1, 5),
        Paragraph(f"Peak boardings stand at {rec['peak']:.1f} percent of their Spring 2018 level and off peak boardings at "
                  f"{rec['off peak']:.1f} percent: the off peak has more than recovered while the peak has lost a third.", body),
        Paragraph('How the counts were placed against the schedules', h),
        Paragraph(f"Each counted train (line, train number, direction) was matched to the scheduled train of the same number and "
                  f"direction in the feed in effect for its season, 23 May 2018 and 16 October 2024, and placed by that train's "
                  f"scheduled departure from its first stop. The feeds write Old Colony train numbers with a leading zero (044) and "
                  f"the count without (44); matched as numbers, every one of the {len(counted[LATEST])} Fall 2024 trains is placed "
                  f"and {len(counted[PREVIOUS]) - len(unplaced[PREVIOUS])} of the {len(counted[PREVIOUS])} Spring 2018 trains; the 2018 feed "
                  f"also prefixes four numbers with a letter (B787, B789, B910, B912), which the digits resolve. Matched as text, the {oc[LATEST]} Greenbush, Kingston and Middleborough/Lakeville trains of Fall 2024 ({sum(c['boardings'] for k, c in counted[LATEST].items() if k in raw[LATEST][2]):,} "
                  f"boardings) and {raw_un[PREVIOUS]} Spring 2018 trains would fall out. The one Spring 2018 train the 23 May schedule "
                  f"does not list ({un18}; {sum(counted[PREVIOUS][k]['boardings'] for k in unplaced[PREVIOUS])} boardings) is left out "
                  f"of the totals as the convention directs. Counted stop times were not used for "
                  f"placement; where they were compared with the schedule they agreed to the minute in Fall 2024 and ran five hours "
                  f"ahead in Spring 2018.", body),
        Paragraph('Lines ranked by the change in peak share', h),
    ]
    rows_l = [['Line', '2018 share', '2024 share', 'Change', '2018 boardings', '2024 boardings', 'Off peak 2024 as % of 2018']]
    for r in ranked:
        rows_l.append([name(r['line']), f"{r['s18']:.1f}%", f"{r['s24']:.1f}%", f"{r['change']:+.1f}", f"{r['b18']:,}", f"{r['b24']:,}", f"{r['ro']:.1f}%"])
    rows_l.append(['All lines', f"{s18:.1f}%", f"{s24:.1f}%", f"{change:+.1f}", f"{T18:,}", f"{T24:,}", f"{rec['off peak']:.1f}%"])
    t2 = Table(rows_l, colWidths=[1.75 * inch, 0.75 * inch, 0.75 * inch, 0.65 * inch, 0.95 * inch, 0.95 * inch, 1.2 * inch], repeatRows=1)
    t2.setStyle(TableStyle([('FONT', (0, 0), (-1, 0), 'Helvetica-Bold', 8), ('FONT', (0, 1), (-1, -1), 'Helvetica', 8),
                            ('FONT', (0, -1), (-1, -1), 'Helvetica-Bold', 8), ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
                            ('LINEBELOW', (0, 0), (-1, 0), 0.6, colors.black), ('LINEABOVE', (0, -1), (-1, -1), 0.6, colors.black),
                            ('TOPPADDING', (0, 0), (-1, -1), 0.8), ('BOTTOMPADDING', (0, 0), (-1, -1), 0.8),
                            ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor('#fde7d9')),
                            ('BACKGROUND', (0, len(ranked)), (-1, len(ranked)), colors.HexColor('#dbe8f8'))]))
    story += [t2, Spacer(1, 5),
        Paragraph(f"<b>{name(fell_most['line'])}</b> fell most, {fell_most['change']:+.1f} points ({fell_most['s18']:.1f} to "
                  f"{fell_most['s24']:.1f} percent). <b>{name(held_best['line'])}</b> held best, {held_best['change']:+.1f} points "
                  f"({held_best['s18']:.1f} to {held_best['s24']:.1f} percent), because its off peak boardings fell almost as far as its "
                  f"peak boardings. Off peak boardings now exceed their Spring 2018 level on {len(above)} lines: "
                  + ', '.join(f"{name(r['line']).replace(' Line', '')} ({r['ro']:.0f}%)" for r in sorted(above, key=lambda r: -r['ro']))
                  + f". On the other {len(line_rows) - len(above)} the off peak fell too, but less than the peak. The Fall River/New "
                  f"Bedford Line, which replaced Middleborough/Lakeville in 2025, has no count and no certified share.", body),
        Paragraph('Fall 2026 weekday supply by period', h),
        Paragraph(f"The Fall 2026 weekday schedule, the one in effect on {fdays} of the rating's {fweekdays} Monday to Friday dates, runs "
                  f"{len(fsched)} Commuter Rail trains: <b>{supply['peak']} in the peak and {supply['off peak']} in the off peak</b> on the "
                  f"same period rule ({100.0 * supply['peak'] / len(fsched):.1f} percent of trains in the peak, carrying "
                  f"{s24:.1f} percent of boardings on the latest count). By line, peak and off peak trains are "
                  + ', '.join(f"{name(l).replace(' Line', '')} {supply_line[l]['peak']} and {supply_line[l]['off peak']}" for l in sorted(supply_line, key=order)) + '.', body),
        Paragraph('Flip point', h),
        Paragraph(f"For the Fall 2024 peak share to hold at the Spring 2018 level of {s18:.1f} percent, <b>{flip:,} weekday boardings</b> "
                  f"would have to move from off peak trains to peak trains in the Fall 2024 count (peak {P24:,} to {P24 + flip:,} of "
                  f"{T24:,}). That is {100.0 * flip / tot[LATEST]['off peak']:.0f} percent of all off peak boardings, and nothing in "
                  f"the count moves it.", body),
        Paragraph('Why no other placement survives', h),
        Paragraph(f"The convention fixes the count (latest season, as published), the period rule (scheduled departure, inbound "
                  f"05:30 to 08:29 and outbound 15:30 to 18:29), the key (train number and direction in the season's schedule) and "
                  f"the test (share held or risen against the previous certification). On those terms the share fell "
                  f"{-change:.1f} points, it fell on every one of twelve lines, and it falls under every nearby boundary and on the "
                  f"other Spring 2018 schedule in the feed. The peak placement survives only by reading one season's periods off a "
                  f"clock that is five hours wrong, or by asking a different question than the convention asks.", body),
    ]
    doc = SimpleDocTemplate(os.path.join(HERE, 'service_allocation_memo.pdf'), pagesize=letter,
                            leftMargin=0.8 * inch, rightMargin=0.8 * inch, topMargin=0.7 * inch, bottomMargin=0.7 * inch,
                            title='Fall 2026 added weekday round trip: service allocation certification', author='Commuter Rail service planning')
    doc.build(story)

    print(f"placement {placement}; share {s18:.2f} -> {s24:.2f} ({change:+.2f}); peak {tot[PREVIOUS]['peak']}->{tot[LATEST]['peak']} off {tot[PREVIOUS]['off peak']}->{tot[LATEST]['off peak']}; placed {T18}/{T24}; recovery peak {rec['peak']:.1f} off {rec['off peak']:.1f}")
    print(f"unplaced 2018 {unplaced[PREVIOUS]} 2024 {unplaced[LATEST]}; offsets 2018 {offsets[PREVIOUS].most_common(3)} 2024 {offsets[LATEST].most_common(3)}")
    print(f"count clock trap: 2018 share {share(clock[PREVIOUS]):.1f} 2024 {share(clock[LATEST]):.1f} change {clock_change:+.1f}; raw join unplaced {raw_un} change {raw_change:+.1f}")
    print('lines:', [(r['line'], round(r['s18'], 1), round(r['s24'], 1), round(r['change'], 1), round(r['ro'], 1)) for r in ranked])
    print(f"fell most {fell_most['line']} held best {held_best['line']}; above 2018 off peak {[r['line'] for r in above]}; flip {flip}")
    print(f"fall 2026 supply {dict(supply)} on {fdays}/{fweekdays} days; by line {[(l, supply_line[l]['peak'], supply_line[l]['off peak']) for l in sorted(supply_line, key=order)]}")


if __name__ == '__main__':
    main()

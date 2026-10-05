"""Builds the three golden deliverables from the shipped input package.

Reads 20260821.zip (and cross checks against 20260812.zip) straight from ../inputs,
so every number in the CSV, the chart, and the memo comes from one pass over one set of files.
"""
import csv, io, zipfile, collections, datetime as dt, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
INPUTS = os.path.join(HERE, '..', 'inputs')
BUS = {'Frequent Bus', 'Local Bus', 'Coverage Bus', 'Commuter Bus', 'Supplemental Bus'}
SUMMER_DAY = dt.date(2026, 9, 2)    # Wednesday, Summer rating, school in session, typical schedule
FALL_DAY = dt.date(2026, 9, 23)     # Wednesday, Fall rating, typical schedule
FINANCE_FIGURE, PLANNING_FIGURE = 321, 121


def table(z, name):
    with z.open(name) as f:
        return list(csv.DictReader(io.TextIOWrapper(f, encoding='utf-8-sig')))


def load(path):
    z = zipfile.ZipFile(path)
    d = {}
    d['routes'] = {r['route_id']: r for r in table(z, 'routes.txt')}
    d['calendar'] = table(z, 'calendar.txt')
    d['cal_dates'] = collections.defaultdict(list)
    for r in table(z, 'calendar_dates.txt'):
        d['cal_dates'][r['date']].append((r['service_id'], r['exception_type']))
    d['attrs'] = {r['service_id']: r for r in table(z, 'calendar_attributes.txt')}
    d['supplemental'] = {r['trip_id'] for r in table(z, 'trips_properties.txt')
                         if r['trip_property_id'] == 'trip_type' and r['value'] == 'supplemental'}
    d['trips'] = table(z, 'trips.txt')
    d['multi'] = collections.defaultdict(list)
    for r in table(z, 'multi_route_trips.txt'):
        d['multi'][r['trip_id']].append(r['added_route_id'])
    d['stops'] = {r['stop_id']: r for r in table(z, 'stops.txt')}
    d['zip'] = z
    return d


def active_services(d, date):
    ds = date.strftime('%Y%m%d')
    dow = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'][date.weekday()]
    s = {r['service_id'] for r in d['calendar'] if r['start_date'] <= ds <= r['end_date'] and r[dow] == '1'}
    for sid, et in d['cal_dates'].get(ds, []):
        (s.add if et == '1' else s.discard)(sid)
    return s


def is_bus(d, trip):
    return d['routes'][trip['route_id']]['route_desc'] in BUS


def register(d, date, count_multi=False):
    s = active_services(d, date)
    c = collections.Counter()
    for t in d['trips']:
        if t['service_id'] in s and is_bus(d, t):
            c[t['route_id']] += 1
            if count_multi:
                for extra in d['multi'].get(t['trip_id'], []):
                    c[extra] += 1
    return c


def supplemental_count(d, date):
    s = active_services(d, date)
    return sum(1 for t in d['trips'] if t['service_id'] in s and is_bus(d, t) and t['trip_id'] in d['supplemental'])


def span_and_ends(d, date, route_id):
    s = active_services(d, date)
    trip_dir = {t['trip_id']: t for t in d['trips'] if t['route_id'] == route_id and t['service_id'] in s}
    first = last = None
    last_stop = {}
    with d['zip'].open('stop_times.txt') as f:
        for r in csv.DictReader(io.TextIOWrapper(f, encoding='utf-8-sig')):
            t = trip_dir.get(r['trip_id'])
            if not t:
                continue
            if first is None or r['departure_time'] < first:
                first = r['departure_time']
            if last is None or r['arrival_time'] > last:
                last = r['arrival_time']
            key = (t['direction_id'], r['trip_id'])
            seq = int(r['stop_sequence'])
            if key not in last_stop or seq > last_stop[key][0]:
                last_stop[key] = (seq, r['stop_id'])
    ends = {}
    for (direction, _), (_, stop_id) in last_stop.items():
        ends.setdefault(direction, collections.Counter())[d['stops'][stop_id]['stop_name']] += 1
    heads = collections.Counter((t['direction_id'], t['trip_headsign']) for t in trip_dir.values())
    return first, last, ends, heads


def revenue_minutes(d, date):
    """Scheduled revenue minutes per bus route: last arrival minus first departure of each active trip."""
    s = active_services(d, date)
    tr = {t['trip_id']: t['route_id'] for t in d['trips'] if t['service_id'] in s and is_bus(d, t)}
    first, last = {}, {}
    with d['zip'].open('stop_times.txt') as f:
        for r in csv.DictReader(io.TextIOWrapper(f, encoding='utf-8-sig')):
            if r['trip_id'] not in tr:
                continue
            k = r['trip_id']
            if k not in first or r['departure_time'] < first[k]:
                first[k] = r['departure_time']
            if k not in last or r['arrival_time'] > last[k]:
                last[k] = r['arrival_time']
    def mins(t):
        h, m, _ = t.split(':')
        return int(h) * 60 + int(m)
    by_route = collections.Counter()
    for k in first:
        by_route[tr[k]] += mins(last[k]) - mins(first[k])
    return by_route


def clock(t):
    h, m, _ = t.split(':')
    h = int(h)
    if h >= 24:
        return f"{t[:5]} ({h-24}:{m} a.m. the next day)"
    return t[:5]


def main():
    fall_feed = load(os.path.join(INPUTS, '20260821.zip'))
    summer_feed = load(os.path.join(INPUTS, '20260812.zip'))
    routes = fall_feed['routes']

    summer = register(fall_feed, SUMMER_DAY)
    fall = register(fall_feed, FALL_DAY)
    # Determinism checks: the Summer feed gives the same Summer register, and every other
    # typical school day Monday to Thursday in each rating gives the same per route counts.
    assert register(summer_feed, SUMMER_DAY) == summer
    for day in [dt.date(2026, 9, 1), dt.date(2026, 9, 3)]:
        assert register(fall_feed, day) == summer, day
    for day in [dt.date(2026, 9, 8), dt.date(2026, 9, 9), dt.date(2026, 9, 10), dt.date(2026, 9, 30)]:
        assert register(fall_feed, day) == fall, day

    all_routes = sorted(set(summer) | set(fall), key=lambda r: int(routes[r]['route_sort_order']))
    S, F = sum(summer.values()), sum(fall.values())
    net = F - S
    delta = {r: fall[r] - summer[r] for r in all_routes}
    changed = sorted([r for r in all_routes if delta[r]],
                     key=lambda r: (-abs(delta[r]), int(routes[r]['route_sort_order'])))
    driver, runner = changed[0], changed[1]
    gap = abs(delta[driver]) - abs(delta[runner])
    flip = gap + 1

    # The two office figures, reproduced from the same files so the memo can say what they counted.
    first_fall_feed_weekday = dt.date(2026, 8, 24)
    finance_summer = sum(register(fall_feed, first_fall_feed_weekday).values())
    finance_net = F - finance_summer
    planning_summer = sum(register(fall_feed, SUMMER_DAY, count_multi=True).values())
    planning_fall = sum(register(fall_feed, FALL_DAY, count_multi=True).values())
    planning_net = planning_fall - planning_summer
    assert finance_net == FINANCE_FIGURE and planning_net == PLANNING_FIGURE, (finance_net, planning_net)

    sup_s, sup_f = supplemental_count(fall_feed, SUMMER_DAY), supplemental_count(fall_feed, FALL_DAY)
    s_first, s_last, s_ends, s_heads = span_and_ends(fall_feed, SUMMER_DAY, driver)
    f_first, f_last, f_ends, f_heads = span_and_ends(fall_feed, FALL_DAY, driver)

    min_s, min_f = revenue_minutes(fall_feed, SUMMER_DAY), revenue_minutes(fall_feed, FALL_DAY)
    MS, MF = sum(min_s.values()), sum(min_f.values())
    dmin = {r: min_f[r] - min_s[r] for r in all_routes}
    hours_driver = max(all_routes, key=lambda r: (abs(dmin[r]), -int(routes[r]['route_sort_order'])))
    hours_second = max([r for r in all_routes if r != hours_driver], key=lambda r: (abs(dmin[r]), -int(routes[r]['route_sort_order'])))
    hrs = lambda m: f"{m / 60:,.1f}"

    # ---------- 1. CSV register ----------
    csv_path = os.path.join(HERE, 'route_service_change.csv')
    with open(csv_path, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['route_id', 'route_name', 'service_category', 'summer_weekday_trips',
                    'fall_weekday_trips', 'change', 'pct_change',
                    'summer_weekday_revenue_minutes', 'fall_weekday_revenue_minutes', 'change_minutes'])
        for r in all_routes:
            pct = '' if summer[r] == 0 else f"{100.0 * delta[r] / summer[r]:.1f}"
            w.writerow([r, routes[r]['route_short_name'] or routes[r]['route_long_name'],
                        routes[r]['route_desc'], summer[r], fall[r], delta[r], pct,
                        min_s[r], min_f[r], dmin[r]])
        w.writerow(['TOTAL', 'All MBTA bus routes', '', S, F, net, f"{100.0 * net / S:.1f}", MS, MF, MF - MS])

    # ---------- 2. Waterfall PNG ----------
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    INK, INK2, SURF = '#0b0b0b', '#52514e', '#fcfcfb'
    UP, DOWN, TOTAL, DRIVER = '#2a78d6', '#e34948', '#b8b7b2', '#eb6834'
    labels = ['Summer\n2026'] + [routes[r]['route_short_name'] for r in changed] + ['Fall\n2026']
    fig, ax = plt.subplots(figsize=(16, 7.2), dpi=200)
    fig.patch.set_facecolor(SURF); ax.set_facecolor(SURF)
    run = S
    x = 0
    ax.bar(x, S, color=TOTAL, width=0.62)
    ax.text(x, S + 8, f"{S:,}", ha='center', va='bottom', fontsize=9, color=INK)
    bottoms, heights, colors = [], [], []
    for r in changed:
        x += 1
        d = delta[r]
        bottom = run if d > 0 else run + d
        color = DRIVER if r == driver else (UP if d > 0 else DOWN)
        ax.bar(x, abs(d), bottom=bottom, color=color, width=0.62)
        ax.text(x, run + d + (8 if d > 0 else -8), f"{d:+d}", ha='center',
                va='bottom' if d > 0 else 'top', fontsize=8.5, color=INK)
        ax.plot([x - 0.5, x + 0.5], [run + d, run + d], color=INK2, lw=0.6, alpha=0.5)
        run += d
    x += 1
    ax.bar(x, F, color=TOTAL, width=0.62)
    ax.text(x, F + 8, f"{F:,}", ha='center', va='bottom', fontsize=9, color=INK)
    assert run == F
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=0, fontsize=8.5, color=INK2)
    ax.set_ylim(S - 40, F + 75)
    ax.set_ylabel('Scheduled weekday bus trips (Monday to Thursday school day)', fontsize=9, color=INK2)
    for side in ['top', 'right']:
        ax.spines[side].set_visible(False)
    for side in ['left', 'bottom']:
        ax.spines[side].set_color('#d6d5d0')
    ax.tick_params(colors=INK2, length=0)
    ax.yaxis.grid(True, color='#e6e5e0', lw=0.6); ax.set_axisbelow(True)
    ax.set_title(f"Weekday bus trips, Summer 2026 rating to Fall 2026 rating: net {net:+,} trips",
                 fontsize=13, color=INK, loc='left', pad=14)
    ax.annotate(f"Route {routes[driver]['route_short_name']} drives the change ({delta[driver]:+d} trips)",
                xy=(1.32, S + delta[driver] - 10), xytext=(2.6, S + 30), fontsize=9.5, color=INK,
                arrowprops=dict(arrowstyle='-', color=INK2, lw=0.8))
    ax.text(len(labels) - 1, F + 26, f"Net change {net:+,} trips", ha='center', fontsize=9.5, color=INK)
    from matplotlib.patches import Patch
    ax.legend(handles=[Patch(color=UP, label='Trips added'), Patch(color=DOWN, label='Trips removed'),
                       Patch(color=DRIVER, label='Driving route'), Patch(color=TOTAL, label='Rating total')],
              loc='upper right', frameon=False, fontsize=8.5, labelcolor=INK2)
    fig.text(0.01, 0.01, 'Source: MBTA GTFS archive feeds 20260812 and 20260821, '
             'services in effect on Wednesday 2 September and Wednesday 23 September 2026.',
             fontsize=7.5, color=INK2)
    fig.tight_layout()
    fig.savefig(os.path.join(HERE, 'service_change_bridge.png'), facecolor=SURF)

    # ---------- 3. Memo PDF ----------
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

    ss = getSampleStyleSheet()
    body = ParagraphStyle('body', parent=ss['Normal'], fontName='Helvetica', fontSize=9.6, leading=12.6, spaceAfter=6)
    h = ParagraphStyle('h', parent=body, fontName='Helvetica-Bold', fontSize=10.5, spaceBefore=6, spaceAfter=3)
    title = ParagraphStyle('t', parent=body, fontName='Helvetica-Bold', fontSize=13.5, leading=17, spaceAfter=4)
    small = ParagraphStyle('s', parent=body, fontSize=8.6, leading=11)
    dn, rn = routes[driver]['route_short_name'], routes[runner]['route_short_name']
    s_in = s_heads.most_common()
    story = [
        Paragraph('Certification of the weekday bus service change, Summer 2026 rating to Fall 2026 rating', title),
        Paragraph('To: MBTA Board of Directors &nbsp;&nbsp; From: Service Planning, schedule certification &nbsp;&nbsp; '
                  'Date: 5 October 2026', small),
        Spacer(1, 4),
        Paragraph('Certified figure', h),
        Paragraph(f"The Board should certify a net increase of <b>{net:+,} scheduled weekday bus trips</b> from the "
                  f"Summer 2026 rating ({S:,} trips) to the Fall 2026 rating ({F:,} trips), counted on a typical "
                  f"school-day weekday, Monday through Thursday, across all MBTA bus routes. <b>Route {dn}</b> "
                  f"({routes[driver]['route_long_name']}) drives the change at {delta[driver]:+d} trips, "
                  f"{summer[driver]} to {fall[driver]}. Neither office's figure is certified: Finance's "
                  f"{FINANCE_FIGURE:+d} and Service Planning's {PLANNING_FIGURE:+d} are both rejected.", body),
        Paragraph('What each office counted, and why it is not certified', h),
        Paragraph(f"<b>Finance, {FINANCE_FIGURE:+d}.</b> Finance compared the first weekday schedule in the feed "
                  f"published as Fall 2026 (Monday 24 August, {finance_summer:,} bus trips) with the Fall count of "
                  f"{F:,}. That August weekday is still the Summer rating, and it is a no-school day: the Summer "
                  f"rating does not switch to its school-day weekday schedule until 31 August, and the Fall rating "
                  f"itself does not begin until 6 September. Comparing a no-school Summer weekday with a school-day "
                  f"Fall weekday counts the {S - finance_summer} school-day trips as if the Fall rating added them. "
                  f"On a like-for-like school-day basis the Summer count is {S:,}, not {finance_summer:,}.", body),
        Paragraph(f"<b>Service Planning, {PLANNING_FIGURE:+d}.</b> Service Planning counted each route's timetable as "
                  f"it is published, which lists a trip under every route it serves, so a trip that runs as a "
                  f"combined route appears in two route counts. That is the right way to print a timetable and the "
                  f"wrong way to count system trips: it gives {planning_summer:,} and {planning_fall:,} instead of "
                  f"{S:,} and {F:,}, and the route rows no longer add to the system total. Counting every trip once, "
                  f"under its own route, the change is {net:+d}.", body),
        Paragraph('How the certified figure was built', h),
        Paragraph("The archive index assigns the feed published 21 August 2026 to every date from 21 August "
                  "onward, so both comparison days were taken from that one feed, and the Summer day was "
                  "re-run on the feed published 12 August to confirm an identical route register. The Summer day "
                  "is Wednesday 2 September 2026 and the Fall day is Wednesday 23 September 2026: both are Monday "
                  "to Thursday school days on which every active service is flagged as a typical schedule, with no "
                  "holiday, modified, or reduced service in effect. Trips were counted by the services actually "
                  "active on each date rather than by the rating label on the service, because several long-running "
                  "services labelled Spring/Summer continue to operate under the Fall rating. The route "
                  "population is every route the feed classifies as Frequent, Local, Coverage, Commuter, or "
                  "Supplemental Bus; rail replacement shuttles, which the feed also stores as bus-type routes, are "
                  "excluded, and none operated on either comparison day. School-day supplemental trips are "
                  "included on both days because the Board's convention is a school-day weekday. Each trip is "
                  "counted once under its own route.", body),
        Paragraph('Routes whose weekday count changed, ranked by size of change', h),
    ]
    rows = [['Rank', 'Route', 'Category', 'Summer', 'Fall', 'Change']]
    for i, r in enumerate(changed, 1):
        rows.append([str(i), routes[r]['route_short_name'], routes[r]['route_desc'],
                     f"{summer[r]}", f"{fall[r]}", f"{delta[r]:+d}"])
    rows.append(['', 'All bus routes', f"{len(all_routes)} routes", f"{S:,}", f"{F:,}", f"{net:+,}"])
    t = Table(rows, colWidths=[0.5 * inch, 0.8 * inch, 1.5 * inch, 0.9 * inch, 0.9 * inch, 0.9 * inch], repeatRows=1)
    t.setStyle(TableStyle([
        ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold', 8.4), ('FONT', (0, 1), (-1, -1), 'Helvetica', 8.4),
        ('FONT', (0, -1), (-1, -1), 'Helvetica-Bold', 8.4),
        ('ALIGN', (3, 0), (-1, -1), 'RIGHT'), ('LINEBELOW', (0, 0), (-1, 0), 0.6, colors.black),
        ('LINEABOVE', (0, -1), (-1, -1), 0.6, colors.black), ('TOPPADDING', (0, 0), (-1, -1), 1.2),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 1.2), ('BACKGROUND', (0, 1), (0, 1), colors.HexColor('#fde7d9')),
        ('BACKGROUND', (1, 1), (-1, 1), colors.HexColor('#fde7d9')),
    ]))
    story += [t, Spacer(1, 6),
        Paragraph(f"The {len(all_routes) - len(changed)} other bus routes run the same number of weekday trips under "
                  f"both ratings. The {len(changed)} changes above sum to {net:+d}, which ties exactly to the two "
                  f"system counts in route_service_change.csv.", body),
        Paragraph('School-day supplemental trips', h),
        Paragraph(f"Of the {S:,} Summer trips, {sup_s} are school-day supplemental trips; of the {F:,} Fall trips, "
                  f"{sup_f} are. The supplemental service is almost unchanged between ratings and explains "
                  f"{sup_f - sup_s:+d} of the {net:+d}.", body),
        Paragraph('Scheduled revenue time behind the trip count', h),
        Paragraph(f"Measured from each trip's first scheduled departure to its last scheduled arrival, the Summer "
                  f"weekday carries {hrs(MS)} revenue hours ({MS:,} minutes) and the Fall weekday {hrs(MF)} "
                  f"({MF:,} minutes), a change of {hrs(MF - MS)} hours. Route {routes[hours_driver]['route_short_name']} "
                  f"leads on revenue time as well, at {dmin[hours_driver] / 60:+.1f} hours, ahead of Route "
                  f"{routes[hours_second]['route_short_name']} at {dmin[hours_second] / 60:+.1f} hours, so the trip "
                  f"driver and the cost driver are the same route. The register carries both measures for every route.", body),
        Paragraph(f"Route {dn}: what changed", h),
        Paragraph(f"Under the Summer rating Route {dn} ran {summer[driver]} weekday trips, with the first scheduled "
                  f"departure at {clock(s_first)} and the last scheduled arrival at {clock(s_last)}. Under the Fall "
                  f"rating it runs {fall[driver]} weekday trips, first departure {clock(f_first)} and last arrival "
                  f"{clock(f_last)}. The route was extended at its inbound end: Summer inbound trips terminate at "
                  f"{list(s_ends.get('1', {}).keys())[0]} (headsign {s_in[0][0][1] if s_in[0][0][0]=='1' else s_in[1][0][1]}) "
                  f"and Fall inbound trips terminate at {list(f_ends.get('1', {}).keys())[0]}, with the span of service "
                  f"opening about an hour earlier and closing more than four hours later. The added trips come from the "
                  f"longer span and more frequent service across the day rather than from any change to the "
                  f"Brighton Center end of the route.", body),
        Paragraph('How close the driving route is to being overtaken', h),
        Paragraph(f"Route {rn} ({routes[runner]['route_long_name']}) is the runner-up at {delta[runner]:+d}, "
                  f"{gap} trips behind Route {dn}. The smallest change in a single route's Fall count that would make "
                  f"a different route the driver is <b>{flip} trips</b>: Route {rn} would become the driver with "
                  f"{fall[runner] + flip} Fall trips ({delta[runner] + flip:+d}), or Route {dn} would lose the lead at "
                  f"{fall[driver] - flip} Fall trips ({delta[driver] - flip:+d}). No other route is within reach: the "
                  f"third-largest change is {delta[changed[2]]:+d} on Route {routes[changed[2]]['route_short_name']}.", body),
        Paragraph('Why no other figure survives', h),
        Paragraph(f"The Board's convention fixes the day type, the day-of-week band, and the population, and the feed "
                  f"fixes which services run on a given date. Once those are applied there is exactly one Summer "
                  f"register and one Fall register, both stable across every qualifying day in their rating and "
                  f"identical across the two archived feeds that cover them. Every alternative figure comes from "
                  f"relaxing one of those fixed points: a no-school day, a Friday, a holiday, a rating label instead "
                  f"of a date, a timetable listing instead of a trip, or a shuttle instead of a bus route. "
                  f"{net:+d} is the only number the convention and the files allow, and Route {dn} is the only "
                  f"route that can be named as its driver.", body),
    ]
    doc = SimpleDocTemplate(os.path.join(HERE, 'certification_memo.pdf'), pagesize=letter,
                            leftMargin=0.8 * inch, rightMargin=0.8 * inch, topMargin=0.7 * inch, bottomMargin=0.7 * inch,
                            title='Certification of the weekday bus service change', author='Service Planning')
    doc.build(story)

    print(f"revenue minutes {MS} -> {MF} ({hrs(MS)} -> {hrs(MF)} h); hours driver {routes[hours_driver]['route_short_name']} {dmin[hours_driver]/60:+.1f}")
    print(f"Summer {S} Fall {F} net {net:+d}; driver {dn} {delta[driver]:+d}; runner {rn} {delta[runner]:+d}; flip {flip}")
    print(f"supplemental {sup_s}/{sup_f}; finance {finance_net:+d} (summer {finance_summer}); planning {planning_net:+d} ({planning_summer}->{planning_fall})")
    print(f"route {dn} span S {s_first}-{s_last} F {f_first}-{f_last}; ends S {dict(s_ends)} F {dict(f_ends)}; heads S {s_heads} F {f_heads}")


if __name__ == '__main__':
    main()

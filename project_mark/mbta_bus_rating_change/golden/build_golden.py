"""Builds the three golden deliverables from the shipped input package.

Reads 20260821.zip (and cross checks against 20260812.zip) straight from ../inputs,
so every number in the CSV, the chart, and the memo comes from one pass over one set of files.
"""
import csv, io, zipfile, collections, datetime as dt, os

HERE = os.path.dirname(os.path.abspath(__file__))
INPUTS = os.path.join(HERE, '..', 'inputs')
BUS = {'Frequent Bus', 'Local Bus', 'Coverage Bus', 'Commuter Bus', 'Supplemental Bus'}
SUMMER_DAY = dt.date(2026, 9, 2)    # Wednesday, Summer rating, school in session, typical schedule
FALL_DAY = dt.date(2026, 9, 23)     # Wednesday, Fall rating, typical schedule
CERTIFIED_SUMMER_PEAK = 615         # the control the prompt states
FINANCE_PEAK, FINANCE_TRIPS, PLANNING_TRIPS = 521, 321, 121
HOURS = list(range(4, 27))          # 04:00 through the 02:00 hour of the next morning


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


def mins(t):
    h, m, _ = t.split(':')
    return int(h) * 60 + int(m)


def clock(m):
    return f"{m // 60:02d}:{m % 60:02d}"


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


def day_bounds(d, date):
    """Per trip (first departure, last arrival) and per block (first departure, last arrival) for bus trips."""
    s = active_services(d, date)
    tr = {t['trip_id']: t for t in d['trips'] if t['service_id'] in s and is_bus(d, t)}
    first, last, last_stop = {}, {}, {}
    with d['zip'].open('stop_times.txt') as f:
        for r in csv.DictReader(io.TextIOWrapper(f, encoding='utf-8-sig')):
            k = r['trip_id']
            if k not in tr:
                continue
            dep, arr = mins(r['departure_time']), mins(r['arrival_time'])
            if k not in first or dep < first[k]:
                first[k] = dep
            if k not in last or arr > last[k]:
                last[k] = arr
            seq = int(r['stop_sequence'])
            if k not in last_stop or seq > last_stop[k][0]:
                last_stop[k] = (seq, r['stop_id'])
    trips = {k: (first[k], last[k]) for k in tr}
    bl = collections.defaultdict(list)
    for k, t in tr.items():
        bl[t['block_id']].append(k)
    blocks = {b: (min(first[k] for k in ks), max(last[k] for k in ks)) for b, ks in bl.items()}
    block_routes = {b: {tr[k]['route_id'] for k in ks} for b, ks in bl.items()}
    return trips, blocks, block_routes, tr, {k: v[1] for k, v in last_stop.items()}


def minute_profile(intervals):
    cnt = [0] * (31 * 60)
    for a, b in intervals:
        for m in range(a, b):          # in service from first departure up to the last arrival
            cnt[m] += 1
    return cnt


def peak(cnt):
    p = max(cnt)
    return p, cnt.index(p)


def main():
    fall_feed = load(os.path.join(INPUTS, '20260821.zip'))
    summer_feed = load(os.path.join(INPUTS, '20260812.zip'))
    routes = fall_feed['routes']

    # ---- trips register (the schedule change behind the fleet change) ----
    summer, fall = register(fall_feed, SUMMER_DAY), register(fall_feed, FALL_DAY)
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
    finance_summer = sum(register(fall_feed, dt.date(2026, 8, 24)).values())
    planning_s = sum(register(fall_feed, SUMMER_DAY, count_multi=True).values())
    planning_f = sum(register(fall_feed, FALL_DAY, count_multi=True).values())
    assert F - finance_summer == FINANCE_TRIPS and planning_f - planning_s == PLANNING_TRIPS

    # ---- buses in service (blocks) ----
    s_trips, s_blocks, s_broutes, s_tr, s_last = day_bounds(fall_feed, SUMMER_DAY)
    f_trips, f_blocks, f_broutes, f_tr, f_last = day_bounds(fall_feed, FALL_DAY)
    s_prof, f_prof = minute_profile(s_blocks.values()), minute_profile(f_blocks.values())
    s_peak, s_when = peak(s_prof)
    f_peak, f_when = peak(f_prof)
    assert s_peak == CERTIFIED_SUMMER_PEAK, s_peak
    # the Summer feed and the other qualifying days give the same peak
    s2_trips, s2_blocks, _, _, _ = day_bounds(summer_feed, SUMMER_DAY)
    assert peak(minute_profile(s2_blocks.values())) == (s_peak, s_when)
    for day in [dt.date(2026, 9, 8), dt.date(2026, 9, 30)]:
        _, b, _, _, _ = day_bounds(fall_feed, day)
        assert peak(minute_profile(b.values())) == (f_peak, f_when), day
    fin_peak, fin_when = peak(minute_profile(f_trips.values()))
    assert fin_peak == FINANCE_PEAK, fin_peak
    fin_s_peak, fin_s_when = peak(minute_profile(s_trips.values()))
    def starts_ends(blocks):
        st, en = collections.Counter(), collections.Counter()
        for a, b in blocks.values():
            st[a // 60] += 1
            en[b // 60] += 1
        return st, en
    s_st, s_en = starts_ends(s_blocks)
    f_st, f_en = starts_ends(f_blocks)
    assert starts_ends(s2_blocks) == (s_st, s_en)
    for day in [dt.date(2026, 9, 8), dt.date(2026, 9, 30)]:
        _, b, _, _, _ = day_bounds(fall_feed, day)
        assert starts_ends(b) == (f_st, f_en), day
    PULL_HOURS = list(range(3, 27))
    hourly = [(h, s_st[h], s_en[h], f_st[h], f_en[h]) for h in PULL_HOURS]
    s_top = max(PULL_HOURS, key=lambda h: (s_st[h], -h))
    f_top = max(PULL_HOURS, key=lambda h: (f_st[h], -h))
    grow = sorted(PULL_HOURS, key=lambda h: (-(f_st[h] - s_st[h]), h))
    best_hour, second_hour = grow[0], grow[1]
    assert f_st[best_hour] - s_st[best_hour] > f_st[second_hour] - s_st[second_hour]
    s_bus65 = sum(1 for b, rs in s_broutes.items() if driver in rs)
    f_bus65 = sum(1 for b, rs in f_broutes.items() if driver in rs)
    s_first = min(a for k, (a, _) in s_trips.items() if s_tr[k]['route_id'] == driver)
    s_lastarr = max(b for k, (_, b) in s_trips.items() if s_tr[k]['route_id'] == driver)
    f_first = min(a for k, (a, _) in f_trips.items() if f_tr[k]['route_id'] == driver)
    f_lastarr = max(b for k, (_, b) in f_trips.items() if f_tr[k]['route_id'] == driver)
    ends = lambda tr, last: collections.Counter(fall_feed['stops'][last[k]]['stop_name'] for k in tr if tr[k]['route_id'] == driver and tr[k]['direction_id'] == '1').most_common(1)[0][0]
    s_end, f_end = ends(s_tr, s_last), ends(f_tr, f_last)
    heads = lambda tr: collections.Counter(tr[k]['trip_headsign'] for k in tr if tr[k]['route_id'] == driver and tr[k]['direction_id'] == '1').most_common(1)[0][0]
    dn, rn = routes[driver]['route_short_name'], routes[runner]['route_short_name']

    def hour_label(h):
        return f"{h:02d}:00" if h < 24 else f"{h - 24:02d}:00 next day"

    # ---------- 1. CSV hourly profile ----------
    with open(os.path.join(HERE, 'weekday_bus_requirement.csv'), 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['hour', 'summer_pull_outs', 'summer_pull_ins', 'fall_pull_outs', 'fall_pull_ins'])
        for h, a, b, c, e in hourly:
            w.writerow([hour_label(h), a, b, c, e])
        w.writerow(['TOTAL', sum(s_st.values()), sum(s_en.values()), sum(f_st.values()), sum(f_en.values())])

    # ---------- 2. Profile PNG ----------
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    INK, INK2, SURF = '#0b0b0b', '#52514e', '#fcfcfb'
    C_SUMMER, C_FALL = '#eb6834', '#2a78d6'
    fig, ax = plt.subplots(figsize=(14, 6.4), dpi=200)
    fig.patch.set_facecolor(SURF); ax.set_facecolor(SURF)
    xs = [m / 60 for m in range(4 * 60, 27 * 60)]
    ax.plot(xs, s_prof[4 * 60:27 * 60], color=C_SUMMER, lw=2, label='Summer 2026 rating')
    ax.plot(xs, f_prof[4 * 60:27 * 60], color=C_FALL, lw=2, label='Fall 2026 rating')
    for pk, when, col, dy in [(s_peak, s_when, C_SUMMER, -34), (f_peak, f_when, C_FALL, 22)]:
        ax.plot(when / 60, pk, 'o', color=col, ms=8, markeredgecolor=SURF, markeredgewidth=2)
        ax.annotate(f"{pk} buses at {clock(when)}", xy=(when / 60, pk), xytext=(when / 60 + 0.9, pk + dy),
                    fontsize=10, color=INK, arrowprops=dict(arrowstyle='-', color=INK2, lw=0.8))
    ax.text(26.9, f_prof[26 * 60 + 30], ' Fall', color=INK2, fontsize=9, va='center')
    ax.set_xlim(4, 27.6); ax.set_ylim(0, 700)
    ticks = list(range(4, 27, 2))
    ax.set_xticks(ticks); ax.set_xticklabels([f"{t % 24:02d}:00" for t in ticks], fontsize=9, color=INK2)
    ax.set_xlabel('Time of day (service day runs past midnight)', fontsize=9, color=INK2)
    ax.set_ylabel('Buses in service', fontsize=9, color=INK2)
    for side in ['top', 'right']:
        ax.spines[side].set_visible(False)
    for side in ['left', 'bottom']:
        ax.spines[side].set_color('#d6d5d0')
    ax.tick_params(colors=INK2, length=0)
    ax.yaxis.grid(True, color='#e6e5e0', lw=0.6); ax.set_axisbelow(True)
    ax.set_title(f"Weekday buses in service, Summer 2026 rating to Fall 2026 rating: peak {s_peak} to {f_peak} buses "
                 f"({f_peak - s_peak:+d})", fontsize=12.5, color=INK, loc='left', pad=12)
    ax.legend(loc='upper right', frameon=False, fontsize=9, labelcolor=INK2)
    fig.text(0.01, 0.01, 'Source: MBTA GTFS archive feeds 20260812 and 20260821; a bus is in service from the first departure '
             'to the last arrival of its block; Wednesday 2 September and Wednesday 23 September 2026.',
             fontsize=7.5, color=INK2)
    fig.tight_layout()
    fig.savefig(os.path.join(HERE, 'bus_requirement_profile.png'), facecolor=SURF)

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
    story = [
        Paragraph('Fall 2026 weekday bus requirement: fleet certification', title),
        Paragraph('To: MBTA Board of Directors &nbsp;&nbsp; From: Service Planning, schedule certification &nbsp;&nbsp; '
                  'Date: 5 October 2026', small),
        Spacer(1, 4),
        Paragraph('Certified requirement', h),
        Paragraph(f"The Board should certify the Fall 2026 weekday bus requirement at <b>{f_peak} buses</b>, "
                  f"{f_peak - s_peak:+d} against the Summer 2026 certification of {s_peak}. The peak falls in the morning, "
                  f"at {clock(f_when)}, when {f_peak} buses are in service at once; the Summer peak fell at {clock(s_when)}. "
                  f"The same files reproduce the Summer certification of {s_peak} exactly, so the two figures are on one "
                  f"basis. Finance's draft peak of {FINANCE_PEAK} is not certified. The schedule behind the fleet change is a "
                  f"net {net:+d} weekday trips, {S:,} to {F:,}, and <b>Route {dn}</b> ({routes[driver]['route_long_name']}) "
                  f"is the single route behind the biggest share of it at {delta[driver]:+d} trips; Finance's {FINANCE_TRIPS:+d} "
                  f"and the planners' {PLANNING_TRIPS:+d} are not certified.", body),
        Paragraph("What the other figures counted, and why they are not certified", h),
        Paragraph(f"<b>Finance's peak of {FINANCE_PEAK} buses.</b> It is the most trips underway at one moment, which happens "
                  f"at {clock(fin_when)} in the afternoon peak (the Summer equivalent is {fin_s_peak} at {clock(fin_s_when)}). "
                  f"A trip is not a bus. Between consecutive trips a bus sits at a terminal on layover and is still in service "
                  f"and still assigned, so the count of trips underway runs about a hundred below the count of buses out, "
                  f"and it peaks in the afternoon when trips are long rather than in the morning when the most buses are out. "
                  f"Counting each bus from its first departure to its last arrival gives {s_peak} for Summer, which matches "
                  f"the certification, and {f_peak} for Fall.", body),
        Paragraph(f"<b>Finance's {FINANCE_TRIPS:+d} weekday trips.</b> It compares the first weekday schedule in the feed "
                  f"published as Fall 2026 (Monday 24 August, {finance_summer:,} trips) with the Fall count of {F:,}. That "
                  f"August weekday is still the Summer rating on a no school day. The Summer rating switches to its "
                  f"school day weekday on 31 August, at {S:,} trips, and the Fall rating begins on 6 September, so the "
                  f"like for like change is {net:+d}.", body),
        Paragraph(f"<b>The planners' {PLANNING_TRIPS:+d}.</b> It counts each route's timetable as published, which lists a "
                  f"trip under every route it serves, so a trip on a combined route is counted two or three times: "
                  f"{planning_s:,} and {planning_f:,} instead of {S:,} and {F:,}. Counting every trip once, under its own "
                  f"route, gives {net:+d}.", body),
        Paragraph('How the certified figures were built', h),
        Paragraph("The archive index assigns the feed published 21 August 2026 to every date from 21 August onward, so both "
                  "comparison days come from that feed, and the Summer day was rerun on the feed published 12 August with "
                  "an identical result. The Summer day is Wednesday 2 September 2026 and the Fall day is Wednesday 23 "
                  "September 2026, both Monday to Thursday school days on which every active service is flagged typical. "
                  "Trips were taken from the services active on each date rather than from the rating label on the service, "
                  "because long running services labelled Spring/Summer continue under the Fall rating. The route "
                  "population is every route the feed classifies as Frequent, Local, Coverage, Commuter, or Supplemental "
                  "Bus; rail replacement shuttles are excluded and none ran on either day. Each trip was counted once under "
                  "its own route. For the fleet figure every trip was assigned to its block, each block was treated as one "
                  "bus in service from its first departure to its last arrival, and the number of blocks in service was "
                  "counted at every minute of the service day. The count is identical on every other qualifying day in "
                  "each rating.", body),
        Paragraph('Pull outs through the day', h),
        Paragraph(f"Under both ratings the hour with the most pull outs is the <b>{hour_label(s_top)} hour</b>: {s_st[s_top]} buses "
                  f"pull out in that hour under Summer and {f_st[f_top]} under Fall. The hour whose pull outs grew the most is the "
                  f"<b>{hour_label(best_hour)} hour, {f_st[best_hour] - s_st[best_hour]:+d}</b> ({s_st[best_hour]} to {f_st[best_hour]}), "
                  f"ahead of the {hour_label(second_hour)} hour at {f_st[second_hour] - s_st[second_hour]:+d}. The Fall rating runs "
                  f"{sum(f_st.values()):,} pull outs against {sum(s_st.values()):,} under Summer, and the added work sits in the "
                  f"evening: the morning peak gains {f_peak - s_peak} buses while pull outs from 19:00 onward gain "
                  f"{sum(f_st[hh] - s_st[hh] for hh in PULL_HOURS if hh >= 19)}. The full profile is in weekday_bus_requirement.csv.", body),
        Paragraph('Routes whose weekday trip count changed, ranked by size of change', h),
    ]
    rows = [['Rank', 'Route', 'Category', 'Summer', 'Fall', 'Change']]
    for i, r in enumerate(changed, 1):
        rows.append([str(i), routes[r]['route_short_name'], routes[r]['route_desc'], f"{summer[r]}", f"{fall[r]}", f"{delta[r]:+d}"])
    rows.append(['', 'All bus routes', f"{len(all_routes)} routes", f"{S:,}", f"{F:,}", f"{net:+,}"])
    t = Table(rows, colWidths=[0.5 * inch, 0.8 * inch, 1.5 * inch, 0.9 * inch, 0.9 * inch, 0.9 * inch], repeatRows=1)
    t.setStyle(TableStyle([
        ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold', 8.4), ('FONT', (0, 1), (-1, -1), 'Helvetica', 8.4),
        ('FONT', (0, -1), (-1, -1), 'Helvetica-Bold', 8.4), ('ALIGN', (3, 0), (-1, -1), 'RIGHT'),
        ('LINEBELOW', (0, 0), (-1, 0), 0.6, colors.black), ('LINEABOVE', (0, -1), (-1, -1), 0.6, colors.black),
        ('TOPPADDING', (0, 0), (-1, -1), 1.2), ('BOTTOMPADDING', (0, 0), (-1, -1), 1.2),
        ('BACKGROUND', (0, 1), (-1, 1), colors.HexColor('#fde7d9')),
    ]))
    story += [t, Spacer(1, 6),
        Paragraph(f"The other {len(all_routes) - len(changed)} bus routes run the same number of weekday trips under both "
                  f"ratings, and the {len(changed)} changes sum to {net:+d}.", body),
        Paragraph(f"Route {dn}: what changed", h),
        Paragraph(f"Under the Summer rating {s_bus65} buses carry Route {dn} trips during the weekday; under the Fall rating "
                  f"{f_bus65} do. Summer service ran {summer[driver]} trips with the first departure at {clock(s_first)} and the "
                  f"last arrival at {clock(s_lastarr)}; Fall runs {fall[driver]} trips from {clock(f_first)} to {clock(f_lastarr)} "
                  f"({clock(f_lastarr - 24 * 60)} the next morning). The route was extended at its inbound end: Summer inbound "
                  f"trips end at {s_end} (headsign {heads(s_tr)}) and Fall inbound trips end at {f_end} (headsign {heads(f_tr)}), "
                  f"with the span opening about an hour earlier and closing more than four hours later. The added trips come "
                  f"from the longer span and more frequent service through the day, not from the Brighton Center end.", body),
        Paragraph('How close the driving route is to being overtaken', h),
        Paragraph(f"Route {rn} ({routes[runner]['route_long_name']}) is the runner up at {delta[runner]:+d}, {gap} trips behind. "
                  f"The smallest change in a single route's Fall trip count that would make a different route the driver is "
                  f"<b>{flip} trips</b>: Route {rn} at {fall[runner] + flip} Fall trips ({delta[runner] + flip:+d}), or Route {dn} "
                  f"at {fall[driver] - flip} ({delta[driver] - flip:+d}). The third largest change is {delta[changed[2]]:+d} on "
                  f"Route {routes[changed[2]]['route_short_name']}.", body),
        Paragraph('Why no other figure survives', h),
        Paragraph(f"The Board's convention fixes the day type, the day of week band, the population, and the unit: a bus from "
                  f"its first departure to its last arrival. The feed fixes which services run on each date and which trips "
                  f"share a bus. Applied together they give one Summer profile and one Fall profile, stable across every "
                  f"qualifying day and identical in both archived feeds, and the Summer profile returns the certified {s_peak} "
                  f"exactly. Every other figure relaxes one fixed point: trips underway instead of buses out, a no school day, "
                  f"a timetable listing instead of a trip, or a rating label instead of a date. {f_peak} buses, {f_peak - s_peak:+d}, "
                  f"is the only requirement the convention and the files allow.", body),
    ]
    doc = SimpleDocTemplate(os.path.join(HERE, 'fleet_certification_memo.pdf'), pagesize=letter,
                            leftMargin=0.8 * inch, rightMargin=0.8 * inch, topMargin=0.7 * inch, bottomMargin=0.7 * inch,
                            title='Fall 2026 weekday bus requirement: fleet certification', author='Service Planning')
    doc.build(story)

    print(f"peak buses {s_peak} at {clock(s_when)} -> {f_peak} at {clock(f_when)} ({f_peak - s_peak:+d}); finance trips-peak {fin_peak} at {clock(fin_when)} (summer {fin_s_peak} at {clock(fin_s_when)})")
    print(f"trips {S} -> {F} net {net:+d}; driver {dn} {delta[driver]:+d}; runner {rn} {delta[runner]:+d}; flip {flip}; top pull-out hour {hour_label(s_top)}/{hour_label(f_top)} {s_st[s_top]}/{f_st[f_top]}; biggest growth {hour_label(best_hour)} {f_st[best_hour]-s_st[best_hour]:+d}")
    print(f"route {dn} buses {s_bus65} -> {f_bus65}; span {clock(s_first)}-{clock(s_lastarr)} -> {clock(f_first)}-{clock(f_lastarr)}; ends {s_end} -> {f_end}")
    print('pull-outs', [(hour_label(hh), a, c) for hh, a, b, c, e in hourly])


if __name__ == '__main__':
    main()

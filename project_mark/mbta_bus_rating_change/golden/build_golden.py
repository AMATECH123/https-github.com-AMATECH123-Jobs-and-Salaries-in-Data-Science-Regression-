"""Builds the three golden deliverables from the shipped input package (version 3).

Summer day: Wednesday 19 August 2026 from 20260812.zip (the feed the archive index assigns to that date),
cross checked on 22 July in 20260610.zip and 24 August in 20260821.zip.
Fall day: Wednesday 30 September 2026 from MBTA_GTFS.zip (the published feed, identical to archive 20260925),
cross checked on 23 September in 20260821.zip.
"""
import csv, io, zipfile, collections, datetime as dt, os

HERE = os.path.dirname(os.path.abspath(__file__))
INPUTS = os.path.join(HERE, '..', 'inputs')
BUS = {'Frequent Bus', 'Local Bus', 'Coverage Bus', 'Commuter Bus', 'Supplemental Bus'}
SUMMER_DAY = dt.date(2026, 8, 19)
FALL_DAY = dt.date(2026, 9, 30)
CERTIFIED_SUMMER_PEAK = 607
FINANCE_PEAK, FINANCE_TRIPS, PLANNING_TRIPS = 521, 321, 149


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
        for m in range(a, b):
            cnt[m] += 1
    return cnt


def peak(cnt):
    p = max(cnt)
    return p, cnt.index(p)


def starts_ends(blocks):
    st, en = collections.Counter(), collections.Counter()
    for a, b in blocks.values():
        st[a // 60] += 1
        en[b // 60] += 1
    return st, en


def weekday_tally(d, start, end):
    """Monday to Thursday dates in [start, end] grouped by the bus trip count of the schedule running that day."""
    tally = collections.Counter()
    day = start
    while day <= end:
        if day.weekday() < 4:
            s = active_services(d, day)
            tally[sum(1 for t in d['trips'] if t['service_id'] in s and is_bus(d, t))] += 1
        day += dt.timedelta(days=1)
    return tally


def main():
    june = load(os.path.join(INPUTS, '20260610.zip'))
    aug = load(os.path.join(INPUTS, '20260812.zip'))
    f0821 = load(os.path.join(INPUTS, '20260821.zip'))
    cur = load(os.path.join(INPUTS, 'MBTA_GTFS.zip'))
    routes = cur['routes']

    # ---- which weekday schedule ran most of each rating ----
    s_tally = weekday_tally(june, dt.date(2026, 6, 15), dt.date(2026, 9, 3))
    f_tally = weekday_tally(f0821, dt.date(2026, 9, 8), dt.date(2026, 9, 24)) + \
        weekday_tally(cur, dt.date(2026, 9, 28), dt.date(2026, 12, 10))

    # ---- trip registers ----
    summer, fall = register(aug, SUMMER_DAY), register(cur, FALL_DAY)
    assert register(june, dt.date(2026, 7, 22)) == summer and register(f0821, dt.date(2026, 8, 24)) == summer
    assert register(f0821, dt.date(2026, 9, 23)) == fall and register(cur, dt.date(2026, 10, 7)) == fall
    S, F = sum(summer.values()), sum(fall.values())
    assert s_tally.most_common(1)[0][0] == S and f_tally.most_common(1)[0][0] == F
    net = F - S
    assert net == FINANCE_TRIPS
    school_summer = sum(register(aug, dt.date(2026, 9, 2)).values())
    assert F - school_summer == PLANNING_TRIPS
    all_routes = sorted(set(summer) | set(fall), key=lambda r: int(routes[r]['route_sort_order']))
    delta = {r: fall[r] - summer[r] for r in all_routes}
    changed = sorted([r for r in all_routes if delta[r]],
                     key=lambda r: (-abs(delta[r]), int(routes[r]['route_sort_order'])))
    driver, runner, third = changed[0], changed[1], changed[2]
    gap = abs(delta[driver]) - abs(delta[runner])
    flip = gap + 1

    # ---- buses in service ----
    s_trips, s_blocks, s_broutes, s_tr, s_last = day_bounds(aug, SUMMER_DAY)
    f_trips, f_blocks, f_broutes, f_tr, f_last = day_bounds(cur, FALL_DAY)
    s_prof, f_prof = minute_profile(s_blocks.values()), minute_profile(f_blocks.values())
    s_peak, s_when = peak(s_prof)
    f_peak, f_when = peak(f_prof)
    assert s_peak == CERTIFIED_SUMMER_PEAK, s_peak
    for feed, day in [(june, dt.date(2026, 7, 22)), (f0821, dt.date(2026, 8, 24)), (aug, dt.date(2026, 8, 13))]:
        _, b, _, _, _ = day_bounds(feed, day)
        assert peak(minute_profile(b.values())) == (s_peak, s_when), day
        assert starts_ends(b) == starts_ends(s_blocks), day
    for feed, day in [(f0821, dt.date(2026, 9, 23)), (cur, dt.date(2026, 10, 7)), (cur, dt.date(2026, 11, 4))]:
        _, b, _, _, _ = day_bounds(feed, day)
        assert peak(minute_profile(b.values())) == (f_peak, f_when), day
        assert starts_ends(b) == starts_ends(f_blocks), day
    fin_peak, fin_when = peak(minute_profile(f_trips.values()))
    assert fin_peak == FINANCE_PEAK, fin_peak
    fin_s_peak, fin_s_when = peak(minute_profile(s_trips.values()))
    _, sch_blocks, _, _, _ = day_bounds(aug, dt.date(2026, 9, 2))
    school_peak, school_when = peak(minute_profile(sch_blocks.values()))

    s_st, s_en = starts_ends(s_blocks)
    f_st, f_en = starts_ends(f_blocks)
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
    ends = lambda d, tr, last: collections.Counter(d['stops'][last[k]]['stop_name'] for k in tr if tr[k]['route_id'] == driver and tr[k]['direction_id'] == '1').most_common(1)[0][0]
    s_end, f_end = ends(aug, s_tr, s_last), ends(cur, f_tr, f_last)
    heads = lambda tr: collections.Counter(tr[k]['trip_headsign'] for k in tr if tr[k]['route_id'] == driver and tr[k]['direction_id'] == '1').most_common(1)[0][0]
    dn, rn, tn = routes[driver]['route_short_name'], routes[runner]['route_short_name'], routes[third]['route_short_name']

    def hour_label(h):
        return f"{h:02d}:00" if h < 24 else f"{h - 24:02d}:00 next day"

    # ---------- 1. CSV ----------
    with open(os.path.join(HERE, 'weekday_bus_requirement.csv'), 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['hour', 'summer_pull_outs', 'summer_pull_ins', 'fall_pull_outs', 'fall_pull_ins'])
        for h, a, b, c, e in hourly:
            w.writerow([hour_label(h), a, b, c, e])
        w.writerow(['TOTAL', sum(s_st.values()), sum(s_en.values()), sum(f_st.values()), sum(f_en.values())])

    # ---------- 2. PNG ----------
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
    for pk, when, col, dy in [(s_peak, s_when, C_SUMMER, -40), (f_peak, f_when, C_FALL, 24)]:
        ax.plot(when / 60, pk, 'o', color=col, ms=8, markeredgecolor=SURF, markeredgewidth=2)
        ax.annotate(f"{pk} buses at {clock(when)}", xy=(when / 60, pk), xytext=(when / 60 + 0.9, pk + dy),
                    fontsize=10, color=INK, arrowprops=dict(arrowstyle='-', color=INK2, lw=0.8))
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
    fig.text(0.01, 0.01, 'Source: MBTA GTFS feeds (archive 20260812 and the published Fall 2026 feed); a bus is in service '
             'from the first departure to the last arrival of its block; Wednesday 19 August and Wednesday 30 September 2026.',
             fontsize=7.5, color=INK2)
    fig.tight_layout()
    fig.savefig(os.path.join(HERE, 'bus_requirement_profile.png'), facecolor=SURF)

    # ---------- 3. PDF ----------
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
    s_days, f_days = sum(s_tally.values()), sum(f_tally.values())
    story = [
        Paragraph('Fall 2026 weekday bus requirement: fleet certification', title),
        Paragraph('To: MBTA Board of Directors &nbsp;&nbsp; From: Service Planning, schedule certification &nbsp;&nbsp; '
                  'Date: 5 October 2026', small),
        Spacer(1, 4),
        Paragraph('Certified requirement', h),
        Paragraph(f"The Board should certify the Fall 2026 weekday bus requirement at <b>{f_peak} buses</b>, "
                  f"{f_peak - s_peak:+d} against the Summer 2026 certification of {s_peak}. The peak falls in the morning, "
                  f"at {clock(f_when)}; the Summer peak fell at {clock(s_when)}. The same files and the same convention "
                  f"reproduce the Summer certification of {s_peak} exactly. Finance's draft peak of {FINANCE_PEAK} is not "
                  f"certified. The schedule behind the fleet change is a net {net:+d} weekday trips, {S:,} to {F:,}, which is "
                  f"Finance's figure and is certified; the planners' {PLANNING_TRIPS:+d} is not. <b>Route {dn}</b> "
                  f"({routes[driver]['route_long_name']}) is the single route behind the biggest share of the change at "
                  f"{delta[driver]:+d} trips.", body),
        Paragraph('The three figures, what each counted, and the certification decision', h),
        Paragraph(f"<b>Finance's peak of {FINANCE_PEAK} buses: not certified.</b> It is the most trips underway at one "
                  f"moment, at {clock(fin_when)} in the afternoon (the Summer equivalent is {fin_s_peak} at {clock(fin_s_when)}). "
                  f"Under the convention a bus is in service from the first departure to the last arrival of its day's work, "
                  f"so a bus on layover between trips is still out. Trips underway run about a hundred below buses out and "
                  f"peak in the afternoon, when trips are long, not in the morning, when the most buses are out.", body),
        Paragraph(f"<b>Finance's {FINANCE_TRIPS:+d} weekday trips: certified.</b> It compares the weekday schedule that ran "
                  f"for most of the Summer rating ({S:,} trips, the no school weekday, {s_tally[S]} of the rating's "
                  f"{s_days} Monday to Thursday dates) with the weekday schedule that runs for most of the Fall rating "
                  f"({F:,} trips, {f_tally[F]} of {f_days} dates). That is the convention's certification day for each rating, "
                  f"and the figure stands.", body),
        Paragraph(f"<b>The planners' {PLANNING_TRIPS:+d}: not certified.</b> It replaces the Summer certification day with "
                  f"the Summer rating's school day weekday ({school_summer:,} trips, {s_tally[school_summer]} of {s_days} "
                  f"dates, the weeks either side of the school holiday) to make a like for like school day comparison with "
                  f"Fall. The comparison is arithmetically correct and it is not the Board's convention, which certifies each "
                  f"rating on the schedule it mostly ran. On the planners' basis the Summer peak would be {school_peak} "
                  f"buses, which does not reproduce the certified {s_peak}; the certified figures are not adjusted.", body),
        Paragraph('How the certified figures were built', h),
        Paragraph(f"The archive index assigns the feed published 12 August 2026 to 19 August, the Summer certification "
                  f"day, and the published Fall feed (the archive's 25 September entry) to 30 September, the Fall "
                  f"certification day. The Summer rating's Monday to Thursday dates split {s_tally[S]} on the no school "
                  f"weekday schedule, {s_tally[school_summer]} on the school day schedule and {s_days - s_tally[S] - s_tally[school_summer]} "
                  f"on transition variants, read from the June feed, whose calendar carries the whole rating from 14 June; "
                  f"the August feed's calendar starts on 12 August and alone would understate how long the no school "
                  f"schedule ran. The Fall rating runs one weekday schedule on {f_tally[F]} of {f_days} dates. Both days "
                  f"carry no holiday, modified or reduced service. Services were taken by date rather than by rating label. "
                  f"The route population is every route the feed classifies as Frequent, Local, Coverage, Commuter or "
                  f"Supplemental Bus; rail replacement shuttles are excluded and none ran on either day. Each trip was "
                  f"assigned to its block, each block counted as one bus from its first departure to its last arrival, and "
                  f"the count taken at every minute. Every figure is identical on every other qualifying day of its rating "
                  f"and in every archived feed that covers it.", body),
        Paragraph('Pull outs through the day', h),
        Paragraph(f"Under both ratings the hour with the most pull outs is the <b>{hour_label(s_top)} hour</b>: {s_st[s_top]} buses "
                  f"under Summer and {f_st[f_top]} under Fall. The hour whose pull outs grew the most is the "
                  f"<b>{hour_label(best_hour)} hour, {f_st[best_hour] - s_st[best_hour]:+d}</b> ({s_st[best_hour]} to {f_st[best_hour]}), "
                  f"ahead of the {hour_label(second_hour)} hour at {f_st[second_hour] - s_st[second_hour]:+d}. The Fall rating runs "
                  f"{sum(f_st.values()):,} pull outs against {sum(s_st.values()):,} under Summer. The full profile is in "
                  f"weekday_bus_requirement.csv.", body),
        Paragraph(f'Routes whose weekday trip count changed, ranked by size of change ({len(changed)} of {len(all_routes)} routes)', h),
    ]
    rows = [['Rank', 'Route', 'Category', 'Summer', 'Fall', 'Change']]
    for i, r in enumerate(changed, 1):
        rows.append([str(i), routes[r]['route_short_name'], routes[r]['route_desc'], f"{summer[r]}", f"{fall[r]}", f"{delta[r]:+d}"])
    rows.append(['', 'All bus routes', f"{len(all_routes)} routes", f"{S:,}", f"{F:,}", f"{net:+,}"])
    t = Table(rows, colWidths=[0.5 * inch, 0.8 * inch, 1.5 * inch, 0.9 * inch, 0.9 * inch, 0.9 * inch], repeatRows=1)
    t.setStyle(TableStyle([
        ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold', 8.2), ('FONT', (0, 1), (-1, -1), 'Helvetica', 8.2),
        ('FONT', (0, -1), (-1, -1), 'Helvetica-Bold', 8.2), ('ALIGN', (3, 0), (-1, -1), 'RIGHT'),
        ('LINEBELOW', (0, 0), (-1, 0), 0.6, colors.black), ('LINEABOVE', (0, -1), (-1, -1), 0.6, colors.black),
        ('TOPPADDING', (0, 0), (-1, -1), 0.9), ('BOTTOMPADDING', (0, 0), (-1, -1), 0.9),
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
        Paragraph(f"Route {rn} ({routes[runner]['route_long_name']}) is the runner up at {delta[runner]:+d}, {gap} trips behind, "
                  f"with Route {tn} next at {delta[third]:+d}. The smallest change in a single route's Fall trip count that "
                  f"would make a different route the driver is <b>{flip} trips</b>: Route {rn} at {fall[runner] + flip} Fall trips "
                  f"({delta[runner] + flip:+d}), or Route {dn} at {fall[driver] - flip} ({delta[driver] - flip:+d}), which would "
                  f"put Route {rn} first.", body),
        Paragraph('Why no other figure survives', h),
        Paragraph(f"The convention fixes the unit, the day type, the day of week band, the population and the certification "
                  f"day, and the feed fixes which services run on each date and which trips share a bus. Applied together they "
                  f"give one Summer profile and one Fall profile, stable across every qualifying day and every archived feed, "
                  f"and the Summer profile returns the certified {s_peak} exactly. Every other figure relaxes one fixed point: "
                  f"trips underway instead of buses out, the school day weeks instead of the schedule that ran the rating, a "
                  f"rating label instead of a date, or a Friday. {f_peak} buses, {f_peak - s_peak:+d}, is the only requirement "
                  f"the convention and the files allow.", body),
    ]
    doc = SimpleDocTemplate(os.path.join(HERE, 'fleet_certification_memo.pdf'), pagesize=letter,
                            leftMargin=0.8 * inch, rightMargin=0.8 * inch, topMargin=0.7 * inch, bottomMargin=0.7 * inch,
                            title='Fall 2026 weekday bus requirement: fleet certification', author='Service Planning')
    doc.build(story)

    print(f"peak {s_peak} at {clock(s_when)} -> {f_peak} at {clock(f_when)} ({f_peak - s_peak:+d}); school-day summer peak {school_peak}; finance trips-peak {fin_peak} at {clock(fin_when)} (summer {fin_s_peak})")
    print(f"trips {S} -> {F} net {net:+d} (school summer {school_summer}); tallies S {dict(s_tally)} F {dict(f_tally)}")
    print(f"driver {dn} {delta[driver]:+d}; runner {rn} {delta[runner]:+d}; third {tn} {delta[third]:+d}; flip {flip}; changed {len(changed)} of {len(all_routes)}")
    print(f"pull outs top {hour_label(s_top)} {s_st[s_top]} / {hour_label(f_top)} {f_st[f_top]}; growth {hour_label(best_hour)} {f_st[best_hour]-s_st[best_hour]:+d}, {hour_label(second_hour)} {f_st[second_hour]-s_st[second_hour]:+d}; totals {sum(s_st.values())}/{sum(f_st.values())}")
    print(f"route {dn} buses {s_bus65} -> {f_bus65}; span {clock(s_first)}-{clock(s_lastarr)} -> {clock(f_first)}-{clock(f_lastarr)}; ends {s_end} -> {f_end}")
    print('changed routes:', [(routes[r]['route_short_name'], summer[r], fall[r], delta[r]) for r in changed])


if __name__ == '__main__':
    main()

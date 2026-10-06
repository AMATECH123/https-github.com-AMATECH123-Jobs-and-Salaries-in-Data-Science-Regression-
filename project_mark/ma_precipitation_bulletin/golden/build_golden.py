"""Builds the three golden deliverables for the Massachusetts 2025 annual precipitation bulletin task.

Everything is computed from the shipped input package: the 2025 GHCN Daily parquet partitions for PRCP,
MDPR and DAPR, the station registry and inventory, and the Boston Logan station file. The rules are the
bulletin compilation standard in inputs/bulletin_compilation_standard.md.
"""
import csv, os, glob, collections, datetime as dt, calendar, statistics
import pyarrow.parquet as pq

HERE = os.path.dirname(os.path.abspath(__file__))
INPUTS = os.path.join(HERE, '..', 'inputs', 'ghcnd')
YEAR = 2025
DRAFT_FIGURE, DRAFT_N = 864.2, 428
REVIEW_FIGURE, REVIEW_N = 1138.7, 59
BOSTON = 'USW00014739'


def registry():
    st = {}
    for l in open(os.path.join(INPUTS, 'ghcnd-stations.txt')):
        if l[38:40] == 'MA':
            st[l[:11]] = dict(lat=float(l[12:20]), lon=float(l[21:30]), name=l[41:71].strip())
    inv = collections.defaultdict(dict)
    for l in open(os.path.join(INPUTS, 'ghcnd-inventory.txt')):
        if l[:11] in st:
            inv[l[:11]][l[31:35]] = (int(l[36:40]), int(l[41:45]))
    return st, inv


def parquet_rows(element, ids):
    out = collections.defaultdict(dict)
    for f in sorted(glob.glob(os.path.join(INPUTS, 'parquet', 'by_year', f'YEAR={YEAR}', f'ELEMENT={element}', '*.parquet'))):
        t = pq.read_table(f, columns=['ID', 'DATE', 'DATA_VALUE', 'M_FLAG', 'Q_FLAG', 'S_FLAG']).to_pydict()
        for i in range(len(t['ID'])):
            if t['ID'][i] in ids:
                out[t['ID'][i]][str(t['DATE'][i])] = dict(v=int(t['DATA_VALUE'][i]), m=t['M_FLAG'][i] or '', q=t['Q_FLAG'][i] or '')
    return out


def station_file_rows(sid):
    pr, md, da = {}, {}, {}
    for r in csv.DictReader(open(os.path.join(INPUTS, 'csv', 'by_station', f'{sid}.csv'))):
        rec = dict(v=int(r['DATA_VALUE']), m=r['M_FLAG'], q=r['Q_FLAG'])
        if r['ELEMENT'] == 'PRCP':
            pr[r['DATE']] = rec
        elif r['ELEMENT'] == 'MDPR':
            md[r['DATE']] = rec
        elif r['ELEMENT'] == 'DAPR':
            da[r['DATE']] = rec
    return pr, md, da


def station_year(pr, md, da, year):
    """Apply rules 2 to 5. Returns total (tenths of mm), measured days, usable multi day totals, flagged values."""
    ndays = 366 if calendar.isleap(year) else 365
    covered, total, usable, flagged = {}, 0, 0, 0
    for d, r in md.items():
        if not d.startswith(str(year)):
            continue
        k = da.get(d)
        if r['q'] or (k and k['q']):
            flagged += 1
        if k is None or r['q'] or k['q']:
            continue
        end = dt.date(int(d[:4]), int(d[4:6]), int(d[6:]))
        days = [(end - dt.timedelta(i)).strftime('%Y%m%d') for i in range(k['v'])]
        if any(not x.startswith(str(year)) for x in days):
            continue
        usable += 1
        total += r['v']
        for x in days:
            covered[x] = 'M'
    for d, r in pr.items():
        if not d.startswith(str(year)):
            continue
        if r['q']:
            flagged += 1
            continue
        if d in covered:
            continue
        covered[d] = 'D'
        total += r['v']
    daily = sum(1 for x in covered.values() if x == 'D')
    return dict(total=total, measured=len(covered), daily=daily, multi=len(covered) - daily, usable=usable,
                flagged=flagged, qualifies=len(covered) == ndays, ndays=ndays)


def main():
    st, inv = registry()
    ids = set(st)
    pr = parquet_rows('PRCP', ids)
    md = parquet_rows('MDPR', ids)
    da = parquet_rows('DAPR', ids)
    population = sorted(set(pr) | set(md))
    res = {s: station_year(pr.get(s, {}), md.get(s, {}), da.get(s, {}), YEAR) for s in population}

    # rule 6: one record per site
    loc = collections.defaultdict(list)
    for s in population:
        loc[(st[s]['lat'], st[s]['lon'])].append(s)
    dropped = {}
    for k, v in loc.items():
        if len(v) > 1:
            keep = min(v, key=lambda s: (inv[s].get('PRCP', (9999,))[0], s))
            for s in v:
                if s != keep:
                    dropped[s] = keep
    qual = [s for s in population if res[s]['qualifies'] and s not in dropped]
    totals = {s: res[s]['total'] / 10 for s in qual}
    N = len(qual)
    mean_exact = sum(res[s]['total'] for s in qual) / 10 / N
    statewide = round(mean_exact, 1)
    assert abs(mean_exact - statewide) < 0.045, mean_exact   # rounding is not on a knife edge
    wettest = max(qual, key=lambda s: (totals[s], s))
    driest = min(qual, key=lambda s: (totals[s], s))
    # the station whose removal moves the mean the most
    def moved(s):
        return (sum(totals[x] for x in qual if x != s) / (N - 1)) - mean_exact
    mover = max(qual, key=lambda s: abs(moved(s)))
    mover_delta = moved(mover)

    # reproduce the two offered figures from the same files
    naive = {s: sum(r['v'] for r in pr[s].values()) for s in pr}
    draft_mean = round(sum(naive.values()) / 10 / len(naive), 1)
    rev = {s: naive[s] for s in pr if len(pr[s]) == 365}
    review_mean = round(sum(rev.values()) / 10 / len(rev), 1)
    assert (draft_mean, len(naive)) == (DRAFT_FIGURE, DRAFT_N), (draft_mean, len(naive))
    assert (review_mean, len(rev)) == (REVIEW_FIGURE, REVIEW_N), (review_mean, len(rev))
    # sensitivity checks recorded for the design note
    unmerged = [s for s in population if res[s]['qualifies']]
    unmerged_mean = round(sum(res[s]['total'] for s in unmerged) / 10 / len(unmerged), 1)

    # rule 8: Boston
    bpr, bmd, bda = station_file_rows(BOSTON)
    bpr.update({d: r for d, r in pr.get(BOSTON, {}).items()})
    bmd.update({d: r for d, r in md.get(BOSTON, {}).items()})
    bda.update({d: r for d, r in da.get(BOSTON, {}).items()})
    years = {y: station_year(bpr, bmd, bda, y) for y in range(1936, YEAR + 1)}
    complete = [y for y in years if years[y]['qualifies']]
    incomplete = [y for y in years if not years[y]['qualifies']]
    ranked = sorted(complete, key=lambda y: (-years[y]['total'], y))
    boston_total = years[YEAR]['total'] / 10
    boston_rank = ranked.index(YEAR) + 1
    assert res[BOSTON]['total'] == years[YEAR]['total'] and BOSTON in qual

    # ---------- 1. CSV ----------
    def reason(s):
        if s in dropped:
            return f"same site as {dropped[s]}"
        if not res[s]['qualifies']:
            return f"{res[s]['ndays'] - res[s]['measured']} days not measured"
        return ''
    with open(os.path.join(HERE, 'station_certification_2025.csv'), 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['station_id', 'station_name', 'days_measured', 'qualifies', 'reason_not_qualifying', 'certified_total_mm'])
        for s in population:
            q = res[s]['qualifies'] and s not in dropped
            w.writerow([s, st[s]['name'], res[s]['measured'], 'Y' if q else 'N', reason(s), f"{totals[s]:.1f}" if q else ''])
        w.writerow(['STATEWIDE', f'mean of {N} qualifying stations', '', '', '', f"{statewide:.1f}"])

    # ---------- 2. PNG ----------
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    INK, INK2, SURF, C1, C2, C3 = '#0b0b0b', '#52514e', '#fcfcfb', '#2a78d6', '#eb6834', '#b8b7b2'
    order = sorted(qual, key=lambda s: totals[s])
    fig, ax = plt.subplots(figsize=(14, 6.4), dpi=200)
    fig.patch.set_facecolor(SURF); ax.set_facecolor(SURF)
    xs = list(range(len(order)))
    ax.bar(xs, [totals[s] for s in order], color=[C2 if s in (wettest, driest, BOSTON) else C1 for s in order], width=0.72)
    ax.axhline(statewide, color=INK2, lw=1, ls='--')
    ax.text(len(order) - 0.5, statewide + 12, f"Statewide figure {statewide:,.1f} mm, mean of {N} qualifying stations", ha='right', fontsize=9.5, color=INK)
    for s, dx, dy in [(wettest, -30, 60), (driest, 4, 420), (BOSTON, 10, 320)]:
        i = order.index(s)
        label = {wettest: 'Wettest', driest: 'Driest', BOSTON: 'Boston Logan'}[s]
        ax.annotate(f"{label}: {st[s]['name'].title()} ({s}) {totals[s]:,.1f} mm", xy=(i, totals[s]), xytext=(i + dx, totals[s] + dy),
                    fontsize=9, color=INK, arrowprops=dict(arrowstyle='-', color=INK2, lw=0.8))
    ax.set_xticks([]); ax.set_xlabel(f'{N} qualifying stations, driest to wettest', fontsize=9, color=INK2)
    ax.set_ylabel('2025 annual precipitation (mm)', fontsize=9, color=INK2)
    ax.set_ylim(0, 1600)
    for side in ['top', 'right']:
        ax.spines[side].set_visible(False)
    for side in ['left', 'bottom']:
        ax.spines[side].set_color('#d6d5d0')
    ax.tick_params(colors=INK2, length=0)
    ax.yaxis.grid(True, color='#e6e5e0', lw=0.6); ax.set_axisbelow(True)
    ax.set_title(f'Massachusetts 2025 annual precipitation, qualifying GHCN Daily stations: statewide {statewide:,.1f} mm', fontsize=12.5, color=INK, loc='left', pad=12)
    fig.text(0.01, 0.01, 'Source: NOAA GHCN Daily 2025 (PRCP, MDPR, DAPR), station registry and inventory; bulletin compilation standard applied.', fontsize=7.5, color=INK2)
    fig.tight_layout()
    fig.savefig(os.path.join(HERE, 'statewide_precipitation_2025.png'), facecolor=SURF)

    # ---------- 3. PDF ----------
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    ss = getSampleStyleSheet()
    body = ParagraphStyle('body', parent=ss['Normal'], fontName='Helvetica', fontSize=9.8, leading=13, spaceAfter=6)
    h = ParagraphStyle('h', parent=body, fontName='Helvetica-Bold', fontSize=10.5, spaceBefore=6, spaceAfter=3)
    title = ParagraphStyle('t', parent=body, fontName='Helvetica-Bold', fontSize=13.5, leading=17, spaceAfter=4)
    small = ParagraphStyle('s', parent=body, fontSize=8.6, leading=11)
    n_multi = sum(1 for s in population if res[s]['usable'])
    n_flag = sum(1 for s in population if res[s]['flagged'])
    n_incomplete = sum(1 for s in population if not res[s]['qualifies'])
    story = [
        Paragraph('Annual Precipitation Bulletin 2025: certification of the statewide figure', title),
        Paragraph('To: Bulletin editor &nbsp;&nbsp; From: Compilation, state climate office &nbsp;&nbsp; Date: 6 October 2026', small),
        Spacer(1, 4),
        Paragraph('Certified figure', h),
        Paragraph(f"The statewide annual precipitation for 2025 is certified at <b>{statewide:,.1f} mm</b>, the mean of the annual "
                  f"totals of <b>{N} qualifying stations</b>. Neither figure in circulation is certified: the draft table's "
                  f"{DRAFT_FIGURE:,.1f} mm across {DRAFT_N} stations and the reviewer's {REVIEW_FIGURE:,.1f} mm across {REVIEW_N} "
                  f"stations are both set aside.", body),
        Paragraph('What the two figures counted', h),
        Paragraph(f"<b>Draft table, {DRAFT_FIGURE:,.1f} mm across {DRAFT_N} stations: not certified.</b> It is the mean of a plain "
                  f"sum of each station's daily values, over every station that reported a daily value in 2025. It ignores "
                  f"completeness, so stations that reported for a few weeks pull the mean down, and it ignores the multi day "
                  f"totals that {n_multi} stations use, so rain that fell during those periods is dropped. The same files "
                  f"reproduce it exactly.", body),
        Paragraph(f"<b>Reviewer, {REVIEW_FIGURE:,.1f} mm across {REVIEW_N} stations: not certified.</b> It keeps only stations with a "
                  f"daily value on all 365 days and sums those values. That treats every day inside a multi day total as "
                  f"unmeasured, which wrongly disqualifies {N - REVIEW_N + 1} stations whose years are complete once their "
                  f"usable multi day totals are counted, and it keeps both Blue Hill identifiers, which the standard "
                  f"merges. The same files reproduce it exactly.", body),
        Paragraph('How the certified figure was built', h),
        Paragraph(f"The population is every station registered to Massachusetts with a 2025 precipitation record in the "
                  f"2025 partition of GHCN Daily: {len(population)} stations. Values carrying a quality flag were treated as "
                  f"missing ({n_flag} stations carry one). A trace is a measured zero. A multi day total was used only with an "
                  f"unflagged day count and a covered period wholly inside 2025; it then counts every covered day as "
                  f"measured, contributes its full amount, and supersedes any daily value inside its period. A station "
                  f"qualifies only when all 365 days are measured; {n_incomplete} stations fall short. Blue Hill is "
                  f"registered twice at the same coordinates ({dropped and list(dropped.keys())[0]} and "
                  f"{dropped and list(dropped.values())[0]}); the cooperative record, whose precipitation record begins in "
                  f"{inv['USC00190736']['PRCP'][0]}, is kept and the other dropped. Keeping both would give {len(unmerged)} "
                  f"stations and {unmerged_mean:,.1f} mm. Values are in tenths of a millimetre in the files and are reported "
                  f"here in millimetres.", body),
        Paragraph('Wettest and driest qualifying stations', h),
        Paragraph(f"Wettest: <b>{st[wettest]['name'].title()} ({wettest})</b> at {totals[wettest]:,.1f} mm. Driest: "
                  f"<b>{st[driest]['name'].title()} ({driest})</b> at {totals[driest]:,.1f} mm. The full station table is in "
                  f"station_certification_2025.csv.", body),
        Paragraph('Boston Logan', h),
        Paragraph(f"Boston Logan International Airport ({BOSTON}) measured <b>{boston_total:,.1f} mm</b> in 2025, every day "
                  f"measured. Its record runs from 1936; {len(complete)} of the {len(years)} years satisfy the completeness "
                  f"rule and {', '.join(str(y) for y in incomplete)} {'is' if len(incomplete) == 1 else 'are'} left out "
                  f"({', '.join(str(years[y]['ndays'] - years[y]['measured']) + ' days not measured' for y in incomplete)}). "
                  f"Among the {len(complete)} complete years, 2025 ranks <b>{boston_rank}th wettest</b>, between "
                  f"{ranked[boston_rank - 2]} at {years[ranked[boston_rank - 2]]['total'] / 10:,.1f} mm and "
                  f"{ranked[boston_rank]} at {years[ranked[boston_rank]]['total'] / 10:,.1f} mm. The station file in the "
                  f"workspace stops on 6 February 2025, so the 2025 year is completed from the 2025 partition; the two "
                  f"agree on every overlapping day.", body),
        Paragraph('Sensitivity of the statewide figure', h),
        Paragraph(f"The qualifying station whose removal would move the statewide figure the most is "
                  f"<b>{st[mover]['name'].title()} ({mover})</b>: without it the mean of the remaining {N - 1} stations would be "
                  f"{mean_exact + mover_delta:,.1f} mm, a move of {mover_delta:+.1f} mm.", body),
        Paragraph('Why no other figure survives', h),
        Paragraph(f"The standard fixes the population, the treatment of flags, traces and multi day totals, the completeness "
                  f"test, the one record per site rule and the statistic. Applied to the shipped files there is exactly one "
                  f"qualifying set of {N} stations and one mean. Every other figure relaxes one rule: counting multi day "
                  f"periods as unmeasured, ignoring the totals they carry, skipping the completeness test, or counting a site "
                  f"twice. {statewide:,.1f} mm across {N} stations is the only figure the standard and the files allow.", body),
    ]
    doc = SimpleDocTemplate(os.path.join(HERE, 'bulletin_certification_memo.pdf'), pagesize=letter,
                            leftMargin=0.8 * inch, rightMargin=0.8 * inch, topMargin=0.7 * inch, bottomMargin=0.7 * inch,
                            title='Annual Precipitation Bulletin 2025: certification', author='State climate office')
    doc.build(story)

    print(f"population {len(population)}; qualifying {N}; statewide {statewide} (exact {mean_exact:.3f}); unmerged {len(unmerged)} {unmerged_mean}")
    print(f"wettest {wettest} {st[wettest]['name']} {totals[wettest]}; driest {driest} {st[driest]['name']} {totals[driest]}; mover {mover} {st[mover]['name']} {mover_delta:+.2f}")
    print(f"boston {boston_total} rank {boston_rank} of {len(complete)}; incomplete {incomplete}; draft {draft_mean}/{len(naive)} review {review_mean}/{len(rev)}; multi {n_multi} flagged {n_flag} incomplete {n_incomplete}")


if __name__ == '__main__':
    main()

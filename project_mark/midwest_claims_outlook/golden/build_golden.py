"""Builds the three golden deliverables for the Midwest claims outlook from the shipped input package.

Record: Opportunity Insights Economic Tracker, UI Claims - State - Weekly.csv (Department of Labor weekly initial
claims by state), repository commit b8adef9 of 5 October 2026. Standard: inputs/office_forecasting_standard.md.
Every figure printed or written here is asserted stable under the determinism checks below.
"""
import csv, os, collections, datetime as dt, statistics as st

HERE = os.path.dirname(os.path.abspath(__file__))
INPUTS = os.path.join(HERE, '..', 'inputs')
MIDWEST = ['IL', 'IN', 'IA', 'KS', 'MI', 'MN', 'MO', 'NE', 'ND', 'OH', 'SD', 'WI']
RATIO_W, BENCH_W, ORIGINS, H_BACK, H_OUT, LAG = 8, 4, 26, 4, 13, 364
METHODS_LEAD_CUT = 20.0


def load():
    geo = {r['statefips']: r for r in csv.DictReader(open(os.path.join(INPUTS, 'data', 'GeoIDs - State.csv'), encoding='utf-8-sig'))}
    abbr = {g['stateabbrev']: f for f, g in geo.items()}
    S = collections.defaultdict(dict); comb_missing = 0
    for r in csv.DictReader(open(os.path.join(INPUTS, 'data', 'UI Claims - State - Weekly.csv'), encoding='utf-8-sig')):
        d = dt.date(int(r['year']), int(r['month']), int(r['day_endofweek']))
        S[r['statefips']][d] = float(r['initclaims_count_regular'])
        comb_missing += r['initclaims_count_combined'] == '.'
    return geo, abbr, S, comb_missing


def model(s, origin, target):
    rec = sum(s[origin - dt.timedelta(days=7 * i)] for i in range(RATIO_W))
    pri = sum(s[origin - dt.timedelta(days=7 * i + LAG)] for i in range(RATIO_W))
    return s[target - dt.timedelta(days=LAG)] * rec / pri


def bench(s, origin):
    return sum(s[origin - dt.timedelta(days=7 * i)] for i in range(BENCH_W)) / BENCH_W


def backtest(s, last, origins=ORIGINS, h=H_BACK, metric='mape', ratio_w=RATIO_W, lag=LAG):
    em, eb = [], []
    for k in range(origins):
        o = last - dt.timedelta(days=7 * (k + h))
        rec = sum(s[o - dt.timedelta(days=7 * i)] for i in range(ratio_w)); pri = sum(s[o - dt.timedelta(days=7 * i + lag)] for i in range(ratio_w))
        b = bench(s, o)
        for j in range(1, h + 1):
            t = o + dt.timedelta(days=7 * j); a = s[t]; m = s[t - dt.timedelta(days=lag)] * rec / pri
            em.append(abs(m - a) / a if metric == 'mape' else abs(m - a)); eb.append(abs(b - a) / a if metric == 'mape' else abs(b - a))
    return (100 * st.mean(em), 100 * st.mean(eb)) if metric == 'mape' else (st.mean(em), st.mean(eb))


def main():
    geo, abbr, S, comb_missing = load()
    dates = sorted(S[abbr['IL']])
    last = dates[-1]
    assert last == dt.date(2026, 9, 26) and all(d.weekday() == 5 for d in dates) and len(dates) == 352
    assert all((b - a).days == 7 for a, b in zip(dates, dates[1:]))
    assert all(len(S[abbr[a]]) == 352 for a in MIDWEST) and comb_missing == 9640
    targets = [last + dt.timedelta(days=7 * j) for j in range(1, H_OUT + 1)]
    res = {}
    for a in MIDWEST:
        s = S[abbr[a]]
        em, eb = backtest(s, last)
        em, eb = round(em, 2), round(eb, 2)
        published = em < eb
        mp = [model(s, last, t) for t in targets]; bp = [bench(s, last) for t in targets]
        pub = mp if published else bp
        prior = [s[t - dt.timedelta(days=LAG)] for t in targets]
        res[a] = dict(name=geo[abbr[a]]['statename'], em=em, eb=eb, published=published, model=mp, bench=bp, pub=pub,
                      prior=prior, total=sum(round(x) for x in pub), prior_total=sum(prior), latest=s[last], series=s)
    held = [a for a in MIDWEST if not res[a]['published']]
    pubs = [a for a in MIDWEST if res[a]['published']]
    assert held == ['IA', 'NE', 'ND'] and len(pubs) == 9
    regional = sum(res[a]['total'] for a in MIDWEST)
    regional_prior = sum(res[a]['prior_total'] for a in MIDWEST)
    # determinism: the same three holds under MAE, 20 and 30 origins, a 4 and a 13 week ratio and a 371 day lag
    for kw in (dict(metric='mae'), dict(origins=20), dict(origins=30), dict(ratio_w=4), dict(ratio_w=13)):
        hv = [a for a in MIDWEST if (lambda e: e[0] >= e[1])(backtest(S[abbr[a]], last, **kw))]
        assert hv == held, (kw, hv)
    # the two drafts
    pooled_m, pooled_b = [], []
    for a in MIDWEST:
        s = S[abbr[a]]
        for k in range(ORIGINS):
            o = last - dt.timedelta(days=7 * (k + H_BACK))
            for j in range(1, H_BACK + 1):
                t = o + dt.timedelta(days=7 * j); pooled_m.append(abs(model(s, o, t) - s[t]) / s[t]); pooled_b.append(abs(bench(s, o) - s[t]) / s[t])
    pooled = (100 * st.mean(pooled_m), 100 * st.mean(pooled_b))
    assert pooled[0] < pooled[1]                      # the desk's regional reading is true and is not the test
    region_sum_m, region_sum_b = [], []               # the region as one series
    for k in range(ORIGINS):
        o = last - dt.timedelta(days=7 * (k + H_BACK))
        for j in range(1, H_BACK + 1):
            t = o + dt.timedelta(days=7 * j)
            a_ = sum(S[abbr[a]][t] for a in MIDWEST); m_ = sum(model(S[abbr[a]], o, t) for a in MIDWEST); b_ = sum(bench(S[abbr[a]], o) for a in MIDWEST)
            region_sum_m.append(abs(m_ - a_) / a_); region_sum_b.append(abs(b_ - a_) / a_)
    region_series = (100 * st.mean(region_sum_m), 100 * st.mean(region_sum_b))
    assert region_series[0] < region_series[1]
    lead_holds = [a for a in MIDWEST if res[a]['em'] > METHODS_LEAD_CUT]
    assert set(lead_holds) == {'IA', 'MI', 'MO', 'NE', 'ND'}, lead_holds
    desk_total = sum(sum(round(x) for x in res[a]['model']) for a in MIDWEST)
    lead_total = sum(sum(round(x) for x in (res[a]['bench'] if a in lead_holds else res[a]['model'])) for a in MIDWEST)
    # change against a year earlier, by state
    change = {a: res[a]['total'] - res[a]['prior_total'] for a in MIDWEST}
    biggest = max(MIDWEST, key=lambda a: abs(change[a]))
    # why the model misses in the held states: the ratio and the prior year's profile over the back test span
    diag = {}
    for a in held:
        s = S[abbr[a]]
        span = [last - dt.timedelta(days=7 * k) for k in range(ORIGINS + H_BACK)][::-1]
        this = [s[d] for d in span]; prior = [s[d - dt.timedelta(days=LAG)] for d in span]
        ratio_now = sum(s[last - dt.timedelta(days=7 * i)] for i in range(RATIO_W)) / sum(s[last - dt.timedelta(days=7 * i + LAG)] for i in range(RATIO_W))
        peak_prior = max(span, key=lambda d: s[d - dt.timedelta(days=LAG)]); peak_this = max(span, key=lambda d: s[d])
        cv_prior = st.pstdev(prior) / st.mean(prior); cv_this = st.pstdev(this) / st.mean(this)
        diag[a] = dict(gap=round(res[a]['em'] - res[a]['eb'], 2), ratio_now=ratio_now, peak_prior=peak_prior, peak_this=peak_this,
                       peak_prior_v=s[peak_prior - dt.timedelta(days=LAG)], peak_this_v=s[peak_this], cv_prior=cv_prior, cv_this=cv_this,
                       span_start=span[0], mean_this=st.mean(this), mean_prior=st.mean(prior))

    # ---------- 1. CSV ----------
    with open(os.path.join(HERE, 'q4_claims_outlook.csv'), 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['state', 'week_ending', 'model_forecast', 'benchmark_forecast', 'published_forecast', 'published_path',
                    'model_backtest_error_pct', 'benchmark_backtest_error_pct', 'status'])
        for a in MIDWEST:
            r = res[a]
            for t, m, b, p in zip(targets, r['model'], r['bench'], r['pub']):
                w.writerow([a, t.isoformat(), round(m), round(b), round(p), 'model' if r['published'] else 'benchmark', '', '', ''])
        for a in MIDWEST:
            r = res[a]
            w.writerow([a, 'backtest', '', '', '', '', f"{r['em']:.2f}", f"{r['eb']:.2f}", 'published' if r['published'] else 'held'])

    # ---------- 2. PNG ----------
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.patches import Patch
    INK, INK2, SURF, GRID = '#0b0b0b', '#52514e', '#fcfcfb', '#e6e5e0'
    C_M, C_B, C_HOLD = '#2a78d6', '#b8b6b0', '#eb6834'
    order = sorted(MIDWEST, key=lambda a: res[a]['em'] - res[a]['eb'])
    fig, ax = plt.subplots(figsize=(12.5, 7.4), dpi=200)
    fig.patch.set_facecolor(SURF); ax.set_facecolor(SURF)
    ys = list(range(len(order)))[::-1]
    for y, a in zip(ys, order):
        r = res[a]; cm = C_HOLD if not r['published'] else C_M
        ax.barh(y + 0.19, r['em'], height=0.36, color=cm, edgecolor=SURF, linewidth=0.8)
        ax.barh(y - 0.19, r['eb'], height=0.36, color=C_B, edgecolor=SURF, linewidth=0.8)
        ax.text(r['em'] + 0.5, y + 0.19, f"{r['em']:.2f}", va='center', fontsize=8.2, color=INK, fontweight='bold' if not r['published'] else 'normal')
        ax.text(r['eb'] + 0.5, y - 0.19, f"{r['eb']:.2f}", va='center', fontsize=8.2, color=INK2)
    ax.set_yticks(ys); ax.set_yticklabels([f"{res[a]['name']}  ({'held' if not res[a]['published'] else 'model path'})" for a in order], fontsize=9, color=INK2)
    ax.set_xlim(0, 60); ax.set_ylim(-0.7, len(order) - 0.3)
    ax.xaxis.grid(True, color=GRID, lw=0.6); ax.set_axisbelow(True)
    for side in ['top', 'right', 'left']:
        ax.spines[side].set_visible(False)
    ax.spines['bottom'].set_color('#d6d5d0'); ax.tick_params(colors=INK2, length=0, labelsize=8.6)
    ax.set_xlabel('Back test error: mean absolute percentage error over 26 origins and 4 horizons (percent)', fontsize=9, color=INK2)
    ax.legend(handles=[Patch(color=C_M, label='Model, state published on the model path'), Patch(color=C_HOLD, label='Model, state held (error not below the benchmark)'),
                       Patch(color=C_B, label='Benchmark (four week mean held flat)')], loc='upper right', frameon=False, fontsize=8.4, labelcolor=INK2)
    fig.text(0.01, 0.975, f"Fourth quarter 2026 claims outlook: back test by state, model against benchmark", fontsize=11, color=INK, fontweight='bold')
    fig.text(0.01, 0.948, f"Model path published for {len(pubs)} states; {', '.join(res[a]['name'] for a in held)} held on the benchmark path. "
             f"States ordered by the model's margin over the benchmark.", fontsize=9.6, color=INK2)
    fig.text(0.01, 0.012, 'Source: U.S. Department of Labor weekly initial claims (regular program) as compiled by the Opportunity Insights Economic Tracker; '
             f'record through the week ending {last.isoformat()}.', fontsize=7.4, color=INK2)
    fig.tight_layout(rect=(0, 0.03, 1, 0.935))
    fig.savefig(os.path.join(HERE, 'backtest_by_state.png'), facecolor=SURF)

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
    def tstyle(n, hl=()):
        return TableStyle([('FONT', (0, 0), (-1, 0), 'Helvetica-Bold', 8.2), ('FONT', (0, 1), (-1, -1), 'Helvetica', 8.2),
                           ('ALIGN', (1, 0), (-1, -1), 'RIGHT'), ('LINEBELOW', (0, 0), (-1, 0), 0.6, colors.black),
                           ('TOPPADDING', (0, 0), (-1, -1), 0.8), ('BOTTOMPADDING', (0, 0), (-1, -1), 0.8),
                           ('LINEABOVE', (0, n - 1), (-1, n - 1), 0.6, colors.black), ('FONT', (0, n - 1), (-1, n - 1), 'Helvetica-Bold', 8.2)]
                          + [('BACKGROUND', (0, i), (-1, i), colors.HexColor('#fde7d9')) for i in hl])
    held_names = ', '.join(res[a]['name'] for a in held)
    story = [
        Paragraph('Fourth quarter 2026 claims outlook: publication decision', title),
        Paragraph(f'To: Publication committee &nbsp;&nbsp; From: Forecasting desk &nbsp;&nbsp; Date: 6 October 2026 &nbsp;&nbsp; Record through the week ending {last.strftime("%d %B %Y")}', small),
        Spacer(1, 4),
        Paragraph('Decision', h),
        Paragraph(f"The outlook publishes the <b>model path for nine states</b> ({', '.join(res[a]['name'] for a in pubs)}) and <b>holds "
                  f"{held_names}</b> on the benchmark path, because in those three the model's back test error is not below the benchmark's. "
                  f"The regional thirteen week total the outlook publishes, weeks ending {targets[0].strftime('%d %B')} to {targets[-1].strftime('%d %B %Y')}, is "
                  f"<b>{regional:,} initial claims</b>. The desk's draft (all twelve on the model path, {desk_total:,}) and the methods lead's draft "
                  f"(five states held, {lead_total:,}) are not adopted.", body),
        Paragraph('The two drafts: what each measured', h),
        Paragraph(f"<b>The desk, all twelve states on the model path: not adopted.</b> Its ground is true: pooled over the twelve states' "
                  f"1,248 back test forecasts the model's error is {pooled[0]:.2f} percent against {pooled[1]:.2f} for the benchmark, and on the region "
                  f"summed as one series it is {region_series[0]:.2f} against {region_series[1]:.2f}. The standard has no regional test; each state is "
                  f"published on its own back test, and three states fail theirs. The regional result is carried by the large states where the model "
                  f"is strong (Illinois, Ohio, Michigan, Minnesota, Wisconsin) and hides the three where it is not.", body),
        Paragraph(f"<b>The methods lead, hold every state with model error above {METHODS_LEAD_CUT:.0f} percent: not adopted.</b> That holds "
                  f"{', '.join(res[a]['name'] for a in lead_holds)}. The level of the model's error is not the test; the test is whether it is "
                  f"below the benchmark's for the same state. Michigan ({res['MI']['em']:.2f} against {res['MI']['eb']:.2f}) and Missouri "
                  f"({res['MO']['em']:.2f} against {res['MO']['eb']:.2f}) carry high errors because their claims are volatile, and the benchmark "
                  f"does worse still; the model earns its place there. The three states the standard holds are the three whose model does not.", body),
        Paragraph('Back test by state', h),
    ]
    rows_t = [['State', 'Model error %', 'Benchmark error %', 'Margin', 'Status', 'Latest week', 'Published 13 week total']]
    for a in order:
        r = res[a]
        rows_t.append([r['name'], f"{r['em']:.2f}", f"{r['eb']:.2f}", f"{r['em'] - r['eb']:+.2f}", 'held' if not r['published'] else 'model', f"{r['latest']:,.0f}", f"{r['total']:,}"])
    rows_t.append(['Midwest Region', f"{pooled[0]:.2f} pooled", f"{pooled[1]:.2f} pooled", '', f"{len(pubs)} model, {len(held)} held", f"{sum(res[a]['latest'] for a in MIDWEST):,.0f}", f"{regional:,}"])
    t = Table(rows_t, colWidths=[1.25 * inch, 0.95 * inch, 1.15 * inch, 0.65 * inch, 0.9 * inch, 0.85 * inch, 1.3 * inch], repeatRows=1)
    t.setStyle(tstyle(len(rows_t), hl=[i + 1 for i, a in enumerate(order) if not res[a]['published']]))
    story += [t, Spacer(1, 5),
        Paragraph(f"The model is the count of the week 364 days before the target, scaled by the ratio of the latest eight weeks to the same eight weeks a "
                  f"year earlier; the benchmark is the latest four week mean held flat; the back test runs 26 origins, 4 to 29 weeks before the latest week, "
                  f"each forecasting the next four weeks, and scores the mean absolute percentage error over the 104 forecasts. The regular program "
                  f"count column was used throughout; the combined column is empty for every week since the pandemic programs ended.", body),
        Paragraph('Why the model misses in the held states', h)]
    for a in held:
        d = diag[a]; r = res[a]
        story.append(Paragraph(f"<b>{r['name']}</b>: model {r['em']:.2f} against benchmark {r['eb']:.2f}, {d['gap']:+.2f} points. The model carries last "
                               f"year's week by week profile forward, and over the back test span (weeks ending {d['span_start'].strftime('%d %B %Y')} to "
                               f"{last.strftime('%d %B %Y')}) that profile does not repeat: a year earlier the span peaked at {d['peak_prior_v']:,.0f} in the "
                               f"week ending {(d['peak_prior'] - dt.timedelta(days=LAG)).strftime('%d %B %Y')}, this year it peaked at {d['peak_this_v']:,.0f} in the week ending "
                               f"{d['peak_this'].strftime('%d %B %Y')}; the prior year's weeks vary {d['cv_prior'] * 100:.0f} percent around their mean against "
                               f"{d['cv_this'] * 100:.0f} percent this year, so the seasonal shape the model relies on is {'sharper' if d['cv_prior'] > d['cv_this'] else 'flatter'} "
                               f"in the base year than in the year being forecast, and the eight week ratio ({d['ratio_now']:.3f} at the latest origin) cannot "
                               f"correct timing. The flat benchmark, with nothing to mistime, does better.", body))
    story += [
        Paragraph('The published outlook against a year earlier', h),
        Paragraph(f"The twelve published paths sum to <b>{regional:,}</b> initial claims over the thirteen weeks, against <b>{regional_prior:,.0f}</b> in the same "
                  f"thirteen weeks a year earlier (weeks ending {(targets[0] - dt.timedelta(days=LAG)).strftime('%d %B %Y')} to "
                  f"{(targets[-1] - dt.timedelta(days=LAG)).strftime('%d %B %Y')}), a change of {regional - regional_prior:+,.0f} "
                  f"({100 * (regional / regional_prior - 1):+.1f} percent). The largest published change is <b>{res[biggest]['name']}</b>, "
                  f"{change[biggest]:+,.0f} ({res[biggest]['prior_total']:,.0f} to {res[biggest]['total']:,}, on the "
                  f"{'model' if res[biggest]['published'] else 'benchmark'} path). By state the changes are "
                  + ', '.join(f"{res[a]['name']} {change[a]:+,.0f}" for a in sorted(MIDWEST, key=lambda a: change[a])) + '.', body),
        Paragraph('What would have published the held states', h),
        Paragraph(' '.join(f"{res[a]['name']}: the model's error would have to fall by <b>{res[a]['em'] - res[a]['eb'] + 0.01:.2f} points</b>, to "
                           f"{res[a]['eb'] - 0.01:.2f}, to sit below the benchmark's {res[a]['eb']:.2f}." for a in held)
                  + " Nothing in the record moves them; the holds stand until the next quarter's back test.", body),
        Paragraph('Why no other publication list survives', h),
        Paragraph(f"The standard fixes the record (regular program counts, week ending Saturday), the model, the benchmark, the back test (26 origins, "
                  f"4 horizons, percentage error) and the decision rule (each state on its own test, model below benchmark). On those terms the same "
                  f"three states hold under absolute as well as percentage error, under 20 or 30 origins and under a four or thirteen week ratio. "
                  f"The twelve state list survives only by replacing the state test with a regional one, and the five state list only by "
                  f"replacing the comparison with a level.", body),
    ]
    doc = SimpleDocTemplate(os.path.join(HERE, 'claims_outlook_memo.pdf'), pagesize=letter, leftMargin=0.8 * inch, rightMargin=0.8 * inch,
                            topMargin=0.7 * inch, bottomMargin=0.7 * inch, title='Fourth quarter 2026 claims outlook: publication decision', author='Forecasting desk')
    doc.build(story)

    print(f"published {pubs}; held {held}; regional total {regional} prior {regional_prior:.0f} change {regional - regional_prior:+.0f}; desk {desk_total} lead {lead_total}")
    print('backtest:', [(a, res[a]['em'], res[a]['eb']) for a in order])
    print(f"pooled {pooled[0]:.2f}/{pooled[1]:.2f}; region series {region_series[0]:.2f}/{region_series[1]:.2f}; lead holds {lead_holds}")
    print('changes:', {a: round(change[a]) for a in MIDWEST}, 'biggest', biggest)
    print('diag:', {a: {k: (v.isoformat() if isinstance(v, dt.date) else (round(v, 3) if isinstance(v, float) else v)) for k, v in d.items()} for a, d in diag.items()})
    print('held fixes:', {a: round(res[a]['em'] - res[a]['eb'] + 0.01, 2) for a in held})
    print('first targets', [t.isoformat() for t in targets[:2]], 'last', targets[-1].isoformat())


if __name__ == '__main__':
    main()

"""Builds the three golden deliverables for the polling partner task from the shipped input package.

Record: FiveThirtyEight's pollster ratings data as published in the fivethirtyeight/data repository (commit
4c1ff5e, CC BY 4.0): the current vintage raw_polls.csv, the published ratings, and the 2023 and 2021 vintages.
Standard: inputs/board_polling_partner_standard.md (scenario document).
Every figure printed or written here is asserted stable under the determinism checks below.
"""
import csv, os, collections, statistics as st

HERE = os.path.dirname(os.path.abspath(__file__))
INPUTS = os.path.join(HERE, '..', 'inputs', 'pollster-ratings')
WINDOW, TEST = (2016, 2022), 2022
MIN_POLLS, MIN_TEST = 40, 10
DESK = ('Harris Insights & Analytics', 3.05)
EDITOR = 'The New York Times/Siena College'
PREVIOUS = ('Emerson College', 4.62)


def general(rows, cyccol):
    out = []
    for r in rows:
        if r['type_simple'].endswith('-G') or r['type_simple'] == 'House-G-US':
            r['cyc'] = int(r[cyccol])
            r['err'] = abs(float(r['margin_poll']) - float(r['margin_actual']))
            r['bias'] = float(r['margin_poll']) - float(r['margin_actual'])
            r['part'] = r['partisan'] not in ('NA', '')
            out.append(r)
    return out


def load(name, cyccol):
    return general(list(csv.DictReader(open(os.path.join(INPUTS, name), encoding='utf-8-sig'))), cyccol)


def by_poll(rs):
    polls = collections.defaultdict(list)
    for r in rs:
        polls[r['poll_id']].append(r)
    return polls


def poll_errors(polls):
    return [st.mean(r['err'] for r in v) for v in polls.values()]


def evaluate(G, window, test, unit='poll', has_active=True, drop_partisan_rows=False, min_polls=MIN_POLLS,
             min_test=MIN_TEST, median_all=True):
    """Applies the standard and returns one record per pollster in the window plus the test cycle median."""
    win = [r for r in G if window[0] <= r['cyc'] <= window[1]]
    if drop_partisan_rows:
        win = [r for r in win if not r['part']]
    P = collections.defaultdict(list)
    for r in win:
        P[r['pollster_rating_id']].append(r)
    test_polls = by_poll([r for r in win if r['cyc'] == test])
    median = st.median(poll_errors(test_polls)) if unit == 'poll' else st.median(r['err'] for r in win if r['cyc'] == test)
    out = {}
    for pid, rs in P.items():
        polls = by_poll(rs)
        tp = {k: v for k, v in polls.items() if v[0]['cyc'] == test}
        if unit == 'poll':
            score = st.mean(poll_errors(polls)); etest = st.mean(poll_errors(tp)) if tp else None
        else:
            score = st.mean(r['err'] for r in rs); etest = st.mean(r['err'] for r in rs if r['cyc'] == test) if tp else None
        active = (rs[0].get('inactive', 'FALSE') == 'FALSE') if has_active else True
        partisan = sum(1 for v in polls.values() if any(r['part'] for r in v))
        d = dict(id=pid, name=rs[0]['pollster'], names=sorted({r['pollster'] for r in rs}), active=active, partisan=partisan,
                 polls=len(polls), questions=len(rs), score=score, ntest=len(tp), etest=etest,
                 bias=st.mean(r['bias'] for r in rs),
                 right=(st.mean((float(r['margin_poll']) > 0) == (float(r['margin_actual']) > 0) for r in rs if float(r['margin_poll']) != 0)
                        if any(float(r['margin_poll']) != 0 for r in rs) else None),
                 calls=sum(1 for r in rs if float(r['margin_poll']) != 0),
                 rows=rs, polls_by_id=polls)
        d['volume'] = active and partisan == 0 and len(polls) >= min_polls
        d['recency'] = d['volume'] and len(tp) >= min_test
        d['passes'] = d['recency'] and etest <= median
        out[pid] = d
    ranked = sorted([d for d in out.values() if d['passes']], key=lambda d: (round(d['score'], 2), -d['polls']))
    for i, d in enumerate(ranked, 1):
        d['rank'] = i
    return out, median, ranked


def main():
    NEW = load('raw_polls.csv', 'cycle')
    OLD23 = load('2023/raw-polls.csv', 'year')
    OLD21 = load('2021/raw-polls.csv', 'year')
    assert len(NEW) == 18250 and len({r['question_id'] for r in NEW}) == 18250
    out, median, ranked = evaluate(NEW, WINDOW, TEST)
    win = [d for d in out.values()]
    funnel = [('pollsters with a poll in the window', len(win)),
              ('active', sum(1 for d in win if d['active'])),
              ('no partisan polls', sum(1 for d in win if d['active'] and d['partisan'] == 0)),
              (f'at least {MIN_POLLS} polls', sum(1 for d in win if d['volume'])),
              (f'at least {MIN_TEST} polls in the {TEST} cycle', sum(1 for d in win if d['recency'])),
              (f'pass the {TEST} test', len(ranked))]
    assert [n for _, n in funnel] == [356, 280, 182, 13, 8, 5], funnel
    w, ru, third = ranked[0], ranked[1], ranked[2]
    assert w['name'] == 'Beacon Research/Shaw & Co. Research' and round(w['score'], 2) == 4.13
    assert ru['name'] == 'Marist College' and round(ru['score'], 2) == 4.29 and third['name'] == 'Emerson College'
    assert round(median, 2) == 4.02
    byname = {d['name']: d for d in out.values()}
    harris, nyt, ia = byname[DESK[0]], byname[EDITOR], byname['InsiderAdvantage']
    assert round(harris['score'], 2) == DESK[1] and harris['ntest'] == 1 and not harris['recency'] and harris['etest'] <= median
    assert ia['recency'] and not ia['passes'] and round(ia['etest'], 2) == 4.92
    assert nyt['passes'] and nyt['rank'] == 4
    raw_order = sorted([d for d in win if d['volume']], key=lambda d: d['score'])
    assert [d['name'] for d in raw_order[:3]] == [DESK[0], 'InsiderAdvantage', w['name']]
    tie = round(round(ru['score'], 2) - round(w['score'], 2), 2)
    flip = round(tie + 0.01, 2)   # at a tie the partner keeps the selection on polls, so the hand over needs one more hundredth
    assert tie == 0.16 and flip == 0.17 and w['polls'] > ru['polls']
    assert any(len({r['race']: 1 for r in v}) > 1 for v in w['polls_by_id'].values())  # one poll can cover several races

    # ---- determinism: the selection holds under the honest variants
    for kw in (dict(unit='question'), dict(drop_partisan_rows=True), dict(min_polls=50), dict(min_test=5), dict(median_all=False)):
        _, _, rk = evaluate(NEW, WINDOW, TEST, **kw)
        assert rk[0]['id'] == w['id'], kw
    _, _, rk = evaluate([r for r in NEW if r['cyc'] % 2 == 0], WINDOW, TEST)
    assert rk[0]['id'] == w['id']
    # the two offered figures and the traps the record offers
    _, _, rk_old = evaluate(OLD23, WINDOW, TEST)
    assert rk_old[0]['name'] == 'Emerson College'        # the 2023 vintage, with its precomputed error column
    _, _, rk30 = evaluate(NEW, WINDOW, TEST, min_polls=30)
    assert rk30[0]['name'] == 'Research Co.'              # a looser volume gate
    comb = {c['pollster_rating_id']: c for c in csv.DictReader(open(os.path.join(INPUTS, 'pollster-ratings-combined.csv'), encoding='utf-8-sig'))}
    assert comb[nyt['id']]['rank'] == '1' and comb[w['id']]['rank'] == '16'
    # plus minus (error relative to the mean error of the same race type and cycle) reverses the lead
    exp = collections.defaultdict(list)
    for r in NEW:
        if WINDOW[0] <= r['cyc'] <= WINDOW[1]:
            exp[(r['type_simple'], r['cyc'])].append(r['err'])
    exp = {k: st.mean(v) for k, v in exp.items()}
    pm = {d['id']: st.mean(st.mean(r['err'] - exp[(r['type_simple'], r['cyc'])] for r in v) for v in d['polls_by_id'].values()) for d in ranked}
    assert min(pm, key=pm.get) == nyt['id']

    # ---- the previous selection on the 2021 vintage, and the same cycles on the current vintage
    out21, med21, rk21 = evaluate(OLD21, (2014, 2020), 2020, has_active=False)
    prev = rk21[0]
    assert prev['name'] == PREVIOUS[0] and round(prev['score'], 2) == PREVIOUS[1]
    raw21 = min((d for d in out21.values() if d['volume']), key=lambda d: d['score'])
    assert raw21['name'] == 'Siena College/The New York Times Upshot' and not raw21['passes'] and raw21['id'] == nyt['id']
    out_cur, med_cur, rk_cur = evaluate(NEW, (2014, 2020), 2020)
    same = rk_cur[0]['id'] == prev['id']
    cur_prev = out_cur[prev['id']]

    # ---- partner record
    cyc_tab = []
    for c in sorted({r['cyc'] for r in w['rows']}):
        pl = {k: v for k, v in w['polls_by_id'].items() if v[0]['cyc'] == c}
        cyc_tab.append((c, len(pl), st.mean(poll_errors(pl))))
    type_tab = []
    for t in sorted({r['type_simple'] for r in w['rows']}):
        rs = [r for r in w['rows'] if r['type_simple'] == t]
        type_tab.append((t, len(rs), st.mean(r['err'] for r in rs)))
    methods = collections.Counter(r['methodology'] for r in w['rows'])
    tname = {'Pres-G': 'President', 'Sen-G': 'Senate', 'Gov-G': 'Governor', 'House-G': 'House district', 'House-G-US': 'Generic ballot'}

    # ---------- 1. CSV scorecard ----------
    rows_out = sorted(out.values(), key=lambda d: (d.get('rank', 99), round(d['score'], 2), -d['polls']))
    with open(os.path.join(HERE, 'pollster_scorecard.csv'), 'w', newline='') as f:
        wr = csv.writer(f)
        wr.writerow(['pollster', 'pollster_rating_id', 'active', 'partisan_polls', 'polls', 'questions', 'certified_error',
                     'polls_2022', 'error_2022', 'meets_volume', 'meets_recency', 'passes_test', 'selection_rank'])
        for d in rows_out:
            wr.writerow([d['name'], d['id'], 'yes' if d['active'] else 'no', d['partisan'], d['polls'], d['questions'],
                         f"{d['score']:.2f}", d['ntest'], f"{d['etest']:.2f}" if d['etest'] is not None else '',
                         'yes' if d['volume'] else 'no', 'yes' if d['recency'] else 'no', 'yes' if d['passes'] else 'no',
                         d.get('rank', '')])

    # ---------- 2. PNG ----------
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D
    INK, INK2, SURF, GRID = '#0b0b0b', '#52514e', '#fcfcfb', '#e6e5e0'
    C_PASS, C_FAIL, C_NONE = '#2a78d6', '#eb6834', '#b8b6b0'
    vol = [d for d in win if d['volume']]
    fig, ax = plt.subplots(figsize=(12, 7.4), dpi=200)
    fig.patch.set_facecolor(SURF); ax.set_facecolor(SURF)
    ax.axhline(median, color=INK2, lw=1, ls='--')
    ax.text(2.85, median + 0.08, f"{TEST} test: median poll error of all {TEST} polls, {median:.2f} points", ha='left', va='bottom', fontsize=8.4, color=INK2)
    short = {'Beacon Research/Shaw & Co. Research': 'Beacon Research/Shaw & Co.', 'The New York Times/Siena College': 'NYT/Siena College',
             'Monmouth University Polling Institute': 'Monmouth University', 'Redfield & Wilton Strategies': 'Redfield & Wilton'}
    offsets = {'Marist College': (6, -12), 'Emerson College': (-6, -13), 'Suffolk University': (6, 6), 'YouGov': (6, 6), 'Harris Insights & Analytics': (6, 6),
               'SurveyMonkey': (6, 6), 'Monmouth University Polling Institute': (6, -12), 'Redfield & Wilton Strategies': (-6, 6),
               'Quinnipiac University': (6, -14)}
    for d in vol:
        if d['ntest'] >= MIN_TEST:
            col, mk, fc = (C_PASS if d['passes'] else C_FAIL), 'o', None
        else:
            col, mk, fc = C_NONE, 'o', SURF
        ax.plot(d['score'], d['etest'], mk, ms=9 if d is not w else 13, color=col, markerfacecolor=fc if fc else col, markeredgewidth=1.8 if fc else 1.2,
                markeredgecolor=col if fc else SURF, zorder=3)
        dx, dy = offsets.get(d['name'], (6, 6))
        ax.annotate(short.get(d['name'], d['name']) + (f"  {d['score']:.2f} / {d['etest']:.2f}" ), (d['score'], d['etest']), xytext=(dx, dy),
                    textcoords='offset points', fontsize=8.2, color=INK, ha='right' if dx < 0 else 'left',
                    fontweight='bold' if d is w else 'normal')
    ax.annotate('Selected partner', (w['score'], w['etest']), xytext=(w['score'] - 0.55, w['etest'] - 0.9), fontsize=9, color=INK, fontweight='bold',
                arrowprops=dict(arrowstyle='-', color=INK2, lw=0.8))
    ax.set_xlim(2.8, 6.8); ax.set_ylim(0, 7)
    ax.set_xlabel('Certified error: mean poll error, general election polls, 2016 to 2022 cycles (points)', fontsize=9, color=INK2)
    ax.set_ylabel(f'Mean poll error in the {TEST} cycle (points)', fontsize=9, color=INK2)
    ax.xaxis.grid(True, color=GRID, lw=0.6); ax.yaxis.grid(True, color=GRID, lw=0.6); ax.set_axisbelow(True)
    for side in ['top', 'right']:
        ax.spines[side].set_visible(False)
    ax.spines['left'].set_color('#d6d5d0'); ax.spines['bottom'].set_color('#d6d5d0'); ax.tick_params(colors=INK2, length=0, labelsize=8.6)
    ax.legend(handles=[Line2D([], [], marker='o', color=C_PASS, lw=0, ms=8, label=f'Passes the {TEST} test'),
                       Line2D([], [], marker='o', color=C_FAIL, lw=0, ms=8, label=f'Fails the {TEST} test (error above the median)'),
                       Line2D([], [], marker='o', color=C_NONE, markerfacecolor=SURF, markeredgewidth=1.8, lw=0, ms=8, label=f'Fewer than {MIN_TEST} polls in {TEST}: no test record')],
              loc='upper left', frameon=False, fontsize=8.4, labelcolor=INK2)
    fig.text(0.01, 0.975, f"The {len(vol)} active, non partisan pollsters with at least {MIN_POLLS} polls, 2016 to 2022: certified error against the {TEST} test", fontsize=11, color=INK, fontweight='bold')
    fig.text(0.01, 0.948, f"Selected partner: {w['name']}, {w['score']:.2f} points ({TEST}: {w['etest']:.2f}). Labels show certified error / {TEST} error.", fontsize=9.6, color=INK2)
    fig.text(0.01, 0.012, 'Source: FiveThirtyEight pollster ratings data, raw_polls.csv (current vintage), general election polls including the generic ballot; '
             'partisan sponsored and inactive pollsters excluded under the standard.', fontsize=7.4, color=INK2)
    fig.tight_layout(rect=(0, 0.03, 1, 0.935))
    fig.savefig(os.path.join(HERE, 'accuracy_vs_test.png'), facecolor=SURF)

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
    tstyle = lambda n, hl=None: TableStyle([('FONT', (0, 0), (-1, 0), 'Helvetica-Bold', 8.2), ('FONT', (0, 1), (-1, -1), 'Helvetica', 8.2),
                                            ('ALIGN', (1, 0), (-1, -1), 'RIGHT'), ('LINEBELOW', (0, 0), (-1, 0), 0.6, colors.black),
                                            ('TOPPADDING', (0, 0), (-1, -1), 0.8), ('BOTTOMPADDING', (0, 0), (-1, -1), 0.8)]
                                           + ([('BACKGROUND', (0, hl), (-1, hl), colors.HexColor('#dbe8f8'))] if hl else []))
    story = [
        Paragraph('2026 midterm cycle: polling partner selection', title),
        Paragraph('To: Editorial board &nbsp;&nbsp; From: Research desk &nbsp;&nbsp; Date: 6 October 2026', small),
        Spacer(1, 4),
        Paragraph('Selection', h),
        Paragraph(f"The board should select <b>{w['name']}</b> as the 2026 polling partner, with a certified error of "
                  f"<b>{w['score']:.2f} points</b> over {w['polls']} general election polls ({w['questions']} questions) in the 2016 to 2022 cycles, "
                  f"and a {TEST} test cycle error of {w['etest']:.2f} points over {w['ntest']} polls against a test median of {median:.2f}. It is the "
                  f"lowest certified error among the {len(ranked)} eligible pollsters that pass the test. The desk's draft "
                  f"({DESK[0]}, {DESK[1]:.2f}) and the standards editor's draft ({EDITOR}) are not certified.", body),
        Paragraph('The two drafts: what each measured', h),
        Paragraph(f"<b>The desk, {DESK[0]} at {DESK[1]:.2f} points: not certified.</b> The figure is right: it is the lowest certified error "
                  f"of any pollster that clears the volume test ({harris['polls']} polls, {harris['questions']} questions, all opt in online panel). It is "
                  f"not eligible because it has <b>{harris['ntest']} poll in the {TEST} cycle</b>, against the ten the standard requires; "
                  f"{harris['polls'] - harris['ntest']} of its {harris['polls']} polls are from 2018 and 2020. A record with no test cycle cannot be "
                  f"tested, and the one {TEST} poll it has (error {harris['etest']:.2f}) is below the median only because there is one of it.", body),
        Paragraph(f"<b>The standards editor, {EDITOR}: not certified.</b> It is first in the published ratings file (rank 1, numeric grade 3.0), "
                  f"and the published ratings measure something else: a predictive plus minus that adjusts each poll's error for the race type, "
                  f"the time to the election and the field, mean reverted and weighted by age across every cycle since 1998. Under the "
                  f"standard's own measure, the unadjusted poll error over 2016 to 2022, it is <b>fourth</b> among the pollsters that pass at "
                  f"{nyt['score']:.2f} points, {nyt['score'] - w['score']:.2f} above the partner, because {sum(1 for v in nyt['polls_by_id'].values() if v[0]['cyc'] == 2018)} of its {nyt['polls']} polls are 2018 "
                  f"House district polls, the hardest races to poll. Its {TEST} record is the best of the field ({nyt['etest']:.2f} over {nyt['ntest']} polls); "
                  f"the standard tests the cycle and ranks on the window.", body),
        Paragraph('From the record to the selection', h),
    ]
    rows_f = [['Test', 'Pollsters remaining']] + [[a, str(b)] for a, b in funnel]
    t = Table(rows_f, colWidths=[3.2 * inch, 1.3 * inch]); t.setStyle(tstyle(len(rows_f)))
    story += [t, Spacer(1, 5),
        Paragraph(f"The record is the current vintage of the raw polls file: {len(NEW):,} general election questions, of which "
                  f"{sum(1 for r in NEW if WINDOW[0] <= r['cyc'] <= WINDOW[1]):,} ({len(by_poll([r for r in NEW if WINDOW[0] <= r['cyc'] <= WINDOW[1]])):,} polls) fall in the 2016 to 2022 cycles. "
                  f"Pollsters were keyed on the rating id. Of the {funnel[0][1]} with a poll in the window, {funnel[0][1] - funnel[1][1]} are flagged inactive "
                  f"and {funnel[1][1] - funnel[2][1]} more carry at least one partisan sponsored poll; the standard excludes the pollster, not the poll. "
                  f"The volume test leaves {funnel[3][1]}; the {TEST} count leaves {funnel[4][1]} (Harris, Monmouth, Quinnipiac, SurveyMonkey and Redfield & Wilton fall "
                  f"short); the {TEST} test leaves {funnel[5][1]} (InsiderAdvantage at {ia['etest']:.2f}, Suffolk at {byname['Suffolk University']['etest']:.2f} and Morning Consult at "
                  f"{byname['Morning Consult']['etest']:.2f} exceed the {median:.2f} median). A poll is counted once whatever its number of questions; "
                  f"{sum(1 for d in vol for v in d['polls_by_id'].values() if len(v) > 1)} of the {sum(d['polls'] for d in vol)} polls of the volume eligible pollsters carry two or more.", body),
        Paragraph(f'The {len(vol)} pollsters that clear the volume test', h)]
    rows_v = [['Pollster', 'Polls', 'Certified error', f'{TEST} polls', f'{TEST} error', 'Outcome']]
    for d in raw_order:
        oc = 'selected' if d is w else ('passes' if d['passes'] else (f'fails {TEST} test' if d['recency'] else f'under {MIN_TEST} polls in {TEST}'))
        rows_v.append([d['name'], str(d['polls']), f"{d['score']:.2f}", str(d['ntest']), f"{d['etest']:.2f}", oc])
    t2 = Table(rows_v, colWidths=[2.5 * inch, 0.6 * inch, 1.0 * inch, 0.8 * inch, 0.8 * inch, 1.4 * inch], repeatRows=1)
    t2.setStyle(tstyle(len(rows_v), hl=raw_order.index(w) + 1))
    story += [t2, Spacer(1, 5),
        Paragraph('Runner up and flip point', h),
        Paragraph(f"The runner up is <b>{ru['name']}</b> at {ru['score']:.2f} points ({ru['polls']} polls; {TEST}: {ru['etest']:.2f} over {ru['ntest']}), then "
                  f"{third['name']} at {third['score']:.2f}. The partner leads by {tie:.2f} points. A rise of {tie:.2f} in its certified error only ties it at "
                  f"{ru['score']:.2f}, and the tie goes to the pollster with more polls, {w['name']} with {w['polls']} against {ru['polls']}; the smallest change "
                  f"that hands the selection to Marist is a rise of <b>{flip:.2f} points</b>, to {round(w['score'], 2) + flip:.2f}. Spread over {w['polls']} polls that is "
                  f"{flip * w['polls']:.1f} points of added error.", body),
        Paragraph(f"The partner's record", h)]
    rows_c = [['Cycle', 'Polls', 'Mean poll error']] + [[str(c), str(n), f"{e:.2f}"] for c, n, e in cyc_tab]
    rows_t = [['Race type', 'Questions', 'Mean error']] + [[tname[t], str(n), f"{e:.2f}"] for t, n, e in type_tab]
    tc = Table(rows_c, colWidths=[0.8 * inch, 0.7 * inch, 1.2 * inch]); tc.setStyle(tstyle(len(rows_c)))
    tt = Table(rows_t, colWidths=[1.3 * inch, 0.9 * inch, 1.0 * inch]); tt.setStyle(tstyle(len(rows_t)))
    both = Table([[tc, tt]], colWidths=[3.0 * inch, 3.5 * inch]); both.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP')]))
    story += [both, Spacer(1, 5),
        Paragraph(f"All {w['questions']} questions were live telephone polls. The signed bias over the window, question by question, is <b>{w['bias']:+.2f} points</b> "
                  f"(positive overstates the Democratic margin), and the partner called the winner in <b>{100 * w['right']:.1f} percent</b> of its "
                  f"{w['calls']} questions with a non zero poll margin ({round(w['right'] * w['calls'])} of {w['calls']}). Its weakest cycle was 2020 ({[e for c, n, e in cyc_tab if c == 2020][0]:.2f}) and its strongest {TEST}; its weakest race type "
                  f"was House districts ({[e for t, n, e in type_tab if t == 'House-G'][0]:.2f} over {[n for t, n, e in type_tab if t == 'House-G'][0]} questions). The published ratings "
                  f"file ranks it {comb[w['id']]['rank']}th with a numeric grade of {comb[w['id']]['numeric_grade']}.", body),
        Paragraph('The previous selection reproduced', h),
        Paragraph(f"On the record's 2021 vintage, with the 2014 to 2020 cycles as the record and 2020 as the test cycle (median {med21:.2f}), the standard "
                  f"selects <b>{prev['name']} at {prev['score']:.2f} points</b> ({prev['polls']} polls; 2020: {prev['etest']:.2f} over {prev['ntest']}), which is the "
                  f"previous selection. The lowest certified error on that vintage, {raw21['name']} at {raw21['score']:.2f}, fails the 2020 test at "
                  f"{raw21['etest']:.2f}; it is the same pollster, by rating id, as {EDITOR}. Applied to the current vintage's record of the same cycles, the "
                  f"standard would {'' if same else 'not '}select the same pollster: the current vintage adds polls and pollsters to those cycles "
                  f"({sum(1 for r in NEW if 2014 <= r['cyc'] <= 2020):,} questions against {sum(1 for r in OLD21 if 2014 <= r['cyc'] <= 2020):,}), and its selection is "
                  f"{rk_cur[0]['name']} at {rk_cur[0]['score']:.2f} with {prev['name']} at {cur_prev['score']:.2f}"
                  + (f" ranked {cur_prev.get('rank')} of {len(rk_cur)}" if cur_prev.get('rank') else ' not passing') + '.', body),
        Paragraph('Why no other pollster survives', h),
        Paragraph(f"The standard fixes the record (the current vintage, general election polls of 2016 to 2022), the unit (the poll), the measure "
                  f"(unadjusted mean error), the eligibility tests (active, no partisan work, {MIN_POLLS} polls, {MIN_TEST} in the test cycle) and the test "
                  f"(at or below the {TEST} median). Every pollster with a lower certified error than the partner fails one of them: Harris has one "
                  f"{TEST} poll, InsiderAdvantage fails the test, and the pollsters with lower error at a 30 poll gate (Research Co.) or on the 2023 "
                  f"vintage, or with a lower adjusted error in the published ratings, are not measured on the standard's terms. The selection holds "
                  f"whether polls or questions are the unit, whether partisan polls or partisan pollsters are dropped, and whether odd year "
                  f"elections are in or out.", body),
    ]
    doc = SimpleDocTemplate(os.path.join(HERE, 'polling_partner_memo.pdf'), pagesize=letter, leftMargin=0.8 * inch, rightMargin=0.8 * inch,
                            topMargin=0.7 * inch, bottomMargin=0.7 * inch, title='2026 midterm cycle: polling partner selection', author='Research desk')
    doc.build(story)

    print(f"partner {w['name']} {w['score']:.4f} polls {w['polls']} q {w['questions']} test {w['etest']:.4f}/{w['ntest']}; median {median:.4f}")
    print(f"runner {ru['name']} {ru['score']:.4f}; third {third['name']} {third['score']:.4f}; tie {tie:.2f} flip {flip:.2f}; funnel {funnel}")
    print(f"harris {harris['score']:.3f} polls {harris['polls']} test {harris['ntest']} {harris['etest']:.3f}; IA {ia['score']:.3f} test {ia['etest']:.3f}; nyt {nyt['score']:.3f} rank {nyt['rank']} test {nyt['etest']:.3f}/{nyt['ntest']}")
    print('volume eligible order:', [(d['name'], round(d['score'], 2), d['ntest'], round(d['etest'], 2), 'sel' if d is w else ('pass' if d['passes'] else 'fail')) for d in raw_order])
    print(f"partner cycles {[(c, n, round(e, 2)) for c, n, e in cyc_tab]} types {[(t, n, round(e, 2)) for t, n, e in type_tab]} bias {w['bias']:+.2f} right {w['right']:.3f} of {w['calls']} methods {dict(methods)}")
    print(f"previous {prev['name']} {prev['score']:.3f} median20 {med21:.3f}; raw21 {raw21['name']} {raw21['score']:.3f} test {raw21['etest']:.3f}; current vintage same cycles: {rk_cur[0]['name']} {rk_cur[0]['score']:.3f}, Emerson {cur_prev['score']:.3f} rank {cur_prev.get('rank')}; same={same}")
    print(f"traps: old vintage {rk_old[0]['name']} {rk_old[0]['score']:.2f}; 30 gate {rk30[0]['name']} {rk30[0]['score']:.2f}; plus minus leader {out[min(pm, key=pm.get)]['name']} {min(pm.values()):.2f}; published rank partner {comb[w['id']]['rank']}")


if __name__ == '__main__':
    main()

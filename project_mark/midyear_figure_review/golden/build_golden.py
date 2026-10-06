"""Golden build for the mid year figure review task. Reads only the files under inputs/ and writes the three
deliverables beside this script. Every figure in the deliverables is computed here; the asserts are the
determinism checks recorded in DESIGN.md."""
import csv, datetime as dt, os, itertools
from decimal import Decimal, ROUND_HALF_UP

HERE = os.path.dirname(os.path.abspath(__file__))
INP = os.path.join(HERE, '..', 'inputs')
MW = {'17': 'Illinois', '18': 'Indiana', '19': 'Iowa', '20': 'Kansas', '26': 'Michigan', '27': 'Minnesota',
      '29': 'Missouri', '31': 'Nebraska', '38': 'North Dakota', '39': 'Ohio', '46': 'South Dakota', '55': 'Wisconsin'}
ABBR = {'17': 'IL', '18': 'IN', '19': 'IA', '20': 'KS', '26': 'MI', '27': 'MN', '29': 'MO', '31': 'NE', '38': 'ND',
        '39': 'OH', '46': 'SD', '55': 'WI'}
R5 = {'17', '18', '26', '27', '39', '55'}; R7 = {'19', '20', '29', '31'}
STATEMENT = (1058808, 1211608, '-12.6')   # the note as published

def rnd1(x):
    return str(Decimal(str(x)).quantize(Decimal('0.1'), rounding=ROUND_HALF_UP))

def pct(a, b):
    return rnd1(100 * (Decimal(a) / Decimal(b) - 1))

def load():
    d, rate = {}, {}
    with open(os.path.join(INP, 'data', 'UI Claims - State - Weekly.csv'), newline='') as f:
        for r in csv.DictReader(f):
            w = dt.date(int(r['year']), int(r['month']), int(r['day_endofweek']))
            v = r['initclaims_count_regular']
            d[(r['statefips'], w)] = int(v) if v not in ('', '.') else None
            rate[(r['statefips'], w)] = r['initclaims_rate_regular']
    return d, rate

def main():
    d, rate = load()
    weeks = sorted({k[1] for k in d})
    assert all(w.weekday() == 5 for w in weeks)
    for s in MW:
        ws = [w for w in weeks if (s, w) in d]
        assert len(ws) == len(weeks) and all((ws[i + 1] - ws[i]).days == 7 for i in range(len(ws) - 1))
        assert all(d[(s, w)] is not None for w in ws)

    def half(y):            # the office's half year: weeks ending on Saturdays from 1 January to 30 June
        return [w for w in weeks if w.year == y and w.month <= 6]
    def shifted(y, k):      # the same count of weeks, moved k weeks later
        ws = half(y); i = weeks.index(ws[0]) + k
        return weeks[i:i + len(ws)]
    def tot(states, ws):
        return sum(d[(s, w)] for s in states for w in ws)

    L26, L25 = half(2026), half(2025)
    assert (L26[0], L26[-1], L25[0], L25[-1]) == (dt.date(2026, 1, 3), dt.date(2026, 6, 27), dt.date(2025, 1, 4), dt.date(2025, 6, 28))
    assert len(L26) == len(L25) == 26
    B26, B25 = shifted(2026, 1), shifted(2025, 1)
    assert (B26[0], B26[-1], B25[0], B25[-1]) == (dt.date(2026, 1, 10), dt.date(2026, 7, 4), dt.date(2025, 1, 11), dt.date(2025, 7, 5))

    MWs = set(MW)
    lab = (tot(MWs, L26), tot(MWs, L25)); lab_pc = pct(*lab)
    bas = (tot(MWs, B26), tot(MWs, B25)); bas_pc = pct(*bas)
    assert lab == (1082313, 1230465) and lab_pc == '-12.0'          # the committee member's figures: right on the label
    assert bas == STATEMENT[:2] and bas_pc == STATEMENT[2]           # the note reproduces on the window one week later

    # Uniqueness of the basis: no other specification in the family reproduces the statement's count, and the
    # percentage alone is matched by several specifications (which is why rule 3 asks for every number).
    cands = {}
    for k in range(-4, 5):
        for n in (24, 25, 26, 27, 28):
            for name, st in (('MW12', MWs), ('R5', R5), ('R7', R7), ('R5+R7', R5 | R7)):
                def win(y):
                    ws = half(y); i = weeks.index(ws[0]) + k; return weeks[i:i + n]
                a, b = tot(st, win(2026)), tot(st, win(2025))
                cands[(k, n, name)] = (a, b, pct(a, b))
    for r in (1, 2):
        for drop in itertools.combinations(sorted(MWs), r):
            st = MWs - set(drop)
            a, b = tot(st, L26), tot(st, L25); cands[('drop',) + drop] = (a, b, pct(a, b))
            a, b = tot(st, B26), tot(st, B25); cands[('drop+1',) + drop] = (a, b, pct(a, b))
    count_matches = [k for k, v in cands.items() if v[0] == STATEMENT[0]]
    full_matches = [k for k, v in cands.items() if v == STATEMENT]
    pct_matches = [k for k, v in cands.items() if v[2] == STATEMENT[2]]
    assert count_matches == [(1, 26, 'MW12')] and full_matches == [(1, 26, 'MW12')], (count_matches, full_matches)
    assert len(pct_matches) >= 4 and ('drop', '18') in pct_matches and (1, 26, 'R5+R7') in pct_matches, pct_matches
    # the record has a single vintage; combined column is empty in both windows; rates are per 100 of the 2019 labour force
    with open(os.path.join(INP, 'data', 'UI Claims - State - Weekly.csv'), newline='') as f:
        comb = [r['initclaims_count_combined'] for r in csv.DictReader(f) if r['statefips'] in MW and int(r['year']) >= 2025]
    assert all(c in ('', '.') for c in comb)

    # The exchange of weeks between the two bases
    out26, in26 = L26[0], B26[-1]; out25, in25 = L25[0], B25[-1]
    ex = {w: tot(MWs, [w]) for w in (out26, in26, out25, in25)}
    assert ex[out26] == 69759 and ex[in26] == 46254 and ex[out25] == 74195 and ex[in25] == 55338
    assert lab[0] - ex[out26] + ex[in26] == bas[0] and lab[1] - ex[out25] + ex[in25] == bas[1]

    mo_w = {w: d[('29', w)] for w in (out26, in26, out25, in25)}
    assert mo_w[in26] > mo_w[out26] and mo_w[out25] > mo_w[in25]
    # By state
    rows = []
    for s in sorted(MW, key=lambda s: MW[s]):
        a, b = tot({s}, L26), tot({s}, L25); c, e = tot({s}, B26), tot({s}, B25)
        pa, pb = pct(a, b), pct(c, e)
        rows.append(dict(fips=s, abbr=ABBR[s], name=MW[s], l26=a, l25=b, lp=pa, b26=c, b25=e, bp=pb,
                         diff=rnd1(Decimal(pb) - Decimal(pa))))
    most = max(rows, key=lambda r: abs(Decimal(r['diff'])))
    assert most['name'] == 'Missouri' and most['lp'] == '-11.4' and most['bp'] == '-4.4' and most['diff'] == '7.0', most
    assert all((Decimal(r['lp']) < 0) == (Decimal(r['bp']) < 0) for r in rows)   # no state changes direction
    second = sorted(rows, key=lambda r: -abs(Decimal(r['diff'])))[1]
    assert second['name'] == 'North Dakota' and second['diff'] == '-6.3', second

    # CSV
    with open(os.path.join(HERE, 'figure_review.csv'), 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['state', 'label_h1_2026', 'label_h1_2025', 'label_change_pct', 'basis_h1_2026', 'basis_h1_2025',
                    'basis_change_pct', 'basis_minus_label_change_points'])
        for r in rows:
            w.writerow([r['name'], r['l26'], r['l25'], r['lp'], r['b26'], r['b25'], r['bp'], r['diff']])
        w.writerow(['Midwest Region', lab[0], lab[1], lab_pc, bas[0], bas[1], bas_pc, rnd1(Decimal(bas_pc) - Decimal(lab_pc))])

    # Chart
    import matplotlib; matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    BLUE, ORANGE, GREY, SURF, INK, MUTED = '#2a78d6', '#eb6834', '#b8b6b0', '#fcfcfb', '#1f1f1f', '#6b6b6b'
    x26 = [w for w in weeks if dt.date(2026, 1, 3) <= w <= dt.date(2026, 7, 11)]
    x25 = [w for w in weeks if dt.date(2025, 1, 4) <= w <= dt.date(2025, 7, 12)]
    y26 = [tot(MWs, [w]) for w in x26]; y25 = [tot(MWs, [w]) for w in x25]
    idx = list(range(1, len(x26) + 1))
    fig, ax = plt.subplots(figsize=(12.5, 7.2), dpi=200)
    fig.patch.set_facecolor(SURF); ax.set_facecolor(SURF)
    ax.plot(idx, y25, color=GREY, lw=2.2, marker='o', ms=4, label='2025 (each week ends one day later than the 2026 date shown)')
    ax.plot(idx, y26, color=BLUE, lw=2.4, marker='o', ms=4.5, label='2026')
    top = max(y25 + y26)
    ax.set_ylim(0, top * 1.36)
    # window brackets
    def bracket(a, b, yv, color, text):
        ax.plot([a - 0.4, b + 0.4], [yv, yv], color=color, lw=2.6, solid_capstyle='butt')
        ax.plot([a - 0.4, a - 0.4], [yv - top * 0.02, yv + top * 0.02], color=color, lw=2.6)
        ax.plot([b + 0.4, b + 0.4], [yv - top * 0.02, yv + top * 0.02], color=color, lw=2.6)
        ax.text((a + b) / 2, yv + top * 0.03, text, ha='center', va='bottom', fontsize=9.2, color=color, fontweight='bold')
    bracket(1, 26, top * 1.24, INK, 'Window as labelled: weeks ending 3 January to 27 June 2026 (4 January to 28 June 2025)')
    bracket(2, 27, top * 1.10, ORANGE, 'Window the figure reproduces on: weeks ending 10 January to 4 July 2026 (11 January to 5 July 2025)')
    for i, (w, v) in enumerate(zip(x26, y26)):
        if i in (0, 26):
            ax.annotate(f'{v:,}', (i + 1, v), textcoords='offset points', xytext=(0, 9), ha='center', fontsize=8.5, color=BLUE, fontweight='bold')
            ax.annotate(f'{y25[i]:,}', (i + 1, y25[i]), textcoords='offset points', xytext=(0, 9), ha='center', fontsize=8.5, color=MUTED, fontweight='bold')
            ax.axvspan(i + 0.6, i + 1.4, color=ORANGE, alpha=0.12, lw=0)
    ax.text(1, top * 0.94, 'leaves', ha='center', fontsize=8.5, color=ORANGE)
    ax.text(27, top * 0.94, 'enters', ha='center', fontsize=8.5, color=ORANGE)
    ax.set_xticks(idx); ax.set_xticklabels([w.strftime('%d %b') for w in x26], rotation=60, ha='right', fontsize=8)
    ax.set_xlabel('Week ending (2026 dates; the matching 2025 week ends one day later)', fontsize=9.5, color=MUTED)
    ax.set_ylabel('Regular program initial claims, twelve Midwest states', fontsize=9.5, color=MUTED)
    ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, p: f'{v:,.0f}'))
    for sp in ('top', 'right'): ax.spines[sp].set_visible(False)
    ax.spines['left'].set_color(GREY); ax.spines['bottom'].set_color(GREY)
    ax.tick_params(colors=MUTED); ax.grid(axis='y', color=GREY, alpha=0.35, lw=0.6)
    ax.legend(loc='upper center', bbox_to_anchor=(0.62, 0.76), frameon=False, fontsize=9, ncol=2)
    fig.text(0.01, 0.975, 'Mid year note under review: weekly claims and the two windows', fontsize=11.5, color=INK, fontweight='bold')
    fig.text(0.01, 0.948, f'The label gives {lab[0]:,} against {lab[1]:,} ({lab_pc} percent). The published {bas[0]:,} against {bas[1]:,} ({bas_pc} percent) '
             f'reproduces on the window one week later.', fontsize=9.2, color=MUTED)
    fig.text(0.01, 0.924, 'The first week of each year leaves that window and the first week of July enters; the twenty five weeks between are the same in both.', fontsize=9.2, color=MUTED)
    fig.text(0.01, 0.012, 'Source: U.S. Department of Labor weekly state initial claims, regular program, as compiled by the Opportunity Insights Economic Tracker.',
             fontsize=8, color=MUTED)
    fig.tight_layout(rect=(0, 0.03, 1, 0.91))
    fig.savefig(os.path.join(HERE, 'weekly_claims_windows.png'), facecolor=SURF)

    # Memo
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    ss = getSampleStyleSheet()
    body = ParagraphStyle('b', parent=ss['Normal'], fontSize=9.6, leading=12.6)
    small = ParagraphStyle('s', parent=body, fontSize=8.4, leading=10.6, textColor=colors.HexColor(MUTED))
    h = ParagraphStyle('h', parent=ss['Heading3'], fontSize=11, spaceBefore=7, spaceAfter=3)
    title = ParagraphStyle('t', parent=ss['Title'], fontSize=15, leading=18, alignment=0, spaceAfter=2)
    def pr(x): return f'{x:,}'
    story = [
        Paragraph('Review of the mid year claims note of 10 July 2026', title),
        Paragraph('To: Publication committee &nbsp;&nbsp; From: Publications desk &nbsp;&nbsp; Date: 6 October 2026 &nbsp;&nbsp; Standard: published figures, review standard', small),
        Spacer(1, 6),
        Paragraph('Outcome', h),
        Paragraph(f"The figure is <b>reissued</b>. It does not reproduce on the basis its label gives, and the review establishes the basis it was "
                  f"computed on: the same twelve states and series, with each half year taken one week later than the label says, the weeks ending "
                  f"<b>10 January to 4 July 2026</b> against <b>11 January to 5 July 2025</b>. On that basis the statement reproduces in every number: "
                  f"<b>{pr(bas[0])}</b> against <b>{pr(bas[1])}</b>, a fall of <b>{bas_pc.lstrip('-')} percent</b>. We publish it again with that basis in its label, "
                  f"and beside it the figure on the basis of the original label: <b>{pr(lab[0])}</b> against <b>{pr(lab[1])}</b>, a fall of "
                  f"<b>{lab_pc.lstrip('-')} percent</b>, for the weeks ending 3 January to 27 June 2026 against 4 January to 28 June 2025. The figure does not stand "
                  f"and is not withdrawn.", body),
        Paragraph('The committee member\'s figures', h),
        Paragraph(f"They are right. On the basis the label gives, the record sums to {pr(lab[0])} for the first half of 2026 and {pr(lab[1])} for "
                  f"the first half of 2025, a fall of {lab_pc.lstrip('-')} percent. That is the figure published beside the reissued one, and the label on it is the "
                  f"label the note carried.", body),
        Paragraph('What the published figure measured and how it was established', h),
        Paragraph(f"Step (a) of the standard: the label's basis gives {pr(lab[0])}, {pr(lab[1])} and {lab_pc}, none of which equals the published "
                  f"number, so the figure does not stand. Step (b): the reviewer tested alternative specifications of the four elements of a basis, "
                  f"the states, the weeks in each period, the series column and the formula, against all three published numbers. Holding the twelve "
                  f"states, the regular program count column and the formula fixed and moving both windows one week later reproduces the statement "
                  f"exactly: {pr(bas[0])}, {pr(bas[1])} and {bas_pc}. No other specification tested reproduces the count {pr(bas[0])}: not the "
                  f"Department of Labor's Chicago and Kansas City regions in place of the Census region, not the window moved by any other number of "
                  f"weeks or made a week longer or shorter, not the twelve states less any one or two of them. The percentage alone is less selective: "
                  f"12.6 is also what the eleven states without Indiana give on the label's window ({pr(cands[('drop','18')][0])} against "
                  f"{pr(cands[('drop','18')][1])}), and what the ten states of the Chicago and Kansas City regions give on the later window "
                  f"({pr(cands[(1,26,'R5+R7')][0])} against {pr(cands[(1,26,'R5+R7')][1])}); neither carries the published totals, so under rule 3 "
                  f"neither is the basis. The later window is what a spreadsheet keyed by the Sunday a week begins produces when the half year is "
                  f"filtered on that date, and what the tracker's own revision note describes for its 2021 error, claims assigned to the report date "
                  f"rather than the week they reflect; which of these happened cannot be known without the working files, and the standard does not "
                  f"require it, since the basis is established by reproduction.", body),
        Paragraph('What the two bases exchange, week by week', h),
    ]
    rows_t = [['Year', 'Leaves the window', 'Claims', 'Enters the window', 'Claims', 'Net', 'Label total', 'Basis total']]
    rows_t.append(['2026', f'week ending {out26.strftime("%d %B")}', pr(ex[out26]), f'week ending {in26.strftime("%d %B")}', pr(ex[in26]),
                   f'{ex[in26]-ex[out26]:+,}', pr(lab[0]), pr(bas[0])])
    rows_t.append(['2025', f'week ending {out25.strftime("%d %B")}', pr(ex[out25]), f'week ending {in25.strftime("%d %B")}', pr(ex[in25]),
                   f'{ex[in25]-ex[out25]:+,}', pr(lab[1]), pr(bas[1])])
    t = Table(rows_t, colWidths=[0.5 * inch, 1.45 * inch, 0.65 * inch, 1.45 * inch, 0.65 * inch, 0.7 * inch, 0.85 * inch, 0.85 * inch])
    t.setStyle(TableStyle([('FONTSIZE', (0, 0), (-1, -1), 8.4), ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                           ('LINEBELOW', (0, 0), (-1, 0), 0.6, colors.HexColor(GREY)), ('ALIGN', (2, 1), (-1, -1), 'RIGHT'),
                           ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5), ('TOPPADDING', (0, 0), (-1, -1), 2.5)]))
    story += [t, Spacer(1, 4),
        Paragraph(f"Twenty five of the twenty six weeks are the same in both bases. The week that leaves is the first week of the year, which carries "
                  f"the post holiday surge in filings ({pr(ex[out26])} in 2026, {pr(ex[out25])} in 2025), and the week that enters is the first week of "
                  f"July, a low week ({pr(ex[in26])} and {pr(ex[in25])}). The exchange lowers both totals, 2026 by {ex[out26]-ex[in26]:,} and 2025 by "
                  f"{ex[out25]-ex[in25]:,}, and because the 2026 total loses more in proportion the fall deepens from {lab_pc.lstrip('-')} to {bas_pc.lstrip('-')} percent. "
                  f"The record has one vintage in the workspace, the combined claims column is empty for every week since the pandemic programs ended, "
                  f"and the rate columns are per hundred of the 2019 labour force, so none of these accounts for the difference; the window does, "
                  f"exactly.", body),
        Paragraph('By state', h)]
    rows_s = [['State', 'Label 2026', 'Label 2025', 'Change %', 'Basis 2026', 'Basis 2025', 'Change %', 'Shift, points']]
    for r in rows:
        rows_s.append([r['name'], pr(r['l26']), pr(r['l25']), r['lp'], pr(r['b26']), pr(r['b25']), r['bp'], r['diff']])
    rows_s.append(['Midwest Region', pr(lab[0]), pr(lab[1]), lab_pc, pr(bas[0]), pr(bas[1]), bas_pc, rnd1(Decimal(bas_pc) - Decimal(lab_pc))])
    t2 = Table(rows_s, colWidths=[1.2 * inch, 0.85 * inch, 0.85 * inch, 0.7 * inch, 0.85 * inch, 0.85 * inch, 0.7 * inch, 0.8 * inch], repeatRows=1)
    mo = [i for i, r in enumerate(rows) if r['name'] == 'Missouri'][0] + 1
    t2.setStyle(TableStyle([('FONTSIZE', (0, 0), (-1, -1), 8.4), ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'), ('LINEBELOW', (0, 0), (-1, 0), 0.6, colors.HexColor(GREY)),
                            ('LINEABOVE', (0, -1), (-1, -1), 0.6, colors.HexColor(GREY)), ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
                            ('BACKGROUND', (0, mo), (-1, mo), colors.HexColor('#fde9df')),
                            ('BOTTOMPADDING', (0, 0), (-1, -1), 2), ('TOPPADDING', (0, 0), (-1, -1), 2)]))
    story += [t2, Spacer(1, 4),
        Paragraph(f"The state whose change moves most between the two bases is <b>Missouri</b>: a fall of {most['lp'].lstrip('-')} percent on the label "
                  f"and of {most['bp'].lstrip('-')} percent on the basis the note used, {most['diff']} points apart. In 2026 Missouri's first July week "
                  f"({pr(mo_w[in26])}) carried more claims than its first week of the year ({pr(mo_w[out26])}), while in 2025 the first week of the "
                  f"year ({pr(mo_w[out25])}) was the heavier of the two ({pr(mo_w[in25])} in July), so the exchange raises Missouri's 2026 total and "
                  f"lowers its 2025 total. North Dakota moves next most, "
                  f"{second['diff'].lstrip('-')} points the other way. No state changes direction: every state fell on both bases.", body),
        Paragraph('Reply to the committee member', h),
        Paragraph(f"Thank you for checking the note. Your figures are right: on the basis the note's label gives, the record shows {pr(lab[0])} "
                  f"against {pr(lab[1])}, a fall of {lab_pc.lstrip('-')} percent. The review under the office's standard found that the published numbers were "
                  f"computed on windows one week later than the label, the weeks ending 10 January to 4 July 2026 against 11 January to 5 July 2025, "
                  f"on which they reproduce exactly. Under the standard the figure is reissued rather than withdrawn: it will be published again with "
                  f"that basis in its label, with the figure on the original label, your figure, beside it, and the difference accounted for week by "
                  f"week as above.", body),
    ]
    doc = SimpleDocTemplate(os.path.join(HERE, 'figure_review_memo.pdf'), pagesize=letter, leftMargin=0.8 * inch, rightMargin=0.8 * inch,
                            topMargin=0.7 * inch, bottomMargin=0.7 * inch, title='Review of the mid year claims note', author='Publications desk')
    doc.build(story)
    print('label', lab, lab_pc, 'basis', bas, bas_pc, 'exchange', ex, 'most', most['name'], most['diff'], 'pct matches', pct_matches)

if __name__ == '__main__':
    main()

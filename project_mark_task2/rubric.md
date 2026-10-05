# Rubric (100 points). Grader-only. Task: Harbor & Pine channel budget

Ground truth: `author/world_truth.json` (data-generating parameters) and `author/reference_outputs/` (reference estimates and ledger). The correct pick is the channel with the highest incremental contribution per marginal dollar at current run-rate: **Meta Lead Ads**. Tolerances reflect honest estimation noise, so a correct method should land inside them.

## Deliverable 1: lead ledger CSV (30 pts)
| # | Check | Pts |
|---|-------|-----|
| 1 | One row per person with an id, first-touch date and channel, deal outcome and contribution to date. | 3 |
| 2 | Unique persons 54,073 (+/-2.5%), i.e. duplicates across forms, calls and contact records merged on email or phone+surname, short and unanswered calls excluded, and different people sharing a phone not blindly merged. | 7 |
| 3 | Persons by first-touch channel within +/-3% (organic +/-8%) for at least 5 of 6: meta 11,288; brand 11,166; lsa 9,535; nonbrand 6,159; retarget 3,671; organic 12,254. Source label drift mapped (e.g. "GAds NB" = non-brand) and tracking numbers mapped for calls. | 7 |
| 4 | Window cohort (first touch 1 Jul - 30 Sep 2025): 7,859 persons, by channel meta 1,630; brand 1,686; lsa 1,365; nonbrand 928; retarget 558; organic 1,692 (each +/-6%). Pre-July timestamps (Central local time) converted correctly. | 4 |
| 5 | Deals and jobs linked to persons: about 16,250 completed jobs linked (+/-3%), including jobs missing a deal id matched by phone/name. | 4 |
| 6 | Contribution to date per job = revenue minus materials, labour at USD 48/h, tiered commission (5% / 8% / 12% bands), card fees 2.9% + 0.30, and refunds/chargebacks. Total contribution to date about USD 4.83M (+/-5%). | 5 |

## Deliverable 2: one-page PDF (70 pts)
| # | Check | Pts |
|---|-------|-----|
| 7 | Recommends **Meta Lead Ads** as the single channel. Anything else scores 0 here. | 20 |
| 8 | Next-dollar incremental contribution per dollar: meta ~1.66 (1.15-2.15), non-brand ~1.06 (0.70-1.40), lsa ~1.11 (0.75-1.45), each within the band (3 pts each); brand and retargeting each below 1.0 (1.5 pts each). | 12 |
| 9 | Incrementality from the geo holdout (difference-in-differences vs control clusters, allowing for the test clusters being higher-volume): brand incremental share well under 0.5 (truth 0.30) and retargeting under 0.75 (truth 0.45); other channels treated as 100%. | 8 |
| 10 | Maturity adjustment for recent leads still closing: Meta's 13-week cohort is only about 47% mature (0.35-0.60); current Meta win rate about 0.22 (0.17-0.27) after adjustment, against about 0.10 unadjusted. | 8 |
| 11 | Response to spend is marginal, not average, with seasonality controlled: elasticities within +/-0.15 of truth for at least 4 of 5 channels (brand 0.30, non-brand 0.70, meta 0.75, lsa 0.40, retargeting 0.45); LSA's elasticity not inflated above ~0.50 by the season-spend correlation. | 8 |
| 12 | Per-job contribution within +/-20%: meta ~USD 535, non-brand ~USD 343 (refunds developed to maturity, commission by band, labour hours priced). | 6 |
| 13 | The walk from platform-reported conversions / attributed ROAS to the final measure shows which adjustment moves each channel (e.g. Brand drops after incrementality; LSA drops from average to marginal; Meta rises after maturity). | 4 |
| 14 | Chart: next-dollar return by channel, pick marked, winning channel in the title. | 4 |

## Wrong answers (each loses item 7 and cascades)
| Shortcut | Channel recommended |
|---|---|
| Rank by platform-reported or attributed average ROAS | Brand search |
| Ignore the holdout (treat everything as incremental) | Brand search |
| Do not adjust recent cohorts for open deals | Non-brand search |
| Use average (not marginal) returns | Local Services Ads |
| Do not control for seasonality in the response curve | Local Services Ads (inflated elasticity) |

import json, os
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
HERE = os.path.dirname(os.path.abspath(__file__))
gt = json.load(open(os.path.join(HERE, "reference_outputs", "ground_truth.json")))
r = gt["results"]; order = ["zapier", "make", "n8n"]; lab = {"zapier": "Zapier", "make": "Make", "n8n": "n8n"}
fig = plt.figure(figsize=(8.27, 11.69))
fig.text(0.08, 0.94, "Recommendation: standardise on Zapier", fontsize=18, weight="bold")
fig.text(0.08, 0.905, f"Lowest 12-month cost (Nov 2025 - Oct 2026): EUR {r['zapier']['total_eur']:,.0f}, "
         f"vs n8n EUR {r['n8n']['total_eur']:,.0f} and Make EUR {r['make']['total_eur']:,.0f}.", fontsize=10.5)
ax = fig.add_axes([0.1, 0.52, 0.8, 0.34])
bot = [0, 0, 0]
for key, name, col in [("subscription_eur", "Subscription", "#3b6ea5"), ("overage_eur", "Overage", "#e0a030"), ("migration_eur", "Migration labour", "#8a8f98")]:
    vals = [r[p][key] for p in order]
    ax.bar([lab[p] for p in order], vals, bottom=bot, label=name, color=col)
    bot = [b + v for b, v in zip(bot, vals)]
for i, p in enumerate(order): ax.text(i, bot[i] + 600, f"EUR {r[p]['total_eur']:,.0f}", ha="center", fontsize=10, weight="bold")
ax.set_ylabel("EUR, 12 months"); ax.legend(frameon=False); ax.spines[["top", "right"]].set_visible(False)
ax.set_ylim(0, max(bot) * 1.15)
txt = (f"How the numbers were built\n"
       f"- {gt['conformed_total_runs']:,} business runs in Oct 2024 - Sep 2025 after de-duplicating export batches, removing retries, replays, tests, "
       f"parallel-run mirrors and incident duplicates, and dropping sandbox items.\n"
       f"- Forward volume repeats the same calendar months; {len(gt['churned_clients'])} churned clients are excluded ({gt['active_workflows']} workflows in scope).\n"
       f"- Zapier plan: {r['zapier']['plan_allowance']:,} tasks/month (annual billing, 20% off); Make plan: {r['make']['plan_allowance']:,} ops/month "
       f"(+14% from Jan 2026); n8n plan: {r['n8n']['plan_allowance']:,} executions/month (peak month {r['n8n']['peak_month_units']:,.0f}).\n"
       f"- Migration: {r['zapier']['migration_workflows']} workflows to Zapier ({r['zapier']['migration_hours']:,.0f} h), "
       f"{r['make']['migration_workflows']} to Make ({r['make']['migration_hours']:,.0f} h), {r['n8n']['migration_workflows']} to n8n ({r['n8n']['migration_hours']:,.0f} h) at EUR 30/h.\n"
       f"- USD converted at EURUSD {gt['eurusd']}.\n"
       f"Zapier is the most expensive subscription but the cheapest platform to move into at this volume. The margin over n8n (runner-up) is about 10%; year-two economics may favour n8n.")
import textwrap
y = 0.46
for para in txt.split("\n"):
    for line in textwrap.wrap(para, 105, subsequent_indent="   "):
        fig.text(0.08, y, line, fontsize=9.5, weight="bold" if para.startswith("How") else "normal"); y -= 0.018
fig.savefig(os.path.join(HERE, "reference_outputs", "reference_recommendation.pdf"))
print("pdf ok")

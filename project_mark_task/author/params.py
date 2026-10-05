"""Shared constants used to write the PDFs/DOCX and by the reference solution."""
MAKE_TIERS = [  # ops/month, EUR/month, overage EUR per 1,000 ops
    (250_000, 1320, 6.30), (500_000, 2440, 5.60), (1_000_000, 4400, 4.90), (2_000_000, 7690, 4.20)]
ZAP_TIERS = [  # tasks/month, USD/month list (monthly billing)
    (100_000, 1500), (200_000, 2750), (300_000, 4000), (500_000, 6000), (750_000, 8250)]
N8N_TIERS = [  # executions/month, EUR/month (annual prepay price)
    (50_000, 220), (100_000, 390), (250_000, 790), (500_000, 1390)]
MAKE_INCREASE = 0.14          # from 2026-01-01
ZAP_ANNUAL_DISCOUNT = 0.20
ZAP_OVERAGE_MULT = 1.25
RATE_EUR_PER_HOUR = 36
HOURS = {  # base, per node
    "zapier": (0.6, 0.12), "make": (2.0, 0.40), "n8n": (3.0, 0.55)}
CUSTOM_BUILD_HOURS = 8

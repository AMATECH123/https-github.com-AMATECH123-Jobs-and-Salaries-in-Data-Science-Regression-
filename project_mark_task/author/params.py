"""Shared constants used to write the PDFs/DOCX and by the reference solution."""
MAKE_TIERS = [  # ops/month, EUR/month, overage EUR per 1,000 ops
    (250_000, 1716, 8.19), (500_000, 3172, 7.28), (1_000_000, 5720, 6.37), (2_000_000, 10000, 5.46)]
ZAP_TIERS = [  # tasks/month, USD/month list (monthly billing)
    (100_000, 1500), (200_000, 2750), (300_000, 4000), (500_000, 6000), (750_000, 8250)]
N8N_TIERS = [  # executions/month, EUR/month (annual prepay price)
    (50_000, 880), (100_000, 1560), (250_000, 3160), (500_000, 5560)]
MAKE_INCREASE = 0.14          # from 2026-01-01
ZAP_ANNUAL_DISCOUNT = 0.20
ZAP_OVERAGE_MULT = 1.25
RATE_EUR_PER_HOUR = 30
HOURS = {  # base, per node
    "zapier": (0.6, 0.12), "make": (2.0, 0.40), "n8n": (2.0, 0.40)}
CUSTOM_BUILD_HOURS = 8
MAKE_NEGOTIATED = {250_000: 1534}   # contract overrides quote for this plan (EUR/month)

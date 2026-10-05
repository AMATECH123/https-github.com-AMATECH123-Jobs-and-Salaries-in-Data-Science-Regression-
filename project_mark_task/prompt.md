# Task prompt (what the model sees)

Dana (our COO) wants a decision before our Make, Zapier and n8n subscriptions all renew on 1 November: do we standardise on one of them for the next 12 months, and if so which? Everything I could pull together is in the folder (usage exports, vendor quotes, contract notes, and Finance's costing standard). I'm tired of three exports that don't agree with each other, so I need two things:

1. One clean usage dataset Finance can trust, as a CSV, conformed across the three platforms so it can be sliced by workflow, client and month.
2. A one-page PDF for Dana with your recommendation, what it will cost over the next 12 months compared with the alternatives, and a chart that makes the comparison obvious.

Dana will read the PDF and nothing else, so it has to stand on its own.

---
Inputs: everything in `inputs/` (14 files: csv x6, json, xlsx x2, pdf x2, docx, txt, md).
Expected outputs: 1 x CSV (conformed usage), 1 x PDF (one page, with chart).

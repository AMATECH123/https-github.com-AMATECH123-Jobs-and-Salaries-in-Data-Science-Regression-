# Data notes (Internal Audit, 1 Oct 2025)

Extracts cover 1 Jan 2024 - 30 Sep 2025. Synthetic data.

- `ap_invoices.csv` - AP invoice register (invoices and credit memos). `vendor_id` is the id in force on the invoice date. `invoice_no` is as typed.
- `payments.csv` - treasury payments. `invoice_ref` is the invoice number as typed on the payment run. Dates are MM/DD/YYYY. `payment_type` REFUND_IN is money received back.
- `vendor_master.xlsx` - vendors (current and legacy ids), status history, related-party register, block overrides.
- `bank_change_requests.json` - bank account change requests with call-back flags.
- `purchase_orders.csv`, `goods_receipts.csv` - procurement and receiving.
- `hr_employees.csv`, `hr_payroll_accounts.json` - HR and payroll bank accounts.
- `contracts_register.xlsx` - contracts and amendments.
- `delegation_of_authority.pdf`, `audit_programme_v2.docx`, `change_log.txt` - as named.

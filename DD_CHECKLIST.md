# QOE Audit Checklist — Tricon Transportation, Inc.

*Prepared as a QOE Analyst. Items are grouped by workstream and prioritized by materiality risk.*

---

## 1. REVENUE BUILD-UP & TIE-OUT TO P&L

**Objective:** Prove every dollar of revenue is real, recorded in the right period, and ties to source documents.

- [ ] **Invoice-Level Revenue Build-Up**
  - Extract all AR invoices by entity (TTI, TK, TFS, etc.) for the LTM and historical periods
  - Build running total: `SUM(Invoice Amount) by month` → compare to P&L "Gross Trucking Income" and "TFS Revenue" lines
  - Variance should be ≤ 1% or explained (timing, credit memos, unapplied cash)

- [ ] **Revenue Recognition Cut-Off Testing**
  - Select 25 invoices from the last 5 days of each fiscal year-end and first 5 days of the next period
  - Verify ship/delivery dates vs. invoice dates — any revenue pulled forward or pushed back?

- [ ] **Credit Memos & Adjustments**
  - Scan for abnormal credit memo volume or timing (especially post-year-end)
  - Flag any credits issued >30 days after original invoice without clear support

- [ ] **Revenue by Service Line Tie-Out**
  - Break down P&L revenue lines (Container Drayage, FTL, LTL, Transload, Warehouse, etc.)
  - Cross-check to invoice line items — does the mix match?

- [ ] **Rate Variance Analysis**
  - Calculate avg revenue per load by customer, by month
  - Flag customers with >20% rate drops or spikes (could signal channel stuffing or misclassification)

---

## 2. CASH TIE-OUT (GL ↔ BANK STATEMENTS)

**Objective:** Every cash movement in the GL is supported by a bank statement line and vice versa.

- [ ] **Bank-to-GL Reconciliation**
  - For each bank account (BMO-TTICorp, BMO-TTIPark, CNB-TTICorp2, TK-Investments, TWS-Warehouse):
    - Roll forward: `Beginning Balance + Deposits - Withdrawals = Ending Balance`
    - Compare to GL cash account ending balances by month
  - Flag unreconciled differences >$500 or >0.1% of account balance

- [ ] **Outstanding Deposits & Checks**
  - List deposits-in-transit and outstanding checks >30 days old
  - Are they real? Or are they stale items being carried to inflate cash?

- [ ] **Cash Concentration / Sweep Activity**
  - Trace inter-account transfers between the 5 bank accounts
  - Verify no "round-tripping" (same dollars moving in circles to inflate activity)

- [ ] **Unidentified / Unapplied Cash**
  - Flag any bank deposits with vague descriptions ("ACH DEPOSIT", "WIRE IN") that don't tie to a named customer remittance
  - Map to AR ledger where possible

- [ ] **Missing Bank Statement Coverage**
  - Confirm we have statements for 100% of days in the audit period
  - Document coverage gaps (we already know BMO-TTICorp 2025 is summary-only)

---

## 3. SUBCONTRACTED SERVICES TIE-OUT (COGS / INTERCOMPANY)

**Objective:** Ensure subcontractor costs are real, properly classified, and intercompany transactions net correctly.

- [ ] **Subcontracted Services Build-Up**
  - Extract all payments to subcontractors from AP ledger
  - Tie to COGS "Subcontracted Services" line in P&L
  - Verify 1099 recipients match subcontractor payments (tax compliance check)

- [ ] **Intercompany Subcontractor Verification**
  - Identify vendors that are related parties (TFS, TK, TTIO, TTIM, TTIW, etc.)
  - For each interco payment:
    - Does the payee record matching revenue on their books?
    - Are rates at arm's length vs. third-party subcontractors?
  - Net intercompany payables/receivables — should sum to ~$0 across the consolidated group

- [ ] **Margin Analysis by Job**
  - Where possible, match subcontractor cost to specific customer invoice
  - Calculate gross margin per load — flag negative-margin jobs or jobs where subcontractor cost = 100% of revenue (pass-through risk)

- [ ] **Subcontractor Concentration**
  - Top 10 subcontractors by dollar
  - Any single sub >20% of total COGS? (concentration risk)

---

## 4. FREIGHT SERVICE / OPEX TIE-OUT (AP-LEVEL)

**Objective:** The largest operating expense ties to actual vendor invoices and doesn't contain personal or non-business spend.

- [ ] **Freight Cost Build-Up**
  - Extract all AP invoices coded to "Freight Cost" or similar OPEX accounts
  - Build `SUM(Invoice Amount) by month` → tie to P&L "Freight Cost" line
  - Variance should be ≤ 1%

- [ ] **Vendor Invoice Testing**
  - Select 30–50 freight vendor invoices (stratified by dollar amount)
  - Verify: vendor name, invoice date, description, amount, approval signature, PO match (if applicable)
  - Confirm no duplicate payments

- [ ] **Personal vs. Business Spend**
  - Scan freight expense for personal indicators (vendor names with personal names, non-business addresses, meal/entertainment vendors misclassified as freight)
  - Flag any freight payments to employee-related entities

- [ ] **Freight Cost per Load / per Mile**
  - Calculate freight cost per load by month and by customer
  - Flag abnormal spikes (could signal undisclosed subcontractor markups or cost allocation errors)

- [ ] **Accrual vs. Cash Timing**
  - Compare freight expense in P&L to actual cash paid for freight in bank statements
  - Large gaps = accrual timing issues or unrecorded payables

---

## 5. CUSTOMER CONCENTRATION ANALYSIS

**Objective:** Understand revenue risk and look for customer-side red flags.

- [ ] **Revenue by Customer (Top 20)**
  - Build customer-level revenue for LTM and prior years
  - Calculate concentration: Top 1, Top 5, Top 10 as % of total revenue
  - Any customer >20%? Any customer >50%? (risk escalation)

- [ ] **Customer Credit & Payment Trends**
  - AR aging by customer — any >90 days?
  - Days Sales Outstanding (DSO) by customer, by month
  - Customers with slowing payments or increasing disputes

- [ ] **Customer-Vendor Overlap**
  - Any customer that is also a vendor? (could signal round-trip revenue)
  - Cross-check customer names against subcontractor and freight vendor lists

- [ ] **Related-Party Customers**
  - Identify customers that are owned/controlled by management, family, or other group entities
  - Verify pricing and terms are at arm's length

- [ ] **Revenue per Customer per Load**
  - Calculate avg revenue per load by top 10 customers
  - Flag customers with abnormally high or low rates vs. portfolio average

---

## 6. WAREHOUSE INTERCOMPANY VERIFICATION

**Objective:** The warehouse subsidiary (TWS) and intercompany warehouse charges are properly recorded and eliminated.

- [ ] **Warehouse Revenue Build-Up**
  - Extract all "WAREHOUSE CHARGE TTIO" / "Warehouse TTIM" / "WAREHOUSE" invoices
  - Tie to P&L warehouse revenue lines
  - Verify customers are predominantly intercompany entities vs. third-party

- [ ] **Intercompany Warehouse Charge Reconciliation**
  - Compare warehouse revenue booked by TWS to warehouse expense booked by TTIO/TTIM
  - Do the amounts match? (Should eliminate to $0 on consolidation)
  - Flag any markup or margin retained at TWS level

- [ ] **Warehouse Cost Allocation**
  - Verify rent, labor, and utilities for warehouse are properly allocated between TWS and parent
  - Check for double-counting of warehouse costs in both COGS and OPEX

- [ ] **TWS Bank Account Activity**
  - Review TWS-Warehouse bank statements (959089530) for non-warehouse transactions
  - Is TWS handling any revenue/cash that should be on TTI's books?

---

## 7. LEASE & FINANCING VERIFICATION

**Objective:** All debt, leases, and equipment financings are on the balance sheet and properly classified.

- [ ] **Debt & Lease Schedule Build**
  - Extract all loans/leases from GL: 2004 Kalmar, 2022 FTLR Tractor&Upfit, 2020 Porsche Macan, 2020 Freightliners, Community Bank note, Note Payable 421, Line of Credit
  - Build amortization schedule for each: Original Principal, Interest Rate, Monthly Payment, Current Balance, Maturity Date

- [ ] **Balance Sheet Tie-Out**
  - Current portion of long-term debt vs. GL balance
  - Interest expense in P&L vs. calculated interest from debt schedule
  - Variance >2% requires explanation

- [ ] **New Leases / Financing (Current Period)**
  - Any new equipment purchases financed?
  - Properly capitalized under ASC 842? (Right-of-use asset + lease liability)
  - Or treated as operating leases? (common in trucking — verify policy consistency)

- [ ] **Debt Covenant Compliance**
  - If covenants exist, calculate actual ratios (DSCR, leverage, current ratio) vs. required
  - Any defaults or waivers? (critical for buyer risk)

- [ ] **Personal vs. Corporate Debt**
  - Are any of these loans personally guaranteed by owners?
  - Will debt survive a transaction, or must it be refinanced?

---

## 8. ADDITIONAL CRITICAL QOE WORKSTREAMS

### 8A. EBITDA NORMALIZATION & ADJUSTMENTS

- [ ] **Identify Non-Recurring Items**
  - One-time gains/losses, asset sales, insurance recoveries, lawsuit settlements
  - Remove from EBITDA and list as adjustments

- [ ] **Owner / Manager Compensation**
  - Is owner salary at market rate? If not, normalize to replacement cost
  - Any "consulting fees" to family members or related entities?

- [ ] **Personal Expenses Run Through Business**
  - Review GL for meals, travel, auto, fuel — any personal use?
  - Common in owner-operated trucking: personal vehicle fuel, family cell phones, owner travel
  - Quantify and add back to EBITDA (buyer won't incur these)

- [ ] **Rent (If Owner-Occupied)**
  - Is warehouse/office owned by a related entity and leased back?
  - Normalize to fair market rent if below/above market

### 8B. WORKING CAPITAL ANALYSIS

- [ ] **AR Aging & Collectability**
  - Full AR aging bucketed: Current, 31-60, 61-90, 91-120, 120+
  - Calculate allowance for doubtful accounts adequacy
  - Any large balances with customers known to be in distress?

- [ ] **Inventory / Prepaid Analysis**
  - Prepaid insurance: amortization schedule, any lapsed coverage?
  - Advanced payments: are these customer deposits or vendor prepaids?

- [ ] **AP & Accrued Liabilities**
  - AP aging — any past-due vendors that could disrupt operations?
  - Accrued payroll, profit sharing, bonuses: are they fully funded?

### 8C. PAYROLL VERIFICATION

- [ ] **Payroll Register to Bank**
  - Extract payroll totals from GL or payroll reports
  - Tie to bank statement payroll withdrawals
  - Verify tax remittances (federal, state, payroll taxes) match withholdings

- [ ] **Headcount & Wage Analysis**
  - Driver count vs. revenue per driver (productivity metric)
  - Wage inflation year-over-year
  - Any 1099 drivers misclassified as W-2? (huge liability risk)

### 8D. TAX EXPOSURE & COMPLIANCE

- [ ] **Open Tax Periods**
  - Are all federal/state tax returns filed?
  - Any audits, assessments, or notices outstanding?
  - Sales tax compliance (does Tricon charge/remit sales tax on warehouse/transload services?)

- [ ] **Employee vs. Independent Contractor Classification**
  - Review driver and warehouse worker classification
  - Any 1099 workers who function as employees? (IRS/DOL risk)

### 8E. ONE-TIME / NON-OPERATING ITEMS

- [ ] **Other Income / Other Expense**
  - Review P&L "Other" categories for non-operating items
  - Interest income, FX gains/losses, asset sales
  - Remove from EBITDA

### 8F. SEGMENT / ENTITY CONSOLIDATION

- [ ] **Multi-Entity P&L by Entity**
  - TTI, TK, TFS, TWS, TTIO, TTIM, TTIW — each should have standalone P&L
  - Verify intercompany eliminations between entities
  - Consolidated P&L should equal standalone P&Ls minus eliminations

- [ ] **Transfer Pricing Review**
  - Intercompany revenue/cost rates between entities
  - Arm's length? Any entity artificially shifting profit?

---

## 9. RED FLAGS / DEAL-KILLER CHECKLIST

*(These get immediate escalation to the deal team)*

- [ ] Revenue recognition appears aggressive (pre-billing, cut-off issues)
- [ ] Material bank statements missing or provided as summaries only
- [ ] Intercompany transactions don't net to zero across entities
- [ ] Customer concentration >50% with no long-term contract
- [ ] Personal expenses materially distort EBITDA (>5% of EBITDA)
- [ ] Debt covenant default or near-default
- [ ] Significant tax exposure (unfiled returns, worker misclassification)
- [ ] Cash doesn't tie to bank statements by >$10K in any month
- [ ] Negative gross margin jobs that aren't clearly pass-through
- [ ] Payroll tax remittances don't match withholdings (fraud indicator)

---

## 10. DELIVERABLES

- [ ] Revenue build-up workbook (invoice-level detail)
- [ ] Cash reconciliation by bank account by month
- [ ] Subcontractor / intercompany netting schedule
- [ ] Freight OPEX tie-out with sample invoice testing
- [ ] Customer concentration analysis (top 20, DSO trends)
- [ ] Warehouse intercompany elimination proof
- [ ] Debt & lease amortization schedule
- [ ] EBITDA normalization bridge (Reported → Adjusted)
- [ ] Working capital schedule (AR, AP, inventory, accruals)
- [ ] Red flag memo (if any)

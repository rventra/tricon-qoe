# Tricon QoE — Agent Context

## End Goal

Full cash tie-out for Tricon Transportation (TTI) and TK across **all years (2023–Q1 2026)** — prove that every dollar in the bank matches the General Ledger and vice versa, and explain every gap. This feeds into the broader intercompany audit (TTI ↔ TK) and supports the client's year-end financial close.

## Project Structure

```
Tricon QOE/
├── bank_to_gl_master/              # GL↔Bank reconciliation master folder
│   ├── 00_engine/                  # Matching engine script
│   ├── 01_data/                    # All source data
│   │   ├── bank/                   # Processed bank JSON
│   │   ├── gl/                     # Cash-account GL CSVs (matching engine input)
│   │   ├── gl_full/                # FULL GL — all accounts (not filtered to cash)
│   │   ├── pnl/                    # P&L detail
│   │   ├── balance_sheet/          # Balance sheet detail
│   │   ├── vendor_payments/        # Vendor payment registers
│   │   ├── payroll/                # Payroll PDF reports
│   │   └── ocr/                    # Textract pipeline outputs
│   ├── 02_outputs/                 # Recon CSVs, gut checks
│   ├── 03_docs/                    # Reports & specs
│   └── 04_analysis_scripts/        # Ad-hoc analysis scripts
├── data/                           # Raw & flat data (pipeline outputs)
│   ├── flat/                       # Processed JSON (bank, textract)
│   └── raw/                        # Raw OCR output, manifests
├── docs/                           # Supporting docs
│   └── schema.json
├── status_updates/                 # HTML status dashboards (Amplify-hosted)
│   ├── index.html                  # Main QoE status dashboard
│   ├── Cash_Reconciliation.html    # TTI net cash movement + AR aging
│   ├── Revenue_AR_TTI.html         # Accrual-to-cash revenue bridge
│   ├── Payroll_Register_Verification.html
│   ├── Credit_Card_Reconciliation.html
│   └── TK_Investment_Cash_Tieout.html / TTI_2024_Cash_Tieout.html / TWS_Warehouse_Cash_Tieout.html
├── CLAUDE.md                       # Project context & instructions
└── AGENTS.md                       # This file
```

**Critical distinction:** The matching engine uses `01_data/gl/` (cash accounts only: BMO, CNB, TFS-CNB). The full GL with all expense/revenue/BS accounts lives in `01_data/gl_full/`.

## What We've Done

### 1. GL→Bank Recon (All Years, TTI + TK)
Built a matching engine (`bank_to_gl_master/00_engine/matching_engine_all_years.py`) that reconciles TTI and TK GL cash entries against bank statements using:
- **EXACT** matching: check# + amount + date (±60d) + account
- **PROXIMITY** matching: amount + date (±60d) + account (no check# required)
- **Direction-aware routing**: GL outflows (check/payment) match bank outflows; GL deposits match bank inflows
- **Account filtering**: BMO GL → BMO bank only; CNB GL → CNB bank only; TK GL → TK bank only

**2023 BMO NO MATCH verification (May 28, 2026):** Systematic relaxed-search analysis of all 725 unmatched 2023 entries (after 60-day window) revealed that **~85% have a matching bank amount** — the primary failure mode is that GL "Payment" entries have no corresponding bank outflow record. The bank shows a deposit from the same vendor (same amount), but no withdrawal/check exists. Only **~15% are truly missing** bank records. The 60-day window recovered an additional 25 matches.

### 2. TK Cash-Account Filter
`load_tk_gl()` filters to `T-K Investments LLC -441394` only, excluding non-cash accounts (revenue, payroll, benefits) that have no bank counterpart. Raw TK GL has 1,005 rows; 730 are cash-account entries (2023–Q1 2026).

### 3. CNB Data Gap Documented
~~2025 CNB statements were originally provided as image-only PDF compilation without check detail pages.~~ **RESOLVED (May 26, 2026)**: Client provided transaction-level CNB 2025 statements (all 12 months). DeepSeek LLM extracted 1,672 transactions. CNB match rate improved from **2.7% → 58.2%**.

### 4. Three-Way Intercompany Audit
TTI P&L → TTI GL → TK P&L by year. 2023 ties perfectly ($1.19M), 2024 has a -$65,797 gap, 2025 has +$89,748 gap.

### 5. Payroll Three-Way Tie (May 2026)
Proved a complete three-way link between BBSi Payroll Registers → GL Expense accounts → GL Cash accounts for TTI and TK (2023–2025).

**Key finding**: The BBSi **Net Invoice** bundles gross wages, employer taxes, worker comp, benefit deductions, and fees into a single figure. Maps to `Split="Payroll"` (TTI) / `Split="Payroll Expenses"` (TK).

**Three-way tie results**:
| Entity | Year | PDF Net Invoice | GL Expense | GL Cash (Debits) | Delta |
|--------|------|----------------|------------|-----------------|-------|
| TTI | 2023 | $1,354,902.55 | $1,396,864.31 | $1,381,223.93 | +$26K (timing) |
| TTI | 2024 | $1,436,366.22 | $1,436,366.22 | $1,436,366.22 | $0 |
| TTI | 2025 | $1,567,284.08 | $1,567,804.08 | $1,567,804.08 | +$520 (reimb) |
| TK | 2023 | $1,093,526.19 | $1,093,426.19 | $1,093,426.19 | -$100 (+$762K WC) |
| TK | 2024 | $1,169,383.45 | $1,169,383.45 | $1,169,383.45 | $0 |
| TK | 2025 | $1,062,336.72 | $1,062,336.70 | $1,062,336.70 | -$0.02 (rounding) |

**TK 2023 note:** GL "Payroll Expenses" includes $762,640 in WC premiums (Jan-Sep). Actual BBSi payroll was $330,787 (Sep-Dec).

### 6. TK Deep-Dive (May 26, 2026)
Enriched Section 2 (TK) of Payroll_Tie_Out_Reports.md matching TTI-level detail:
- Pay type breakdown: REG-heavy (80-84%), no SAL — hourly driver workforce
- Employee roster: 19→15 (26% turnover, 5 departed, 1 new)
- Employer cost: simpler than TTI — no health insurance or profit sharing
- P&L = GL for all years (verified)
- WC premiums ($762K) coded as "Payroll Expenses" in 2023 GL
- 2024 bank statements missing; WC inflates 2023 bank matches

### 7. WC Mystery — Open Investigation (May 26, 2026)

**Key question**: Where did TK's $762K/yr in workers' comp premiums go in 2024/2025?

Search results across all data sources:
- TK GL 2024: 0 WC entries anywhere (across all accounts, splits, memos, names)
- TK GL 2025: 0 WC entries
- TK P&L 2024: Insurance Expense = $1,766 (general liability, not WC)
- TK P&L 2025: Insurance Expense = 0
- TTI GL 2024: 0 WC entries (17,450 entries searched)
- TTI GL 2025: 0 WC entries (only "WCS Permits" found — not workers comp)
- BBSi Billed excess ~$140K — cannot hold $762K WC

**TTI WC finding**: TTI GL 2022 Payroll split has 2 WC entries: $75,975 (9/23) and $41,852 (9/9) — spikes ~3x and 1.6x normal.

**Dashboard verification**: All TK PDF numbers confirmed accurate. Dashboard needs updating for anomalies (401K spikes, bonus patterns, WC gap).

### 8. Credit Card Roll-Forward & QoE Add-Back Hunt (May 26, 2026)

Parsed 54 Amex statements (27 Business Platinum `9-05006`, 27 Personal Platinum `6-02006`) from Jan 2024–Mar 2026 using Textract OCR + pure-Python parser.

**Parser fixes applied:**
- Fixed metadata extraction bug: `new_balance` / `previous_balance` were $0 because Y-search used `0 <= (yy - y)` instead of `abs(yy - y)`
- Fixed transaction-type bug: page 3 `payments` section leaked into `charges`, causing positive amounts to be mis-tagged as payments

**Critical accounting finding — GL workflow:**
The client does **NOT** maintain a credit card payable workflow. The "American Express" GL liability account had only **4 entries across ALL years** (static at ~$72,313 until a 12/31/2024 journal entry zeroed it out). Instead:
- Charges go directly to P&L expense accounts
- Payments flow directly from bank (BMO → CNB) to Amex with expense splits
- P&L reflects **payment date**, not purchase date

**TAX AJE #8 — $72K Amex liability write-off (12/31/2024):**
The $72,313 Amex liability was **not paid down with cash**. It was eliminated via year-end adjusting journal entry **TAX AJE #8** (*"To reconcile credit cards/advanced payments"*). The full $166,572 reclassification:

| Primary GL Account | Amount | Effect |
|---|---|---|
| American Express | **+$72,313** | Debit → liability ↓ |
| MasterCard | **+$27,114** | Debit → liability ↓ |
| Loan – 2×2020 Freightliners | **+$67,145** | Debit → liability ↓ |
| Advanced Payments | **–$102,683** | Credit → asset ↓ |
| Line of Credit | **–$63,889** | Credit → liability ↑ |

This was a **tax-basis clean-up** that consolidated three stale liabilities into a single Line of Credit increase and prepaid write-down. The Amex account then drifted to **–$29** by 12/31/2025 (a single $29 check from Amex → CNB on 11/13/2025).

**2023 data gap:**
- **No 2023 credit card statements** exist in the data room
- GL shows **$821,437 in Amex payments** via 52 Check/Bill Pmt entries
- Imputed charges = $821,887 (using BS delta)
- BS 2023 YE shows $99,427 total CC liability ($72,313 Amex + $27,114 MasterCard), but actual Dec 2023 statement balances were only **$44,132** ($41,968 Business + $2,164 Personal)
- BS overstated true Amex liability by ~$28K; MasterCard ($27,114) was stale/unchanged 2022–2024

**GL filter to identify CC payments:**
```
WHERE Name = "American Express"
  AND Type IN ("Check", "Bill Pmt -Check")
  AND Amount <> 0
```
This yields 295 entries / $3.6M total (2022–Q1 2026). Memo codes `-2006` (~$14K) and `5006` (~$666K) partially map to Personal/Business cards, but **86% have no card-identifying memo**.

**Deliverable:** `credit_cards/CC_Roll_Forward_Analysis_v2.xlsx` — 5 sheets (Cover, Roll-Forward Summary, Statement Detail, 2023 GL Reconstruction, Variance Analysis)

### 9. QoE Status Dashboards (Amplify)
Hosted at `https://d2ucc03atd4qn9.amplifyapp.com` (app `d2ucc03atd4qn9`, us-east-2).

- **`status_updates/index.html`** — Main QoE status dashboard. Shows net cash tie (-$3.6K on $4.25M), workstream status table, links to all detail pages.
- **`status_updates/Cash_Reconciliation.html`** — QoE-first cash reconciliation for TTI. Bank net movement vs GL net movement by year and month (39 months). Grand total: **$4.25M bank vs $4.25M GL, -$3,571 variance (0.08%)**. Also includes **AR Aging** (Current–>90, $2.17M total, 68% current/1–30, 17% >90 flagged) and transaction-level matching detail below the fold.
- **`status_updates/Revenue_AR_TTI.html`** — Accrual-to-cash revenue bridge. Gross Billed $55.1M → Implied Cash $55.85M → Cash Collections $55.86M (99.993% collection rate).
- **`status_updates/Payroll_Register_Verification.html`** — Payroll three-way verification dashboard (needs update for anomalies/WC gap).
- **`status_updates/Credit_Card_Reconciliation.html`** — Credit card reconciliation status.

### 10. Reports Maintained
- `bank_to_gl_master/03_docs/Bank_Statement_Tie_Out_Reports.md` — Full GL↔Bank tie-out with exec summaries, account breakdowns, per-year analysis
- `bank_to_gl_master/03_docs/matching_engine_specs.md` — Technical specs and parameters
- `payroll_tie_out/Payroll_Tie_Out_Reports.md` — Payroll three-way tie documentation
- `credit_cards/CC_GL_FILTER_SPEC.md` — GL filter spec for credit card payment identification

## Where The Data Lives

| Type | Location |
|------|----------|
| Bank JSON | `bank_to_gl_master/01_data/bank/BANK_DATA_PROCESSED.json` |
| TTI GL (cash only, CSV) | `bank_to_gl_master/01_data/gl/TTI_GEN_LEDGER_Flattened.csv` |
| TK GL (cash only, CSV) | `bank_to_gl_master/01_data/gl/TK_GEN_LEDGER_Flattened.csv` |
| TTI GL (full, all accounts, JSON) | `bank_to_gl_master/01_data/gl_full/TTI_GEN_LEDGER_Flattened.json` |
| TK GL (full, all accounts, JSON) | `bank_to_gl_master/01_data/gl_full/TK_GEN_LEDGER_Flattened.json` |
| TK P&L (flattened CSV) | `bank_to_gl_master/01_data/pnl/TK_P&L_Flattened.csv` |
| Payroll Registers (PDFs) | `bank_to_gl_master/01_data/payroll/` |
| Vendor Payments | `bank_to_gl_master/01_data/vendor_payments/` |
| Engine Script | `bank_to_gl_master/00_engine/matching_engine_all_years.py` |
| GL→Bank Recon TTI | `bank_to_gl_master/02_outputs/GL_to_Bank_Recon_All_Years_TTI.csv` |
| GL→Bank Recon TK | `bank_to_gl_master/02_outputs/GL_to_Bank_Recon_All_Years_TK.csv` |
| CC Parsed Statements | `credit_cards/PARSED_AMEX_STATEMENTS.json` |
| CC Roll-Forward Excel | `credit_cards/CC_Roll_Forward_Analysis_v2.xlsx` |
| CC GL Filter Spec | `credit_cards/CC_GL_FILTER_SPEC.md` |

## Current Match Rates (Verified) — Updated May 28, 2026

**Payment→AR direction fix applied (May 28, 2026).** GL "Payment" with Split="Accounts Receivable" is now correctly treated as INFLOW (deposit), matching bank deposits. TTI match rate improved from 79.5% → 92.7%. Date window: ±60 days.

**Bank data cleaned (May 28, 2026).** Removed 612 duplicate records from `BANK_DATA_PROCESSED.json` — 497 exact duplicates + 115 near-duplicates. CNB deposits now tie to reference. TTI match rate: 92.7% → 91.9% (more accurate).

### TTI — Overall 91.9%

| Year | Entries | EXACT | PROXIMITY | NO MATCH | Match Rate | GL Net $ | Matched Net $ | Unmatched Net $ |
|------|---------|-------|-----------|----------|-----------|----------|--------------|----------------|
| 2023 | 3,029 | 918 | 1,881 | 230 | **92.4%** | +$1.56M | +$2.10M | -$0.54M |
| 2024 | 2,939 | 1,298 | 1,405 | 236 | **92.0%** | +$1.40M | -$0.91M | +$2.31M |
| 2025 | 3,054 | 1,845 | 982 | 227 | **92.6%** | +$1.39M | +$2.06M | -$0.67M |
| 2026 | 791 | 439 | 227 | 125 | **84.2%** | +$0.15M | +$0.43M | -$0.28M |
| **Total** | **9,813** | **4,500** | **4,515** | **798** | **91.9%** | **+$4.50M** | **+$3.68M** | **+$0.82M** |

**Why the match rate is not 100%:**
- **~30%** are checks clearing after 60 days
- **~25%** are non-cash entries (year-end accruals, -SPLIT- QB artifacts)
- **~25%** are greedy matching (more GL entries than bank records for same amount)
- **~20%** are direction mismatches correctly rejected by engine

### TTI — By Account (per Year)

| Year | Account | Entries | EXACT | PROXIMITY | NO MATCH | Match Rate | GL $M |
|------|---------|---------|-------|-----------|----------|-----------|-------|
| 2023 | BMO Corporate Account - Other | 3,029 | 918 | 1,881 | 230 | **92.4%** | +$1.56M |
| 2024 | BMO Corporate Account - Other | 2,771 | 1,288 | 1,414 | 69 | **97.5%** | -$0.77M |
| 2024 | CNB Corp. | 168 | 16 | 25 | 127 | **24.4%** | +$2.17M |
| 2025 | BMO Corporate Account - Other | 741 | 181 | 538 | 22 | **97.0%** | +$0.10M |
| 2025 | CNB Corp. | 2,312 | 1,668 | 474 | 170 | **92.6%** | +$1.28M |
| 2025 | Tricon Freight Services - CNB | 1 | 0 | 0 | 1 | **0.0%** | +$6.5K |
| 2026 | BMO Corporate Account - Other | 88 | 4 | 80 | 4 | **95.5%** | +$0.34M |
| 2026 | CNB Corp. | 703 | 451 | 157 | 95 | **86.5%** | -$0.19M |

### TK — Overall 96.0%

| Year | Entries | EXACT | PROXIMITY | NO MATCH | Match Rate | GL Net $ | Bank Net $ |
|------|---------|-------|-----------|----------|-----------|----------|------------|
| 2023 | 222 | 22 | 194 | 6 | **97.3%** | -$6.3K | +$15.6K |
| 2024 | 212 | 23 | 185 | 4 | **98.1%** | -$46.2K | +$19.8K |
| 2025 | 197 | 19 | 165 | 13 | **93.4%** | +$78.6K | +$20.0K |
| 2026 | 48 | 4 | 40 | 4 | **91.7%** | -$3.4K | -$3.3K |
| **Total** | **679** | **68** | **584** | **27** | **96.0%** | **+$22.7K** | **+$52.2K** |

## Known Data Gaps (Client-Confirmed)

Per Jacob Sidaros (Benchmark, May 22 2026):

- **BMO-TTIPark (#696) 2024** — Missing, client doesn't have 2024 statements (covered by BMO-TTICorp)
- ~~**TK-Investments (#394) 2024** — Missing~~ **RESOLVED**: All 12 months received and extracted. TK 2024 match rate: **97.2%**
- ~~**CNB-TTICorp2 (#7740) 2025** — Image-only compilation~~ **RESOLVED**: Transaction-level statements received and extracted. CNB 2025 match rate: **65.5%**
- **BMO-TTICorp (#2724) 2026** — Partially resolved: Jan–Apr 2026 received. May+ still pending
- **CNB-TTICorp2 (#7740) 2026** — No 2026 statements received yet

## Key Accounts

| Account | # | Entity | Bank Recs | GL Entries | Match Rate | Status |
|---------|---|--------|-----------|-----------|-----------|--------|
| BMO (TTICorp+TTIPark) | 2724 / 6696 | TTI | 7,028 | 6,629 | **95.1%** | Active |
| CNB-TTICorp2 | 248017740 | TTI | 3,370 | 3,183 | **87.7%** | Resolved |
| TWS-Warehouse | 959089530 | TTI | 189 | 0 | N/A | No GL mapping |
| TK-Investments | 037441394 | TK | 711 | 679 | **96.0%** | Resolved |

## Next Steps

- ~~Obtain CNB 2025 detailed check-level statements from client~~ **DONE** — transaction-level statements received, match rate improved from 2.7% → 58.2%
- ~~Request TK-Investments 2024 bank statements from client~~ **DONE** — all 12 months received, match rate improved from 0.5% → 97.2%
- Investigate 2024 TTI↔TK intercompany gap (-$65,797)
- Reconcile outstanding -SPLIT- bundled deposit artifacts (~$1.5M)
- Implement Bank→GL direction (reverse recon) for all years
- Request BMO-TTICorp 2026 statements as they become available
- Request **2023 Amex credit card statements** from client (currently missing; $821K GL payments unverifiable)
- ~~Clarify **2025 BS Amex liability = -$29**~~ — **Resolved**: TAX AJE #8 wrote off $72K on 12/31/2024; only residual $29 check remains by 12/31/2025
- ~~Investigate stale **MasterCard $27,114**~~ — **Resolved**: Also written off via TAX AJE #8 on 12/31/2024; MasterCard no longer appears on 12/31/2025 BS
- **Request client's workpapers and tax-team rationale for TAX AJE #8** — $166K of liability disappeared without cash outflow; need to confirm no personal/shareholder charges treated as company payable
- Optionally pursue Bank Statement (Leg 3): prove GL Cash → actual Bank Statement outflow for payroll

# Tricon QoE — Website Documentation

## Overview

Static HTML status dashboard hosted on **AWS Amplify** for the Tricon Transportation Quality of Earnings engagement. All pages are hand-written HTML (no framework) with inline CSS. Deployed via Git push to `master` → Amplify auto-build.

---

## Architecture

| Component | Detail |
|---|---|
| **Host** | AWS Amplify (`d2ucc03atd4qn9.amplifyapp.com`) |
| **Region** | us-east-2 |
| **Profile** | `northcastle` (AWS CLI) |
| **Repo** | `https://github.com/rventra/tricon-qoe` |
| **Branch** | `master` |
| **Build spec** | Inline in Amplify app (not `amplify.yml` in repo) |
| **Base directory** | `.` (repo root) |
| **Files pattern** | `'**/*'` (single-quoted, critical) |

### Build Spec (stored in Amplify, NOT in repo)
```yaml
version: 1
frontend:
  phases:
    build:
      commands: []
  artifacts:
    baseDirectory: .
    files:
      - '**/*'
  cache:
    paths: []
```

**CRITICAL:** The `files` pattern must be single-quoted `'**/*'`. Unquoted `**/*` causes `CustomerError: Unable to parse build spec`.

### Custom Rule (404 → index.html)
```json
{
  "source": "/<*>",
  "target": "/index.html",
  "status": "404-200"
}
```

### Root Redirect
`index.html` (repo root) is a meta refresh to `status_updates/index.html`:
```html
<meta http-equiv="refresh" content="0; url=status_updates/index.html">
```

**Note:** The Amplify default domain is `master.d2ucc03atd4qn9.amplifyapp.com`. The bare `d2ucc03atd4qn9.amplifyapp.com` may 404 — always use the `master.` prefix when sharing URLs.

---

## File Structure

```
status_updates/
├── index.html                      # Homepage / exec summary
├── Cash_Reconciliation.html        # TTI & TK cash recon (COMPLETE)
├── Revenue_AR_TTI.html             # Revenue & AR bridge
├── Payroll_Register_Verification.html  # Payroll three-way tie
├── Credit_Card_Reconciliation.html # CC reconciliation
├── NWC_Peg.html                    # Net Working Capital Peg (NEW)
├── EBITDA_Normalization.html       # EBITDA normalization (NEW)
├── Vendor_Payments_Freight.html    # Vendor payments & freight tie-out (NEW)
└── (other HTML files may exist)
```

### `index.html` — Homepage
- **Purpose:** Executive summary of all QoE workstreams
- **Style:** Simple table-based layout with badge statuses
- **Badges:** `badge-complete` (green), `badge-almost` (blue), `badge-progress` (yellow), `badge-hold` (gray)
- **Status pills:** In Progress / Not Started / Complete / Almost Complete counts
- **Links to:** All sub-pages via relative URLs

### `Cash_Reconciliation.html` — Cash Reconciliation
- **Status:** **COMPLETE** for TTI
- **Sections:**
  1. QoE Summary KPIs (Bank Net, GL Adjusted, Variance, Unexplained)
  2. Yearly Bank vs GL table (2023–Q1 2026)
  3. Cash Roll-Forward Proof (beginning/ending balances per bank statement)
  4. Grand Total card (dark background)
  5. Monthly accordion — TTI (click to expand)
  6. QoE Observations (4 observations)
  7. TK — Bank Net vs GL Net (yearly summary + monthly detail table)
  8. TK GL Cash Detail (checks vs deposits)
  9. TWS Warehouse — Net Activity by Year + monthly accordion
  10. Bank Statement Coverage matrix
  11. Matching Criteria
- **Key numbers:**
  - TTI Bank 39-mo: **+$2,878,994**
  - TTI GL Adjusted: **+$2,883,985**
  - TTI Variance: **-$4,991 (0.17%)**
  - Unexplained: **-$700K** (Sep 1–3 2023 bank switchover)
  - **TAX AJE #1: $1.59M Top-Side Tax Plug** — CPA booked on 12/31/2024 with no supporting docs to artificially force cash to match tax return. Signals severe internal bookkeeping failures. **Material internal control weakness.**
  - TK Bank: All 39 months received (Jan 2023–Mar 2026)
  - TK 2023 Bank Net: **-$5,327** | GL Net: **-$6,294** | Var: **+$967**
  - TK 2024 Bank Net: **+$19,813** | GL Net: **-$46,239** | Var: **+$66,052**
  - TK 2025 Bank Net: **+$13,647** | GL Net: **+$78,638** | Var: **-$64,991**
  - TK Q1 2026: Bank **-$3,336** vs GL **-$3,423** = **$87 variance**
  - TK Total Bank: **+$24,797** | GL: **+$22,682** | Var: **+$2,115**

### `Revenue_AR_TTI.html` — Revenue & AR
- **Status:** Almost Complete
- **Key numbers:**
  - Gross Billed Invoices: **$55.85M**
  - Cash Collections: **$55.86M**
  - Collection Rate: **99.993%**
  - Ending AR: **$2,165,993**
  - >90 Days: **$374,543**
  - Dormant credit reclass to AP: **($19,930)**
  - All revenue now classified — no unclassified bucket

### `Credit_Card_Reconciliation.html` — Credit Cards
- **Status:** Complete
- **Key findings:**
  - 54 AMEX statements parsed (2024–Q1 2026)
  - $1.28M spend categorized
  - $1.6M liability written off via TAX AJE #8 (12/31/2024)
  - 2023 statements missing — immaterial to QoE

### `Payroll_Register_Verification.html` — Payroll
- **Status:** Almost Complete
- **Covers:** TTI and TK three-way tie (PDF registers → GL Expense → GL Cash)

### `NWC_Peg.html` — Net Working Capital Peg (NEW)
- **Status:** **COMPLETE**
- **Locked Peg:** **$1,984,123** (TTM average, cash-free debt-free basis)
- **Observation period:** 24 months (Jan 2024 – Dec 2025)
- **Methodology:**
  - Operating Current Assets = A/R + Advance Payments + Undeposited Funds
  - Operating Current Liabilities = A/P + Credit Card liabilities
  - **Adjustment 1:** $19,930 flat monthly reclassification (ancient negative A/R → A/P)
  - **Adjustment 2:** $374,543 bad debt waterfall (removed chronologically by invoice vintage)
- **Key stats:**
  - Avg Op. Current Assets: **$2.32M**
  - Avg Op. Current Liabilities: **$313K**
  - Avg Asset Adjustment: **$169K**
  - Avg Liability Adjustment: **$19.9K**
- **Related-party flag:** $99,682 TK Loan Receivable discovered and stripped from NWC
- **Cash exclusion note:** Standard M&A practice — seller retains cash at closing
- **Monthly detail table:** All 24 months with Beginning/Ending/Net Delta

### `EBITDA_Normalization.html` — EBITDA Normalization & Adjustments (NEW)
- **Status:** **COMPLETE**
- **TTI Standalone only** (not consolidated)
- **Period scope:** Jan 2023 – Mar 2026 (39 months)
- **Book EBITDA:** **$8.30M** (39 months)
- **Total Adjustments:** **+$3.60M**
- **Adjusted EBITDA:** **$11.90M** (39 months total)
- **Critical fixes applied:**
  - **Double-Count Fix:** CPA year-end reversals reduced owner tax add-backs from $2.79M to $87K net. Without this fix, Adjusted EBITDA would be inflated by $2.7M.
  - **AR Haircut:** ~$200K of >90-day receivables flagged uncollectable. Reduces 2025 from $2.67M raw to $2.47M after haircut.
  - **Freight Expense Timing Adjustment:** CPA period-cutoff distortion for freight costs only. Net +$116,932 total. Shifted one year forward per client direction.
- **2025 figures:**
  - TTI Book EBITDA: **$1,661,941**
  - TTI Adjusted EBITDA (raw): **$2,937,812**
  - TTI Adjusted EBITDA (after ~$200K AR haircut): **$2.74M**
  - Broker Consolidated (all entities): **$2,520,000**
  - **Variance: +$417,812 (16.6%) raw** — directionally aligned, immaterial
- **Normalization adjustments (by category):**

| Category | Adjustment | 2023 | 2024 | 2025 | Q1 2026 | Total |
|---|---|---|---|---|---|---|
| Owner Comp | Disguised Owner Tax Payments (Tami) | $40,000 | $47,000 | — | — | $87,000 |
| Owner Comp | Eliminated Owner Salary (Tami) | $48,000 | $48,000 | $48,000 | $12,000 | $156,000 |
| Owner Comp | GM Salary Replacement | ($86,000) | ($86,000) | ($86,000) | ($21,500) | ($279,500) |
| Owner Comp | Owner Personal Health Insurance | $336 | — | — | — | $336 |
| Owner Comp | Executive Life & Disability | $2,479 | $2,479 | $2,012 | $620 | $7,590 |
| Discretionary | Auto, Travel & Lifestyle | $60,814 | $61,257 | $53,510 | $10,145 | $185,726 |
| Discretionary | Personal Warehouse Rent | $44,580 | $33,435 | $33,435 | $11,145 | $122,595 |
| Related-Party | Intercompany Transfers (TWS) | — | — | $720,000 | $207,000 | $927,000 |
| Related-Party | IT Consulting (Steve) | $82,256 | $73,368 | $83,519 | $20,888 | $260,031 |
| Non-Recurring | Bad Debt Expense | $6,508 | $282,544 | $91 | $15,588 | $304,731 |
| Non-Recurring | Discretionary Profit Sharing | — | — | $168,000 | — | $168,000 |
| Related-Party | Intercompany Transfers (TWS — P&L) | — | — | $720,000 | $207,000 | $927,000 |
| Related-Party | TWS Cash Transfers | $885,000 | $500,000 | $120,000 | — | $1,505,000 |
| Timing | Freight Expense Push/Pull (CPA cutoff) | — | ($12,145) | $13,304 | $115,773 | $116,932 |
| | **Total Adjustments** | **$1,183,973** | **$829,938** | **$1,275,871** | **$309,770** | **$3,599,552** |
| | **Adjusted EBITDA** | **$6,143,070** | **$1,682,470** | **$2,937,812** | **$1,139,453** | **$11,902,805** |

- **Broker comparison framing:** Directionally aligned. TTI standalone ($2.94M raw / $2.74M after AR haircut) and broker consolidated ($2.52M) for 2025 are in the same ballpark. The $418K difference (16.6%) is attributable to consolidated vs. standalone treatment of intercompany transfers (including $1.5M TWS cash transfers and $927K P&L account funding) and transaction-level vs. summary-level review.

---

## How to Deploy

### 1. Make edits locally
Edit files in `status_updates/` using `WriteFile`, `StrReplaceFile`, or `ReadFile` → edit → `WriteFile`.

### 2. Git commit & push
```bash
cd "C:\Users\New User\.claude\projects\Tricon QoE"
git add status_updates/<file>.html
git commit -m "<message>"
git push origin master
```

### 3. Verify Amplify build
```bash
aws amplify list-jobs --app-id d2ucc03atd4qn9 --branch-name master --region us-east-2 --profile northcastle --max-items 3 --query 'jobSummaries[*].[jobId,status,commitId]' --output table
```

Wait for status `SUCCEED` (typically 30–60 seconds).

### 4. Verify live (use `master.` prefix + `?nocache=1`)
```powershell
Invoke-WebRequest -Uri "https://master.d2ucc03atd4qn9.amplifyapp.com/status_updates/<page>.html?nocache=1" -MaximumRedirection 5 -UseBasicParsing
```

---

## Current Workstream Status (Homepage)

| Workstream | Status | Comment |
|---|---|---|
| Revenue Verification & AR Tie-Out | Almost Complete | $55.77M revenue, 99.993% collection, all revenue classified |
| Cash Reconciliation (GL ↔ Bank) | **Complete** | TTI tied 0.17%. TK all statements received, Q1 2026 ties to $87. TWS off-GL flagged. $1.59M Top-Side Tax Plug flagged as material internal control weakness. |
| Subcontracted Services & Intercompany | In Progress | 2023 ties perfectly. 2024 gap -$65,797. 2025 gap +$89,748. |
| EBITDA Normalization | **Complete** | $11.90M Adjusted EBITDA (39 mo). $2.94M raw / $2.74M after AR haircut for 2025 vs broker $2.52M consolidated. Directionally aligned. Double-count fix, AR haircut, freight timing, $1.5M TWS cash transfers, $100K REG deposit, $120K TTIM deposit, ($120K) pro-forma rent, ($61,889) missing Jan 2026 rent applied. |
| Vendor Payments & Freight Cost | **Complete** | $1.51M TWS intercompany add-back ($885K/$500K/$120K by year). $3.86M T-K subcontracted loop flagged for consolidation elimination. AP aging ~$115K (immaterial; cash-basis). Freight $13.12M reclassified to COGS. +$942K unrealized annual rent lift from TTIM/TTIO lease optimization. |
| Credit Card Statement to GL | **Complete** | 54 AMEX statements parsed. 2023 missing, immaterial. |
| Customer Concentration | Not Started | Needs complete revenue by customer |
| Payroll Register Verification | Almost Complete | TTI and TK clean. TWS pending. |
| Dispatch Logs / TMS | Not Started | TMS data not received |
| Lease & Financing | Not Started | QBX received, ready to commence |
| Working Capital Analysis & NWC Peg | **Complete** | Locked peg $1,984,123. $374K bad debt waterfall + $19.9K reclassification. $99.7K TK Loan Receivable flagged. |
| Tax Exposure & Compliance | Not Started | QBX received, ready to commence |
| Tax Returns Tie-Out | In Progress | 2023/2024 returns received. 2025 pending. |
| Segment / Entity Consolidation | Not Started | QBX received, ready to commence |

**Summary pills:** 2 In Progress / 6 Not Started / 4 Complete / 2 Almost Complete / 14 Total

---

## Known Issues / Gotchas

1. **URL prefix:** Always use `master.d2ucc03atd4qn9.amplifyapp.com`, not the bare domain. The bare domain 404s.
2. **Cache busting:** Use `?nocache=1` when verifying changes via `Invoke-WebRequest`.
3. **Build spec:** Never put unquoted `**/*` in the `files` pattern. Must be `'**/*'`.
4. **Line endings:** Git warns about LF→CRLF replacement on Windows. This is harmless.
5. **Emoji rendering:** Some emoji (▸, ⚠) may render as �?� in PowerShell output but display correctly in browsers.

---

## Content Update Log

| Date | Change | File |
|---|---|---|
| May 28 | TTI Cash Recon marked Complete, new bank data, $1.6M TAX AJE flagged | Cash_Reconciliation.html, index.html |
| May 28 | TK section simplified with new bank deltas | Cash_Reconciliation.html |
| May 28 | TWS Warehouse updated with monthly deltas, account info | Cash_Reconciliation.html |
| May 28 | Homepage commentary updated | index.html |
| May 28 | Caution framing softened on $1.6M and $700K | Cash_Reconciliation.html |
| May 28 | BMO-Park KPI removed | Cash_Reconciliation.html |
| May 28 | Cash Roll-Forward Proof added (statement balances) | Cash_Reconciliation.html |
| May 28 | BMO classification language softened | Cash_Reconciliation.html |
| May 28 | TTI monthly accordion hint added, TK monthly removed | Cash_Reconciliation.html |
| May 28 | Revenue updated — all revenue classified | Revenue_AR_TTI.html |
| May 28 | AR Aging updated with year-based detail + EBITDA hit | Revenue_AR_TTI.html |
| May 28 | Negative AR reclass explained (escheatment liability) | Revenue_AR_TTI.html |
| May 28 | Working Capital marked In Progress | index.html |
| May 28 | Credit Card Recon marked Complete | index.html |
| May 30 | TK bank statements: all 39 months received, monthly detail table added | Cash_Reconciliation.html |
| May 30 | NWC Peg page created: locked $1,984,123 TTM average, methodology, 24-month detail | NWC_Peg.html |
| May 30 | Working Capital marked Complete, linked to NWC Peg | index.html |
| May 30 | $1.59M Top-Side Tax Plug flagged as material internal control weakness | Cash_Reconciliation.html, index.html |
| May 30 | $99,682 TK Loan Receivable added to NWC as related-party flag | NWC_Peg.html |
| May 30 | TK status updated: all statements received, April gaps resolved | Cash_Reconciliation.html, index.html |
| May 30 | EBITDA Normalization page created: $10.36M Adjusted EBITDA, $2.06M add-backs | EBITDA_Normalization.html |
| May 30 | Double-Count Fix applied: CPA reversals reduced tax add-backs from $2.79M to $87K | EBITDA_Normalization.html |
| May 30 | AR Haircut added: ~$200K uncollectable receivables flagged, 2025 EBITDA $2.67M→$2.47M | EBITDA_Normalization.html, Revenue_AR_TTI.html |
| May 30 | Freight Expense Timing Adjustment added: net +$116,932, freight costs only | EBITDA_Normalization.html |
| May 30 | Freight-only scope clarification added to timing adjustment row and detail cards | EBITDA_Normalization.html |
| May 30 | Vendor Payments & Freight Cost Tie-Out page created. $1.51M TWS add-back, $3.86M T-K loop, freight profile, +$942K rent lift | Vendor_Payments_Freight.html, index.html |
| May 30 | Broker comparison updated: $2.68M raw / $2.48M after haircut vs broker $2.52M, +$164K (6.5%) | EBITDA_Normalization.html |
| May 30 | TWS Cash Transfers adjustment added: $1.505M (2023-2025) under Related-Party & Intercompany | EBITDA_Normalization.html |
| May 30 | REG Logistics Security Deposit add-back: $100K (2023 only), miscategorized expense → asset | EBITDA_Normalization.html |
| May 30 | Pro-Forma Rent Adjustment: ($120K) unfavorable to 2024, deposit-funded Sept rent skipped P&L | EBITDA_Normalization.html |
| May 30 | TTIM Security Deposit add-back: $120K (2025), miscategorized in TTIM expense | EBITDA_Normalization.html |
| May 30 | Missing January 2026 Base Rent: ($61,889) to Q1 2026, pro-forma correction | EBITDA_Normalization.html |
| May 30 | Index dashboard updated with EBITDA Normalization, new counts | index.html |

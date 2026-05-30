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
└── (other HTML files may exist)
```

### `index.html` — Homepage
- **Purpose:** Executive summary of all QoE workstreams
- **Style:** Simple table-based layout with badge statuses
- **Badges:** `badge-complete` (green), `badge-almost` (blue), `badge-progress` (yellow), `badge-hold` (gray)
- **Status pills:** In Progress / Not Started / Complete counts
- **Links to:** All sub-pages via relative URLs

### `Cash_Reconciliation.html` — Cash Reconciliation
- **Status:** **COMPLETE** for TTI
- **Sections:**
  1. QoE Summary KPIs (Bank Net, GL Adjusted, Variance, Unexplained)
  2. Yearly Bank vs GL table (2023–Q1 2026)
  3. Cash Roll-Forward Proof (beginning/ending balances per bank statement)
  4. Grand Total card (dark background)
  5. Balance Sheet Cash Proof (statement-balance method)
  6. Monthly accordion — TTI (click to expand)
  7. QoE Observations (4 observations)
  8. TK — Bank Net vs GL Net (yearly summary only)
  9. TWS Warehouse — Net Activity by Year + monthly accordion
  10. Bank Statement Coverage matrix
  11. Matching Criteria
- **Key numbers:**
  - TTI Bank 39-mo: **+$2,878,994**
  - TTI GL Adjusted: **+$2,883,985**
  - Variance: **-$4,991 (0.17%)**
  - Unexplained: **-$700K** (Sep 1–3 2023 bank switchover)
  - TAX AJE #1: **$1.6M** — treated as non-cash, needs tax team confirmation
  - TK Q1 2026: Bank -$3,336 vs GL -$3,423 = **$87 variance**

### `Revenue_AR_TTI.html` — Revenue & AR
- **Status:** Almost Complete
- **Sections:**
  1. QoE Summary KPIs (Gross Billed, Cash Collections, Collection Rate, Net AR Change)
  2. Revenue by GL Entry Type table
  3. Accrual-to-Cash Bridge
  4. QoE Observations (4 observations)
  5. AR Aging — TTI (Current, 1-30, 31-60, 61-90, >90)
  6. AR by Customer — >90 Days Detail (year-based grouping)
  7. Data Sources
- **Key numbers:**
  - Gross Billed Invoices: **$55.85M**
  - Cash Collections: **$55.86M**
  - Collection Rate: **99.993%**
  - Implied Cash: **$55,852,708**
  - Variance: **$3,917**
  - Ending AR: **$2,165,993**
  - >90 Days: **$374,543** (2025: $201K, 2024: $78K, 2023: $76K)
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
| Cash Reconciliation (GL ↔ Bank) | **Complete** | TTI tied 0.17%. TK Q1 2026 ties to $87. TWS off-GL flagged. |
| Subcontracted Services & Intercompany | In Progress | 2023 ties perfectly. 2024 gap -$65,797. 2025 gap +$89,748. |
| EBITDA Normalization | Not Started | Will start after financials loaded |
| Vendor Payments & Freight Cost | Not Started | Blocked on correct TTI GL file |
| Credit Card Statement to GL | **Complete** | 54 AMEX statements parsed. 2023 missing, immaterial. |
| Customer Concentration | Not Started | Needs complete revenue by customer |
| Payroll Register Verification | Almost Complete | TTI and TK clean. TWS pending. |
| Dispatch Logs / TMS | Not Started | TMS data not received |
| Lease & Financing | Not Started | QBX received, ready to commence |
| Working Capital Analysis | **In Progress** | AR aging complete, EBITDA impact analysis in progress |
| Tax Exposure & Compliance | Not Started | QBX received, ready to commence |
| Tax Returns Tie-Out | In Progress | 2023/2024 returns received. 2025 pending. |
| Segment / Entity Consolidation | Not Started | QBX received, ready to commence |

**Summary pills:** 3 In Progress / 8 Not Started / 4 Complete / 14 Total

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

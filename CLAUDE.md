# Tricon QOE — Bank Statement Extraction & Reconciliation Workflow

## Architecture

```
120 PDFs → [Filter] → 80 non-empty, non-duplicate, non-redundant
    ↓
PyMuPDF render @ 4× zoom → base64 PNG per page
    ↓
Phase 1: Gemini Flash-Lite (page-by-page) → RAW nested JSON (3,604 txns)
    ↓
Phase 2: Gemini Flash/Pro (reasoning) → FLAT structured JSON (3,594 txns)
    ↓
Phase 3: Reconcile raw vs. flat → AI review → Coverage gap analysis
    ↓
Phase 4: QOE — GL↔Bank recon, Intercompany audit, Cash tie-out
```

## Data File Locations

| File | Path |
|------|------|
| Bank transactions (flat JSON) | `C:\Users\New User\.claude\projects\Tricon QOE\data\flat\bank_transactions_flat.json` |
| TTI General Ledger (CSV) | `Z:\Shared\Selenius Holdings\Tricon Transportation Data Room\Documents\Data Request\1.3 General Ledger\flattened files\TTI_GEN_LEDGER_Flattened.csv` |
| TK General Ledger (JSON) | `Z:\Shared\Selenius Holdings\Tricon Transportation Data Room\Documents\Data Request\1.3 General Ledger\flattened files\TK_GEN_LEDGER_Flattened.json` |
| TK P&L (JSON) | `Z:\Shared\Selenius Holdings\Tricon Transportation Data Room\Documents\Data Request\1.1 P&L\flattened files\TK_P&L_Flattened.json` |

## Output Files (From Northcastle)

| File | Location | Description |
|------|----------|-------------|
| GL-to-Bank Recon 2024 TTI | `From Northcastle\Bank Statement to GL tie out\2024\GL_to_Bank_Recon_2024_TTI.csv` | 2,939 GL records matched to bank (buffer: Dec23-Jan25) |
| GL-to-Bank Recon 2024 TK | `From Northcastle\Bank Statement to GL tie out\2024\GL_to_Bank_Recon_2024_TK.csv` | TK GL-to-Bank (100% NO MATCH, no bank data) |
| P&L-to-GL Recon 2024 TK | `From Northcastle\P&L to GL tie out\2024\P&L_to_GL_Recon_2024_TK.csv` | TK P&L↔GL (100% EXACT match) |
| Interco All Years | `From Northcastle\Intercompany Transactions\Intercompany_TTI_to_TK_All_Years.csv` | TTI GL checks ↔ TK GL deposits |
| Interco Detail | `From Northcastle\Intercompany Transactions\Intercompany_TTI_to_TK_Transaction_Detail.csv` | Transaction-level interco detail |
| Three-Way Audit | `From Northcastle\Intercompany Transactions\Three_Way_Audit_TTI_PL_to_TK_PL.csv` | TTI P&L → TTI GL → TK P&L by year |

## Account Mapping

```python
bank_acct_map = {
    'Account #9530': ('TWS-Warehouse', '959089530'),
    'BMO/0069956696': ('BMO-TTIPark', '0069956696'),
    'BMO/0677032724': ('BMO-TTICorp', '0677032724'),
    'CNB': ('CNB-TTICorp2', '248017740'),
    'TK': ('TK-Investments', '037441394'),
}

# GL cash accounts for TTI (filter on Primary GL Account field):
gl_accts = ['BMO Corporate Account - Other', 'CNB Corp.']
# 'BMO Corporate Account - Other' maps to bank 'BMO-TTICorp'
# 'CNB Corp.' maps to bank 'CNB-TTICorp2'
# 'Tricon Freight Services - CNB' is another CNB account in GL
# BMO-TTIPark and TWS-Warehouse have bank data but NO GL cash accounts in TTI books
# TK-Investments is TK entity, not TTI
```

## GL-to-Bank Recon Methodology

- **LEFT side**: TTI GL 2024, filtered to `Primary GL Account` IN ('BMO Corporate Account - Other', 'CNB Corp.')
- **RIGHT side**: Bank flat JSON with 30-day buffer (Dec 1, 2023 – Jan 31, 2025)
- **Step 1 - EXACT**: Match by check number + same amount (±45 day window)
- **Step 2 - PROXIMITY**: Match by amount + date proximity (±45 days, no check# required)
- **Step 3 - NO MATCH**: Remaining unmatched GL entries

## TTI 2024 Cash Tie-Out Results (as of 2026-05-22)

### GL-to-Bank Summary

| | BMO-TTICorp | CNB-TTICorp2 | Combined |
|---|---|---|---|
| EXACT | 1,796 / $6.7M | 15 / $113K | 1,811 / $6.8M |
| PROXIMITY | 807 / $23.7M | 45 / $2.7M | 852 / $26.4M |
| NO MATCH | 168 / $2.3M | 108 / $1.2M | 276 / $3.5M |
| **Match Rate** | **93.1%** | **69.1%** | **90.5%** |

### NO MATCH Breakdown

| Category | Count | Amount | Explanation |
|---|---|---|---|
| Journal Entries | 2 | $1.6M | Year-end non-cash JE (accruals, not real cash) |
| Outstanding Checks | 114 | $827K | GL checks never cleared bank |
| Deposits (-SPLIT-) | 8 | $684K | QuickBooks bundled deposit artifacts |
| Payments | 13 | $222K | A/P payments not clearing |
| Bill Pmt-Check | 139 | $165K | Bill payments via check |
| **Total** | **276** | **$3.5M** | |

### Outstanding Checks >30 Days (at 12/31/2024)

- 140 checks, $379K total
- 30-60 days: $272K (likely Jan/Feb clearing)
- 90+ days: **$105K** (stale — possibly never sent or void but not reversed, or vendor never cashed)
- Not clearing = check recorded in QB but never appeared on bank statement within the buffer period

### Inter-Account Transfers

- GL side: 4 same-day BMO↔CNB transfers ($1.5M) — BMO funding CNB disbursement account
- Bank side: 511 FORCED CHECK TRANSFERS, 87 wire transfers ($3.2M), 61 PC TRANSFERS ($2.7M)
- CNB acts as a pass-through: BMO → wire → CNB → checks to carriers

### Vague Bank Deposits

- $25M in vague deposits (1,562 of 2,846 bank txns)
- $6.0M "TELLER DEPOSIT" — physical branch, untraceable without deposit slips
- $2.8M "E-Deposit", $2.1M "FORCE POST CREDIT CK DEPOSIT", $2.8M "ACH DEPOSIT CCD CASS INFO"

### Bank Statement Coverage (2024)

| Account | Coverage | Missing |
|---|---|---|
| BMO-TTICorp | 12/12 months | None |
| CNB-TTICorp2 | 8/12 months | Mar, Jul, Dec |
| BMO-TTIPark | 0/12 months | ALL — no statements |
| TWS-Warehouse | 8/12 months | Jan, Mar, Jul, Aug |
| TK-Investments | 0/12 months | ALL — no statements |

## Intercompany Audit (2023+)

### Three-Way: TTI P&L → TTI GL → TK P&L

| Year | TTI P&L (Subcon) | TTI GL-Cash (TK) | TK P&L (Gross Truck) | Interco Gap |
|------|-----------------|-----------------|---------------------|-------------|
| 2023 | $1,191,392 | $1,189,253 | $1,189,253 | $0 |
| 2024 | $1,282,026 | $1,282,026 | $1,216,229 | -$65,797 |
| 2025 | $1,133,093 | $1,133,093 | $1,222,841 | +$89,748 |
| 2026 | $338,549 | $338,549 | $338,459 | -$90 |
| **TOTAL** | **$3,945,060** | **$3,942,921** | **$3,966,782** | **+$23,861** |

- TTI P&L = TTI GL (same QB entries, Split="Subcontracted Services" = P&L, Primary GL Account = cash)
- $2,140 gap in 2023 is MVM Trucking LLC (non-TK subcontractor)
- TK interco filter: Split="Subcontracted Services" AND Name contains "TK" or "TRICON"
- Non-TK subcontractors: only MVM Trucking LLC ($2,140 in 2023) and Jairo Martinez (5 entries, $5,881)

### TK P&L data structure
- `Level 3` = P&L line name (e.g., "Gross Trucking Income")
- `Split` = cash account (e.g., "T-K Investments LLC -441394")
- TK P&L and TK GL are identical (same 212 QB entries, different view)

## Key Learnings

1. **Flash-Lite is the best reader** for raw extraction — fast, cheap, captures dense tables
2. **Page-by-page is mandatory** for 6+ page BMO statements
3. **A reasoning model (Flash/Pro) is needed** for structured shaping
4. **CNB filenames are systematically wrong** — always read actual dates from inside PDFs
5. **Check numbers are the ground truth** — use them to deduplicate and reconcile
6. **The recon is GL→Bank only** — it does NOT flag bank deposits with no GL counterpart (unrecorded revenue)
7. **TTI P&L = TTI GL** for Subcontracted Services — same QuickBooks entries, different field views
8. **-SPLIT- deposits** are QB bundled deposit artifacts that can't be matched 1:1 (~$684K)
9. **Bank amounts in flat JSON are all positive** — deposit/withdrawal split requires the `type` field

## Pending / Next Steps

1. **Bank→GL recon**: Flag bank deposits with no GL match (unrecorded revenue risk)
2. **Client request**: Obtain missing statements (BMO-TTIPark all, TK all, CNB Mar/Jul/Dec, TWS Jan/Mar/Jul/Aug)
3. **TTI standalone P&L**: Check if a separate TTI P&L file exists (currently using GL Split field as P&L)
4. **BMO-TTIPark ownership**: Clarify which entity owns this account — not in TTI GL
5. **Outstanding checks >90 days ($105K)**: Verify with client whether stale or void
6. **$6M TELLER DEPOSIT detail**: Request deposit slip copies for traceability

## Python Environment

- Path: `C:\Users\New User\AppData\Local\Programs\Python\Python313\python.exe`
- Run scripts via PowerShell: `& "C:\Users\New User\AppData\Local\Programs\Python\Python313\python.exe" "path\to\script.py"`
- Temp scripts: write to project dir first, then execute, then clean up
- CSV output: use `encoding='utf-8-sig'` for Excel compatibility
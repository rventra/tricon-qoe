# P&L Structure Analysis: TTI Standalone with Intercompany Transactions

## The "Combined" P&L is NOT Combined — It's TTI's QuickBooks with Internal Tracking

The file `Combined Income Statement with Adjustments.xlsx` is **TTI's standalone P&L** exported from QuickBooks with class/location tracking. It includes:
- Revenue by service type
- **Intercompany transactions with TFS** (revenue FROM TFS + payments TO TFS)
- **Internal cost allocations by warehouse location** (TTIM, TTIO, TTIA)

It does **NOT** consolidate TK or TWS as separate entities.

---

## Evidence from the P&L Structure

### Revenue Side (Rows 7-47)

| Row | Label | Column A Tag | 2024 | 2025 | What It Is |
|-----|-------|-------------|------|------|-----------|
| 9 | Warehouse TTIM | **TWS** | $2,711,503 | $3,210,279 | Warehouse revenue at TTIM location |
| 11 | WAREHOUSE CHARGE TTIO | **TWS** | $1,413,411 | $1,270,652 | Warehouse revenue at TTIO location |
| 22 | TFS REVENUE | | $136,750 | $819,090 | Revenue TTI recognizes FROM TFS |

**Key insight:** Column A tags certain revenue lines as **TWS** — meaning TWS (the separate LLC) generates this warehouse revenue, but it's recorded on TTI's books. This is an intercompany revenue attribution, not true external revenue.

### Expense Side (Rows 60-75)

| Row | Label | 2024 | 2025 | What It Is |
|-----|-------|------|------|-----------|
| 61 | Freight Cost | $4,135,627 | $4,518,180 | External freight/subcontractor payments |
| 62 | TTIM | $1,573,176 | $1,592,310 | **Internal cost allocation** — TTIM warehouse expenses |
| 63 | Payroll | $1,436,366 | $1,567,804 | TTI-only payroll (matches Barrett report) |
| 64 | TTIO | $1,543,164 | $1,466,290 | **Internal cost allocation** — TTIO warehouse expenses |
| 65 | Account Funding | $0 | $720,000 | Capital injection / funding |
| 66 | Insurance Expense | $564,437 | $638,191 | Insurance |
| 67 | Rent Expense | $754,649 | $600,019 | Facility rent |
| 68 | **TFS** | **$225,269** | **$580,457** | **INTERCOMPANY — TTI paying TFS** |
| 69 | Chassis Fees | $435,316 | $529,779 | Chassis rental/parking fees |
| 70 | Advances | $469,816 | $469,111 | Driver advances |
| 73 | TTIA | $77,150 | $177,099 | **Internal cost allocation** — TTIA warehouse expenses |

---

## What TTIM, TTIO, TTIA Actually Are

These are **warehouse locations**, not separate entities:

| Code | Location | Evidence |
|------|----------|----------|
| TTIM | Warehouse #1 / Main | "Warehouse P&L 2026.xlsx" shows TTIM as a warehouse column |
| TTIO | Warehouse #2 | "WHSE 2025 Analysis.xlsx" shows TTIO as warehouse #3 |
| TTIA | Warehouse #3 / Anaheim | "WHSE 2025 Analysis.xlsx" shows TTIA as warehouse #1 |

The P&L tracks revenue and expenses **by warehouse location** using QuickBooks classes. This is internal management reporting, not entity-level consolidation.

---

## TFS Intercompany Transactions

TFS (Tricon Freight Services, LLC) appears on BOTH sides of the P&L:

### Revenue: "TFS REVENUE" = $819K (2025)
- TTI recognizes revenue **from** TFS
- This likely represents TFS brokering freight and paying TTI for trucking services
- TFS's own customer invoices total **$2.46M in 2025** (per `TFS JAN-DEC 2025.xlsx`)
- Only $819K of that flows through to TTI's books as "TFS REVENUE"

### Expense: "TFS" = $580K (2025)
- TTI pays **to** TFS
- Bank data shows "DTFS SVC" payments from BMO-TTICorp totaling ~$293K in 2024
- These are monthly ACH debits ($3,265 + $7,281 = ~$10,546/month)
- The $177K payment in Nov 2024 may be a catch-up or bulk payment

### Net Intercompany Impact on TTI: +$239K (2025)
- TTI receives $819K from TFS
- TTI pays $580K to TFS
- Net: TTI is **+$239K** from the TFS relationship

But this is **not the full picture** — TFS's standalone revenue is $2.46M, of which only $819K hits TTI's books.

---

## What Is NOT in This P&L

| Entity | What's Missing | Evidence of Exclusion |
|--------|---------------|----------------------|
| **TK (T-K Investments, LLC)** | ALL revenue ($2.45M), ALL expenses ($2.29M), ALL payroll ($1.06M) | Separate P&L, separate bank account, zero mentions in Combined P&L |
| **TWS (Tricon Warehouse Services, LLC)** | ALL payroll (~$585K report / $605K bank), ALL vendor checks (~$208K), ALL other expenses | No P&L found in data room, own bank account, zero expense lines in Combined P&L |

---

## The "Combined" Label is Misleading

This P&L should be called:
- **"TTI Standalone Income Statement with Class Tracking"**
- **"TTI QuickBooks P&L by Location and Service"**

It is **NOT** a consolidated financial statement.

### What It Actually Combines:
- TTI's core trucking operations
- TTI's warehouse operations (by location: TTIM, TTIO, TTIA)
- Intercompany transactions with TFS (expense + revenue)

### What It Does NOT Combine:
- TK (separate LLC with its own books)
- TWS (separate LLC with its own bank account, no books found)

---

## Why This Matters for Northcastle

1. **Enterprise EBITDA is understated** — TK generates $157K net income (2025) that is invisible
2. **Intercompany eliminations are missing** — TFS revenue/expense should be eliminated in true consolidation
3. **TWS is a black box** — generates revenue (tagged in P&L) but expenses are off-book
4. **The name creates false confidence** — "Combined" implies full consolidation, which this is not

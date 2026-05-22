# Entity Scope Analysis: "Combined Income Statement" is TTI-Only

## Executive Summary

The file `Combined Income Statement with Adjustments.xlsx` is **misleadingly named**. It does **not** combine the full Tricon enterprise. It includes only **Tricon Transportation, Inc. (TTI)** and its wholly-owned subsidiary **Tricon Freight Services, LLC (TFS)**. Two separate legal entities are **entirely excluded**:

| Entity | EIN | Role | 2025 Payroll (per reports) | Bank Account |
|--------|-----|------|---------------------------|--------------|
| **T-K Investments, LLC (TK)** | 33-0464812 | Provides hourly employee drivers to TTI | **$1,064,000** | TK-Investments (037441394) |
| **Tricon Warehouse Services, LLC (TWS)** | 88-3591978 | Warehouse management & labor | **$585,000** | TWS-Warehouse (959089530) |

**Bottom line:** The "Combined" P&L is missing **~$1.65M of annual payroll** and all other expenses of TK and TWS. If Northcastle intends to value the full enterprise, this is a material scope gap.

---

## Evidence

### 1. Payroll Line Matches TTI-Only

The 2025 Payroll expense in the Combined P&L is **$1,567,804**.

The TTI payroll report (Barrett PEO) for 2025 totals **$1,567,284**.

| Source | 2025 Payroll |
|--------|-------------|
| Combined P&L Row 63 | $1,567,804 |
| TTI Barrett payroll report | $1,567,284 |
| TK Barrett payroll report | $1,064,000 |
| TWS Barrett payroll report | $585,000 |

**The Combined P&L payroll line matches TTI to the dollar. TK and TWS payroll are absent.**

### 2. No TK or TWS Line Items in the P&L

A full-text search of the Combined P&L for:
- `TWS`, `Tri-West`, `Tri West`
- `TK`, `T-K`, `T K Investments`
- `Barrett` (as an expense line, not just payroll processor)

**Returns zero matches.** The only entity codes appearing are internal TTI divisions:
- TTIM (warehouse location)
- TTIO (warehouse location)
- TTIA (warehouse location)
- TFS (freight brokerage subsidiary)
- TTIFU, TTIW, TTI Nevada

### 3. TK Has Its Own Separate P&L

File: `T-K Financials/P&L/TK 2025 P&L by MONTH.xlsx`

| Metric | 2025 |
|--------|------|
| Revenue ("Gross Trucking Income") | $2,445,682 |
| Expenses | $2,288,406 |
| Net Income | $157,276 |

TK is a **profitable standalone entity** that is not reflected in the "Combined" P&L at all.

### 4. TWS Has Its Own Bank Account & Books

TWS-Warehouse (account 959089530) has:
- Its own Barrett payroll debits ($604K in 2025 bank data)
- Its own vendor checks ($208K in 2025)
- Its own Amex and tax payments

No separate TWS entity P&L was found in the data room, but the bank data confirms it operates as a distinct entity with its own expenses.

### 5. Intercompany Funding Flows Confirm Separation

**TK receives weekly funding from TTI:**
- BMO-TTICorp sends "PC TRANSFER DEBIT" withdrawals of $20K-$27K on a weekly schedule
- One transfer explicitly references TK's account: `TRANSFER 000037441394 PER REQUEST`
- TK-Investments receives matching "PC TRANSFER CREDIT" deposits
- 2025 total: **$1,420,606** in transfer deposits to TK

**TWS receives monthly funding from TTI:**
- TWS-Warehouse receives "Online Transfer From Chk ...9255" deposits ($142,500 total)
- TWS also receives large monthly deposits ($52K-$75K) labeled as generic "Deposits"
- Two Fedwire credits explicitly state: `B/O: Tricon Transportation, Inc` (CNB bank)
- 2025 total deposits to TWS: **$869,615**

**These are not external revenues — they are intercompany funding from TTI to its subsidiaries.**

---

## What Is Actually "Combined"?

The P&L combines **TTI + TFS** (and internal warehouse divisions). It does **not** combine TK or TWS.

| Entity | Included? | How? |
|--------|-----------|------|
| TTI (Tricon Transportation, Inc.) | Yes | Main P&L |
| TFS (Tricon Freight Services, LLC) | Yes | Revenue line "TFS REVENUE"; expense line "TFS" |
| TTIM / TTIO / TTIA | Yes | Warehouse divisions (revenue & expense lines) |
| TK (T-K Investments, LLC) | **No** | Separate P&L, separate bank, separate payroll |
| TWS (Tricon Warehouse Services, LLC) | **No** | Separate bank, separate payroll, no P&L in data room |

---

## Financial Impact of Exclusion (2025)

| Item | Amount | Notes |
|------|--------|-------|
| Missing Payroll — TK | $1,064,000 | Per TK payroll report |
| Missing Payroll — TWS | $585,000 | Per TWS payroll report |
| **Total Missing Payroll** | **$1,649,000** | |
| TK Other Expenses | ~$1,224,000 | Per TK P&L (total $2.29M less payroll ~$1.06M) |
| TWS Other Expenses | ~$215,000 | Vendor checks + Amex + taxes (from bank) |
| **Total Missing Expenses** | **~$3,088,000** | Approximate |
| TK Revenue | $2,445,682 | Would offset if consolidated |
| TWS Revenue | Unknown | No P&L found; bank shows only intercompany deposits |

If the goal is **enterprise EBITDA**, TK should be consolidated (adds $157K net income in 2025). TWS impact is unknown without its P&L.

---

## Bank-to-P&L Mapping

| Bank Account | Entity | P&L Inclusion |
|--------------|--------|---------------|
| BMO-TTICorp (0677032724) | TTI main | Combined P&L |
| BMO-TTIPark (0069956696) | TTI main | Combined P&L |
| CNB-TTICorp2 (248017740) | TTI main | Combined P&L |
| TK-Investments (037441394) | **TK** | **Excluded** |
| TWS-Warehouse (959089530) | **TWS** | **Excluded** |

---

## Recommendations

1. **Rename the P&L** to "TTI Consolidated Income Statement" or clarify in footnotes that TK and TWS are excluded.

2. **Request TWS entity P&L** — none was found in the data room. Without it, TWS's revenue, expenses, and net income cannot be assessed.

3. **Consolidate TK** — since TK is 100% owned by the same shareholders and provides essential services to TTI, a true "Combined" or "Consolidated" enterprise P&L should include TK. Its 2025 net income of $157K is material.

4. **Map intercompany eliminations** — if consolidating TK and TWS, eliminate intercompany transfers (TTI funding → TK/TWS revenue) to avoid double-counting.

5. **Clarify with management** whether TWS is a cost center (no external revenue) or a profit center. The bank data suggests TWS is entirely funded by TTI with no identifiable external revenue.

---

## Open Questions

1. Does TWS have external revenue, or is it purely an internal service provider funded by TTI?
2. Are the $110K and $169K monthly outgoing wires from BMO-TTICorp going to TWS, TK, or a third party?
3. Is there an intercompany elimination schedule for TTI↔TK and TTI↔TWS transactions?
4. Why does the Combined P&L include TFS (a separate LLC) but exclude TK and TWS?

# Bank Statement Coverage Summary

Last updated: 2026-05-17

## Coverage Gap Table

**"Complete"** = all 12 monthly statements have extractable transactions.

**"Provided"** = statement file exists. May have transactions (TxnCount > 0) or confirmed no activity (TxnCount = 0).

**"Missing"** = no statement file exists.

| Bank Account | 2022 | 2023 | 2024 | 2025 | 2026 |
|-------------|------|------|------|------|------|
| **BMO-TTICorp** (0677032724) | Jan-Dec | Jan-Dec | **Complete** | Jun-Dec | Jan-Apr |
| **BMO-TTIPark** (0069956696) | Jan-Dec | Jan-Dec | Jan-Dec | **Complete** | **Complete** |
| **CNB-TTICorp2** (248017740) | Jan-Dec | Jan-Dec | Jan, (Mar no activity), (Jul no activity) | **Complete** | Jan-Apr |
| **TK-Investments** (037441394) | Jan-Dec | Jan-Dec | Jan-Dec | **Complete** | **Complete** |
| **TWS-Warehouse** (959089530) | Jan-Dec | Jan-May, (May no activity), Jul-Nov | Jan, (Mar no activity), Jul, Aug | **Complete** | **Complete** |

---

## No Activity Confirmed (Statement Provided, 0 Transactions)

These 9 months had a statement file but the bank confirmed **no activity**:

| Account | Year | Month | Details |
|---------|------|-------|---------|
| TWS-Warehouse | 2023 | May | Empty statement folder |
| TWS-Warehouse | 2023 | Jul | Empty statement folder |
| TWS-Warehouse | 2023 | Aug | Empty statement folder |
| TWS-Warehouse | 2023 | Sep | Empty statement folder |
| TWS-Warehouse | 2023 | Oct | Empty statement folder |
| TWS-Warehouse | 2023 | Nov | Empty statement folder |
| TWS-Warehouse | 2024 | Mar | Raw extraction: 0 transactions |
| CNB-TTICorp2 | 2024 | Mar | Empty statement (mislabeled as APR) |
| CNB-TTICorp2 | 2024 | Jul | Empty statement (mislabeled as AUG) |

**Total: 9 months with no activity confirmed.**

---

## Key Findings

### CNB Filename Mislabeling
CNB statement filenames are systematically off by one month (they use the month AFTER the statement period):
- `2024 APR CNB.pdf` = actually **March 2024** (no activity)
- `2024 AUG CNB.pdf` = actually **July 2024** (no activity)
- `2024 MAY CNB.pdf` = actually **April 2024** (4 transactions)
- `2024 JUN CNB.pdf` = actually **May 2024** (2 transactions)
- `2024 JUL CNB.pdf` = actually **June 2024** (1 transaction)
- `2024 SEP CNB.pdf` = actually **August 2024** (1 transaction)
- `2024 OCT CNB.pdf` = actually **September 2024** (3 transactions)
- `2024 NOV CNB.pdf` = actually **November 2024** (23 transactions)
- `2024 DEC CNB.pdf` = actually **October 2024** (18 transactions)

The flat JSON correctly maps transactions by date, not filename.

### 2025: Best-Captured Year
All five accounts have **Provided** status for all 12 months of 2025. Total transactions: **3,594**.

### Critical Gaps
- **BMO-TTICorp 2025**: Compilation captured deposits Jan-May but **all withdrawals missing** for the full year. Jun-Dec completely missing.
- **CNB 2024**: Jan missing, Mar/Jul no activity. Feb/Jun/Sep have very thin data (1-4 txns). Only Oct-Nov have meaningful volume.
- **TK**: No 2024 data at all.

---

## Flat File Location

**`C:\Users\New User\.claude\projects\Tricon QOE\bank_statement_status_flat.txt`**

Columns: `Account | Date | Year | Month | Status | TxnCount`

- **Status** = `Provided` or `Missing`
- **TxnCount** = number of transactions from flat JSON (0 = no activity)
- Filter `Status = "Provided"` and `TxnCount = 0` to find the 9 no-activity months
- Total transactions: **3,594**

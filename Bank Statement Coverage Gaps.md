# Bank Statement Coverage Gaps

## Transaction Count by Account and Month

| Account | 2023 | | 2024 | | | | | | | | | | | | 2025 | | | | | | | | | | | | 2026 | | | | |
|---------|------|---|------|---|---|---|---|---|---|---|---|---|---|---|------|---|---|---|---|---|---|---|---|---|---|---|------|---|---|---|---|
| | Jun | Dec | Jan | Feb | Mar | Apr | May | Jun | Jul | Aug | Sep | Oct | Nov | Dec | Jan | Feb | Mar | Apr | May | Jun | Jul | Aug | Sep | Oct | Nov | Dec | Jan | Feb | Mar | Apr |
| **BMO-TTICorp** | 0 | 0 | 237 | 227 | 214 | 246 | 249 | 191 | 255 | 279 | 181 | 247 | 215 | 160 | 11 | 12 | 11 | 3 | 12 | **0** | **0** | **0** | **0** | **0** | **0** | **0** | 0 | 0 | 0 | 0 |
| **BMO-TTIPark** | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 12 | 10 | 18 | 11 | 10 | 10 | 14 | 14 | 11 | 18 | 10 | 10 | 12 | 13 | 12 | **0** |
| **CNB-TTICorp2** | 0 | 0 | **0** | 1 | **0** | 4 | 2 | 1 | **0** | 1 | 3 | 18 | 23 | **0** | 10 | 12 | 27 | 14 | 18 | 12 | 11 | 17 | 19 | 18 | 17 | 11 | 0 | 0 | 0 | 0 |
| **TK-Investments** | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 16 | 17 | 13 | 18 | 14 | 17 | 19 | 15 | 15 | 12 | 11 | 17 | 16 | 16 | 17 | **0** |
| **TWS-Warehouse** | 1 | 1 | **0** | 1 | **0** | 1 | 1 | 3 | **0** | **0** | 1 | 5 | 9 | 9 | 12 | 10 | 9 | 11 | 9 | 8 | 13 | 10 | 8 | 11 | 7 | 13 | 9 | 8 | 7 | 10 |

**Bold = months with 0 transactions (missing statements)**

---

## Summary of Gaps

### BMO-TTICorp (Account 0677032724)
| Period | Status | Detail |
|--------|--------|--------|
| 2023 | **MISSING** | No statements in data room |
| 2024 | Complete | 12 monthly statements, 2,329 transactions |
| 2025 Jan-May | **Partial** | Compilation PDF captured only deposits; **all withdrawals missing** |
| 2025 Jun-Dec | **MISSING** | Compilation PDF truncated; no data captured |
| 2026 | **MISSING** | No statements in data room |

**Impact:** 2025 TTI payroll (~$1.57M) is invisible. BMO is TTI's primary operating account.

---

### BMO-TTIPark (Account 0069956696)
| Period | Status | Detail |
|--------|--------|--------|
| 2023-2024 | **MISSING** | No statements in data room |
| 2025 | Complete | 12 monthly statements, 153 transactions |
| 2026 Jan-Mar | Complete | Monthly statements available |
| 2026 Apr | **MISSING** | No statement in data room |

**Impact:** Low impact; this is a secondary account with minimal activity (~$3K/month net flow).

---

### CNB-TTICorp2 (Account 248017740)
| Period | Status | Detail |
|--------|--------|--------|
| 2023 | **MISSING** | No statements in data room |
| 2024 Jan, Mar, Jul, Dec | **MISSING** | No statements in data room |
| 2024 Feb-Jun, Aug-Nov | Partial | Only a few transactions per month; check detail missing for most months |
| 2025 | Complete | 12 monthly statements, check detail available for most months |
| 2026 | **MISSING** | No statements in data room |

**Impact:** 2024 is severely incomplete. 2025 is the best-captured year for CNB.

---

### TK-Investments (Account 037441394)
| Period | Status | Detail |
|--------|--------|--------|
| 2023-2024 | **MISSING** | No statements in data room |
| 2025 | Complete | 12 monthly statements, 195 transactions |
| 2026 Jan-Mar | Complete | Monthly statements available |
| 2026 Apr | **MISSING** | No statement in data room |

**Impact:** TK payroll and intercompany flows are fully captured for 2025.

---

### TWS-Warehouse (Account 959089530)
| Period | Status | Detail |
|--------|--------|--------|
| 2023 Jul-Nov | **MISSING** | No statements in data room |
| 2024 Jan, Mar, Jul, Aug | **MISSING** | No statements in data room |
| 2024 Feb, Apr-Jun, Sep-Dec | Partial | Limited transactions; most months have <10 records |
| 2025 | Complete | 12 monthly statements, 117 transactions |
| 2026 Jan-Apr | Complete | Monthly statements available |

**Impact:** TWS payroll and vendor payments are fully captured for 2025.

---

## Critical Data Gaps for QOE

| Gap | Impact | Can Estimate? |
|-----|--------|---------------|
| BMO-TTICorp 2025 withdrawals | Missing ALL payroll, vendor payments, intercompany transfers for 7 months | Partial — from TTI P&L and payroll reports |
| BMO-TTICorp 2023 | Missing entire year | No — no P&L data to triangulate |
| CNB-TTICorp2 2024 | Missing 4 months + most check detail | Partial — from P&L |
| TWS-Warehouse 2023 | Missing 5 months | No — no TWS P&L available |
| TWS-Warehouse 2024 | Missing 4 months | Partial — from bank data we have |

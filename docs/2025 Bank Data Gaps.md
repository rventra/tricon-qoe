# 2025 Bank Statement Data Gaps

## Executive Summary

The 2025 bank statement extraction for Tricon Transportation, Inc. reveals **significant data gaps** across the two primary operating accounts (BMO-TTICorp and CNB-TTICorp2). These gaps materially impact the ability to perform a complete revenue tie-out and cash flow analysis for 2025.

---

## Missing Data by Account

### BMO-TTICorp (Account #0677032724)

| Data Type | Months Present | Months Missing |
|-----------|---------------|----------------|
| Deposits | Jan–May | **Jun–Dec (7 months)** |
| Withdrawals | **NONE** | **ALL 12 months** |

**Source:** `2025 BMO TTI CORP1 Bank Statements.pdf` — 12 pages, 49 transactions total

**Note:** This is a **compilation PDF**, not individual monthly statements. The compilation only captured deposit activity for Jan–May and **completely omitted all withdrawal detail** across the full year.

**Impact:**
- Expected annual deposit volume (based on 2024 run rate): ~$14M
- Captured deposits: $1.12M (~8% of expected)
- Missing withdrawal detail: ~$16.7M annual run rate (2,300+ transactions)

---

### CNB-TTICorp2 (Account #248017740)

| Data Type | Months Present | Months Missing |
|-----------|---------------|----------------|
| Deposits | **All 12 months** | **NONE** |
| Withdrawals | Feb, Mar | **Jan, Apr–Dec (10 months)** |

**Source:** `2025 CNB TTI CORP2 Bank Statements.pdf` — 12 pages, 186 transactions total

**Note:** This is also a **compilation PDF**, not individual monthly statements. Deposits are fully represented, but check detail/withdrawal detail is heavily truncated.

**Impact:**
- Deposits fully captured: $11.19M
- Missing withdrawal detail: ~$150K+ annual run rate (based on 2024 pattern)

---

## Combined TTI Corp Impact (BMO + CNB)

| Metric | 2024 (Baseline) | 2025 (Captured) | Gap |
|--------|-----------------|-----------------|-----|
| Deposits | $16.77M | $12.32M | **-$4.45M** |
| Withdrawals | $16.81M | $0.13M | **-$16.68M** |
| Transaction Records | 2,807 | 235 | **-2,572** |

---

## Root Cause

The 2024 dataset includes **individual monthly PDFs** for each account (e.g., `2024 JAN BMO TTI.pdf`, `2024 FEB BMO TTI.pdf`, etc.), enabling full page-by-page extraction.

The 2025 dataset was provided as **compilation PDFs only** (single file per account for the full year). These compilations:
- Truncated or omitted withdrawal detail pages
- Appear to be summary documents rather than full transaction-level statements
- Do not include check images or check register detail

---

## Data Room Reference

| Account | 2024 Files | 2025 Files |
|---------|-----------|-----------|
| BMO-TTICorp | 12 individual monthly PDFs | 1 compilation PDF |
| CNB-TTICorp2 | 8 individual monthly PDFs | 1 compilation PDF |
| BMO-TTIPark | 0 | 12 individual monthly PDFs |
| TK-Investments | 0 | 12 individual monthly PDFs |
| TWS-Warehouse | 8 individual monthly PDFs | 12 individual monthly PDFs |

---

## Recommendation

To close the 2025 data gap, request from Tricon:

1. **Individual monthly BMO statements** for Jun–Dec 2025 (account 0677032724)
2. **Individual monthly CNB statements** with check detail for Jan, Apr–Dec 2025 (account 248017740)
3. **BMO withdrawal/check detail** for all 12 months of 2025

Without these documents, the 2025 bank-based revenue analysis will remain incomplete and the ~$4.45M deposit variance vs. P&L cannot be fully reconciled.

---

*Generated from bank_transactions_flat.json and MASTER_BANK_STATEMENT_RAW.json*
*Verified against raw extraction records*

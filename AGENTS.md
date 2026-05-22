# Tricon Transportation, Inc. — Bank Statement Extraction Project

## Project Overview
Quality of Earnings (QOE) bank statement extraction for Tricon Transportation, Inc.

## Working Directory
`C:\Users\New User\.claude\projects\Tricon QOE\`

## Key Files
| File | Purpose |
|------|---------|
| `bank_transactions_flat.json` | **CLASSIFICATION JSON** — 3,594 structured flat records |
| `master_raw_extractions/MASTER_BANK_STATEMENT_RAW.json` | **RAW EXTRACTION** — 80 files, 318 pages, 3,604 transactions |
| `build_master_json.py` | Extraction pipeline |
| `schema.json` | JSON schema for flat output |
| `AGENTS.md` | This file — agent context |
| `CLAUDE.md` | Workflow documentation |
| `bank_statement_status_flat.txt` | **COVERAGE GAPS** — 300-row flat file (Account/Date/Year/Month/Status/TxnCount) |

## Data Room
`Z:\Shared\Selenius Holdings\Tricon Transportation Data Room\Documents\Initial DD\2. Other Financial Information\d. Bank Statements`

## Document Inventory

| Category | Count |
|----------|-------|
| Total PDFs | 120 |
| Duplicates (TWS) | 27 |
| Redundant compilations | 2 |
| Empty statements (no activity) | 9 |
| **Files with transactions** | **80** |

### Account Mapping

| Folder | Account Name | Account # |
|--------|-------------|-----------|
| Account #9530 | TWS-Warehouse | 959089530 |
| BMO/Account 0069956696 | BMO-TTIPark | 0069956696 |
| BMO/Account 0677032724 | BMO-TTICorp | 0677032724 |
| CNB | CNB-TTICorp2 | 248017740 |
| TK | TK-Investments | 037441394 |

## Coverage Gaps (Verified)

| Account | Missing | Provided (Incomplete) | No Activity |
|---------|---------|----------------------|-------------|
| BMO-TTICorp (0677032724) | 2022-2023, 2025 Jun-Dec, 2026 | 2025 Jan-May (compilation) | — |
| BMO-TTIPark (0069956696) | 2022-2024, 2026 Apr-Dec | — | — |
| CNB-TTICorp2 (248017740) | 2022-2023, 2024 Jan/Dec, 2026 | — | 2024 Mar, 2024 Jul |
| TK-Investments (037441394) | 2022-2024, 2026 Apr-Dec | — | — |
| TWS-Warehouse (959089530) | 2022, 2023 Jan-Apr, 2024 Jan/Jul/Aug, 2026 May-Dec | — | 2023 May/Jul-Nov, 2024 Mar |

### No Activity (9 months)
Statement received but bank confirmed zero transactions:
- CNB: 2024-03, 2024-07
- TWS: 2023-05, 2023-07, 2023-08, 2023-09, 2023-10, 2023-11, 2024-03

### Key Finding: CNB Filename Mislabeling
CNB statement filenames use the month AFTER the actual statement period:
- `2024 MAY CNB.pdf` = actually **April 2024**
- `2024 JUN CNB.pdf` = actually **May 2024**
- `2024 JUL CNB.pdf` = actually **June 2024**
- `2024 SEP CNB.pdf` = actually **August 2024**
- `2024 OCT CNB.pdf` = actually **September 2024**
- `2024 NOV CNB.pdf` = actually **November 2024**
- `2024 DEC CNB.pdf` = actually **October 2024**
- `2024 APR CNB.pdf` (Empty folder) = actually **March 2024** (no activity)
- `2024 AUG CNB.pdf` (Empty folder) = actually **July 2024** (no activity)

The flat JSON maps transactions by internal dates, not filenames.

## Two JSON Formats

### 1. RAW EXTRACTION (nested)
```
file → pages[] → transactions[]
```
- Location: `master_raw_extractions/MASTER_BANK_STATEMENT_RAW.json`
- Created by: Gemini 3.1 Flash-Lite page-by-page
- Purpose: Preserves every raw transaction exactly as extracted

### 2. FLAT JSON (structured)
```
[{"id": 1, "date": "2024-01-15", "amount": 5000.00, "type": "deposit", ...}, ...]
```
- Location: `bank_transactions_flat.json`
- Created by: Reasoning model shaping raw into uniform schema
- Size: **3,594 transactions** (after deduplication and AI review)

## Extraction Workflow

### Phase 1: Raw Extraction (Gemini Flash-Lite)
**Model:** `google/gemini-3.1-flash-lite-preview` (via OpenRouter)
**Mode:** Page-by-page (each page sent individually)
**Zoom:** 4× (PyMuPDF)

### Phase 2: Structured Shaping (Reasoning Model)
**Model:** `google/gemini-3.1-flash-preview` or `google/gemini-3.1-pro-preview`

### Phase 3: Reconciliation
- Compare flat JSON against raw extraction
- 20 page-break duplicates removed
- 1,006 AI review flags applied programmatically
- 3 records remain flagged for human review

## API Key
OpenRouter: `YOUR_OPENROUTER_API_KEY_HERE`

## Color Palette (North Castle Branding)
- Primary Navy: `#0f172a`
- Warm Gold: `#d4a853`
- Slate Gray: `#64748b`
- Light Gray: `#f8fafc`

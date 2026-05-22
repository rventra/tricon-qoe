#!/usr/bin/env python3
"""
Tricon QOE - Data Factory Pipeline
==================================
Two-stage pipeline:
  Stage 1: Extract new PDFs page-by-page with Gemini Flash Lite → append to RAW JSON
  Stage 2: Shape new raw records into TEMP flat JSON (same schema as existing flat)

Usage:
  python data_factory_pipeline.py --stage 1    # Extract only
  python data_factory_pipeline.py --stage 2    # Shape only
  python data_factory_pipeline.py --stage both # Full pipeline
"""

import argparse
import base64
import io
import json
import os
import sys
import time
from collections import Counter
from datetime import datetime, timezone

import fitz  # PyMuPDF
from PIL import Image

# ── Configuration ───────────────────────────────────────────────────────────

OPENROUTER_API_KEY = "YOUR_OPENROUTER_API_KEY_HERE"
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

DATA_ROOM = r"Z:\Shared\Selenius Holdings\Tricon Transportation Data Room\Documents\Initial DD\2. Other Financial Information\d. Bank Statements"
RAW_JSON_PATH = r"data\raw\MASTER_BANK_STATEMENT_RAW.json"
FLAT_JSON_PATH = r"data\flat\bank_transactions_flat.json"
TEMP_FLAT_PATH = r"data\flat\bank_transactions_flat_TEMP.json"
BACKUP_DIR = r"data\raw\backups"
YOY_REPORT_PATH = r"data\flat\yoy_variance_report.json"

EXTRACTION_MODEL = "google/gemini-3.1-flash-preview"
SHAPING_MODEL = "google/gemini-3.1-flash-preview"
ZOOM = 4
MAX_TOKENS_EXTRACT = 4000
MAX_TOKENS_SHAPE = 8000
TEMPERATURE = 0.1

# ── System Prompts ──────────────────────────────────────────────────────────

EXTRACTION_SYSTEM_PROMPT = """You are a bank statement transaction extractor.
Your task is to read the provided bank statement page image and extract every financial transaction shown.

For each transaction, return an object with these exact fields:
- "date": string (MM/DD or MM/DD/YY format as shown on the statement)
- "description": string (full transaction description)
- "amount": number (absolute value, no commas)
- "type": string ("deposit", "withdrawal", "check", "fee", or "transfer")
- "check_number": string or null (if shown)
- "reference_number": string or null (if shown)

If a line is NOT a transaction (header, footer, summary, balance, etc.), do NOT include it.
If the page has no transactions, return an empty array.

Respond with a JSON object: {"transactions": [...]}
No markdown, no explanation — only the JSON object."""

SHAPING_SYSTEM_PROMPT = """You are a financial data shaping expert.
Your task is to convert raw bank statement extractions into a standardized flat schema.

For each raw transaction, produce an object with these exact fields:
- "date": string (YYYY-MM-DD, infer full year from statement filename/period)
- "year": string (YYYY)
- "month": string (MM)
- "account": string (one of: BMO-TTICorp, BMO-TTIPark, CNB-TTICorp2, TK-Investments, TWS-Warehouse)
- "account_number": string (full account number)
- "amount": number (absolute value)
- "type": string (deposit, withdrawal, check, fee, transfer)
- "description": string (cleaned description)
- "check_number": string or null
- "reference_number": string or null
- "bucket": string (Revenue, COGS, Operating Expense, Payroll, Intercompany, Loan, Other)
- "confidence": string (High, Medium, Low)
- "reasoning": string (brief explanation for bucket assignment)
- "review_flags": array of strings (flag any issues: "date_uncertain", "amount_ambiguous", "bucket_uncertain", "missing_check", etc. — empty array if clean)

Account mapping rules:
- Folder/account containing "0069956696" or "BMO" + "Park" → BMO-TTIPark, account_number "0069956696"
- Folder/account containing "0677032724" or "BMO" + "Corp" (not Park) → BMO-TTICorp, account_number "0677032724"
- Folder/account containing "248017740" or "CNB" → CNB-TTICorp2, account_number "248017740"
- Folder/account containing "037441394" or "TK" or "Investments" → TK-Investments, account_number "037441394"
- Folder/account containing "959089530" or "9530" or "TWS" or "Warehouse" → TWS-Warehouse, account_number "959089530"

CNB filename mislabeling correction (filenames use month AFTER actual period):
- "JAN" → December of previous year
- "FEB" → January
- "MAR" → February
- "APR" → March
- "MAY" → April
- "JUN" → May
- "JUL" → June
- "AUG" → July
- "SEP" → August
- "OCT" → September
- "NOV" → November
- "DEC" → October

Respond with a JSON array of shaped records. No markdown, no explanation — only the JSON array."""

# ── Helpers ─────────────────────────────────────────────────────────────────

import requests


def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")


def load_raw_json():
    with open(RAW_JSON_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_raw_json(data):
    os.makedirs(BACKUP_DIR, exist_ok=True)
    backup_path = os.path.join(BACKUP_DIR, f"MASTER_BANK_STATEMENT_RAW_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    with open(backup_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    log(f"Raw JSON backed up to: {backup_path}")
    with open(RAW_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    log(f"Raw JSON saved ({len(data['files'])} files)")


def load_flat_json():
    with open(FLAT_JSON_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def get_account_info_from_path(full_path):
    """Infer account name and number from file path."""
    path_lower = full_path.lower()
    if "0069956696" in path_lower or ("bmo" in path_lower and "park" in path_lower):
        return "BMO-TTIPark", "0069956696"
    if "0677032724" in path_lower or ("bmo" in path_lower and "corp" in path_lower):
        return "BMO-TTICorp", "0677032724"
    if "248017740" in path_lower or "cnb" in path_lower:
        return "CNB-TTICorp2", "248017740"
    if "037441394" in path_lower or "tk" in path_lower or "investments" in path_lower:
        return "TK-Investments", "037441394"
    if "959089530" in path_lower or "9530" in path_lower or "tws" in path_lower or "warehouse" in path_lower:
        return "TWS-Warehouse", "959089530"
    return "Unknown", "Unknown"


def infer_date_from_filename(filename):
    """Extract year/month from filename for CNB correction and general inference."""
    import re
    fname = filename.upper()
    year_match = re.search(r'20(\d{2})', fname)
    year = "20" + year_match.group(1) if year_match else None

    month_map = {
        'JAN': 1, 'FEB': 2, 'MAR': 3, 'APR': 4, 'MAY': 5, 'JUN': 6,
        'JUL': 7, 'AUG': 8, 'SEP': 9, 'OCT': 10, 'NOV': 11, 'DEC': 12
    }
    for mon, num in month_map.items():
        if mon in fname:
            return year, str(num).zfill(2), mon
    return year, None, None


def render_page_to_base64(doc, page_num, zoom=ZOOM):
    page = doc.load_page(page_num)
    mat = fitz.Matrix(zoom, zoom)
    pix = page.get_pixmap(matrix=mat)
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode("utf-8")


def call_openrouter(model, system_prompt, user_content, max_tokens=MAX_TOKENS_EXTRACT, retries=3):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://localhost",
        "X-Title": "Tricon-QOE-DataFactory",
    }
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ],
        "max_tokens": max_tokens,
        "temperature": TEMPERATURE,
    }
    for attempt in range(retries):
        try:
            resp = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=120)
            if resp.status_code == 200:
                data = resp.json()
                if "choices" in data and len(data["choices"]) > 0:
                    return data["choices"][0]["message"]["content"]
                return None
            elif resp.status_code == 429:
                wait = 2 ** attempt
                log(f"  Rate limited, waiting {wait}s...")
                time.sleep(wait)
            else:
                log(f"  API error {resp.status_code}: {resp.text[:200]}")
                time.sleep(1)
        except Exception as e:
            log(f"  Request error: {e}")
            time.sleep(1)
    return None


def extract_page_transactions(b64_image, filename, page_num, total_pages):
    user_content = [
        {"type": "text", "text": f"Extract page {page_num} of {total_pages} from file: {filename}"},
        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64_image}"}},
    ]
    raw = call_openrouter(EXTRACTION_MODEL, EXTRACTION_SYSTEM_PROMPT, user_content, max_tokens=MAX_TOKENS_EXTRACT)
    if not raw:
        return None
    # Clean up markdown fences
    raw = raw.strip()
    if raw.startswith("```json"):
        raw = raw[7:]
    if raw.startswith("```"):
        raw = raw[3:]
    if raw.endswith("```"):
        raw = raw[:-3]
    raw = raw.strip()
    try:
        parsed = json.loads(raw)
        if isinstance(parsed, dict) and "transactions" in parsed:
            return parsed["transactions"]
        if isinstance(parsed, list):
            return parsed
        return []
    except json.JSONDecodeError:
        log(f"  JSON parse error on page {page_num}, raw length={len(raw)}")
        return None


def shape_file_transactions(raw_file_obj, extraction_meta):
    """Send raw file extractions to shaping model, return flat records."""
    # Build a compact representation for the API
    account_name, account_number = get_account_info_from_path(raw_file_obj["full_path"])
    year_hint, month_hint, month_code = infer_date_from_filename(raw_file_obj["filename"])

    # Flatten page transactions with page context
    txns_with_context = []
    for pe in raw_file_obj.get("page_extractions", []):
        for t in pe.get("transactions", []):
            txns_with_context.append({
                "page": pe["page_number"],
                **t
            })

    if not txns_with_context:
        return []

    user_text = f"""Shape these raw bank statement transactions into the standard flat schema.

File: {raw_file_obj['filename']}
Account inferred: {account_name} ({account_number})
Year hint from filename: {year_hint}
Month hint from filename: {month_hint} (code: {month_code})
Total raw transactions: {len(txns_with_context)}

Raw transactions:
{json.dumps(txns_with_context, indent=2)}

Remember:
- CNB filenames use the month AFTER the actual period (e.g., "MAY" = April)
- Infer full YYYY-MM-DD dates from statement period + transaction day
- Use the account mapping rules from the system prompt
- Return ONLY a JSON array of shaped records."""

    raw = call_openrouter(SHAPING_MODEL, SHAPING_SYSTEM_PROMPT, [{"type": "text", "text": user_text}], max_tokens=MAX_TOKENS_SHAPE)
    if not raw:
        return None
    raw = raw.strip()
    if raw.startswith("```json"):
        raw = raw[7:]
    if raw.startswith("```"):
        raw = raw[3:]
    if raw.endswith("```"):
        raw = raw[:-3]
    raw = raw.strip()
    try:
        shaped = json.loads(raw)
        if isinstance(shaped, list):
            # Enrich with metadata
            now_iso = datetime.now(timezone.utc).isoformat()
            for rec in shaped:
                rec["statement_file"] = raw_file_obj["filename"]
                rec["source_file"] = raw_file_obj["full_path"]
                rec["extraction_method"] = EXTRACTION_MODEL
                rec["extracted_at"] = now_iso
                if "review_flags" not in rec:
                    rec["review_flags"] = []
            return shaped
        return []
    except json.JSONDecodeError:
        log(f"  JSON parse error shaping {raw_file_obj['filename']}, raw length={len(raw)}")
        return None


# ── Stage 1: Extract ────────────────────────────────────────────────────────

def stage_1_extract():
    log("=" * 60)
    log("STAGE 1: Extract new PDFs to RAW JSON")
    log("=" * 60)

    raw_data = load_raw_json()
    existing_files = {f["filename"] for f in raw_data["files"]}
    log(f"Existing files in RAW JSON: {len(existing_files)}")

    # Scan data room
    all_pdfs = []
    for root, dirs, files in os.walk(DATA_ROOM):
        # Skip archived
        if "archived" in root.lower():
            continue
        for f in files:
            if f.lower().endswith(".pdf"):
                full = os.path.join(root, f)
                rel = os.path.relpath(full, DATA_ROOM)
                all_pdfs.append((f, full, rel))

    missing = [(f, full, rel) for f, full, rel in all_pdfs if f not in existing_files]
    log(f"Total PDFs in data room (excl archived): {len(all_pdfs)}")
    log(f"Missing from RAW JSON: {len(missing)}")

    if not missing:
        log("No new PDFs to extract. Exiting.")
        return []

    # Show breakdown
    folders = Counter(rel.split("\\")[0] for _, _, rel in missing)
    for folder, count in sorted(folders.items()):
        log(f"  {folder}: {count} files")

    # Extract
    new_raw_entries = []
    extraction_date = datetime.now(timezone.utc).isoformat()
    total_pages_processed = 0
    total_txns_extracted = 0

    for idx, (filename, full_path, rel_path) in enumerate(missing, 1):
        log(f"[{idx}/{len(missing)}] Extracting: {filename}")
        if not os.path.exists(full_path):
            log(f"  FILE NOT FOUND, skipping: {full_path}")
            continue

        try:
            doc = fitz.open(full_path)
        except Exception as e:
            log(f"  Error opening PDF: {e}")
            continue

        pages = len(doc)
        page_extractions = []
        file_txn_count = 0

        for p in range(pages):
            try:
                b64 = render_page_to_base64(doc, p)
                txns = extract_page_transactions(b64, filename, p + 1, pages)
                if txns is None:
                    log(f"  Page {p+1}: API failure, skipping")
                    page_extractions.append({
                        "page_number": p + 1,
                        "transactions_count": 0,
                        "transactions": [],
                        "api_error": True
                    })
                else:
                    page_extractions.append({
                        "page_number": p + 1,
                        "transactions_count": len(txns),
                        "transactions": txns
                    })
                    file_txn_count += len(txns)
            except Exception as e:
                log(f"  Page {p+1}: Render error: {e}")
                page_extractions.append({
                    "page_number": p + 1,
                    "transactions_count": 0,
                    "transactions": [],
                    "render_error": True
                })

        doc.close()

        entry = {
            "filename": filename,
            "full_path": full_path,
            "relative_path": rel_path,
            "pages": pages,
            "page_extractions": page_extractions,
            "total_transactions": file_txn_count,
            "extraction_date": extraction_date,
            "extraction_method": EXTRACTION_MODEL,
            "zoom_level": ZOOM,
        }
        new_raw_entries.append(entry)
        raw_data["files"].append(entry)
        total_pages_processed += pages
        total_txns_extracted += file_txn_count

        # Save progress every 5 files
        if idx % 5 == 0:
            raw_data["_metadata"]["last_updated"] = datetime.now(timezone.utc).isoformat()
            raw_data["_metadata"]["total_files"] = len(raw_data["files"])
            save_raw_json(raw_data)
            log(f"  Progress saved ({idx}/{len(missing)})")

        # Rate limit breathing room
        time.sleep(0.5)

    # Final save
    raw_data["_metadata"]["last_updated"] = datetime.now(timezone.utc).isoformat()
    raw_data["_metadata"]["total_files"] = len(raw_data["files"])
    raw_data["_metadata"]["total_pages_processed"] = raw_data["_metadata"].get("total_pages_processed", 0) + total_pages_processed
    raw_data["_metadata"]["total_transactions_extracted"] = raw_data["_metadata"].get("total_transactions_extracted", 0) + total_txns_extracted
    save_raw_json(raw_data)

    log(f"Stage 1 complete: {len(new_raw_entries)} new files, {total_pages_processed} pages, {total_txns_extracted} transactions")
    return new_raw_entries


# ── Stage 2: Shape ──────────────────────────────────────────────────────────

def build_yoy_lookup():
    """Index existing flat data by (account, month) for YoY lookup."""
    flat_data = load_flat_json()
    lookup = {}
    for r in flat_data:
        key = (r.get("account"), r.get("month"))
        if key not in lookup:
            lookup[key] = {}
        year = r.get("year")
        if year not in lookup[key]:
            lookup[key][year] = []
        lookup[key][year].append(r)
    return lookup


def compute_monthly_metrics(records):
    """Compute summary metrics for a set of records."""
    if not records:
        return None
    deposits = [r for r in records if r.get("type") == "deposit"]
    withdrawals = [r for r in records if r.get("type") == "withdrawal"]
    checks = [r for r in records if r.get("type") == "check"]
    total_vol = sum(r.get("amount", 0) for r in records)
    dep_vol = sum(r.get("amount", 0) for r in deposits)
    wd_vol = sum(r.get("amount", 0) for r in withdrawals)
    return {
        "txn_count": len(records),
        "deposit_count": len(deposits),
        "withdrawal_count": len(withdrawals),
        "check_count": len(checks),
        "total_volume": round(total_vol, 2),
        "deposit_volume": round(dep_vol, 2),
        "withdrawal_volume": round(wd_vol, 2),
        "avg_txn_size": round(total_vol / len(records), 2) if records else 0,
        "unique_descriptions": len(set(r.get("description", "") for r in records)),
    }


def pct_change(curr, prev):
    if prev == 0:
        return float('inf') if curr > 0 else 0
    return round((curr - prev) / prev * 100, 1)


def compare_yoy_for_file(shaped_records, yoy_lookup):
    """Compare newly shaped records against same account+month from prior year."""
    if not shaped_records:
        return None
    account = shaped_records[0].get("account")
    year = shaped_records[0].get("year")
    month = shaped_records[0].get("month")
    if not account or not year or not month:
        return None
    prev_year = str(int(year) - 1)
    key = (account, month)
    if key not in yoy_lookup or prev_year not in yoy_lookup[key]:
        return None
    prior_records = yoy_lookup[key][prev_year]
    curr_metrics = compute_monthly_metrics(shaped_records)
    prev_metrics = compute_monthly_metrics(prior_records)
    if not curr_metrics or not prev_metrics:
        return None
    result = {
        "account": account,
        "month": month,
        "current_year": year,
        "prior_year": prev_year,
        "current_metrics": curr_metrics,
        "prior_metrics": prev_metrics,
        "variances": {
            "txn_count_pct": pct_change(curr_metrics["txn_count"], prev_metrics["txn_count"]),
            "total_volume_pct": pct_change(curr_metrics["total_volume"], prev_metrics["total_volume"]),
            "deposit_count_pct": pct_change(curr_metrics["deposit_count"], prev_metrics["deposit_count"]),
            "deposit_volume_pct": pct_change(curr_metrics["deposit_volume"], prev_metrics["deposit_volume"]),
            "withdrawal_count_pct": pct_change(curr_metrics["withdrawal_count"], prev_metrics["withdrawal_count"]),
            "withdrawal_volume_pct": pct_change(curr_metrics["withdrawal_volume"], prev_metrics["withdrawal_volume"]),
            "avg_txn_size_pct": pct_change(curr_metrics["avg_txn_size"], prev_metrics["avg_txn_size"]),
        },
        "flags": [],
        "checked_at": datetime.now(timezone.utc).isoformat(),
    }
    v = result["variances"]
    # Flag significant variances (>50% change or near-zero current vs substantial prior)
    if abs(v["txn_count_pct"]) > 50:
        direction = "DROP" if v["txn_count_pct"] < 0 else "SPIKE"
        result["flags"].append(f"{direction}: txn_count {v['txn_count_pct']:+.1f}% ({prev_metrics['txn_count']} -> {curr_metrics['txn_count']})")
    if abs(v["total_volume_pct"]) > 50:
        direction = "DROP" if v["total_volume_pct"] < 0 else "SPIKE"
        result["flags"].append(f"{direction}: total_volume {v['total_volume_pct']:+.1f}%")
    # Special flag: current month has <20% of prior's txn count (possible under-extraction)
    if curr_metrics["txn_count"] < prev_metrics["txn_count"] * 0.2 and prev_metrics["txn_count"] >= 10:
        result["flags"].append(f"EXTRACTION_RISK: only {curr_metrics['txn_count']}/{prev_metrics['txn_count']} transactions extracted ({v['txn_count_pct']:+.1f}%)")
    return result


def save_yoy_report(report_entries):
    """Write rolling YoY report to JSON."""
    with open(YOY_REPORT_PATH, "w", encoding="utf-8") as f:
        json.dump({
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "total_comparisons": len(report_entries),
            "comparisons": report_entries,
        }, f, indent=2)


def check_variance_patterns(report_entries):
    """After processing batch, check for systematic patterns across accounts."""
    if len(report_entries) < 2:
        return []
    by_account = {}
    for entry in report_entries:
        acc = entry["account"]
        by_account.setdefault(acc, []).append(entry)
    alerts = []
    for acc, entries in by_account.items():
        if len(entries) < 2:
            continue
        drops = sum(1 for e in entries if e["variances"]["txn_count_pct"] < -30)
        if drops >= 2:
            months = ", ".join(e["month"] for e in entries if e["variances"]["txn_count_pct"] < -30)
            alerts.append(f"PATTERN ALERT: {acc} shows {drops} months with >30% txn count drop ({months}) — possible systematic under-extraction")
        # Check if ALL months for this account are under-extracted
        all_under = all(e["variances"]["txn_count_pct"] < -50 for e in entries)
        if all_under and len(entries) >= 2:
            alerts.append(f"PATTERN ALERT: {acc} ALL {len(entries)} months show >50% txn count drop — STRONG extraction quality issue")
    return alerts


def stage_2_shape(new_raw_entries=None):
    log("=" * 60)
    log("STAGE 2: Shape new raw records to TEMP flat JSON")
    log("=" * 60)

    raw_data = load_raw_json()
    flat_data = load_flat_json()

    # Determine which files are "new" (extracted today or not in flat)
    existing_statement_files = {r.get("statement_file") for r in flat_data}
    
    if new_raw_entries is not None:
        candidates = new_raw_entries
    else:
        # Find files in raw that are NOT represented in flat
        candidates = [f for f in raw_data["files"] if f["filename"] not in existing_statement_files]

    log(f"Candidates to shape: {len(candidates)}")

    if not candidates:
        log("No new records to shape. Exiting.")
        return

    # Get max ID for sequential numbering
    max_id = max(r["id"] for r in flat_data) if flat_data else 0
    log(f"Existing max ID: {max_id}")

    all_shaped = []
    errors = []
    yoy_report_entries = []
    yoy_lookup = build_yoy_lookup()
    log(f"YoY lookup built: {len(yoy_lookup)} account-month combinations in existing data")

    for idx, raw_file in enumerate(candidates, 1):
        log(f"[{idx}/{len(candidates)}] Shaping: {raw_file['filename']}")
        shaped = shape_file_transactions(raw_file, {})
        if shaped is None:
            log(f"  API failure — will retry not implemented, skipping")
            errors.append(raw_file["filename"])
            continue
        if not shaped:
            log(f"  No transactions to shape")
            continue

        # Assign sequential IDs
        for rec in shaped:
            max_id += 1
            rec["id"] = max_id

        all_shaped.extend(shaped)
        log(f"  → {len(shaped)} shaped records (IDs {shaped[0]['id']}–{shaped[-1]['id']})")

        # Save temp progress every 10 files
        if idx % 10 == 0:
            with open(TEMP_FLAT_PATH, "w", encoding="utf-8") as f:
                json.dump(all_shaped, f, indent=2)
            log(f"  Temp progress saved: {len(all_shaped)} records so far")

        time.sleep(0.3)

    # Final save
    with open(TEMP_FLAT_PATH, "w", encoding="utf-8") as f:
        json.dump(all_shaped, f, indent=2)

    # Final YoY report
    save_yoy_report(yoy_report_entries)

    # Pattern alerts
    alerts = check_variance_patterns(yoy_report_entries)
    if alerts:
        log("=" * 60)
        log("YOY PATTERN ALERTS")
        log("=" * 60)
        for alert in alerts:
            log(f"  *** {alert}")
    else:
        log("No systematic YoY variance patterns detected.")

    log(f"Stage 2 complete: {len(all_shaped)} shaped records saved to {TEMP_FLAT_PATH}")
    log(f"YoY report saved: {YOY_REPORT_PATH} ({len(yoy_report_entries)} comparisons)")
    if errors:
        log(f"Errors ({len(errors)}): {errors}")

    # Summary stats
    if all_shaped:
        accounts = Counter(r["account"] for r in all_shaped)
        years = Counter(r["year"] for r in all_shaped)
        log("By account:")
        for acc, cnt in sorted(accounts.items()):
            log(f"  {acc}: {cnt}")
        log("By year:")
        for yr, cnt in sorted(years.items()):
            log(f"  {yr}: {cnt}")


# ── Main ────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Tricon QOE Data Factory Pipeline")
    parser.add_argument("--stage", choices=["1", "2", "both"], default="both",
                        help="Run stage 1 (extract), stage 2 (shape), or both")
    args = parser.parse_args()

    if args.stage in ("1", "both"):
        new_entries = stage_1_extract()
    else:
        new_entries = None

    if args.stage in ("2", "both"):
        stage_2_shape(new_entries)

    log("Pipeline complete.")


if __name__ == "__main__":
    main()

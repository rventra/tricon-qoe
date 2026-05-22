#!/usr/bin/env python3
"""
Extraction Quality Diagnostic
=============================
Option B: Count money-lines in PDF vs. model-extracted transactions.
Identifies under-extraction before running full pipeline.
"""

import base64
import io
import json
import os
import re
import time
from collections import Counter
from datetime import datetime, timezone

import fitz
from PIL import Image
import requests

# ── Config ──────────────────────────────────────────────────────────────────

OPENROUTER_API_KEY = "YOUR_OPENROUTER_API_KEY_HERE"
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
EXTRACTION_MODEL = "google/gemini-3.1-flash-lite-preview"
ZOOM = 4
DATA_ROOM = r"Z:\Shared\Selenius Holdings\Tricon Transportation Data Room\Documents\Initial DD\2. Other Financial Information\d. Bank Statements"

# ── Helpers ─────────────────────────────────────────────────────────────────

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")


def count_money_lines_in_page(doc, page_num):
    """
    Count lines on a page that look like financial transactions.
    Heuristics: contains $ sign, OR date pattern + number pattern.
    """
    page = doc.load_page(page_num)
    text = page.get_text("text")
    lines = text.split('\n')
    
    money_line_count = 0
    sample_lines = []
    
    for line in lines:
        line_stripped = line.strip()
        if not line_stripped:
            continue
        
        # Heuristic 1: Contains dollar sign
        has_dollar = '$' in line_stripped
        
        # Heuristic 2: Contains date pattern (MM/DD, MM-DD, or month abbrev)
        has_date = bool(re.search(r'\d{1,2}[/-]\d{1,2}', line_stripped)) or \
                   bool(re.search(r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{1,2}', line_stripped, re.I))
        
        # Heuristic 3: Contains numeric amount (decimal with 2 places, or large integer)
        has_amount = bool(re.search(r'\d{1,3}(,\d{3})*\.\d{2}', line_stripped)) or \
                     bool(re.search(r'\b\d{5,}\b', line_stripped))
        
        # Count as money-line if has dollar, or (has date AND has amount)
        if has_dollar or (has_date and has_amount):
            money_line_count += 1
            if len(sample_lines) < 3:
                sample_lines.append(line_stripped[:80])
    
    return money_line_count, sample_lines, len(lines)


def render_page_to_base64(doc, page_num, zoom=ZOOM):
    page = doc.load_page(page_num)
    mat = fitz.Matrix(zoom, zoom)
    pix = page.get_pixmap(matrix=mat)
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode("utf-8")


def extract_page_with_model(b64_image, filename, page_num, total_pages):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://localhost",
        "X-Title": "Tricon-QOE-Diagnostic",
    }
    system_prompt = """You are a bank statement transaction extractor.
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

    payload = {
        "model": EXTRACTION_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": [
                {"type": "text", "text": f"Extract page {page_num} of {total_pages} from file: {filename}"},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64_image}"}},
            ]},
        ],
        "max_tokens": 4000,
        "temperature": 0.1,
    }
    
    try:
        resp = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=120)
        if resp.status_code != 200:
            return None, f"API error {resp.status_code}"
        data = resp.json()
        if "choices" not in data or len(data["choices"]) == 0:
            return None, "No choices"
        raw = data["choices"][0]["message"]["content"].strip()
        if raw.startswith("```json"):
            raw = raw[7:]
        if raw.startswith("```"):
            raw = raw[3:]
        if raw.endswith("```"):
            raw = raw[:-3]
        raw = raw.strip()
        parsed = json.loads(raw)
        if isinstance(parsed, dict) and "transactions" in parsed:
            return parsed["transactions"], None
        if isinstance(parsed, list):
            return parsed, None
        return [], None
    except Exception as e:
        return None, str(e)


def diagnose_file(full_path, do_api_test=False):
    """Diagnose a single PDF file."""
    filename = os.path.basename(full_path)
    log(f"Diagnosing: {filename}")
    
    try:
        doc = fitz.open(full_path)
    except Exception as e:
        log(f"  ERROR opening: {e}")
        return None
    
    pages = len(doc)
    page_results = []
    total_money_lines = 0
    total_extracted = 0
    
    for p in range(min(pages, 20)):  # Cap at 20 pages per file for speed
        money_count, samples, total_lines = count_money_lines_in_page(doc, p)
        total_money_lines += money_count
        
        extracted_count = 0
        api_error = None
        
        if do_api_test and money_count > 0:
            # Only API-test pages that have money lines
            try:
                b64 = render_page_to_base64(doc, p)
                extracted, api_error = extract_page_with_model(b64, filename, p+1, pages)
                if extracted is not None:
                    extracted_count = len(extracted)
                    total_extracted += extracted_count
            except Exception as e:
                api_error = str(e)
            time.sleep(0.5)
        
        page_results.append({
            "page": p + 1,
            "total_lines": total_lines,
            "money_lines": money_count,
            "extracted": extracted_count if do_api_test else None,
            "extraction_ratio": round(extracted_count / money_count, 2) if do_api_test and money_count > 0 else None,
            "samples": samples,
            "api_error": api_error,
        })
    
    doc.close()
    
    # File-level summary
    file_ratio = round(total_extracted / total_money_lines, 2) if do_api_test and total_money_lines > 0 else None
    
    return {
        "filename": filename,
        "full_path": full_path,
        "pages": pages,
        "total_money_lines": total_money_lines,
        "total_extracted": total_extracted if do_api_test else None,
        "overall_extraction_ratio": file_ratio,
        "page_details": page_results,
    }


def main():
    # Find all missing PDFs
    with open(r'data\raw\MASTER_BANK_STATEMENT_RAW.json', 'r') as f:
        raw = json.load(f)
    existing = {file["filename"] for file in raw["files"]}
    
    all_pdfs = []
    for root, dirs, files in os.walk(DATA_ROOM):
        if "archived" in root.lower():
            continue
        for f in files:
            if f.lower().endswith('.pdf'):
                full = os.path.join(root, f)
                all_pdfs.append(full)
    
    missing = [p for p in all_pdfs if os.path.basename(p) not in existing]
    log(f"Total PDFs: {len(all_pdfs)}, Missing from raw: {len(missing)}")
    
    # Phase 1: Count money lines in ALL missing files (fast, no API)
    log("=" * 60)
    log("PHASE 1: Counting money lines in all missing PDFs (no API)")
    log("=" * 60)
    
    all_results = []
    for idx, pdf_path in enumerate(missing, 1):
        result = diagnose_file(pdf_path, do_api_test=False)
        if result:
            all_results.append(result)
            log(f"[{idx}/{len(missing)}] {result['filename']}: {result['pages']} pages, {result['total_money_lines']} money-lines")
    
    # Sort by money-line count descending to find the big ones
    all_results.sort(key=lambda x: x['total_money_lines'], reverse=True)
    
    log("=" * 60)
    log("PHASE 1 SUMMARY")
    log("=" * 60)
    log(f"Files scanned: {len(all_results)}")
    total_ml = sum(r['total_money_lines'] for r in all_results)
    log(f"Total money-lines across all files: {total_ml}")
    
    # Group by folder
    by_folder = Counter()
    for r in all_results:
        folder = r['full_path'].replace(DATA_ROOM, '').lstrip('\\').split('\\')[0]
        by_folder[folder] += r['total_money_lines']
    
    log("Money-lines by folder:")
    for folder, ml in sorted(by_folder.items(), key=lambda x: -x[1]):
        log(f"  {folder}: {ml}")
    
    # Show top 10 files by money-line count
    log("Top 10 files by money-line count:")
    for r in all_results[:10]:
        log(f"  {r['filename']}: {r['total_money_lines']} money-lines ({r['pages']} pages)")
    
    # Show files with 0 money-lines (possible empty/no-activity)
    zero_ml = [r for r in all_results if r['total_money_lines'] == 0]
    if zero_ml:
        log(f"Files with 0 money-lines (possibly empty): {len(zero_ml)}")
        for r in zero_ml[:5]:
            log(f"  {r['filename']}")
    
    # Phase 2: API extraction test on a sample of high-activity files
    log("=" * 60)
    log("PHASE 2: API extraction test on sample files")
    log("=" * 60)
    
    # Pick 3 representative files: one high-activity, one medium, one low
    # Prioritize BMO-TTICorp 2025 since that's the known problem area
    bmo_2025 = [r for r in all_results if 'bmo' in r['full_path'].lower() and '2025' in r['filename'].lower()]
    if bmo_2025:
        test_files = [bmo_2025[0]]  # First BMO 2025 file
    else:
        test_files = []
    
    # Add one high-activity non-BMO file
    for r in all_results:
        if r not in test_files and r['total_money_lines'] > 50:
            test_files.append(r)
            break
    
    # Add one medium-activity file
    for r in all_results:
        if r not in test_files and 10 < r['total_money_lines'] <= 50:
            test_files.append(r)
            break
    
    log(f"Selected {len(test_files)} files for API testing:")
    for r in test_files:
        log(f"  {r['filename']}: {r['total_money_lines']} money-lines")
    
    api_results = []
    for r in test_files:
        result = diagnose_file(r['full_path'], do_api_test=True)
        if result:
            api_results.append(result)
            ratio = result.get('overall_extraction_ratio', 'N/A')
            log(f"  API RESULT: {result['filename']} - {result['total_money_lines']} money-lines -> {result['total_extracted']} extracted (ratio: {ratio})")
            
            # Show per-page breakdown
            for pd in result['page_details']:
                if pd['money_lines'] > 0:
                    log(f"    Page {pd['page']}: {pd['money_lines']} money-lines -> {pd['extracted']} extracted (ratio: {pd['extraction_ratio']})")
    
    # Save report
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "phase_1_all_files": all_results,
        "phase_2_api_test": api_results,
        "summary": {
            "total_files_scanned": len(all_results),
            "total_money_lines": total_ml,
            "files_api_tested": len(api_results),
        }
    }
    
    report_path = r'data\raw\extraction_diagnostic_report.json'
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    log(f"Report saved to: {report_path}")
    
    # Final verdict
    log("=" * 60)
    log("VERDICT")
    log("=" * 60)
    if api_results:
        ratios = [r['overall_extraction_ratio'] for r in api_results if r.get('overall_extraction_ratio') is not None]
        if ratios:
            avg_ratio = sum(ratios) / len(ratios)
            log(f"Average extraction ratio (money-lines -> extracted): {avg_ratio:.0%}")
            if avg_ratio >= 0.85:
                log("VERDICT: Extraction quality GOOD. Safe to run full pipeline.")
            elif avg_ratio >= 0.60:
                log("VERDICT: Extraction quality MARGINAL. Review flagged pages before full run.")
            else:
                log("VERDICT: Extraction quality POOR. Do NOT run full pipeline. Need format/prompt adjustments.")
        else:
            log("VERDICT: Could not compute extraction ratios.")
    else:
        log("VERDICT: No API tests performed.")


if __name__ == "__main__":
    main()

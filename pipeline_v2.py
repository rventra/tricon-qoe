#!/usr/bin/env python3
"""Tricon QOE Pipeline v2: Page-by-page extraction + shaping with embedded schema"""

import base64, io, json, os, re, time, requests, fitz
from datetime import datetime, timezone

API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
API_URL = "https://openrouter.ai/api/v1/chat/completions"
EXTRACT_MODEL = "google/gemini-3.1-flash-lite-preview"
SHAPE_MODEL = "google/gemini-3.5-flash"
DATA_ROOM = r"Z:\Shared\Selenius Holdings\Tricon Transportation Data Room\Documents\Initial DD\2. Other Financial Information\d. Bank Statements"
RAW_PATH = r"data\raw\MASTER_BANK_STATEMENT_RAW.json"
FLAT_PATH = r"data\flat\bank_transactions_flat.json"

os.makedirs(r"data\raw", exist_ok=True)
os.makedirs(r"data\flat", exist_ok=True)

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)

def load_json(path):
    if os.path.exists(path) and os.path.getsize(path) > 10:
        with open(path, "r", encoding="utf-8-sig") as f:
            return json.load(f)
    return None

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def ensure_raw():
    data = load_json(RAW_PATH)
    if data and "files" in data:
        return data
    return {
        "_metadata": {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "generated_by": "Kimi Code CLI",
            "extraction_method": EXTRACT_MODEL,
            "shaping_method": SHAPE_MODEL,
            "extraction_mode": "page-by-page",
            "zoom_level": 4,
            "total_files": 0,
            "data_room_root": DATA_ROOM,
            "total_pages_processed": 0,
            "total_transactions_extracted": 0,
            "last_updated": datetime.now(timezone.utc).isoformat()
        },
        "files": []
    }

def ensure_flat():
    data = load_json(FLAT_PATH)
    if isinstance(data, list) and len(data) > 0:
        return data
    return []

def scan_pdfs():
    pdfs = []
    for root, dirs, files in os.walk(DATA_ROOM):
        if "archived" in root.lower():
            continue
        for f in files:
            if f.lower().endswith(".pdf"):
                pdfs.append((f, os.path.join(root, f)))
    return pdfs

def render_page(doc, p, zoom=4):
    page = doc.load_page(p)
    pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom))
    img = io.BytesIO(pix.tobytes("png"))
    return base64.b64encode(img.getvalue()).decode("utf-8")

def extract_page(b64, filename, page_num, total_pages):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://localhost",
        "X-Title": "Tricon-QOE",
    }
    system = """You are an expert financial data extractor. Read the bank statement page and extract every individual line-item transaction (deposits, withdrawals, checks, fees).

Look for tabular data containing dates, descriptions, and amounts.
Do NOT extract the overall account starting/ending balances, but DO extract every individual transaction row.

Return ONLY a JSON object with a "transactions" array. Each object in the array must have:
- "date": string (MM/DD or MM/DD/YY as shown)
- "description": string (full description)
- "amount": number (absolute value)
- "type": string (deposit, withdrawal, check, fee, transfer)
- "check_number": string or null
- "reference_number": string or null

If there are absolutely no transaction line items on this specific page, return {"transactions": []}."""

    payload = {
        "model": EXTRACT_MODEL,
        "response_format": {"type": "json_object"},
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": [
                {"type": "text", "text": f"Page {page_num} of {total_pages}: {filename}"},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64}"}}
            ]}
        ],
        "max_tokens": 4000,
        "temperature": 0.1
    }
    for attempt in range(3):
        try:
            r = requests.post(API_URL, headers=headers, json=payload, timeout=120)
            if r.status_code == 200:
                data = r.json()
                if "choices" in data and len(data["choices"]) > 0:
                    return data["choices"][0]["message"]["content"]
            elif r.status_code == 429:
                time.sleep(2 ** attempt)
            else:
                time.sleep(1)
        except Exception as e:
            log(f"    API error: {e}")
            time.sleep(1)
    return None

def parse_extract(raw_text):
    if not raw_text:
        return None
    raw = raw_text.strip()
    for prefix in ["```json", "```"]:
        if raw.startswith(prefix):
            raw = raw[len(prefix):]
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
    except:
        return None

def get_account_info(path):
    p = path.lower()
    if "0069956696" in p or ("bmo" in p and "park" in p):
        return "BMO-TTIPark", "0069956696"
    if "0677032724" in p or ("bmo" in p and "corp" in p):
        return "BMO-TTICorp", "0677032724"
    if "248017740" in p or "cnb" in p:
        return "CNB-TTICorp2", "248017740"
    if "037441394" in p or "tk" in p or "investments" in p:
        return "TK-Investments", "037441394"
    if "959089530" in p or "9530" in p or "tws" in p or "warehouse" in p:
        return "TWS-Warehouse", "959089530"
    return "Unknown", "Unknown"

def infer_date(filename):
    fn = filename.upper()
    m = re.search(r'20(\d{2})(\d{2})', fn)
    if m:
        return "20" + m.group(1), m.group(2)
    y = re.search(r'20(\d{2})', fn)
    mth = None
    for i, mon in enumerate(['JAN','FEB','MAR','APR','MAY','JUN','JUL','AUG','SEP','OCT','NOV','DEC'], 1):
        if mon in fn:
            mth = str(i).zfill(2)
            break
    if y:
        return "20" + y.group(1), mth
    return None, None

# EMBEDDED FLAT SCHEMA
FLAT_SCHEMA = """{
  "id": integer,
  "date": "YYYY-MM-DD",
  "year": "YYYY",
  "month": "MM",
  "account": "BMO-TTICorp | BMO-TTIPark | CNB-TTICorp2 | TK-Investments | TWS-Warehouse",
  "account_number": "string",
  "amount": number,
  "type": "deposit | withdrawal | check | fee | transfer",
  "description": "string",
  "check_number": "string or null",
  "reference_number": "string or null",
  "bucket": "Revenue | COGS | OPEX-Non Payroll | Payroll | Financing | Vendor Payment | Intercompany | Loan | Other | (empty string)",
  "confidence": "High | Medium | Low | (empty string)",
  "reasoning": "string",
  "statement_file": "string",
  "source_file": "string",
  "extraction_method": "string",
  "extracted_at": "ISO datetime",
  "review_flags": []
}"""

def shape_transactions(raw_txns, filename, filepath, page_num):
    if not raw_txns:
        return []
    account, account_num = get_account_info(filepath)
    year, month = infer_date(filename)

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://localhost",
        "X-Title": "Tricon-QOE",
    }

    system = f"""You are a financial data shaper. Convert raw bank transactions into the exact flat schema below.

TARGET SCHEMA (return ONLY a JSON array of these objects):
{FLAT_SCHEMA}

RULES:
- Infer full YYYY-MM-DD dates from statement period + transaction day
- CNB filenames are month AFTER actual period (MAY=April, JUN=May, etc.)
- Account mapping:
  - 0069956696 or bmo+park -> BMO-TTIPark, 0069956696
  - 0677032724 or bmo+corp -> BMO-TTICorp, 0677032724
  - 248017740 or cnb -> CNB-TTICorp2, 248017740
  - 037441394 or tk or investments -> TK-Investments, 037441394
  - 959089530 or 9530 or tws or warehouse -> TWS-Warehouse, 959089530
- Every record MUST have ALL fields from the schema
- review_flags should be an empty array [] if clean, or ["date_uncertain"] etc. if issues
- Return ONLY a JSON array. No markdown, no explanation."""

    txns_json = json.dumps(raw_txns, indent=2)
    user = f"File: {filename}\nPage: {page_num}\nAccount: {account} ({account_num})\nYear: {year}, Month: {month}\n\nRaw transactions:\n{txns_json}\n\nReturn JSON array only."

    payload = {
        "model": SHAPE_MODEL,
        "response_format": {"type": "json_object"},
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": [{"type": "text", "text": user}]}
        ],
        "max_tokens": 8000,
        "temperature": 0.1
    }

    for attempt in range(3):
        try:
            r = requests.post(API_URL, headers=headers, json=payload, timeout=120)
            if r.status_code == 200:
                data = r.json()
                if "choices" in data and len(data["choices"]) > 0:
                    raw_text = data["choices"][0]["message"]["content"].strip()
                    for pre in ["```json", "```"]:
                        if raw_text.startswith(pre):
                            raw_text = raw_text[len(pre):]
                    if raw_text.endswith("```"):
                        raw_text = raw_text[:-3]
                    raw_text = raw_text.strip()
                    shaped = json.loads(raw_text)
                    if isinstance(shaped, list):
                        now = datetime.now(timezone.utc).isoformat()
                        for rec in shaped:
                            rec["statement_file"] = filename
                            rec["source_file"] = filepath
                            rec["page_number"] = page_num
                            rec["extraction_method"] = EXTRACT_MODEL
                            rec["extracted_at"] = now
                            if "review_flags" not in rec:
                                rec["review_flags"] = []
                        return shaped
        except Exception as e:
            log(f"    Shape parse error: {e}")
            time.sleep(1)
    return []

def main():
    log("=" * 60)
    log("PIPELINE V2: Starting from file 1, page 1")
    log("=" * 60)

    raw_data = ensure_raw()
    flat_data = ensure_flat()
    max_id = max((r.get("id", 0) for r in flat_data), default=0)

    pdfs = scan_pdfs()
    log(f"Total PDFs found: {len(pdfs)}")

    done = set()
    for f in raw_data["files"]:
        for pe in f.get("page_extractions", []):
            done.add((f["filename"], pe["page_number"]))

    total_pages = raw_data["_metadata"].get("total_pages_processed", 0)
    total_txns = raw_data["_metadata"].get("total_transactions_extracted", 0)

    for file_idx, (filename, filepath) in enumerate(pdfs, 1):
        log(f"--- FILE [{file_idx}/{len(pdfs)}]: {filename} ---")

        if not os.path.exists(filepath):
            log(f"  FILE NOT FOUND")
            continue

        try:
            doc = fitz.open(filepath)
        except Exception as e:
            log(f"  ERROR opening: {e}")
            continue

        pages = len(doc)
        file_entry = None
        for f in raw_data["files"]:
            if f["filename"] == filename:
                file_entry = f
                break
        if not file_entry:
            file_entry = {
                "filename": filename,
                "full_path": filepath,
                "pages": pages,
                "page_extractions": [],
                "total_transactions": 0,
                "extraction_date": datetime.now(timezone.utc).isoformat(),
                "extraction_method": EXTRACT_MODEL,
                "zoom_level": 4,
            }
            raw_data["files"].append(file_entry)

        for p in range(pages):
            page_num = p + 1
            if (filename, page_num) in done:
                log(f"  Page {page_num}/{pages}: ALREADY DONE")
                continue

            log(f"  Page {page_num}/{pages}: rendering...")
            try:
                b64 = render_page(doc, p)
            except Exception as e:
                log(f"  Page {page_num}/{pages}: RENDER ERROR: {e}")
                file_entry["page_extractions"].append({
                    "page_number": page_num, "transactions_count": 0,
                    "transactions": [], "render_error": True
                })
                continue

            log(f"  Page {page_num}/{pages}: extracting with Flash Lite...")
            raw_text = extract_page(b64, filename, page_num, pages)

            if raw_text:
                preview = raw_text[:150].replace('\n', ' ')
                log(f"    RAW: {preview}...")
            else:
                log(f"    RAW: (API failed)")

            raw_txns = parse_extract(raw_text)

            if raw_txns is None:
                log(f"  Page {page_num}/{pages}: EXTRACT ERROR")
                file_entry["page_extractions"].append({
                    "page_number": page_num, "transactions_count": 0,
                    "transactions": [], "api_error": True
                })
                continue

            log(f"  Page {page_num}/{pages}: extracted {len(raw_txns)} raw transactions")
            file_entry["page_extractions"].append({
                "page_number": page_num, "transactions_count": len(raw_txns),
                "transactions": raw_txns
            })
            file_entry["total_transactions"] += len(raw_txns)
            total_txns += len(raw_txns)

            shaped_count = 0
            if raw_txns:
                log(f"  Page {page_num}/{pages}: shaping with Flash...")
                shaped = shape_transactions(raw_txns, filename, filepath, page_num)
                if shaped:
                    for rec in shaped:
                        max_id += 1
                        rec["id"] = max_id
                    flat_data.extend(shaped)
                    shaped_count = len(shaped)
                    log(f"  Page {page_num}/{pages}: extracted {len(raw_txns)} raw -> shaped {shaped_count} records")
                else:
                    log(f"  Page {page_num}/{pages}: SHAPE ERROR")
            else:
                log(f"  Page {page_num}/{pages}: no transactions")

            total_pages += 1
            done.add((filename, page_num))

            raw_data["_metadata"]["total_files"] = len(raw_data["files"])
            raw_data["_metadata"]["total_pages_processed"] = total_pages
            raw_data["_metadata"]["total_transactions_extracted"] = total_txns
            raw_data["_metadata"]["last_updated"] = datetime.now(timezone.utc).isoformat()
            save_json(RAW_PATH, raw_data)
            save_json(FLAT_PATH, flat_data)
            log(f"  SAVED: {total_pages} pages, {len(flat_data)} flat records total")

            time.sleep(0.3)

        doc.close()
        log(f"  FILE DONE: {filename}")

    log("=" * 60)
    log(f"COMPLETE: {total_pages} pages, {total_txns} raw txns, {len(flat_data)} flat records")
    log("=" * 60)

if __name__ == "__main__":
    main()

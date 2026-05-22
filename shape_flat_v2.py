import json, time, requests
from pathlib import Path
from datetime import datetime, timezone

# --- Config ---
API_KEY = "YOUR_OPENROUTER_API_KEY_HERE"
MODEL = "google/gemini-3.1-flash-preview"
ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"

# --- Paths ---
raw_path = Path(r".\data\raw\MASTER_BANK_STATEMENT_RAW.json")
flat_path = Path(r".\data\flat\bank_transactions_flat.json")

# --- Load flat ---
with open(flat_path, "r", encoding="utf-8") as f:
    flat_data = json.load(f)

existing_files = set(t.get("statement_file", "") for t in flat_data)
max_id = max(t.get("id", 0) for t in flat_data)
print(f"Existing: {len(flat_data)} records, max ID: {max_id}")

# --- Load raw ---
with open(raw_path, "r", encoding="utf-8") as f:
    raw = json.load(f)

files = raw.get("files", [])
new_files = [f for f in files if f.get("filename", "") not in existing_files]
print(f"New files to shape: {len(new_files)}")

# --- Account mapping ---
def map_account(filename, full_path):
    combined = (filename + " " + full_path).lower()
    if "6696" in combined or "park" in combined:
        return "BMO-TTIPark", "0069956696"
    elif "2724" in combined or "corp" in combined:
        return "BMO-TTICorp", "0677032724"
    elif "9530" in combined or "tws" in combined:
        return "TWS-Warehouse", "959089530"
    elif "1394" in combined or "tk-" in combined:
        return "TK-Investments", "037441394"
    elif "7740" in combined or "cnb" in combined:
        return "CNB-TTICorp2", "248017740"
    return "UNKNOWN", "UNKNOWN"

# --- Date parser ---
def parse_date(date_str, filename):
    """Convert various date formats to YYYY-MM-DD"""
    if not date_str or date_str == "":
        return "", "", ""
    
    # Extract year from filename
    year = ""
    for y in ["2023", "2024", "2025", "2026"]:
        if y in filename:
            year = y
            break
    
    date_str = str(date_str).strip()
    
    # Format: MM/DD/YYYY
    if "/" in date_str and len(date_str.split("/")) == 3:
        parts = date_str.split("/")
        return f"{parts[2]}-{parts[0].zfill(2)}-{parts[1].zfill(2)}", parts[2], parts[0].zfill(2)
    
    # Format: M/D or MM/DD (no year)
    if "/" in date_str:
        parts = date_str.split("/")
        if len(parts) == 2 and year:
            return f"{year}-{parts[0].zfill(2)}-{parts[1].zfill(2)}", year, parts[0].zfill(2)
    
    # Format: YYYY-MM-DD
    if "-" in date_str and len(date_str) == 10:
        return date_str, date_str[:4], date_str[5:7]
    
    return date_str, year, ""

# --- Bucket classifier ---
def classify_bucket(description, amount, txn_type):
    desc_lower = (description or "").lower()
    
    if any(k in desc_lower for k in ["payroll", "wage", "salary", "adp", "paychex", "gross pay"]):
        return "Payroll"
    if any(k in desc_lower for k in ["subcontractor", "subcontract", "owner-op", "1099", "contractor pay"]):
        return "COGS"
    if any(k in desc_lower for k in ["fuel", "diesel", "gas", "wex", "comdata", "petro"]):
        return "COGS"
    if any(k in desc_lower for k in ["insurance", "premium", "workers comp", "cargo ins"]):
        return "OPEX"
    if any(k in desc_lower for k in ["rent", "lease", "facility", "warehouse rent"]):
        return "OPEX"
    if any(k in desc_lower for k in ["loan", "principal", "interest", "line of credit", "note pay"]):
        return "Loan"
    if any(k in desc_lower for k in ["tax", "irs", "ftb", "estimate tax", "payroll tax"]):
        return "Taxes"
    if any(k in desc_lower for k in ["transfer", "zelle", "pc transfer", "forced check transfer", "inter-account"]):
        return "Transfer"
    if any(k in desc_lower for k in ["tfs", "ttio", "ttim", "ttiw", "intercompany", "tk investment"]):
        return "Intercompany"
    if any(k in desc_lower for k in ["bank fee", "wire fee", "service charge", "nsf", "overdraft"]):
        return "Other Expense"
    if any(k in desc_lower for k in ["interest income", "rebate", "refund", "cash back"]):
        return "Other Income"
    if any(k in desc_lower for k in ["deposit", "ach dep", "wire in", "incoming", "customer pay", "revenue", "invoice pay"]):
        if txn_type == "deposit" or (amount and amount > 0):
            return "Revenue"
    if any(k in desc_lower for k in ["maintenance", "repair", "tire", "parts", "shop"]):
        return "COGS"
    if any(k in desc_lower for k in ["chassis", "drayage fee", "port fee", "demurrage", "detention", "tmf", "pier pass"]):
        return "COGS"
    
    # Default based on type
    if txn_type == "deposit":
        return "Revenue"
    return "Unknown"

# --- Confidence classifier ---
def classify_confidence(description):
    desc_lower = (description or "").lower()
    vague = ["ach deposit", "wire in", "transfer", "deposit", "withdrawal", "check", "payment"]
    
    if any(v in desc_lower for v in vague) and len(desc_lower) < 30:
        return "Low"
    if any(v in desc_lower for v in vague):
        return "Medium"
    return "High"

# --- Shaping prompt for API ---
SHAPE_PROMPT = """Shape raw bank transactions into structured format.

Input: JSON array of raw transactions with fields: date, description, amount, type
Output: JSON array of shaped transactions with these exact fields:
- date (YYYY-MM-DD)
- year (YYYY)
- month (MM)
- amount (positive number)
- type ("deposit" or "withdrawal")
- description (cleaned, full text)
- check_number (string or null)
- reference_number (string or null)
- bucket (one of: Revenue, COGS, Payroll, OPEX, Taxes, Loan, Transfer, Intercompany, Other Income, Other Expense, Unknown)
- confidence (High, Medium, Low)
- reasoning (brief explanation)
- review_flags (empty array [])

Rules:
- date: Parse MM/DD/YYYY to YYYY-MM-DD. If no year in date, use statement year.
- amount: Always positive.
- type: "deposit" for money in, "withdrawal" for money out.
- check_number: Extract "CK #123", "Check 567", etc. Otherwise null.
- reference_number: Extract wire refs, ACH trace numbers. Otherwise null.
- bucket: Revenue=customer payments/deposits, COGS=subcontractor/fuel/maintenance/chassis, Payroll=wages/salary, OPEX=rent/insurance/office, Taxes=tax payments, Loan=loan payments, Transfer=inter-account, Intercompany=payments to TFS/TK/TTIO/TTIM/TTIW, Other Income=interest/refunds, Other Expense=bank fees, Unknown=ambiguous.
- confidence: High=clear vendor/customer name, Medium=partially clear, Low=vague like "ACH DEPOSIT".

Return ONLY JSON array. No markdown."""

# --- API shaper for complex cases ---
def api_shape(txns, account, account_number, filename):
    if not txns:
        return []
    
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": SHAPE_PROMPT},
            {"role": "user", "content": f"Account: {account} ({account_number}). File: {filename}\n\nTransactions:\n{json.dumps(txns, indent=2)}"}
        ],
        "max_tokens": 4000,
        "temperature": 0.1
    }
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://localhost",
        "X-Title": "Tricon Shaper"
    }
    
    try:
        resp = requests.post(ENDPOINT, headers=headers, json=payload, timeout=120)
        resp.raise_for_status()
        content = resp.json()["choices"][0]["message"]["content"].strip()
        
        if content.startswith("```"):
            content = content.split("\n", 1)[1]
            if content.endswith("```"):
                content = content.rsplit("\n", 1)[0]
            content = content.strip()
        
        shaped = json.loads(content)
        if not isinstance(shaped, list):
            shaped = [shaped]
        return shaped
    except Exception as e:
        print(f"    API ERROR: {str(e)[:80]}")
        return None

# --- Local fallback shaper ---
def local_shape(raw_txn, account, account_number, filename):
    date_str = raw_txn.get("date", "")
    desc = raw_txn.get("description", "")
    amount = raw_txn.get("amount", 0)
    txn_type = raw_txn.get("type", "deposit")
    
    parsed_date, year, month = parse_date(date_str, filename)
    
    # Extract check number
    check_num = None
    import re
    ck_match = re.search(r'(?:ck|check)\s*#?\s*(\d+)', desc, re.IGNORECASE)
    if ck_match:
        check_num = ck_match.group(1)
    
    # Extract reference
    ref_num = None
    ref_match = re.search(r'(?:ref|reference)\s*#?\s*(\w+)', desc, re.IGNORECASE)
    if ref_match:
        ref_num = ref_match.group(1)
    
    bucket = classify_bucket(desc, amount, txn_type)
    confidence = classify_confidence(desc)
    
    return {
        "date": parsed_date,
        "year": year,
        "month": month,
        "account": account,
        "account_number": account_number,
        "amount": abs(float(amount)) if amount else 0,
        "type": "deposit" if txn_type in ["deposit", "credit", "income"] else "withdrawal",
        "description": desc,
        "check_number": check_num,
        "reference_number": ref_num,
        "bucket": bucket,
        "confidence": confidence,
        "reasoning": f"Classified as {bucket} based on description keywords",
        "review_flags": [],
        "statement_file": filename,
        "source_file": raw_txn.get("_source_path", ""),
        "extraction_method": "google/gemini-3.1-flash-lite-preview",
        "extracted_at": datetime.now(timezone.utc).isoformat()
    }

# --- Main: shape page by page ---
new_records = []
current_id = max_id
errors = 0

for fidx, file_entry in enumerate(new_files):
    fname = file_entry.get("filename", "")
    fpath = file_entry.get("full_path", "")
    account, account_number = map_account(fname, fpath)
    
    pages = file_entry.get("page_extractions", [])
    file_txns = 0
    
    for page in pages:
        raw_txns = page.get("transactions", [])
        if not raw_txns:
            continue
        
        # Try API for first batch, fallback to local
        api_result = api_shape(raw_txns[:15], account, account_number, fname)
        
        if api_result:
            # API succeeded - use result
            for record in api_result:
                current_id += 1
                record["id"] = current_id
                record["statement_file"] = fname
                record["source_file"] = fpath
                record["extraction_method"] = "google/gemini-3.1-flash-lite-preview"
                record["extracted_at"] = datetime.now(timezone.utc).isoformat()
                new_records.append(record)
                file_txns += 1
            
            # Handle remaining with local
            for rtx in raw_txns[15:]:
                current_id += 1
                record = local_shape(rtx, account, account_number, fname)
                record["id"] = current_id
                record["source_file"] = fpath
                new_records.append(record)
                file_txns += 1
        else:
            # API failed - use local for all
            errors += 1
            for rtx in raw_txns:
                current_id += 1
                record = local_shape(rtx, account, account_number, fname)
                record["id"] = current_id
                record["source_file"] = fpath
                new_records.append(record)
                file_txns += 1
        
        time.sleep(0.2)
    
    print(f"[{fidx+1}/{len(new_files)}] {fname}: {file_txns} shaped (account: {account})")

# --- Save ---
final = flat_data + new_records
with open(flat_path, "w", encoding="utf-8") as f:
    json.dump(final, f, indent=2, ensure_ascii=False)

print(f"\n{'='*60}")
print(f"DONE. New records: {len(new_records)}")
print(f"Total flat: {len(final)}")
print(f"API errors (fallback used): {errors}")
print(f"New ID range: {max_id+1} to {current_id}")

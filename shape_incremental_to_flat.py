import json, time, requests
from pathlib import Path
from datetime import datetime, timezone

# --- Config ---
API_KEY = "YOUR_OPENROUTER_API_KEY_HERE"
MODEL = "google/gemini-3.1-flash-preview"  # Reasoning model for shaping
ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"

# --- Paths ---
raw_path = Path(r".\data\raw\MASTER_BANK_STATEMENT_RAW.json")
flat_path = Path(r".\data\flat\bank_transactions_flat.json")
backup_path = Path(r".\data\flat\bank_transactions_flat_backup_pre_incremental.json")

# --- Load flat file ---
with open(flat_path, "r", encoding="utf-8") as f:
    flat_data = json.load(f)

existing_files = set(t.get("statement_file", "") for t in flat_data)
max_id = max(t.get("id", 0) for t in flat_data)
print(f"Existing flat records: {len(flat_data)}")
print(f"Existing source files: {len(existing_files)}")
print(f"Max ID: {max_id}")

# --- Load raw ---
with open(raw_path, "r", encoding="utf-8") as f:
    raw = json.load(f)

files = raw.get("files", [])

# --- Identify new files ---
new_raw_files = [f for f in files if f.get("filename", "") not in existing_files]
print(f"New files to shape: {len(new_raw_files)}")

# --- Shaping prompt ---
SHAPE_PROMPT = """You are a bank transaction data shaper. Convert raw extracted transactions into a structured flat format.

For each transaction, return an object with these exact fields:
{
  "date": "YYYY-MM-DD",
  "year": "YYYY",
  "month": "MM",
  "account": "ACCOUNT_NAME",
  "account_number": "ACCOUNT_NUMBER",
  "amount": 1234.56,
  "type": "deposit" or "withdrawal",
  "description": "full description",
  "check_number": "1234" or null,
  "reference_number": "REF123" or null,
  "bucket": "Revenue" or "COGS" or "OPEX" or "Payroll" or "Taxes" or "Other Income" or "Other Expense" or "Intercompany" or "Loan" or "Transfer" or "Unknown",
  "confidence": "High" or "Medium" or "Low",
  "reasoning": "Brief explanation of why this bucket was chosen",
  "review_flags": []
}

ACCOUNT MAPPING (use exact names):
- Filename/path contains "6696" or "park" -> account: "BMO-TTIPark", account_number: "0069956696"
- Filename/path contains "2724" or "corp" -> account: "BMO-TTICorp", account_number: "0677032724"
- Filename/path contains "9530" or "tws" -> account: "TWS-Warehouse", account_number: "959089530"
- Filename/path contains "1394" or "tk" -> account: "TK-Investments", account_number: "037441394"
- Filename/path contains "7740" or "cnb" -> account: "CNB-TTICorp2", account_number: "248017740"

BUCKET RULES:
- "Revenue": Customer payments, deposits from customers, ACH deposits from named customers, wire transfers from customers
- "COGS": Subcontractor payments, fuel, maintenance, repairs, equipment rental, chassis fees
- "Payroll": Wages, salaries, payroll taxes, 401k contributions, bonus payments
- "OPEX": Rent, utilities, insurance, office supplies, meals, travel, phone, software, professional fees
- "Taxes": Tax payments, estimated tax, payroll tax remittances
- "Loan": Loan payments, principal, interest, line of credit draws/payments
- "Transfer": Inter-account transfers, PC transfers, Zelle, internal transfers
- "Intercompany": Payments to/from related entities (TFS, TK, TTIO, TTIM, TTIW)
- "Other Income": Interest income, refunds, rebates, miscellaneous income
- "Other Expense": Bank fees, wire fees, service charges, NSF fees
- "Unknown": Cannot determine from description alone

CONFIDENCE RULES:
- "High": Clear description (customer name, vendor name, payroll, loan payment)
- "Medium": Description is partially clear but could be multiple things
- "Low": Vague description ("ACH DEPOSIT", "WIRE IN", "TRANSFER")

DATE RULES:
- Convert MM/DD/YYYY to YYYY-MM-DD
- If only day shown (e.g., "08/15"), infer month/year from statement period context
- If date is blank, use "" for all date fields

CHECK_NUMBER: Extract from description if present (e.g., "CK #1234", "Check 5678"). Otherwise null.
REFERENCE_NUMBER: Extract wire reference, ACH trace number, etc. Otherwise null.

Return ONLY a JSON array of transaction objects. No markdown, no explanations."""

# --- Account mapping helper ---
def map_account(filename, full_path):
    combined = (filename + " " + full_path).lower()
    if "6696" in combined or "park" in combined:
        return "BMO-TTIPark", "0069956696"
    elif "2724" in combined or "corp" in combined:
        return "BMO-TTICorp", "0677032724"
    elif "9530" in combined or "tws" in combined:
        return "TWS-Warehouse", "959089530"
    elif "1394" in combined or "tk" in combined:
        return "TK-Investments", "037441394"
    elif "7740" in combined or "cnb" in combined:
        return "CNB-TTICorp2", "248017740"
    return "UNKNOWN", "UNKNOWN"

# --- Batch shaping ---
def shape_transactions(raw_txns, filename, full_path):
    if not raw_txns:
        return []
    
    account, account_number = map_account(filename, full_path)
    
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": SHAPE_PROMPT},
            {"role": "user", "content": f"Shape these transactions. Account: {account} ({account_number}). File: {filename}\n\nRaw transactions (JSON):\n{json.dumps(raw_txns, indent=2)}"}
        ],
        "max_tokens": 8000,
        "temperature": 0.1
    }
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://localhost",
        "X-Title": "Tricon Flat Shaper"
    }
    
    try:
        resp = requests.post(ENDPOINT, headers=headers, json=payload, timeout=180)
        resp.raise_for_status()
        content = resp.json()["choices"][0]["message"]["content"].strip()
        
        # Clean markdown
        if content.startswith("```"):
            content = content.split("\n", 1)[1]
            if content.endswith("```"):
                content = content.rsplit("\n", 1)[0]
            content = content.strip()
        
        shaped = json.loads(content)
        if not isinstance(shaped, list):
            shaped = [shaped]
        
        # Add metadata
        for tx in shaped:
            tx["statement_file"] = filename
            tx["source_file"] = full_path
            tx["extraction_method"] = "google/gemini-3.1-flash-lite-preview"
            tx["extracted_at"] = datetime.now(timezone.utc).isoformat()
        
        return shaped
    except Exception as e:
        print(f"    SHAPE ERROR: {str(e)[:100]}")
        return []

# --- Main loop ---
new_flat_records = []
current_id = max_id
start_time = time.time()

for idx, file_entry in enumerate(new_raw_files):
    fname = file_entry.get("filename", "")
    fpath = file_entry.get("full_path", "")
    
    # Collect all transactions from all pages
    all_raw_txns = []
    for page in file_entry.get("page_extractions", []):
        for txn in page.get("transactions", []):
            all_raw_txns.append(txn)
    
    if not all_raw_txns:
        print(f"[{idx+1}/{len(new_raw_files)}] {fname} - 0 transactions, skipping")
        continue
    
    print(f"[{idx+1}/{len(new_raw_files)}] {fname} - {len(all_raw_txns)} raw txns")
    
    # Shape in batches of 30 to avoid token limits
    batch_size = 30
    shaped_count = 0
    
    for batch_start in range(0, len(all_raw_txns), batch_size):
        batch = all_raw_txns[batch_start:batch_start + batch_size]
        shaped = shape_transactions(batch, fname, fpath)
        
        for record in shaped:
            current_id += 1
            record["id"] = current_id
            new_flat_records.append(record)
            shaped_count += 1
        
        time.sleep(0.3)
    
    print(f"  -> Shaped {shaped_count} records")
    
    # Save intermediate backup every 10 files
    if (idx + 1) % 10 == 0:
        backup = flat_data + new_flat_records
        with open(backup_path, "w", encoding="utf-8") as f:
            json.dump(backup, f, indent=2, ensure_ascii=False)
        print(f"  -> Backup saved ({len(backup)} total records)")

# --- Final save ---
final_data = flat_data + new_flat_records
with open(flat_path, "w", encoding="utf-8") as f:
    json.dump(final_data, f, indent=2, ensure_ascii=False)

print(f"\n{'='*60}")
print(f"DONE.")
print(f"Existing records: {len(flat_data):,}")
print(f"New records: {len(new_flat_records):,}")
print(f"Total flat records: {len(final_data):,}")
print(f"ID range: 1 to {current_id}")
print(f"Elapsed: {(time.time()-start_time)/60:.1f} minutes")

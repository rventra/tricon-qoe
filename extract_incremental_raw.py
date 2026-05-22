import json, base64, os, time, fitz, requests
from pathlib import Path
from io import BytesIO
from PIL import Image

# --- Config ---
API_KEY = "YOUR_OPENROUTER_API_KEY_HERE"
MODEL = "google/gemini-3.1-flash-lite-preview"
ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"

# --- Paths ---
data_room = Path(r"Z:\Shared\Selenius Holdings\Tricon Transportation Data Room\Documents\Initial DD\2. Other Financial Information\d. Bank Statements")
raw_path = Path(r".\data\raw\MASTER_BANK_STATEMENT_RAW.json")
backup_dir = Path(r".\data\raw\backups")
backup_dir.mkdir(exist_ok=True)

# --- Load existing data ---
with open(raw_path, "r", encoding="utf-8") as f:
    raw = json.load(f)

existing_files = raw.get("files", [])
extracted_names = {f.get("filename", f.get("file_name", "")) for f in existing_files}
print(f"Loaded existing: {len(existing_files)} files")

# --- Find incremental PDFs ---
def should_skip(pdf_path):
    rel = str(pdf_path.relative_to(data_room)).lower()
    return any(k in rel for k in ["archived", "empty", "redundant"])

incremental = []
for pdf in data_room.rglob("*.pdf"):
    if should_skip(pdf):
        continue
    if pdf.name not in extracted_names:
        incremental.append(pdf)

print(f"Incremental to extract: {len(incremental)}")

# --- Extraction prompt ---
SYSTEM_PROMPT = """Extract ALL bank transactions from this statement page.

Return ONLY JSON: {"transactions": [{"date":"MM/DD/YYYY","description":"...","amount":1234.56,"type":"deposit"}]}

Rules:
- Page 1 of statements is often just a summary header. Skip if no transactions visible.
- Look for transaction tables with columns: Date, Description, Amount, Balance.
- type: "deposit" for credits/money in, "withdrawal" for debits/money out.
- amount: Positive number only. No $ or commas.
- date: MM/DD/YYYY. Infer year from statement header if not shown.
- description: Full text from all lines of the entry.
- Return ONLY valid JSON. No markdown, no explanations."""

# --- Page rendering ---
def render_page_4x(doc, page_num):
    page = doc[page_num]
    mat = fitz.Matrix(4, 4)
    pix = page.get_pixmap(matrix=mat)
    img = Image.open(BytesIO(pix.tobytes("png")))
    max_w = 1600
    if img.width > max_w:
        ratio = max_w / img.width
        img = img.resize((max_w, int(img.height * ratio)), Image.LANCZOS)
    buf = BytesIO()
    img.save(buf, format="PNG", optimize=True)
    return base64.b64encode(buf.getvalue()).decode("utf-8")

# --- API call ---
def extract_page(image_b64, page_num, filename):
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": [
                {"type": "text", "text": f"Page {page_num + 1} of {filename}"},
                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_b64}"}}
            ]}
        ],
        "max_tokens": 4000,
        "temperature": 0.1
    }
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://localhost",
        "X-Title": "Tricon Bank Extraction"
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
        result = json.loads(content)
        return result.get("transactions", [])
    except Exception as e:
        print(f"    API ERROR page {page_num+1}: {str(e)[:80]}")
        return []

# --- Main loop ---
new_entries = []
start_time = time.time()

for idx, pdf in enumerate(incremental):
    elapsed = time.time() - start_time
    eta = (elapsed / (idx + 1)) * (len(incremental) - idx - 1) if idx > 0 else 0
    print(f"\n[{idx+1}/{len(incremental)}] {pdf.name} | ETA: {eta/60:.1f}m")
    
    try:
        doc = fitz.open(str(pdf))
        pages_data = []
        total_txns = 0
        
        for pnum in range(len(doc)):
            img_b64 = render_page_4x(doc, pnum)
            txns = extract_page(img_b64, pnum, pdf.name)
            pages_data.append({
                "page_number": pnum + 1,
                "transactions_count": len(txns),
                "transactions": txns
            })
            total_txns += len(txns)
        
        doc.close()
        
        entry = {
            "filename": pdf.name,
            "full_path": str(pdf),
            "pages": len(pages_data),
            "page_extractions": pages_data,
            "total_transactions": total_txns
        }
        new_entries.append(entry)
        print(f"  TOTAL: {total_txns} transactions from {len(pages_data)} pages")
        
        # Backup every 10 files
        if (idx + 1) % 10 == 0:
            raw["files"] = existing_files + new_entries
            backup_path = backup_dir / f"MASTER_BANK_STATEMENT_RAW_backup_{idx+1}.json"
            with open(backup_path, "w", encoding="utf-8") as f:
                json.dump(raw, f, indent=2, ensure_ascii=False)
            print(f"  -> Backup saved: {backup_path.name}")
        
        time.sleep(0.3)
        
    except Exception as e:
        print(f"  ERROR on {pdf.name}: {e}")

# --- Final save ---
raw["files"] = existing_files + new_entries
with open(raw_path, "w", encoding="utf-8") as f:
    json.dump(raw, f, indent=2, ensure_ascii=False)

print(f"\n{'='*60}")
print(f"DONE. Added {len(new_entries)} files.")
print(f"Total in raw: {len(raw['files'])} files")
print(f"Elapsed: {(time.time()-start_time)/60:.1f} minutes")

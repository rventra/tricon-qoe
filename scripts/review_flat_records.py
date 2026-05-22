#!/usr/bin/env python3
"""
Tricon QOE - AI Review of Flat Records
Uses Gemini Flash via OpenRouter to review all flat records for accuracy.
Adds 'review_flags' key with suggested changes where needed.
"""

import json
import os
import re
import sys
import time
from datetime import datetime
from pathlib import Path

FLAT_PATH = Path("bank_transactions_flat.json")
OUTPUT_PATH = Path("bank_transactions_flat_reviewed.json")
PROGRESS_PATH = Path("_review_progress.json")
SETTINGS_PATH = Path.home() / ".claude" / "settings.json"

BASE_URL = "https://openrouter.ai/api/v1"
MODEL_REVIEW = "google/gemini-3-flash-preview"
BATCH_SIZE = 80
MAX_RETRIES = 3
RATE_LIMIT_DELAY = 1.0


def load_api_key():
    with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
        settings = json.load(f)
    return settings["env"]["ANTHROPIC_AUTH_TOKEN"]


def init_client(api_key):
    from openai import OpenAI
    return OpenAI(base_url=BASE_URL, api_key=api_key)


REVIEW_SYSTEM_PROMPT = """You are a senior financial analyst reviewing bank transaction records for Tricon Transportation, Inc.

Your job: Review each transaction record and flag ONLY records that have clear issues.

For each record, evaluate:
1. DATE: Is the date plausible? Watch for year-boundary errors (e.g., Dec transaction in a Jan statement should be prior year).
2. BUCKET: Is the classification correct?
   - "Revenue" = deposits from customers, sales, parking income
   - "Payroll" = wages, salaries, benefits, 401k, PEO (Barrett), CalSavers
   - "OPEX-Non Payroll" = rent, utilities, insurance, bank fees, taxes, freight/logistics (PayCargo, freight costs), software, permits
   - "Financing" = loans, credit lines, interest, intercompany transfers, DTFS
   - "Vendor Payment" = checks to vendors, wire transfers to suppliers
   - "COGS" = direct vehicle costs: fuel, repairs, parts, tires, maintenance ONLY (NOT freight/shipping)
3. CHECK_NUMBER: Was a check number missed? Look for numeric-only descriptions (3-6 digits) that are clearly check numbers.
4. DESCRIPTION: Is the description meaningful? Flag if it looks truncated or garbled.
5. AMOUNT: Any obviously wrong amounts (e.g., $0.01 for a payroll check)?

OUTPUT FORMAT:
Return ONLY a JSON array of objects. One object per reviewed record, in the SAME ORDER as input.
Each object must have:
- "id": the record's id (exactly as provided)
- "review_flags": array of strings (empty if no issues found), e.g. ["Bucket may be wrong - 'Service Charges' is typically OPEX-Non Payroll, not Financing", "Check number likely missing - description '482931' appears to be a check number"]

Rules:
- ONLY flag records with REAL issues. Do NOT flag records that look correct.
- Keep flags concise (1 sentence each).
- Do NOT add fields other than 'id' and 'review_flags'.
- Return valid JSON only, no markdown fences, no commentary.
"""


def sanitize_json(content):
    content = content.strip()
    content = re.sub(r'^```json\s*', '', content)
    content = re.sub(r'^```\s*', '', content)
    content = re.sub(r'\s*```$', '', content)
    # Fix invalid escapes
    def fix_esc(m):
        following = m.group(0)[1:]
        if following in ('"', '\\', '/', 'b', 'f', 'n', 'r', 't') or following.startswith('u'):
            return m.group(0)
        return '\\\\' + following
    content = re.sub(r'\\(?!"|\\|/|b|f|n|r|t|u)', fix_esc, content)
    return content


def call_review(client, prompt, retries=MAX_RETRIES):
    for attempt in range(1, retries + 1):
        try:
            resp = client.chat.completions.create(
                model=MODEL_REVIEW,
                messages=[
                    {"role": "system", "content": REVIEW_SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.0,
                max_tokens=32000,
            )
            content = sanitize_json(resp.choices[0].message.content)
            parsed = json.loads(content)
            if not isinstance(parsed, list):
                raise ValueError("Response not a JSON array")
            return parsed
        except Exception as e:
            print(f"    API attempt {attempt}/{retries} failed: {e}")
            if attempt < retries:
                sleep_time = 2 ** attempt
                time.sleep(sleep_time)
            else:
                raise


def load_progress():
    if PROGRESS_PATH.exists():
        with open(PROGRESS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"completed_batches": 0, "reviewed_records": []}


def save_progress(progress):
    with open(PROGRESS_PATH, "w", encoding="utf-8") as f:
        json.dump(progress, f, indent=2)


def build_review_prompt(batch_records):
    """Build prompt for a batch of records."""
    # Strip unnecessary fields to reduce token count
    slim = []
    for rec in batch_records:
        slim.append({
            "id": rec["id"],
            "date": rec["date"],
            "account": rec["account"],
            "amount": rec["amount"],
            "type": rec["type"],
            "description": rec["description"],
            "check_number": rec.get("check_number"),
            "bucket": rec["bucket"],
            "confidence": rec["confidence"],
            "reasoning": rec["reasoning"],
            "statement_file": rec["statement_file"],
        })

    return f"""Review these {len(slim)} bank transaction records for Tricon Transportation, Inc.

For each record, check:
1. DATE accuracy (year-boundary logic)
2. BUCKET classification correctness
3. CHECK_NUMBER extraction (did we miss any?)
4. DESCRIPTION quality
5. AMOUNT plausibility

Return a JSON array where each object has:
- "id": matching the input record id
- "review_flags": array of issue strings (empty if no issues)

RECORDS:
{json.dumps(slim, indent=2)}
"""


def apply_programmatic_fixes(records):
    """Apply known fixes before AI review."""
    fixes = 0
    for rec in records:
        # Freight/logistics (PayCargo) → OPEX-Non Payroll, not COGS
        desc_upper = rec["description"].upper()
        if "PAYCARGO" in desc_upper and rec["bucket"] == "COGS":
            rec["bucket"] = "OPEX-Non Payroll"
            rec["reasoning"] = "Freight/logistics payment - classified as OPEX-Non Payroll"
            rec["confidence"] = "High"
            fixes += 1

        # Service charges → OPEX-Non Payroll
        if "SERV CHG" in desc_upper or "SERVICE CHARGES" in desc_upper:
            if rec["bucket"] != "OPEX-Non Payroll":
                rec["bucket"] = "OPEX-Non Payroll"
                rec["reasoning"] = "Bank service charges"
                rec["confidence"] = "High"
                fixes += 1

        # CalSavers → Payroll
        if "CALSAVERS" in desc_upper and rec["bucket"] != "Payroll":
            rec["bucket"] = "Payroll"
            rec["reasoning"] = "CalSavers retirement contribution / payroll deduction"
            rec["confidence"] = "High"
            fixes += 1

    print(f"  Programmatic fixes applied: {fixes}")
    return records


def main():
    print("=" * 60)
    print("Tricon QOE - AI Review of Flat Records")
    print("=" * 60)

    api_key = load_api_key()
    client = init_client(api_key)

    with open(FLAT_PATH, "r", encoding="utf-8") as f:
        records = json.load(f)

    print(f"Loaded {len(records)} flat records")

    # Step 1: Apply programmatic fixes
    records = apply_programmatic_fixes(records)

    # Step 2: Add review_flags field to all records
    for rec in records:
        rec["review_flags"] = []

    progress = load_progress()
    completed_batches = progress["completed_batches"]

    total_batches = (len(records) + BATCH_SIZE - 1) // BATCH_SIZE
    print(f"Reviewing in {total_batches} batches of ~{BATCH_SIZE} records")
    print(f"Already completed: {completed_batches} batches")
    print()

    for batch_num in range(completed_batches, total_batches):
        start_idx = batch_num * BATCH_SIZE
        end_idx = min(start_idx + BATCH_SIZE, len(records))
        batch = records[start_idx:end_idx]

        print(f"[{batch_num + 1}/{total_batches}] Reviewing records {start_idx + 1}-{end_idx}...")

        prompt = build_review_prompt(batch)
        try:
            review_results = call_review(client, prompt)
        except Exception as e:
            print(f"  FAILED after retries: {e}")
            save_progress(progress)
            sys.exit(1)

        # Map review results by id
        result_map = {r["id"]: r.get("review_flags", []) for r in review_results if "id" in r}

        flagged_count = 0
        for rec in batch:
            flags = result_map.get(rec["id"], [])
            rec["review_flags"] = flags
            if flags:
                flagged_count += 1

        progress["completed_batches"] = batch_num + 1
        save_progress(progress)

        print(f"  -> {flagged_count}/{len(batch)} records flagged for review")
        time.sleep(RATE_LIMIT_DELAY)

    # Step 3: Save reviewed output
    print()
    print("Saving reviewed records...")

    total_flagged = sum(1 for r in records if r.get("review_flags"))
    print(f"Total records with review flags: {total_flagged}/{len(records)}")

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2)
    print(f"Saved: {OUTPUT_PATH}")

    # Print sample flags
    if total_flagged > 0:
        print()
        print("Sample flagged records:")
        for rec in records:
            if rec.get("review_flags"):
                print(f"  ID {rec['id']}: {rec['description'][:50]}")
                for flag in rec["review_flags"]:
                    print(f"    - {flag}")
                if sum(1 for r in records if r.get("review_flags")) > 10:
                    break

    print()
    print("Done.")


if __name__ == "__main__":
    main()

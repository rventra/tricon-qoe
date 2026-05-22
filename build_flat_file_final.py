import json
import re
import os
import fitz
from collections import defaultdict
import calendar

# 1. Flat JSON counts (ground truth for transactions)
with open(r'data\flat\bank_transactions_flat.json', 'r') as f:
    flat = json.load(f)

flat_counts = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
for t in flat:
    flat_counts[t['account']][int(t['year'])][int(t['month'])] += 1

# 2. Scan ALL PDFs to determine actual statement months
# For CNB, we must read actual dates from inside PDFs because filenames are wrong

base_path = r'Z:\Shared\Selenius Holdings\Tricon Transportation Data Room\Documents\Initial DD\2. Other Financial Information\d. Bank Statements'

folders_to_scan = [
    os.path.join(base_path, 'Account #9530', 'Empty Statements'),
    os.path.join(base_path, 'Account #9530', 'Transaction Level Statements'),
    os.path.join(base_path, 'BMO', 'Empty Statements'),
    os.path.join(base_path, 'BMO', 'Transaction Level Statements'),
    os.path.join(base_path, 'CNB', 'Empty Statements'),
    os.path.join(base_path, 'CNB', 'Transaction Level Statements'),
    os.path.join(base_path, 'CNB', 'Compilations'),
    os.path.join(base_path, 'TK', 'Empty Statements'),
    os.path.join(base_path, 'TK', 'Transaction Level Statements'),
    os.path.join(base_path, 'TWS Bank Statements', 'Empty Statements'),
    os.path.join(base_path, 'TWS Bank Statements', 'Transaction Level Statements'),
]

provided_months = defaultdict(lambda: defaultdict(set))

def get_account_from_path(path):
    upper = path.upper()
    if '9530' in upper:
        return 'TWS-Warehouse'
    elif 'BMO' in upper and 'TTI' in upper:
        return 'BMO-TTICorp'
    elif 'TTI PARK' in upper or 'TTI_PARK' in upper:
        return 'BMO-TTIPark'
    elif 'CNB' in upper:
        return 'CNB-TTICorp2'
    elif 'TK' in upper:
        return 'TK-Investments'
    return None

def read_statement_date_from_pdf(path):
    """Read the actual statement date from inside the PDF"""
    try:
        doc = fitz.open(path)
        text = doc[0].get_text()
        
        # Look for "This statement: Month DD, YYYY" or similar
        stmt_match = re.search(r'This statement:\s*([A-Za-z]+\s+\d{1,2},?\s+\d{4})', text)
        if stmt_match:
            date_str = stmt_match.group(1).strip()
            mon_map = {'JANUARY':1,'FEBRUARY':2,'MARCH':3,'APRIL':4,'MAY':5,'JUNE':6,
                       'JULY':7,'AUGUST':8,'SEPTEMBER':9,'OCTOBER':10,'NOVEMBER':11,'DECEMBER':12,
                       'JAN':1,'FEB':2,'MAR':3,'APR':4,'MAY':5,'JUN':6,
                       'JUL':7,'AUG':8,'SEP':9,'OCT':10,'NOV':11,'DEC':12}
            parts = date_str.replace(',', '').split()
            if len(parts) >= 3:
                month_str = parts[0].upper()
                year = int(parts[-1])
                month = mon_map.get(month_str)
                if month and 2020 <= year <= 2030:
                    return year, month
        
        # Fallback: look for date in filename
        fname = os.path.basename(path)
        m1 = re.search(r'^(\d{4})(\d{2})\d{2}', fname)
        if m1:
            return int(m1.group(1)), int(m1.group(2))
        m2 = re.search(r'(\d{4})\s+([A-Z]{3})', fname.upper())
        if m2:
            year = int(m2.group(1))
            mon_str = m2.group(2)
            mon_map = {'JAN':1,'FEB':2,'MAR':3,'APR':4,'MAY':5,'JUN':6,'JUL':7,'AUG':8,'SEP':9,'OCT':10,'NOV':11,'DEC':12}
            month = mon_map.get(mon_str)
            if month:
                return year, month
    except Exception as e:
        pass
    return None, None

for folder in folders_to_scan:
    if os.path.exists(folder):
        for fname in os.listdir(folder):
            if fname.endswith('.pdf'):
                path = os.path.join(folder, fname)
                acct = get_account_from_path(path)
                if not acct:
                    continue
                year, month = read_statement_date_from_pdf(path)
                if year and month:
                    provided_months[acct][year].add(month)

# Also check raw extraction files
with open(r'data\raw\MASTER_BANK_STATEMENT_RAW.json', 'r') as f:
    raw = json.load(f)

for file_info in raw['files']:
    fname = file_info['filename']
    upper = fname.upper()
    
    acct = None
    if 'BMO TTI' in upper:
        acct = 'BMO-TTICorp'
    elif 'TTI PARK' in upper or 'TTI_PARK' in upper:
        acct = 'BMO-TTIPark'
    elif 'CNB' in upper:
        acct = 'CNB-TTICorp2'
    elif '9530' in upper:
        acct = 'TWS-Warehouse'
    elif ' TK' in upper or upper.startswith('2025 TK') or upper.startswith('2026 TK'):
        acct = 'TK-Investments'
    
    if not acct:
        continue
    
    # For CNB, use actual dates from transactions inside the PDF
    if acct == 'CNB-TTICorp2':
        for page in file_info['page_extractions']:
            for tx in page['transactions']:
                date_str = tx.get('date', '')
                if date_str and date_str != 'N/A':
                    m = re.search(r'^(\d{2})', date_str)
                    if m:
                        month = int(m.group(1))
                        # Determine year from filename or other means
                        year_match = re.search(r'(\d{4})', fname)
                        if year_match:
                            year = int(year_match.group(1))
                            if 2020 <= year <= 2030 and 1 <= month <= 12:
                                provided_months[acct][year].add(month)
                                break
            else:
                continue
            break
    else:
        year, month = read_statement_date_from_pdf(os.path.join(base_path, fname))
        if year and month:
            provided_months[acct][year].add(month)
        else:
            # Fallback to filename parsing
            m1 = re.search(r'^(\d{4})(\d{2})\d{2}', fname)
            if m1:
                year = int(m1.group(1))
                month = int(m1.group(2))
                provided_months[acct][year].add(month)
            else:
                m2 = re.search(r'(\d{4})\s+([A-Z]{3})', fname.upper())
                if m2:
                    year = int(m2.group(1))
                    mon_str = m2.group(2)
                    mon_map = {'JAN':1,'FEB':2,'MAR':3,'APR':4,'MAY':5,'JUN':6,'JUL':7,'AUG':8,'SEP':9,'OCT':10,'NOV':11,'DEC':12}
                    month = mon_map.get(mon_str)
                    if month:
                        provided_months[acct][year].add(month)

# 3. Build flat file
accounts = ['BMO-TTICorp', 'BMO-TTIPark', 'CNB-TTICorp2', 'TK-Investments', 'TWS-Warehouse']
account_names = {
    'BMO-TTICorp': 'BMO-TTICorp (0677032724)',
    'BMO-TTIPark': 'BMO-TTIPark (0069956696)',
    'CNB-TTICorp2': 'CNB-TTICorp2 (248017740)',
    'TK-Investments': 'TK-Investments (037441394)',
    'TWS-Warehouse': 'TWS-Warehouse (959089530)',
}

def last_day(year, month):
    return calendar.monthrange(year, month)[1]

lines = []
header = 'Account\tDate\tYear\tMonth\tStatus\tTxnCount'
lines.append(header)

for acct in accounts:
    for year in [2022, 2023, 2024, 2025, 2026]:
        for month in range(1, 13):
            txn_count = flat_counts[acct][year].get(month, 0)
            is_provided = month in provided_months[acct].get(year, set())
            
            if txn_count > 0 or is_provided:
                status = 'Provided'
            else:
                status = 'Missing'
            
            day = last_day(year, month)
            date_str = f'{year}-{month:02d}-{day:02d}'
            
            line = f'{account_names[acct]}\t{date_str}\t{year}\t{month:02d}\t{status}\t{txn_count}'
            lines.append(line)

# Write to file
output_path = 'bank_statement_status_flat.txt'
with open(output_path, 'w') as f:
    f.write('\n'.join(lines) + '\n')

print(f'Wrote {len(lines)-1} rows to {output_path}')

# Verify total transactions
total_txns = sum(flat_counts[acct][year].get(month, 0) for acct in accounts for year in [2022,2023,2024,2025,2026] for month in range(1,13))
print(f'Total transactions in flat JSON: {total_txns}')

# Show "Provided with 0 txns" (no activity confirmed)
print()
print('=== Provided with 0 transactions (No Activity Confirmed) ===')
for acct in accounts:
    for year in [2022, 2023, 2024, 2025, 2026]:
        for month in range(1, 13):
            txn_count = flat_counts[acct][year].get(month, 0)
            is_provided = month in provided_months[acct].get(year, set())
            if txn_count == 0 and is_provided:
                print(f'  {account_names[acct]} {year}-{month:02d}')

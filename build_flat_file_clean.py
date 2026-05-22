import json
import re
import os
import fitz
from collections import defaultdict
import calendar

# 1. Flat JSON counts (ground truth)
with open(r'data\flat\bank_transactions_flat.json', 'r') as f:
    flat = json.load(f)

flat_counts = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
for t in flat:
    yr = int(t['year']) if isinstance(t['year'], (int, str)) else t['year']
    mo = int(t['month']) if isinstance(t['month'], (int, str)) else t['month']
    flat_counts[t['account']][yr][mo] += 1

# 2. Find empty/no-activity statement files
# Key insight: CNB filenames are wrong. Must read actual dates from inside PDFs.
# For all other accounts, trust the filename dates.

base_path = r'Z:\Shared\Selenius Holdings\Tricon Transportation Data Room\Documents\Initial DD\2. Other Financial Information\d. Bank Statements'

# Map folder to account
folder_accounts = {
    os.path.join(base_path, 'Account #9530', 'Empty Statements'): 'TWS-Warehouse',
    os.path.join(base_path, 'Account #9530', 'Transaction Level Statements'): 'TWS-Warehouse',
    os.path.join(base_path, 'BMO', 'Empty Statements'): 'BMO-TTICorp',
    os.path.join(base_path, 'BMO', 'Transaction Level Statements'): 'BMO-TTICorp',
    os.path.join(base_path, 'CNB', 'Empty Statements'): 'CNB-TTICorp2',
    os.path.join(base_path, 'CNB', 'Transaction Level Statements'): 'CNB-TTICorp2',
    os.path.join(base_path, 'CNB', 'Compilations', 'Redundant'): 'CNB-TTICorp2',
    os.path.join(base_path, 'TK', 'Empty Statements'): 'TK-Investments',
    os.path.join(base_path, 'TK', 'Transaction Level Statements'): 'TK-Investments',
    os.path.join(base_path, 'TWS Bank Statements', 'Empty Statements'): 'TWS-Warehouse',
    os.path.join(base_path, 'TWS Bank Statements', 'Transaction Level Statements'): 'TWS-Warehouse',
}

def read_actual_date_from_pdf(path):
    """Read 'This statement: Month DD, YYYY' from inside PDF"""
    try:
        doc = fitz.open(path)
        text = doc[0].get_text()
        stmt_match = re.search(r'This statement:\s*([A-Za-z]+\s+\d{1,2},?\s+\d{4})', text)
        if stmt_match:
            date_str = stmt_match.group(1).strip().replace(',', '')
            parts = date_str.split()
            mon_map = {'JANUARY':1,'FEBRUARY':2,'MARCH':3,'APRIL':4,'MAY':5,'JUNE':6,
                       'JULY':7,'AUGUST':8,'SEPTEMBER':9,'OCTOBER':10,'NOVEMBER':11,'DECEMBER':12,
                       'JAN':1,'FEB':2,'MAR':3,'APR':4,'MAY':5,'JUN':6,
                       'JUL':7,'AUG':8,'SEP':9,'OCT':10,'NOV':11,'DEC':12}
            month = mon_map.get(parts[0].upper())
            year = int(parts[-1])
            if month and 2020 <= year <= 2030:
                return year, month
    except:
        pass
    return None, None

def parse_filename_date(fname):
    """Parse date from filename like 20230531 or 2024 APR"""
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
    return None, None

provided_months = defaultdict(lambda: defaultdict(set))

# Scan all relevant folders
for folder, acct in folder_accounts.items():
    if not os.path.exists(folder):
        continue
    for fname in os.listdir(folder):
        if not fname.endswith('.pdf'):
            continue
        path = os.path.join(folder, fname)
        
        if acct == 'CNB-TTICorp2':
            # CNB filenames are wrong - read actual date from inside PDF
            year, month = read_actual_date_from_pdf(path)
        else:
            # Other accounts: trust filename
            year, month = parse_filename_date(fname)
        
        if year and month:
            provided_months[acct][year].add(month)

# Also scan raw extraction for files (these are the ones that were actually extracted)
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
    
    if acct == 'CNB-TTICorp2':
        # CNB: read actual dates from inside PDF
        # But we need the full path to read it
        # For raw extraction, try filename first, fallback to transaction dates
        year, month = parse_filename_date(fname)
        if not year:
            # Try reading from transactions inside
            for page in file_info['page_extractions']:
                for tx in page['transactions']:
                    ds = tx.get('date', '')
                    m = re.search(r'^(\d{2})', ds)
                    if m:
                        month = int(m.group(1))
                        ym = re.search(r'(\d{4})', fname)
                        if ym:
                            year = int(ym.group(1))
                            break
                if year:
                    break
    else:
        year, month = parse_filename_date(fname)
    
    if year and month:
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

# Write
output_path = 'bank_statement_status_flat.txt'
with open(output_path, 'w') as f:
    f.write('\n'.join(lines) + '\n')

print(f'Wrote {len(lines)-1} rows to {output_path}')

# Verify totals
total_txns = sum(flat_counts[acct][year].get(month, 0) for acct in accounts for year in [2022,2023,2024,2025,2026] for month in range(1,13))
print(f'Total transactions in flat JSON: {total_txns}')

# Show Provided with 0 txns
print()
print('=== Provided with 0 transactions (No Activity Confirmed) ===')
count = 0
for acct in accounts:
    for year in [2022, 2023, 2024, 2025, 2026]:
        for month in range(1, 13):
            txn_count = flat_counts[acct][year].get(month, 0)
            is_provided = month in provided_months[acct].get(year, set())
            if txn_count == 0 and is_provided:
                print(f'  {account_names[acct]} {year}-{month:02d}')
                count += 1
print(f'Total: {count} months')
